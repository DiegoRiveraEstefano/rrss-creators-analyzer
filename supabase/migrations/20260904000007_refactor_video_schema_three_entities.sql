-- ==============================================================================
-- Migration: 20260904000007_refactor_video_schema_three_entities.sql
-- Description: Modelo de datos de Videos en 3 entidades (videos, video_publications, video_relations)
-- ==============================================================================

-- 1. Tabla Principal: Videos (Activo digital de contenido)
CREATE TABLE IF NOT EXISTS public.videos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
    creator_id UUID NOT NULL REFERENCES public.creators(id) ON DELETE CASCADE,
    
    title TEXT NOT NULL,
    internal_name TEXT,
    description TEXT,
    tags TEXT[] DEFAULT '{}',
    category TEXT,
    duration_seconds INTEGER NOT NULL DEFAULT 0,
    production_cost NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    status TEXT NOT NULL DEFAULT 'published', -- 'draft', 'editing', 'ready', 'published', 'archived'
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

CREATE INDEX IF NOT EXISTS idx_videos_org ON public.videos(organization_id);
CREATE INDEX IF NOT EXISTS idx_videos_creator ON public.videos(creator_id);
CREATE INDEX IF NOT EXISTS idx_videos_created_at ON public.videos(created_at DESC);

-- 2. Tabla Secundaria: Publicaciones por Plataforma (YouTube, TikTok, Reels, etc.)
CREATE TABLE IF NOT EXISTS public.video_publications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id UUID NOT NULL REFERENCES public.videos(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
    creator_id UUID NOT NULL REFERENCES public.creators(id) ON DELETE CASCADE,
    channel_id UUID REFERENCES public.channels(id) ON DELETE SET NULL,
    import_batch_id UUID REFERENCES public.import_batches(id) ON DELETE SET NULL,

    platform public.platform_type NOT NULL DEFAULT 'youtube',
    platform_post_id TEXT,
    post_url TEXT,
    thumbnail_url TEXT,
    publication_type TEXT NOT NULL DEFAULT 'standard', -- 'standard', 'short/reel', 'vod', 'clip', 'teaser'
    published_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    status TEXT NOT NULL DEFAULT 'published',

    -- Métricas en la plataforma
    views_count BIGINT NOT NULL DEFAULT 0,
    likes_count INTEGER NOT NULL DEFAULT 0,
    comments_count INTEGER NOT NULL DEFAULT 0,
    shares_count INTEGER NOT NULL DEFAULT 0,
    watch_time_hours NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    estimated_revenue NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    engagement_rate NUMERIC(5, 2) NOT NULL DEFAULT 0.00,

    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

CREATE INDEX IF NOT EXISTS idx_vpub_video ON public.video_publications(video_id);
CREATE INDEX IF NOT EXISTS idx_vpub_org ON public.video_publications(organization_id);
CREATE INDEX IF NOT EXISTS idx_vpub_creator ON public.video_publications(creator_id);
CREATE INDEX IF NOT EXISTS idx_vpub_platform ON public.video_publications(platform);
CREATE INDEX IF NOT EXISTS idx_vpub_published_at ON public.video_publications(published_at DESC);

-- 3. Tabla Terciaria: Relaciones de Video (con otros Videos o Transmisiones en Vivo)
CREATE TABLE IF NOT EXISTS public.video_relations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
    source_video_id UUID NOT NULL REFERENCES public.videos(id) ON DELETE CASCADE,
    target_video_id UUID REFERENCES public.videos(id) ON DELETE CASCADE,
    target_session_id UUID REFERENCES public.streaming_sessions(id) ON DELETE CASCADE,
    
    relation_type TEXT NOT NULL DEFAULT 'derived_from_live', -- 'derived_from_live', 'continuation', 'sequel', 'clip', 'spin_off', 'reference'
    description TEXT,
    timestamp_start_seconds INTEGER,
    timestamp_end_seconds INTEGER,
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    
    -- Restricción: debe relacionarse o con un video o con una sesión
    CONSTRAINT check_relation_target CHECK (
        (target_video_id IS NOT NULL AND target_session_id IS NULL) OR
        (target_video_id IS NULL AND target_session_id IS NOT NULL) OR
        (target_video_id IS NOT NULL AND target_session_id IS NOT NULL)
    )
);

CREATE INDEX IF NOT EXISTS idx_vrel_org ON public.video_relations(organization_id);
CREATE INDEX IF NOT EXISTS idx_vrel_source ON public.video_relations(source_video_id);
CREATE INDEX IF NOT EXISTS idx_vrel_target_video ON public.video_relations(target_video_id);
CREATE INDEX IF NOT EXISTS idx_vrel_target_session ON public.video_relations(target_session_id);

-- 4. Habilitar RLS en las tres tablas
ALTER TABLE public.videos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.video_publications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.video_relations ENABLE ROW LEVEL SECURITY;

-- Políticas para `videos`
CREATE POLICY "Members can view videos in their org"
    ON public.videos FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Admins can manage videos"
    ON public.videos FOR ALL
    USING (public.is_org_admin(organization_id));

-- Políticas para `video_publications`
CREATE POLICY "Members can view video publications in their org"
    ON public.video_publications FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Admins can manage video publications"
    ON public.video_publications FOR ALL
    USING (public.is_org_admin(organization_id));

-- Políticas para `video_relations`
CREATE POLICY "Members can view video relations in their org"
    ON public.video_relations FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Admins can manage video relations"
    ON public.video_relations FOR ALL
    USING (public.is_org_admin(organization_id));

-- 5. Migrar datos existentes si la tabla anterior published_videos tenía registros
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'published_videos') THEN
        -- Insertar videos en la tabla master
        INSERT INTO public.videos (id, organization_id, creator_id, title, duration_seconds, status, created_at, updated_at)
        SELECT 
            id, 
            organization_id, 
            creator_id, 
            title, 
            duration_seconds, 
            'published', 
            created_at, 
            updated_at
        FROM public.published_videos
        ON CONFLICT (id) DO NOTHING;

        -- Insertar publicaciones iniciales
        INSERT INTO public.video_publications (
            id, video_id, organization_id, creator_id, channel_id, import_batch_id,
            platform, post_url, thumbnail_url, published_at,
            views_count, likes_count, comments_count, shares_count, estimated_revenue,
            created_at, updated_at
        )
        SELECT 
            id, 
            id, -- usa el mismo id o gen_random_uuid()
            organization_id, 
            creator_id, 
            channel_id, 
            import_batch_id,
            platform, 
            video_url, 
            thumbnail_url, 
            published_at,
            views_count, 
            likes_count, 
            comments_count, 
            shares_count, 
            estimated_revenue,
            created_at, 
            updated_at
        FROM public.published_videos
        ON CONFLICT (id) DO NOTHING;
    END IF;
END $$;

-- 6. Actualizar Vista Materializada mv_creator_performance_summary
DROP MATERIALIZED VIEW IF EXISTS public.mv_creator_performance_summary;

CREATE MATERIALIZED VIEW public.mv_creator_performance_summary AS
SELECT
    c.id AS creator_id,
    c.organization_id,
    c.display_name,
    c.handle,
    c.primary_platform,
    c.status,
    -- Métricas de streaming
    COALESCE(COUNT(DISTINCT s.id), 0)::INTEGER AS total_streams,
    COALESCE(SUM(s.duration_seconds), 0)::BIGINT AS total_stream_seconds,
    COALESCE(ROUND(SUM(s.duration_seconds)::numeric / 3600.0, 2), 0.00) AS total_hours_streamed,
    COALESCE(ROUND(AVG(s.avg_ccv), 0), 0)::INTEGER AS overall_avg_ccv,
    COALESCE(MAX(s.peak_viewers), 0)::INTEGER AS max_peak_viewers,
    COALESCE(SUM(s.total_earnings), 0.00)::NUMERIC(12, 2) AS total_stream_earnings,
    -- Métricas de videos y publicaciones
    COALESCE(COUNT(DISTINCT v.id), 0)::INTEGER AS total_videos,
    COALESCE(SUM(vp.views_count), 0)::BIGINT AS total_video_views,
    COALESCE(SUM(vp.likes_count), 0)::BIGINT AS total_video_likes,
    COALESCE(SUM(vp.estimated_revenue), 0.00)::NUMERIC(12, 2) AS total_video_earnings,
    -- Totales consolidados
    COALESCE(SUM(s.total_earnings), 0.00) + COALESCE(SUM(vp.estimated_revenue), 0.00) AS total_combined_revenue,
    now() AS last_refreshed_at
FROM public.creators c
LEFT JOIN public.streaming_sessions s ON s.creator_id = c.id
LEFT JOIN public.videos v ON v.creator_id = c.id
LEFT JOIN public.video_publications vp ON vp.video_id = v.id
GROUP BY c.id, c.organization_id, c.display_name, c.handle, c.primary_platform, c.status;

CREATE UNIQUE INDEX idx_mv_creator_perf_id ON public.mv_creator_performance_summary(creator_id);

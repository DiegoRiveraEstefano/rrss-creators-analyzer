-- ==============================================================================
-- Migration: 20260904000005_published_videos_and_materialized_views.sql
-- Description: Tabla de videos subidos (YouTube, TikTok, VODs), Vistas Materializadas y Funciones
-- ==============================================================================

-- 1. Tabla de Videos Publicados / Subidos
CREATE TABLE public.published_videos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
    creator_id UUID NOT NULL REFERENCES public.creators(id) ON DELETE CASCADE,
    channel_id UUID REFERENCES public.channels(id) ON DELETE SET NULL,
    import_batch_id UUID REFERENCES public.import_batches(id) ON DELETE SET NULL,

    title TEXT NOT NULL,
    platform public.platform_type NOT NULL DEFAULT 'youtube',
    video_url TEXT,
    thumbnail_url TEXT,
    published_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    duration_seconds INTEGER NOT NULL DEFAULT 0,

    -- Métricas de rendimiento
    views_count BIGINT NOT NULL DEFAULT 0,
    likes_count INTEGER NOT NULL DEFAULT 0,
    comments_count INTEGER NOT NULL DEFAULT 0,
    shares_count INTEGER NOT NULL DEFAULT 0,
    estimated_revenue NUMERIC(10, 2) NOT NULL DEFAULT 0.00,

    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

CREATE INDEX idx_videos_org ON public.published_videos(organization_id);
CREATE INDEX idx_videos_creator ON public.published_videos(creator_id);
CREATE INDEX idx_videos_published_at ON public.published_videos(published_at DESC);

-- Habilitar RLS en published_videos
ALTER TABLE public.published_videos ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Managers can view all videos, creators only their own"
    ON public.published_videos FOR SELECT
    USING (
        public.is_org_admin(organization_id)
        OR creator_id IN (SELECT public.get_user_creator_ids(organization_id))
    );

CREATE POLICY "Admins can manage published videos"
    ON public.published_videos FOR ALL
    USING (public.is_org_admin(organization_id));

-- 2. Vista Materializada: Rendimiento Consolidado por Creador (Streams + Videos)
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
    -- Métricas de videos
    COALESCE(COUNT(DISTINCT v.id), 0)::INTEGER AS total_videos,
    COALESCE(SUM(v.views_count), 0)::BIGINT AS total_video_views,
    COALESCE(SUM(v.likes_count), 0)::BIGINT AS total_video_likes,
    COALESCE(SUM(v.estimated_revenue), 0.00)::NUMERIC(12, 2) AS total_video_earnings,
    -- Totales consolidados
    COALESCE(SUM(s.total_earnings), 0.00) + COALESCE(SUM(v.estimated_revenue), 0.00) AS total_combined_revenue,
    now() AS last_refreshed_at
FROM public.creators c
LEFT JOIN public.streaming_sessions s ON s.creator_id = c.id
LEFT JOIN public.published_videos v ON v.creator_id = c.id
GROUP BY c.id, c.organization_id, c.display_name, c.handle, c.primary_platform, c.status;

-- Índice único requerido para CONCURRENT REFRESH
CREATE UNIQUE INDEX idx_mv_creator_perf_id ON public.mv_creator_performance_summary(creator_id);

-- 3. Vista Materializada: Rendimiento por Categoría y Plataforma
CREATE MATERIALIZED VIEW public.mv_platform_category_stats AS
SELECT
    s.organization_id,
    s.platform,
    COALESCE(s.game_or_category, 'General') AS category_name,
    COUNT(s.id)::INTEGER AS session_count,
    ROUND(SUM(s.duration_seconds)::numeric / 3600.0, 2) AS total_hours,
    ROUND(AVG(s.avg_ccv), 0)::INTEGER AS avg_ccv,
    MAX(s.peak_viewers)::INTEGER AS max_peak,
    SUM(s.total_earnings)::NUMERIC(12, 2) AS total_revenue
FROM public.streaming_sessions s
GROUP BY s.organization_id, s.platform, s.game_or_category;

CREATE INDEX idx_mv_category_org ON public.mv_platform_category_stats(organization_id);

-- 4. Función para refrescar las vistas materializadas
CREATE OR REPLACE FUNCTION public.refresh_creator_analytics_mv()
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY public.mv_creator_performance_summary;
    REFRESH MATERIALIZED VIEW public.mv_platform_category_stats;
END;
$$;

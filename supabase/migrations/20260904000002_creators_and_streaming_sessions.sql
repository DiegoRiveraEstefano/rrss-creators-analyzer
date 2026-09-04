-- ==============================================================================
-- Migration: 20260904000002_creators_and_streaming_sessions.sql
-- Description: Creadores, canales de plataforma y sesiones de streaming normalizadas
-- ==============================================================================

-- 1. Creadores asociados a una Organización / Agencia
CREATE TABLE public.creators (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL, -- Si el creador tiene cuenta de usuario
    display_name TEXT NOT NULL,
    handle TEXT NOT NULL,
    avatar_url TEXT,
    bio TEXT,
    primary_platform public.platform_type NOT NULL DEFAULT 'twitch',
    status public.creator_status NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 2. Canales de plataforma específicos para cada creador
CREATE TABLE public.channels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    creator_id UUID NOT NULL REFERENCES public.creators(id) ON DELETE CASCADE,
    platform public.platform_type NOT NULL,
    platform_channel_id TEXT NOT NULL,
    channel_url TEXT,
    followers_count INTEGER NOT NULL DEFAULT 0,
    subscribers_count INTEGER NOT NULL DEFAULT 0,
    is_live BOOLEAN NOT NULL DEFAULT false,
    last_synced_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    UNIQUE(creator_id, platform, platform_channel_id)
);

-- 3. Lotes de Importación (declarada aquí para FK en streaming_sessions)
CREATE TABLE public.import_batches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
    uploaded_by UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    filename TEXT NOT NULL,
    source_platform public.platform_type NOT NULL DEFAULT 'twitch',
    total_rows INTEGER NOT NULL DEFAULT 0,
    valid_rows INTEGER NOT NULL DEFAULT 0,
    error_count INTEGER NOT NULL DEFAULT 0,
    status public.import_status NOT NULL DEFAULT 'completed',
    error_summary JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 4. Sesiones de Streaming y Métricas Analíticas Normalizadas
CREATE TABLE public.streaming_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
    creator_id UUID NOT NULL REFERENCES public.creators(id) ON DELETE CASCADE,
    channel_id UUID REFERENCES public.channels(id) ON DELETE SET NULL,
    import_batch_id UUID REFERENCES public.import_batches(id) ON DELETE SET NULL,
    
    session_title TEXT NOT NULL DEFAULT 'Live Stream',
    game_or_category TEXT DEFAULT 'Just Chatting',
    platform public.platform_type NOT NULL DEFAULT 'twitch',
    
    streamed_at TIMESTAMPTZ NOT NULL,
    duration_seconds INTEGER NOT NULL DEFAULT 0,
    hours_streamed NUMERIC(6, 2) GENERATED ALWAYS AS (ROUND((duration_seconds::numeric / 3600.0), 2)) STORED,
    
    peak_viewers INTEGER NOT NULL DEFAULT 0,
    avg_ccv INTEGER NOT NULL DEFAULT 0,
    chat_messages_count INTEGER NOT NULL DEFAULT 0,
    new_followers INTEGER NOT NULL DEFAULT 0,
    
    -- Métricas financieras
    ad_revenue NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    donations_revenue NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    subs_revenue NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    total_earnings NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    earnings_per_hour NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- Índices de alto rendimiento para analítica y agregaciones
CREATE INDEX idx_creators_org ON public.creators(organization_id);
CREATE INDEX idx_creators_user ON public.creators(user_id);
CREATE INDEX idx_channels_creator ON public.channels(creator_id);
CREATE INDEX idx_sessions_org ON public.streaming_sessions(organization_id);
CREATE INDEX idx_sessions_creator ON public.streaming_sessions(creator_id);
CREATE INDEX idx_sessions_streamed_at ON public.streaming_sessions(streamed_at DESC);
CREATE INDEX idx_sessions_org_date ON public.streaming_sessions(organization_id, streamed_at DESC);

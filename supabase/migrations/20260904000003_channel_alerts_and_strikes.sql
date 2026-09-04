-- ==============================================================================
-- Migration: 20260904000003_channel_alerts_and_strikes.sql
-- Description: Sistema de alertas, advertencias y sanciones de canales (TOS, DMCA)
-- ==============================================================================

-- Tabla de Alertas y Sanciones de Canal
CREATE TABLE public.channel_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
    creator_id UUID NOT NULL REFERENCES public.creators(id) ON DELETE CASCADE,
    channel_id UUID REFERENCES public.channels(id) ON DELETE SET NULL,
    
    alert_type TEXT NOT NULL, -- 'dmca_strike', 'tos_violation', 'unusual_drop', 'suspicious_traffic'
    severity public.alert_severity NOT NULL DEFAULT 'warning',
    status public.alert_status NOT NULL DEFAULT 'active',
    
    title TEXT NOT NULL,
    description TEXT,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    resolved_at TIMESTAMPTZ,
    resolution_notes TEXT,
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

CREATE INDEX idx_alerts_org ON public.channel_alerts(organization_id);
CREATE INDEX idx_alerts_creator ON public.channel_alerts(creator_id);
CREATE INDEX idx_alerts_status ON public.channel_alerts(status);
CREATE INDEX idx_alerts_occurred_at ON public.channel_alerts(occurred_at DESC);

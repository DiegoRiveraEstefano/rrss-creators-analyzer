-- ==============================================================================
-- Migration: 20260904000009_secure_views_revoke_mv_and_pg_cron.sql
-- Description:
--   1. Vistas SQL envolventes seguras con WITH (security_invoker = true) y filtro
--      multi-tenant WHERE organization_id IN (SELECT public.get_user_org_ids())
--   2. Revocación de permisos de lectura directa en las vistas materializadas (mv_*)
--      para asegurar que solo se lean a través de las vistas seguras (v_*).
--   3. Eliminación de triggers transaccionales en tablas para evitar contención.
--   4. Programación periódica del refresco concurrente de vistas con pg_cron.
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. Crear Vistas SQL Envolventes Seguras (Multi-Tenant con security_invoker = true)
-- ------------------------------------------------------------------------------

-- 1.1 Vista Segura: Rendimiento de Creadores
CREATE OR REPLACE VIEW public.v_creator_performance_summary
WITH (security_invoker = true) AS
SELECT *
FROM public.mv_creator_performance_summary
WHERE organization_id IN (SELECT public.get_user_org_ids());

-- 1.2 Vista Segura: Rendimiento por Plataforma
CREATE OR REPLACE VIEW public.v_platform_performance_summary
WITH (security_invoker = true) AS
SELECT *
FROM public.mv_platform_performance_summary
WHERE organization_id IN (SELECT public.get_user_org_ids());

-- 1.3 Vista Segura: Rendimiento por Categoría y Plataforma
CREATE OR REPLACE VIEW public.v_platform_category_stats
WITH (security_invoker = true) AS
SELECT *
FROM public.mv_platform_category_stats
WHERE organization_id IN (SELECT public.get_user_org_ids());

-- 1.4 Vista Segura: Resumen Mensual de Ingresos y Métricas
CREATE OR REPLACE VIEW public.v_monthly_revenue_summary
WITH (security_invoker = true) AS
SELECT *
FROM public.mv_monthly_revenue_summary
WHERE organization_id IN (SELECT public.get_user_org_ids());

-- 1.5 Vista Segura: Métricas por Formato de Contenido por Creador
CREATE OR REPLACE VIEW public.v_creator_content_type_metrics
WITH (security_invoker = true) AS
SELECT *
FROM public.mv_creator_content_type_metrics
WHERE organization_id IN (SELECT public.get_user_org_ids());

-- 1.6 Actualizar v_creator_overall_rankings para filtrar estrictamente por organización
CREATE OR REPLACE VIEW public.v_creator_overall_rankings
WITH (security_invoker = true) AS
SELECT
    m.creator_id,
    m.organization_id,
    m.display_name,
    m.handle,
    m.primary_platform,
    m.status,
    m.total_combined_revenue,
    m.total_stream_earnings,
    m.total_video_earnings,
    m.overall_avg_ccv,
    m.max_peak_viewers,
    m.total_hours_streamed,
    m.total_streams,
    m.total_video_views,
    m.total_publications,
    DENSE_RANK() OVER (PARTITION BY m.organization_id ORDER BY m.total_combined_revenue DESC) AS revenue_rank,
    DENSE_RANK() OVER (PARTITION BY m.organization_id ORDER BY m.overall_avg_ccv DESC) AS ccv_rank,
    DENSE_RANK() OVER (PARTITION BY m.organization_id ORDER BY m.total_hours_streamed DESC) AS hours_rank
FROM public.mv_creator_performance_summary m
WHERE m.organization_id IN (SELECT public.get_user_org_ids());


-- ------------------------------------------------------------------------------
-- 2. Revocar Permisos Directos en Vistas Materializadas y Conceder en Vistas Seguras
-- ------------------------------------------------------------------------------

-- Revocar lectura directa sobre las vistas materializadas físicas a roles de cliente
REVOKE SELECT ON public.mv_creator_performance_summary FROM anon, authenticated;
REVOKE SELECT ON public.mv_platform_category_stats FROM anon, authenticated;
REVOKE SELECT ON public.mv_platform_performance_summary FROM anon, authenticated;
REVOKE SELECT ON public.mv_monthly_revenue_summary FROM anon, authenticated;
REVOKE SELECT ON public.mv_creator_content_type_metrics FROM anon, authenticated;

-- Conceder permisos de lectura a las vistas seguras
GRANT SELECT ON public.v_creator_performance_summary TO authenticated, anon;
GRANT SELECT ON public.v_platform_performance_summary TO authenticated, anon;
GRANT SELECT ON public.v_platform_category_stats TO authenticated, anon;
GRANT SELECT ON public.v_monthly_revenue_summary TO authenticated, anon;
GRANT SELECT ON public.v_creator_content_type_metrics TO authenticated, anon;

GRANT SELECT ON public.v_daily_stream_analytics TO authenticated, anon;
GRANT SELECT ON public.v_creator_overall_rankings TO authenticated, anon;
GRANT SELECT ON public.v_video_publication_details TO authenticated, anon;
GRANT SELECT ON public.v_recent_channel_activity TO authenticated, anon;


-- ------------------------------------------------------------------------------
-- 3. Eliminar Triggers de Tabla para Evitar Contención en Escrituras
-- ------------------------------------------------------------------------------

DROP TRIGGER IF EXISTS trg_refresh_mv_on_sessions ON public.streaming_sessions;
DROP TRIGGER IF EXISTS trg_refresh_mv_on_publications ON public.video_publications;
DROP TRIGGER IF EXISTS trg_refresh_mv_on_videos ON public.videos;
DROP TRIGGER IF EXISTS trg_refresh_mv_on_creators ON public.creators;
DROP FUNCTION IF EXISTS public.trg_fn_refresh_materialized_views();


-- ------------------------------------------------------------------------------
-- 4. Programación de Tareas Periódicas con pg_cron
-- ------------------------------------------------------------------------------

-- Habilitar extensión pg_cron (si el entorno lo permite)
CREATE EXTENSION IF NOT EXISTS pg_cron;

DO $$
BEGIN
    -- Verificar si la extensión pg_cron está instalada y activa
    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_cron') THEN
        -- Desprogramar job previo para mantener idempotencia si existía
        IF EXISTS (SELECT 1 FROM cron.job WHERE jobname = 'refresh-all-materialized-views') THEN
            PERFORM cron.unschedule('refresh-all-materialized-views');
        END IF;

        -- Programar refresco concurrente de todas las vistas cada 15 minutos
        PERFORM cron.schedule(
            'refresh-all-materialized-views',
            '*/15 * * * *',
            'SELECT public.refresh_all_materialized_views_concurrently();'
        );
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Nota: pg_cron no está disponible en este entorno o requiere permisos de superusuario: %', SQLERRM;
END $$;

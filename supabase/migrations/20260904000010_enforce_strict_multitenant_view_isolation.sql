-- ==============================================================================
-- Migration: 20260904000010_enforce_strict_multitenant_view_isolation.sql
-- Description:
--   1. Recrear Vistas Materializadas y Vistas SQL con JOINs compuestos que igualan
--      explícitamente tanto los IDs de entidad como el organization_id.
--   2. Asegurar que las Vistas SQL Envolventes filtren estrictamente por las
--      organizaciones del usuario autenticado.
--   3. Blindar funciones y accesos multi-tenant.
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. Recrear Vistas Materializadas con JOINs Aislados por Organización
-- ------------------------------------------------------------------------------

-- 1.1 mv_creator_performance_summary
DROP MATERIALIZED VIEW IF EXISTS public.mv_creator_performance_summary CASCADE;

CREATE MATERIALIZED VIEW public.mv_creator_performance_summary AS
SELECT
    c.id AS creator_id,
    c.organization_id,
    c.display_name,
    c.handle,
    c.primary_platform,
    c.status,
    -- Métricas de streaming en vivo
    COALESCE(COUNT(DISTINCT s.id), 0)::INTEGER AS total_streams,
    COALESCE(SUM(s.duration_seconds), 0)::BIGINT AS total_stream_seconds,
    COALESCE(ROUND(SUM(s.duration_seconds)::numeric / 3600.0, 2), 0.00) AS total_hours_streamed,
    COALESCE(ROUND(AVG(s.avg_ccv), 0), 0)::INTEGER AS overall_avg_ccv,
    COALESCE(MAX(s.peak_viewers), 0)::INTEGER AS max_peak_viewers,
    COALESCE(SUM(s.total_earnings), 0.00)::NUMERIC(12, 2) AS total_stream_earnings,
    -- Métricas de videos y publicaciones
    COALESCE(COUNT(DISTINCT v.id), 0)::INTEGER AS total_videos,
    COALESCE(COUNT(DISTINCT vp.id), 0)::INTEGER AS total_publications,
    COALESCE(SUM(vp.views_count), 0)::BIGINT AS total_video_views,
    COALESCE(SUM(vp.likes_count), 0)::BIGINT AS total_video_likes,
    COALESCE(SUM(vp.comments_count), 0)::BIGINT AS total_video_comments,
    COALESCE(SUM(vp.shares_count), 0)::BIGINT AS total_video_shares,
    COALESCE(SUM(vp.estimated_revenue), 0.00)::NUMERIC(12, 2) AS total_video_earnings,
    -- Totales financieros consolidados
    COALESCE(SUM(s.total_earnings), 0.00) + COALESCE(SUM(vp.estimated_revenue), 0.00) AS total_combined_revenue,
    now() AS last_refreshed_at
FROM public.creators c
LEFT JOIN public.streaming_sessions s 
    ON s.creator_id = c.id AND s.organization_id = c.organization_id
LEFT JOIN public.videos v 
    ON v.creator_id = c.id AND v.organization_id = c.organization_id
LEFT JOIN public.video_publications vp 
    ON vp.video_id = v.id AND vp.organization_id = c.organization_id
GROUP BY c.id, c.organization_id, c.display_name, c.handle, c.primary_platform, c.status;

CREATE UNIQUE INDEX idx_mv_creator_perf_id ON public.mv_creator_performance_summary(creator_id);
CREATE INDEX idx_mv_creator_perf_org ON public.mv_creator_performance_summary(organization_id);

-- 1.2 mv_platform_category_stats
DROP MATERIALIZED VIEW IF EXISTS public.mv_platform_category_stats CASCADE;

CREATE MATERIALIZED VIEW public.mv_platform_category_stats AS
SELECT
    s.organization_id,
    s.platform,
    COALESCE(s.game_or_category, 'General') AS category_name,
    COUNT(s.id)::INTEGER AS session_count,
    ROUND(SUM(s.duration_seconds)::numeric / 3600.0, 2) AS total_hours,
    ROUND(AVG(s.avg_ccv), 0)::INTEGER AS avg_ccv,
    MAX(s.peak_viewers)::INTEGER AS max_peak,
    SUM(s.total_earnings)::NUMERIC(12, 2) AS total_revenue,
    now() AS last_refreshed_at
FROM public.streaming_sessions s
GROUP BY s.organization_id, s.platform, COALESCE(s.game_or_category, 'General');

CREATE UNIQUE INDEX idx_mv_platform_cat_unique ON public.mv_platform_category_stats(organization_id, platform, category_name);
CREATE INDEX idx_mv_category_org ON public.mv_platform_category_stats(organization_id);

-- 1.3 mv_platform_performance_summary
DROP MATERIALIZED VIEW IF EXISTS public.mv_platform_performance_summary CASCADE;

CREATE MATERIALIZED VIEW public.mv_platform_performance_summary AS
WITH stream_agg AS (
    SELECT
        s.organization_id,
        s.platform,
        COUNT(DISTINCT s.creator_id)::INTEGER AS live_creators_count,
        COUNT(s.id)::INTEGER AS total_streams,
        COALESCE(ROUND(SUM(s.duration_seconds)::numeric / 3600.0, 2), 0.00) AS total_stream_hours,
        COALESCE(ROUND(AVG(s.avg_ccv), 0), 0)::INTEGER AS avg_ccv,
        COALESCE(MAX(s.peak_viewers), 0)::INTEGER AS max_peak_viewers,
        COALESCE(SUM(s.ad_revenue), 0.00)::NUMERIC(12, 2) AS stream_ad_revenue,
        COALESCE(SUM(s.subs_revenue), 0.00)::NUMERIC(12, 2) AS stream_subs_revenue,
        COALESCE(SUM(s.donations_revenue), 0.00)::NUMERIC(12, 2) AS stream_donations_revenue,
        COALESCE(SUM(s.total_earnings), 0.00)::NUMERIC(12, 2) AS total_stream_earnings
    FROM public.streaming_sessions s
    GROUP BY s.organization_id, s.platform
),
video_agg AS (
    SELECT
        vp.organization_id,
        vp.platform,
        COUNT(DISTINCT vp.creator_id)::INTEGER AS video_creators_count,
        COUNT(vp.id)::INTEGER AS total_publications,
        COALESCE(SUM(vp.views_count), 0)::BIGINT AS total_video_views,
        COALESCE(SUM(vp.likes_count), 0)::BIGINT AS total_video_likes,
        COALESCE(SUM(vp.comments_count), 0)::BIGINT AS total_video_comments,
        COALESCE(SUM(vp.shares_count), 0)::BIGINT AS total_video_shares,
        COALESCE(ROUND(AVG(vp.engagement_rate), 2), 0.00) AS avg_engagement_rate,
        COALESCE(SUM(vp.estimated_revenue), 0.00)::NUMERIC(12, 2) AS total_video_earnings
    FROM public.video_publications vp
    GROUP BY vp.organization_id, vp.platform
),
platforms_list AS (
    SELECT DISTINCT organization_id, platform FROM public.streaming_sessions
    UNION
    SELECT DISTINCT organization_id, platform FROM public.video_publications
    UNION
    SELECT organization_id, primary_platform AS platform FROM public.creators
)
SELECT
    p.organization_id,
    p.platform,
    GREATEST(COALESCE(sa.live_creators_count, 0), COALESCE(va.video_creators_count, 0))::INTEGER AS total_creators,
    COALESCE(sa.total_streams, 0)::INTEGER AS total_streams,
    COALESCE(sa.total_stream_hours, 0.00) AS total_stream_hours,
    COALESCE(sa.avg_ccv, 0)::INTEGER AS avg_ccv,
    COALESCE(sa.max_peak_viewers, 0)::INTEGER AS max_peak_viewers,
    COALESCE(sa.stream_ad_revenue, 0.00)::NUMERIC(12, 2) AS stream_ad_revenue,
    COALESCE(sa.stream_subs_revenue, 0.00)::NUMERIC(12, 2) AS stream_subs_revenue,
    COALESCE(sa.stream_donations_revenue, 0.00)::NUMERIC(12, 2) AS stream_donations_revenue,
    COALESCE(sa.total_stream_earnings, 0.00)::NUMERIC(12, 2) AS total_stream_earnings,
    COALESCE(va.total_publications, 0)::INTEGER AS total_publications,
    COALESCE(va.total_video_views, 0)::BIGINT AS total_video_views,
    COALESCE(va.total_video_likes, 0)::BIGINT AS total_video_likes,
    COALESCE(va.total_video_comments, 0)::BIGINT AS total_video_comments,
    COALESCE(va.total_video_shares, 0)::BIGINT AS total_video_shares,
    COALESCE(va.avg_engagement_rate, 0.00) AS avg_engagement_rate,
    COALESCE(va.total_video_earnings, 0.00)::NUMERIC(12, 2) AS total_video_earnings,
    (COALESCE(sa.total_stream_earnings, 0.00) + COALESCE(va.total_video_earnings, 0.00))::NUMERIC(12, 2) AS total_combined_revenue,
    now() AS last_refreshed_at
FROM platforms_list p
LEFT JOIN stream_agg sa ON sa.organization_id = p.organization_id AND sa.platform = p.platform
LEFT JOIN video_agg va ON va.organization_id = p.organization_id AND va.platform = p.platform;

CREATE UNIQUE INDEX idx_mv_plat_perf_unique ON public.mv_platform_performance_summary(organization_id, platform);
CREATE INDEX idx_mv_plat_perf_org ON public.mv_platform_performance_summary(organization_id);

-- 1.4 mv_monthly_revenue_summary
DROP MATERIALIZED VIEW IF EXISTS public.mv_monthly_revenue_summary CASCADE;

CREATE MATERIALIZED VIEW public.mv_monthly_revenue_summary AS
WITH monthly_streams AS (
    SELECT
        organization_id,
        EXTRACT(YEAR FROM streamed_at)::INTEGER AS period_year,
        EXTRACT(MONTH FROM streamed_at)::INTEGER AS period_month,
        TO_CHAR(streamed_at, 'YYYY-MM') AS period_label,
        COUNT(id)::INTEGER AS total_streams,
        ROUND(SUM(duration_seconds)::numeric / 3600.0, 2) AS total_stream_hours,
        ROUND(AVG(avg_ccv), 0)::INTEGER AS avg_ccv,
        MAX(peak_viewers)::INTEGER AS peak_viewers,
        SUM(ad_revenue)::NUMERIC(12, 2) AS stream_ad_revenue,
        SUM(subs_revenue)::NUMERIC(12, 2) AS stream_subs_revenue,
        SUM(donations_revenue)::NUMERIC(12, 2) AS stream_donations_revenue,
        SUM(total_earnings)::NUMERIC(12, 2) AS total_stream_earnings
    FROM public.streaming_sessions
    GROUP BY organization_id, EXTRACT(YEAR FROM streamed_at), EXTRACT(MONTH FROM streamed_at), TO_CHAR(streamed_at, 'YYYY-MM')
),
monthly_videos AS (
    SELECT
        organization_id,
        EXTRACT(YEAR FROM published_at)::INTEGER AS period_year,
        EXTRACT(MONTH FROM published_at)::INTEGER AS period_month,
        TO_CHAR(published_at, 'YYYY-MM') AS period_label,
        COUNT(id)::INTEGER AS total_publications,
        SUM(views_count)::BIGINT AS total_video_views,
        SUM(likes_count)::BIGINT AS total_video_likes,
        SUM(estimated_revenue)::NUMERIC(12, 2) AS total_video_earnings
    FROM public.video_publications
    GROUP BY organization_id, EXTRACT(YEAR FROM published_at), EXTRACT(MONTH FROM published_at), TO_CHAR(published_at, 'YYYY-MM')
),
periods AS (
    SELECT DISTINCT organization_id, period_year, period_month, period_label FROM monthly_streams
    UNION
    SELECT DISTINCT organization_id, period_year, period_month, period_label FROM monthly_videos
)
SELECT
    p.organization_id,
    p.period_year,
    p.period_month,
    p.period_label,
    COALESCE(ms.total_streams, 0)::INTEGER AS total_streams,
    COALESCE(ms.total_stream_hours, 0.00) AS total_stream_hours,
    COALESCE(ms.avg_ccv, 0)::INTEGER AS avg_ccv,
    COALESCE(ms.peak_viewers, 0)::INTEGER AS peak_viewers,
    COALESCE(ms.stream_ad_revenue, 0.00)::NUMERIC(12, 2) AS stream_ad_revenue,
    COALESCE(ms.stream_subs_revenue, 0.00)::NUMERIC(12, 2) AS stream_subs_revenue,
    COALESCE(ms.stream_donations_revenue, 0.00)::NUMERIC(12, 2) AS stream_donations_revenue,
    COALESCE(ms.total_stream_earnings, 0.00)::NUMERIC(12, 2) AS total_stream_earnings,
    COALESCE(mv.total_publications, 0)::INTEGER AS total_publications,
    COALESCE(mv.total_video_views, 0)::BIGINT AS total_video_views,
    COALESCE(mv.total_video_likes, 0)::BIGINT AS total_video_likes,
    COALESCE(mv.total_video_earnings, 0.00)::NUMERIC(12, 2) AS total_video_earnings,
    (COALESCE(ms.total_stream_earnings, 0.00) + COALESCE(mv.total_video_earnings, 0.00))::NUMERIC(12, 2) AS total_combined_revenue,
    now() AS last_refreshed_at
FROM periods p
LEFT JOIN monthly_streams ms ON ms.organization_id = p.organization_id AND ms.period_year = p.period_year AND ms.period_month = p.period_month
LEFT JOIN monthly_videos mv ON mv.organization_id = p.organization_id AND mv.period_year = p.period_year AND mv.period_month = p.period_month;

CREATE UNIQUE INDEX idx_mv_monthly_rev_unique ON public.mv_monthly_revenue_summary(organization_id, period_year, period_month);
CREATE INDEX idx_mv_monthly_rev_org ON public.mv_monthly_revenue_summary(organization_id);

-- 1.5 mv_creator_content_type_metrics
DROP MATERIALIZED VIEW IF EXISTS public.mv_creator_content_type_metrics CASCADE;

CREATE MATERIALIZED VIEW public.mv_creator_content_type_metrics AS
SELECT
    vp.creator_id,
    vp.organization_id,
    c.display_name AS creator_name,
    c.handle AS creator_handle,
    vp.platform,
    COALESCE(vp.publication_type, 'standard') AS publication_type,
    COUNT(vp.id)::INTEGER AS total_publications,
    COALESCE(SUM(vp.views_count), 0)::BIGINT AS total_views,
    COALESCE(ROUND(AVG(vp.views_count), 0), 0)::BIGINT AS avg_views_per_video,
    COALESCE(SUM(vp.likes_count), 0)::BIGINT AS total_likes,
    COALESCE(SUM(vp.comments_count), 0)::BIGINT AS total_comments,
    COALESCE(SUM(vp.shares_count), 0)::BIGINT AS total_shares,
    COALESCE(ROUND(AVG(vp.engagement_rate), 2), 0.00) AS avg_engagement_rate,
    COALESCE(SUM(vp.estimated_revenue), 0.00)::NUMERIC(12, 2) AS total_revenue,
    COALESCE(ROUND(AVG(vp.estimated_revenue), 2), 0.00)::NUMERIC(10, 2) AS avg_revenue_per_video,
    now() AS last_refreshed_at
FROM public.video_publications vp
JOIN public.creators c 
    ON c.id = vp.creator_id AND c.organization_id = vp.organization_id
GROUP BY vp.creator_id, vp.organization_id, c.display_name, c.handle, vp.platform, COALESCE(vp.publication_type, 'standard');

CREATE UNIQUE INDEX idx_mv_creator_content_unique ON public.mv_creator_content_type_metrics(creator_id, platform, publication_type);
CREATE INDEX idx_mv_creator_content_org ON public.mv_creator_content_type_metrics(organization_id);


-- ------------------------------------------------------------------------------
-- 2. Recrear Vistas SQL Seguras Envolventes y Vistas Estándar (Multi-Tenant Estricto)
-- ------------------------------------------------------------------------------

-- 2.1 v_creator_performance_summary
CREATE OR REPLACE VIEW public.v_creator_performance_summary
WITH (security_invoker = true) AS
SELECT *
FROM public.mv_creator_performance_summary
WHERE organization_id IN (SELECT public.get_user_org_ids());

-- 2.2 v_platform_performance_summary
CREATE OR REPLACE VIEW public.v_platform_performance_summary
WITH (security_invoker = true) AS
SELECT *
FROM public.mv_platform_performance_summary
WHERE organization_id IN (SELECT public.get_user_org_ids());

-- 2.3 v_platform_category_stats
CREATE OR REPLACE VIEW public.v_platform_category_stats
WITH (security_invoker = true) AS
SELECT *
FROM public.mv_platform_category_stats
WHERE organization_id IN (SELECT public.get_user_org_ids());

-- 2.4 v_monthly_revenue_summary
CREATE OR REPLACE VIEW public.v_monthly_revenue_summary
WITH (security_invoker = true) AS
SELECT *
FROM public.mv_monthly_revenue_summary
WHERE organization_id IN (SELECT public.get_user_org_ids());

-- 2.5 v_creator_content_type_metrics
CREATE OR REPLACE VIEW public.v_creator_content_type_metrics
WITH (security_invoker = true) AS
SELECT *
FROM public.mv_creator_content_type_metrics
WHERE organization_id IN (SELECT public.get_user_org_ids());

-- 2.6 v_creator_overall_rankings
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

-- 2.7 v_daily_stream_analytics
CREATE OR REPLACE VIEW public.v_daily_stream_analytics
WITH (security_invoker = true) AS
SELECT
    date_trunc('day', s.streamed_at)::DATE AS stream_date,
    s.organization_id,
    s.creator_id,
    c.display_name AS creator_name,
    c.handle AS creator_handle,
    s.platform,
    COUNT(s.id)::INTEGER AS session_count,
    ROUND(SUM(s.duration_seconds)::numeric / 3600.0, 2) AS total_hours_streamed,
    ROUND(AVG(s.avg_ccv), 0)::INTEGER AS avg_ccv,
    MAX(s.peak_viewers)::INTEGER AS max_peak_viewers,
    SUM(s.chat_messages_count)::BIGINT AS total_chat_messages,
    SUM(s.new_followers)::INTEGER AS total_new_followers,
    SUM(s.ad_revenue)::NUMERIC(10, 2) AS ad_revenue,
    SUM(s.subs_revenue)::NUMERIC(10, 2) AS subs_revenue,
    SUM(s.donations_revenue)::NUMERIC(10, 2) AS donations_revenue,
    SUM(s.total_earnings)::NUMERIC(10, 2) AS total_earnings,
    CASE
        WHEN SUM(s.duration_seconds) > 0
        THEN ROUND((SUM(s.total_earnings) / (SUM(s.duration_seconds)::numeric / 3600.0)), 2)
        ELSE 0.00
    END AS earnings_per_hour
FROM public.streaming_sessions s
JOIN public.creators c 
    ON c.id = s.creator_id AND c.organization_id = s.organization_id
WHERE s.organization_id IN (SELECT public.get_user_org_ids())
GROUP BY date_trunc('day', s.streamed_at)::DATE, s.organization_id, s.creator_id, c.display_name, c.handle, s.platform;

-- 2.8 v_video_publication_details
CREATE OR REPLACE VIEW public.v_video_publication_details
WITH (security_invoker = true) AS
SELECT
    vp.id AS publication_id,
    vp.video_id,
    vp.organization_id,
    vp.creator_id,
    c.display_name AS creator_name,
    c.handle AS creator_handle,
    v.title AS video_title,
    v.internal_name,
    v.category,
    v.duration_seconds,
    ROUND(v.duration_seconds::numeric / 60.0, 1) AS duration_minutes,
    v.production_cost,
    vp.platform,
    vp.publication_type,
    vp.post_url,
    vp.thumbnail_url,
    vp.published_at,
    vp.views_count,
    vp.likes_count,
    vp.comments_count,
    vp.shares_count,
    vp.engagement_rate,
    vp.watch_time_hours,
    vp.estimated_revenue,
    (vp.estimated_revenue - v.production_cost)::NUMERIC(10, 2) AS net_profit,
    CASE
        WHEN v.production_cost > 0
        THEN ROUND(((vp.estimated_revenue - v.production_cost) / v.production_cost) * 100.0, 2)
        ELSE NULL
    END AS roi_percentage,
    CASE
        WHEN vp.views_count > 0
        THEN ROUND((vp.estimated_revenue / (vp.views_count::numeric / 1000.0)), 2)
        ELSE 0.00
    END AS rpm_estimated
FROM public.video_publications vp
JOIN public.videos v 
    ON v.id = vp.video_id AND v.organization_id = vp.organization_id
JOIN public.creators c 
    ON c.id = vp.creator_id AND c.organization_id = vp.organization_id
WHERE vp.organization_id IN (SELECT public.get_user_org_ids());

-- 2.9 v_recent_channel_activity
CREATE OR REPLACE VIEW public.v_recent_channel_activity
WITH (security_invoker = true) AS
SELECT
    'stream' AS activity_type,
    s.id AS activity_id,
    s.organization_id,
    s.creator_id,
    c.display_name AS creator_name,
    s.platform,
    s.session_title AS title,
    s.game_or_category AS subtitle,
    s.streamed_at AS timestamp,
    s.total_earnings AS monetary_value,
    s.avg_ccv AS primary_metric,
    'CCV' AS metric_unit
FROM public.streaming_sessions s
JOIN public.creators c 
    ON c.id = s.creator_id AND c.organization_id = s.organization_id
WHERE s.organization_id IN (SELECT public.get_user_org_ids())
UNION ALL
SELECT
    'video' AS activity_type,
    vp.id AS activity_id,
    vp.organization_id,
    vp.creator_id,
    c.display_name AS creator_name,
    vp.platform,
    v.title AS title,
    vp.publication_type AS subtitle,
    vp.published_at AS timestamp,
    vp.estimated_revenue AS monetary_value,
    vp.views_count AS primary_metric,
    'Vistas' AS metric_unit
FROM public.video_publications vp
JOIN public.videos v 
    ON v.id = vp.video_id AND v.organization_id = vp.organization_id
JOIN public.creators c 
    ON c.id = vp.creator_id AND c.organization_id = vp.organization_id
WHERE vp.organization_id IN (SELECT public.get_user_org_ids())
UNION ALL
SELECT
    'alert' AS activity_type,
    a.id AS activity_id,
    a.organization_id,
    a.creator_id,
    c.display_name AS creator_name,
    'twitch'::public.platform_type AS platform,
    a.title AS title,
    a.severity::TEXT AS subtitle,
    a.occurred_at AS timestamp,
    0.00 AS monetary_value,
    0 AS primary_metric,
    a.status::TEXT AS metric_unit
FROM public.channel_alerts a
JOIN public.creators c 
    ON c.id = a.creator_id AND c.organization_id = a.organization_id
WHERE a.organization_id IN (SELECT public.get_user_org_ids());

-- ------------------------------------------------------------------------------
-- 3. Permisos Explícitos
-- ------------------------------------------------------------------------------
REVOKE SELECT ON public.mv_creator_performance_summary FROM anon, authenticated;
REVOKE SELECT ON public.mv_platform_category_stats FROM anon, authenticated;
REVOKE SELECT ON public.mv_platform_performance_summary FROM anon, authenticated;
REVOKE SELECT ON public.mv_monthly_revenue_summary FROM anon, authenticated;
REVOKE SELECT ON public.mv_creator_content_type_metrics FROM anon, authenticated;

GRANT SELECT ON public.v_creator_performance_summary TO authenticated, anon;
GRANT SELECT ON public.v_platform_performance_summary TO authenticated, anon;
GRANT SELECT ON public.v_platform_category_stats TO authenticated, anon;
GRANT SELECT ON public.v_monthly_revenue_summary TO authenticated, anon;
GRANT SELECT ON public.v_creator_content_type_metrics TO authenticated, anon;

GRANT SELECT ON public.v_daily_stream_analytics TO authenticated, anon;
GRANT SELECT ON public.v_creator_overall_rankings TO authenticated, anon;
GRANT SELECT ON public.v_video_publication_details TO authenticated, anon;
GRANT SELECT ON public.v_recent_channel_activity TO authenticated, anon;

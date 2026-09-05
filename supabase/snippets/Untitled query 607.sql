CREATE MATERIALIZED VIEW public.mv_platform_performance_summary
with(security_invoker = true) AS
WITH 
    stream_agg AS (
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
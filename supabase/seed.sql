-- ==============================================================================
-- Seed: supabase/seed.sql
-- Description: Datos de prueba para desarrollo y demostración de agencias y creadores
-- ==============================================================================

DO $$
DECLARE
    v_org_id UUID := 'a0000000-0000-0000-0000-000000000001';
    v_creator1_id UUID := 'c0000000-0000-0000-0000-000000000001';
    v_creator2_id UUID := 'c0000000-0000-0000-0000-000000000002';
    v_creator3_id UUID := 'c0000000-0000-0000-0000-000000000003';
    v_creator4_id UUID := 'c0000000-0000-0000-0000-000000000004';
    v_channel1_id UUID := 'b0000000-0000-0000-0000-000000000001';
    v_channel2_id UUID := 'b0000000-0000-0000-0000-000000000002';
    v_channel3_id UUID := 'b0000000-0000-0000-0000-000000000003';
    v_channel4_id UUID := 'b0000000-0000-0000-0000-000000000004';

    v_vid1_id UUID := 'd0000000-0000-0000-0000-000000000001';
    v_vid2_id UUID := 'd0000000-0000-0000-0000-000000000002';
    v_vid3_id UUID := 'd0000000-0000-0000-0000-000000000003';
    v_vid4_id UUID := 'd0000000-0000-0000-0000-000000000004';
    v_vid5_id UUID := 'd0000000-0000-0000-0000-000000000005';
BEGIN
    -- 1. Crear Organización Demo
    INSERT INTO public.organizations (id, name, slug, plan)
    VALUES (v_org_id, 'Koa Talent Management', 'koa-talent', 'enterprise')
    ON CONFLICT (slug) DO NOTHING;

    -- 2. Insertar Creadores del Roster
    INSERT INTO public.creators (id, organization_id, display_name, handle, avatar_url, primary_platform, status, bio)
    VALUES
        (v_creator1_id, v_org_id, 'Ibai Llanos', 'ibai', 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80', 'twitch', 'active', 'Streamer de eventos especiales, League of Legends y Just Chatting'),
        (v_creator2_id, v_org_id, 'Samy Rivera', 'rivers_gg', 'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=150&auto=format&fit=crop&q=80', 'twitch', 'active', 'Creadora de contenido y presidenta de PIO FC'),
        (v_creator3_id, v_org_id, 'Juan Guarnizo', 'juansguarnizo', 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80', 'twitch', 'active', 'Variedad, roleplay y gameplays interactivos'),
        (v_creator4_id, v_org_id, 'Rubén Doblas', 'elrubius', 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&auto=format&fit=crop&q=80', 'youtube', 'active', 'Creador pionero de YouTube y Twitch gaming')
    ON CONFLICT (id) DO NOTHING;

    -- 3. Canales de plataforma
    INSERT INTO public.channels (id, creator_id, platform, platform_channel_id, channel_url, followers_count, subscribers_count, is_live)
    VALUES
        (v_channel1_id, v_creator1_id, 'twitch', 'ibai', 'https://twitch.tv/ibai', 15400000, 42000, true),
        (v_channel2_id, v_creator2_id, 'twitch', 'rivers_gg', 'https://twitch.tv/rivers_gg', 6100000, 18500, false),
        (v_channel3_id, v_creator3_id, 'twitch', 'juansguarnizo', 'https://twitch.tv/juansguarnizo', 9200000, 24100, true),
        (v_channel4_id, v_creator4_id, 'youtube', 'elrubiusOMG', 'https://youtube.com/@elrubius', 40500000, 0, false)
    ON CONFLICT (creator_id, platform, platform_channel_id) DO NOTHING;

    -- 4. Sesiones de Streaming
    INSERT INTO public.streaming_sessions (
        organization_id, creator_id, channel_id, session_title, game_or_category, platform,
        streamed_at, duration_seconds, peak_viewers, avg_ccv, chat_messages_count, new_followers,
        ad_revenue, donations_revenue, subs_revenue, total_earnings, earnings_per_hour
    ) VALUES
        (v_org_id, v_creator1_id, v_channel1_id, 'LA VELADA DEL AÑO 4 - ANUNCIO OFICIAL', 'Special Events', 'twitch', now() - INTERVAL '1 day', 18000, 142000, 98500, 420000, 8400, 3200.00, 1450.00, 5600.00, 10250.00, 2050.00),
        (v_org_id, v_creator1_id, v_channel1_id, 'Charlando con amigos y probando comida', 'Just Chatting', 'twitch', now() - INTERVAL '3 days', 14400, 78000, 52000, 185000, 3100, 1100.00, 680.00, 2200.00, 3980.00, 995.00),
        (v_org_id, v_creator2_id, v_channel2_id, 'KINGS LEAGUE - REACCIONANDO AL DRAFT', 'Sports & Gaming', 'twitch', now() - INTERVAL '2 days', 12600, 54000, 34000, 120000, 2400, 850.00, 420.00, 1800.00, 3070.00, 877.14),
        (v_org_id, v_creator2_id, v_channel2_id, 'VALORANT CON SQUAD TROLL', 'VALORANT', 'twitch', now() - INTERVAL '4 days', 16200, 41000, 28000, 98000, 1900, 620.00, 310.00, 1400.00, 2330.00, 517.78),
        (v_org_id, v_creator3_id, v_channel3_id, 'MARATÓN DE MINECRAFT EXTREMO', 'Minecraft', 'twitch', now() - INTERVAL '1 day', 21600, 62000, 45000, 160000, 3800, 1400.00, 950.00, 3100.00, 5450.00, 908.33),
        (v_org_id, v_creator4_id, v_channel4_id, 'PROBANDO EL NUEVO JUEGO DE TERROR', 'Horror Games', 'youtube', now() - INTERVAL '5 days', 10800, 95000, 72000, 250000, 5200, 2100.00, 1200.00, 0.00, 3300.00, 1100.00);

    -- 5. Videos Master
    INSERT INTO public.videos (id, organization_id, creator_id, title, internal_name, category, duration_seconds, production_cost, status)
    VALUES
        (v_vid1_id, v_org_id, v_creator1_id, 'MEJORES MOMENTOS DE LA VELADA 4', 'velada4_highlights', 'Special Events', 1240, 450.00, 'published'),
        (v_vid2_id, v_org_id, v_creator1_id, 'Ibai reacciona a los combates más épicos', 'ibai_reacts_epic', 'Entertainment', 750, 150.00, 'published'),
        (v_vid3_id, v_org_id, v_creator2_id, 'PIO FC: El Camino a la Final de la Kings League', 'pio_kings_journey', 'Sports & Gaming', 1800, 600.00, 'published'),
        (v_vid4_id, v_org_id, v_creator3_id, 'Sobreviviendo 100 Días en Minecraft Hardcore', 'minecraft_100_days', 'Gaming', 3600, 800.00, 'published'),
        (v_vid5_id, v_org_id, v_creator4_id, 'ESTE JUEGO DE TERROR ME DEJÓ SIN DORMIR', 'horror_gameplay_yt', 'Horror Games', 1520, 200.00, 'published')
    ON CONFLICT (id) DO NOTHING;

    -- 6. Publicaciones de Video en Plataformas
    INSERT INTO public.video_publications (
        video_id, organization_id, creator_id, channel_id, platform, post_url, thumbnail_url,
        publication_type, published_at, views_count, likes_count, comments_count, shares_count,
        watch_time_hours, estimated_revenue, engagement_rate
    ) VALUES
        (v_vid1_id, v_org_id, v_creator1_id, v_channel1_id, 'youtube', 'https://youtube.com/watch?v=demo1', 'https://images.unsplash.com/photo-1542751371-adc38448a05e?w=300&auto=format&fit=crop&q=80', 'standard', now() - INTERVAL '1 day', 1450000, 112000, 8400, 12000, 31000.5, 4350.00, 9.1),
        (v_vid1_id, v_org_id, v_creator1_id, v_channel1_id, 'tiktok', 'https://tiktok.com/@ibai/video/demo1', 'https://images.unsplash.com/photo-1542751371-adc38448a05e?w=300&auto=format&fit=crop&q=80', 'short/reel', now() - INTERVAL '1 day', 2800000, 320000, 14000, 45000, 9200.0, 980.00, 13.5),
        (v_vid2_id, v_org_id, v_creator1_id, v_channel1_id, 'youtube', 'https://youtube.com/watch?v=demo2', 'https://images.unsplash.com/photo-1511512578047-dfb367046420?w=300&auto=format&fit=crop&q=80', 'standard', now() - INTERVAL '2 days', 890000, 76000, 4200, 3100, 12400.0, 2150.00, 9.3),
        (v_vid3_id, v_org_id, v_creator2_id, v_channel2_id, 'youtube', 'https://youtube.com/watch?v=demo3', 'https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=300&auto=format&fit=crop&q=80', 'vod', now() - INTERVAL '2 days', 420000, 38000, 2900, 1800, 8500.0, 1280.00, 10.1),
        (v_vid4_id, v_org_id, v_creator3_id, v_channel3_id, 'youtube', 'https://youtube.com/watch?v=demo4', 'https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=300&auto=format&fit=crop&q=80', 'standard', now() - INTERVAL '1 day', 980000, 85000, 6100, 4500, 22400.0, 2940.00, 9.7),
        (v_vid5_id, v_org_id, v_creator4_id, v_channel4_id, 'youtube', 'https://youtube.com/watch?v=demo5', 'https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=300&auto=format&fit=crop&q=80', 'standard', now() - INTERVAL '4 days', 1850000, 142000, 12500, 9800, 38500.0, 5550.00, 8.8);

    -- 7. Alertas y advertencias de prueba
    INSERT INTO public.channel_alerts (
        organization_id, creator_id, channel_id, alert_type, severity, status, title, description, occurred_at
    ) VALUES
        (v_org_id, v_creator1_id, v_channel1_id, 'dmca_strike', 'warning', 'active', 'Reclamación de Audio en VOD #1042', 'Música con copyright detectada en el minuto 42:15', now() - INTERVAL '2 hours'),
        (v_org_id, v_creator3_id, v_channel3_id, 'unusual_drop', 'info', 'resolved', 'Pérdida temporal de bitrate detectada', 'Caída de frames por saturación de ISP resuelta en 10 min', now() - INTERVAL '2 days'),
        (v_org_id, v_creator2_id, v_channel2_id, 'tos_violation', 'critical', 'active', 'Strike de Términos de Servicio de Twitch', 'Advertencia por lenguaje potencialmente no moderado en chat', now() - INTERVAL '6 hours');

    -- 8. Refresco de Vistas Materializadas
    PERFORM public.refresh_all_materialized_views_concurrently();
END $$;

-- ==============================================================================
-- RRSS Creators Analyzer — Complete SQLite 3 Database Schema (DDL)
-- ==============================================================================
-- Engine       : SQLite 3.35+ (WAL Mode, Foreign Keys Enforced, Generated Columns)
-- Framework    : Django 6.0 (Single-Tenant / Single-Company Architecture)
-- Auth & RBAC  : Native Django Permissions & Groups (`django.contrib.auth` + `contenttypes`)
-- Cache Layer  : DiskCache / LocMemCache (replaces legacy PostgreSQL Materialized Views)
-- Reference    : Adapted & expanded from /old-migrations/*.sql
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 0. CONFIGURACIÓN DE RENDIMIENTO E INTEGRIDAD PARA SQLITE (PRAGMAS)
-- ------------------------------------------------------------------------------
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA temp_store = MEMORY;
PRAGMA mmap_size = 134217728; -- 128 MB
PRAGMA cache_size = -64000;   -- 64 MB
PRAGMA foreign_keys = ON;
PRAGMA busy_timeout = 5000;


-- ==============================================================================
-- 1. IDENTIDAD, GRUPOS Y PERMISOS NATIVOS DE DJANGO (`auth` & `users`)
-- ==============================================================================
-- Toda la autorización se delega al sistema nativo de Grupos y Permisos de Django
-- (sin columnas `role` acopladas en `users_user`).
--
-- Grupos base del sistema (`auth_group.name`):
--   1. 'Company Admin' : Control total sobre configuración, contratos, usuarios y datos.
--   2. 'Manager'       : Gestión operativa de creadores, canales, sesiones, videos y alertas.
--   3. 'Analyst'       : Lectura global, analítica avanzada, importación y exportación de reportes.
--   4. 'Finance'       : Gestión de contratos, campañas de patrocinio y liquidaciones (payouts).
--   5. 'Creator'       : Acceso de lectura restringido exclusivamente a sus propios activos y métricas.
--
-- Permisos personalizados del dominio (`Meta.permissions` en modelos Django):
--   - creators.view_all_creators        ("Puede ver todos los creadores de la compañía")
--   - creators.manage_contracts         ("Puede gestionar contratos y revenue splits")
--   - streams.view_all_sessions         ("Puede ver las sesiones de todos los creadores")
--   - streams.export_sessions           ("Puede exportar reportes de sesiones")
--   - videos.view_all_videos            ("Puede ver los videos y publicaciones de todos los creadores")
--   - videos.view_production_costs      ("Puede ver costos de producción, beneficio neto y ROI")
--   - alerts.view_all_alerts            ("Puede ver las alertas de todos los canales")
--   - alerts.resolve_channel_alert      ("Puede resolver o apelar alertas y strikes")
--   - analytics.view_company_dashboard  ("Puede ver el dashboard global y rankings de la compañía")
--   - analytics.refresh_analytics_cache ("Puede forzar la invalidación/refresco de DiskCache")

-- 1.1 Registro de Tipos de Contenido de Django (`django.contrib.contenttypes`)
CREATE TABLE IF NOT EXISTS django_content_type (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    app_label VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,

    CONSTRAINT uq_django_content_type UNIQUE (app_label, model)
);

-- 1.2 Catálogo de Permisos (`django.contrib.auth.models.Permission`)
CREATE TABLE IF NOT EXISTS auth_permission (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_type_id INTEGER NOT NULL REFERENCES django_content_type(id) ON DELETE CASCADE,
    codename VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,

    CONSTRAINT uq_auth_permission UNIQUE (content_type_id, codename)
);

CREATE INDEX IF NOT EXISTS idx_auth_perm_content_type ON auth_permission(content_type_id);

-- 1.3 Grupos de Usuarios / Roles de Negocio (`django.contrib.auth.models.Group`)
CREATE TABLE IF NOT EXISTS auth_group (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(150) NOT NULL UNIQUE
);

-- 1.4 Asignación de Permisos a Grupos (`auth_group_permissions`)
CREATE TABLE IF NOT EXISTS auth_group_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL REFERENCES auth_group(id) ON DELETE CASCADE,
    permission_id INTEGER NOT NULL REFERENCES auth_permission(id) ON DELETE CASCADE,

    CONSTRAINT uq_auth_group_perm UNIQUE (group_id, permission_id)
);

CREATE INDEX IF NOT EXISTS idx_auth_group_perm_group ON auth_group_permissions(group_id);
CREATE INDEX IF NOT EXISTS idx_auth_group_perm_perm ON auth_group_permissions(permission_id);

-- 1.5 Usuarios del Sistema (`rrss_creatos_analyzer.apps.users.models.User`)
CREATE TABLE IF NOT EXISTS users_user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    password VARCHAR(128) NOT NULL,
    last_login DATETIME NULL,
    is_superuser BOOL NOT NULL DEFAULT 0,
    username VARCHAR(150) NOT NULL UNIQUE,
    email VARCHAR(254) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL DEFAULT '',
    avatar_url VARCHAR(500) NOT NULL DEFAULT '',
    phone VARCHAR(50) NOT NULL DEFAULT '',
    timezone VARCHAR(64) NOT NULL DEFAULT 'UTC',
    is_staff BOOL NOT NULL DEFAULT 0,
    is_active BOOL NOT NULL DEFAULT 1,
    date_joined DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_user_active ON users_user(is_active);

-- 1.6 Membresía de Usuarios en Grupos (`users_user_groups`)
CREATE TABLE IF NOT EXISTS users_user_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
    group_id INTEGER NOT NULL REFERENCES auth_group(id) ON DELETE CASCADE,

    CONSTRAINT uq_users_user_group UNIQUE (user_id, group_id)
);

CREATE INDEX IF NOT EXISTS idx_user_groups_user ON users_user_groups(user_id);
CREATE INDEX IF NOT EXISTS idx_user_groups_group ON users_user_groups(group_id);

-- 1.7 Permisos Directos por Usuario (`users_user_user_permissions`)
CREATE TABLE IF NOT EXISTS users_user_user_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
    permission_id INTEGER NOT NULL REFERENCES auth_permission(id) ON DELETE CASCADE,

    CONSTRAINT uq_users_user_perm UNIQUE (user_id, permission_id)
);

CREATE INDEX IF NOT EXISTS idx_user_perms_user ON users_user_user_permissions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_perms_perm ON users_user_user_permissions(permission_id);


-- 1.8 Configuración Global de la Compañía / Agencia (Singleton Single-Tenant)
CREATE TABLE IF NOT EXISTS core_company_settings (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    company_name VARCHAR(200) NOT NULL DEFAULT 'My Creator Agency',
    legal_name VARCHAR(255) NOT NULL DEFAULT '',
    tax_id VARCHAR(100) NOT NULL DEFAULT '',
    logo_url VARCHAR(500) NOT NULL DEFAULT '',
    default_currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    default_timezone VARCHAR(64) NOT NULL DEFAULT 'UTC',
    default_agency_split_pct NUMERIC(5, 2) NOT NULL DEFAULT 20.00,
    default_creator_split_pct NUMERIC(5, 2) NOT NULL DEFAULT 80.00,
    alert_webhook_url VARCHAR(500) NOT NULL DEFAULT '',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_company_splits CHECK (
        default_agency_split_pct >= 0 AND default_creator_split_pct >= 0
        AND (default_agency_split_pct + default_creator_split_pct) = 100.00
    )
);


-- ==============================================================================
-- 2. SISTEMA DE ETIQUETADO TRANSVERSAL (`django-taggit` / App: `core`)
-- ==============================================================================
-- Reemplaza los campos `tags TEXT[]` de PostgreSQL por tablas relacionales SQLite

CREATE TABLE IF NOT EXISTS taggit_tag (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS core_entity_tag (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_id INTEGER NOT NULL REFERENCES taggit_tag(id) ON DELETE CASCADE,
    entity_type VARCHAR(50) NOT NULL, -- 'creator', 'video', 'stream', 'campaign'
    entity_id INTEGER NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_entity_tag UNIQUE (tag_id, entity_type, entity_id),
    CONSTRAINT chk_entity_tag_type CHECK (
        entity_type IN ('creator', 'video', 'stream', 'campaign')
    )
);

CREATE INDEX IF NOT EXISTS idx_entity_tag_lookup ON core_entity_tag(entity_type, entity_id);


-- ==============================================================================
-- 3. DIRECTORIO DE CREADORES, CONTRATOS Y CANALES (App: `creators`)
-- ==============================================================================

-- 3.1 Creadores / Streamers de la Compañía
CREATE TABLE IF NOT EXISTS creators_creator (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NULL UNIQUE REFERENCES users_user(id) ON DELETE SET NULL,
    manager_id INTEGER NULL REFERENCES users_user(id) ON DELETE SET NULL,

    display_name VARCHAR(150) NOT NULL,
    handle VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(120) NOT NULL UNIQUE,
    legal_full_name VARCHAR(255) NOT NULL DEFAULT '',
    contact_email VARCHAR(254) NOT NULL DEFAULT '',
    country_code VARCHAR(2) NOT NULL DEFAULT '',
    language_code VARCHAR(10) NOT NULL DEFAULT 'es',
    avatar_url VARCHAR(500) NOT NULL DEFAULT '',
    banner_url VARCHAR(500) NOT NULL DEFAULT '',
    bio TEXT NOT NULL DEFAULT '',
    main_category VARCHAR(120) NOT NULL DEFAULT 'General',

    primary_platform VARCHAR(20) NOT NULL DEFAULT 'twitch',
    tier VARCHAR(20) NOT NULL DEFAULT 'standard',
    status VARCHAR(20) NOT NULL DEFAULT 'active',

    joined_company_at DATE NULL,
    left_company_at DATE NULL,
    internal_notes TEXT NOT NULL DEFAULT '',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_creator_primary_platform CHECK (
        primary_platform IN ('twitch', 'youtube', 'kick', 'tiktok', 'instagram', 'x')
    ),
    CONSTRAINT chk_creator_status CHECK (
        status IN ('onboarding', 'active', 'inactive', 'on_leave', 'suspended', 'terminated')
    ),
    CONSTRAINT chk_creator_tier CHECK (
        tier IN ('rookie', 'standard', 'partner', 'elite', 'ambassador')
    )
);

CREATE INDEX IF NOT EXISTS idx_creators_status ON creators_creator(status);
CREATE INDEX IF NOT EXISTS idx_creators_platform ON creators_creator(primary_platform);
CREATE INDEX IF NOT EXISTS idx_creators_manager ON creators_creator(manager_id);
CREATE INDEX IF NOT EXISTS idx_creators_tier ON creators_creator(tier);


-- 3.2 Asignación Operativa de Equipo por Creador
-- Vincula usuarios staff con creadores específicos usando `auth_group` para el rol funcional
CREATE TABLE IF NOT EXISTS creators_team_assignment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    creator_id INTEGER NOT NULL REFERENCES creators_creator(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
    group_id INTEGER NULL REFERENCES auth_group(id) ON DELETE SET NULL,
    responsibility VARCHAR(40) NOT NULL DEFAULT 'talent_manager',
    is_primary BOOL NOT NULL DEFAULT 0,
    assigned_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_creator_user_responsibility UNIQUE (creator_id, user_id, responsibility),
    CONSTRAINT chk_assignment_responsibility CHECK (
        responsibility IN ('talent_manager', 'video_editor', 'thumbnail_designer', 'analyst', 'moderator')
    )
);

CREATE INDEX IF NOT EXISTS idx_team_assign_user ON creators_team_assignment(user_id);
CREATE INDEX IF NOT EXISTS idx_team_assign_group ON creators_team_assignment(group_id);


-- 3.3 Contratos, Acuerdos de Revenue Split y Cuotas Mensuales (Funcionalidad Futura/Financiera)
CREATE TABLE IF NOT EXISTS creators_contract (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    creator_id INTEGER NOT NULL REFERENCES creators_creator(id) ON DELETE CASCADE,
    contract_code VARCHAR(60) NOT NULL UNIQUE,
    status VARCHAR(20) NOT NULL DEFAULT 'active',

    start_date DATE NOT NULL,
    end_date DATE NULL,
    auto_renew BOOL NOT NULL DEFAULT 0,

    -- Ingresos fijos y repartos porcentuales (0.00 a 100.00)
    base_monthly_retainer NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    stream_creator_split_pct NUMERIC(5, 2) NOT NULL DEFAULT 80.00,
    stream_agency_split_pct NUMERIC(5, 2) NOT NULL DEFAULT 20.00,
    video_creator_split_pct NUMERIC(5, 2) NOT NULL DEFAULT 70.00,
    video_agency_split_pct NUMERIC(5, 2) NOT NULL DEFAULT 30.00,
    sponsorship_creator_split_pct NUMERIC(5, 2) NOT NULL DEFAULT 75.00,
    sponsorship_agency_split_pct NUMERIC(5, 2) NOT NULL DEFAULT 25.00,

    -- Compromisos / Metas contractuales mensuales (KPIs de cumplimiento)
    min_monthly_stream_hours NUMERIC(6, 2) NOT NULL DEFAULT 0.00,
    min_monthly_videos INTEGER NOT NULL DEFAULT 0,
    min_monthly_shorts INTEGER NOT NULL DEFAULT 0,

    document_url VARCHAR(500) NOT NULL DEFAULT '',
    notes TEXT NOT NULL DEFAULT '',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_contract_status CHECK (
        status IN ('draft', 'active', 'expired', 'terminated', 'renewed')
    ),
    CONSTRAINT chk_contract_stream_split CHECK (
        stream_creator_split_pct >= 0 AND stream_agency_split_pct >= 0
        AND (stream_creator_split_pct + stream_agency_split_pct) = 100.00
    ),
    CONSTRAINT chk_contract_video_split CHECK (
        video_creator_split_pct >= 0 AND video_agency_split_pct >= 0
        AND (video_creator_split_pct + video_agency_split_pct) = 100.00
    ),
    CONSTRAINT chk_contract_sponsor_split CHECK (
        sponsorship_creator_split_pct >= 0 AND sponsorship_agency_split_pct >= 0
        AND (sponsorship_creator_split_pct + sponsorship_agency_split_pct) = 100.00
    ),
    CONSTRAINT chk_contract_quotas_positive CHECK (
        base_monthly_retainer >= 0
        AND min_monthly_stream_hours >= 0
        AND min_monthly_videos >= 0
        AND min_monthly_shorts >= 0
    )
);

CREATE INDEX IF NOT EXISTS idx_contracts_creator ON creators_contract(creator_id, status);


-- 3.4 Canales por Plataforma de cada Creador
CREATE TABLE IF NOT EXISTS creators_channel (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    creator_id INTEGER NOT NULL REFERENCES creators_creator(id) ON DELETE CASCADE,
    platform VARCHAR(20) NOT NULL,
    platform_channel_id VARCHAR(150) NOT NULL,
    handle VARCHAR(150) NOT NULL DEFAULT '',
    channel_name VARCHAR(150) NOT NULL DEFAULT '',
    channel_url VARCHAR(500) NOT NULL DEFAULT '',

    is_primary BOOL NOT NULL DEFAULT 0,
    is_verified BOOL NOT NULL DEFAULT 0,
    is_monetized BOOL NOT NULL DEFAULT 1,
    is_live BOOL NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'active',

    -- Métricas actuales consolidadas en el canal
    followers_count INTEGER NOT NULL DEFAULT 0,
    subscribers_count INTEGER NOT NULL DEFAULT 0,
    paid_subscribers_count INTEGER NOT NULL DEFAULT 0,
    total_views_count BIGINT NOT NULL DEFAULT 0,

    -- Estado de sincronización con APIs o scrapers futuros
    sync_enabled BOOL NOT NULL DEFAULT 1,
    last_synced_at DATETIME NULL,
    last_stream_at DATETIME NULL,

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_creator_platform_channel UNIQUE (creator_id, platform, platform_channel_id),
    CONSTRAINT chk_channel_platform CHECK (
        platform IN ('twitch', 'youtube', 'kick', 'tiktok', 'instagram', 'x')
    ),
    CONSTRAINT chk_channel_status CHECK (
        status IN ('active', 'demonetized', 'shadowbanned', 'suspended', 'banned', 'archived')
    ),
    CONSTRAINT chk_channel_counts_non_negative CHECK (
        followers_count >= 0 AND subscribers_count >= 0
        AND paid_subscribers_count >= 0 AND total_views_count >= 0
    )
);

CREATE INDEX IF NOT EXISTS idx_channels_creator ON creators_channel(creator_id);
CREATE INDEX IF NOT EXISTS idx_channels_platform ON creators_channel(platform);
CREATE INDEX IF NOT EXISTS idx_channels_is_live ON creators_channel(is_live);


-- 3.5 Snapshots Históricos de Crecimiento de Canal (Funcionalidad de Tendencias de Audiencia)
CREATE TABLE IF NOT EXISTS creators_channel_snapshot (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_id INTEGER NOT NULL REFERENCES creators_channel(id) ON DELETE CASCADE,
    snapshot_date DATE NOT NULL,

    followers_count INTEGER NOT NULL DEFAULT 0,
    followers_delta INTEGER NOT NULL DEFAULT 0,
    subscribers_count INTEGER NOT NULL DEFAULT 0,
    subscribers_delta INTEGER NOT NULL DEFAULT 0,
    paid_subscribers_count INTEGER NOT NULL DEFAULT 0,
    total_views_count BIGINT NOT NULL DEFAULT 0,
    views_delta BIGINT NOT NULL DEFAULT 0,

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_channel_snapshot_date UNIQUE (channel_id, snapshot_date)
);

CREATE INDEX IF NOT EXISTS idx_channel_snapshots_date ON creators_channel_snapshot(snapshot_date DESC);


-- ==============================================================================
-- 4. LOTES DE IMPORTACIÓN Y SINCRONIZACIÓN DE DATOS (App: `imports`)
-- ==============================================================================

CREATE TABLE IF NOT EXISTS imports_import_batch (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uploaded_by_id INTEGER NULL REFERENCES users_user(id) ON DELETE SET NULL,

    batch_type VARCHAR(30) NOT NULL DEFAULT 'streams', -- 'streams', 'videos', 'publications', 'channels', 'alerts'
    source_platform VARCHAR(20) NOT NULL DEFAULT 'twitch',
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL DEFAULT '',
    file_hash_sha256 VARCHAR(64) NOT NULL DEFAULT '',

    total_rows INTEGER NOT NULL DEFAULT 0,
    valid_rows INTEGER NOT NULL DEFAULT 0,
    created_rows INTEGER NOT NULL DEFAULT 0,
    updated_rows INTEGER NOT NULL DEFAULT 0,
    skipped_rows INTEGER NOT NULL DEFAULT 0,
    error_count INTEGER NOT NULL DEFAULT 0,

    status VARCHAR(20) NOT NULL DEFAULT 'processing',
    error_summary JSON NOT NULL DEFAULT '[]', -- JSON válido en SQLite
    started_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_import_batch_type CHECK (
        batch_type IN ('streams', 'videos', 'publications', 'channels', 'alerts', 'mixed')
    ),
    CONSTRAINT chk_import_platform CHECK (
        source_platform IN ('twitch', 'youtube', 'kick', 'tiktok', 'instagram', 'x', 'multi')
    ),
    CONSTRAINT chk_import_status CHECK (
        status IN ('pending', 'processing', 'completed', 'partial', 'failed', 'rolled_back')
    ),
    CONSTRAINT chk_import_counts_non_negative CHECK (
        total_rows >= 0 AND valid_rows >= 0 AND error_count >= 0
    )
);

CREATE INDEX IF NOT EXISTS idx_imports_status ON imports_import_batch(status);
CREATE INDEX IF NOT EXISTS idx_imports_created_at ON imports_import_batch(created_at DESC);


-- ==============================================================================
-- 5. SESIONES DE STREAMING EN VIVO Y SEGMENTOS (App: `streams`)
-- ==============================================================================

-- 5.1 Sesiones de Streaming Normalizadas
CREATE TABLE IF NOT EXISTS streams_streaming_session (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    creator_id INTEGER NOT NULL REFERENCES creators_creator(id) ON DELETE CASCADE,
    channel_id INTEGER NULL REFERENCES creators_channel(id) ON DELETE SET NULL,
    import_batch_id INTEGER NULL REFERENCES imports_import_batch(id) ON DELETE SET NULL,

    external_stream_id VARCHAR(150) NOT NULL DEFAULT '',
    session_title VARCHAR(255) NOT NULL DEFAULT 'Live Stream',
    game_or_category VARCHAR(150) NOT NULL DEFAULT 'Just Chatting',
    platform VARCHAR(20) NOT NULL DEFAULT 'twitch',
    stream_url VARCHAR(500) NOT NULL DEFAULT '',
    vod_url VARCHAR(500) NOT NULL DEFAULT '',

    streamed_at DATETIME NOT NULL,
    ended_at DATETIME NULL,
    duration_seconds INTEGER NOT NULL DEFAULT 0,

    -- Columna Generada (SQLite Generated Column compatible con Django GeneratedField)
    hours_streamed NUMERIC(8, 2) GENERATED ALWAYS AS (ROUND(CAST(duration_seconds AS REAL) / 3600.0, 2)) STORED,

    -- Métricas de Audiencia y Engagement
    peak_viewers INTEGER NOT NULL DEFAULT 0,
    avg_ccv INTEGER NOT NULL DEFAULT 0,
    unique_viewers INTEGER NOT NULL DEFAULT 0,
    live_views_count INTEGER NOT NULL DEFAULT 0,
    chat_messages_count INTEGER NOT NULL DEFAULT 0,
    unique_chatters_count INTEGER NOT NULL DEFAULT 0,
    new_followers INTEGER NOT NULL DEFAULT 0,
    new_subscriptions INTEGER NOT NULL DEFAULT 0,
    gifted_subscriptions INTEGER NOT NULL DEFAULT 0,
    raids_received INTEGER NOT NULL DEFAULT 0,

    -- Métricas Financieras de la Sesión (Moneda base de la compañía)
    ad_revenue NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    subs_revenue NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    donations_revenue NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    bits_or_gifts_revenue NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    sponsorship_revenue NUMERIC(12, 2) NOT NULL DEFAULT 0.00,

    -- Columnas Financieras Calculadas Deterministas
    total_earnings NUMERIC(12, 2) GENERATED ALWAYS AS (
        ROUND(ad_revenue + subs_revenue + donations_revenue + bits_or_gifts_revenue + sponsorship_revenue, 2)
    ) STORED,
    earnings_per_hour NUMERIC(12, 2) GENERATED ALWAYS AS (
        CASE
            WHEN duration_seconds > 0
            THEN ROUND((ad_revenue + subs_revenue + donations_revenue + bits_or_gifts_revenue + sponsorship_revenue) / (CAST(duration_seconds AS REAL) / 3600.0), 2)
            ELSE 0.00
        END
    ) STORED,

    is_sponsored BOOL NOT NULL DEFAULT 0,
    notes TEXT NOT NULL DEFAULT '',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_stream_platform CHECK (
        platform IN ('twitch', 'youtube', 'kick', 'tiktok', 'instagram', 'x')
    ),
    CONSTRAINT chk_stream_metrics_non_negative CHECK (
        duration_seconds >= 0 AND peak_viewers >= 0 AND avg_ccv >= 0
        AND unique_viewers >= 0 AND chat_messages_count >= 0
        AND ad_revenue >= 0 AND subs_revenue >= 0 AND donations_revenue >= 0
        AND bits_or_gifts_revenue >= 0 AND sponsorship_revenue >= 0
    )
);

CREATE INDEX IF NOT EXISTS idx_streams_creator_date ON streams_streaming_session(creator_id, streamed_at DESC);
CREATE INDEX IF NOT EXISTS idx_streams_platform_date ON streams_streaming_session(platform, streamed_at DESC);
CREATE INDEX IF NOT EXISTS idx_streams_category ON streams_streaming_session(game_or_category);
CREATE INDEX IF NOT EXISTS idx_streams_streamed_at ON streams_streaming_session(streamed_at DESC);


-- 5.2 Segmentos de Categoría dentro de un mismo Stream (Funcionalidad Futura: Streams Multi-Juego)
CREATE TABLE IF NOT EXISTS streams_session_segment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL REFERENCES streams_streaming_session(id) ON DELETE CASCADE,
    game_or_category VARCHAR(150) NOT NULL,
    start_offset_seconds INTEGER NOT NULL DEFAULT 0,
    duration_seconds INTEGER NOT NULL DEFAULT 0,
    avg_ccv INTEGER NOT NULL DEFAULT 0,
    peak_viewers INTEGER NOT NULL DEFAULT 0,

    CONSTRAINT chk_segment_non_negative CHECK (
        start_offset_seconds >= 0 AND duration_seconds >= 0 AND avg_ccv >= 0 AND peak_viewers >= 0
    )
);

CREATE INDEX IF NOT EXISTS idx_stream_segments_session ON streams_session_segment(session_id);


-- ==============================================================================
-- 6. ACTIVOS DE VIDEO, PUBLICACIONES Y RELACIONES (App: `videos`)
-- ==============================================================================
-- Basado en el modelo de 3 entidades de 20260904000007_refactor_video_schema_three_entities.sql

-- 6.1 Tabla Principal: Videos (Activo Digital Maestro y Producción Editorial)
CREATE TABLE IF NOT EXISTS videos_video (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    creator_id INTEGER NOT NULL REFERENCES creators_creator(id) ON DELETE CASCADE,
    assigned_editor_id INTEGER NULL REFERENCES users_user(id) ON DELETE SET NULL,

    title VARCHAR(255) NOT NULL,
    internal_code VARCHAR(100) NOT NULL DEFAULT '',
    internal_name VARCHAR(150) NOT NULL DEFAULT '',
    description TEXT NOT NULL DEFAULT '',
    category VARCHAR(100) NOT NULL DEFAULT 'General',
    content_format VARCHAR(30) NOT NULL DEFAULT 'long_form', -- 'long_form', 'short_vertical', 'vod_highlight', 'podcast'

    duration_seconds INTEGER NOT NULL DEFAULT 0,
    production_cost NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    editing_cost NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    thumbnail_cost NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    total_production_cost NUMERIC(10, 2) GENERATED ALWAYS AS (
        ROUND(production_cost + editing_cost + thumbnail_cost, 2)
    ) STORED,

    status VARCHAR(20) NOT NULL DEFAULT 'published',
    target_release_date DATE NULL,
    master_asset_url VARCHAR(500) NOT NULL DEFAULT '',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_video_status CHECK (
        status IN ('idea', 'scripting', 'recording', 'editing', 'review', 'ready', 'published', 'archived')
    ),
    CONSTRAINT chk_video_format CHECK (
        content_format IN ('long_form', 'short_vertical', 'vod_highlight', 'clip', 'podcast', 'teaser')
    ),
    CONSTRAINT chk_video_costs_non_negative CHECK (
        duration_seconds >= 0 AND production_cost >= 0 AND editing_cost >= 0 AND thumbnail_cost >= 0
    )
);

CREATE INDEX IF NOT EXISTS idx_videos_creator ON videos_video(creator_id);
CREATE INDEX IF NOT EXISTS idx_videos_status ON videos_video(status);
CREATE INDEX IF NOT EXISTS idx_videos_category ON videos_video(category);
CREATE INDEX IF NOT EXISTS idx_videos_created_at ON videos_video(created_at DESC);


-- 6.2 Tabla Secundaria: Publicaciones por Plataforma (YouTube, TikTok, Reels, Shorts, etc.)
CREATE TABLE IF NOT EXISTS videos_video_publication (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id INTEGER NOT NULL REFERENCES videos_video(id) ON DELETE CASCADE,
    creator_id INTEGER NOT NULL REFERENCES creators_creator(id) ON DELETE CASCADE,
    channel_id INTEGER NULL REFERENCES creators_channel(id) ON DELETE SET NULL,
    import_batch_id INTEGER NULL REFERENCES imports_import_batch(id) ON DELETE SET NULL,

    platform VARCHAR(20) NOT NULL DEFAULT 'youtube',
    platform_post_id VARCHAR(150) NOT NULL DEFAULT '',
    published_title VARCHAR(255) NOT NULL DEFAULT '',
    post_url VARCHAR(500) NOT NULL DEFAULT '',
    thumbnail_url VARCHAR(500) NOT NULL DEFAULT '',
    publication_type VARCHAR(30) NOT NULL DEFAULT 'standard',
    published_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'published',

    -- Métricas de Rendimiento en la Plataforma
    views_count BIGINT NOT NULL DEFAULT 0,
    unique_viewers_count BIGINT NOT NULL DEFAULT 0,
    impressions_count BIGINT NOT NULL DEFAULT 0,
    click_through_rate NUMERIC(5, 2) NOT NULL DEFAULT 0.00, -- CTR %
    likes_count INTEGER NOT NULL DEFAULT 0,
    dislikes_count INTEGER NOT NULL DEFAULT 0,
    comments_count INTEGER NOT NULL DEFAULT 0,
    shares_count INTEGER NOT NULL DEFAULT 0,
    saves_count INTEGER NOT NULL DEFAULT 0,
    watch_time_hours NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    avg_view_duration_seconds INTEGER NOT NULL DEFAULT 0,
    retention_rate_pct NUMERIC(5, 2) NOT NULL DEFAULT 0.00,
    engagement_rate NUMERIC(6, 2) NOT NULL DEFAULT 0.00,

    -- Métricas Financieras de la Publicación
    ad_revenue NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    sponsorship_revenue NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    estimated_revenue NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    rpm_estimated NUMERIC(10, 2) GENERATED ALWAYS AS (
        CASE
            WHEN views_count > 0
            THEN ROUND((estimated_revenue / (CAST(views_count AS REAL) / 1000.0)), 2)
            ELSE 0.00
        END
    ) STORED,

    last_metrics_synced_at DATETIME NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_vpub_platform CHECK (
        platform IN ('youtube', 'tiktok', 'twitch', 'kick', 'instagram', 'x')
    ),
    CONSTRAINT chk_vpub_type CHECK (
        publication_type IN ('standard', 'short', 'reel', 'tiktok', 'vod', 'clip', 'teaser')
    ),
    CONSTRAINT chk_vpub_status CHECK (
        status IN ('scheduled', 'published', 'unlisted', 'private', 'demonetized', 'removed', 'struck')
    ),
    CONSTRAINT chk_vpub_metrics_non_negative CHECK (
        views_count >= 0 AND likes_count >= 0 AND comments_count >= 0
        AND shares_count >= 0 AND watch_time_hours >= 0 AND estimated_revenue >= 0
    )
);

CREATE INDEX IF NOT EXISTS idx_vpub_video ON videos_video_publication(video_id);
CREATE INDEX IF NOT EXISTS idx_vpub_creator_date ON videos_video_publication(creator_id, published_at DESC);
CREATE INDEX IF NOT EXISTS idx_vpub_platform_type ON videos_video_publication(platform, publication_type);
CREATE INDEX IF NOT EXISTS idx_vpub_published_at ON videos_video_publication(published_at DESC);


-- 6.3 Tabla Terciaria: Relaciones de Video (con otros Videos o Sesiones de Streaming en Vivo)
CREATE TABLE IF NOT EXISTS videos_video_relation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_video_id INTEGER NOT NULL REFERENCES videos_video(id) ON DELETE CASCADE,
    target_video_id INTEGER NULL REFERENCES videos_video(id) ON DELETE CASCADE,
    target_session_id INTEGER NULL REFERENCES streams_streaming_session(id) ON DELETE CASCADE,

    relation_type VARCHAR(30) NOT NULL DEFAULT 'derived_from_live',
    description TEXT NOT NULL DEFAULT '',
    timestamp_start_seconds INTEGER NULL,
    timestamp_end_seconds INTEGER NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_vrel_type CHECK (
        relation_type IN ('derived_from_live', 'continuation', 'sequel', 'clip', 'spin_off', 'reference', 'reupload')
    ),
    CONSTRAINT chk_vrel_target_present CHECK (
        target_video_id IS NOT NULL OR target_session_id IS NOT NULL
    ),
    CONSTRAINT chk_vrel_timestamps CHECK (
        timestamp_start_seconds IS NULL
        OR timestamp_end_seconds IS NULL
        OR timestamp_end_seconds >= timestamp_start_seconds
    )
);

CREATE INDEX IF NOT EXISTS idx_vrel_source ON videos_video_relation(source_video_id);
CREATE INDEX IF NOT EXISTS idx_vrel_target_video ON videos_video_relation(target_video_id);
CREATE INDEX IF NOT EXISTS idx_vrel_target_session ON videos_video_relation(target_session_id);


-- ==============================================================================
-- 7. ALERTAS DE CANAL, SANCIONES (DMCA / TOS) Y ANOMALÍAS (App: `alerts`)
-- ==============================================================================

CREATE TABLE IF NOT EXISTS alerts_channel_alert (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    creator_id INTEGER NOT NULL REFERENCES creators_creator(id) ON DELETE CASCADE,
    channel_id INTEGER NULL REFERENCES creators_channel(id) ON DELETE SET NULL,
    related_session_id INTEGER NULL REFERENCES streams_streaming_session(id) ON DELETE SET NULL,
    related_publication_id INTEGER NULL REFERENCES videos_video_publication(id) ON DELETE SET NULL,
    assigned_to_id INTEGER NULL REFERENCES users_user(id) ON DELETE SET NULL,
    resolved_by_id INTEGER NULL REFERENCES users_user(id) ON DELETE SET NULL,

    alert_type VARCHAR(40) NOT NULL,
    severity VARCHAR(20) NOT NULL DEFAULT 'warning',
    status VARCHAR(20) NOT NULL DEFAULT 'active',

    strike_points INTEGER NOT NULL DEFAULT 0, -- Ej. 1 a 3 strikes en YouTube/Twitch
    strike_expires_at DATETIME NULL,
    account_suspension_days INTEGER NOT NULL DEFAULT 0,

    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    evidence_url VARCHAR(500) NOT NULL DEFAULT '',
    occurred_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME NULL,
    resolution_notes TEXT NOT NULL DEFAULT '',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_alert_type CHECK (
        alert_type IN (
            'dmca_strike',
            'copyright_claim',
            'tos_violation',
            'community_guideline_strike',
            'demonetization',
            'temporary_ban',
            'unusual_ccv_drop',
            'suspicious_bot_traffic',
            'quota_missed'
        )
    ),
    CONSTRAINT chk_alert_severity CHECK (
        severity IN ('info', 'warning', 'critical')
    ),
    CONSTRAINT chk_alert_status CHECK (
        status IN ('active', 'investigating', 'appealed', 'resolved', 'expired', 'dismissed')
    ),
    CONSTRAINT chk_alert_strikes_non_negative CHECK (
        strike_points >= 0 AND account_suspension_days >= 0
    )
);

CREATE INDEX IF NOT EXISTS idx_alerts_creator_status ON alerts_channel_alert(creator_id, status);
CREATE INDEX IF NOT EXISTS idx_alerts_severity_status ON alerts_channel_alert(severity, status);
CREATE INDEX IF NOT EXISTS idx_alerts_occurred_at ON alerts_channel_alert(occurred_at DESC);


-- ==============================================================================
-- 8. CAMPAÑAS COMERCIALES, PATROCINIOS Y ENTREGABLES (Funcionalidad Futura: `campaigns`)
-- ==============================================================================
-- Permite a la compañía gestionar acuerdos con marcas (brands), entregables por
-- creador (streams patrocinados o menciones en video) y su ROI comercial.

-- 8.1 Campañas de Marca / Sponsors
CREATE TABLE IF NOT EXISTS campaigns_sponsor_campaign (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_manager_id INTEGER NULL REFERENCES users_user(id) ON DELETE SET NULL,

    brand_name VARCHAR(150) NOT NULL,
    campaign_name VARCHAR(200) NOT NULL,
    campaign_code VARCHAR(60) NOT NULL UNIQUE,
    status VARCHAR(20) NOT NULL DEFAULT 'active',

    start_date DATE NOT NULL,
    end_date DATE NULL,

    total_budget NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    agency_fee_amount NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    creator_pool_amount NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    target_views_or_impressions BIGINT NOT NULL DEFAULT 0,

    brief_url VARCHAR(500) NOT NULL DEFAULT '',
    notes TEXT NOT NULL DEFAULT '',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_campaign_status CHECK (
        status IN ('proposal', 'negotiating', 'active', 'completed', 'invoiced', 'paid', 'cancelled')
    ),
    CONSTRAINT chk_campaign_budget_non_negative CHECK (
        total_budget >= 0 AND agency_fee_amount >= 0 AND creator_pool_amount >= 0
    )
);

CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns_sponsor_campaign(status);


-- 8.2 Entregables de Campaña por Creador (Vinculables a un Stream o Publicación de Video)
CREATE TABLE IF NOT EXISTS campaigns_campaign_deliverable (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL REFERENCES campaigns_sponsor_campaign(id) ON DELETE CASCADE,
    creator_id INTEGER NOT NULL REFERENCES creators_creator(id) ON DELETE CASCADE,
    linked_session_id INTEGER NULL REFERENCES streams_streaming_session(id) ON DELETE SET NULL,
    linked_publication_id INTEGER NULL REFERENCES videos_video_publication(id) ON DELETE SET NULL,

    deliverable_type VARCHAR(30) NOT NULL DEFAULT 'sponsored_stream',
    platform VARCHAR(20) NOT NULL DEFAULT 'twitch',
    title VARCHAR(255) NOT NULL,
    due_date DATE NULL,
    completed_at DATETIME NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',

    agreed_creator_payout NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    tracking_link VARCHAR(500) NOT NULL DEFAULT '',
    promo_code VARCHAR(60) NOT NULL DEFAULT '',
    conversions_count INTEGER NOT NULL DEFAULT 0,

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_deliverable_type CHECK (
        deliverable_type IN ('sponsored_stream', 'dedicated_video', 'integrated_ad_read', 'short_or_reel', 'social_post')
    ),
    CONSTRAINT chk_deliverable_status CHECK (
        status IN ('pending', 'in_progress', 'submitted', 'approved', 'published', 'rejected')
    )
);

CREATE INDEX IF NOT EXISTS idx_deliverables_campaign ON campaigns_campaign_deliverable(campaign_id);
CREATE INDEX IF NOT EXISTS idx_deliverables_creator ON campaigns_campaign_deliverable(creator_id, status);


-- ==============================================================================
-- 9. LIQUIDACIONES Y PAGOS A CREADORES (Funcionalidad Futura: `payouts`)
-- ==============================================================================

CREATE TABLE IF NOT EXISTS payouts_creator_payout (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    creator_id INTEGER NOT NULL REFERENCES creators_creator(id) ON DELETE CASCADE,
    contract_id INTEGER NULL REFERENCES creators_contract(id) ON DELETE SET NULL,
    approved_by_id INTEGER NULL REFERENCES users_user(id) ON DELETE SET NULL,

    period_year INTEGER NOT NULL,
    period_month INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'draft',

    -- Desglose bruto generado en el mes
    gross_stream_revenue NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    gross_video_revenue NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    gross_sponsorship_revenue NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    base_retainer_amount NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    bonuses_amount NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    deductions_or_recoupment NUMERIC(12, 2) NOT NULL DEFAULT 0.00,

    -- Montos netos finales
    agency_commission_amount NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    net_creator_payout NUMERIC(12, 2) NOT NULL DEFAULT 0.00,

    invoice_reference VARCHAR(120) NOT NULL DEFAULT '',
    paid_at DATETIME NULL,
    notes TEXT NOT NULL DEFAULT '',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_creator_payout_period UNIQUE (creator_id, period_year, period_month),
    CONSTRAINT chk_payout_period_month CHECK (period_month BETWEEN 1 AND 12),
    CONSTRAINT chk_payout_status CHECK (
        status IN ('draft', 'pending_approval', 'approved', 'paid', 'disputed', 'cancelled')
    )
);

CREATE INDEX IF NOT EXISTS idx_payouts_period ON payouts_creator_payout(period_year DESC, period_month DESC);
CREATE INDEX IF NOT EXISTS idx_payouts_status ON payouts_creator_payout(status);


-- ==============================================================================
-- 10. AUDITORÍA HISTÓRICA (`django-simple-history`)
-- ==============================================================================
-- Ejemplo de tabla histórica generada por django-simple-history para modelos críticos

CREATE TABLE IF NOT EXISTS creators_historicalcreator (
    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
    id INTEGER NOT NULL,
    user_id INTEGER NULL,
    manager_id INTEGER NULL,
    display_name VARCHAR(150) NOT NULL,
    handle VARCHAR(100) NOT NULL,
    primary_platform VARCHAR(20) NOT NULL,
    tier VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL,
    history_date DATETIME NOT NULL,
    history_change_reason VARCHAR(100) NULL,
    history_type VARCHAR(1) NOT NULL, -- '+' (Created), '~' (Changed), '-' (Deleted)
    history_user_id INTEGER NULL REFERENCES users_user(id) ON DELETE SET NULL,

    CONSTRAINT chk_history_type CHECK (history_type IN ('+', '~', '-'))
);

CREATE INDEX IF NOT EXISTS idx_hist_creator_id_date ON creators_historicalcreator(id, history_date DESC);


-- ==============================================================================
-- 11. VISTAS SQL ANALÍTICAS PARA SQLITE (Reemplazo de Vistas Legadas sin Multi-Tenant)
-- ==============================================================================
-- Nota: SQLite soporta CREATE VIEW nativamente (incluyendo funciones de ventana
-- como DENSE_RANK()). Para cargas pesadas, los Selectors de Django cachean el
-- resultado de estas vistas/consultas en DiskCache.

-- 11.1 v_creator_performance_summary (Rendimiento Consolidado por Creador: Streams + Videos)
DROP VIEW IF EXISTS v_creator_performance_summary;
CREATE VIEW v_creator_performance_summary AS
WITH stream_stats AS (
    SELECT
        creator_id,
        COUNT(id) AS total_streams,
        COALESCE(SUM(duration_seconds), 0) AS total_stream_seconds,
        ROUND(COALESCE(SUM(duration_seconds), 0) / 3600.0, 2) AS total_hours_streamed,
        CAST(ROUND(COALESCE(AVG(avg_ccv), 0), 0) AS INTEGER) AS overall_avg_ccv,
        COALESCE(MAX(peak_viewers), 0) AS max_peak_viewers,
        ROUND(COALESCE(SUM(total_earnings), 0.00), 2) AS total_stream_earnings
    FROM streams_streaming_session
    GROUP BY creator_id
),
video_stats AS (
    SELECT
        v.creator_id,
        COUNT(DISTINCT v.id) AS total_videos,
        COUNT(DISTINCT vp.id) AS total_publications,
        COALESCE(SUM(vp.views_count), 0) AS total_video_views,
        COALESCE(SUM(vp.likes_count), 0) AS total_video_likes,
        COALESCE(SUM(vp.comments_count), 0) AS total_video_comments,
        COALESCE(SUM(vp.shares_count), 0) AS total_video_shares,
        ROUND(COALESCE(SUM(vp.estimated_revenue), 0.00), 2) AS total_video_earnings
    FROM videos_video v
    LEFT JOIN videos_video_publication vp ON vp.video_id = v.id
    GROUP BY v.creator_id
)
SELECT
    c.id AS creator_id,
    c.display_name,
    c.handle,
    c.primary_platform,
    c.tier,
    c.status,
    COALESCE(ss.total_streams, 0) AS total_streams,
    COALESCE(ss.total_stream_seconds, 0) AS total_stream_seconds,
    COALESCE(ss.total_hours_streamed, 0.00) AS total_hours_streamed,
    COALESCE(ss.overall_avg_ccv, 0) AS overall_avg_ccv,
    COALESCE(ss.max_peak_viewers, 0) AS max_peak_viewers,
    COALESCE(ss.total_stream_earnings, 0.00) AS total_stream_earnings,
    COALESCE(vs.total_videos, 0) AS total_videos,
    COALESCE(vs.total_publications, 0) AS total_publications,
    COALESCE(vs.total_video_views, 0) AS total_video_views,
    COALESCE(vs.total_video_likes, 0) AS total_video_likes,
    COALESCE(vs.total_video_comments, 0) AS total_video_comments,
    COALESCE(vs.total_video_shares, 0) AS total_video_shares,
    COALESCE(vs.total_video_earnings, 0.00) AS total_video_earnings,
    ROUND(COALESCE(ss.total_stream_earnings, 0.00) + COALESCE(vs.total_video_earnings, 0.00), 2) AS total_combined_revenue
FROM creators_creator c
LEFT JOIN stream_stats ss ON ss.creator_id = c.id
LEFT JOIN video_stats vs ON vs.creator_id = c.id;


-- 11.2 v_creator_overall_rankings (Leaderboard Global de la Compañía con DENSE_RANK)
DROP VIEW IF EXISTS v_creator_overall_rankings;
CREATE VIEW v_creator_overall_rankings AS
SELECT
    m.*,
    DENSE_RANK() OVER (ORDER BY m.total_combined_revenue DESC) AS revenue_rank,
    DENSE_RANK() OVER (ORDER BY m.overall_avg_ccv DESC) AS ccv_rank,
    DENSE_RANK() OVER (ORDER BY m.total_hours_streamed DESC) AS hours_rank
FROM v_creator_performance_summary m;


-- 11.3 v_platform_category_stats (Rendimiento por Plataforma y Categoría/Juego)
DROP VIEW IF EXISTS v_platform_category_stats;
CREATE VIEW v_platform_category_stats AS
SELECT
    s.platform,
    COALESCE(NULLIF(s.game_or_category, ''), 'General') AS category_name,
    COUNT(s.id) AS session_count,
    ROUND(SUM(s.duration_seconds) / 3600.0, 2) AS total_hours,
    CAST(ROUND(AVG(s.avg_ccv), 0) AS INTEGER) AS avg_ccv,
    MAX(s.peak_viewers) AS max_peak,
    ROUND(SUM(s.total_earnings), 2) AS total_revenue
FROM streams_streaming_session s
GROUP BY s.platform, COALESCE(NULLIF(s.game_or_category, ''), 'General');


-- 11.4 v_monthly_revenue_summary (Resumen Financiero Mensual de la Compañía)
DROP VIEW IF EXISTS v_monthly_revenue_summary;
CREATE VIEW v_monthly_revenue_summary AS
WITH monthly_streams AS (
    SELECT
        strftime('%Y-%m', streamed_at) AS period_label,
        CAST(strftime('%Y', streamed_at) AS INTEGER) AS period_year,
        CAST(strftime('%m', streamed_at) AS INTEGER) AS period_month,
        COUNT(id) AS total_streams,
        ROUND(SUM(duration_seconds) / 3600.0, 2) AS total_stream_hours,
        CAST(ROUND(AVG(avg_ccv), 0) AS INTEGER) AS avg_ccv,
        MAX(peak_viewers) AS peak_viewers,
        ROUND(SUM(ad_revenue), 2) AS stream_ad_revenue,
        ROUND(SUM(subs_revenue), 2) AS stream_subs_revenue,
        ROUND(SUM(donations_revenue), 2) AS stream_donations_revenue,
        ROUND(SUM(total_earnings), 2) AS total_stream_earnings
    FROM streams_streaming_session
    GROUP BY strftime('%Y-%m', streamed_at)
),
monthly_videos AS (
    SELECT
        strftime('%Y-%m', published_at) AS period_label,
        CAST(strftime('%Y', published_at) AS INTEGER) AS period_year,
        CAST(strftime('%m', published_at) AS INTEGER) AS period_month,
        COUNT(id) AS total_publications,
        SUM(views_count) AS total_video_views,
        SUM(likes_count) AS total_video_likes,
        ROUND(SUM(estimated_revenue), 2) AS total_video_earnings
    FROM videos_video_publication
    GROUP BY strftime('%Y-%m', published_at)
),
periods AS (
    SELECT period_label, period_year, period_month FROM monthly_streams
    UNION
    SELECT period_label, period_year, period_month FROM monthly_videos
)
SELECT
    p.period_year,
    p.period_month,
    p.period_label,
    COALESCE(ms.total_streams, 0) AS total_streams,
    COALESCE(ms.total_stream_hours, 0.00) AS total_stream_hours,
    COALESCE(ms.avg_ccv, 0) AS avg_ccv,
    COALESCE(ms.peak_viewers, 0) AS peak_viewers,
    COALESCE(ms.stream_ad_revenue, 0.00) AS stream_ad_revenue,
    COALESCE(ms.stream_subs_revenue, 0.00) AS stream_subs_revenue,
    COALESCE(ms.stream_donations_revenue, 0.00) AS stream_donations_revenue,
    COALESCE(ms.total_stream_earnings, 0.00) AS total_stream_earnings,
    COALESCE(mv.total_publications, 0) AS total_publications,
    COALESCE(mv.total_video_views, 0) AS total_video_views,
    COALESCE(mv.total_video_likes, 0) AS total_video_likes,
    COALESCE(mv.total_video_earnings, 0.00) AS total_video_earnings,
    ROUND(COALESCE(ms.total_stream_earnings, 0.00) + COALESCE(mv.total_video_earnings, 0.00), 2) AS total_combined_revenue
FROM periods p
LEFT JOIN monthly_streams ms ON ms.period_label = p.period_label
LEFT JOIN monthly_videos mv ON mv.period_label = p.period_label
ORDER BY p.period_label DESC;


-- 11.5 v_video_publication_details (Detalle de Publicaciones con Beneficio Neto, ROI y RPM)
DROP VIEW IF EXISTS v_video_publication_details;
CREATE VIEW v_video_publication_details AS
SELECT
    vp.id AS publication_id,
    vp.video_id,
    vp.creator_id,
    c.display_name AS creator_name,
    c.handle AS creator_handle,
    v.title AS video_title,
    v.internal_name,
    v.category,
    v.duration_seconds,
    ROUND(v.duration_seconds / 60.0, 1) AS duration_minutes,
    v.total_production_cost AS production_cost,
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
    ROUND(vp.estimated_revenue - v.total_production_cost, 2) AS net_profit,
    CASE
        WHEN v.total_production_cost > 0
        THEN ROUND(((vp.estimated_revenue - v.total_production_cost) / v.total_production_cost) * 100.0, 2)
        ELSE NULL
    END AS roi_percentage,
    vp.rpm_estimated
FROM videos_video_publication vp
JOIN videos_video v ON v.id = vp.video_id
JOIN creators_creator c ON c.id = vp.creator_id;


-- 11.6 v_recent_channel_activity (Timeline Unificado de Streams, Videos y Alertas)
DROP VIEW IF EXISTS v_recent_channel_activity;
CREATE VIEW v_recent_channel_activity AS
SELECT
    'stream' AS activity_type,
    s.id AS activity_id,
    s.creator_id,
    c.display_name AS creator_name,
    s.platform,
    s.session_title AS title,
    s.game_or_category AS subtitle,
    s.streamed_at AS occurred_at,
    s.total_earnings AS monetary_value,
    s.avg_ccv AS primary_metric,
    'CCV' AS metric_unit
FROM streams_streaming_session s
JOIN creators_creator c ON c.id = s.creator_id
UNION ALL
SELECT
    'video' AS activity_type,
    vp.id AS activity_id,
    vp.creator_id,
    c.display_name AS creator_name,
    vp.platform,
    v.title AS title,
    vp.publication_type AS subtitle,
    vp.published_at AS occurred_at,
    vp.estimated_revenue AS monetary_value,
    vp.views_count AS primary_metric,
    'Vistas' AS metric_unit
FROM videos_video_publication vp
JOIN videos_video v ON v.id = vp.video_id
JOIN creators_creator c ON c.id = vp.creator_id
UNION ALL
SELECT
    'alert' AS activity_type,
    a.id AS activity_id,
    a.creator_id,
    c.display_name AS creator_name,
    COALESCE(ch.platform, c.primary_platform) AS platform,
    a.title AS title,
    a.severity AS subtitle,
    a.occurred_at AS occurred_at,
    0.00 AS monetary_value,
    a.strike_points AS primary_metric,
    a.status AS metric_unit
FROM alerts_channel_alert a
JOIN creators_creator c ON c.id = a.creator_id
LEFT JOIN creators_channel ch ON ch.id = a.channel_id;

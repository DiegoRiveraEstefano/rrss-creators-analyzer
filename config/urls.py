from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include
from django.urls import path
from django.views import defaults as default_views
from drf_spectacular.views import SpectacularAPIView
from drf_spectacular.views import SpectacularSwaggerView
from rest_framework.authtoken.views import obtain_auth_token

from rrss_creatos_analyzer.apps.core.views import AboutView
from rrss_creatos_analyzer.apps.core.views import DemoQuickLoginView
from rrss_creatos_analyzer.apps.core.views import HomeDashboardView

urlpatterns = [
    path("", HomeDashboardView.as_view(), name="home"),
    path("about/", AboutView.as_view(), name="about"),
    path("demo/login/", DemoQuickLoginView.as_view(), name="demo_login"),
    path("captcha/", include("captcha.urls")),
    # Django Admin, use {% url 'admin:index' %}
    path("admin/dj-cache-panel/", include("dj_cache_panel.urls")),
    path("admin/dj-urls-panel/", include("dj_urls_panel.urls")),
    path("admin/dj_signals_panel/", include("dj_signals_panel.urls")),
    path("admin/dj-control-room/", include("dj_control_room.urls")),
    path(settings.ADMIN_URL, admin.site.urls),
    # User & Access management
    path("users/", include("rrss_creatos_analyzer.apps.users.urls", namespace="users")),
    path(
        "permissions/",
        include("rrss_creatos_analyzer.apps.permissions.urls", namespace="permissions"),
    ),
    path(
        "members/",
        include("rrss_creatos_analyzer.apps.members.urls", namespace="members"),
    ),
    path("accounts/", include("allauth.urls")),
    # Core & Business Domain Apps
    path("core/", include("rrss_creatos_analyzer.apps.core.urls", namespace="core")),
    path(
        "creators/",
        include("rrss_creatos_analyzer.apps.creators.urls", namespace="creators"),
    ),
    path(
        "contracts/",
        include("rrss_creatos_analyzer.apps.contracts.urls", namespace="contracts"),
    ),
    path(
        "schedules/",
        include("rrss_creatos_analyzer.apps.schedules.urls", namespace="schedules"),
    ),
    path(
        "streams/",
        include("rrss_creatos_analyzer.apps.streams.urls", namespace="streams"),
    ),
    path(
        "videos/",
        include("rrss_creatos_analyzer.apps.videos.urls", namespace="videos"),
    ),
    path(
        "editors/",
        include("rrss_creatos_analyzer.apps.editors.urls", namespace="editors"),
    ),
    path(
        "alerts/",
        include("rrss_creatos_analyzer.apps.alerts.urls", namespace="alerts"),
    ),
    path(
        "campaigns/",
        include("rrss_creatos_analyzer.apps.campaigns.urls", namespace="campaigns"),
    ),
    path(
        "payouts/",
        include("rrss_creatos_analyzer.apps.payouts.urls", namespace="payouts"),
    ),
    path(
        "analytics/",
        include("rrss_creatos_analyzer.apps.analytics.urls", namespace="analytics"),
    ),
    # Data Pipeline & Operations Apps
    path(
        "imports/",
        include("rrss_creatos_analyzer.apps.imports.urls", namespace="imports"),
    ),
    path(
        "exports/",
        include("rrss_creatos_analyzer.apps.exports.urls", namespace="exports"),
    ),
    path(
        "audit/",
        include("rrss_creatos_analyzer.apps.audit.urls", namespace="audit"),
    ),
    path(
        "logs/",
        include("rrss_creatos_analyzer.apps.logs.urls", namespace="logs"),
    ),
    path(
        "monitor/",
        include("rrss_creatos_analyzer.apps.monitor.urls", namespace="monitor"),
    ),
    path(
        "backups/",
        include("rrss_creatos_analyzer.apps.backups.urls", namespace="backups"),
    ),
    # Media files
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]
if settings.DEBUG:
    # Static file serving when using Gunicorn + Uvicorn for local web socket development
    urlpatterns += staticfiles_urlpatterns()

# API URLS
urlpatterns += [
    # API base url
    path("api/", include("config.api_router")),
    # DRF auth token
    path("api/auth-token/", obtain_auth_token, name="obtain_auth_token"),
    path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="api-schema"),
        name="api-docs",
    ),
]

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
            *urlpatterns,
        ]

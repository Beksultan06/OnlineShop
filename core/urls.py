from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.static import serve as static_serve
from pathlib import Path

# Swagger
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from core.views import FrontendApp

schema_view = get_schema_view(
    openapi.Info(
        title="Shop API",
        default_version='v1',
        description="Документация API для проекта Shop",
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# === ПУТЬ К Vite-билду ===
# если папка с билдом называется иначе (например, frontend_dist), поменяй тут
DIST_DIR = Path(settings.BASE_DIR) / "dist"

urlpatterns = [
    path('admin/', admin.site.urls),

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/',   schema_view.with_ui('redoc',   cache_timeout=0), name='schema-redoc'),
]

# i18n API маршруты
urlpatterns += i18n_patterns(
    path('api/v1/shop/',     include('app.shop.urls')),
    path('api/v1/settings/', include('app.settings.urls')),
)

# Статика и медиа в DEBUG (helper добавляет только при DEBUG=True)
urlpatterns += static(settings.MEDIA_URL,  document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# === Vite ассеты (ОБЯЗАТЕЛЬНО ДО catch-all!) ===
# /assets/* и /vite.svg должны отдаваться как файлы из билда, иначе будет белый экран
urlpatterns += [
    re_path(r'^assets/(?P<path>.*)$',
            static_serve, {'document_root': DIST_DIR / 'assets'}),
    re_path(r'^vite\.svg$',
            static_serve, {'document_root': DIST_DIR}),
]

# === Catch-all ДОЛЖЕН быть самым последним ===
urlpatterns += [
    re_path(r'^.*$', FrontendApp.as_view(), name='spa'),
]

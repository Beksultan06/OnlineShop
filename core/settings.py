from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ── БАЗОВОЕ ─────────────────────────────────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = True  # В проде лучше False

ALLOWED_HOSTS = [
    "megamix24.com",
    "www.megamix24.com",
    "megamix.webtm.ru",
    "188.225.44.65",
    "localhost:5173",
    "127.0.0.1",
]

# Если сайт за прокси/NGINX с HTTPS — ОБЯЗАТЕЛЬНО указать этот заголовок
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# ── ТЕЛЕГРАМ ───────────────────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

# ── APPS ───────────────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    "jazzmin",
    "corsheaders",
    "modeltranslation",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
    "django_filters",
    "drf_yasg",
    "django_celery_beat",

    "app.shop",
    "app.settings",
    "ckeditor",
]

# ── MIDDLEWARE ─────────────────────────────────────────────────────────────────
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # оставляем самым верхним
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",   # ← ВКЛЮЧАЕМ обратно CSRF
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "app.analytics.middleware.VisitMiddleware",
]

ROOT_URLCONF = "core.urls"

# ── TEMPLATES ──────────────────────────────────────────────────────────────────
FRONTEND_DIR = BASE_DIR / "dist"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [FRONTEND_DIR],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

# ── БД ─────────────────────────────────────────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ── DRF ────────────────────────────────────────────────────────────────────────
# Оставляем SessionAuthentication (она требует CSRF) и TokenAuthentication
REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "core.auth.CsrfExemptSessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
}

# ── ПАРОЛИ ─────────────────────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ── ЛОКАЛИ/ВРЕМЯ ───────────────────────────────────────────────────────────────
LANGUAGE_CODE = "ru"
LANGUAGES = [("ru", "Russian"), ("en", "English")]
MODELTRANSLATION_DEFAULT_LANGUAGE = "ru"

TIME_ZONE = "Asia/Bishkek"
USE_I18N = True
USE_TZ = True

# ── СТАТИКА/МЕДИА ──────────────────────────────────────────────────────────────
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"
STATICFILES_DIRS = [FRONTEND_DIR / "assets"]

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ── JAZZMIN ───────────────────────────────────────────────────────────────────
JAZZMIN_SETTINGS = {
    "site_title": "Мой магазин",
    "site_header": "Панель управления",
    "site_brand": "Админка",
    "welcome_sign": "Добро пожаловать в админку",
    "copyright": "Мой проект © 2025",
}

# ── CORS/CSRF/COOKIES ─────────────────────────────────────────────────────────
# У тебя POST идёт с того же origin (megamix24.com) → SameSite="Lax" достаточно.
# Если реально нужен cross-origin фронт (например, megamix.webtm.ru), верни "None".
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE   = "Lax"

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE    = True

# чтобы JS мог прочитать csrftoken и положить его в заголовок X-CSRFToken
CSRF_COOKIE_HTTPONLY = False

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    "https://megamix24.com",
    "https://www.megamix24.com",
    "http://localhost:5173",
    "https://localhost:5173",
    "http://188.225.44.65",
    "https://188.225.44.65",
]

CSRF_TRUSTED_ORIGINS = [
    "https://megamix24.com",
    "https://www.megamix24.com",
    "https://megamix.webtm.ru",
    "https://188.225.44.65",
    "https://localhost:5173",
]

CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]

CORS_ALLOW_HEADERS = [
    "authorization",
    "content-type",
    "accept",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

# ── CELERY ─────────────────────────────────────────────────────────────────────
CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Asia/Bishkek"

# ── СЕССИИ ─────────────────────────────────────────────────────────────────────
SESSION_COOKIE_AGE = 60 * 60 * 24 * 30  # 30 дней
SESSION_SAVE_EVERY_REQUEST = True

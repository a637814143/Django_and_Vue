import os
from datetime import timedelta
from pathlib import Path

from corsheaders.defaults import default_headers

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-change-me")
DEBUG = os.getenv("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,47.108.151.60").split(",")
    if host.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "django_filters",
    "corsheaders",
    "campus_store.accounts",
    "campus_store.catalog",
    "campus_store.commerce",
    "campus_store.customization",
    "campus_store.analytics",
    "campus_store.community",
    "campus_store.focus",
    "campus_store.wallet",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "campus_store.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "campus_store.wsgi.application"

USE_SQLITE = os.getenv("DJANGO_USE_SQLITE", "0") == "1"
if USE_SQLITE:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.getenv("MYSQL_DATABASE", "yhl_0118"),
            "USER": os.getenv("MYSQL_USER", "yhl_0118"),
            "PASSWORD": os.getenv("MYSQL_PASSWORD", "qiQi1314**00"),
            "HOST": os.getenv("MYSQL_HOST", "47.108.151.60"),
            "PORT": os.getenv("MYSQL_PORT", "3306"),
            "OPTIONS": {
                "charset": "utf8mb4",
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "zh-hans"
TIME_ZONE = "Asia/Shanghai"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.User"
LOGIN_URL = "/login"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "None" if DEBUG else "Lax"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = "None" if DEBUG else "Lax"
CSRF_COOKIE_SECURE = True

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "campus_store.accounts.authentication.SessionTokenAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "campus_store.accounts.permissions.AuthenticatedOrRedirect",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "EXCEPTION_HANDLER": "campus_store.exceptions.api_exception_handler",
}

SESSION_TOKEN_TTL_HOURS = int(os.getenv("SESSION_TOKEN_TTL_HOURS", "12"))

CORS_ALLOW_CREDENTIALS = True
# 开发环境放宽源限制，方便本地调试（Vite 5173/4173/5174 等）
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
    ]
CORS_ALLOW_HEADERS = list(default_headers) + ["x-session-token", "X-SESSION-TOKEN"]
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]

"""
Django settings for mysite project.
使用 django-environ：所有环境相关配置来自 .env 或环境变量，不区分配置文件。
参考：https://django-environ.readthedocs.io/
"""

import os
from datetime import timedelta
from pathlib import Path

import environ

# 项目根目录：api/
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(DEBUG=(bool, False), ALLOWED_HOSTS=(list, []))

# 从项目根目录的 .env 加载（.env 按环境各自维护，不提交版本库）
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# ---------- 安全与基础 ----------
SECRET_KEY = env("SECRET_KEY", default="django-insecure-dev-key-change-in-production")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")

# ---------- 应用与中间件 ----------
INSTALLED_APPS = [
    "django.contrib.admin",  # Django管理后台应用
    "django.contrib.auth",  # Django认证系统
    "django.contrib.contenttypes",  # 内容类型框架
    "django.contrib.sessions",  # 会话框架
    "django.contrib.messages",  # 消息框架
    "django.contrib.staticfiles",  # 静态文件管理
    "django_filters",  # 过滤器
    "corsheaders",  # CORS 跨域支持
    "rest_framework",  # Django REST framework
    "rest_framework_simplejwt",  # JWT 认证（无状态，不需要数据库）
    "apps.authorization",
    "apps.apilog",
    "apps.system",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",  # 安全中间件，提供安全相关HTTP头
    "corsheaders.middleware.CorsMiddleware",  # CORS 中间件（必须在 CommonMiddleware 之前）
    "django.contrib.sessions.middleware.SessionMiddleware",  # 会话中间件，处理会话
    "django.middleware.common.CommonMiddleware",  # 通用中间件，处理URL规范化等
    "django.middleware.csrf.CsrfViewMiddleware",  # CSRF保护中间件
    "django.contrib.auth.middleware.AuthenticationMiddleware",  # 认证中间件，处理用户认证
    "django.contrib.messages.middleware.MessageMiddleware",  # 消息中间件，处理一次性消息
    "django.middleware.clickjacking.XFrameOptionsMiddleware",  # 点击劫持保护中间件
    "apps.apilog.middleware.ApiLogMiddleware",
]

# ---------- CORS ----------
CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=["http://localhost:5173", "http://127.0.0.1:5173"],
)
CORS_ALLOW_CREDENTIALS = True  # 允许携带 Cookie

# ---------- URL / 模板 / WSGI ----------
ROOT_URLCONF = "mysite.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",  # 模板后端引擎
        "DIRS": [],  # 模板文件搜索目录列表
        "APP_DIRS": True,  # 是否在已安装应用的目录中查找模板
        "OPTIONS": {  # 模板选项配置
            "context_processors": [  # 上下文处理器列表
                "django.template.context_processors.request",  # 请求上下文处理器
                "django.contrib.auth.context_processors.auth",  # 认证上下文处理器
                "django.contrib.messages.context_processors.messages",  # 消息上下文处理器
            ],
        },
    },
]
WSGI_APPLICATION = "mysite.wsgi.application"  # WSGI应用对象，用于部署

# ---------- 数据库 ----------
# 未设置 DATABASE_URL 时使用 SQLite；生产可用 psql://user:pass@host:port/dbname
_db_url = env("DATABASE_URL", default=None)
if _db_url:
    DATABASES = {"default": env.db("DATABASE_URL")}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# ---------- 密码校验 ----------
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },  # 验证密码与用户属性（如用户名）的相似度
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},  # 验证密码最小长度
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},  # 验证密码是否为常见密码
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},  # 验证密码是否全为数字
]

# ---------- 国际化 ----------
LANGUAGE_CODE = "zh-hans"  # 语言代码，设置项目的默认语言
TIME_ZONE = "Asia/Shanghai"  # 北京时区
USE_I18N = True  # 启用国际化支持
USE_TZ = True  # 启用时区支持

# ---------- 静态文件 ----------
STATIC_URL = "static/"  # 静态文件URL前缀，用于在模板中引用静态文件
STATIC_ROOT = str(BASE_DIR / "staticfiles")

# ---------- 主键 ----------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"  # 默认主键字段类型，用于自动生成的主键

# ---------- DRF ----------
REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "utils.custom_exception.custom_exception_handler",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    # 登录接口限流，防止暴力破解（按 IP，如 10 次/分钟）
    "DEFAULT_THROTTLE_RATES": {
        "login": env("LOGIN_THROTTLE_RATE", default="3/min"),
    },
}

# ---------- Simple JWT ----------
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=env.int("JWT_ACCESS_HOURS", default=24)),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=env.int("JWT_REFRESH_DAYS", default=7)),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

# ---------- 接口日志排除路径 ----------
APILOG_EXCLUDE_PATHS = ["/static/", "/favicon.ico", "/api/apilog"]

# ---------- Loguru 接管 logging ----------
from utils.custom_logger import setup_logging_intercept

setup_logging_intercept()

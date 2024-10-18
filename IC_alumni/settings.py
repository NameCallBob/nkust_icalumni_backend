"""
Django settings for IC_alumni project.

Generated by 'django-admin startproject' using Django 5.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from datetime import timedelta

from pathlib import Path
from dotenv import load_dotenv
import os

# 匯入環境變數
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Auth_UserModel
AUTH_USER_MODEL = 'Private.Private'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    # 本機端    
    "127.0.0.1",
    # 瓊文伺服器測試用
    os.getenv("TEST_SERVER_IP"),
    # 實際上架伺服器
    # os.getenv("PRODUCTION_SERVER_IP"),
    ]


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # RESTful API & JWT token
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',

    # 使用者相關
    "apps.private.apps.PrivateConfig",
    "apps.member.apps.MemberConfig",
    "apps.company.apps.CompanyConfig",
    "apps.product.apps.ProductConfig",
    # 功能
    "apps.article.apps.ArticleConfig",
    "apps.picture.apps.PictureConfig",
    "apps.recruit.apps.RecruitConfig",
    "apps.notice.apps.NoticeConfig",

    # swagger or redoc
    "drf_yasg",
    # for article release
    'ckeditor',
    # CORS
    'corsheader',



]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    # CORS
    'corsheaders.middleware.CorsMiddleware',
    # 照片
    'IC_alumni.middleware.CORSMiddlewareForStaticFiles',

    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'IC_alumni.urls'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    # 設置分頁
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
}

# JWTtoken設定

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=3),  # 設定JWT Token的有效期
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
    'SLIDING_TOKEN_LIFETIME': timedelta(days=1),
    'SLIDING_TOKEN_REFRESH_LIFETIME_LAMBDA': lambda token: token.access_token.lifetime,
    'SLIDING_TOKEN_LIFETIME_LAMBDA': lambda token: token.access_token.lifetime,
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'AUTH_HEADER_TYPES': ('Bearer', 'JWT'),
    "ALGORITHM": "HS256",
    'SIGNING_KEY': SECRET_KEY,
    'USER_ID_FIELD': 'id',
    # 設定
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "TOKEN_OBTAIN_SERIALIZER": "data_maintenance.serializers.Member_TokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",

}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR,"apps","notice","templates"),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'IC_alumni.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv("SERVER_DATABASE"),
        'USER': os.getenv("SERVER_USER"),
        'PASSWORD': os.getenv("SERVER_PWD"),
        'HOST': os.getenv("SERVER_IP"),
        'PORT': os.getenv("SERVER_PORT"),
    }
}



# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'zh-Hant'

TIME_ZONE = 'Asia/Taipei'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'

# 開發
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# 實際架設
STATIC_ROOT = BASE_DIR / 'static_files'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS setting_開發完後要打開
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3000/"
# ]

CORS_ALLOW_METHODS = [
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
    'DELETE',
]

CORS_ALLOW_HEADERS = [
    'Accept',
    'accept-encoding',
    'Authorization',
    'Content-Type',
    'dnt',
    'origin',
    'user-agent',
    # ngrok 免費版服務必須標頭 (開發會為no-simple request)
    'ngrok-skip-browser-warning',
]

CORS_ALLOW_CREDENTIALS = True
# 開發轉為True，記得上線轉為False
CORS_ALLOW_ALL_ORIGINS = True

# SMTP Service
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = 'noreply_nkustICalumni@gmail.com'

from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = os.getenv("DEBUG", "False") == "True"

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

WEB_VERSION = os.getenv("WEB_VERSION", "1.0.0")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost").split(",")

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'dltik',
    'django.contrib.sitemaps',
    'tinymce'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'dlhub.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'dltik.context.global_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'dlhub.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv("DB_NAME"),
        'USER': os.getenv("DB_USER"),
        'PASSWORD': os.getenv("DB_PASSWORD"),
        'HOST': os.getenv("DB_HOST", "localhost"),
        'PORT': os.getenv("DB_PORT", "3306"),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET NAMES 'utf8mb4' COLLATE 'utf8mb4_unicode_ci'"
        },
    }
}

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_TZ = True

USE_I18N = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'dltik' / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files (uploaded video output)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")

CKEDITOR_UPLOAD_PATH = "uploads/"

TINYMCE_DEFAULT_CONFIG = {
    'height': '720',
    'width': '100%',
    'menubar': True,
    'plugins': 'image code codesample lists link',
    'toolbar': 'undo redo | formatselect | bold italic underline | alignleft aligncenter alignright | bullist numlist indent outdent | link unlink | image | code',
    'images_upload_url': '/tinymce/upload/',
    'automatic_uploads': True,
    'file_picker_types': 'image',
    'content_css': [
        'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css',
        'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css',
    ],
    'valid_elements': '*[*]',
    'extended_valid_elements': 'style[type],script[language|type|src|charset],iframe[src|width|height|name|align|allowfullscreen|frameborder],a[href|target|rel]',
    'verify_html': False,
    'codesample_languages': [
        {'text': 'Python', 'value': 'python'},
        {'text': 'HTML/XML', 'value': 'markup'},
        {'text': 'JavaScript', 'value': 'javascript'},
        {'text': 'CSS', 'value': 'css'},
        {'text': 'Bash', 'value': 'bash'},
        {'text': 'JSON', 'value': 'json'},
    ],
}

RECAPTCHA_SITE_KEY = os.getenv("RECAPTCHA_SITE_KEY")
RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY")
# Meta SEO
SITE_NAME = os.getenv("SITE_NAME")
META_TITLE = os.getenv("META_TITLE")
META_DESC = os.getenv("META_DESC")
META_KEYWORDS = os.getenv("META_KEYWORDS")

# Google Analytics & Ads
GA_ID = os.getenv("GA_ID", "")
GOOGLE_ADSENSE_CLIENT = os.getenv("GOOGLE_ADSENSE_CLIENT", "")
GOOGLE_ADS_ID = os.getenv("GOOGLE_ADS_ID", "")
GOOGLE_ADS_CONVERSION_1 = os.getenv("GOOGLE_ADS_CONVERSION_1", "")
GOOGLE_ADS_CONVERSION_2 = os.getenv("GOOGLE_ADS_CONVERSION_2", "")

THEMES = [
    {"thame": "auto", "text": "Auto", "icon": "bi-circle-half"},
    {"thame": "light", "text": "Sáng", "icon": "bi-sun"},
    {"thame": "dark", "text": "Tối", "icon": "bi-moon"},
]
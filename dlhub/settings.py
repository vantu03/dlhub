from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-*e+drp1##-#*#*@-2!^y!+%v4o3t13=oab46l385t899ahpx1l'

DEBUG = True

ALLOWED_HOSTS = ['dlhub.vn', '.dlhub.vn', '127.0.0.1', 'localhost', '14.225.192.23']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'dltik',
    'ckeditor',
    'ckeditor_uploader',
    'django.contrib.sitemaps',
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
                'dltik.context.current_url'
            ],
        },
    },
]

WSGI_APPLICATION = 'dlhub.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'svprovn_dlhub',
        'USER': 'svprovn_vantu',
        'PASSWORD': 'DvAHy7j6Sfk@GWw',
        'HOST': '103.200.23.188',
        'PORT': '3306',
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

CSRF_TRUSTED_ORIGINS = ['https://dlhub.vn']

CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': [
            {'name': 'document', 'items': ['Source']},
            {'name': 'basicstyles', 'items': ['Bold', 'Italic', 'Underline']},
            {'name': 'paragraph', 'items': ['NumberedList', 'BulletedList', 'Blockquote']},
            {'name': 'links', 'items': ['Link', 'Unlink']},
            {'name': 'insert', 'items': ['Image', 'Table']},
            {'name': 'styles', 'items': ['Format', 'FontSize']},
            {'name': 'tools', 'items': ['RemoveFormat', 'Maximize']},
        ],
        'height': 500,
        'width': 'auto',
        'toolbarCanCollapse': False,
        'removePlugins': 'elementspath',
        'resize_enabled': True,
        'filebrowserUploadUrl': "/ckeditor/upload/",
        'filebrowserBrowseUrl': "/ckeditor/browse/",
        'contentsCss': [
            'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css',
            'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css'
            '/static/css/ckeditor_dark.css?v1',
        ],
        'allowedContent': True,
    }
}
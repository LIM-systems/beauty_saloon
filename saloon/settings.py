from os import makedirs, path
from pathlib import Path

import env

if not path.exists('logs'):
    makedirs('logs')

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = env.SECRET_KEY

DEBUG = env.DEBUG

ALLOWED_HOSTS = env.ALLOWED_HOSTS

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'inwork.apps.InworkConfig',
    'corsheaders',
    'rest_framework',
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
    ]
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

CORS_ALLOWED_ORIGINS = env.CORS_ALLOWED_ORIGINS

CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = 'saloon.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'saloon.wsgi.application'

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

LANGUAGE_CODE = 'ru-RU'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = False


STATIC_URL = 'static/'
MEDIA_URL = 'media/'
MEDIA_ROOT = path.join(BASE_DIR, 'media/')

brstart = path.join(MEDIA_ROOT, 'broadcasts/start')
brfinish = path.join(MEDIA_ROOT, 'broadcasts/finish')
# создадим папки для отчетов по рассылкам если их нет
if not path.exists(brstart):
    makedirs(brstart)
if not path.exists(brfinish):
    makedirs(brfinish)

# developer
if DEBUG:
    # STATIC_ROOT = path.join(BASE_DIR, 'static/')
    STATICFILES_DIRS = [path.join(BASE_DIR, 'static/'),]
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
            }
    }

# production
else:
    STATIC_ROOT = path.join(BASE_DIR, 'static/')
    # STATICFILES_DIRS = [path.join(BASE_DIR, 'static/'),]
    DATABASES = {
        'default': {
            'ENGINE': env.DB_ENGINE,
            'NAME': env.DB_NAME,
            'USER': env.POSTGRES_USER,
            'PASSWORD': env.POSTGRES_PASSWORD,
            'HOST': env.DB_HOST,
            'PORT': env.DB_PORT
        }
    }

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


JAZZMIN_SETTINGS = {

    'order_with_respect_to': [
        'inwork.client',
        'inwork.master',
        'inwork.masterschedule',
        'inwork.visitjournal',
        'inwork.service',
        'inwork.categories',
        'inwork.broadcast',
    ],

    # title of the window (Will default to current_admin_site.site_title if absent or None)
    'site_title': 'Ваниль админка',

    # Title on the login screen (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    'site_header': 'Ваниль',

    # Title on the brand (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    'site_brand': 'Ваниль',

    # CSS classes that are applied to the logo above
    'site_logo_classes': 'img-circle',

    # Welcome text on the login screen
    'welcome_sign': 'Добро пожаловать в админку Ваниль',

    # Copyright on the footer
    'copyright': 'Ваниль',
    # Показать кнопку настройки UI
    'show_ui_builder': True,

    "icons": {
        'inwork.client': 'fas fas fa-user',
        'inwork.master': 'fas fa-star',
        'inwork.masterschedule': 'fas fa-forward',
        'inwork.visitjournal': 'fas fa-check',
        'inwork.service': 'fas fa-history',
        'inwork.categories': 'fas fa-list',
        'inwork.broadcast': 'fas fa-paper-plane',
    },

}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": True,
    "footer_small_text": False,
    "body_small_text": True,
    "brand_small_text": True,
    "brand_colour": "navbar-dark",
    "accent": "accent-primary",
    "navbar": "navbar-white navbar-light",
    "no_navbar_border": True,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-purple",
    "sidebar_nav_small_text": True,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": True,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": True,
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-outline-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    },
    "actions_sticky_top": False
}
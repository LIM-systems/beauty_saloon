from os import makedirs, path
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler
import env


BASE_DIR = Path(__file__).resolve().parent.parent

log_dir = path.join(BASE_DIR, 'logs')

if not path.exists('logs'):
    makedirs('logs')

SECRET_KEY = env.SECRET_KEY
BASE_URL = env.BASE_URL
DEBUG = env.DEBUG


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
    'rangefilter',
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
    ),
}


# dev
# ALLOWED_HOSTS = ['*']
# ACCESS_CONTROL_ALLOW_ORIGIN = '*'
# CORS_ORIGIN_ALLOW_ALL = True
# CORS_ALLOW_CREDENTIALS = True
# ACCESS_CONTROL_ALLOW_CREDENTIALS = True
# ACCESS_CONTROL_ALLOW_METHODS = '*'
# ACCESS_CONTROL_ALLOW_HEADERS = '*'

'''
SESSION_COOKIE_SECURE = True
'''
# CSRF_COOKIE_SAMESITE = 'None'
# SESSION_COOKIE_SAMESITE = 'None'


CSRF_TRUSTED_ORIGINS = [BASE_URL]


# prod
ALLOWED_HOSTS = [BASE_URL, '*']

CORS_ALLOWED_ORIGINS = env.CORS_ALLOWED_ORIGINS

CORS_ALLOW_CREDENTIALS = True

# Разрешает куки передаваться между разными доменами
SESSION_COOKIE_SAMESITE = 'None'
# Использование secure cookies (только через HTTPS)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'None'    # Для CSRF токенов тоже
CSRF_COOKIE_SECURE = True        # Для безопасности CSRF токенов
CSRF_USE_SESSIONS = True


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

# developer
if DEBUG:
    # STATIC_ROOT = path.join(BASE_DIR, 'static/')
    STATICFILES_DIRS = [path.join(BASE_DIR, 'static/'), ]

# production
else:
    STATIC_ROOT = path.join(BASE_DIR, 'static/')

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


LOGGING_LEVEL = logging.DEBUG

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'main_format': {
            'format': '{asctime} - {levelname} - {module} - {filename} - {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': LOGGING_LEVEL,
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'main_format',
            'filename': path.join(log_dir, 'django.log'),
            'maxBytes': 500 * 1024 * 1024,
            'backupCount': 3,
        },
        'console': {  # Вот новый обработчик для вывода в консоль
            'level': LOGGING_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'main_format',
        },
    },
    'loggers': {
        'main': {
            'handlers': ['file'],
            'level': LOGGING_LEVEL,
            'propagate': True,
        },
    },
}

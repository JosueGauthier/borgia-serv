"""
Django settings for borgia project.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

'''
⚠️⚠️⚠️
THIS FILE IS FOR PRODUCTION ONLY.
FOR DEVELOPMENT, USE THE FILE IN THE FOLDER DEVELOPMENT AND CHECK THE DOCUMENTATION.

BEFORE USE:
- COPY THIS FILE IN BORGIA/BORGIA
- CHANGE PARAMETERS LABELLED AS "TO BE CHANGED" TO THE RIGHT VALUE.
⚠️⚠️⚠️
'''


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'XXX'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['86.212.121.222','borgia.boquette.fr', 'localhost', '*']


# Application definition
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrapform',
    'static_precompiler',
    'configurations',
    'users',
    'shops',
    'finances',
    'events',
    'modules',
    'sales',
    'stocks',
    'rest_framework',
    'django_filters',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware'
]

ROOT_URLCONF = 'borgia.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages'
            ],
            'builtins': ['users.templatetags.users_extra']
        },
    },
]

WSGI_APPLICATION = 'borgia.wsgi.application'

# Database
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': '',
#         'USER': '',
#         'PASSWORD': '',
#         'HOST': '',
#         'PORT': '5432',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'borgia12',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Password validation
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend'
]

# Token auth backend
# TOKEN_CHECK_ACTIVE_USER = True
# TOKEN_TIMEOUT_DAYS = 7

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
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Auth
AUTH_USER_MODEL = 'users.User'
LOGIN_URL = '/'
LOGIN_REDIRECT_URL = '/members/'
LOGOUT_REDIRECT_URL = LOGIN_URL


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static', 'static_root')
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static', 'static_dirs'),
)

if DEBUG:
    STATIC_PRECOMPILER_ROOT = os.path.join(BASE_DIR, 'static', 'static_dirs')


MEDIA_ROOT = os.path.join(BASE_DIR, 'static', 'media')
MEDIA_URL = '/media/'


EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = '@gmail.com'
SERVER_EMAIL = '@gmail.com'
EMAIL_HOST = 'TO BE CHANGED'
EMAIL_PORT = 'TO BE CHANGED'
EMAIL_HOST_USER = '@mail.com'
EMAIL_HOST_PASSWORD = ''
EMAIL_BACKEND = 'TO BE CHANGED'


ADMINS = ['@gmail.com']


# Password reset validity duration
PASSWORD_RESET_TIMEOUT_DAYS = 1  # en jours


# Automatic session logout
SESSION_COOKIE_AGE = 7200


DEFAULT_TEMPLATE = "light"  # Default template, en minuscule


DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    # 'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend']
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],

    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ]



}

CSRF_TRUSTED_ORIGINS = ['https://*.boquette.fr','https://*.127.0.0.1']



LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/borgia-app/test.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

import os, sys
from django.utils.crypto import get_random_string

def str2bool(value):
    '''Convert a string value to a boolean'''
    value = value.lower()

    if value in ('t', 'true', 'y', 'yes', '1', ):
        return True

    if value in ('f', 'false', 'n', 'no', '0', ):
        return False

    raise RuntimeError('Unable to parse {} as a boolean value'.format(value))

VERSION = '0.1'

TEST = 'test' in sys.argv
COMPRESS_ENABLED = True

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))

PRODUCTION = True if CURRENT_PATH.startswith('/var/www') else False
DEBUG = False

HOME = os.environ.get('HOME','/tmp')

MANAGERS = ADMINS
SITE_ID = 1

DATABASES = {
    'default': {
        'NAME': os.environ.get('DB_NAME', ''),
        "USER": os.environ.get('DB_USER', ''),
        "PASSWORD": os.environ.get('DB_PASSWD', ''),
        "HOST": os.environ.get('DB_HOST', ''),
        "ENGINE": "django.db.backends.mysql",
        }
    }

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


SECRET_KEY = os.environ.get('SECRET_KEY','')
if not SECRET_KEY:
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    SECRET_KEY = get_random_string(50, chars)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'observe.apps.ObserveConfig',
    'pagedown',
    'markdown_deux',
    'storages',
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

ROOT_URLCONF = 'asteroidday.urls'

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
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.contrib.messages.context_processors.messages',

            ],
        },
    },
]

WSGI_APPLICATION = 'asteroidday.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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

MARKDOWN_DEUX_STYLES = {
    "default": {
        "extras": {
            "code-friendly": None,
        },
        "safe_mode": False,
    },
}

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False


TOKEN_API = 'api-token-auth/'
THUMBNAIL_URL = 'https://thumbnails.lco.global/'
ARCHIVE_URL = 'https://archive-api.lco.global/'

ARCHIVE_TOKEN = os.environ.get('ARCHIVE_TOKEN','')

PORTAL_API_URL = 'https://observe.lco.global/api/'
PORTAL_REQUEST_API = PORTAL_API_URL + 'userrequests/'
PORTAL_TOKEN_URL = PORTAL_API_URL + 'api-token-auth/'
PORTAL_PROFILE_API = PORTAL_API_URL + 'profile/'

PORTAL_TOKEN = os.environ.get('PORTAL_TOKEN','')

PROPOSAL_USER = os.environ.get('PROPOSAL_USER','')
PROPOSAL_CODE = os.environ.get('PROPOSAL_CODE','')

FFMPEG = '/bin/ffmpeg'

STATIC_ROOT = '/var/www/html/static/'
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR,'observe','static'),]

MEDIA_ROOT = os.path.join(BASE_DIR, 'timelapse')
MEDIA_URL = '/timelapse/'

if str2bool(os.getenv('USE_S3', 'False')):
    # aws settings
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.getenv('AWS_DEFAULT_REGION', 'us-west-2')
    AWS_DEFAULT_ACL = None
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
    # s3 public media settings
    PUBLIC_MEDIA_LOCATION = 'timelapse'
    MEDIA_URL = f'https://s3-{AWS_S3_REGION_NAME}.amazonaws.com/{AWS_STORAGE_BUCKET_NAME}/{PUBLIC_MEDIA_LOCATION}/'
    DEFAULT_FILE_STORAGE = 'asteroidday.storage_backends.PublicMediaStorage'
    # s3 public static files storage settings
    PUBLIC_STATIC_LOCATION = 'static'
    STATIC_URL = f'https://s3-{AWS_S3_REGION_NAME}.amazonaws.com/{AWS_STORAGE_BUCKET_NAME}/{PUBLIC_STATIC_LOCATION}/'
    STATICFILES_STORAGE = 'asteroidday.storage_backends.StaticStorage'

EMAIL_ENABLED = str2bool(os.environ.get('EMAIL_ENABLED', 'False'))
if EMAIL_ENABLED:
    EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_USE_TLS       = True
    EMAIL_HOST          = 'smtp.gmail.com'
    EMAIL_HOST_USER     = os.environ.get('EMAIL_USERNAME','')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD','')
    EMAIL_PORT          =  587
    DEFAULT_FROM_EMAIL  = 'Asteroid Tracker <streams@lco.global>'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'filters': ['require_debug_false']
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        }
    },
    'loggers': {
            'django': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'asteroid': {
            'handlers':['console'],
            'level' : 'DEBUG'
        }
    }
}

if not CURRENT_PATH.startswith('/var/www'):
    try:
        from .local_settings import *
    except ImportError as e:
        if "local_settings" not in str(e):
            raise e

# settings.py


from pathlib import Path
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured

import dj_database_url, os


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(os.path.join(BASE_DIR, '.env'))


DEBUG = os.environ.get('DEBUG', 'False') == 'True'

def get_env_variable(var_name, required_in_prod=True):
    try:
        val = os.environ[var_name]
        if not val and required_in_prod and not DEBUG:
            raise ImproperlyConfigured(f"Set the {var_name} environment variable")
        return val
    except KeyError:
        if required_in_prod and not DEBUG:
            raise ImproperlyConfigured(f"Set the {var_name} environment variable")
        return None

SECRET_KEY = get_env_variable('SECRET_KEY')
if not SECRET_KEY:
    # Provide a dummy key for development if missing, so it doesn't crash in dev
    SECRET_KEY = 'django-insecure-dummy-key-for-dev-only'

HUB_SECRET_KEY = get_env_variable('HUB_SECRET_KEY')
KAHOOT_SECRET_KEY = get_env_variable('KAHOOT_SECRET_KEY', required_in_prod=False)
B2B_HOST_SECRET = get_env_variable('B2B_HOST_SECRET', required_in_prod=False)


ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',') if not DEBUG else ['*']


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'core'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'main.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'main.wsgi.application'


DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=60
    )
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

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOW_ALL_ORIGINS = False
    CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',')
    CORS_ALLOWED_ORIGINS = [origin for origin in CORS_ALLOWED_ORIGINS if origin]

# Security headers for production
if not DEBUG and os.environ.get('SECURE_SSL', 'True') == 'True':
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

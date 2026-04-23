"""
Saagu.farm Django Settings
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY — Change these in production
SECRET_KEY = 'django-insecure-CHANGE-ME-IN-PRODUCTION-saagu-farm-2026'
DEBUG = True
ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:8000', 'http://localhost:8000']

# --- Apps ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    # Project apps
    'accounts',
    'store',
]

# --- Custom User Model ---
AUTH_USER_MODEL = 'accounts.User'

# --- Middleware ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'saagu_farm.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'store.context_processors.cart_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'saagu_farm.wsgi.application'

# --- Database ---
# SQLite for development. Switch to PostgreSQL for production:
# pip install psycopg2-binary
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'saagu_farm',
        # 'USER': 'saagu_admin',
         'USER': "postgres",
        'PASSWORD': '12345',

        'HOST': 'localhost',
        'PORT': '5432',
    }
}


# --- Auth ---
AUTH_PASSWORD_VALIDATORS = []  # Relaxed for dev — tighten in production
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# --- OTP Settings ---
OTP_LENGTH = 6
OTP_EXPIRY_MINUTES = 5

# --- Static & Media ---
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# --- Misc ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# --- Firebase ---
FIREBASE_CREDENTIALS_PATH = BASE_DIR / 'saagu-farm-firebase-adminsdk-fbsvc-6282f7f62e.json'
FIREBASE_CONFIG = {
    'apiKey':            'AIzaSyDZviLw0cqCjUZrFrmzyjvyEdsxeL9hWNM',
    'authDomain':        'saagu-farm.firebaseapp.com',
    'projectId':         'saagu-farm',
    'storageBucket':     'saagu-farm.firebasestorage.app',
    'messagingSenderId': '410557441820',
    'appId':             '1:410557441820:web:83009ef6986cccf57c7cd9',
}

# --- Razorpay ---
RAZORPAY_KEY_ID     = 'rzp_test_REPLACE_ME'
RAZORPAY_KEY_SECRET = 'REPLACE_ME'

WHATSAPP_NUMBER = '919381172007'

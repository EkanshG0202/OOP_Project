from pathlib import Path
import os # Imported os to read environment variables if you choose to use them

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-YOUR-SECRET-KEY-HERE' # Replace with your own

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # --- ADDED: CORS Headers App ---
    'corsheaders',
    # -------------------------------

    # Our Apps
    'users',
    'store',
    'orders',

    # 3rd Party Apps
    'rest_framework',
    'rest_framework.authtoken', # For token authentication
    'django_filters',         # For search/filtering
    
    # Auth Apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'dj_rest_auth',
    'dj_rest_auth.registration',
]

MIDDLEWARE = [
    # --- ADDED: CORS Middleware (Must be at the top) ---
    'corsheaders.middleware.CorsMiddleware',
    # ---------------------------------------------------
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Allauth middleware
    "allauth.account.middleware.AccountMiddleware",
]

# --- ADDED: CORS Configuration ---
# Allows requests from your React frontend running on port 5173
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
# ---------------------------------

ROOT_URLCONF = 'livemart.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'livemart.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
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

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I1N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

# --- Add Media Root for Image Uploads ---
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# --- Additions for DRF and Auth ---

# 1. (THE FIX) Tell Django to use our custom User model
AUTH_USER_MODEL = 'users.User'

# 2. Tell DRF to use Token-based authentication
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        # By default, allow anyone to view (read-only)
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ]
}

# 3. Tell dj-rest-auth to use our new custom registration serializer
REST_AUTH = {
    'REGISTER_SERIALIZER': 'users.serializers.CustomRegisterSerializer',
}

# --- Allauth settings for Email Verification (as OTP) ---

# "mandatory" requires email verification to log in.
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'

# Users will be required to provide an email during registration
ACCOUNT_EMAIL_REQUIRED = True

# Allows users to log in using email
ACCOUNT_AUTHENTICATION_METHOD = 'email'

# Ensure username is still required for the database schema
ACCOUNT_USERNAME_REQUIRED = True

# Optional: Logs the user in immediately after they click the verification link
LOGIN_ON_EMAIL_CONFIRMATION = True

# Optional: Confirms the email just by clicking the link (no "Confirm" button)
ACCOUNT_CONFIRM_EMAIL_ON_GET = True

# --- FIX 2: Added Authentication Backends ---
# This allows allauth to intercept the login and authenticate via email
AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
]

# 5. Required by allauth
SITE_ID = 1

# =========================================================
# === SMTP EMAIL SETTINGS (For Sending Real Emails) ===
# =========================================================

# 1. Set the backend to SMTP
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# 2. Host settings (Example for Gmail)
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# 3. YOUR CREDENTIALS (REPLACE THESE!)
# Do NOT use your real login password. 
# Go to your Google Account -> Security -> 2-Step Verification -> App Passwords
# Create a new App Password and paste it below.
EMAIL_HOST_USER = 'ekanshgupta0202@gmail.com' 
EMAIL_HOST_PASSWORD = 'tcfvoncbaovxxauo'

# 4. Default Sender
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
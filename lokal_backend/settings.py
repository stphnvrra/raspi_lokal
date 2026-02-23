"""
Django settings for LoKal backend.
Optimized for Raspberry Pi 4B (4GB RAM) deployment.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-lokal-dev-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1,0.0.0.0').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'rest_framework',
    'corsheaders',
    # Local apps
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'lokal_backend.urls'

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

WSGI_APPLICATION = 'lokal_backend.wsgi.application'

# Database - SQLite optimized for Raspberry Pi
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 20,  # Increase timeout for SD card I/O
        }
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files (uploaded audio, TTS output)
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # Allow anonymous for register/login
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',  # For file uploads
        'rest_framework.parsers.FormParser',
    ],
}

# CORS settings - allow frontend to send cookies
CORS_ALLOW_ALL_ORIGINS = True  # Since this runs locally on the Pi
CORS_ALLOW_CREDENTIALS = True  # Allow cookies for session auth

# CSRF settings for session auth with separate frontend
CSRF_TRUSTED_ORIGINS = ['http://localhost:8000', 'http://127.0.0.1:8000']
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SAMESITE = 'Lax'

# ========================
# LoKal-specific settings
# ========================

# Ollama configuration for Raspberry Pi 4B (4GB RAM)
# 
# RECOMMENDED FOR STABILITY (4GB RAM):
#   - tinyllama     (~637MB)  - MOST STABLE, best for demos/presentations
#   - qwen2.5:0.5b  (~400MB)  - Very stable, smaller model
#
# OPTIONAL (if you have more headroom):
#   - llama3.2:1b   (~1.3GB)  - Better quality, still fits
#   - gemma:2b      (~1.4GB)  - Good balance, monitor RAM
#
# NOT RECOMMENDED FOR 4GB (will crash with Django+TTS+STT):
#   - phi3:mini     (~2.3GB)  - Too large, causes memory pressure
#   - Any 7B+ model           - Requires 8GB+ RAM
#
OLLAMA_HOST = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'qwen2.5:0.5b')  # Optimized for 4GB RAM stability
OLLAMA_TIMEOUT = int(os.environ.get('OLLAMA_TIMEOUT', '120'))  # Longer timeout for Pi

# Educational system prompt for the AI
LOKAL_SYSTEM_PROMPT = """You are LoKal, a helpful educational assistant for students in remote areas.

Your role:
- Explain Math, Science, English, and other basic subjects
- Use clear, simple language suitable for young learners
- Be patient and encouraging
- Provide step-by-step explanations when needed
- Keep answers concise but thorough
- If you don't know something, be honest about it

Remember: You are helping students who may have limited access to educational resources.
Always be supportive and make learning enjoyable."""

# Text-to-Speech settings
TTS_RATE = int(os.environ.get('TTS_RATE', '150'))  # Words per minute
TTS_VOLUME = float(os.environ.get('TTS_VOLUME', '1.0'))  # 0.0 to 1.0

# Speech-to-Text settings
VOSK_MODEL_PATH = os.environ.get('VOSK_MODEL_PATH', str(BASE_DIR / 'models' / 'vosk-model-small-en-us-0.15'))

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'lokal.log',
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'api': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Create required directories
for directory in [MEDIA_ROOT, BASE_DIR / 'logs', BASE_DIR / 'models']:
    directory.mkdir(parents=True, exist_ok=True)

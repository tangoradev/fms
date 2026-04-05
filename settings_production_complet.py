import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-8^h5o^1*)0d5u$j!2_65d%qq(t6in^f#9h@abj#5e474*t0)y%'

DEBUG = False

ALLOWED_HOSTS = ['127.0.0.1', '10.20.160.77', 'localhost', 'fms.undpciv.org', 'www.fms.undpciv.org']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # apps personnalisées
    'core',
    # extensions
    'crispy_forms',
    'crispy_bootstrap5',
    'widget_tweaks',
    # autres apps utiles
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # pour servir les fichiers statiques en prod
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'fms.urls'

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
                'django.template.context_processors.media',  # Ajouté pour les médias
                'core.context_processors.media_variables',  # Context processor personnalisé
            ],
        },
    },
]

WSGI_APPLICATION = 'fms.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'c2501100c_fms',
        'USER': 'c2501100c_fms',
        'PASSWORD': 'IVCpnud2016',
        'HOST': 'localhost',
        'PORT': '3306',
        'CONN_MAX_AGE': 60,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Abidjan'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuration du modèle utilisateur personnalisé
AUTH_USER_MODEL = 'core.Utilisateur'

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.undpciv.org'
EMAIL_PORT = 465
EMAIL_HOST_USER = 'fms@undpciv.org'
EMAIL_HOST_PASSWORD = 'Pnud2016'
EMAIL_USE_SSL = True
DEFAULT_FROM_EMAIL = 'fms@undpciv.org'

# Sécurité supplémentaire en prod
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# ============================================================
# CORRECTION CSRF - OBLIGATOIRE POUR DJANGO 4.x
# ============================================================
# Configuration CSRF pour la production
CSRF_TRUSTED_ORIGINS = [
    'http://fms.undpciv.org',
    'https://fms.undpciv.org',
    'http://www.fms.undpciv.org',
    'https://www.fms.undpciv.org',
]

# Configuration supplémentaire des cookies CSRF
CSRF_COOKIE_HTTPONLY = False  # Permet à JavaScript d'accéder au token si nécessaire
CSRF_COOKIE_SAMESITE = 'Lax'  # Protection contre les attaques CSRF cross-site

# Configuration de l'authentification
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# URL de base pour les liens dans les emails
BASE_URL = 'https://fms.undpciv.org'

# Configuration du système de journalisation
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'debug.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'core': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}

# Pour WhiteNoise (servir les fichiers statiques)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

import os
import django_heroku
from decouple import config
import dj_database_url


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ALLOWED_HOSTS = ['https://gastrodichtung.ch', 'https://127.0.0.1:8000/', 'https://bonetta.herokuapp.com']


if config('STAGE') == 'dev':
    #start

    DEBUG = True

    CSRF_COOKIE_SECURE = False
    SECURE_SSL_REDIRECT = False

    DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
                'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
            }
        }
    EMAIL_MASTER = ["sandro@sh-digital.ch"]

    #end

else:
    #start

    DEBUG = False

    #take out for dev
    CSRF_COOKIE_SECURE = True
    CSRF_TRUSTED_ORIGINS = ['https://gastrodichtung.ch', 'https://bonetta.herokuapp.com', 'https://127.0.0.1:8000/']
    CSRF_COOKIE_DOMAIN = '.gastrodichtung.ch'
    SECURE_SSL_REDIRECT = True
    #end

    DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': 'd7ibnto16o82nt',
            }
        }

    db_from_env = dj_database_url.config(conn_max_age=600, ssl_require=True)
    DATABASES['default'].update(db_from_env)

    EMAIL_MASTER = ["sandro@sh-digital.ch", "livio.bonetta@geboshop.ch"]

    #end



SECRET_KEY = config('SECRET_KEY')


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'store',
    'django_extensions',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'crispy_forms',
    'django_countries',
    'storages',
    'mathfilters',
    'django_template_maths',
    'store.templatetags.custom_filters',
    'django_brotli',
    
]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_brotli.middleware.BrotliMiddleware',

]

ROOT_URLCONF = 'webshop.urls'

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
                'store.context_processors.extras', #for category display every
                'store.context_processors.sub_extras', #for category display every
                'store.context_processors.extras_marke', #for marke display every
                'store.context_processors.first_cat',
            ],
        },
    },
]

WSGI_APPLICATION = 'webshop.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'de-ch'

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_L10N = False

USE_TZ = True

DATE_INPUT_FORMATS = ['%d-%m-%Y']



SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')



STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

MEDIA_URL = '/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'static/images')


# upload images
CKEDITOR_UPLOAD_PATH = "upload/"


# sending emails
EMAIL_HOST = 'asmtp.mail.hostpoint.ch'  # Hostpoint SMTP server
EMAIL_PORT = 465  # SSL encrypted connection on port 465
EMAIL_HOST_USER = config('EMAIL_HOST_USER')  # Your email address (e.g., 'your.email@domain.ch')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')  # The password for the email account
EMAIL_USE_TLS = False  # Disable TLS because we are using SSL
EMAIL_USE_SSL = True  # Enable SSL for port 465 (encrypted connection)
DEFAULT_FROM_EMAIL = "bestellungen@gastrodichtung.ch"  # Default sender email

#Aws storage
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME')

AWS_S3_FILE_OVERWRITE  = False
AWS_DEFAULT_ACL = None
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# Auth
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend'
)

# Payrexx
INSTANCE_API_SECRET = config('INSTANCE_API_SECRET')
INSTANCE_NAME = config('INSTANCE_NAME')
PAYMENT_URL_OPEN = config('PAYMENT_URL_OPEN')
PAYMENT_SUCCESS_URL = config('PAYMENT_SUCCESS_URL')
PAYMENT_DECLINE_URL = config('PAYMENT_DECLINE_URL')


LOGIN_REDIRECT_URL = '/mydichtungen'
LOGOUT_REDIRECT_URL = '/'
REGISTER_REDIRECT_URL = '/'


CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Country Field
COUNTRIES_ONLY = [
    'CH',
    'DE',
    'AT',
]

COUNTRIES_OVERRIDE = {
    'CH': 'Schweiz',
    'DE': 'Deutschland',
    'AT': 'Österreich',
}

ACCOUNT_FORMS = {
    'signup' : 'store.forms.RegistrationForm'
}

django_heroku.settings(locals())



STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key-for-development")

# DEBUG должен быть False в production. Управляем через переменную окружения.
DEBUG = os.getenv("DEBUG", "False") == "True"

# Specify domain names or IP addresses from which requests are allowed
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'django_ckeditor_5',
    
    # My apps
    'apps.users',
    'apps.theory',
    'apps.quiz',
    'apps.calculator',
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

ROOT_URLCONF = 'core.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
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
STATICFILES_DIRS = [BASE_DIR / "static"]

# Directory where the `collectstatic` command will collect ALL static files.
# Nginx will serve files from this folder.
STATIC_ROOT = BASE_DIR / "staticfiles"


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'users.User'

# Authentication backends
AUTHENTICATION_BACKENDS = [
    'apps.users.backends.EmailOrUsernameModelBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# URL for redirection if the user is not authenticated
LOGIN_URL = 'users:login'

# Media files (User uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# CKEditor 5 Configuration
customColorPalette = [
    {
        'color': 'hsl(4, 90%, 58%)',
        'label': 'Red'
    },
    {
        'color': 'hsl(340, 82%, 52%)',
        'label': 'Pink'
    },
    {
        'color': 'hsl(291, 64%, 42%)',
        'label': 'Purple'
    },
    {
        'color': 'hsl(262, 52%, 47%)',
        'label': 'Deep Purple'
    },
    {
        'color': 'hsl(231, 48%, 48%)',
        'label': 'Indigo'
    },
    {
        'color': 'hsl(207, 90%, 54%)',
        'label': 'Blue'
    },
]

CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': ['heading', '|', 'bold', 'italic', 'link',
                    'bulletedList', 'numberedList', 'blockQuote', 'imageUpload', ],
    },
    'theory_editor': {
        'toolbar': [
            'heading', '|', 'bold', 'italic', 'underline', 'strikethrough',
            'subscript', 'superscript', '|', 'link', 'imageUpload', 
            'blockQuote', 'codeBlock', '|', 'bulletedList', 'numberedList', 
            'todoList', '|', 'outdent', 'indent', '|', 'insertTable', 
            'tableColumn', 'tableRow', 'mergeTableCells', '|', 'alignment', '|', 'undo', 'redo'
        ],
        'image': {
            'toolbar': [
                'imageTextAlternative', '|', 
                'imageStyle:alignLeft', 'imageStyle:alignRight', 'imageStyle:alignCenter',
                'imageStyle:side', 'imageStyle:inline'
            ],
            'styles': [
                'alignLeft', 'alignRight', 'alignCenter', 'side', 'inline'
            ]
        },
        'table': {
            'contentToolbar': [ 
                'tableColumn', 'tableRow', 'mergeTableCells',
                'tableProperties', 'tableCellProperties' 
            ],
            'tableProperties': {
                'borderColors': [],
                'backgroundColors': []
            }
        },
        'alignment': {
            'options': [ 'left', 'center', 'right', 'justify' ]
        },
        'heading' : {
            'options': [
                { 'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph' },
                { 'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1' },
                { 'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2' },
                { 'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3' }
            ]
        }
    }
}

CKEDITOR_5_UPLOAD_PATH = "uploads/"

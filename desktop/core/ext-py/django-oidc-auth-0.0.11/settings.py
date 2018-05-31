import django
import logging
django_version = django.get_version()

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'sqlite.db'
    }
}

# Local time zone for this installation. Choices can be found here:
# http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
# although not all variations may be possible on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

STATIC_URL = '/static/'

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '34958734985734985734985798437'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.messages',
    'django.contrib.admin',
    'django_nose',
    'oidc_auth',
)

TESTABLE_APPS = (
    'oidc_auth',
)

SKIP_TESTS = (
    'south',
)

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

SOUTH_TESTS_MIGRATE = False

AUTHENTICATION_BACKENDS = (
    'oidc_auth.auth.OpenIDConnectBackend',
    'django.contrib.auth.backends.ModelBackend',
)

LOGIN_URL = '/oidc/login/'

OIDC_AUTH = {
    'DEFAULT_PROVIDER': {
        'issuer': 'http://localhost:8000/',
        'authorization_endpoint': 'http://localhost:8000/o/authorize/',
        'token_endpoint': 'http://localhost:8000/o/token/',
        'userinfo_endpoint': 'http://localhost:8000/o/userinfo/',
        'client_id': 'abcdef',
        'client_secret': '123456'
    }
}


oidc_auth_log = logging.getLogger('oidc_auth')
oidc_auth_log.setLevel(logging.DEBUG)
# oidc_auth_log.addHandler(logging.StreamHandler())

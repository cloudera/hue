from __future__ import absolute_import, division, print_function, unicode_literals


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

ALLOWED_HOSTS = []

TIME_ZONE = 'UTC'
LANGUAGE_CODE = 'en-us'
USE_I18N = False
USE_L10N = False
USE_TZ = True

SECRET_KEY = 'nt56v8)moa)37ta5z7dd=if-@y#k@l7+t8lct*c8m730lpd=so'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',

    'tests',
)

MIDDLEWARE_CLASSES = []

AUTH_USER_MODEL = 'auth.User'

AUTHENTICATION_BACKENDS = [
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
]

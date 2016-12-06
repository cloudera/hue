#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Django settings for Hue.
#
# Local customizations are done by symlinking a file
# as local_settings.py.

import logging
import os
import pkg_resources
import sys

from guppy import hpy

from django.utils.translation import ugettext_lazy as _

import desktop.redaction
from desktop.lib.paths import get_desktop_root
from desktop.lib.python_util import force_dict_to_strings

from aws.conf import is_enabled as is_s3_enabled


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', '..', '..'))


HUE_DESKTOP_VERSION = pkg_resources.get_distribution("desktop").version or "Unknown"
NICE_NAME = "Hue"

ENV_HUE_PROCESS_NAME = "HUE_PROCESS_NAME"
ENV_DESKTOP_DEBUG = "DESKTOP_DEBUG"


############################################################
# Part 1: Logging and imports.
############################################################

# Configure debug mode
DEBUG = True
TEMPLATE_DEBUG = DEBUG

# Start basic logging as soon as possible.
if ENV_HUE_PROCESS_NAME not in os.environ:
  _proc = os.path.basename(len(sys.argv) > 1 and sys.argv[1] or sys.argv[0])
  os.environ[ENV_HUE_PROCESS_NAME] = _proc

desktop.log.basic_logging(os.environ[ENV_HUE_PROCESS_NAME])

logging.info("Welcome to Hue " + HUE_DESKTOP_VERSION)

# Then we can safely import some more stuff
from desktop import appmanager
from desktop.lib import conf

# Add fancy logging
desktop.log.fancy_logging()


############################################################
# Part 2: Generic Configuration
############################################################

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

LANGUAGES = [
  ('de', _('German')),
  ('en-us', _('English')),
  ('es', _('Spanish')),
  ('fr', _('French')),
  ('ja', _('Japanese')),
  ('ko', _('Korean')),
  ('pt', _('Portuguese')),
  ('pt_BR', _('Brazilian Portuguese')),
  ('zh_CN', _('Simplified Chinese')),
]

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''


############################################################
# Part 3: Django configuration
############################################################

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'desktop', 'libs', 'indexer', 'src', 'indexer', 'static'),
    os.path.join(BASE_DIR, 'desktop', 'libs', 'notebook', 'src', 'notebook', 'static'),
    os.path.join(BASE_DIR, 'desktop', 'libs', 'liboauth', 'src', 'liboauth', 'static'),
)

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.CachedStaticFilesStorage'

# For Django admin interface
STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'build', 'static')

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
  'django.template.loaders.filesystem.Loader',
  'django.template.loaders.app_directories.Loader'
)

MIDDLEWARE_CLASSES = [
    # The order matters
    'desktop.middleware.MetricsMiddleware',
    'desktop.middleware.EnsureSafeMethodMiddleware',
    'desktop.middleware.AuditLoggingMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'desktop.middleware.SpnegoMiddleware',
    'desktop.middleware.HueRemoteUserMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'babeldjango.middleware.LocaleMiddleware',
    'desktop.middleware.AjaxMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'desktop.middleware.ContentSecurityPolicyMiddleware',
    # Must be after Session, Auth, and Ajax. Before everything else.
    'desktop.middleware.LoginAndPermissionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'desktop.middleware.NotificationMiddleware',
    'desktop.middleware.ExceptionMiddleware',
    'desktop.middleware.ClusterMiddleware',
    # 'debug_toolbar.middleware.DebugToolbarMiddleware'
    'django.middleware.csrf.CsrfViewMiddleware',

    'django.middleware.http.ConditionalGetMiddleware',
    'axes.middleware.FailedLoginMiddleware',
]

# if os.environ.get(ENV_DESKTOP_DEBUG):
#   MIDDLEWARE_CLASSES.append('desktop.middleware.HtmlValidationMiddleware')
#   logging.debug("Will try to validate generated HTML.")

ROOT_URLCONF = 'desktop.urls'

# Hue runs its own wsgi applications
WSGI_APPLICATION = None

TEMPLATE_DIRS = (
    get_desktop_root("core/templates"),
)

INSTALLED_APPS = [
    'django.contrib.auth',
    'django_openid_auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',

    'django.contrib.admin',
    'django_extensions',

    # 'debug_toolbar',
    'south', # database migration tool

    # i18n support
    'babeldjango',

    # Desktop injects all the other installed apps into here magically.
    'desktop',

    # App that keeps track of failed logins.
    'axes',
]

LOCALE_PATHS = [
  get_desktop_root('core/src/desktop/locale')
]

# Keep default values up to date
TEMPLATE_CONTEXT_PROCESSORS = (
  'django.contrib.auth.context_processors.auth',
  'django.core.context_processors.debug',
  'django.core.context_processors.i18n',
  'django.core.context_processors.media',
  'django.core.context_processors.request',
  'django.contrib.messages.context_processors.messages',
   # Not default
  'desktop.context_processors.app_name',
)


# Desktop doesn't use an auth profile module, because
# because it doesn't mesh very well with the notion
# of having multiple apps.  If your app needs
# to store data related to users, it should
# manage its own table with an appropriate foreign key.
AUTH_PROFILE_MODULE = None

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/" # For djangosaml2 bug.

PYLINTRC = get_desktop_root('.pylintrc')

# Custom CSRF Failure View
CSRF_FAILURE_VIEW = 'desktop.views.csrf_failure'

############################################################
# Part 4: Installation of apps
############################################################

_config_dir = os.getenv("HUE_CONF_DIR", get_desktop_root("conf"))

# Libraries are loaded and configured before the apps
appmanager.load_libs()
_lib_conf_modules = [dict(module=app.conf, config_key=None) for app in appmanager.DESKTOP_LIBS if app.conf is not None]
LOCALE_PATHS.extend([app.locale_path for app in appmanager.DESKTOP_LIBS])

# Load desktop config
_desktop_conf_modules = [dict(module=desktop.conf, config_key=None)]
conf.initialize(_desktop_conf_modules, _config_dir)

# Register the redaction filters into the root logger as soon as possible.
desktop.redaction.register_log_filtering(desktop.conf.get_redaction_policy())


# Activate l10n
# Install apps
appmanager.load_apps(desktop.conf.APP_BLACKLIST.get())
for app in appmanager.DESKTOP_APPS:
  INSTALLED_APPS.extend(app.django_apps)
  LOCALE_PATHS.append(app.locale_path)


logging.debug("Installed Django modules: %s" % ",".join(map(str, appmanager.DESKTOP_MODULES)))

# Load app configuration
_app_conf_modules = [dict(module=app.conf, config_key=app.config_key) for app in appmanager.DESKTOP_APPS if app.conf is not None]

conf.initialize(_lib_conf_modules, _config_dir)
conf.initialize(_app_conf_modules, _config_dir)

# Now that we've loaded the desktop conf, set the django DEBUG mode based on the conf.
DEBUG = desktop.conf.DJANGO_DEBUG_MODE.get()
TEMPLATE_DEBUG = DEBUG
if DEBUG: # For simplification, force all DEBUG when django_debug_mode is True and re-apply the loggers
  os.environ[ENV_DESKTOP_DEBUG] = 'True'
  desktop.log.basic_logging(os.environ[ENV_HUE_PROCESS_NAME])
  desktop.log.fancy_logging()

############################################################
# Part 4a: Django configuration that requires bound Desktop
# configs.
############################################################

# Configure allowed hosts
ALLOWED_HOSTS = desktop.conf.ALLOWED_HOSTS.get()

X_FRAME_OPTIONS = desktop.conf.X_FRAME_OPTIONS.get()

# Configure hue admins
ADMINS = []
for admin in desktop.conf.DJANGO_ADMINS.get():
  admin_conf = desktop.conf.DJANGO_ADMINS[admin]
  if 'name' in admin_conf.bind_to and 'email' in admin_conf.bind_to:
    ADMINS.append(((admin_conf.NAME.get(), admin_conf.EMAIL.get())))
ADMINS = tuple(ADMINS)
MANAGERS = ADMINS

# Server Email Address
SERVER_EMAIL = desktop.conf.DJANGO_SERVER_EMAIL.get()

# Email backend
EMAIL_BACKEND = desktop.conf.DJANGO_EMAIL_BACKEND.get()

# Configure database
if os.getenv('DESKTOP_DB_CONFIG'):
  conn_string = os.getenv('DESKTOP_DB_CONFIG')
  logging.debug("DESKTOP_DB_CONFIG SET: %s" % (conn_string))
  default_db = dict(zip(
    ["ENGINE", "NAME", "TEST_NAME", "USER", "PASSWORD", "HOST", "PORT"],
    conn_string.split(':')))
  default_db['NAME'] = default_db['NAME'].replace('#', ':') # For is_db_alive command
else:
  test_name = os.environ.get('DESKTOP_DB_TEST_NAME', get_desktop_root('desktop-test.db'))
  logging.debug("DESKTOP_DB_TEST_NAME SET: %s" % test_name)

  test_user = os.environ.get('DESKTOP_DB_TEST_USER', 'hue_test')
  logging.debug("DESKTOP_DB_TEST_USER SET: %s" % test_user)

  default_db = {
    "ENGINE" : desktop.conf.DATABASE.ENGINE.get(),
    "NAME" : desktop.conf.DATABASE.NAME.get(),
    "USER" : desktop.conf.DATABASE.USER.get(),
    "PASSWORD" : desktop.conf.get_database_password(),
    "HOST" : desktop.conf.DATABASE.HOST.get(),
    "PORT" : str(desktop.conf.DATABASE.PORT.get()),
    "OPTIONS": force_dict_to_strings(desktop.conf.DATABASE.OPTIONS.get()),
    # DB used for tests
    "TEST_NAME" : test_name,
    "TEST_USER" : test_user,
    # Wrap each request in a transaction.
    "ATOMIC_REQUESTS" : True,
  }

DATABASES = {
  'default': default_db
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-hue'
    }
}

# Configure sessions
SESSION_COOKIE_AGE = desktop.conf.SESSION.TTL.get()
SESSION_COOKIE_SECURE = desktop.conf.SESSION.SECURE.get()
SESSION_EXPIRE_AT_BROWSER_CLOSE = desktop.conf.SESSION.EXPIRE_AT_BROWSER_CLOSE.get()

# HTTP only
SESSION_COOKIE_HTTPONLY = desktop.conf.SESSION.HTTP_ONLY.get()

CSRF_COOKIE_SECURE = desktop.conf.SESSION.SECURE.get()
CSRF_COOKIE_HTTPONLY = desktop.conf.SESSION.HTTP_ONLY.get()
CSRF_COOKIE_NAME='csrftoken'

SECURE_HSTS_SECONDS = desktop.conf.SECURE_HSTS_SECONDS.get()
SECURE_HSTS_INCLUDE_SUBDOMAINS = desktop.conf.SECURE_HSTS_INCLUDE_SUBDOMAINS.get()
SECURE_CONTENT_TYPE_NOSNIFF = desktop.conf.SECURE_CONTENT_TYPE_NOSNIFF.get()
SECURE_BROWSER_XSS_FILTER = desktop.conf.SECURE_BROWSER_XSS_FILTER.get()
SECURE_SSL_REDIRECT = desktop.conf.SECURE_SSL_REDIRECT.get()
SECURE_SSL_HOST = desktop.conf.SECURE_SSL_HOST.get()
SECURE_REDIRECT_EXEMPT = desktop.conf.SECURE_REDIRECT_EXEMPT.get()

# django-nose test specifics
TEST_RUNNER = 'desktop.lib.test_runners.HueTestRunner'
# Turn off cache middleware
if 'test' in sys.argv:
  CACHE_MIDDLEWARE_SECONDS = 0

# Limit Nose coverage to Hue apps
NOSE_ARGS = [
  '--cover-package=%s' % ','.join([app.name for app in appmanager.DESKTOP_APPS + appmanager.DESKTOP_LIBS]),
  '--no-path-adjustment',
  '--traverse-namespace'
]

TIME_ZONE = desktop.conf.TIME_ZONE.get()

if desktop.conf.DEMO_ENABLED.get():
  AUTHENTICATION_BACKENDS = ('desktop.auth.backend.DemoBackend',)
else:
  AUTHENTICATION_BACKENDS = tuple(desktop.conf.AUTH.BACKEND.get())

EMAIL_HOST = desktop.conf.SMTP.HOST.get()
EMAIL_PORT = desktop.conf.SMTP.PORT.get()
EMAIL_HOST_USER = desktop.conf.SMTP.USER.get()
EMAIL_HOST_PASSWORD = desktop.conf.get_smtp_password()
EMAIL_USE_TLS = desktop.conf.SMTP.USE_TLS.get()
DEFAULT_FROM_EMAIL = desktop.conf.SMTP.DEFAULT_FROM.get()

# Used for securely creating sessions. Should be unique and not shared with anybody. Changing auth backends will invalidate all open sessions.
SECRET_KEY = desktop.conf.get_secret_key()
if SECRET_KEY:
  SECRET_KEY += str(AUTHENTICATION_BACKENDS)
else:
  import uuid
  SECRET_KEY = str(uuid.uuid4())

# Axes
AXES_LOGIN_FAILURE_LIMIT = desktop.conf.AUTH.LOGIN_FAILURE_LIMIT.get()
AXES_LOCK_OUT_AT_FAILURE = desktop.conf.AUTH.LOGIN_LOCK_OUT_AT_FAILURE.get()
AXES_COOLOFF_TIME = desktop.conf.AUTH.LOGIN_COOLOFF_TIME.get()
AXES_USE_USER_AGENT = desktop.conf.AUTH.LOGIN_LOCK_OUT_USE_USER_AGENT.get()
AXES_LOCK_OUT_BY_COMBINATION_USER_AND_IP = desktop.conf.AUTH.LOGIN_LOCK_OUT_BY_COMBINATION_USER_AND_IP.get()
AXES_BEHIND_REVERSE_PROXY = desktop.conf.AUTH.BEHIND_REVERSE_PROXY.get()
AXES_REVERSE_PROXY_HEADER = desktop.conf.AUTH.REVERSE_PROXY_HEADER.get()

# SAML
SAML_AUTHENTICATION = 'libsaml.backend.SAML2Backend' in AUTHENTICATION_BACKENDS
if SAML_AUTHENTICATION:
  from libsaml.saml_settings import *
  INSTALLED_APPS.append('libsaml')
  LOGIN_URL = '/saml2/login/'
  SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Middleware classes.
for middleware in desktop.conf.MIDDLEWARE.get():
  MIDDLEWARE_CLASSES.append(middleware)

# OpenId
OPENID_AUTHENTICATION = 'libopenid.backend.OpenIDBackend' in AUTHENTICATION_BACKENDS
if OPENID_AUTHENTICATION:
  from libopenid.openid_settings import *
  INSTALLED_APPS.append('libopenid')
  LOGIN_URL = '/openid/login'
  SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# OAuth
OAUTH_AUTHENTICATION='liboauth.backend.OAuthBackend' in AUTHENTICATION_BACKENDS
if OAUTH_AUTHENTICATION:
    INSTALLED_APPS.append('liboauth')
    LOGIN_URL = '/oauth/accounts/login'
    SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# URL Redirection white list.
if desktop.conf.REDIRECT_WHITELIST.get():
  MIDDLEWARE_CLASSES.append('desktop.middleware.EnsureSafeRedirectURLMiddleware')

# Enable X-Forwarded-Host header if the load balancer requires it
USE_X_FORWARDED_HOST = desktop.conf.USE_X_FORWARDED_HOST.get()

# Support HTTPS load-balancing
if desktop.conf.SECURE_PROXY_SSL_HEADER.get():
  SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Add last activity tracking and idle session timeout
if 'useradmin' in [app.name for app in appmanager.DESKTOP_APPS]:
  MIDDLEWARE_CLASSES.append('useradmin.middleware.LastActivityMiddleware')

################################################################
# Register file upload handlers
# This section must go after the desktop lib modules are loaded
################################################################

# Insert our custom upload handlers
file_upload_handlers = [
    'hadoop.fs.upload.HDFSfileUploadHandler',
    'django.core.files.uploadhandler.MemoryFileUploadHandler',
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
]

if is_s3_enabled():
  file_upload_handlers.insert(0, 'aws.s3.upload.S3FileUploadHandler')

FILE_UPLOAD_HANDLERS = tuple(file_upload_handlers)

############################################################

# Necessary for South to not fuzz with tests.  Fixed in South 0.7.1
SKIP_SOUTH_TESTS = True

# Set up environment variable so Kerberos libraries look at our private
# ticket cache
os.environ['KRB5CCNAME'] = desktop.conf.KERBEROS.CCACHE_PATH.get()
if not os.getenv('SERVER_SOFTWARE'):
  os.environ['SERVER_SOFTWARE'] = 'apache'

# If Hue is configured to use a CACERTS truststore, make sure that the
# REQUESTS_CA_BUNDLE is set so that we can use it when we make external requests.
# This is for the REST calls made by Hue with the requests library.
if desktop.conf.SSL_CACERTS.get() and os.environ.get('REQUESTS_CA_BUNDLE') is None:
  os.environ['REQUESTS_CA_BUNDLE'] = desktop.conf.SSL_CACERTS.get()

# Preventing local build failure by not validating the default value of REQUESTS_CA_BUNDLE
if os.environ.get('REQUESTS_CA_BUNDLE') and os.environ.get('REQUESTS_CA_BUNDLE') != desktop.conf.SSL_CACERTS.config.default and not os.path.isfile(os.environ['REQUESTS_CA_BUNDLE']):
  raise Exception(_('SSL Certificate pointed by REQUESTS_CA_BUNDLE does not exist: %s') % os.environ['REQUESTS_CA_BUNDLE'])

# Memory
if desktop.conf.MEMORY_PROFILER.get():
  MEMORY_PROFILER = hpy()
  MEMORY_PROFILER.setrelheap()


if not desktop.conf.DATABASE_LOGGING.get():
  def disable_database_logging():
    from django.db.backends import BaseDatabaseWrapper
    from django.db.backends.util import CursorWrapper

    BaseDatabaseWrapper.make_debug_cursor = lambda self, cursor: CursorWrapper(cursor, self)

  disable_database_logging()

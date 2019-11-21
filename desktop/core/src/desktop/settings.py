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

from builtins import map, zip
import datetime
import gc
import json
import logging
import os
import pkg_resources
import sys
import uuid

import django_opentracing

from django.utils.translation import ugettext_lazy as _

import desktop.redaction

from desktop.conf import has_channels
from desktop.lib.paths import get_desktop_root, get_run_root
from desktop.lib.python_util import force_dict_to_strings

from aws.conf import is_enabled as is_s3_enabled
from azure.conf import is_abfs_enabled


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', '..', '..'))

HUE_DESKTOP_VERSION = pkg_resources.get_distribution("desktop").version or "Unknown"
NICE_NAME = "Hue"

ENV_HUE_PROCESS_NAME = "HUE_PROCESS_NAME"
ENV_DESKTOP_DEBUG = "DESKTOP_DEBUG"
LOGGING_CONFIG = None # We're handling our own logging config. Consider upgrading our logging infra to LOGGING_CONFIG


############################################################
# Part 1: Logging and imports.
############################################################

# Configure debug mode
DEBUG = True
GTEMPLATE_DEBUG = DEBUG

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
  ('zh-CN', _('Simplified Chinese')),
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
GTEMPLATE_LOADERS = (
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
    'desktop.middleware.ProxyMiddleware',
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
    'django.middleware.csrf.CsrfViewMiddleware',

    'django.middleware.http.ConditionalGetMiddleware',
    #@TODO@ Prakash to check FailedLoginMiddleware working or not?
    #'axes.middleware.FailedLoginMiddleware',
    'desktop.middleware.MimeTypeJSFileFixStreamingMiddleware',
    'crequest.middleware.CrequestMiddleware',
]

# if os.environ.get(ENV_DESKTOP_DEBUG):
#   MIDDLEWARE_CLASSES.append('desktop.middleware.HtmlValidationMiddleware')
#   logging.debug("Will try to validate generated HTML.")

ROOT_URLCONF = 'desktop.urls'

# Hue runs its own wsgi applications
WSGI_APPLICATION = None

GTEMPLATE_DIRS = (
    get_desktop_root("core/templates"),
)

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',

    'django.contrib.admin',
    'django_extensions',

    # 'debug_toolbar',
    #'south', # database migration tool

    # i18n support
    'babeldjango',

    # Desktop injects all the other installed apps into here magically.
    'desktop',

    # App that keeps track of failed logins.
    'axes',
    'webpack_loader',
    'django_prometheus',
    'crequest',
    #'django_celery_results',
]

WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'desktop/js/bundles/hue/',
        'STATS_FILE': os.path.join(BASE_DIR, 'webpack-stats.json')
    },
    'WORKERS': {
        'BUNDLE_DIR_NAME': 'desktop/js/bundles/workers/',
        'STATS_FILE': os.path.join(BASE_DIR, 'webpack-stats-workers.json')
    },
    'LOGIN': {
        'BUNDLE_DIR_NAME': 'desktop/js/bundles/login/',
        'STATS_FILE': os.path.join(BASE_DIR, 'webpack-stats-login.json')
    }
}

LOCALE_PATHS = [
  get_desktop_root('core/src/desktop/locale')
]

# Keep default values up to date
GTEMPLATE_CONTEXT_PROCESSORS = (
  'django.contrib.auth.context_processors.auth',
  'django.template.context_processors.debug',
  'django.template.context_processors.i18n',
  'django.template.context_processors.media',
  'django.template.context_processors.request',
  'django.contrib.messages.context_processors.messages',
   # Not default
  'desktop.context_processors.app_name',
)

TEMPLATES = [
  {
    'BACKEND': 'djangomako.backends.MakoBackend',
    'DIRS': GTEMPLATE_DIRS,
    'NAME': 'mako',
    'OPTIONS': {
      'context_processors': GTEMPLATE_CONTEXT_PROCESSORS,
      'loaders': GTEMPLATE_LOADERS,
    },
  },
  {
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [
      get_desktop_root("core/templates/debug_toolbar"),
      get_desktop_root("core/templates/djangosaml2"),
    ],
    'NAME': 'django',
    'APP_DIRS': True,
  },
]

# Desktop doesn't use an auth profile module, because
# because it doesn't mesh very well with the notion
# of having multiple apps.  If your app needs
# to store data related to users, it should
# manage its own table with an appropriate foreign key.
AUTH_PROFILE_MODULE = None

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/" # For djangosaml2 bug.

PYLINTRC = get_run_root('.pylintrc')

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
GTEMPLATE_DEBUG = DEBUG
if DEBUG: # For simplification, force all DEBUG when django_debug_mode is True and re-apply the loggers
  os.environ[ENV_DESKTOP_DEBUG] = 'True'
  desktop.log.basic_logging(os.environ[ENV_HUE_PROCESS_NAME])
  desktop.log.fancy_logging()

############################################################
# Part 4a: Django configuration that requires bound Desktop
# configs.
############################################################

if desktop.conf.ENABLE_ORGANIZATIONS.get():
  AUTH_USER_MODEL = 'useradmin.OrganizationUser'
  MIGRATION_MODULES = {
    'beeswax': 'beeswax.org_migrations',
    'useradmin': 'useradmin.org_migrations',
    'desktop': 'desktop.org_migrations',
  }

# Configure allowed hosts
ALLOWED_HOSTS = desktop.conf.ALLOWED_HOSTS.get()

X_FRAME_OPTIONS = desktop.conf.X_FRAME_OPTIONS.get()

# Configure admins
ADMINS = []
for admin in desktop.conf.DJANGO_ADMINS.get():
  admin_conf = desktop.conf.DJANGO_ADMINS[admin]
  if 'name' in admin_conf.bind_to and 'email' in admin_conf.bind_to:
    ADMINS.append(((admin_conf.NAME.get(), admin_conf.EMAIL.get())))
ADMINS = tuple(ADMINS)
MANAGERS = ADMINS

SERVER_EMAIL = desktop.conf.DJANGO_SERVER_EMAIL.get()
EMAIL_BACKEND = desktop.conf.DJANGO_EMAIL_BACKEND.get()
EMAIL_SUBJECT_PREFIX = 'Hue %s - ' % desktop.conf.CLUSTER_ID.get()


# Configure database
if os.getenv('DESKTOP_DB_CONFIG'):
  conn_string = os.getenv('DESKTOP_DB_CONFIG')
  logging.debug("DESKTOP_DB_CONFIG SET: %s" % (conn_string))
  default_db = dict(
    list(
      zip(["ENGINE", "NAME", "TEST_NAME", "USER", "PASSWORD", "HOST", "PORT"], conn_string.split(':'))
    )
  )
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
    "SCHEMA" : desktop.conf.DATABASE.SCHEMA.get(),
    "PASSWORD" : desktop.conf.get_database_password(),
    "HOST" : desktop.conf.DATABASE.HOST.get(),
    "PORT" : str(desktop.conf.DATABASE.PORT.get()),
    "OPTIONS": force_dict_to_strings(desktop.conf.DATABASE.OPTIONS.get()),
    # DB used for tests
    "TEST_NAME" : test_name,
    "TEST_USER" : test_user,
    # Wrap each request in a transaction.
    "ATOMIC_REQUESTS" : True,
    "CONN_MAX_AGE" : desktop.conf.DATABASE.CONN_MAX_AGE.get(),
  }

DATABASES = {
  'default': default_db
}

if desktop.conf.QUERY_DATABASE.HOST.get():
  DATABASES['query'] = {
    'ENGINE': desktop.conf.QUERY_DATABASE.ENGINE.get(),
    'HOST': desktop.conf.QUERY_DATABASE.HOST.get(),
    'NAME': desktop.conf.QUERY_DATABASE.NAME.get(),
    'USER': desktop.conf.QUERY_DATABASE.USER.get(),
    'PASSWORD': desktop.conf.QUERY_DATABASE.PASSWORD.get(),
    'OPTIONS': desktop.conf.QUERY_DATABASE.OPTIONS.get(),
    'PORT': desktop.conf.QUERY_DATABASE.PORT.get(),
    "SCHEMA" : desktop.conf.QUERY_DATABASE.SCHEMA.get(),
  }

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache', # TODO: Parameterize here for all the caches
        'LOCATION': 'unique-hue'
    },
}
CACHES_HIVE_DISCOVERY_KEY = 'hive_discovery'
CACHES[CACHES_HIVE_DISCOVERY_KEY] = {
    'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    'LOCATION': CACHES_HIVE_DISCOVERY_KEY
}

CACHES_CELERY_KEY = 'celery'
CACHES_CELERY_QUERY_RESULT_KEY = 'celery_query_results'
if desktop.conf.TASK_SERVER.ENABLED.get():
  CACHES[CACHES_CELERY_KEY] = json.loads(desktop.conf.TASK_SERVER.EXECUTION_STORAGE.get())
  if desktop.conf.TASK_SERVER.RESULT_CACHE.get():
    CACHES[CACHES_CELERY_QUERY_RESULT_KEY] = json.loads(desktop.conf.TASK_SERVER.RESULT_CACHE.get())

# Configure sessions
SESSION_COOKIE_NAME = desktop.conf.SESSION.COOKIE_NAME.get()
SESSION_COOKIE_AGE = desktop.conf.SESSION.TTL.get()
SESSION_COOKIE_SECURE = desktop.conf.SESSION.SECURE.get()
SESSION_EXPIRE_AT_BROWSER_CLOSE = desktop.conf.SESSION.EXPIRE_AT_BROWSER_CLOSE.get()

# HTTP only
SESSION_COOKIE_HTTPONLY = desktop.conf.SESSION.HTTP_ONLY.get()

CSRF_COOKIE_SECURE = desktop.conf.SESSION.SECURE.get()
CSRF_COOKIE_HTTPONLY = desktop.conf.SESSION.HTTP_ONLY.get()
CSRF_COOKIE_NAME='csrftoken'

TRUSTED_ORIGINS = []
if desktop.conf.SESSION.TRUSTED_ORIGINS.get():
  TRUSTED_ORIGINS += desktop.conf.SESSION.TRUSTED_ORIGINS.get()

# This is required for knox
if desktop.conf.KNOX.KNOX_PROXYHOSTS.get(): # The hosts provided here don't have port. Add default knox port
  if desktop.conf.KNOX.KNOX_PORTS.get():
    hostport = []
    ports = [host.split(':')[1] for host in desktop.conf.KNOX.KNOX_PROXYHOSTS.get() if len(host.split(':')) > 1] # In case the ports are in hostname
    for port in ports + desktop.conf.KNOX.KNOX_PORTS.get():
      if port == '80':
        port = '' # Default port needs to be empty
      else:
        port = ':' + port
      hostport += [host.split(':')[0] + port for host in desktop.conf.KNOX.KNOX_PROXYHOSTS.get()]
    TRUSTED_ORIGINS += hostport
  else:
    TRUSTED_ORIGINS += desktop.conf.KNOX.KNOX_PROXYHOSTS.get()

if TRUSTED_ORIGINS:
  CSRF_TRUSTED_ORIGINS = TRUSTED_ORIGINS

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

if EMAIL_BACKEND == 'sendgrid_backend.SendgridBackend':
  SENDGRID_API_KEY = desktop.conf.get_smtp_password()
  SENDGRID_SANDBOX_MODE_IN_DEBUG = DEBUG


if has_channels():
  INSTALLED_APPS.append('channels')
  ASGI_APPLICATION = 'desktop.routing.application'
  CHANNEL_LAYERS = {
    'default': {
      'BACKEND': 'channels_redis.core.RedisChannelLayer',
      'CONFIG': {
        'hosts': [(desktop.conf.WEBSOCKETS.LAYER_HOST.get(), desktop.conf.WEBSOCKETS.LAYER_PORT.get())],
      },
    },
  }

# Used for securely creating sessions. Should be unique and not shared with anybody. Changing auth backends will invalidate all open sessions.
SECRET_KEY = desktop.conf.get_secret_key()
if SECRET_KEY:
  SECRET_KEY += str(AUTHENTICATION_BACKENDS)
else:
  SECRET_KEY = str(uuid.uuid4())

# Axes
AXES_LOGIN_FAILURE_LIMIT = desktop.conf.AUTH.LOGIN_FAILURE_LIMIT.get()
AXES_LOCK_OUT_AT_FAILURE = desktop.conf.AUTH.LOGIN_LOCK_OUT_AT_FAILURE.get()
AXES_COOLOFF_TIME = None
if desktop.conf.AUTH.LOGIN_COOLOFF_TIME.get() and desktop.conf.AUTH.LOGIN_COOLOFF_TIME.get() != 0:
  AXES_COOLOFF_TIME = desktop.conf.AUTH.LOGIN_COOLOFF_TIME.get()
AXES_USE_USER_AGENT = desktop.conf.AUTH.LOGIN_LOCK_OUT_USE_USER_AGENT.get()
AXES_LOCK_OUT_BY_COMBINATION_USER_AND_IP = desktop.conf.AUTH.LOGIN_LOCK_OUT_BY_COMBINATION_USER_AND_IP.get()
AXES_BEHIND_REVERSE_PROXY = desktop.conf.AUTH.BEHIND_REVERSE_PROXY.get()
AXES_REVERSE_PROXY_HEADER = desktop.conf.AUTH.REVERSE_PROXY_HEADER.get()


LOGIN_URL = '/hue/accounts/login'


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


# OpenID Connect
def is_oidc_configured():
  return 'desktop.auth.backend.OIDCBackend' in AUTHENTICATION_BACKENDS

if is_oidc_configured():
  INSTALLED_APPS.append('mozilla_django_oidc')
  if 'desktop.auth.backend.AllowFirstUserDjangoBackend' not in AUTHENTICATION_BACKENDS:
    # when multi-backend auth, standard login URL '/hue/accounts/login' is used.
    LOGIN_URL = '/oidc/authenticate/'
  SESSION_EXPIRE_AT_BROWSER_CLOSE = True
  MIDDLEWARE_CLASSES.append('mozilla_django_oidc.middleware.SessionRefresh')
  OIDC_RENEW_ID_TOKEN_EXPIRY_SECONDS = 15 * 60
  OIDC_RP_SIGN_ALGO = 'RS256'
  OIDC_RP_CLIENT_ID = desktop.conf.OIDC.OIDC_RP_CLIENT_ID.get()
  OIDC_RP_CLIENT_SECRET = desktop.conf.OIDC.OIDC_RP_CLIENT_SECRET.get()
  OIDC_OP_AUTHORIZATION_ENDPOINT = desktop.conf.OIDC.OIDC_OP_AUTHORIZATION_ENDPOINT.get()
  OIDC_OP_TOKEN_ENDPOINT = desktop.conf.OIDC.OIDC_OP_TOKEN_ENDPOINT.get()
  OIDC_OP_USER_ENDPOINT = desktop.conf.OIDC.OIDC_OP_USER_ENDPOINT.get()
  OIDC_RP_IDP_SIGN_KEY = desktop.conf.OIDC.OIDC_RP_IDP_SIGN_KEY.get()
  OIDC_OP_JWKS_ENDPOINT = desktop.conf.OIDC.OIDC_OP_JWKS_ENDPOINT.get()
  OIDC_VERIFY_SSL = desktop.conf.OIDC.OIDC_VERIFY_SSL.get()
  LOGIN_REDIRECT_URL = desktop.conf.OIDC.LOGIN_REDIRECT_URL.get()
  LOGOUT_REDIRECT_URL = desktop.conf.OIDC.LOGOUT_REDIRECT_URL.get()
  LOGIN_REDIRECT_URL_FAILURE = desktop.conf.OIDC.LOGIN_REDIRECT_URL_FAILURE.get()
  OIDC_STORE_ACCESS_TOKEN = True
  OIDC_STORE_ID_TOKEN = True
  OIDC_STORE_REFRESH_TOKEN = True
  OIDC_CREATE_USER = desktop.conf.OIDC.CREATE_USERS_ON_LOGIN.get()
  OIDC_USERNAME_ATTRIBUTE = desktop.conf.OIDC.OIDC_USERNAME_ATTRIBUTE.get()

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

if desktop.conf.SESSION.CONCURRENT_USER_SESSION_LIMIT.get():
  MIDDLEWARE_CLASSES.append('useradmin.middleware.ConcurrentUserSessionMiddleware')

LOAD_BALANCER_COOKIE = 'ROUTEID'

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

if is_abfs_enabled():
  file_upload_handlers.insert(0, 'azure.abfs.upload.ABFSFileUploadHandler')


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

# Instrumentation
if desktop.conf.INSTRUMENTATION.get():
  if sys.version_info[0] > 2:
    gc.set_debug(gc.DEBUG_UNCOLLECTABLE)
  else:
    gc.set_debug(gc.DEBUG_UNCOLLECTABLE | gc.DEBUG_OBJECTS)


if not desktop.conf.DATABASE_LOGGING.get():
  def disable_database_logging():
    from django.db.backends.base.base import BaseDatabaseWrapper
    from django.db.backends.utils import CursorWrapper

    BaseDatabaseWrapper.make_debug_cursor = lambda self, cursor: CursorWrapper(cursor, self)
  disable_database_logging()


############################################################
# Searching saved documents in Oracle returns following error:
#   DatabaseError: ORA-06502: PL/SQL: numeric or value error: character string buffer too small
# This is caused by DBMS_LOB.SUBSTR(%s, 4000) in Django framework django/db/backends/oracle/base.py
# Django has a ticket for this issue but unfixed: https://code.djangoproject.com/ticket/11580.
# Buffer size 4000 limit the length of field equals or less than 2000 characters.
#
# For performance reasons and to avoid searching in huge fields, we also truncate to a max length
DOCUMENT2_SEARCH_MAX_LENGTH = 2000

# To avoid performace issue, config check will display warning when Document2 over this size
DOCUMENT2_MAX_ENTRIES = 100000

DEBUG_TOOLBAR_PATCH_SETTINGS = False

def show_toolbar(request):
  # Here can be used to decide if showing toolbar bases on request object:
  #   For example, limit IP address by checking request.META['REMOTE_ADDR'], which can avoid setting INTERNAL_IPS.
  list_allowed_users = desktop.conf.DJANGO_DEBUG_TOOL_USERS.get()
  is_user_allowed = list_allowed_users[0] == '' or request.user.username in list_allowed_users
  return DEBUG and desktop.conf.ENABLE_DJANGO_DEBUG_TOOL.get() and is_user_allowed

if DEBUG and desktop.conf.ENABLE_DJANGO_DEBUG_TOOL.get():
  idx = MIDDLEWARE_CLASSES.index('desktop.middleware.ClusterMiddleware')
  MIDDLEWARE_CLASSES.insert(idx + 1, 'debug_panel.middleware.DebugPanelMiddleware')

  INSTALLED_APPS += (
      'debug_toolbar',
      'debug_panel',
  )

  DEBUG_TOOLBAR_PANELS = [
      'debug_toolbar.panels.versions.VersionsPanel',
      'debug_toolbar.panels.timer.TimerPanel',
      'debug_toolbar.panels.settings.SettingsPanel',
      'debug_toolbar.panels.headers.HeadersPanel',
      'debug_toolbar.panels.request.RequestPanel',
      'debug_toolbar.panels.sql.SQLPanel',
      'debug_toolbar.panels.staticfiles.StaticFilesPanel',
      'debug_toolbar.panels.templates.TemplatesPanel',
      'debug_toolbar.panels.cache.CachePanel',
      'debug_toolbar.panels.signals.SignalsPanel',
      'debug_toolbar.panels.logging.LoggingPanel',
      'debug_toolbar.panels.redirects.RedirectsPanel',
  ]

  DEBUG_TOOLBAR_CONFIG = {
      'JQUERY_URL': os.path.join(STATIC_ROOT, 'desktop/ext/js/jquery/jquery-2.2.4.min.js'),
      'RESULTS_CACHE_SIZE': 200,
      'SHOW_TOOLBAR_CALLBACK': show_toolbar
  }

  CACHES.update({
      'debug-panel': {
          'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
          'LOCATION': '/var/tmp/debug-panel-cache',
          'OPTIONS': {
              'MAX_ENTRIES': 10000
          }
      }
  })


################################################################
# Celery settings
################################################################

if desktop.conf.TASK_SERVER.ENABLED.get() or desktop.conf.TASK_SERVER.BEAT_ENABLED.get():
  CELERY_BROKER_URL = desktop.conf.TASK_SERVER.BROKER_URL.get()

  CELERY_ACCEPT_CONTENT = ['json']
  CELERY_RESULT_BACKEND = desktop.conf.TASK_SERVER.CELERY_RESULT_BACKEND.get()
  CELERY_TASK_SERIALIZER = 'json'

  CELERYD_OPTS = desktop.conf.TASK_SERVER.RESULT_CELERYD_OPTS.get()

# %n will be replaced with the first part of the nodename.
# CELERYD_LOG_FILE="/var/log/celery/%n%I.log"
# CELERYD_PID_FILE="/var/run/celery/%n.pid"
# CELERY_CREATE_DIRS = 1
# CELERYD_USER = desktop.conf.SERVER_USER.get()
# CELERYD_GROUP = desktop.conf.SERVER_GROUP.get()

  if desktop.conf.TASK_SERVER.BEAT_ENABLED.get():
    INSTALLED_APPS.append('django_celery_beat')
    INSTALLED_APPS.append('timezone_field')
    USE_TZ = True


PROMETHEUS_EXPORT_MIGRATIONS = False # Needs to be there even when enable_prometheus is not enabled
if desktop.conf.ENABLE_PROMETHEUS.get():
  MIDDLEWARE_CLASSES.insert(0, 'django_prometheus.middleware.PrometheusBeforeMiddleware')
  MIDDLEWARE_CLASSES.append('django_prometheus.middleware.PrometheusAfterMiddleware')

  if 'mysql' in DATABASES['default']['ENGINE']:
    DATABASES['default']['ENGINE'] = DATABASES['default']['ENGINE'].replace('django.db.backends', 'django_prometheus.db.backends')
  # enable only when use these metrics: django_cache_get_total, django_cache_hits_total, django_cache_misses_total
  # for name, val in list(CACHES.items()):
  #   val['BACKEND'] = val['BACKEND'].replace('django.core.cache.backends', 'django_prometheus.cache.backends')


################################################################
# OpenTracing settings
################################################################

if desktop.conf.TRACING.ENABLED.get():
  OPENTRACING_TRACE_ALL = desktop.conf.TRACING.TRACE_ALL.get()
  OPENTRACING_TRACER_CALLABLE = __name__ + '.tracer'

  def tracer():
      from jaeger_client import Config
      config = Config(
          config={
              'sampler': {
                  'type': 'const',
                  'param': 1,
              },
          },
          # metrics_factory=PrometheusMetricsFactory(namespace='hue-api'),
          service_name='hue-api',
          validate=True,
      )
      return config.initialize_tracer()

  OPENTRACING_TRACED_ATTRIBUTES = ['META'] # Only valid if OPENTRACING_TRACE_ALL == True
  if desktop.conf.TRACING.TRACE_ALL.get():
    MIDDLEWARE_CLASSES.insert(0, 'django_opentracing.OpenTracingMiddleware')

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
import sys
import desktop.conf
import desktop.log
from desktop.lib.paths import get_desktop_root
import pkg_resources

HUE_DESKTOP_VERSION = pkg_resources.get_distribution("desktop").version or "Unknown"
NICE_NAME = "Hue"

ENV_HUE_PROCESS_NAME = "HUE_PROCESS_NAME"

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
ADMINS = (
    ('Hue Administrator', 'admin@localhost')
)
MANAGERS = ADMINS

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'
#LANGUAGE_CODE = 'it'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True
USE_L10N = True

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

############################################################
# Part 3: Django configuration
############################################################

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'desktop.lib.template_loader.load_template_source',
)

MIDDLEWARE_CLASSES = [
    'desktop.middleware.DatabaseLoggingMiddleware',

    'django.middleware.common.CommonMiddleware',
    'desktop.middleware.SessionOverPostMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'babeldjango.middleware.LocaleMiddleware',
    'desktop.middleware.AjaxMiddleware',
    # Must be after Session, Auth, and Ajax.  Before everything else.
    'desktop.middleware.LoginAndPermissionMiddleware',
    'desktop.middleware.FlashMessageMiddleware',
    'desktop.middleware.JFrameMiddleware',
    'desktop.middleware.ExceptionMiddleware',
    'desktop.middleware.ClusterMiddleware',
    'desktop.middleware.AppSpecificMiddleware',
    # 'debug_toolbar.middleware.DebugToolbarMiddleware'
]

ROOT_URLCONF = 'desktop.urls'

TEMPLATE_DIRS = (
    get_desktop_root("core/templates")
)

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',

    'django.contrib.admin',
    'django_extensions',

    # 'debug_toolbar',
    'south', # database migration tool

    # JavaScript depency loading
    'depender',

	# i18n support
	'babeldjango',

    # Desktop injects all the other installed apps into here magically.
    'desktop'
]

# Desktop doesn't use an auth profile module, because
# because it doesn't mesh very well with the notion
# of having multiple apps.  If your app needs
# to store data related to users, it should
# manage its own table with an appropriate foreign key.
AUTH_PROFILE_MODULE=None

LOGIN_REDIRECT_URL = "/"

PYLINTRC = get_desktop_root('.pylintrc')

# Insert our HDFS upload handler
FILE_UPLOAD_HANDLERS = (
  'hadoop.fs.upload.HDFSfileUploadHandler',
  'django.core.files.uploadhandler.MemoryFileUploadHandler',
  'django.core.files.uploadhandler.TemporaryFileUploadHandler',
)

############################################################
# Part 4: Installation of apps
############################################################

_config_dir = os.getenv("HUE_CONF_DIR", get_desktop_root("conf"))

# Libraries are loaded and configured before the apps
appmanager.load_libs()
_lib_conf_modules = [dict(module=app.conf, config_key=None) for app in appmanager.DESKTOP_LIBS if app.conf is not None]

appmanager.load_apps()
for app in appmanager.DESKTOP_APPS:
  INSTALLED_APPS.extend(app.django_apps)

logging.debug("Installed Django modules: %s" % ",".join(map(str, appmanager.DESKTOP_MODULES)))

# Load app configuration
_app_conf_modules = [dict(module=app.conf, config_key=app.config_key) for app in appmanager.DESKTOP_APPS if app.conf is not None]
_app_conf_modules.append(dict(module=desktop.conf, config_key=None))

conf.initialize(_lib_conf_modules, _config_dir)
conf.initialize(_app_conf_modules, _config_dir)

appmanager.determine_broken_apps()

# Now that we've loaded the desktop conf, set the django DEBUG mode based on the conf.
DEBUG = desktop.conf.DJANGO_DEBUG_MODE.get()
TEMPLATE_DEBUG = DEBUG

############################################################
# Part 4a: Django configuration that requires bound Desktop
# configs.
############################################################
# Configure database

if os.getenv('DESKTOP_DB_CONFIG'):
  conn_string = os.getenv('DESKTOP_DB_CONFIG')
  logging.debug("DESKTOP_DB_CONFIG SET: %s" % (conn_string))
  default_db = dict(zip(
    ["ENGINE", "NAME", "TEST__NAME", "USER", "PASSWORD", "HOST", "PORT"],
    conn_string.split(':')))
else:
  default_db = {
    "ENGINE" : desktop.conf.DATABASE.ENGINE.get(),
    "NAME" : desktop.conf.DATABASE.NAME.get(),
    "USER" : desktop.conf.DATABASE.USER.get(),
    "PASSWORD" : desktop.conf.DATABASE.PASSWORD.get(),
    "HOST" : desktop.conf.DATABASE.HOST.get(),
    "PORT" : desktop.conf.DATABASE.PORT.get(),
    # DB used for tests
    "TEST_NAME" : get_desktop_root('desktop-test.db')
  }

DATABASES = {
  'default': default_db
}

TIME_ZONE = desktop.conf.TIME_ZONE.get()
# Desktop supports only one authentication backend.
AUTHENTICATION_BACKENDS = (desktop.conf.AUTH.BACKEND.get(),)

EMAIL_HOST = desktop.conf.SMTP.HOST.get()
EMAIL_PORT = desktop.conf.SMTP.PORT.get()
EMAIL_HOST_USER = desktop.conf.SMTP.USER.get()
EMAIL_HOST_PASSWORD = desktop.conf.SMTP.PASSWORD.get()
EMAIL_USE_TLS = desktop.conf.SMTP.USE_TLS.get()
DEFAULT_FROM_EMAIL = desktop.conf.SMTP.DEFAULT_FROM.get()

# Used for securely creating sessions.  Should be unique and not shared with anybody.
SECRET_KEY = desktop.conf.SECRET_KEY.get()
if SECRET_KEY == "":
  logging.warning("secret_key should be configured")


############################################################

# Depender configuration
DEPENDER_ROOT = get_desktop_root(".")

def prep_depender_config():
  yamls = [
    "../ext/thirdparty/js/core/package.yml",
    "../ext/thirdparty/js/more/package.yml",
    "../ext/thirdparty/js/art/package.yml",
    "../ext/thirdparty/js/touch/package.yml",
    "../ext/thirdparty/js/color/package.yml",
    "../ext/thirdparty/js/behavior/package.yml",
    "../ext/thirdparty/js/more-behaviors/package.yml",
    "../ext/thirdparty/js/widgets/package.yml",
    "../ext/thirdparty/js/slick/package.yml",
    "core/static/js/package.yml",
    "core/static/js/ccs.package.yml",
    "../ext/thirdparty/js/depender/package.yml",
    "../ext/thirdparty/js/fittext/package.yml",
    "../ext/thirdparty/js/jframe/package.yml",
  ]
  scripts_json = [
    ("clientcide",  "../ext/thirdparty/js/clientcide/Source/scripts.json"),
    ("protovis" ,  "../desktop/libs/protovis/static/js/Source/scripts.json"),
  ]


  for app in appmanager.DESKTOP_APPS:
    yamls.extend(app.depender_yamls)
    scripts_json.extend(app.depender_jsons)

  return ([ os.path.abspath(os.path.join(DEPENDER_ROOT, x)) for x in yamls ],
    [ (name, os.path.abspath(os.path.join(DEPENDER_ROOT, p))) for name, p in scripts_json ])

DEPENDER_PACKAGE_YMLS, DEPENDER_SCRIPTS_JSON = prep_depender_config()
DEPENDER_YUI_PATH = None
DEPENDER_COMPRESSOR = None
# Set to true to re-load all JS every time. (slowish)
DEPENDER_DEBUG = os.getenv("DESKTOP_DEPENDER_DEBUG", "0") not in ["0",""]

# Necessary for South to not futz with tests.  Fixed in South 0.7.1
SKIP_SOUTH_TESTS = True

# Set up environment variable so Kerberos libraries look at our private
# ticket cache
os.environ['KRB5CCNAME'] = desktop.conf.KERBEROS.CCACHE_PATH.get()

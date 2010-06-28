# Minimal Django settings for mootools depender.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
)

ROOT_URLCONF = 'mootools.urls'

INSTALLED_APPS = (
    'depender'
)

# Depender configuration


# Configuration of MooTools Depender for Django
# =============================================
import os
import logging
logging.basicConfig(level=logging.INFO)

DEPENDER_PACKAGE_YMLS = (
  os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "libs", "core", "package.yml")),
  os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "libs", "more", "package.yml")),
  # Don't forget to add the depender client to your libraries!
  os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "client", "package.yml")),
)
DEPENDER_SCRIPTS_JSON = []

# Set to true to re-load all JS every time. (slowish)
DEPENDER_DEBUG = os.getenv("DEPENDER_DEBUG", "0").lower() not in ["0","false",""]

DEPENDER_YUI_PATH = os.path.join(os.path.dirname(__file__), "../../compressors/yuicompressor-2.4.2.jar")

# Copyright (C) 2010-2012 Yaco Sistemas (http://www.yaco.es)
# Copyright (C) 2009 Lorenzo Gil Sanchez <lorenzo.gil.sanchez@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#            http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import copy
from importlib import import_module

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from saml2.config import SPConfig

from djangosaml2.utils import get_custom_setting


def get_config_loader(path, request=None):
    i = path.rfind('.')
    module, attr = path[:i], path[i + 1:]
    try:
        mod = import_module(module)
    except ImportError as e:
        raise ImproperlyConfigured(
            'Error importing SAML config loader %s: "%s"' % (path, e))
    except ValueError as e:
        raise ImproperlyConfigured(
            'Error importing SAML config loader. Is SAML_CONFIG_LOADER '
            'a correctly string with a callable path?'
            )
    try:
        config_loader = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured(
            'Module "%s" does not define a "%s" config loader' %
            (module, attr)
            )

    if not hasattr(config_loader, '__call__'):
        raise ImproperlyConfigured(
            "SAML config loader must be a callable object.")

    return config_loader


def config_settings_loader(request=None):
    """Utility function to load the pysaml2 configuration.

    This is also the default config loader.
    """
    conf = SPConfig()
    conf.load(copy.deepcopy(settings.SAML_CONFIG))
    return conf


def get_config(config_loader_path=None, request=None):
    config_loader_path = config_loader_path or get_custom_setting(
        'SAML_CONFIG_LOADER', 'djangosaml2.conf.config_settings_loader')

    config_loader = get_config_loader(config_loader_path)
    return config_loader(request)

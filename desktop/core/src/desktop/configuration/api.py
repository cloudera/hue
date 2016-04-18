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

import logging

from django.contrib.auth.models import Group, User
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST

from desktop.lib.django_util import JsonResponse
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import force_unicode
from desktop.models import DefaultConfiguration

from notebook.connectors.hiveserver2 import HiveConfiguration, ImpalaConfiguration
from notebook.connectors.spark_shell import SparkConfiguration


LOG = logging.getLogger(__name__)


def api_error_handler(func):
  def decorator(*args, **kwargs):
    response = {}

    try:
      return func(*args, **kwargs)
    except Exception, e:
      LOG.exception('Error running %s' % func)
      response['status'] = -1
      response['message'] = force_unicode(str(e))
    finally:
      if response:
        return JsonResponse(response)

  return decorator

def get_configurable():
  # TODO: Use metaclasses to self-register configurable apps
  app_configs = {}
  config_classes = [HiveConfiguration, ImpalaConfiguration, SparkConfiguration]

  for config_cls in config_classes:
    if not hasattr(config_cls, 'APP_NAME') or not hasattr(config_cls, 'PROPERTIES'):
      LOG.exception('Configurable classes must define APP_NAME and PROPERTIES.')
    app_name = config_cls.APP_NAME
    app_configs[app_name] = {
      'properties': config_cls.PROPERTIES
    }

    # Get default config
    if DefaultConfiguration.objects.filter(app=app_name, is_default=True).exists():
      default_config = DefaultConfiguration.objects.get(app=app_name, is_default=True)
      app_configs[app_name].update({'default': default_config.properties_list})

    # Get group configs
    if DefaultConfiguration.objects.filter(app=app_name, group__isnull=False).exists():
      app_configs[app_name].update({'groups': {}})
      for grp_config in DefaultConfiguration.objects.filter(app=app_name, group__isnull=False).all():
        app_configs[app_name]['groups'].update({grp_config.group.id: grp_config.properties_list})

  return {
    'status': 0,
    'apps': app_configs
  }

@api_error_handler
def get_configurable_apps(request):
  # TODO: Use metaclasses to self-register configurable apps
  app_configs = {}
  config_classes = [HiveConfiguration, ImpalaConfiguration]

  for config_cls in config_classes:
    if not hasattr(config_cls, 'APP_NAME') or not hasattr(config_cls, 'PROPERTIES'):
      LOG.exception('Configurable classes must define APP_NAME and PROPERTIES.')
    app_name = config_cls.APP_NAME
    app_configs[app_name] = {
      'properties': config_cls.PROPERTIES
    }

    # Get default config
    if DefaultConfiguration.objects.filter(app=app_name, is_default=True).exists():
      default_config = DefaultConfiguration.objects.get(app=app_name, is_default=True)
      app_configs[app_name].update({'default': default_config.properties_list})

    # Get group configs
    if DefaultConfiguration.objects.filter(app=app_name, group__isnull=False).exists():
      app_configs[app_name].update({'groups': {}})
      for grp_config in DefaultConfiguration.objects.filter(app=app_name, group__isnull=False).all():
        app_configs[app_name]['groups'].update({grp_config.group.id: grp_config.properties_list})

  return JsonResponse({
    'status': 0,
    'apps': app_configs
  })


@api_error_handler
def search_default_configurations(request):
  app = request.GET.get('app')
  is_default = request.GET.get('is_default', None)
  group_id = request.GET.get('group_id')
  user_id = request.GET.get('user_id')

  configs = DefaultConfiguration.objects.all()

  if app:
    configs = configs.filter(app=app)

  if is_default:
    configs = configs.filter(is_default=is_default.lower() == 'true')

  if group_id:
    configs = configs.filter(group=Group.objects.get(id=group_id))

  if user_id:
    configs = configs.filter(user=User.objects.get(id=user_id))

  return JsonResponse({
    'status': 0,
    'configurations': [config.to_dict() for config in configs]
  })


@api_error_handler
def get_default_configuration_for_user(request):
  app = request.GET.get('app')
  user_id = request.GET.get('user_id')

  if not app or not user_id:
    raise PopupException(_('get_default_configuration_for_user requires app and user_id'))

  user = User.objects.get(id=user_id)

  if not user:
    raise PopupException(_('Could not find user with User ID: %s') % user_id)

  config = DefaultConfiguration.objects.get_configuration_for_user(app, user)

  return JsonResponse({
    'status': 0,
    'configuration': config.to_dict() if config is not None else None
  })


@api_error_handler
@require_POST
def save_default_configuration(request):
  app = request.POST.get('app')
  properties = request.POST.get('properties')
  is_default = request.POST.get('is_default', 'false')
  group_id = request.POST.get('group_id')
  user_id = request.POST.get('user_id')

  if not app or not properties or not (is_default or group_id or user_id):
    raise PopupException(_('save_default_configuration requires app, properties, and is_default, group_id or user_id'))

  if is_default and is_default.lower() == 'true':
    kwargs = {'app': app, 'is_default': True}
  elif group_id:
    try:
      group = Group.objects.get(id=int(group_id))
      kwargs = {'app': app, 'is_default': False, 'group': group}
    except Group.DoesNotExist, e:
      raise PopupException(_('Could not find group with ID: %s') % group_id)
  elif user_id:
    try:
      user = User.objects.get(id=int(user_id))
      kwargs = {'app': app, 'is_default': False, 'user': user}
    except User.DoesNotExist, e:
      raise PopupException(_('Could not find user with ID: %s') % user_id)
  else:
    raise PopupException(_('Cannot find configuration for %(app)s with: is_default=%(is_default)s, group_id=%(group_id)s, user_id=%(user_id)s') %
                         {'app': app, 'is_default': is_default, 'group_id': group_id, 'user_id': user_id})

  config, created = DefaultConfiguration.objects.get_or_create(**kwargs)
  # TODO: Validate properties?
  config.properties = properties
  config.save()

  return JsonResponse({
    'status': 0,
    'configuration': config.to_dict()
  })


@api_error_handler
@require_POST
def delete_default_configuration(request):
  app = request.POST.get('app')
  is_default = request.POST.get('is_default', 'false')
  group_id = request.POST.get('group_id')
  user_id = request.POST.get('user_id')

  if not app or not (is_default or group_id or user_id):
    raise PopupException(_('save_default_configuration requires app and is_default, group_id or user_id'))

  if is_default and is_default.lower() == 'true':
    kwargs = {'app': app, 'is_default': True}
  elif group_id:
    try:
      group = Group.objects.get(id=int(group_id))
      kwargs = {'app': app, 'is_default': False, 'group': group}
    except Group.DoesNotExist, e:
      raise PopupException(_('Could not find group with ID: %s') % group_id)
  elif user_id:
    try:
      user = User.objects.get(id=int(user_id))
      kwargs = {'app': app, 'is_default': False, 'user': user}
    except User.DoesNotExist, e:
      raise PopupException(_('Could not find user with ID: %s') % user_id)
  else:
    raise PopupException(_('Cannot find configuration for %(app)s with: is_default=%(is_default)s, group_id=%(group_id)s, user_id=%(user_id)s') %
                         {'app': app, 'is_default': is_default, 'group_id': group_id, 'user_id': user_id})

  try:
    DefaultConfiguration.objects.get(**kwargs).delete()
  except DefaultConfiguration.DoesNotExist, e:
    raise PopupException(_('Cannot find configuration for %(app)s with: is_default=%(is_default)s, group_id=%(group_id)s, user_id=%(user_id)s') %
                         {'app': app, 'is_default': is_default, 'group_id': group_id, 'user_id': user_id})

  return JsonResponse({
    'status': 0,
    'message': _('Successfully deleted the default configuration.')
  })

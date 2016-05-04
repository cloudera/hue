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

import json
import logging

from django.contrib.auth.models import Group, User
from django.db import transaction
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST

from desktop.lib.django_util import JsonResponse
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import force_unicode
from desktop.models import DefaultConfiguration

from notebook.connectors.hiveserver2 import HiveConfiguration, ImpalaConfiguration
from notebook.connectors.spark_shell import SparkConfiguration

try:
  from oozie.models2 import WorkflowConfiguration as OozieWorkflowConfiguration
except ImportError, e:
  OozieWorkflowConfiguration = None


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


@api_error_handler
def default_configurations(request):
  if request.method == 'GET':  # get configurable apps
    configurations = _get_default_configurations()

    response = {
      'status': 0,
      'configuration': configurations
    }
  elif request.method == 'POST':  # save/overwrite app configurations
    configurations = json.loads(request.POST.get('configuration'))
    updated_configurations = _update_default_and_group_configurations(configurations)

    response = {
      'status': 0,
      'configuration': updated_configurations
    }
  else:
    raise PopupException(_('%s method is not supported') % request.method)

  return JsonResponse(response)


@api_error_handler
def app_configuration_for_user(request):
  if request.method == 'GET':  # get app configuration for user (checks in order of user, group, default precedence)
    app = request.GET.get('app')
    user_id = request.GET.get('user_id')

    if not app or not user_id:
      raise PopupException(_('app_configuration_for_user requires app and user_id'))

    user = User.objects.get(id=user_id)

    if not user:
      raise PopupException(_('Could not find user with User ID: %s') % user_id)

    config = DefaultConfiguration.objects.get_configuration_for_user(app, user)

    response = {
      'status': 0,
      'configuration': config.to_dict() if config is not None else None
    }
  elif request.method == 'POST':  # save user-specific configuration for app
    app = request.POST.get('app')
    user_id = request.POST.get('user_id')
    properties = json.loads(request.POST.get('properties'))

    if not app or not user_id or not properties:
      raise PopupException(_('app_configuration_for_user requires app, user_id, and properties'))

    try:
      user = User.objects.get(id=int(user_id))
    except User.DoesNotExist, e:
      raise PopupException(_('Could not find user with ID: %s') % user_id)

    config = _save_configuration(app, properties, is_default=False, user=user)
    LOG.info('Saved user configuration for app: %s and group_id: %s' % (app, user_id))

    response = {
      'status': 0,
      'configuration': config.to_dict()
    }
  else:
    raise PopupException(_('%s method is not supported') % request.method)

  return JsonResponse(response)


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


def _get_default_configurations():
  """
  :return: Dictionary where key is app name and values include the defined "properties" list and any saved "default"
    configuration or "groups" configurations
  """
  # TODO: Use metaclasses to self-register configurable apps
  app_configs = {}
  config_classes = _get_configurable_classes()

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

  return app_configs


def _get_configurable_classes():
  config_classes = [HiveConfiguration, ImpalaConfiguration, SparkConfiguration]

  # Optional configurable classes from installed apps
  if OozieWorkflowConfiguration is not None:
    config_classes.append(OozieWorkflowConfiguration)

  return config_classes


def _update_default_and_group_configurations(configurations):
  """
  Overrides (deletes and updates) saved app configs based on the given configurations dict. Wrapped in an atomic
    transaction block so that it is an all-or-nothing operation.
  :param configurations: Dictionary of app to configuration objects. Only processes "default" and "groups" configs
  :return: updated configurations dict
  """
  with transaction.atomic():
    # delete all previous default and group configurations
    DefaultConfiguration.objects.filter(Q(is_default=True) | Q(group__isnull=False)).delete()

    for app, configs in configurations.items():
      if 'default' in configs:
        properties = configs['default']
        _save_configuration(app, properties, is_default=True)
        LOG.info('Saved default configuration for app: %s' % app)

      if 'groups' in configs:
        for group_id, properties in configs['groups'].items():
          try:
            group = Group.objects.get(id=int(group_id))
          except Group.DoesNotExist, e:
            raise PopupException(_('Could not find group with ID: %s') % group_id)
          _save_configuration(app, properties, is_default=False, group=group)
          LOG.info('Saved group configuration for app: %s and group_id: %s' % (app, group_id))

  return _get_default_configurations()


def _save_configuration(app, properties, is_default=False, group=None, user=None):
  if not (is_default or group or user):
    raise PopupException(_('_save_configuration requires app, properties, and is_default, group_id or user_id'))

  kwargs = {'app': app, 'is_default': is_default, 'group': group, 'user': user}
  config, created = DefaultConfiguration.objects.get_or_create(**kwargs)
  config.properties = json.dumps(properties)
  config.save()
  return config

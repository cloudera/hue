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

from builtins import str
import json
import logging

from django.utils.translation import ugettext as _

from desktop import appmanager
from desktop.lib.django_util import JsonResponse, render, login_notrequired
from desktop.log.access import access_log_level
from desktop.models import Settings, hue_version
from desktop.views import collect_usage

from desktop.auth.backend import is_admin


def admin_wizard(request):
  if is_admin(request.user):
    apps = appmanager.get_apps(request.user)
  else:
    apps = []
  app_names = [app.name for app in sorted(apps, key=lambda app: app.menu_index)]

  return render('admin_wizard.mako', request, {
      'version': hue_version(),
      'apps': dict([(app.name, app) for app in apps]),
      'app_names': app_names,
      'is_embeddable': request.GET.get('is_embeddable', False),
      'collect_usage': collect_usage(),
  })


def update_preferences(request):
  response = {'status': -1, 'data': ''}

  if request.method == 'POST':
    try:
      settings = Settings.get_settings()
      settings.collect_usage = request.POST.get('collect_usage', False)
      settings.save()
      response['status'] = 0
      response['collect_usage'] = settings.collect_usage
    except Exception as e:
      response['data'] = str(e)
  else:
    response['data'] = _('POST request required.')

  return JsonResponse(response)

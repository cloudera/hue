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

from django.conf import settings
from django.utils.translation import ugettext as _

from desktop import appmanager
from desktop.lib.django_util import JsonResponse, render, login_notrequired
from desktop.log.access import access_log_level
from desktop.models import Settings
from desktop.views import collect_usage


@login_notrequired
@access_log_level(logging.DEBUG)
def admin_wizard(request):
  if request.user.is_superuser:
    apps = appmanager.get_apps(request.user)
  else:
    apps = []
  app_names = [app.name for app in sorted(apps, key=lambda app: app.menu_index)]

  tours_and_tutorials = Settings.get_settings().tours_and_tutorials

  return render('admin_wizard.mako', request, {
      'version': settings.HUE_DESKTOP_VERSION,
      'apps': dict([(app.name, app) for app in apps]),
      'app_names': app_names,
      'tours_and_tutorials': tours_and_tutorials,
      'collect_usage': collect_usage(),
  })


def update_preferences(request):
  response = {'status': -1, 'data': ''}

  if request.method == 'POST':
    try:
      settings = Settings.get_settings()
      settings.tours_and_tutorials = request.POST.get('tours_and_tutorials', False)
      settings.collect_usage = request.POST.get('collect_usage', False)
      settings.save()
      response['status'] = 0
      response['tours_and_tutorials'] = settings.tours_and_tutorials
      response['collect_usage'] = settings.collect_usage
    except Exception, e:
      response['data'] = str(e)
  else:
    response['data'] = _('POST request required.')

  return JsonResponse(response)

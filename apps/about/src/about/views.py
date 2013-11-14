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

from django.conf import settings
from django.http import HttpResponse
from django.utils.translation import ugettext as _

from desktop.lib.django_util import render
from desktop.models import Settings
from desktop import appmanager


def admin_wizard(request):
  apps = appmanager.get_apps(request.user)
  app_names = [app.name for app in sorted(apps, key=lambda app: app.menu_index)]

  tours_and_tutorials = Settings.get_settings().tours_and_tutorials

  return render('admin_wizard.mako', request, {
      'version': settings.HUE_DESKTOP_VERSION,
      'apps': dict([(app.name, app) for app in apps]),
      'app_names': app_names,
      'tours_and_tutorials': tours_and_tutorials,
  })


def update_preferences(request):
  response = {'status': -1, 'data': ''}

  if request.method == 'POST':
    try:
      settings = Settings.get_settings()
      settings.tours_and_tutorials = request.POST.get('tours_and_tutorials', False)
      settings.save()
      response['status'] = 0
      response['tours_and_tutorials'] = settings.tours_and_tutorials
    except Exception, e:
      response['data'] = str(e)
  else:
    response['data'] = _('POST request required.')

  return HttpResponse(json.dumps(response), mimetype="application/json")

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

from __future__ import absolute_import

import logging
import re

# FIXME: This could be replaced with hooking into the `AppConfig.ready()`
# signal in Django 1.7:
#
# https://docs.djangoproject.com/en/1.7/ref/applications/#django.apps.AppConfig.ready
#
# For now though we have to load in the monkey patches here because we know
# this file has been loaded after `desktop.settings` has been loaded.
import desktop.monkey_patches

import desktop.lib.metrics.file_reporter
desktop.lib.metrics.file_reporter.start_file_reporter()

from django.conf import settings
from django.conf.urls import include, patterns
from django.contrib import admin

from desktop import appmanager
from desktop.conf import METRICS, USE_NEW_EDITOR


# Django expects handler404 and handler500 to be defined.
# django.conf.urls provides them. But we want to override them.
# Also see http://code.djangoproject.com/ticket/5350
handler403 = 'desktop.views.serve_403_error'
handler404 = 'desktop.views.serve_404_error'
handler500 = 'desktop.views.serve_500_error'


admin.autodiscover()

# Some django-wide URLs
dynamic_patterns = patterns('desktop.auth.views',
  (r'^accounts/login/$', 'dt_login'),
  (r'^accounts/logout/$', 'dt_logout', {'next_page': '/'}),
  (r'^profile$', 'profile'),
  (r'^login/oauth/?$', 'oauth_login'),
  (r'^login/oauth_authenticated/?$', 'oauth_authenticated'),
)


if USE_NEW_EDITOR.get():
  dynamic_patterns += patterns('desktop.views',
    (r'^home$','home2'),
    (r'^home2$','home')
  )
else:
  dynamic_patterns += patterns('desktop.views',
    (r'^home$','home'),
    (r'^home2$','home2')
  )

dynamic_patterns += patterns('desktop.views',
  (r'^logs$','log_view'),
  (r'^desktop/dump_config$','dump_config'),
  (r'^desktop/download_logs$','download_log_view'),
  (r'^bootstrap.js$', 'bootstrap'), # unused

  (r'^desktop/prefs/(?P<key>\w+)?$', 'prefs'),
  (r'^desktop/status_bar/?$', 'status_bar'),
  (r'^desktop/debug/is_alive$','is_alive'),
  (r'^desktop/debug/is_idle$','is_idle'),
  (r'^desktop/debug/threads$', 'threads'),
  (r'^desktop/debug/memory$', 'memory'),
  (r'^desktop/debug/check_config$', 'check_config'),
  (r'^desktop/debug/check_config_ajax$', 'check_config_ajax'),
  (r'^desktop/log_frontend_event$', 'log_frontend_event'),

  # Jasmine
  (r'^jasmine', 'jasmine'),

  # Unsupported browsers
  (r'^boohoo$','unsupported'),

  # Top level web page!
  (r'^$', 'index'),
)

dynamic_patterns += patterns('desktop.api',
  # Tags
  (r'^desktop/api/tag/add_tag$', 'add_tag'),
  (r'^desktop/api/tag/remove_tag$', 'remove_tag'),
  (r'^desktop/api/doc/tag$', 'tag'),
  (r'^desktop/api/doc/update_tags$', 'update_tags'),
  (r'^desktop/api/doc/get$', 'get_document'),

  # Permissions
  (r'^desktop/api/doc/update_permissions', 'update_permissions'),
)

dynamic_patterns += patterns('desktop.api2',
  (r'^desktop/api2/doc/open?$', 'open_document'),  # To keep before get_document
  (r'^desktop/api2/docs/?$', 'search_documents'),  # search documents for current user
  (r'^desktop/api2/doc/?$', 'get_document'),  # get doc/dir by path or UUID

  (r'^desktop/api2/doc/move/?$', 'move_document'),
  (r'^desktop/api2/doc/mkdir/?$', 'create_directory'),
  (r'^desktop/api2/doc/update/?$', 'update_document'),
  (r'^desktop/api2/doc/delete/?$', 'delete_document'),
  (r'^desktop/api2/doc/share/?$', 'share_document'),

  (r'^desktop/api2/doc/export/?$', 'export_documents'),
  (r'^desktop/api2/doc/import/?$', 'import_documents'),
)

# Default Configurations
dynamic_patterns += patterns('desktop.configuration.api',
  (r'^desktop/api/configurations/?$', 'default_configurations'),
  (r'^desktop/api/configurations/user/?$', 'app_configuration_for_user'),
  (r'^desktop/api/configurations/delete/?$', 'delete_default_configuration'),
)

dynamic_patterns += patterns('useradmin.views',
  (r'^desktop/api/users/autocomplete', 'list_for_autocomplete'),
)

# Metrics specific
if METRICS.ENABLE_WEB_METRICS.get():
  dynamic_patterns += patterns('',
    (r'^desktop/metrics/', include('desktop.lib.metrics.urls'))
  )

dynamic_patterns += patterns('',
  (r'^admin/', include(admin.site.urls)),
)

static_patterns = []

# SAML specific
if settings.SAML_AUTHENTICATION:
  static_patterns.append((r'^saml2/', include('libsaml.urls')))

# OpenId specific
if settings.OPENID_AUTHENTICATION:
    static_patterns.append((r'^openid/', include('libopenid.urls')))

if settings.OAUTH_AUTHENTICATION:
  static_patterns.append((r'^oauth/', include('liboauth.urls')))

# Root each app at /appname if they have a "urls" module
for app in appmanager.DESKTOP_MODULES:
  if app.urls:
    if app.is_url_namespaced:
      namespace = {'namespace': app.name, 'app_name': app.name}
    else:
      namespace = {}
    if namespace or app in appmanager.DESKTOP_APPS:
      dynamic_patterns.extend( patterns('', ('^' + re.escape(app.name) + '/', include(app.urls, **namespace))) )
      app.urls_imported = True

static_patterns.append(
    (r'^%s(?P<path>.*)$' % re.escape(settings.STATIC_URL.lstrip('/')),
      'django.views.static.serve',
      { 'document_root': settings.STATIC_ROOT })
)

urlpatterns = patterns('', *static_patterns) + dynamic_patterns

for x in dynamic_patterns:
  logging.debug("Dynamic pattern: %s" % (x,))
for x in static_patterns:
  logging.debug("Static pattern: %s" % (x,))

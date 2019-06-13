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
import debug_toolbar

# FIXME: This could be replaced with hooking into the `AppConfig.ready()`
# signal in Django 1.7:
#
# https://docs.djangoproject.com/en/1.7/ref/applications/#django.apps.AppConfig.ready
#

import desktop.lib.metrics.file_reporter
desktop.lib.metrics.file_reporter.start_file_reporter()

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.static import serve

from desktop import appmanager
from desktop.conf import METRICS, USE_NEW_EDITOR, ENABLE_DJANGO_DEBUG_TOOL, CONNECTORS, ANALYTICS

from desktop.auth import views as desktop_auth_views
from desktop.settings import is_oidc_configured
from desktop import views as desktop_views
from desktop import api as desktop_api
from desktop import api2 as desktop_api2
from notebook import views as notebook_views
from desktop.configuration import api as desktop_configuration_api
from useradmin import views as useradmin_views
from desktop.lib.vcs import api as desktop_lib_vcs_api

# Django expects handler404 and handler500 to be defined.
# django.conf.urls provides them. But we want to override them.
# Also see http://code.djangoproject.com/ticket/5350
handler403 = 'desktop.views.serve_403_error'
handler404 = 'desktop.views.serve_404_error'
handler500 = 'desktop.views.serve_500_error'

admin.autodiscover()

# Some django-wide URLs
dynamic_patterns = [
  url(r'^hue/accounts/login', desktop_auth_views.dt_login, name='desktop_auth_views_dt_login'),
  url(r'^accounts/login/?$', desktop_auth_views.dt_login), # Deprecated
  url(r'^accounts/logout/?$', desktop_auth_views.dt_logout, {'next_page': '/'}),
  url(r'^profile$', desktop_auth_views.profile),
  url(r'^login/oauth/?$', desktop_auth_views.oauth_login),
  url(r'^login/oauth_authenticated/?$', desktop_auth_views.oauth_authenticated),
  url(r'^hue/oidc_failed', desktop_auth_views.oidc_failed),
]

if USE_NEW_EDITOR.get():
  dynamic_patterns += [
    url(r'^home/?$', desktop_views.home2, name='desktop_views_home2'),
    url(r'^home2$', desktop_views.home, name='desktop_views_home'),
    url(r'^home_embeddable$', desktop_views.home_embeddable),
  ]
else:
  dynamic_patterns += [
    url(r'^home$', desktop_views.home, name='desktop_views_home'),
    url(r'^home2$', desktop_views.home2, name='desktop_views_home2')
  ]

dynamic_patterns += [
  url(r'^logs$', desktop_views.log_view, name="desktop.views.log_view"),
  url(r'^desktop/log_analytics$', desktop_views.log_analytics),
  url(r'^desktop/log_js_error$', desktop_views.log_js_error),
  url(r'^desktop/dump_config$', desktop_views.dump_config, name="desktop.views.dump_config"),
  url(r'^desktop/download_logs$', desktop_views.download_log_view),
  url(r'^desktop/get_debug_level', desktop_views.get_debug_level),
  url(r'^desktop/set_all_debug', desktop_views.set_all_debug),
  url(r'^desktop/reset_all_debug', desktop_views.reset_all_debug),
  url(r'^bootstrap.js$', desktop_views.bootstrap), # unused

  url(r'^desktop/status_bar/?$', desktop_views.status_bar),
  url(r'^desktop/debug/is_alive$', desktop_views.is_alive),
  url(r'^desktop/debug/is_idle$', desktop_views.is_idle),
  url(r'^desktop/debug/threads$', desktop_views.threads, name="desktop.views.threads"),
  url(r'^desktop/debug/memory$', desktop_views.memory),
  url(r'^desktop/debug/check_config$', desktop_views.check_config, name="desktop.views.check_config"),
  url(r'^desktop/debug/check_config_ajax$', desktop_views.check_config_ajax),
  url(r'^desktop/log_frontend_event$', desktop_views.log_frontend_event),

  # Mobile
  url(r'^assist_m', desktop_views.assist_m),
  # Hue 4
  url(r'^hue.*/?$', desktop_views.hue, name='desktop_views_hue'),
  url(r'^403$', desktop_views.path_forbidden),
  url(r'^404$', desktop_views.not_found),
  url(r'^500$', desktop_views.server_error),

  # KO components, change to doc?name=ko_editor or similar
  url(r'^ko_editor', desktop_views.ko_editor),
  url(r'^ko_metastore', desktop_views.ko_metastore),

  # JS that needs to be mako
  url(r'^desktop/globalJsConstants.js', desktop_views.global_js_constants),

  url(r'^desktop/topo/(?P<location>\w+)', desktop_views.topo),

  # Web workers
  url(r'^desktop/workers/aceSqlLocationWorker.js', desktop_views.ace_sql_location_worker),
  url(r'^desktop/workers/aceSqlSyntaxWorker.js', desktop_views.ace_sql_syntax_worker),

  # Unsupported browsers
  url(r'^boohoo$', desktop_views.unsupported, name='desktop_views_unsupported'),

  # Top level web page!
  url(r'^$', desktop_views.index, name="desktop_views.index"),
]

dynamic_patterns += [
  # Tags
  url(r'^desktop/api/tag/add_tag$', desktop_api.add_tag),
  url(r'^desktop/api/tag/remove_tag$', desktop_api.remove_tag),
  url(r'^desktop/api/doc/tag$', desktop_api.tag),
  url(r'^desktop/api/doc/update_tags$', desktop_api.update_tags),
  url(r'^desktop/api/doc/get$', desktop_api.get_document),

  # Permissions
  url(r'^desktop/api/doc/update_permissions', desktop_api.update_permissions),
]

dynamic_patterns += [
  url(r'^desktop/api2/doc/open?$', desktop_api2.open_document),  # To keep before get_document
  url(r'^desktop/api2/docs/?$', desktop_api2.search_documents),  # search documents for current user
  url(r'^desktop/api2/doc/?$', desktop_api2.get_document),  # get doc/dir by path or UUID

  url(r'^desktop/api2/doc/move/?$', desktop_api2.move_document),
  url(r'^desktop/api2/doc/mkdir/?$', desktop_api2.create_directory),
  url(r'^desktop/api2/doc/update/?$', desktop_api2.update_document),
  url(r'^desktop/api2/doc/delete/?$', desktop_api2.delete_document),
  url(r'^desktop/api2/doc/copy/?$', desktop_api2.copy_document),
  url(r'^desktop/api2/doc/restore/?$', desktop_api2.restore_document),
  url(r'^desktop/api2/doc/share/?$', desktop_api2.share_document),

  url(r'^desktop/api2/get_config/?$', desktop_api2.get_config),
  url(r'^desktop/api2/context/namespaces/(?P<interface>[\w\-]+)/?$', desktop_api2.get_context_namespaces),
  url(r'^desktop/api2/context/computes/(?P<interface>[\w\-]+)/?$', desktop_api2.get_context_computes),
  url(r'^desktop/api2/context/clusters/(?P<interface>[\w\-]+)/?$', desktop_api2.get_context_clusters),
  url(r'^desktop/api2/user_preferences(?:/(?P<key>\w+))?/?$', desktop_api2.user_preferences, name="desktop.api2.user_preferences"),

  url(r'^desktop/api2/doc/export/?$', desktop_api2.export_documents),
  url(r'^desktop/api2/doc/import/?$', desktop_api2.import_documents),

  url(r'^desktop/api/search/entities/?$', desktop_api2.search_entities),
  url(r'^desktop/api/search/entities_interactive/?$', desktop_api2.search_entities_interactive),
]

dynamic_patterns += [
  url(r'^editor', notebook_views.editor),
]

# Default Configurations
dynamic_patterns += [
  url(r'^desktop/api/configurations/?$', desktop_configuration_api.default_configurations),
  url(r'^desktop/api/configurations/user/?$', desktop_configuration_api.app_configuration_for_user),
  url(r'^desktop/api/configurations/delete/?$', desktop_configuration_api.delete_default_configuration),
]

dynamic_patterns += [
  url(r'^desktop/api/users/autocomplete', useradmin_views.list_for_autocomplete, name='useradmin_views_list_for_autocomplete'),
  url(r'^desktop/api/users/?$', useradmin_views.get_users_by_id)
]

dynamic_patterns += [
  url(r'^desktop/api/vcs/contents/?$', desktop_lib_vcs_api.contents),
  url(r'^desktop/api/vcs/authorize/?$', desktop_lib_vcs_api.authorize),
]

# Metrics specific
if METRICS.ENABLE_WEB_METRICS.get():
  dynamic_patterns += [
    url(r'^desktop/metrics/?', include('desktop.lib.metrics.urls'))
  ]

if CONNECTORS.IS_ENABLED.get():
  dynamic_patterns += [
    url(r'^desktop/connectors/?', include('desktop.lib.connectors.urls'))
  ]

if ANALYTICS.IS_ENABLED.get():
  dynamic_patterns += [
    url(r'^desktop/analytics/?', include('desktop.lib.analytics.urls'))
  ]

dynamic_patterns += [
  url(r'^admin/?', include(admin.site.urls)),
]

static_patterns = []

# SAML specific
if settings.SAML_AUTHENTICATION:
  static_patterns.append(url(r'^saml2/', include('libsaml.urls')))

# OpenId specific
if settings.OPENID_AUTHENTICATION:
    static_patterns.append(url(r'^openid/', include('libopenid.urls')))

if settings.OAUTH_AUTHENTICATION:
  static_patterns.append(url(r'^oauth/', include('liboauth.urls')))

# Root each app at /appname if they have a "urls" module
app_urls_patterns = []
for app in appmanager.DESKTOP_MODULES:
  if app.urls:
    if app.is_url_namespaced:
      namespace = {'namespace': app.name, 'app_name': app.name}
    else:
      namespace = {}
    if namespace or app in appmanager.DESKTOP_APPS:
      app_urls_patterns.append(url('^' + re.escape(app.name) + '/', include(app.urls, **namespace)))
      app.urls_imported = True

static_patterns.append(
    url(r'^%s(?P<path>.*)$' % re.escape(settings.STATIC_URL.lstrip('/')),
      serve,
      { 'document_root': settings.STATIC_ROOT })
)

urlpatterns = []
urlpatterns.extend(dynamic_patterns)
urlpatterns.extend(app_urls_patterns)
urlpatterns.extend(static_patterns)

for x in dynamic_patterns:
  logging.debug("Dynamic pattern: %s" % (x,))
for x in app_urls_patterns:
  logging.debug("Dynamic pattern: %s" % (x,))
for x in static_patterns:
  logging.debug("Static pattern: %s" % (x,))

if settings.DEBUG and ENABLE_DJANGO_DEBUG_TOOL.get():
  urlpatterns += [
    url(r'^__debug__/', include(debug_toolbar.urls)),
  ]

if is_oidc_configured():
  urlpatterns += [
    url(r'^oidc/', include('mozilla_django_oidc.urls')),
  ]

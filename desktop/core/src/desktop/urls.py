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
import sys


# FIXME: This could be replaced with hooking into the `AppConfig.ready()`
# signal in Django 1.7:
#
# https://docs.djangoproject.com/en/1.7/ref/applications/#django.apps.AppConfig.ready
#

import desktop.lib.metrics.file_reporter
desktop.lib.metrics.file_reporter.start_file_reporter()

from django.conf import settings
from django.views.static import serve
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from notebook import views as notebook_views
from useradmin import views as useradmin_views

from desktop import appmanager

from desktop import views as desktop_views
from desktop import api as desktop_api
from desktop import api2 as desktop_api2
from desktop import api_public_urls_v1
from desktop.auth import views as desktop_auth_views
from desktop.conf import METRICS, USE_NEW_EDITOR, ANALYTICS, has_connectors, ENABLE_PROMETHEUS, SLACK
from desktop.configuration import api as desktop_configuration_api
from desktop.lib.vcs import api as desktop_lib_vcs_api
from desktop.settings import is_oidc_configured

if sys.version_info[0] > 2:
  from django.urls import include, re_path
else:
  from django.conf.urls import include, url as re_path

# Django expects handler404 and handler500 to be defined.
# django.conf.urls provides them. But we want to override them.
# Also see http://code.djangoproject.com/ticket/5350
handler403 = 'desktop.views.serve_403_error'
handler404 = 'desktop.views.serve_404_error'
handler500 = 'desktop.views.serve_500_error'


# Some django-wide URLs
dynamic_patterns = [
  re_path(r'^hue/accounts/login', desktop_auth_views.dt_login, name='desktop_auth_views_dt_login'),
  re_path(r'^hue/accounts/logout/?$', desktop_auth_views.dt_logout, {'next_page': '/'}),
  re_path(r'^accounts/login/?$', desktop_auth_views.dt_login), # Deprecated
  re_path(r'^accounts/logout/?$', desktop_auth_views.dt_logout, {'next_page': '/'}),
  re_path(r'^profile$', desktop_auth_views.profile),
  re_path(r'^login/oauth/?$', desktop_auth_views.oauth_login),
  re_path(r'^login/oauth_authenticated/?$', desktop_auth_views.oauth_authenticated),
  re_path(r'^hue/oidc_failed', desktop_auth_views.oidc_failed),
]

if USE_NEW_EDITOR.get():
  dynamic_patterns += [
    re_path(r'^home/?$', desktop_views.home2, name='desktop_views_home2'),
    re_path(r'^home2$', desktop_views.home, name='desktop_views_home'),
    re_path(r'^home_embeddable$', desktop_views.home_embeddable),
  ]
else:
  dynamic_patterns += [
    re_path(r'^home$', desktop_views.home, name='desktop_views_home'),
    re_path(r'^home2$', desktop_views.home2, name='desktop_views_home2')
  ]

dynamic_patterns += [
  re_path(r'^logs$', desktop_views.log_view, name="desktop.views.log_view"),
  re_path(r'^desktop/log_analytics$', desktop_views.log_analytics),
  re_path(r'^desktop/log_js_error$', desktop_views.log_js_error),
  re_path(r'^desktop/dump_config$', desktop_views.dump_config, name="desktop.views.dump_config"),
  re_path(r'^desktop/download_logs$', desktop_views.download_log_view),
  re_path(r'^desktop/get_debug_level', desktop_views.get_debug_level),
  re_path(r'^desktop/set_all_debug', desktop_views.set_all_debug),
  re_path(r'^desktop/reset_all_debug', desktop_views.reset_all_debug),
  re_path(r'^bootstrap.js$', desktop_views.bootstrap), # unused

  re_path(r'^desktop/status_bar/?$', desktop_views.status_bar),
  re_path(r'^desktop/debug/is_alive$', desktop_views.is_alive),
  re_path(r'^desktop/debug/is_idle$', desktop_views.is_idle),
  re_path(r'^desktop/debug/threads$', desktop_views.threads, name="desktop.views.threads"),
  re_path(r'^desktop/debug/memory$', desktop_views.memory),
  re_path(r'^desktop/debug/check_config$', desktop_views.check_config, name="desktop.views.check_config"),
  re_path(r'^desktop/debug/check_config_ajax$', desktop_views.check_config_ajax),
  re_path(r'^desktop/log_frontend_event$', desktop_views.log_frontend_event),

  # Catch-up gist
  re_path(r'^hue/gist/?$', desktop_api2.gist_get),

  # Mobile
  re_path(r'^assist_m', desktop_views.assist_m),

  # Hue 4
  re_path(r'^hue.*/?$', desktop_views.hue, name='desktop_views_hue'),
  re_path(r'^403$', desktop_views.path_forbidden),
  re_path(r'^404$', desktop_views.not_found),
  re_path(r'^500$', desktop_views.server_error),

  # KO components, change to doc?name=ko_editor or similar
  re_path(r'^ko_editor', desktop_views.ko_editor),
  re_path(r'^ko_metastore', desktop_views.ko_metastore),

  # JS that needs to be mako
  re_path(r'^desktop/globalJsConstants.js', desktop_views.global_js_constants),

  re_path(r'^desktop/topo/(?P<location>\w+)', desktop_views.topo),

  # Web workers
  re_path(r'^desktop/workers/aceSqlLocationWorker.js', desktop_views.ace_sql_location_worker),
  re_path(r'^desktop/workers/aceSqlSyntaxWorker.js', desktop_views.ace_sql_syntax_worker),

  re_path(r'^dynamic_bundle/(?P<config>\w+)/(?P<bundle_name>.+)', desktop_views.dynamic_bundle),

  # Unsupported browsers
  re_path(r'^boohoo$', desktop_views.unsupported, name='desktop_views_unsupported'),

  # Top level web page!
  re_path(r'^$', desktop_views.index, name="desktop_views.index"),
]

dynamic_patterns += [
  # Tags
  re_path(r'^desktop/api/tag/add_tag$', desktop_api.add_tag),
  re_path(r'^desktop/api/tag/remove_tag$', desktop_api.remove_tag),
  re_path(r'^desktop/api/doc/tag$', desktop_api.tag),
  re_path(r'^desktop/api/doc/update_tags$', desktop_api.update_tags),
  re_path(r'^desktop/api/doc/get$', desktop_api.get_document),

  # Permissions
  re_path(r'^desktop/api/doc/update_permissions', desktop_api.update_permissions),
]

dynamic_patterns += [
  re_path(r'^desktop/api2/doc/open?$', desktop_api2.open_document),  # To keep before get_document
  re_path(r'^desktop/api2/docs/?$', desktop_api2.search_documents),  # search documents for current user
  re_path(r'^desktop/api2/doc/?$', desktop_api2.get_document),  # get doc/dir by path or UUID

  re_path(r'^desktop/api2/doc/move/?$', desktop_api2.move_document),
  re_path(r'^desktop/api2/doc/mkdir/?$', desktop_api2.create_directory),
  re_path(r'^desktop/api2/doc/update/?$', desktop_api2.update_document),
  re_path(r'^desktop/api2/doc/delete/?$', desktop_api2.delete_document),
  re_path(r'^desktop/api2/doc/copy/?$', desktop_api2.copy_document),
  re_path(r'^desktop/api2/doc/restore/?$', desktop_api2.restore_document),
  re_path(r'^desktop/api2/doc/share/link/?$', desktop_api2.share_document_link),
  re_path(r'^desktop/api2/doc/share/?$', desktop_api2.share_document),

  re_path(r'^desktop/api2/get_config/?$', desktop_api2.get_config),
  re_path(r'^desktop/api2/get_hue_config/?$', desktop_api2.get_hue_config),
  re_path(r'^desktop/api2/context/namespaces/(?P<interface>[\w\-]+)/?$', desktop_api2.get_context_namespaces),
  re_path(r'^desktop/api2/context/computes/(?P<interface>[\w\-]+)/?$', desktop_api2.get_context_computes),
  re_path(r'^desktop/api2/context/clusters/(?P<interface>[\w\-]+)/?$', desktop_api2.get_context_clusters),
  re_path(r'^desktop/api2/user_preferences(?:/(?P<key>\w+))?/?$', desktop_api2.user_preferences, name="desktop.api2.user_preferences"),

  re_path(r'^desktop/api2/doc/export/?$', desktop_api2.export_documents),
  re_path(r'^desktop/api2/doc/import/?$', desktop_api2.import_documents),

  re_path(r'^desktop/api2/gist/create/?$', desktop_api2.gist_create),
  re_path(r'^desktop/api2/gist/open/?$', desktop_api2.gist_get),


  re_path(r'^desktop/api/search/entities/?$', desktop_api2.search_entities),
  re_path(r'^desktop/api/search/entities_interactive/?$', desktop_api2.search_entities_interactive),
]

dynamic_patterns += [
  re_path(r'^editor', notebook_views.editor),
]

# Default Configurations
dynamic_patterns += [
  re_path(r'^desktop/api/configurations/?$', desktop_configuration_api.default_configurations),
  re_path(r'^desktop/api/configurations/user/?$', desktop_configuration_api.app_configuration_for_user),
  re_path(r'^desktop/api/configurations/delete/?$', desktop_configuration_api.delete_default_configuration),
]

dynamic_patterns += [
  re_path(r'^desktop/api/users/autocomplete', useradmin_views.list_for_autocomplete, name='useradmin_views_list_for_autocomplete'),
  re_path(r'^desktop/api/users/?$', useradmin_views.get_users_by_id)
]

dynamic_patterns += [
  re_path('^api/v1/token/auth/?$', TokenObtainPairView.as_view(), name='token_obtain'),
  re_path('^api/v1/token/verify/?$', TokenVerifyView.as_view(), name='token_verify'),
  re_path('^api/v1/token/refresh/?$', TokenRefreshView.as_view(), name='token_refresh'),

  re_path(r'^api/v1/', include(('desktop.api_public_urls_v1', 'api'), 'api')),
]

dynamic_patterns += [
  re_path(r'^desktop/api/vcs/contents/?$', desktop_lib_vcs_api.contents),
  re_path(r'^desktop/api/vcs/authorize/?$', desktop_lib_vcs_api.authorize),
]

if METRICS.ENABLE_WEB_METRICS.get():
  dynamic_patterns += [
    re_path(r'^desktop/metrics/?', include('desktop.lib.metrics.urls'))
  ]

dynamic_patterns += [
  re_path(r'^desktop/connectors/?', include('desktop.lib.connectors.urls'))
]

if ANALYTICS.IS_ENABLED.get():
  dynamic_patterns += [
    re_path(r'^desktop/analytics/?', include('desktop.lib.analytics.urls'))
  ]

dynamic_patterns += [
  re_path(r'^scheduler/', include('desktop.lib.scheduler.urls'))
]

if ENABLE_PROMETHEUS.get():
  dynamic_patterns += [
    re_path('', include('django_prometheus.urls')),
  ]


static_patterns = []

# SAML specific
if settings.SAML_AUTHENTICATION:
  static_patterns.append(re_path(r'^saml2/', include('libsaml.urls')))


if settings.OAUTH_AUTHENTICATION:
  static_patterns.append(re_path(r'^oauth/', include('liboauth.urls')))

# Root each app at /appname if they have a "urls" module
app_urls_patterns = []
for app in appmanager.DESKTOP_MODULES:
  if app.urls:
    if app.is_url_namespaced:
      namespace = app.name
    else:
      namespace = None
    if namespace or app in appmanager.DESKTOP_APPS:
      app_urls_patterns.append(re_path('^' + re.escape(app.name) + '/', include((app.urls, app.name), namespace=namespace)))
      app.urls_imported = True

static_patterns.append(
    re_path(r'^%s(?P<path>.*)$' % re.escape(settings.STATIC_URL.lstrip('/')),
      serve,
      {'document_root': settings.STATIC_ROOT})
)

urlpatterns = []
urlpatterns.extend(dynamic_patterns)
urlpatterns.extend(app_urls_patterns)
urlpatterns.extend(static_patterns)

if is_oidc_configured():
  urlpatterns += [
    re_path(r'^oidc/', include('mozilla_django_oidc.urls')),
  ]

# Slack botserver URLs
if SLACK.IS_ENABLED.get():
  urlpatterns += [
    re_path(r'^desktop/slack/', include('desktop.lib.botserver.urls')),
  ]

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
import os
import re

from django.conf import settings
from django.conf.urls.defaults import include, patterns
from django.contrib import admin

from desktop import appmanager

# Django expects handler404 and handler500 to be defined.
# django.conf.urls.defaults provides them. But we want to override them.
# Also see http://code.djangoproject.com/ticket/5350
handler404 = 'desktop.views.serve_404_error'
handler500 = 'desktop.views.serve_500_error'


# Set up /appname/static mappings for any apps that have static directories
def static_pattern(urlprefix, root):
  """
  First argument is the url mapping, and second argument is the
  directory to serve.
  """
  return (r'^%s/(?P<path>.*)$' % urlprefix, 'django.views.static.serve', { 'document_root': root, 'show_indexes': False })


admin.autodiscover()

# Some django-wide URLs
dynamic_patterns = patterns('desktop.auth.views',
  (r'^accounts/login/$', 'dt_login'),
  (r'^accounts/logout/$', 'dt_logout', {'next_page': '/'}),
  (r'^profile$', 'profile'),
  (r'^login/oauth/?$', 'oauth_login'),
  (r'^login/oauth_authenticated/?$', 'oauth_authenticated'),
)

dynamic_patterns += patterns('desktop.views',
  (r'^logs$','log_view'),
  (r'^home$','home'),
  (r'^desktop/dump_config$','dump_config'),
  (r'^desktop/download_logs$','download_log_view'),
  (r'^bootstrap.js$', 'bootstrap'), # unused

  (r'^desktop/prefs/(?P<key>\w+)?$', 'prefs'),
  (r'^desktop/status_bar/?$', 'status_bar'),
  (r'^desktop/debug/is_alive$','is_alive'),
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

dynamic_patterns += patterns('useradmin.views',
  (r'^desktop/api/users/autocomplete', 'list_for_autocomplete'),
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
  static_patterns.append(static_pattern("liboauth_static",
        os.path.join(os.path.dirname(__file__), "..", '..', '..', "libs/liboauth/src/liboauth/static/")))

# Add indexer app
if 'search' in [app.name for app in appmanager.DESKTOP_APPS]:
  namespace = {'namespace': 'indexer', 'app_name': 'indexer'}
  dynamic_patterns.extend( patterns('', ('^indexer/', include('indexer.urls', **namespace))) )
  static_patterns.append(static_pattern('indexer/static',
                                        os.path.join(os.path.dirname(__file__), "..", '..', '..', "libs/indexer/static/")))

# Root each app at /appname if they have a "urls" module
for app in appmanager.DESKTOP_APPS:
  if app.urls:
    if app.is_url_namespaced:
      namespace = {'namespace': app.name, 'app_name': app.name}
    else:
      namespace = {}
    dynamic_patterns.extend( patterns('', ('^' + re.escape(app.name) + '/', include(app.urls, **namespace))) )
    app.urls_imported = True

  # Root a /appname/static if they have a static dir
  if app.static_dir:
    static_patterns.append(
      static_pattern('%s/static' % app.name, app.static_dir))

# TODO this stuff should probably be moved into a "ui" lib or such so it
# is autodiscovered
def buildpath(d):
  return os.path.join(os.path.dirname(__file__), "..", '..', '..', d)
static_patterns.append(static_pattern("static", buildpath("core/static")))
static_patterns.append((r'^(?P<path>favicon.ico)$',
                        'django.views.static.serve',
                        { 'document_root': buildpath('core/static/art') }))

urlpatterns = patterns('', *static_patterns) + dynamic_patterns

for x in dynamic_patterns:
  logging.debug("Dynamic pattern: %s" % (x,))
for x in static_patterns:
  logging.debug("Static pattern: %s" % (x,))

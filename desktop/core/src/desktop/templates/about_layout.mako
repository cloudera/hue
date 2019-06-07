## Licensed to Cloudera, Inc. under one
## or more contributor license agreements.  See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  Cloudera, Inc. licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.

<%!
from django.utils.translation import ugettext as _

from desktop.auth.backend import is_admin
from desktop.conf import METRICS, CONNECTORS, ANALYTICS

def is_selected(section, matcher):
  if section == matcher:
    return "active"
  else:
    return ""
%>

<%def name="menubar(section='')">
  <div class="navbar hue-title-bar">
      <div class="navbar-inner">
        <div class="container-fluid">
          <div class="nav-collapse">
            <ul class="nav">
              <li class="app-header">
                <a href="${ url('about:admin_wizard') }">
                  <img src="${ static('desktop/art/icon_hue_48.png') }" class="app-icon"  alt="${ _('Hue icon') }"/>
                  ${ _('About Hue') }
                </a>
               </li>
              % if is_admin(user):
                <li class="${is_selected(section, 'quick_start')}">
                  <a href="${ url('about:admin_wizard') }">${_('Quick start')}</a>
                </li>
                <li class="${is_selected(section, 'dump_config')}">
                  <a href="${ url('desktop.views.dump_config') }">${_('Configuration')}</a>
                </li>
                % if CONNECTORS.IS_ENABLED.get():
                <li class="${is_selected(section, 'connectors')}">
                  <a href="${ url('desktop.lib.connectors.views.index') }">${_('Connectors')}</a>
                </li>
                % endif
                % if ANALYTICS.IS_ENABLED.get():
                <li class="${is_selected(section, 'analytics')}">
                  <a href="${ url('desktop.lib.analytics.views.index') }">${_('Analytics')}</a>
                </li>
                % endif
                <li class="${is_selected(section, 'log_view')}">
                  <a href="${ url('desktop.views.log_view') }">${_('Server Logs')}</a>
                </li>
                <li class="${is_selected(section, 'threads')}">
                  <a href="${ url('desktop.views.threads') }">${_('Threads')}</a>
                </li>
                % if METRICS.ENABLE_WEB_METRICS.get():
                <li class="${is_selected(section, 'metrics')}">
                  <a href="${ url('desktop.lib.metrics.views.index') }">${_('Metrics')}</a>
                </li>
                % endif
              % endif
            </ul>
          </div>
        </div>
      </div>
  </div>
</%def>

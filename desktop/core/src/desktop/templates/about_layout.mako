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
##
##
## no spaces in this method please; we're declaring a CSS class, and ART uses this value for stuff, and it splits on spaces, and
## multiple spaces and line breaks cause issues
<%!
from django.utils.translation import ugettext as _

def is_selected(section, matcher):
  if section == matcher:
    return "active"
  else:
    return ""
%>

<%def name="menubar(section='')">
  <div class="navbar navbar-inverse navbar-fixed-top">
      <div class="navbar-inner">
        <div class="container-fluid">
          <div class="nav-collapse">
            <ul class="nav">
              <li class="currentApp">
                <a href="/about">
                  <img src="${ static('desktop/art/icon_hue_48.png') }" class="app-icon" />
                  ${ _('About Hue') }
                </a>
               </li>
              % if user.is_superuser:
                <li class="${is_selected(section, 'quick_start')}"><a href="${url("about:admin_wizard")}">${_('Quick start')}</a></li>
                <li class="${is_selected(section, 'dump_config')}"><a href="${url("desktop.views.dump_config")}">${_('Configuration')}</a></li>
                <li class="${is_selected(section, 'log_view')}"><a href="${url("desktop.views.log_view")}">${_('Server Logs')}</a></li>
              % endif
            </ul>
          </div>
        </div>
      </div>
  </div>
</%def>

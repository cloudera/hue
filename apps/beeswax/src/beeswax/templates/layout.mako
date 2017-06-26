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
                <a href="/${app_name}">
                % if app_name == 'impala':
                  <img src="${ static('impala/art/icon_impala_48.png') }" class="app-icon" alt="${ _('Impala icon') }" />
                  Impala
                % elif app_name == 'rdbms':
                  <img src="${ static('rdbms/art/icon_rdbms_48.png') }" class="app-icon" alt="${ _('DBQuery icon') }" />
                  DB Query
                % else:
                  <img src="${ static('beeswax/art/icon_beeswax_48.png') }" class="app-icon" alt="${ _('Beeswax icon') }" />
                  Hive Editor
                % endif
                </a>
              </li>
              <li class="${is_selected(section, 'query')}"><a href="${ url(app_name + ':execute_query') }">${_('Query Editor')}</a></li>
              <li class="${is_selected(section, 'my queries')}"><a href="${ url(app_name + ':my_queries') }">${_('My Queries')}</a></li>
              <li class="${is_selected(section, 'saved queries')}"><a href="${ url(app_name + ':list_designs') }">${_('Saved Queries')}</a></li>
              <li class="${is_selected(section, 'history')}"><a href="${ url(app_name + ':list_query_history') }">${_('History')}</a></li>
            </ul>
          </div>
        </div>
      </div>
  </div>
</%def>

<%def name="metastore_menubar()">
  <div class="navbar hue-title-bar">
      <div class="navbar-inner">
        <div class="container-fluid">
          <div class="nav-collapse">
            <ul class="nav">
              <li class="app-header">
                <a href="/metastore">
                  <img src="${ static('metastore/art/icon_metastore_48.png') }" class="app-icon" alt="${ _('Metastore icon') }" />
                  ${ _('Metastore Manager') }
                </a>
              </li>
            </ul>
          </div>
        </div>
      </div>
  </div>
</%def>


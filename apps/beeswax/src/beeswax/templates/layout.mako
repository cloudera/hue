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
  % if app_name == 'spark':
  ## Duplication from spark common.mako!
  <div class="navbar navbar-inverse navbar-fixed-top">
    <div class="navbar-inner">
      <div class="container-fluid">
        <div class="nav-collapse">
          <ul class="nav">
            <li class="currentApp">
              <a href="/spark">
                <img src="/spark/static/art/icon_spark_24.png" />
                ${ _('Spark Igniter') }
              </a>
            </li>
            <li class="${is_selected(section, 'query')}"><a href="${ url('spark:editor') }">${_('Editor')}</a></li>
            ##<li class="${is_selected(section, 'my queries')}"><a href="${ url(app_name + ':my_queries') }">${_('My Queries')}</a></li>
            <li class="${is_selected(section, 'saved queries')}"><a href="${ url('spark:list_designs') }">${_('Applications')}</a></li>
            ##<li class="${is_selected(section, 'history')}"><a href="${ url('spark:list_query_history') }">${_('History')}</a></li>
            <li class="${is_selected(section, 'jobs')}"><a href="${ url('spark:list_jobs') }">${_('Dashboard')}</a></li>
            <li class="${is_selected(section, 'contexts')}"><a href="${ url('spark:list_contexts') }">${_('Contexts')}</a></li>
            <li class="${is_selected(section, 'applications')}"><a href="${ url('spark:list_applications') }">${_('Uploads')}</a></li>
          </ul>
        </div>
      </div>
    </div>
  </div>
  % else:
  <div class="navbar navbar-inverse navbar-fixed-top">
      <div class="navbar-inner">
        <div class="container-fluid">
          <div class="nav-collapse">
            <ul class="nav">
              <li class="currentApp">
                <a href="/${app_name}">
                % if app_name == 'impala':
                  <img src="/impala/static/art/icon_impala_24.png" />
                  Impala
                % elif app_name == 'rdbms':
                  <img src="/rdbms/static/art/icon_rdbms_24.png" />
                  DB Query
                % else:
                  <img src="/beeswax/static/art/icon_beeswax_24.png" />
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
  % endif
</%def>

<%def name="metastore_menubar()">
  <div class="navbar navbar-inverse navbar-fixed-top">
      <div class="navbar-inner">
        <div class="container-fluid">
          <div class="nav-collapse">
            <ul class="nav">
              <li class="currentApp">
                <a href="/metastore">
                  <img src="/metastore/static/art/icon_metastore_24.png" />
                  ${ _('Metastore Manager') }
                </a>
              </li>
            </ul>
          </div>
        </div>
      </div>
  </div>
</%def>


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

<%! from django.utils.translation import ugettext as _ %>

<%!
def is_selected(section, matcher):
  if section == matcher:
    return "active"
  else:
    return ""
%>

<%def name="navbar(section='editor')">
  <div class="navbar navbar-inverse navbar-fixed-top">
    <div class="navbar-inner">
      <div class="container-fluid">
        <div class="nav-collapse">
          <ul class="nav">
            <li class="currentApp">
              <a href="/spark">
                <img src="/spark/static/art/icon_spark_24.png" />
                ${ _('Spark Editor') }
              </a>
            </li>
            <li class="${is_selected(section, 'query')}"><a href="${ url('spark:editor') }">${_('Query Editor')}</a></li>
            ##<li class="${is_selected(section, 'my queries')}"><a href="${ url(app_name + ':my_queries') }">${_('My Queries')}</a></li>
            <li class="${is_selected(section, 'queries')}"><a href="${ url('spark:list_designs') }">${_('Queries')}</a></li>
            <li class="${is_selected(section, 'history')}"><a href="${ url('spark:list_query_history') }">${_('History')}</a></li>
            <li class="currentApp">
              <a href="/spark">
                ${ _('Browser') }
              </a>
            </li>
            <li class="${is_selected(section, 'jobs')}"><a href="${ url('spark:list_jobs') }">${_('Jobs')}</a></li>
            <li class="${is_selected(section, 'contexts')}"><a href="${ url('spark:list_contexts') }">${_('Contexts')}</a></li>
            <li class="${is_selected(section, 'jars')}"><a href="${ url('spark:list_jars') }">${_('Jars')}</a></li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</%def>

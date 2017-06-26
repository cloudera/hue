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

<%def name="navbar()">
  <div class="navbar hue-title-bar">
    <div class="navbar-inner">
      <div class="container-fluid">
        <div class="nav-collapse">
          <ul class="nav">
            <li class="app-header">
              <a href="/rdbms">
                <img src="${ static('rdbms/art/icon_rdbms_48.png') }" class="app-icon" alt="${ _('DBQuery icon') }" />
                ${ _('DB Query') }
              </a>
            </li>
            <li class="active"><a href="${ url('rdbms:execute_query') }">${_('Query Editor')}</a></li>
            <li><a href="${ url('rdbms:my_queries') }">${_('My Queries')}</a></li>
            <li><a href="${ url('rdbms:list_designs') }">${_('Saved Queries')}</a></li>
            <li><a href="${ url('rdbms:list_query_history') }">${_('History')}</a></li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</%def>

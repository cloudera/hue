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
%>

<%namespace name="utils" file="utils.inc.mako" />


<%def name="menubar(section='')">
  <ul class="nav nav-tabs">
    <li class="${ utils.is_selected(section, 'search') }">
      <a href="${ url('search:index') }">${ _('Search') }</a>
    </li>
    <li class="${ utils.is_selected(section, 'cores') }">
      <a href="${ url('search:admin_cores') }">${ _('Cores') }</a>
    </li>
    <li class="${ utils.is_selected(section, 'settings') }">
      <a href="${ url('search:admin_settings') }">${ _('Settings') }</a>
    </li>
  </ul>
</%def>

<%def name="sub_menubar(core, section='')">
  <ul class="nav nav-pills">
    <li class="${ utils.is_selected(section, 'properties') }">
      <a href="${ url('search:admin_core', core=core) }">${ _('Properties') }</a>
    </li>
    <li class="${ utils.is_selected(section, 'result') }">
      <a href="${ url('search:admin_core_result', core=core) }">${ _('Result') }</a>
    </li>
    <li class="${ utils.is_selected(section, 'facets') }">
      <a href="${ url('search:admin_core_facets', core=core) }">${ _('Facets') }</a>
    </li>
    <li class="${ utils.is_selected(section, 'sorting') }">
      <a href="${ url('search:admin_core_sorting', core=core) }">${ _('Sorting') }</a>
    </li>
  </ul>
</%def>

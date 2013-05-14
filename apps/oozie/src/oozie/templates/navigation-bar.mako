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
  <div class="subnav subnav-fixed">
    <div class="container-fluid">
      <ul class="nav nav-pills">
        <li class="${utils.is_selected(section, 'dashboard')}"><a href="${url('oozie:list_oozie_workflows')}">${ _('Dashboard') }</a></li>
        <li class="${utils.is_selected(section, 'workflows')}"><a href="${url('oozie:list_workflows')}">${ _('Workflows') }</a></li>
        <li class="${utils.is_selected(section, 'coordinators')}"><a href="${url('oozie:list_coordinators')}">${ _('Coordinators') }</a></li>
        <li class="${utils.is_selected(section, 'bundles')}"><a href="${url('oozie:list_bundles')}">${ _('Bundles') }</a></li>
      </ul>
    </div>
  </div>
</%def>

<%def name="dashboard_sub_menubar(section='')">
  <h1>${ _('Dashboard') }</h1>

  <ul class="nav nav-tabs">
    <li class="${utils.is_selected(section, 'workflows')}"><a href="${url('oozie:list_oozie_workflows')}">${ _('Workflows') }</a></li>
    <li class="${utils.is_selected(section, 'coordinators')}"><a href="${url('oozie:list_oozie_coordinators')}">${ _('Coordinators') }</a></li>
    <li class="${utils.is_selected(section, 'bundles')}"><a href="${url('oozie:list_oozie_bundles')}">${ _('Bundles') }</a></li>
    <li class="${utils.is_selected(section, 'oozie')}"><a href="${url('oozie:list_oozie_info')}">${ _('Oozie') }</a></li>
  </ul>
</%def>


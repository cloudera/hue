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
  from oozie.conf import ENABLE_V2
%>

<%namespace name="utils" file="utils.inc.mako" />


<%def name="menubar(section='', dashboard=False, is_editor=False)">
    <div class="navbar navbar-inverse navbar-fixed-top">
      <div class="navbar-inner">
        <div class="container-fluid">
          <div class="nav-collapse">
            <ul class="nav">
              <li class="currentApp">
                <a href="/${app_name}">
                  % if dashboard:
                    <img src="/oozie/static/art/icon_oozie_dashboard_48.png" class="app-icon" />
                  % else:
                    <img src="/oozie/static/art/icon_oozie_editor_48.png" class="app-icon" />
                  % endif
                  ${ _('Oozie Dashboard') if dashboard else _('Oozie Editor') }
                </a>
               </li>
              % if dashboard:
                <li class="${utils.is_selected(section, 'workflows')}"><a href="${url('oozie:list_oozie_workflows')}">${ _('Workflows') }</a></li>
                <li class="${utils.is_selected(section, 'coordinators')}"><a href="${url('oozie:list_oozie_coordinators')}">${ _('Coordinators') }</a></li>
                <li class="${utils.is_selected(section, 'bundles')}"><a href="${url('oozie:list_oozie_bundles')}">${ _('Bundles') }</a></li>
                <li class="${utils.is_selected(section, 'sla')}"><a href="${url('oozie:list_oozie_sla')}">${ _('SLA') }</a></li>
                <li class="${utils.is_selected(section, 'oozie')}"><a href="${url('oozie:list_oozie_info')}">${ _('Oozie') }</a></li>
              % else:
                % if is_editor:
                  <li class="${utils.is_selected(section, 'workflows')}"><a href="${url('oozie:list_editor_workflows')}">${ _('Workflows') }</a></li>
                  <li class="${utils.is_selected(section, 'coordinators')}"><a href="${url('oozie:list_editor_coordinators')}">${ _('Coordinators') }</a></li>
                  <li class="${utils.is_selected(section, 'bundles')}"><a href="${url('oozie:list_editor_bundles')}">${ _('Bundles') }</a></li>
                % else:
                  <li class="${utils.is_selected(section, 'workflows')}"><a href="${url('oozie:list_workflows')}">${ _('Workflows') }</a></li>
                  <li class="${utils.is_selected(section, 'coordinators')}"><a href="${url('oozie:list_coordinators')}">${ _('Coordinators') }</a></li>
                  <li class="${utils.is_selected(section, 'bundles')}"><a href="${url('oozie:list_bundles')}">${ _('Bundles') }</a></li>

                  % if ENABLE_V2.get():
                    <li class="inline alert alert-warn" style="margin-left:20px; margin-bottom:0px; margin-top:4px">
                      ${ _('This is the old editor, please migrate your jobs to the ') } <a style="display:inline" href="${url('oozie:list_editor_workflows') if utils.is_selected(section, 'workflows') else url('oozie:list_editor_coordinators') if utils.is_selected(section, 'coordinators') else url('oozie:list_editor_bundles')}">${ _('new editor.') }</a>
                    </li>
                  % endif
                % endif
              % endif
            </ul>
          </div>
        </div>
      </div>
  </div>
</%def>


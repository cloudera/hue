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


<%def name="menubar(section='', dashboard=False, is_editor=False, pullright=None, is_embeddable=False)">
    <div class="navbar hue-title-bar">
      <div class="navbar-inner">
        <div class="container-fluid">
          %if pullright:
            ${pullright()}
          %endif
          <div class="nav-collapse">
            <ul class="nav">
              <li class="app-header">
                <%def name="getInterpreter(section)"><%
                  if section == 'coordinators':
                    return 'oozie-coordinator'
                  elif section == 'bundles':
                    return 'oozie-bundle'
                  else:
                    return 'oozie-workflow'
                %></%def>
                <%def name="getURL(section, dashboard, is_v2)">
                <%
                  if dashboard:
                    if is_v2:
                      if section == 'coordinators':
                        return url('oozie:list_editor_coordinators')
                      elif section == 'bundles':
                        return url('oozie:list_editor_bundles')
                      else:
                        return url('oozie:list_editor_workflows')
                    else:
                      if section == 'coordinators':
                        return url('oozie:list_coordinators')
                      elif section == 'bundles':
                        return url('oozie:list_bundles')
                      else:
                        return url('oozie:list_workflows')
                  else:
                    if section == 'coordinators':
                      return url('oozie:list_oozie_coordinators')
                    elif section == 'bundles':
                      return url('oozie:list_oozie_bundles')
                    else:
                      return url('oozie:list_oozie_workflows')
                %>
              </%def>

                % if dashboard:
                <a title="${ _('Switch to the editor') }" href="${getURL(section, dashboard, ENABLE_V2.get())}">
                  <img src="${ static('oozie/art/icon_oozie_dashboard_48.png') }" class="app-icon" alt="${ _('Oozie dashboard icon') }" /> ${ _('Oozie Dashboard') }
                </a>
                % else:
                <a title="${ _('Switch to the dashboard') }" href="${ is_embeddable and '/hue/jobbrowser/#!workflows' or getURL(section, dashboard, ENABLE_V2.get())}">
                  <svg class="svg-app-icon"><use xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="#hi-oozie"></use></svg> ${ _('Oozie Editor') }
                  <!-- ko component: { name: 'hue-favorite-app', params: { app: 'scheduler', interpreter: '${ getInterpreter(section) }' }} --><!-- /ko -->
                </a>
                % endif
               </li>
              % if dashboard:
                <li class="${utils.is_selected(section, 'workflows')}"><a href="${url('oozie:list_oozie_workflows')}">${ _('Workflows') }</a></li>
                <li class="${utils.is_selected(section, 'coordinators')}"><a href="${url('oozie:list_oozie_coordinators')}">${ _('Coordinators') }</a></li>
                <li class="${utils.is_selected(section, 'bundles')}"><a href="${url('oozie:list_oozie_bundles')}">${ _('Bundles') }</a></li>
                <li class="${utils.is_selected(section, 'sla')}"><a href="${url('oozie:list_oozie_sla')}">${ _('SLA') }</a></li>
                <li class="${utils.is_selected(section, 'oozie')}"><a href="${url('oozie:list_oozie_info')}">${ _('Oozie') }</a></li>
              % else:
                % if not is_embeddable:
                  % if is_editor:
                    <li class="${utils.is_selected(section, 'workflows')}"><a href="${url('oozie:list_editor_workflows')}">${ _('Workflows') }</a></li>
                    <li class="${utils.is_selected(section, 'coordinators')}"><a href="${url('oozie:list_editor_coordinators')}">${ _('Coordinators') }</a></li>
                    <li class="${utils.is_selected(section, 'bundles')}"><a href="${url('oozie:list_editor_bundles')}">${ _('Bundles') }</a></li>
                  % else:
                    <li class="${utils.is_selected(section, 'workflows')}"><a href="${url('oozie:list_workflows')}">${ _('Workflows') }</a></li>
                    <li class="${utils.is_selected(section, 'coordinators')}"><a href="${url('oozie:list_coordinators')}">${ _('Coordinators') }</a></li>
                    <li class="${utils.is_selected(section, 'bundles')}"><a href="${url('oozie:list_bundles')}">${ _('Bundles') }</a></li>
                  % endif
                % endif
              % endif
            </ul>
          </div>
        </div>
      </div>
  </div>
  % if not dashboard and not is_editor and ENABLE_V2.get():
    <div class="alert alert-warn" style="position: fixed; top: 28px; z-index: 1031; right: 0; height: 28px; line-height: 28px; border: none">
      ${ _('This is the old editor, please migrate your jobs to the ') }
      <a style="display:inline" href="${url('oozie:new_workflow') if utils.is_selected(section, 'workflows') else url('oozie:new_coordinator') if utils.is_selected(section, 'coordinators') else url('oozie:new_bundle')}">${ _('new editor.') }</a>
    </div>
  % endif
</%def>


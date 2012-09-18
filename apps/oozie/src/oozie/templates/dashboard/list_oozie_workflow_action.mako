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
  from desktop.views import commonheader, commonfooter
  from django.utils.translation import ugettext as _
%>

<%namespace name="layout" file="../navigation-bar.mako" />
<%namespace name="utils" file="../utils.inc.mako" />

${ commonheader(_("Oozie App"), "oozie", user, "100px") }
${ layout.menubar(section='running') }


<div class="container-fluid">
  ${ layout.dashboard_sub_menubar(section='workflows') }

  <h1>
    ${ _('Workflow') } <a href="${ url('oozie:list_oozie_workflow', job_id=workflow.id) }">${ workflow.appName }</a> :
    ${ _('Action') } ${ action.name }
  </h1>

  <table class="table table-condensed datatables" id="jobTable">
    <thead>
      <tr>
        <th>${ _('Property') }</th>
        <th>${ _('Value') }</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>${ _('Name') }</td>
        <td>${ action.name }</td>
      </tr>
      <tr>
        <td>${ _('Type') }</td>
        <td>${ action.type }</td>
      </tr>
      <tr>
        <td>${ _('Status') }</td>
        <td><span class="label ${ utils.get_status(action.status) }">${ action.status }</span></td>
      </tr>
      <tr>
        <td>${ _('Configuration') }</td>
        <td>${ utils.display_conf(action.conf_dict) }</td>
      </tr>
      % if action.errorCode:
        <tr>
          <td>${ _('Error Code') }</td>
          <td>${ action.errorCode }</td>
        </tr>
      % endif
      % if action.errorMessage:
        <tr>
          <td>${ _('Error Message') }</td>
          <td>${ action.errorMessage }</td>
        </tr>
      % endif
    </tbody>
  </table>

  <h2>${ _('Details') }</h2>

  <table class="table table-condensed datatables" id="jobTable">
    <thead>
      <tr>
        <th>${ _('Property') }</th>
        <th>${ _('Value') }</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>${ _('External Id') }</td>
        <td>
          % if action.externalId:
            <a href="${ url('jobbrowser.views.single_job', jobid=action.externalId) }">${ action.externalId }</a>
          % endif
        </td>
      </tr>
      <tr>
        <td>${ _('External Status') }</td>
        <td><span class="label ${ utils.get_status(action.externalStatus) }">${ action.externalStatus }<span></td>
      </tr>
      <tr>
        <td>${ _('Data') }</td>
        <td>${ action.data }</td>
      </tr>
      <tr>
        <td>${ _('Start time') }</td>
        <td>${ utils.format_time(action.startTime) }</td>
      </tr>
      <tr>
        <td>${ _('End time') }</td>
        <td>${ utils.format_time(action.endTime) }</td>
      </tr>
      <tr>
        <td>${ _('Id') }</td>
        <td>${ action.id }</td>
      </tr>
      <tr>
        <td>${ _('Retries') }</td>
        <td>${ action.retries }</td>
      </tr>
      <tr>
        <td>${ _('TrackerUri') }</td>
        <td>${ action.trackerUri }</td>
      </tr>
      <tr>
        <td>${ _('Transition') }</td>
        <td>${ action.transition }</td>
      </tr>
    </tbody>
  </table>

  <br/>
  <a class="btn" onclick="history.back()">${ _('Back') }</a>
</div>

${commonfooter(messages)}

## -*- coding: utf-8 -*-
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

${ commonheader(_("Workflow Action"), "oozie", user, "100px") | n,unicode }
${ layout.menubar(section='running') }


<div class="container-fluid">
  ${ layout.dashboard_sub_menubar(section='workflows') }

  <h1>
    % if oozie_bundle:
      ${ _('Bundle') } <a href="${ oozie_bundle.get_absolute_url() }">${ oozie_bundle.appName }</a> :
    % endif
    % if oozie_coordinator:
      ${ _('Coordinator') } <a href="${ oozie_coordinator.get_absolute_url() }">${ oozie_coordinator.appName }</a> :
    % endif
    ${ _('Workflow') } <a href="${ workflow.get_absolute_url() }">${ workflow.appName }</a> :
    ${ _('Action') } ${ action.name }
  </h1>

 <div class="row-fluid">
    <div class="span2">
      <div class="well sidebar-nav">
        <ul class="nav nav-list">
          <li class="nav-header">${ _('Workflow') }</li>
          <li>
            <a title="${ _('Edit workflow') }" href="${ workflow.get_absolute_url() }">${ workflow.appName }</a>
          </li>

          <li class="nav-header">${ _('Name') }</li>
          <li>${ action.name }</li>

          % if action.externalId:
            <li class="nav-header">${ _('External Id') }</li>
            <li><a href="${ url('jobbrowser.views.single_job', job=action.externalId) }">${ "_".join(action.externalId.split("_")[-2:]) }</a></li>

            <li class="nav-header">${ _('Logs') }</li>
            <li>
              <a href="${ url('jobbrowser.views.job_single_logs', job=action.externalId) }" title="${ _('View the logs') }" rel="tooltip"><i class="icon-tasks"></i></a>
            </li>
          % endif

          <li class="nav-header">${ _('Type') }</li>
          <li>${ action.type }</li>

          <li class="nav-header">${ _('Status') }</li>
          <li id="status"><span class="label ${ utils.get_status(action.status) }">${ action.status }</span></li>
        </ul>
      </div>
    </div>

    <div class="span9">
      <ul class="nav nav-tabs">
        <li class="active"><a href="#details" data-toggle="tab">${ _('Details') }</a></li>
        <li><a href="#configuration" data-toggle="tab">${ _('Configuration') }</a></li>
        <li><a href="#child-jobs" data-toggle="tab">${ _('Child Jobs') }</a></li>
      </ul>

      <div id="workflow-tab-content" class="tab-content" style="min-height:200px">

        <div class="tab-pane active" id="details">
          <table class="table table-condensed datatables" id="jobTable">
            <thead>
              <tr>
                <th>${ _('Property') }</th>
                <th>${ _('Value') }</th>
              </tr>
            </thead>
            <tbody>
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
              <tr>
                <td>${ _('Retries') }</td>
                <td>${ action.retries }</td>
              </tr>
              <tr>
                <td>${ _('TrackerURI') }</td>
                <td>${ action.trackerUri }</td>
              </tr>
              <tr>
                <td>${ _('Transition') }</td>
                <td>${ action.transition }</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div id="configuration" class="tab-pane" style="min-height:400px">
          <textarea id="configurationEditor">${ action.conf }</textarea>
        </div>

        <div id="child-jobs" class="tab-pane">
          % if not action.externalChildIDs:
            ${ _('No child jobs') }
          % else:
          <table class="table table-condensed datatables" id="jobTable">
            <thead>
              <tr>
                <th>${ _('Logs') }</th>
                <th>${ _('Ids') }</th>
              </tr>
            </thead>
            <tbody>
            % for child_id in action.externalChildIDs.split(','):
              <tr>
                <td>
                  <a href="${ url('jobbrowser.views.job_single_logs', job=child_id) }" title="${ _('View the logs') }" rel="tooltip">
                    <i class="icon-tasks"></i>
                  </a>
                </td>
                <td>
                  <a href="${ url('jobbrowser.views.single_job', job=child_id) }">
                    ${ "_".join(child_id.split("_")[-2:]) }
                  </a>
                </td>
              </tr>
            % endfor
              </tbody>
            </table>
          % endif
        </div>
      </div>

      <div style="margin-bottom: 16px">
        <a class="btn" onclick="history.back()">${ _('Back') }</a>
      </div>
    </div>
  </div>

</div>

<script src="/static/ext/js/codemirror-3.11.js"></script>
<link rel="stylesheet" href="/static/ext/css/codemirror.css">
<script src="/static/ext/js/codemirror-xml.js"></script>

<script type="text/javascript">

  $(document).ready(function() {
    var definitionEditor = $("#configurationEditor")[0];

    var codeMirror = CodeMirror(function (elt) {
      definitionEditor.parentNode.replaceChild(elt, definitionEditor);
    }, {
      value:definitionEditor.value,
      readOnly:true,
      lineNumbers:true
    });

    // force refresh on tab change
    $("a[data-toggle='tab']").on("shown", function (e) {
      if ($(e.target).attr("href") == "#configuration") {
        codeMirror.refresh();
      }
    });
  });
</script>

${ commonfooter(messages) | n,unicode }

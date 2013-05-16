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
  from oozie.forms import ParameterForm
%>

<%namespace name="layout" file="../navigation-bar.mako" />
<%namespace name="utils" file="../utils.inc.mako" />

${ commonheader(_("Workflow Dashboard"), "oozie", user, "100px") | n,unicode }
${ layout.menubar(section='dashboard') }


<div class="container-fluid" xmlns="http://www.w3.org/1999/html" xmlns="http://www.w3.org/1999/html">

  ${ layout.dashboard_sub_menubar(section='workflows') }

  <h1>
    % if oozie_bundle:
      ${ _('Bundle') } <a href="${ oozie_bundle.get_absolute_url() }">${ oozie_bundle.appName }</a> :
    % endif
    % if oozie_coordinator:
      ${ _('Coordinator') } <a href="${ oozie_coordinator.get_absolute_url(oozie_bundle) }">${ oozie_coordinator.appName }</a> :
    % endif

    ${ _('Workflow') } ${ oozie_workflow.appName }
  </h1>

  <div class="row-fluid">
    <div class="span2">
      <div class="well sidebar-nav">
        <ul class="nav nav-list">
          <li class="nav-header">${ _('Workflow') }</li>
          <li>
              % if hue_workflow is not None:
                <a title="${ _('Edit workflow') }" href="${ hue_workflow.get_absolute_url() }">${ hue_workflow }</a>
              % else:
              ${ oozie_workflow.appName }
              % endif
          </li>

          % if hue_coord:
              <li class="nav-header">${ _('Coordinator') }</li>
              <li><a href="${ hue_coord.get_absolute_url() }">${ hue_coord.name }</a></li>
          % endif

          <li class="nav-header">${ _('Submitter') }</li>
          <li>${ oozie_workflow.user }</li>

          <li class="nav-header">${ _('Status') }</li>
          <li id="status"><span class="label ${ utils.get_status(oozie_workflow.status) }">${ oozie_workflow.status }</span></li>

          <li class="nav-header">${ _('Progress') }</li>
          <li id="progress">
            <div class="progress">
              <div class="bar" style="width: 0">${ oozie_workflow.get_progress() }%</div>
            </div>
          </li>

          <li class="nav-header">${ _('Id') }</li>
          <li>${  oozie_workflow.id }</li>

          % if parameters and len(parameters) < 10:
              <li class="nav-header">${ _('Variables') }</li>
              % for var, value in parameters.iteritems():
                % if var not in ParameterForm.NON_PARAMETERS and var != 'oozie.use.system.libpath':
                  <li rel="tooltip" title="${ var } : ${ str(value) }">
                    % if utils.is_linkable(var, str(value)):
                      <a href="${ utils.hdfs_link_js(str(value)) }"><i class="icon-eye-open"></i> <span class="variable hide">${ var }</span></a>
                    % else:
                    <i class="icon-eye-open"></i> <span class="variable">${ var }</span>
                    % endif
                  </li>
                % endif
              % endfor
          % endif

          % if has_job_edition_permission(oozie_workflow, user):
              <li class="nav-header">${ _('Manage') }</li>
              <li>
                <button title="${_('Kill %(workflow)s') % dict(workflow=oozie_workflow.id)}"
                   id="kill-btn"
                   class="btn btn-small confirmationModal
                   % if not oozie_workflow.is_running():
                     hide
                   % endif
                   "
                   alt="${ _('Are you sure you want to kill workflow %s?') %  oozie_workflow.id }"
                   href="javascript:void(0)"
                   data-url="${ url('oozie:manage_oozie_jobs', job_id=oozie_workflow.id, action='kill') }"
                   data-message="${ _('The workflow was killed.') }"
                   data-confirmation-message="${ _('Are you sure you\'d like to kill this job?') }">
                ${_('Kill')}
                </button>
                <button title="${ _('Suspend the workflow after finishing the current running actions') }" id="suspend-btn"
                   data-url="${ url('oozie:manage_oozie_jobs', job_id=oozie_workflow.id, action='suspend') }"
                   data-confirmation-message="${ _('Are you sure you\'d like to suspend this job?') }"
                   class="btn btn-small confirmationModal
                   % if not oozie_workflow.is_running():
                     hide
                   % endif
                   " rel="tooltip" data-placement="right">
                  ${ _('Suspend') }
                </button>
                <button title="${ _('Resume the workflow') }" id="resume-btn"
                   data-url="${ url('oozie:manage_oozie_jobs', job_id=oozie_workflow.id, action='resume') }"
                   data-confirmation-message="${ _('Are you sure you\'d like to resume this job?') }"
                   class="btn btn-small confirmationModal
                   % if oozie_workflow.is_running():
                     hide
                   % endif
                   ">
                  ${ _('Resume') }
                </button>
                <button title="${ _('Rerun the same workflow') }" id="rerun-btn"
                   data-rerun-url="${ url('oozie:rerun_oozie_job', job_id=oozie_workflow.id, app_path=oozie_workflow.appPath) }"
                   class="btn btn-small
                   % if oozie_workflow.is_running():
                     hide
                   % endif
                   ">
                  ${ _('Rerun') }
                </button>
                <div id="rerun-wf-modal" class="modal hide"></div>
              </li>
          % endif
        </ul>
      </div>
    </div>

    <div class="span9">
      <ul class="nav nav-tabs">
        % if workflow_graph:
            <li class="active"><a href="#graph" data-toggle="tab">${ _('Graph') }</a></li>
            <li><a href="#actions" data-toggle="tab">${ _('Actions') }</a></li>
        % else:
            <li class="active"><a href="#actions" data-toggle="tab">${ _('Actions') }</a></li>
        % endif
        <li><a href="#details" data-toggle="tab">${ _('Details') }</a></li>
        <li><a href="#configuration" data-toggle="tab">${ _('Configuration') }</a></li>
        <li><a href="#log" data-toggle="tab">${ _('Log') }</a></li>
        <li><a href="#definition" data-toggle="tab">${ _('Definition') }</a></li>
      </ul>

      <div id="workflow-tab-content" class="tab-content" style="min-height:200px">

        % if workflow_graph:
            <div id="graph" class="tab-pane active">
            ${ workflow_graph | n,unicode }
            </div>
        % endif

        <div id="actions" class="tab-pane ${ utils.if_false(workflow_graph, 'active') }">
          <table class="table table-striped table-condensed selectable">
            <thead>
            <tr>
              <th>${ _('Logs') }</th>
              <th>${ _('Id') }</th>
              <th>${ _('Name') }</th>
              <th>${ _('Type') }</th>
              <th>${ _('Status') }</th>
              <th>${ _('External Id') }</th>

              <th>${ _('Start Time') }</th>
              <th>${ _('End Time') }</th>

              <th>${ _('Retries') }</th>
              <th>${ _('Error Code') }</th>
              <th>${ _('Error Message') }</th>
              <th>${ _('Transition') }</th>

              <th>${ _('Data') }</th>
            </tr>
            </thead>
            <tbody data-bind="template: {name: 'actionTemplate', foreach: actions}">

            </tbody>
            <tfoot>
            <tr data-bind="visible: actions().length == 0">
              <td colspan="12">
                <div class="alert">
                  ${ _('There are no actions to be shown.') }
                </div>
              </td>
            </tr>
            </tfoot>
          </table>
        </div>


        <script id="actionTemplate" type="text/html">
          <tr>
            <td>
              <a data-bind="visible:externalId !='', attr: { href: log}" data-row-selector-exclude="true"><i class="icon-tasks"></i></a>
            </td>
            <td>
              <a data-bind="text: id, attr: { href: url}" data-row-selector="true"></a>
            </td>
            <td data-bind="text: name"></td>
            <td data-bind="text: type"></td>
            <td><span data-bind="text: status, attr: {'class': statusClass}"></span></td>
            <td>
              <a data-bind="visible:externalId !='', attr: { href: externalIdUrl}, text: externalId" data-row-selector-exclude="true"></a>
            </td>

            <td data-bind="text: startTime"></td>
            <td data-bind="text: endTime"></td>

            <td data-bind="text: retries"></td>
            <td data-bind="text: errorCode"></td>
            <td data-bind="text: errorMessage"></td>
            <td data-bind="text: transition"></td>

            <td data-bind="text: data"></td>

          </tr>
        </script>


        <div class="tab-pane" id="details">
          <table class="table table-condensed">
            <tbody>
            <tr>
              <td>${ _('Group') }</td>
              <td>${ oozie_workflow.group or '-' }</td>
            </tr>
            <tr>
              <td>${ _('External Id') }</td>
              <td>${ oozie_workflow.externalId or '-' }</td>
            </tr>
            <tr>
              <td>${ _('Last Modified') }</td>
              <td>${ utils.format_time(oozie_workflow.lastModTime) }</td>
            </tr>
            <tr>
              <td>${ _('Start Time') }</td>
              <td>${ utils.format_time(oozie_workflow.startTime) }</td>
            </tr>
            <tr>
              <td>${ _('Created Time') }</td>
              <td>${ utils.format_time(oozie_workflow.createdTime) }</td>
            </tr>
            <tr>
              <td>${ _('End Time') }</td>
              <td>${  utils.format_time(oozie_workflow.endTime) }</td>
            </tr>
            <tr>
              <td>${ _('Application Path') }</td>
              <td>${  utils.hdfs_link(oozie_workflow.appPath) }</td>
            </tr>
            <tr>
              <td>${ _('Run') }</td>
              <td>${  oozie_workflow.run }</td>
            </tr>
            </tbody>
          </table>
        </div>

        <div class="tab-pane" id="configuration">
          ${ utils.display_conf(oozie_workflow.conf_dict) }
        </div>

        <div class="tab-pane" id="log">
          <pre>${ oozie_workflow.log.decode('utf-8', 'replace') }</pre>
        </div>

        <div class="tab-pane" id="definition" style="min-height:400px">
          <textarea id="definitionEditor">${ oozie_workflow.definition.decode('utf-8', 'replace') }</textarea>
        </div>
      </div>

      <div style="margin-bottom: 16px">
        <a class="btn" onclick="history.back()">${ _('Back') }</a>
      </div>
    </div>

  </div>

</div>

<div id="confirmation" class="modal hide">
  <div class="modal-header">
    <a href="#" class="close" data-dismiss="modal">&times;</a>
    <h3 class="message"></h3>
  </div>
  <div class="modal-footer">
    <a href="#" class="btn" data-dismiss="modal">${_('No')}</a>
    <a class="btn btn-danger" href="javascript:void(0);">${_('Yes')}</a>
  </div>
</div>

<script src="/oozie/static/js/bundles.utils.js" type="text/javascript" charset="utf-8"></script>
<link rel="stylesheet" href="/oozie/static/css/workflow.css">
<script src="/static/ext/js/knockout-2.1.0.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/datatables-paging-0.1.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/codemirror-3.11.js"></script>
<link rel="stylesheet" href="/static/ext/css/codemirror.css">
<script src="/static/ext/js/codemirror-xml.js"></script>

<style>
.CodeMirror.cm-s-default {
   height:500px;
}
.sidebar-nav {
  padding: 9px 0;
}
</style>

<script type="text/javascript">

  var Action = function (action) {
    return {
      id: action.id,
      log: action.log,
      url: action.url,
      name: action.name,
      type: action.type,
      status: action.status,
      statusClass: "label " + getStatusClass(action.status),
      externalIdUrl: action.externalIdUrl,
      externalId: action.externalId,
      startTime: action.startTime,
      endTime: action.endTime,
      retries: action.retries,
      errorMessage: action.errorMessage,
      errorCode: action.errorCode,
      transition: action.transition,
      data: action.data
    }
  }

  var RunningWorkflowActionsModel = function (actions) {
    var self = this;

    self.actions = ko.observableArray(ko.utils.arrayMap(actions), function (action) {
      return new Action(action);
    });

  };

  var viewModel = new RunningWorkflowActionsModel([]);
  ko.applyBindings(viewModel);

  $(document).ready(function() {

    $("*[rel=tooltip]").tooltip();

    $(".variable").each(function () {
      if ($(this).text().length > 15) {
        $(this).html($(this).text().substr(0, 14) + "&hellip;");
      }
      $(this).removeClass("hide");
    });

    var definitionEditor = $("#definitionEditor")[0];

    var codeMirror = CodeMirror(function (elt) {
      definitionEditor.parentNode.replaceChild(elt, definitionEditor);
    }, {
      value:definitionEditor.value,
      readOnly:true,
      lineNumbers:true
    });

    // force refresh on tab change
    $("a[data-toggle='tab']").on("shown", function (e) {
      if ($(e.target).attr("href") == "#definition") {
        codeMirror.refresh();
      }
    });

    $(".action-link").click(function(){
      window.location = $(this).data('edit');
    });

    $(".confirmationModal").click(function(){
      var _this = $(this);
      $("#confirmation .message").text(_this.data("confirmation-message"));
      $("#confirmation").modal("show");
      $("#confirmation a.btn-danger").click(function() {
        _this.trigger('confirmation');
      });
    });

    $("#kill-btn").bind('confirmation', function() {
      var _this = this;
      $.post($(this).data("url"),
        { 'notification': $(this).data("message") },
        function(response) {
          if (response['status'] != 0) {
            $.jHueNotify.error("${ _('Error: ') }" + response['data']);
          } else {
            window.location.reload();
          }
        }
      );
      return false;
    });

    $("#suspend-btn").bind('confirmation', function() {
      var _this = this;
      $.post($(this).data("url"),
        { 'notification': $(this).data("message") },
        function(response) {
          if (response['status'] != 0) {
            $.jHueNotify.error("${ _('Error: ') }" + response['data']);
          } else {
            window.location.reload();
          }
        }
      );
      return false;
    });

    $("#resume-btn").bind('confirmation', function() {
      var _this = this;
      $.post($(this).data("url"),
        { 'notification': $(this).data("message") },
        function(response) {
          if (response['status'] != 0) {
            $.jHueNotify.error("${ _('Error: ') }" + response['data']);
          } else {
            window.location.reload();
          }
        }
      );
      return false;
    });

    $('#rerun-btn').click(function() {
      var _action = $(this).data("rerun-url");

      $.get(_action,  function(response) {
          $('#rerun-wf-modal').html(response);
          $('#rerun-wf-modal').modal('show');
        }
      );
     });

    $("a[data-row-selector='true']").jHueRowSelector();

    resizeLogs();
    refreshView();
    var logsAtEnd = true;

    function refreshView() {
      $.getJSON("${ oozie_workflow.get_absolute_url() }" + "?format=json", function (data) {

        if (data.actions){
          viewModel.actions(ko.utils.arrayMap(data.actions, function (action) {
            return new Action(action);
          }));
        }

        $("#status span").attr("class", "label").addClass(getStatusClass(data.status)).text(data.status);

        if (data.id && data.status == "SUSPENDED"){
          $("#resume-btn").show();
        } else {
          $("#resume-btn").hide();
        }

        if (data.id && data.status == "RUNNING"){
          $("#suspend-btn").show();
        } else {
          $("#suspend-btn").hide();
        }

        if (data.id && data.status != "RUNNING" && data.status != "SUSPENDED"){
          $("#kill-btn").hide();
          $("#rerun-btn").show();
        }

        $("#progress .bar").text(data.progress+"%").css("width", data.progress+"%").attr("class", "bar "+getStatusClass(data.status, "bar-"));
        $("#graph").html(data.graph);

        var _logsEl = $("#log pre");
        var newLines = data.log.split("\n").slice(_logsEl.text().split("\n").length);
        _logsEl.text(_logsEl.text() + newLines.join("\n"));
        if (logsAtEnd) {
          _logsEl.scrollTop(_logsEl[0].scrollHeight - _logsEl.height());
        }
        if (data.status != "RUNNING" && data.status != "PREP"){
          return;
        }
        window.setTimeout(refreshView, 1000);
      });
    }

    $(window).resize(function () {
      resizeLogs();
    });

    $("a[href='#log']").on("shown", function () {
      resizeLogs();
    });

    $("#log pre").scroll(function () {
      if ($(this).scrollTop() + $(this).height() + 20 >= $(this)[0].scrollHeight) {
        logsAtEnd = true;
      }
      else {
        logsAtEnd = false;
      }
    });

    function resizeLogs() {
      $("#log pre").css("overflow", "auto").height($(window).height() - $("#log pre").position().top - 80);
    }

  });
</script>

${ commonfooter(messages) | n,unicode }

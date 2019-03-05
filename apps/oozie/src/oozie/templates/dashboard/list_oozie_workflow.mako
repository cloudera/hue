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
<%namespace name="workflow" file="../editor2/common_workflow.mako" />
<%namespace name="dashboard" file="/common_dashboard.mako" />

${ commonheader(_("Workflow Dashboard"), "oozie", user, request) | n,unicode }
${ layout.menubar(section='workflows', dashboard=True) }

<div id="oozie_workflowComponents" class="container-fluid oozie_workflowComponents">
<div class="card card-small">
  <div class="card-body">
  <p>

  <div class="row-fluid">
    <div class="span2">
      <div class="sidebar-nav">
        <ul class="nav nav-list" style="border:none">
          <li class="nav-header">${ _('Workflow') }</li>
          % if hue_workflow is not None:
          <li><a title="${ _('Edit workflow') }" href="${ hue_workflow.get_absolute_url() }">${ hue_workflow }</a></li>
          % else:
          <li class="white">${ oozie_workflow.appName }</li>
          % endif

          % if hue_coord:
          <li class="nav-header">${ _('Coordinator') }</li>
          <li><a href="${ hue_coord.get_absolute_url() }">${ hue_coord.name }</a></li>
          % endif

          <li class="nav-header">${ _('Submitter') }</li>
          <li class="white">${ oozie_workflow.user }</li>

          <li class="nav-header">${ _('Status') }</li>
          <li class="white" id="status"><span class="label ${ utils.get_status(oozie_workflow.status) }">${ oozie_workflow.status }</span></li>

          <li class="nav-header">${ _('Progress') }</li>
          <li class="white" id="progress">
            <div class="progress">
              <div class="bar" style="width: 0">${ oozie_workflow.get_progress() }%</div>
            </div>
          </li>

          <li class="nav-header">${ _('Id') }</li>
          <li class="white">${ oozie_workflow.id }</li>

          % if parameters and len(parameters) <= 15:
            <li class="nav-header">${ _('Variables') }</li>
            % for var, value in parameters.iteritems():
                % if utils.is_linkable(var, unicode(value)):
                  <li rel="tooltip" title="${ var } : ${ str(value) }">
                    <a href="${ utils.hdfs_link_js(str(value)) }"><i class="fa fa-eye"></i> <span class="variable hide">${ var }</span></a>
                % else:
                  <li rel="tooltip" title="${ var } : ${ unicode(value) }" class="white">
                    <i class="fa fa-eye"></i> <span class="variable">${ var }</span>
                % endif
                  </li>
              % endfor
          % endif

          % if has_job_edition_permission(oozie_workflow, user):
              <li class="nav-header">${ _('Manage') }</li>
              <li class="white">
                <button title="${_('Kill %(workflow)s') % dict(workflow=oozie_workflow.id)}"
                   id="kill-btn"
                   class="btn btn-small btn-danger disable-feedback confirmationModal
                   % if not oozie_workflow.is_running():
                     hide
                   % endif
                   "
                   alt="${ _('Are you sure you want to kill workflow %s?') %  oozie_workflow.id }"
                   href="javascript:void(0)"
                   data-url="${ url('oozie:manage_oozie_jobs', job_id=oozie_workflow.id, action='kill') }"
                   data-message="${ _('The workflow was killed.') }"
                   data-confirmation-message="${ _('Are you sure you\'d like to kill this job?') }" style="margin-bottom: 5px">
                ${_('Kill')}
                </button>
                <button title="${ _('Suspend the workflow after finishing the current running actions') }" id="suspend-btn"
                   data-url="${ url('oozie:manage_oozie_jobs', job_id=oozie_workflow.id, action='suspend') }"
                   data-confirmation-message="${ _('Are you sure you\'d like to suspend this job?') }"
                   class="btn btn-small confirmationModal
                   % if not oozie_workflow.is_running():
                     hide
                   % endif
                   " rel="tooltip" data-placement="right" style="margin-bottom: 5px">
                  ${ _('Suspend') }
                </button>
                <button title="${ _('Resume the workflow') }" id="resume-btn"
                   data-url="${ url('oozie:manage_oozie_jobs', job_id=oozie_workflow.id, action='resume') }"
                   data-confirmation-message="${ _('Are you sure you\'d like to resume this job?') }"
                   class="btn btn-small confirmationModal
                   % if oozie_workflow.is_running():
                     hide
                   % endif
                   " style="margin-bottom: 5px">
                  ${ _('Resume') }
                </button>
                <button title="${ _('Rerun the same workflow') }" id="rerun-btn"
                   data-rerun-url="${ url('oozie:rerun_oozie_job', job_id=oozie_workflow.id, app_path=oozie_workflow.appPath) }"
                   class="btn btn-small
                   % if oozie_workflow.is_running():
                     hide
                   % endif
                   " style="margin-bottom: 5px">
                  ${ _('Rerun') }
                </button>
                <div id="rerun-wf-modal" class="modal hide"></div>
              </li>
          % endif
        </ul>
      </div>
    </div>

    <div class="span10" style="margin-left: 2.56410256%;">
      <h1 class="card-heading simple card-heading-nopadding card-heading-noborder card-heading-blue" style="margin-bottom: 10px">
        % if oozie_bundle:
          ${ _('Bundle') } <a href="${ oozie_bundle.get_absolute_url() }">${ oozie_bundle.appName }</a> :
        % endif
        % if oozie_coordinator:
          ${ _('Coordinator') } <a href="${ oozie_coordinator.get_absolute_url(oozie_bundle) }">${ oozie_coordinator.appName }</a> :
        % endif
        % if oozie_parent and (oozie_coordinator is None or oozie_parent.id != oozie_coordinator.id):
          ${ _('Parent') } <a href="${ oozie_parent.get_absolute_url() }">${ oozie_parent.appName }</a> :
        % endif

        ${ _('Workflow') } ${ oozie_workflow.appName }
      </h1>
      <ul class="nav nav-tabs">
        % if workflow_graph != 'MISSING':
        <li class="active"><a href="#graph" data-toggle="tab">${ _('Graph') }</a></li>
        <li><a href="#actions" data-toggle="tab">${ _('Actions') }</a></li>
        % else:
        <li class="active"><a href="#actions" data-toggle="tab">${ _('Actions') }</a></li>
        % endif
        <li><a href="#details" data-toggle="tab">${ _('Details') }</a></li>
        <li><a href="#configuration" data-toggle="tab">${ _('Configuration') }</a></li>
        <li><a href="#log" data-toggle="tab">${ _('Log') }</a></li>
        <li><a href="#definition" data-toggle="tab">${ _('Definition') }</a></li>
        % if oozie_workflow.has_sla:
        <li><a href="#sla" data-toggle="tab">${ _('SLA') }</a></li>
        % endif
      </ul>

      <div id="workflow-tab-content" class="tab-content" style="min-height:200px; overflow: visible">
        % if workflow_graph != 'MISSING':
        <div id="graph" class="tab-pane active dashboard-container">
        % if layout_json == '':
        ${ workflow_graph | n,unicode }
        % else:
        ${ workflow.render() }
        % endif
        </div>
        <div id="actions" class="tab-pane">
        % else:
        <div id="actions" class="tab-pane active">
        % endif
          <table class="table table-condensed selectable">
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
              <!-- ko if: externalId !='' && log != '' && log != null -->
              <a data-bind="attr: { href: log}" data-row-selector-exclude="true"><i class="fa fa-tasks"></i></a>
              <!-- /ko -->
              <!-- ko if: externalId =='' || log == '' || log == null -->
              <i class="fa fa-ban muted"></i>
              <!-- /ko -->
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
          <pre></pre>
        </div>

        <div class="tab-pane" id="definition">
          <div id="definitionEditor">${ oozie_workflow.definition.decode('utf-8', 'replace') }</div>
        </div>

        % if oozie_workflow.has_sla:
        <div class="tab-pane" id="sla" style="padding-left: 20px">
          <div id="yAxisLabel" class="hide">${_('Time since Nominal Time in min')}</div>
          <div id="slaChart"></div>
          <table id="slaTable" class="table table-condensed hide">
            <thead>
              <th>${_('Status')}</th>
              <th>${_('Nominal Time')}</th>
              <th>${_('Expected Start')}</th>
              <th>${_('Actual Start')}</th>
              <th>${_('Expected End')}</th>
              <th>${_('Actual End')}</th>
              <th>${_('Expected Duration')}</th>
              <th>${_('Actual Duration')}</th>
              <th>${_('SLA')}</th>
            </thead>
            <tbody>
            %for sla in oozie_slas:
              <tr>
                <td class="slaStatus">${sla['slaStatus']}</td>
                <td><span class="nominalTime">${sla['nominalTime']}</span></td>
                <td><span class="expectedStart">${sla['expectedStart']}</span></td>
                <td><span class="actualStart">${sla['actualStart']}</span></td>
                <td><span class="expectedEnd">${sla['expectedEnd']}</span></td>
                <td><span class="actualEnd">${sla['actualEnd']}</span></td>
                <td>${sla['expectedDuration']}</td>
                <td>${sla['actualDuration']}</td>
                <td><a href="${ url('oozie:list_oozie_sla') }#${ sla['id'] }"></a></td>
              </tr>
            %endfor
            </tbody>
          </table>
        </div>
        % endif
      </div>

      <div style="margin-bottom: 16px">
        <a class="btn" onclick="history.back()">${ _('Back') }</a>
      </div>
    </div>

  </div>


  </p>
  </div>
  </div>
</div>

<div id="confirmation" class="modal hide">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
    <h2 class="modal-title message"></h2>
  </div>
  <div class="modal-footer">
    <a href="#" class="btn" data-dismiss="modal">${_('No')}</a>
    <a class="btn btn-danger disable-feedback" href="javascript:void(0);">${_('Yes')}</a>
  </div>
</div>

<script src="${ static('oozie/js/dashboard-utils.js') }" type="text/javascript" charset="utf-8"></script>
<link rel="stylesheet" href="${ static('oozie/css/workflow.css') }">
<script src="${ static('desktop/ext/js/datatables-paging-0.1.js') }" type="text/javascript" charset="utf-8"></script>

% if oozie_workflow.has_sla:
<script src="${ static('oozie/js/sla.utils.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/jquery/plugins/jquery.flot.min.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/jquery/plugins/jquery.flot.selection.min.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/jquery/plugins/jquery.flot.time.min.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/js/jquery.blueprint.js') }"></script>
%endif

% if layout_json != '':

<link rel="stylesheet" href="${ static('oozie/css/common-editor.css') }">
<link rel="stylesheet" href="${ static('oozie/css/workflow-editor.css') }">
<link rel="stylesheet" href="${ static('desktop/ext/css/bootstrap-editable.css') }">

${ dashboard.import_layout() }

<script src="${ static('oozie/js/workflow-editor.ko.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('oozie/js/workflow-editor.utils.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/jquery/plugins/jquery.curvedarrow.js') }" type="text/javascript" charset="utf-8"></script>
%endif

<style type="text/css">
  #definitionEditor {
    min-height: 250px;
    margin-bottom: 10px;
  }

  #sla th {
    vertical-align: middle !important;
  }

  #yAxisLabel {
    -webkit-transform: rotate(270deg);
    -moz-transform: rotate(270deg);
    -o-transform: rotate(270deg);
    writing-mode: lr-tb;
    margin-left: -110px;
    margin-top: 130px;
    position: absolute;
  }

  #slaTable {
    margin-top: 20px;
  }

  % if not workflow_graph:
  #graph {
    margin-top: 0;
  }
  #graph, #new-node {
    text-align: left;
  }
  % endif

</style>

<script type="text/javascript">

  ${ utils.slaGlobal() }

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
      externalJobId: action.externalJobId,
      startTime: action.startTime,
      endTime: action.endTime,
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

  var actionsViewModel = new RunningWorkflowActionsModel([]);
  ko.applyBindings(actionsViewModel, $("#actions")[0]);

  % if layout_json != '':
  var viewModel = new WorkflowEditorViewModel(${ layout_json | n,unicode }, ${ workflow_json | n,unicode }, ${ credentials_json | n,unicode }, ${ workflow_properties_json | n,unicode }, ${ subworkflows_json | n,unicode }, ${ can_edit_json | n,unicode });
  ko.applyBindings(viewModel, $("#graph")[0]);
  viewModel.isViewer = ko.observable(true);
  viewModel.init();
  fullLayout(viewModel);

  var globalFilechooserOptions = {
    skipInitialPathIfEmpty: true,
    showExtraHome: true,
    uploadFile: true,
    createFolder: true,
    extraHomeProperties: {
      label: '${ _('Workspace') }',
      icon: 'fa-folder-open',
      path: viewModel.workflow.properties.deployment_dir()
    },
    deploymentDir: viewModel.workflow.properties.deployment_dir()
  }
  %endif

  var CHART_LABELS = {
    NOMINAL_TIME: "${_('Nominal Time')}",
    EXPECTED_START: "${_('Expected Start')}",
    ACTUAL_START: "${_('Actual Start')}",
    EXPECTED_END: "${_('Expected End')}",
    ACTUAL_END: "${_('Actual End')}",
    TOOLTIP_ADDON: "${_('click for the SLA dashboard')}"
  }
  var slaTable;

  $(document).ready(function() {
    % if layout_json != '':
    viewModel.drawArrows();
    %endif

    var CURRENT_ZOOM = 1;
    $(document).keydown(function(e) {
      if (e.ctrlKey){
        if (e.which == 173 || e.which == 189) {
          CURRENT_ZOOM -= 0.1;
          zoom();
        }
        if (e.which == 61 || e.which == 187) {
          CURRENT_ZOOM += 0.1;
          zoom();
        }
        if (e.which == 48) {
          CURRENT_ZOOM = 1;
          zoom();
        }
      }
    });

    function zoom(){
      $("#graph").css("zoom", CURRENT_ZOOM);
      $("#graph").css("-moz-transform", "scale(" + CURRENT_ZOOM + ")");
    }

    $("*[rel=tooltip]").tooltip();

    % if oozie_workflow.has_sla:
    slaTable = $("#slaTable").dataTable({
      "bPaginate": false,
      "bLengthChange": false,
      "bInfo": false,
      "bAutoWidth": false,
      "oLanguage": {
        "sEmptyTable": "${_('No data available')}",
        "sZeroRecords": "${_('No matching records')}"
      }
    });

    $(".dataTables_wrapper").css("min-height", "0");
    $(".dataTables_filter").hide();
    % endif

    $(".variable").each(function () {
      if ($(this).text().length > 25) {
        $(this).html($(this).text().substr(0, 24) + "&hellip;");
      }
      $(this).removeClass("hide");
    });

    var editor = ace.edit("definitionEditor");
    editor.setOptions({
      readOnly: true,
      maxLines: Infinity
    });
    editor.setTheme($.totalStorage("hue.ace.theme") || "ace/theme/hue");
    editor.getSession().setMode("ace/mode/xml");

    // force refresh on tab change
    $("a[data-toggle='tab']").on("shown", function (e) {
      if ($(e.target).attr("href") == "#graph") {
        % if layout_json != '':
        viewModel.drawArrows();
        %endif
      }
      else {
        $("canvas").remove();
      }
      % if oozie_workflow.has_sla:
      if ($(e.target).attr("href") == "#sla") {
        window.setTimeout(function () {
          updateSLAChart(slaTable, CHART_LABELS, 30); // limits to 30 results
        }, 100)
      }
      % endif
    });

    $(".action-link").click(function(){
      window.location = $(this).data('edit');
    });

    $(".confirmationModal").click(function(){
      var _this = $(this);
      $("#confirmation .message").text(_this.data("confirmation-message"));
      $("#confirmation").modal("show");
      $("#confirmation a.btn-danger").on("click", function() {
        _this.trigger('confirmation');
        $(this).attr("data-loading-text", $(this).text() + " ...");
        $(this).button("loading");
      });
    });

    $("#kill-btn").bind('confirmation', function() {
      var _this = this;
      $.post($(this).data("url"),
        { 'notification': $(this).data("message") },
        function(response) {
          if (response['status'] != 0) {
            $(document).trigger("error", "${ _('Error: ') }" + response['data']);
            $("#confirmation a.btn-danger").button("reset");
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
            $(document).trigger("error", "${ _('Error: ') }" + response['data']);
            $("#confirmation a.btn-danger").button("reset");
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
            $(document).trigger("error", "${ _('Error: ') }" + response['data']);
            $("#confirmation a.btn-danger").button("reset");
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
    refreshLogs();

    var logsAtEnd = true;
    function refreshLogs() {
      $.getJSON("${ url('oozie:get_oozie_job_log', job_id=oozie_workflow.id) }", function (data) {
        var _logsEl = $("#log pre");
        _logsEl.text(data.log);

        if (logsAtEnd) {
          _logsEl.scrollTop(_logsEl[0].scrollHeight - _logsEl.height());
        }
        if (data.status != "RUNNING" && data.status != "PREP"){
          return;
        }
        window.setTimeout(refreshLogs, 3000);
      });
    }


    function refreshView() {
      $.getJSON("${ oozie_workflow.get_absolute_url(format='json') }", function (data) {

        if (data.actions){
          actionsViewModel.actions(ko.utils.arrayMap(data.actions, function (action) {
            return new Action(action);
          }));
          % if layout_json != '':
          ko.utils.arrayForEach(actionsViewModel.actions(), function(action) {
            var _w, actionId = action.id.substr(action.id.length - 4);
            if (actionId === '@End'){
              _w = viewModel.getWidgetById('33430f0f-ebfa-c3ec-f237-3e77efa03d0a');
            }
            else {
              _w = viewModel.getWidgetById($("[id^=wdg_" + actionId.toLowerCase() + "]").attr("id").substr(4));
            }
            if (_w != null) {
              if (['SUCCEEDED', 'OK', 'DONE'].indexOf(action.status) > -1) {
                _w.status("success");
                _w.progress(100);
              }
              else if (['RUNNING', 'READY', 'PREP', 'WAITING', 'SUSPENDED', 'PREPSUSPENDED', 'PREPPAUSED', 'PAUSED', 'SUBMITTED', 'SUSPENDEDWITHERROR', 'PAUSEDWITHERROR'].indexOf(action.status) > -1) {
                _w.status("running");
                _w.progress(50);
              }
              else {
                _w.status("failed");
                _w.progress(100);
              }
              _w.actionURL(action.url);
              _w.logsURL(action.log);
              _w.externalIdUrl(action.externalIdUrl);
            }
          });
          %endif
        }

        $("#status span").attr("class", "label").addClass(getStatusClass(data.status)).text(data.status);

        $.jHueTitleUpdater.set(data.progress + "%");

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

        if (data.id && data.status != "RUNNING" && data.status != "SUSPENDED" && data.status != "PREP"){
          $("#kill-btn").hide();
          $("#rerun-btn").show();
          $.jHueTitleUpdater.reset();
        }

        $("#progress .bar").text(data.progress + "%").css("width", data.progress + "%").attr("class", "bar " + getStatusClass(data.status, "bar-"));
        %if layout_json == '':
          if (data.graph != "MISSING") { // constant from dashboard.py
            $("#graph").html(data.graph);
          }
        %endif

        if (data.status != "RUNNING" && data.status != "PREP"){
          return;
        }
        window.setTimeout(refreshView, 1000);
      });
    }

    var resizeTimeout = -1;
    $(window).on("resize", function () {
      window.clearTimeout(resizeTimeout);
      resizeTimeout = window.setTimeout(function () {
        resizeLogs();
        if ($("#graph").is(":visible")){
          % if layout_json != '':
          viewModel.drawArrows();
          %endif
        }
      }, 200);
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

    if (window.location.hash == "#showSla") {
      $("a[href='#sla']").click();
    }

  });
</script>

${ commonfooter(request, messages) | n,unicode }

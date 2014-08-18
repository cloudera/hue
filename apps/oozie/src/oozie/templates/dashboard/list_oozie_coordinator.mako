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

${ commonheader(_("Coordinator Dashboard"), "oozie", user) | n,unicode }
${ layout.menubar(section='coordinators', dashboard=True) }

<div class="container-fluid">
<div class="card card-small">
  <div class="card-body">
  <p>

<div class="row-fluid">
  <div class="span2">
    <div class="sidebar-nav">
      <ul class="nav nav-list" style="border:none">
        <li class="nav-header">${ _('Coordinator') }</li>
        % if coordinator is not None:
        <li><a href="${ coordinator.get_absolute_url() }">${ oozie_coordinator.appName }</a></li>
        % else:
        <li class="white">${ oozie_coordinator.appName }</li>
        % endif

        <li class="nav-header">${ _('Submitter') }</li>
        <li class="white">${ oozie_coordinator.user }</li>

        <li class="nav-header">${ _('Status') }</li>
        <li class="white" id="status"><span class="label ${ utils.get_status(oozie_coordinator.status) }">${ oozie_coordinator.status }</span></li>

        <li class="nav-header">${ _('Progress') }</li>
        <li class="white" id="progress">
          <div class="progress">
            <div class="bar" style="width: 0">${ oozie_coordinator.get_progress() }%</div>
          </div>
        </li>

        <li class="nav-header">${ _('Frequency') }</li>
        % if enable_cron_scheduling:
        <li class="white cron-frequency"><input class="value" type="hidden" value="${ oozie_coordinator.frequency }"/></li>
        % else:
        <li class="white">${ oozie_coordinator.frequency } ${ oozie_coordinator.timeUnit }</li>
        % endif

        <li class="nav-header">${ _('Next Materialized Time') }</li>
        <li class="white" id="nextTime">${ utils.format_time(oozie_coordinator.nextMaterializedTime) }</li>

        <li class="nav-header">${ _('Id') }</li>
        <li class="white">${ oozie_coordinator.id }</li>

        % if coordinator:
            <li class="nav-header">${ _('Datasets') }</li>
          % for dataset in coordinator.dataset_set.all():
            <li rel="tooltip" title="${ dataset.name } : ${ dataset.uri }" class="white"><i class="fa fa-eye"></i> <span class="dataset">${ dataset.name }</span></li>
          % endfor
        % endif

        % if has_job_edition_permission(oozie_coordinator, user):
          <li class="nav-header">${ _('Manage') }</li>
          <li class="white">
            <button title="${_('Kill %(coordinator)s') % dict(coordinator=oozie_coordinator.id)}"
              id="kill-btn"
              class="btn btn-small btn-danger disable-feedback confirmationModal
               % if not oozie_coordinator.is_running():
                 hide
               % endif
              "
              alt="${ _('Are you sure you want to kill coordinator %s?') % oozie_coordinator.id }"
              href="javascript:void(0)"
              data-url="${ url('oozie:manage_oozie_jobs', job_id=oozie_coordinator.id, action='kill') }"
              data-message="${ _('The coordinator was killed!') }"
              data-confirmation-message="${ _('Are you sure you\'d like to kill this job?') }">
                ${_('Kill')}
            </button>
            <button class="btn btn-small
               % if oozie_coordinator.is_running() or oozie_coordinator.status in ('KILLED', 'FAILED'):
                 hide
               % endif
            "
              id="rerun-btn"
              data-rerun-url="${ url('oozie:rerun_oozie_coord', job_id=oozie_coordinator.id, app_path=oozie_coordinator.coordJobPath) }"
            >
              ${ _('Rerun') }
            </button>
            <div id="rerun-coord-modal" class="modal hide"></div>
            <button title="${ _('Suspend the coordinator after finishing the current running actions') }" id="suspend-btn"
               data-url="${ url('oozie:manage_oozie_jobs', job_id=oozie_coordinator.id, action='suspend') }"
               data-confirmation-message="${ _('Are you sure you\'d like to suspend this job?') }"
               class="btn btn-small confirmationModal
               % if not oozie_coordinator.is_running():
                 hide
               % endif
               " rel="tooltip" data-placement="right">
              ${ _('Suspend') }
            </button>
            <button title="${ _('Resume the coordinator') }" id="resume-btn"
               data-url="${ url('oozie:manage_oozie_jobs', job_id=oozie_coordinator.id, action='resume') }"
               data-confirmation-message="${ _('Are you sure you\'d like to resume this job?') }"
               class="btn btn-small confirmationModal
               % if oozie_coordinator.is_running():
                 hide
               % endif
               ">
              ${ _('Resume') }
            </button>
          </li>
        % endif
      </ul>
    </div>
  </div>
  <div class="span10">
    <h1 class="card-heading simple card-heading-nopadding card-heading-noborder card-heading-blue" style="margin-bottom: 10px">
      % if oozie_bundle:
        ${ _('Bundle') } <a href="${ oozie_bundle.get_absolute_url() }">${ oozie_bundle.appName }</a> :
      % endif
      ${ _('Coordinator') } ${ oozie_coordinator.appName }
    </h1>

    <ul class="nav nav-tabs">
      <li class="active"><a href="#calendar" data-toggle="tab">${ _('Calendar') }</a></li>
      <li><a href="#actions" data-toggle="tab">${ _('Actions') }</a></li>
      <li><a href="#details" data-toggle="tab">${ _('Details') }</a></li>
      <li><a href="#configuration" data-toggle="tab">${ _('Configuration') }</a></li>
      <li><a href="#log" data-toggle="tab">${ _('Log') }</a></li>
      <li><a href="#definition" data-toggle="tab">${ _('Definition') }</a></li>
      % if oozie_coordinator.has_sla:
      <li><a href="#sla" data-toggle="tab">${ _('SLA') }</a></li>
      % endif
    </ul>

    <div class="tab-content" style="min-height:200px">
      <div class="tab-pane active" id="calendar">
        <table class="table table-striped table-condensed">
          <thead>
          <tr>
            <th>${ _('Day') }</th>
            <th>${ _('Comment') }</th>
          </tr>
          </thead>
          <tbody data-bind="template: {name: 'calendarTemplate', foreach: actions}">
          </tbody>
          <tfoot>
            <tr>
              <td data-bind="visible: !isLoading() && paginate()" colspan="10">
                </br>
                <div class="alert">
                  ${ _('There are older actions to be shown:') }
                  <a class="btn" href="${ oozie_coordinator.get_absolute_url() }?show_all_actions=true">${ _('Expand') }</a>
                </div>
              </td>
            </tr>
            <tr data-bind="visible: isLoading()">
              <td colspan="2" class="left">
                <img src="/static/art/spinner.gif" />
              </td>
            </tr>
            <tr data-bind="visible: actions().length == 0 && !isLoading()">
              <td colspan="2">
                <div class="alert">
                  ${ _('There are no actions to be shown.') }
                </div>
              </td>
            </tr>
          </tfoot>
        </table>
      </div>

      <script id="calendarTemplate" type="text/html">
        <tr>
          <td>
            <a data-bind="attr: {href: url}" data-row-selector="true">
              <span data-bind="text: title, attr: {'class': statusClass, 'id': 'date-' + $index()}"></span>
            </a>
          </td>
          <td><span data-bind="text: errorMessage"></span> <span data-bind="visible:missingDependencies !='', text: '${ _('Missing')}' + missingDependencies"></span></td>
        </tr>
      </script>


      <div class="tab-pane" id="actions">
        <table class="table table-striped table-condensed" cellpadding="0" cellspacing="0">
          <thead>
          <tr>
            <th>${ _('Number') }</th>
            <th>${ _('Nominal Time') }</th>

            <th>${ _('Type') }</th>
            <th>${ _('Status') }</th>

            <th>${ _('Error Code') }</th>
            <th>${ _('Error Message') }</th>
            <th>${ _('Missing Dependencies') }</th>

            <th>${ _('Created Time') }</th>
            <th>${ _('Last Modified') }</th>

            <th>${ _('Id') }</th>
            <th>${ _('External Id') }</th>
          </tr>
          </thead>

          <tbody data-bind="template: {name: 'actionTemplate', foreach: actions}">
          </tbody>

          <tfoot>
          <tr data-bind="visible: isLoading()">
            <td colspan="10" class="left">
              <img src="/static/art/spinner.gif" />
            </td>
          </tr>
          <tr data-bind="visible: !isLoading() && actions().length == 0">
            <td colspan="10">
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
          <td data-bind="text: number"></td>
          <td data-bind="text: nominalTime"></td>
          <td data-bind="text: type"></td>
          <td><span data-bind="text: status, attr: {'class': statusClass}"></span></td>
          <td data-bind="text: errorCode"></td>
          <td data-bind="text: errorMessage"></td>
          <td data-bind="text: missingDependencies"></td>
          <td data-bind="text: createdTime"></td>
          <td data-bind="text: lastModifiedTime"></td>
          <td>
            <a data-bind="visible:externalId !='', attr: {href: url}, text: id" data-row-selector"true"></a>
          </td>
          <td>
            <a data-bind="visible:externalId !='', attr: {href: externalIdUrl}, text: externalId"></a>
          </td>
        </tr>
      </script>

      <div class="tab-pane" id="details">
        <table class="table table-condensed">
          <tbody>
            <tr>
              <td>${ _('Start time') }</td>
              <td>${ utils.format_time(oozie_coordinator.startTime) }</td>
            </tr>
            <tr>
              <td>${ _('End time') }</td>
              <td>${ utils.format_time(oozie_coordinator.endTime) }</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="tab-pane" id="configuration">
        ${ utils.display_conf(oozie_coordinator.conf_dict) }
      </div>

      <div class="tab-pane" id="log">
        <pre></pre>
      </div>

      <div class="tab-pane" id="definition">
        <textarea id="definitionEditor">${ oozie_coordinator.definition.decode('utf-8', 'replace') }</textarea>
      </div>

      % if oozie_coordinator.has_sla:
      <div class="tab-pane" id="sla" style="padding-left: 20px">
        <div id="yAxisLabel" class="hide">${_('Time since Nominal Time in min')}</div>
        <div id="slaChart"></div>
        <table id="slaTable" class="table table-striped table-condensed hide">
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
      <a href="${ url('oozie:list_oozie_coordinators') }" class="btn">${ _('Back') }</a>
    </div>

  </div>
</div>


  </p>
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
    <a class="btn btn-danger disable-feedback" href="javascript:void(0);">${_('Yes')}</a>
  </div>
</div>

<script src="/oozie/static/js/bundles.utils.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/codemirror-3.11.js"></script>
<link rel="stylesheet" href="/static/ext/css/codemirror.css">
<script src="/static/ext/js/codemirror-xml.js"></script>

% if oozie_coordinator.has_sla:
<script src="/static/ext/js/moment.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/oozie/static/js/sla.utils.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/jquery/plugins/jquery.flot.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/jquery/plugins/jquery.flot.selection.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/jquery/plugins/jquery.flot.time.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/js/jquery.blueprint.js"></script>
% endif

% if enable_cron_scheduling:
<link href="/static/css/jqCron.css" rel="stylesheet" type="text/css" />
<script src="/static/js/jqCron.js" type="text/javascript"></script>
% endif

<style type="text/css">
  .CodeMirror.cm-s-default {
    height:500px;
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
</style>

<script>

  var Action = function (action) {
    return {
      id: action.id,
      url: action.url,
      number: action.number,
      type: action.type,
      status: action.status,
      statusClass: "label " + getStatusClass(action.status),
      externalId: action.externalId,
      externalIdUrl: action.externalIdUrl,
      title: action.title,
      nominalTime: action.nominalTime,
      createdTime: action.createdTime,
      lastModifiedTime: action.lastModifiedTime,
      errorMessage: action.errorMessage,
      errorCode: action.errorCode,
      missingDependencies: action.missingDependencies
    }
  }

  var RunningCoordinatorActionsModel = function (actions) {
    var self = this;
    self.isLoading = ko.observable(true);
    self.actions = ko.observableArray(ko.utils.arrayMap(actions), function (action) {
      return new Action(action);
    });
    self.paginate = ko.computed(function(){
      return self.actions().length >= ${ MAX_COORD_ACTIONS } && ${ "false" if show_all_actions else 'true' | n,unicode };
    });
  };

  var viewModel = new RunningCoordinatorActionsModel([]);
  ko.applyBindings(viewModel);

  var CHART_LABELS = {
    NOMINAL_TIME: "${_('Nominal Time')}",
    EXPECTED_START: "${_('Expected Start')}",
    ACTUAL_START: "${_('Actual Start')}",
    EXPECTED_END: "${_('Expected End')}",
    ACTUAL_END: "${_('Actual End')}",
    TOOLTIP_ADDON: "${_('click for the SLA dashboard')}"
  }
  var slaTable;

  $(document).ready(function(){
    $("a[data-row-selector='true']").jHueRowSelector();

    $("*[rel=tooltip]").tooltip();

    % if enable_cron_scheduling:
      ${ utils.cron_js() }
      renderCrons();
    % endif

    $(".dataset").each(function () {
      if ($(this).text().length > 15) {
        $(this).html($(this).text().substr(0, 14) + "&hellip;");
      }
      $(this).removeClass("hide");
    });

    % if oozie_coordinator.has_sla:
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

    var definitionEditor = $("#definitionEditor")[0];

    var codeMirror = CodeMirror(function(elt) {
      definitionEditor.parentNode.replaceChild(elt, definitionEditor);
      }, {
        value: definitionEditor.value,
      readOnly: true,
      lineNumbers: true
    });

    // force refresh on tab change
    $("a[data-toggle='tab']").on("shown", function (e) {
      if ($(e.target).attr("href") == "#definition") {
        codeMirror.refresh();
      }
      % if oozie_coordinator.has_sla:
      if ($(e.target).attr("href") == "#sla") {
        window.setTimeout(function () {
          updateSLAChart(slaTable, CHART_LABELS, 30); // limits to 30 results
        }, 100)
      }
      % endif
    });

    $(".confirmationModal").click(function(){
      var _this = $(this);
      $("#confirmation .message").text(_this.attr("data-confirmation-message"));
      $("#confirmation").modal("show");
      $("#confirmation a.btn-danger").click(function() {
        _this.trigger('confirmation');
        $(this).attr("data-loading-text", $(this).text() + " ...");
        $(this).button("loading");
      });
    });

    $(".confirmationModal").bind('confirmation', function() {
      var _this = this;
      $.post($(this).attr("data-url"),
        { 'notification': $(this).attr("data-message") },
        function(response) {
          if (response['status'] != 0) {
            $(document).trigger("error", "${ _('Problem: ') }" + response['data']);
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

    $('#rerun-btn').click(function() {
      var _action = $(this).data("rerun-url");

      $.get(_action, function(response) {
          $('#rerun-coord-modal').html(response);
          $('#rerun-coord-modal').modal('show');
        }
      );
     });

    resizeLogs();
    refreshView();
    refreshLogs();

    var logsAtEnd = true;
    function refreshLogs() {
      $.getJSON("${ url('oozie:get_oozie_job_log', job_id=oozie_coordinator.id) }", function (data) {
        var _logsEl = $("#log pre");
        _logsEl.text(data.log);

        if (logsAtEnd) {
          _logsEl.scrollTop(_logsEl[0].scrollHeight - _logsEl.height());
        }
        if (data.status != "RUNNING" && data.status != "PREP"){
          return;
        }
        window.setTimeout(refreshLogs, 20000);
      });
    }

    function refreshView() {
      $.getJSON("${ oozie_coordinator.get_absolute_url(oozie_bundle=oozie_bundle, format='json') }" + "${ "&show_all_actions=true" if show_all_actions else '' | n,unicode }", function (data) {
        viewModel.isLoading(false);
        if (data.actions){
          viewModel.actions(ko.utils.arrayMap(data.actions, function (action) {
            return new Action(action);
          }));
        }

        $("#status span").attr("class", "label").addClass(getStatusClass(data.status)).text(data.status);

        $.jHueTitleUpdater.set(data.progress + "%");

        if (data.id && data.status != "RUNNING" && data.status != "SUSPENDED" && data.status != "KILLED" && data.status != "FAILED"){
          $("#kill-btn").hide();
        }

        if (data.id && data.status != "KILLED" && data.status != "FAILED"){
          $("#rerun-btn").show();
        } else {
          $("#rerun-btn").hide();
        }

        if (data.id && (data.status == "RUNNING" || data.status == "RUNNINGWITHERROR")){
          $("#suspend-btn").show();
        } else {
          $("#suspend-btn").hide();
        }

        if (data.id && (data.status == "SUSPENDED" || data.status == "SUSPENDEDWITHERROR" || data.status == "SUSPENDEDWITHERROR"
            || data.status == "PREPSUSPENDED")){
          $("#resume-btn").show();
          $.jHueTitleUpdater.reset();
        } else {
          $("#resume-btn").hide();
        }

        $("#progress .bar").text(data.progress + "%").css("width", data.progress + "%").attr("class", "bar " + getStatusClass(data.status, "bar-"));

        if (data.status != "RUNNING" && data.status != "PREP"){
          return;
        }
        window.setTimeout(refreshView, 5000);
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

    if (window.location.hash == "#showSla") {
      $("a[href='#sla']").click();
    }
  });
</script>

${ commonfooter(messages) | n,unicode }

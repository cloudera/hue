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
  import urllib
  from desktop.lib.paths import SAFE_CHARACTERS_URI_COMPONENTS
  from desktop.views import commonheader, commonfooter
  from django.utils.translation import ugettext as _

  from oozie.conf import ENABLE_V2
%>

<%namespace name="layout" file="../navigation-bar.mako" />
<%namespace name="utils" file="../utils.inc.mako" />

${ commonheader(_("Bundle Dashboard"), "oozie", user, request) | n,unicode }
${ layout.menubar(section='bundles', dashboard=True) }

<div class="container-fluid">
<div class="card card-small">
  <div class="card-body">
  <p>


<div class="row-fluid">
  <div class="span2">
    <div class="sidebar-nav">
      <ul class="nav nav-list" style="border:none">
        <li class="nav-header">${ _('Bundle') }</li>
        % if bundle is not None:
        <li><a href="${ bundle.get_absolute_url() }">${ oozie_bundle.appName }</a></li>
        % else:
        <li class="white">${ oozie_bundle.appName }</li>
        % endif

        <li class="nav-header">${ _('Submitter') }</li>
        <li class="white">${ oozie_bundle.user }</li>

        <li class="nav-header">${ _('Status') }</li>
        <li class="white" id="status"><span class="label ${ utils.get_status(oozie_bundle.status) }">${ oozie_bundle.status }</span></li>

        <li class="nav-header">${ _('Progress') }</li>
        <li class="white" id="progress">
          <div class="progress">
            <div class="bar" style="width: 0">${ oozie_bundle.get_progress() }%</div>
          </div>
        </li>

        <li class="nav-header">${ _('Kick off time') }</li>
        <li class="white">${ oozie_bundle.kickoffTime }</li>

        <li class="nav-header">${ _('Id') }</li>
        <li class="white">${ oozie_bundle.id }</li>

        % if bundle:
            <li class="nav-header">${ _('Coordinators') }</li>
          % if not ENABLE_V2.get():
            % for bundled in bundle.coordinators.distinct():
              <li rel="tooltip" title="${ bundled.coordinator.name }" class="white">
                <a href="${ bundled.coordinator.get_absolute_url() }">
                  <i class="fa fa-eye"></i> <span class="dataset">${ bundled.coordinator.name }</span>
                </a>
              </li>
            % endfor
          % else:
             % for coord in bundle.get_coordinator_objects():
              <li rel="tooltip" title="${ coord.name }" class="white">
                <a href="${ coord.get_absolute_url() }">
                  <i class="fa fa-eye"></i> <span class="dataset">${ coord.name }</span>
                </a>
              </li>
            % endfor
          % endif
        % endif

        % if has_job_edition_permission(oozie_bundle, user) and oozie_bundle.status not in ('KILLED', 'FAILED'):
          <li class="nav-header">${ _('Manage') }</li>
          <li class="white">
            <button title="${_('Kill %(bundle)s') % dict(bundle=oozie_bundle.id)}"
              id="kill-btn"
              class="btn btn-small btn-danger disable-feedback confirmationModal
               % if not oozie_bundle.is_running():
                 hide
               % endif
              "
              alt="${ _('Are you sure you want to kill bundle %s?') % oozie_bundle.id }"
              href="javascript:void(0)"
              data-url="${ url('oozie:manage_oozie_jobs', job_id=oozie_bundle.id, action='kill') }"
              data-message="${ _('The bundle was killed!') }"
              data-confirmation-message="${ _('Are you sure you\'d like to kill this job?') }" style="margin-bottom: 5px">
                ${_('Kill')}
            </button>
            <button class="btn btn-small
               % if oozie_bundle.status in ('KILLED', 'FAILED'):
                 hide
               % endif
            "
              id="rerun-btn"
              data-rerun-url="${ url('oozie:rerun_oozie_bundle', job_id=oozie_bundle.id, app_path=urllib.quote(oozie_bundle.bundleJobPath.encode('utf-8'), safe=SAFE_CHARACTERS_URI_COMPONENTS)) }"
            style="margin-bottom: 5px">
              ${ _('Rerun') }
            </button>
            <div id="rerun-coord-modal" class="modal hide"></div>
            <button title="${ _('Suspend the bundle after finishing the current running actions') }" id="suspend-btn"
               data-url="${ url('oozie:manage_oozie_jobs', job_id=oozie_bundle.id, action='suspend') }"
               data-confirmation-message="${ _('Are you sure you\'d like to suspend this job?') }"
               class="btn btn-small confirmationModal
               % if not oozie_bundle.is_running():
                 hide
               % endif
               " rel="tooltip" data-placement="right" style="margin-bottom: 5px">
              ${ _('Suspend') }
            </button>
            <button title="${ _('Resume the bundle') }" id="resume-btn"
               data-url="${ url('oozie:manage_oozie_jobs', job_id=oozie_bundle.id, action='resume') }"
               data-confirmation-message="${ _('Are you sure you\'d like to resume this job?') }"
               class="btn btn-small confirmationModal
               % if oozie_bundle.is_running():
                 hide
               % endif
               " style="margin-bottom: 5px">
              ${ _('Resume') }
            </button>
          </li>
        % endif
      </ul>
    </div>
  </div>
  <div class="span10">
    <h1 class="card-heading simple card-heading-nopadding card-heading-noborder card-heading-blue" style="margin-bottom: 10px">${ _('Bundle') } ${ oozie_bundle.appName }</h1>
    <ul class="nav nav-tabs">
      <li class="active"><a href="#calendar" data-toggle="tab">${ _('Coordinators') }</a></li>
      <li><a href="#actions" data-toggle="tab">${ _('Actions') }</a></li>
      <li><a href="#details" data-toggle="tab">${ _('Details') }</a></li>
      <li><a href="#configuration" data-toggle="tab">${ _('Configuration') }</a></li>
      <li><a href="#log" data-toggle="tab">${ _('Log') }</a></li>
      <li><a href="#definition" data-toggle="tab">${ _('Definition') }</a></li>
    </ul>

    <div class="tab-content" style="min-height:200px">
      <div class="tab-pane active" id="calendar">
        <table class="table table-condensed">
          <thead>
          <tr>
            <th>${ _('Coordinator') }</th>
            <th>${ _('Last action') }</th>
            <th>${ _('Next materialization') }</th>
          </tr>
          </thead>
          <tbody data-bind="template: {name: 'calendarTemplate', foreach: actions}">
          </tbody>
          <tfoot>
            <tr data-bind="visible: isLoading()">
              <td colspan="3" class="left">
                <i class="fa fa-spinner fa-spin"></i>
              </td>
            </tr>
            <tr data-bind="visible: actions().length == 0 && !isLoading()">
              <td colspan="3">
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
              <span data-bind="text: name, attr: {'class': statusClass, 'id': 'date-' + $index()}"></span>
            </a>
          </td>
          <td><span data-bind="text: lastAction"></span></td>
          <td><span data-bind="text: nextMaterializedTime"></span></td>
        </tr>
      </script>


      <div class="tab-pane" id="actions">
        <table class="table table-condensed" cellpadding="0" cellspacing="0">
          <thead>
          <tr>
            <th>${ _('Name') }</th>
            <th>${ _('Id') }</th>

            <th>${ _('Last action') }</th>

            <th>${ _('Frequency') }</th>
            <th>${ _('Time Unit') }</th>

            <th>${ _('Acl') }</th>

            <th>${ _('Type') }</th>
            <th>${ _('Status') }</th>

            <th>${ _('Time out') }</th>
            <th>${ _('Start Time') }</th>

            <th>${ _('End Time') }</th>
            <th>${ _('Pause Time') }</th>
          </tr>
          </thead>

          <tbody data-bind="template: {name: 'actionTemplate', foreach: actions}">
          </tbody>

          <tfoot>
          <tr data-bind="visible: isLoading()">
            <td colspan="10" class="left">
              <i class="fa fa-spinner fa-spin"></i>
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
          <td>
            <a data-bind="visible:name !='', attr: {href: url}, text: name"></a>
          </td>
          <td>
            <a data-bind="visible:externalId !='', attr: {href: url}, text: id" data-row-selector"true"></a>
          </td>
          <td data-bind="text: lastAction"></td>
          <td data-bind="text: frequency"></td>
          <td data-bind="text: timeUnit"></td>
          <td data-bind="text: acl"></td>
          <td data-bind="text: type"></td>
          <td><span data-bind="text: status, attr: {'class': statusClass}"></span></td>
          <td data-bind="text: timeOut"></td>
          <td data-bind="text: startTime"></td>
          <td data-bind="text: endTime"></td>
          <td data-bind="text: pauseTime"></td>
        </tr>
      </script>

      <div class="tab-pane" id="details">
        <table class="table table-condensed">
          <tbody>
            <tr>
              <td>${ _('Created time') }</td>
              <td>${ oozie_bundle.createdTime }</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="tab-pane" id="configuration">
        ${ utils.display_conf(oozie_bundle.conf_dict) }
      </div>

      <div class="tab-pane" id="log">
        <pre></pre>
      </div>

      <div class="tab-pane" id="definition">
        <div id="definitionEditor">${ oozie_bundle.definition.decode('utf-8', 'replace') }</div>
      </div>
    </div>

    <div style="margin-bottom: 16px">
      <a href="${ url('oozie:list_oozie_bundles') }" class="btn">${ _('Back') }</a>
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

<style type="text/css">
  #definitionEditor {
    min-height: 250px;
    margin-bottom: 10px;
  }
</style>

<script>

  var Action = function (action) {
    return {
      id: action.id,
      url: action.url,
      name: action.name,
      type: action.type,
      status: action.status,
      statusClass: "label " + getStatusClass(action.status),
      externalId: action.externalId,
      frequency: action.frequency,
      timeUnit: action.timeUnit,
      concurrency: action.concurrency,
      pauseTime: action.pauseTime,
      acl: action.acl,
      user: action.user,
      timeOut: action.timeOut,
      coordJobPath: action.coordJobPath,
      executionPolicy: action.executionPolicy,
      startTime: action.startTime,
      endTime: action.endTime,
      lastAction: action.lastAction,
      nextMaterializedTime: action.nextMaterializedTime
    }
  }

  var RunningCoordinatorActionsModel = function (actions) {
    var self = this;
    self.isLoading = ko.observable(true);
    self.actions = ko.observableArray(ko.utils.arrayMap(actions), function (action) {
      return new Action(action);
    });
  };

  var viewModel = new RunningCoordinatorActionsModel([]);
  ko.applyBindings(viewModel);

  $(document).ready(function(){
    $("a[data-row-selector='true']").jHueRowSelector();

    $("*[rel=tooltip]").tooltip();

    $(".dataset").each(function () {
      if ($(this).text().length > 15) {
        $(this).html($(this).text().substr(0, 14) + "&hellip;");
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
      $.getJSON("${ url('oozie:get_oozie_job_log', job_id=oozie_bundle.id) }", function (data) {
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
      $.getJSON("${ oozie_bundle.get_absolute_url(format='json') }", function (data) {
        viewModel.isLoading(false);
        if (data.actions){
          viewModel.actions(ko.utils.arrayMap(data.actions, function (action) {
            return new Action(action);
          }));
        }

        $("#status span").attr("class", "label").addClass(getStatusClass(data.status)).text(data.status);

        $.jHueTitleUpdater.set(data.progress + "%");

        if (data.id && (data.status == "KILLED" || data.status == "SUCCEEDED" ||  data.status == "DONEWITHERROR" || data.status == "FAILED")) {
          $("#kill-btn").hide();
        } else {
          $("#kill-btn").show();
        }

        if (data.id && (data.status == "KILLED" || data.status == "FAILED" ||  data.status == "PREP" || data.status == "PREPPAUSED" || data.status == "PREPSUSPENDED")) {
          $("#rerun-btn").hide();
        } else {
          $("#rerun-btn").show();
        }

        if (data.id && (data.status == "RUNNING" || data.status == "RUNNINGWITHERROR")){
          $("#suspend-btn").show();
          $.jHueTitleUpdater.reset();
        } else {
          $("#suspend-btn").hide();
        }

        if (data.id && (data.status == "SUSPENDED" || data.status == "SUSPENDEDWITHERROR" || data.status == "SUSPENDEDWITHERROR"
            || data.status == "PREPSUSPENDED")){
          $("#resume-btn").show();
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
  });
</script>

${ commonfooter(request, messages) | n,unicode }

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

${ commonheader(_("Bundle Dashboard"), "oozie", user, "100px") | n,unicode }
${ layout.menubar(section='dashboard') }


<div class="container-fluid">
  ${ layout.dashboard_sub_menubar(section='bundles') }

  <h1>${ _('Bundle') } ${ oozie_bundle.appName }</h1>


<div class="row-fluid">
  <div class="span2">
    <div class="well sidebar-nav">
      <ul class="nav nav-list">
        <li class="nav-header">${ _('Bundle') }</li>
        <li>
            % if bundle is not None:
              <a href="${ bundle.get_absolute_url() }">${ oozie_bundle.appName }</a>
            % else:
              ${ oozie_bundle.appName }
            % endif
        </li>

        <li class="nav-header">${ _('Submitter') }</li>
        <li>${ oozie_bundle.user }</li>

        <li class="nav-header">${ _('Status') }</li>
        <li id="status"><span class="label ${ utils.get_status(oozie_bundle.status) }">${ oozie_bundle.status }</span></li>

        <li class="nav-header">${ _('Progress') }</li>
        <li id="progress">
          <div class="progress">
            <div class="bar" style="width: 0">${ oozie_bundle.get_progress() }%</div>
          </div>
        </li>

        <li class="nav-header">${ _('Kick off time') }</li>
        <li>${ oozie_bundle.kickoffTime }</li>

        <li class="nav-header">${ _('Id') }</li>
        <li>${ oozie_bundle.id }</li>

        % if bundle:
            <li class="nav-header">${ _('Coordinators') }</li>
          % for bundled in bundle.coordinators.all():
            <li rel="tooltip" title="${ bundled.coordinator.name }">
              <i class="icon-eye-open"></i> <span class="dataset">${ bundled.coordinator.name }</span>
            </li>
          % endfor
        % endif

        % if has_job_edition_permission(oozie_bundle, user):
          <li class="nav-header">${ _('Manage') }</li>
          <li>
            <button title="${_('Kill %(bundle)s') % dict(bundle=oozie_bundle.id)}"
              id="kill-btn"
              class="btn btn-small confirmationModal
               % if not oozie_bundle.is_running():
                 hide
               % endif
              "
              alt="${ _('Are you sure you want to kill bundle %s?') % oozie_bundle.id }"
              href="javascript:void(0)"
              data-url="${ url('oozie:manage_oozie_jobs', job_id=oozie_bundle.id, action='kill') }"
              data-message="${ _('The bundle was killed!') }"
              data-confirmation-message="${ _('Are you sure you\'d like to kill this job?') }">
                ${_('Kill')}
            </button>
            <button class="btn btn-small
               % if oozie_bundle.is_running() or oozie_bundle.status in ('KILLED', 'FAILED'):
                 hide
               % endif
            "
              id="rerun-btn"
              data-rerun-url="${ url('oozie:rerun_oozie_bundle', job_id=oozie_bundle.id, app_path=oozie_bundle.bundleJobPath) }"
            >
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
               " rel="tooltip" data-placement="right">
              ${ _('Suspend') }
            </button>
            <button title="${ _('Resume the bundle') }" id="resume-btn"
               data-url="${ url('oozie:manage_oozie_jobs', job_id=oozie_bundle.id, action='resume') }"
               data-confirmation-message="${ _('Are you sure you\'d like to resume this job?') }"
               class="btn btn-small confirmationModal
               % if oozie_bundle.is_running():
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
    <ul class="nav nav-tabs">
      <li class="active"><a href="#calendar" data-toggle="tab">${ _('Coordinators') }</a></li>
      <li><a href="#actions" data-toggle="tab">${ _('Actions') }</a></li>
      <li><a href="#details" data-toggle="tab">${ _('Details') }</a></li>
      <li><a href="#configuration" data-toggle="tab">${ _('Configuration') }</a></li>
      <li><a href="#log" data-toggle="tab">${ _('Log') }</a></li>
      <li><a href="#definition" data-toggle="tab">${ _('Definition') }</a></li>
    </ul>

    <div class="tab-content" style="padding-bottom:200px">
      <div class="tab-pane active" id="calendar">
        <table class="table table-striped table-condensed">
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
              <span data-bind="text: name, attr: {'class': statusClass, 'id': 'date-' + $index()}"></span>
            </a>
          </td>
          <td><span data-bind="text: lastAction"></span></td>
          <td><span data-bind="text: nextMaterializedTime"></span></td>
        </tr>
      </script>


      <div class="tab-pane" id="actions">
        <table class="table table-striped table-condensed" cellpadding="0" cellspacing="0">
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
        <pre>${ oozie_bundle.log.decode('utf-8', 'replace') }</pre>
      </div>

      <div class="tab-pane" id="definition">
        <textarea id="definitionEditor">${ oozie_bundle.definition.decode('utf-8', 'replace') }</textarea>
      </div>
    </div>

    <div style="margin-bottom: 16px">
      <a href="${ url('oozie:list_oozie_bundles') }" class="btn">${ _('Back') }</a>
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
<script src="/static/ext/js/knockout-2.1.0.js" type="text/javascript" charset="utf-8"></script>
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
    });

    $(".confirmationModal").click(function(){
      var _this = $(this);
      $("#confirmation .message").text(_this.attr("data-confirmation-message"));
      $("#confirmation").modal("show");
      $("#confirmation a.btn-danger").click(function() {
        _this.trigger('confirmation');
      });
    });

    $(".confirmationModal").bind('confirmation', function() {
      var _this = this;
      $.post($(this).attr("data-url"),
        { 'notification': $(this).attr("data-message") },
        function(response) {
          if (response['status'] != 0) {
            $.jHueNotify.error("${ _('Problem: ') }" + response['data']);
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
    var logsAtEnd = true;

    function refreshView() {
      $.getJSON("${ oozie_bundle.get_absolute_url() }" + "?format=json", function (data) {
        viewModel.isLoading(false);
        if (data.actions){
          viewModel.actions(ko.utils.arrayMap(data.actions, function (action) {
            return new Action(action);
          }));
        }

        $("#status span").attr("class", "label").addClass(getStatusClass(data.status)).text(data.status);

        if (data.id && data.status != "RUNNING" && data.status != "SUSPENDED" && data.status != "KILLED" && data.status != "FAILED"){
          $("#kill-btn").hide();
          $("#rerun-btn").show();
        }

        if (data.id && data.status == "KILLED") {
          $("#kill-btn").hide();
        }

        if (data.id && (data.status == "RUNNING" || data.status == "RUNNINGWITHERROR")){
          $("#suspend-btn").show();
        } else {
          $("#suspend-btn").hide();
        }

        if (data.id && (data.status == "SUSPENDED" || data.status == "SUSPENDEDWITHERROR" || data.status == "SUSPENDEDWITHERROR"
            || data.status == "PREPSUSPENDED")){
          $("#resume-btn").show();
        } else {
          $("#resume-btn").hide();
        }

        $("#progress .bar").text(data.progress+"%").css("width", data.progress+"%").attr("class", "bar "+getStatusClass(data.status, "bar-"));

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

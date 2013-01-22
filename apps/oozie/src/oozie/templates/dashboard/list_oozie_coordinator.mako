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

${ commonheader(_("Oozie App"), "oozie", user, "100px") | n,unicode }
${ layout.menubar(section='dashboard') }


<div class="container-fluid">
  ${ layout.dashboard_sub_menubar(section='coordinators') }

  <h1>${ _('Coordinator') } ${ oozie_coordinator.appName }</h1>


<div class="row-fluid">
  <div class="span2">
    <div class="well sidebar-nav">
      <ul class="nav nav-list">
        <li class="nav-header">${ _('Coordinator') }</li>
        <li>
            % if coordinator is not None:
              <a href="${ coordinator.get_absolute_url() }">${ oozie_coordinator.appName }</a>
            % else:
            ${ oozie_coordinator.appName }
            % endif
        </li>

        <li class="nav-header">${ _('Submitter') }</li>
        <li>${ oozie_coordinator.user }</li>

        <li class="nav-header">${ _('Status') }</li>
        <li id="status"><span class="label ${ utils.get_status(oozie_coordinator.status) }">${ oozie_coordinator.status }</span></li>

        <li class="nav-header">${ _('Progress') }</li>
        <li id="progress">
          <div class="progress">
            <div class="bar" style="width: 0">${ oozie_coordinator.get_progress() }%</div>
          </div>
        </li>

        <li class="nav-header">${ _('Frequency') }</li>
        <li>${ oozie_coordinator.frequency } ${ oozie_coordinator.timeUnit }</li>

        <li class="nav-header">${ _('Next Materialized Time') }</li>
        <li id="nextTime">${ utils.format_time(oozie_coordinator.nextMaterializedTime) }</li>

        <li class="nav-header">${ _('Start time') }</li>
        <li>${ utils.format_time(oozie_coordinator.startTime) }</li>

        <li class="nav-header">${ _('End time') }</li>
        <li id="endTime">${ utils.format_time(oozie_coordinator.endTime) }</li>

        % if coordinator:
            <li class="nav-header">${ _('Datasets') }</li>
          % for dataset in coordinator.dataset_set.all():
            <li rel="tooltip" title="${ dataset.name } : ${ dataset.uri }"><i class="icon-eye-open"></i> <span class="dataset">${ dataset.name }</span></li>
          % endfor
        % endif

        % if has_job_edition_permission(oozie_coordinator, user):
          <li class="nav-header">${ _('Manage') }</li>
          <li>
          <form action="${ url('oozie:resubmit_coordinator', oozie_coord_id=oozie_coordinator.id) }" method="post">
              <button type="button" title="${_('Kill %(coordinator)s') % dict(coordinator=oozie_coordinator.id)}"
                 id="kill-btn"
                 class="btn btn-small btn-danger confirmationModal"
                 alt="${ _('Are you sure you want to kill coordinator %s?') % oozie_coordinator.id }"
                 href="javascript:void(0)"
                 data-url="${ url('oozie:manage_oozie_jobs', job_id=oozie_coordinator.id, action='kill') }"
                 data-message="${ _('The coordinator was killed!') }"
                 data-confirmation-message="${ _('Are you sure you\'d like to kill this job?') }">
              ${_('Kill')}
              </button>
              <button id="resubmit-btn" type="submit" class="btn btn-small
              % if oozie_coordinator.is_running():
                hide
              % endif
              ">
              ${ _('Resubmit') }
              </button>
          </form>
          </li>
        % endif
      </ul>
    </div>
  </div>
  <div class="span10">
    <ul class="nav nav-tabs">
      <li class="active"><a href="#calendar" data-toggle="tab">${ _('Calendar') }</a></li>
      <li><a href="#actions" data-toggle="tab">${ _('Actions') }</a></li>
      <li><a href="#configuration" data-toggle="tab">${ _('Configuration') }</a></li>
      <li><a href="#log" data-toggle="tab">${ _('Log') }</a></li>
      <li><a href="#definition" data-toggle="tab">${ _('Definition') }</a></li>
    </ul>

    <div class="tab-content" style="padding-bottom:200px">
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
            <a data-bind="visible:externalId !='', attr: { href: externalIdUrl}" data-row-selector="true"></a>
            <span data-bind="text: nominalTime, attr: {'class': statusClass}"></span>
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

            <th>${ _('Error Message') }</th>
            <th>${ _('Missing Dependencies') }</th>

            <th>${ _('Created Time') }</th>
            <th>${ _('Last Modified Time') }</th>

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
          <td data-bind="text: errorMessage"></td>
          <td data-bind="text: missingDependencies"></td>
          <td data-bind="text: createdTime"></td>
          <td data-bind="text: lastModifiedTime"></td>

          <td>
            <a data-bind="visible:externalId !='', attr: { href: url}, text: id" data-row-selector"true"></a>
          </td>

          <td>
            <a data-bind="visible:externalId !='', attr: { href: externalIdUrl}, text: externalId"></a>
          </td>

        </tr>

      </script>

      <div class="tab-pane" id="configuration">
        ${ utils.display_conf(oozie_coordinator.conf_dict) }
      </div>

      <div class="tab-pane" id="log">
        <pre>${ oozie_coordinator.log }</pre>
      </div>

      <div class="tab-pane" id="definition">
        <textarea id="definitionEditor">${ oozie_coordinator.definition }</textarea>
      </div>
    </div>

    <div style="margin-bottom: 16px">
      <a href="${ url('oozie:list_oozie_coordinators') }" class="btn">${ _('Back') }</a>
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

<script src="/static/ext/js/knockout-2.1.0.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/codemirror-3.0.js"></script>
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
  function getStatusClass(status, prefix){
    if(!Array.prototype.indexOf) {
      Array.prototype.indexOf = function(needle) {
        for(var i = 0; i < this.length; i++) {
          if(this[i] === needle) {
            return i;
          }
        }
        return -1;
      };
    }
    if (prefix == null){
      prefix = "label-";
    }
    var klass = "";
    if (['SUCCEEDED', 'OK'].indexOf(status) > -1){
      klass = prefix + "success";
    }
    else if (['RUNNING', 'PREP', 'WAITING', 'SUSPENDED', 'PREPSUSPENDED', 'PREPPAUSED', 'PAUSED'].indexOf(status) > -1){
      klass = prefix + "warning";
    }
    else if (status == 'READY'){
      klass = prefix + "success";
    }
    else {
      klass = prefix + "important";
      if (prefix == "bar-"){
        klass = prefix + "danger";
      }
    }
    return klass;
  }

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
      nominalTime: action.nominalTime,
      createdTime: action.createdTime,
      lastModifiedTime: action.lastModifiedTime,
      errorMessage: action.errorMessage,
      missingDependencies: action.missingDependencies
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

    resizeLogs();
    refreshView();
    var logsAtEnd = true;

    function refreshView() {
      $.getJSON(window.location.href + "?format=json", function (data) {
        viewModel.isLoading(false);
        if (data.actions){
          viewModel.actions(ko.utils.arrayMap(data.actions, function (action) {
            return new Action(action);
          }));
        }

        $("#status span").attr("class", "label").addClass(getStatusClass(data.status)).text(data.status);

        if (data.id && data.status != "RUNNING" && data.status != "SUSPENDED"){
          $("#kill-btn").hide();
          $("#resubmit-btn").show();
        }

        $("#progress .bar").text(data.progress+"%").css("width", data.progress+"%").attr("class", "bar "+getStatusClass(data.status, "bar-"));

        var _logsEl = $("#log pre");
        var newLines = data.log.split("\n").slice(_logsEl.text().split("\n").length);
        _logsEl.text(_logsEl.text() + newLines.join("\n"));
        if (logsAtEnd) {
          _logsEl.scrollTop(_logsEl[0].scrollHeight - _logsEl.height());
        }
        if (data.status != "RUNNING"){
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

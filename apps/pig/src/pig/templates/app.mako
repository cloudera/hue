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

<%namespace name="actionbar" file="actionbar.mako" />

${ commonheader(_('Pig'), "pig", user, "100px") | n,unicode }

<div class="subnav subnav-fixed">
  <div class="container-fluid">
    <ul class="nav nav nav-pills">
      <li class="active"><a href="#editor">${ _('Editor') }</a></li>
      <li><a href="#scripts">${ _('Scripts') }</a></li>
      <li><a href="#dashboard">${ _('Dashboard') }</a></li>
      ##<li class="${utils.is_selected(section, 'udfs')}"><a href="${ url('pig:udfs') }">${ _('UDF') }</a></li>
      </ul>
  </div>
</div>


<div class="container-fluid">
  <div id="scripts" class="row-fluid mainSection hide">
    <%actionbar:render>
      <%def name="search()">
          <input id="filter" type="text" class="input-xlarge search-query" placeholder="${_('Search for script name or content')}">
      </%def>

      <%def name="actions()">
          <button class="btn fileToolbarBtn" title="${_('Run this script')}" data-bind="enable: selectedScripts().length == 1, click: listRunScript, visible: scripts().length > 0"><i class="icon-play"></i> ${_('Run')}</button>
          <button class="btn fileToolbarBtn" title="${_('Copy this script')}" data-bind="enable: selectedScripts().length == 1, click: listCopyScript, visible: scripts().length > 0"><i class="icon-retweet"></i> ${_('Copy')}</button>
          <button class="btn fileToolbarBtn" title="${_('Delete this script')}" data-bind="enable: selectedScripts().length > 0, click: listConfirmDeleteScripts, visible: scripts().length > 0"><i class="icon-trash"></i> ${_('Delete')}</button>
      </%def>

      <%def name="creation()">
          <button class="btn fileToolbarBtn" title="${_('Create a new script')}" data-bind="click: newScript"><i class="icon-plus-sign"></i> ${_('New script')}</button>
      </%def>
    </%actionbar:render>
    <div class="alert alert-info" data-bind="visible: scripts().length == 0">
      ${_('There are currently no scripts defined. Please add a new script clicking on "New script"')}
    </div>

    <table class="table table-striped table-condensed tablescroller-disable" data-bind="visible: scripts().length > 0">
      <thead>
      <tr>
        <th width="1%"><div data-bind="click: selectAll, css: {hueCheckbox: true, 'icon-ok': allSelected}"></div></th>
        <th width="20%">${_('Name')}</th>
        <th width="79%">${_('Script')}</th>
      </tr>
      </thead>
      <tbody id="scriptTable" data-bind="template: {name: 'scriptTemplate', foreach: filteredScripts}">

      </tbody>
      <tfoot>
      <tr data-bind="visible: isLoading()">
        <td colspan="3" class="left">
          <img src="/static/art/spinner.gif" />
        </td>
      </tr>
      <tr data-bind="visible: filteredScripts().length == 0 && !isLoading()">
        <td colspan="3">
          <div class="alert">
              ${_('There are no scripts matching the search criteria.')}
          </div>
        </td>
      </tr>
      </tfoot>
    </table>

    <script id="scriptTemplate" type="text/html">
      <tr style="cursor: pointer" data-bind="event: { mouseover: toggleHover, mouseout: toggleHover}">
        <td class="center" data-bind="click: handleSelect" style="cursor: default">
          <div data-bind="css: {hueCheckbox: true, 'icon-ok': selected}"></div>
        </td>
        <td data-bind="click: $root.viewScript">
          <strong><a href="#" data-bind="click: $root.viewScript, text: name"></a></strong>
        </td>
        <td data-bind="click: $root.viewScript">
          <span data-bind="text: scriptSumup"></span>
        </td>
      </tr>
    </script>
  </div>

  <div id="editor" class="row-fluid mainSection hide">
    <div class="span2">
      <div class="well sidebar-nav">
        <form id="advancedSettingsForm" method="POST" class="form form-horizontal noPadding">
          <ul class="nav nav-list">
            <li class="nav-header">${_('Editor')}</li>
            <li data-bind="click: editScript" class="active" data-section="edit">
              <a href="#"><i class="icon-edit"></i> ${ _('Edit script') }</a>
            </li>
            <li data-bind="click: newScript">
              <a href="#" title="${ _('New script') }" rel="tooltip" data-placement="right">
                <i class="icon-plus-sign"></i> ${ _('New script') }
              </a>
            </li>
            <li class="nav-header">${_('Properties')}</li>
            <li data-bind="click: editScriptProperties" data-section="properties">
              <a href="#"><i class="icon-reorder"></i> ${ _('Edit properties') }</a>
            </li>
            ##<li class="nav-header">${_('UDF')}</li>
            ##<li><a href="#createDataset">${ _('New') }</a></li>
            ##<li><a href="#createDataset">${ _('Add') }</a></li>
            <li class="nav-header">${_('Actions')}</li>
            <li data-bind="click: saveScript">
              <a href="#" title="${ _('Save the script') }" rel="tooltip" data-placement="right">
                <i class="icon-save"></i> ${ _('Save') }
              </a>
            </li>
            <li data-bind="click: showSubmissionModal, visible: !currentScript().isRunning()">
              <a href="#" title="${ _('Run the script') }" rel="tooltip" data-placement="right">
                <i class="icon-play"></i> ${ _('Run') }
              </a>
            </li>
            <li data-bind="visible: currentScript().isRunning()">
              <a href="#" title="${ _('Run the script') }" rel="tooltip" data-placement="right" class="disabled">
                <i class="icon-spinner icon-spin"></i> ${ _('Running...') }
              </a>
            </li>
            <li data-bind="visible: currentScript().id() != -1, click: copyScript">
              <a href="#" title="${ _('Copy the script') }" rel="tooltip" data-placement="right">
                <i class="icon-retweet"></i> ${ _('Copy') }
              </a>
            </li>
            <li data-bind="visible: currentScript().id() != -1, click: confirmDeleteScript">
              <a href="#" title="${ _('Delete the script') }" rel="tooltip" data-placement="right">
                <i class="icon-trash"></i> ${ _('Delete') }
              </a>
            </li>
            <li class="nav-header" data-bind="visible: currentScript().isRunning()">${_('Logs')}</li>
            <li data-bind="visible: currentScript().isRunning(), click: showScriptLogs" data-section="logs">
              <a href="#" title="${ _('Show Logs') }" rel="tooltip" data-placement="right">${ _('Current Logs') }</a>
            </li>
          </ul>
        </form>
      </div>
    </div>

    <div class="span10">
      <div id="edit" class="section">
        <div class="alert alert-info"><h3>${ _('Edit') } '<span data-bind="text: currentScript().name"></span>'</h3></div>
        <form id="queryForm">
          <textarea id="scriptEditor" data-bind="text:currentScript().script"></textarea>
        </form>
      </div>

      <div id="properties" class="section hide">
        <div class="alert alert-info"><h3>${ _('Edit properties for') } '<span data-bind="text: currentScript().name"></span>'</h3></div>
         <form class="form-inline" style="padding-left: 10px">
          <label>
            ${ _('Script name') } &nbsp;
            <input type="text" id="scriptName" class="input-xlarge" data-bind="value: currentScript().name" />
          </label>
          <br/>
          <br/>
          <label>${ _('Parameters') } &nbsp;
            <button class="btn" data-bind="click: currentScript().addParameter, visible: currentScript().parameters().length == 0" style="margin-left: 4px">
              <i class="icon-plus"></i> ${ _('Add') }
            </button>
          </label>
          <div>
            <table data-bind="css: {'parameterTable': currentScript().parameters().length > 0}">
              <thead data-bind="visible: currentScript().parameters().length > 0">
                <tr>
                  <th>${ _('Name') }</th>
                  <th>${ _('Value') }</th>
                  <th>&nbsp;</th>
                </tr>
              </thead>
              <tbody data-bind="foreach: currentScript().parameters">
                <tr>
                  <td><input type="text" data-bind="value: name" class="input-large" /></td>
                  <td><input type="text" data-bind="value: value" class="input-large" /></td>
                  <td><button data-bind="click: viewModel.currentScript().removeParameter" class="btn"><i class="icon-trash"></i> ${ _('Remove') }</button></td>
                </tr>
              </tbody>
              <tfoot data-bind="visible: currentScript().parameters().length > 0">
                <tr>
                  <td colspan="3">
                    <button class="btn" data-bind="click: currentScript().addParameter"><i class="icon-plus"></i> ${ _('Add') }</button>
                  </td>
                </tr>
              </tfoot>
            </table>
          </div>
        </form>
      </div>

      <div id="logs" class="section hide">
        <div class="alert alert-info"><h3>${ _('Logs for') } '<span data-bind="text: currentScript().name"></span>'</h3></div>
        <div data-bind="visible: currentScript().actions().length == 0">
          <img src="/static/art/spinner.gif" />
        </div>
        <div data-bind="template: {name: 'logTemplate', foreach: currentScript().actions}"></div>
        <script id="logTemplate" type="text/html">
          <div data-bind="css:{'alert-modified': name != '', 'alert': name != '', 'alert-success': status == 'SUCCEEDED' || status == 'OK', 'alert-error': status != 'RUNNING' && status != 'SUCCEEDED' && status != 'OK' && status != 'PREP'}">
            <div class="pull-right" data-bind="text: status"></div>
              <h4>${ _('Progress:') } <span data-bind="text: progress"></span>${ _('%') }</h4>
              <div data-bind="css: {'progress': name != '', 'progress-striped': name != '', 'active': status == 'RUNNING'}" style="margin-top:10px">
                <div data-bind="css: {'bar': name != '', 'bar-success': status == 'SUCCEEDED' || status == 'OK', 'bar-warning': status == 'RUNNING' || status == 'PREP', 'bar-danger': status != 'RUNNING' && status != 'SUCCEEDED' && status != 'OK' && status != 'PREP'}, attr: {'style': 'width:' + progressPercent}"></div>
              </div>
          </div>
          <pre data-bind="visible: logs == ''">${ _('No available logs.') }</pre>
          <pre data-bind="visible: logs != '', text: logs"></pre>
        </script>
      </div>
    </div>

  </div>

  <div id="dashboard" class="row-fluid mainSection hide">
    <h3>Running</h3>
    <div class="alert alert-info" data-bind="visible: runningScripts().length == 0">
      ${_('There are currently no running scripts.')}
    </div>
    <table class="table table-striped table-condensed datatables tablescroller-disable" data-bind="visible: runningScripts().length > 0">
      <thead>
      <tr>
        <th width="20%">${_('Name')}</th>
        <th width="10%">${_('Status')}</th>
        <th width="">${_('Created on')}</th>
      </tr>
      </thead>
      <tbody data-bind="template: {name: 'dashboardTemplate', foreach: runningScripts}">

      </tbody>
    </table>

    <h3>Completed</h3>
    <div class="alert alert-info" data-bind="visible: completedScripts().length == 0">
      ${_('There are currently no completed scripts.')}
    </div>
    <table class="table table-striped table-condensed datatables tablescroller-disable" data-bind="visible: completedScripts().length > 0">
      <thead>
      <tr>
        <th width="20%">${_('Name')}</th>
        <th width="20%">${_('Status')}</th>
        <th width="">${_('Created on')}</th>
      </tr>
      </thead>
      <tbody data-bind="template: {name: 'dashboardTemplate', foreach: completedScripts}">

      </tbody>
    </table>

    <script id="dashboardTemplate" type="text/html">
      <tr style="cursor: pointer">
        <td data-bind="click: $root.viewSubmittedScript" title="${_('Click to edit')}">
          <strong><a data-bind="text: appName"></a></strong>
        </td>
        <td>
          <span data-bind="attr: {'class': statusClass}, text: status"></span>
        </td>
        <td>
          <strong><a data-bind="text: created, attr: {'href': absoluteUrl}" target="_blank"></a></strong>
        </td>
      </tr>
    </script>
  </div>
</div>


<div id="deleteModal" class="modal hide fade">
  <div class="modal-header">
    <a href="#" class="close" data-dismiss="modal">&times;</a>
    <h3>${_('Confirm Delete')}</h3>
  </div>
  <div class="modal-body">
    <p class="deleteMsg hide single">${_('Are you sure you want to delete this script?')}</p>
    <p class="deleteMsg hide multiple">${_('Are you sure you want to delete these scripts?')}</p>
  </div>
  <div class="modal-footer">
    <a class="btn" data-dismiss="modal">${_('No')}</a>
    <a class="btn btn-danger" data-bind="click: deleteScripts">${_('Yes')}</a>
  </div>
</div>


<div id="submitModal" class="modal hide fade">
  <div class="modal-header">
    <a href="#" class="close" data-dismiss="modal">&times;</a>
    <h3>${_('Submit Script')} '<span data-bind="text: currentScript().name"></span>' ${_('?')}</h3>
  </div>
  <div class="modal-body" data-bind="visible: submissionVariables().length > 0">
    <legend style="color:#666">${_('Script variables')}</legend>
    <div data-bind="foreach: submissionVariables" style="margin-bottom: 20px">
      <div class="row-fluid">
        <span data-bind="text: name" class="span3"></span>
        <input type="text" data-bind="value: value" class="span9" />
      </div>
    </div>
  </div>
  <div class="modal-footer">
    <a class="btn" data-dismiss="modal">${_('No')}</a>
    <a class="btn btn-danger" data-bind="click: runScript">${_('Yes')}</a>
  </div>
</div>


<div class="bottomAlert alert"></div>

<script src="/static/ext/js/knockout-2.1.0.js" type="text/javascript" charset="utf-8"></script>
<script src="/pig/static/js/utils.js" type="text/javascript" charset="utf-8"></script>
<script src="/pig/static/js/pig.ko.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/routie-0.3.0.min.js" type="text/javascript" charset="utf-8"></script>
<link rel="stylesheet" href="/pig/static/css/pig.css">
<script src="/static/ext/js/codemirror-3.11.js"></script>
<link rel="stylesheet" href="/static/ext/css/codemirror.css">
<script src="/static/ext/js/codemirror-pig.js"></script>
<script src="/static/ext/js/codemirror-show-hint.js"></script>
<script src="/static/js/Source/jHue/codemirror-pig-hint.js"></script>
<link rel="stylesheet" href="/static/ext/css/codemirror-show-hint.css">


<script type="text/javascript" charset="utf-8">

  var LABELS = {
    KILL_ERROR: "${ _('The pig job could not be killed.') }",
    TOOLTIP_PLAY: "${ _('Run this pig script') }",
    TOOLTIP_STOP: "${ _('Stop the execution') }",
    SAVED: "${ _('Saved') }",
    NEW_SCRIPT_NAME: "${ _('Unsaved script') }",
    NEW_SCRIPT_CONTENT: "ie. A = LOAD '/user/${ user }/data';",
    NEW_SCRIPT_PARAMETERS: []
  };

  var scripts = ${ scripts | n,unicode };

  var appProperties = {
    labels: LABELS,
    listScripts: "${ url('pig:scripts') }",
    saveUrl: "${ url('pig:save') }",
    runUrl: "${ url('pig:run') }",
    copyUrl: "${ url('pig:copy') }",
    deleteUrl: "${ url('pig:delete') }"
  }

  var viewModel = new PigViewModel(scripts, appProperties);
  ko.applyBindings(viewModel);

  $(document).ready(function () {

    var scriptEditor = $("#scriptEditor")[0];

    CodeMirror.commands.autocomplete = function(cm) {
      CodeMirror.showHint(cm, CodeMirror.pigHint);
    }
    var codeMirror = CodeMirror(function (elt) {
      scriptEditor.parentNode.replaceChild(elt, scriptEditor);
    }, {
      value: scriptEditor.value,
      readOnly: false,
      lineNumbers: true,
      mode: "text/x-pig",
      extraKeys: {"Shift-Space": "autocomplete"}
    });

    codeMirror.on("focus", function () {
      if (codeMirror.getValue() == LABELS.NEW_SCRIPT_CONTENT) {
        codeMirror.setValue("");
      }
    });

    codeMirror.on("change", function () {
      viewModel.currentScript().script(codeMirror.getValue());
    });

    showMainSection("editor");

    $(document).on("loadEditor", function () {
      codeMirror.setValue(viewModel.currentScript().script());
    });

    $(document).on("showEditor", function () {
      if (viewModel.currentScript().id() != -1) {
        routie("edit/" + viewModel.currentScript().id());
      }
      else {
        routie("edit");
      }
    });

    $(document).on("showProperties", function () {
      if (viewModel.currentScript().id() != -1) {
        routie("properties/" + viewModel.currentScript().id());
      }
      else {
        routie("properties");
      }
    });

    $(document).on("showLogs", function () {
      if (viewModel.currentScript().id() != -1) {
        routie("logs/" + viewModel.currentScript().id());
      }
      else {
        routie("logs");
      }
    });

    $(document).on("updateTooltips", function () {
      $("a[rel=tooltip]").tooltip("destroy");
      $("a[rel=tooltip]").tooltip();
    });

    $(document).on("saving", function () {
      showAlert("${_('Saving')} <b>" + viewModel.currentScript().name() + "</b>...");
    });

    $(document).on("running", function () {
      showAlert("${_('Running')} <b>" + viewModel.currentScript().name() + "</b>...", "info");
    });

    $(document).on("saved", function () {
      showAlert("<b>" + viewModel.currentScript().name() + "</b> ${_('has been saved correctly.')}", "success");
    });

    $(document).on("error", function () {
      showAlert("<b>${_('There was an error with your request!')}</b>", "error");
    });

    $(document).on("refreshDashboard", function () {
      refreshDashboard();
    });

    $(document).on("showDashboard", function () {
      routie("dashboard");
    });

    $(document).on("showScripts", function () {
      routie("scripts");
    });

    $(document).on("scriptsRefreshed", function () {
      $("#filter").val("");
    });

    var logsRefreshInterval;
    $(document).on("startLogsRefresh", function () {
      logsRefreshInterval = window.setInterval(function () {
        refreshLogs();
      }, 1000);
    });

    $(document).on("stopLogsRefresh", function () {
      window.clearTimeout(logsRefreshInterval);
    });

    var _resizeTimeout = -1;
    $(window).on("resize", function () {
      window.clearTimeout(_resizeTimeout);
      _resizeTimeout = window.setTimeout(function () {
        codeMirror.setSize("100%", $(window).height() - 250);
      }, 100);
    });

    var _filterTimeout = -1;
    $("#filter").on("keyup", function () {
      window.clearTimeout(_filterTimeout);
      _filterTimeout = window.setTimeout(function () {
        viewModel.filterScripts($("#filter").val());
      }, 350);
    });

    viewModel.filterScripts('');

    refreshDashboard();

    var dashboardRefreshInterval = window.setInterval(function () {
      if (viewModel.runningScripts().length > 0) {
        refreshDashboard();
      }
    }, 1000);

    function refreshDashboard() {
      $.getJSON("${ url('pig:dashboard') }", function (data) {
        viewModel.updateDashboard(data);
      });
    }

    function refreshLogs() {
      if (viewModel.currentScript().watchUrl() != "") {
        $.getJSON(viewModel.currentScript().watchUrl(), function (data) {
          if (data.workflow && data.workflow.isRunning) {
            viewModel.currentScript().actions(data.workflow.actions);
          }
          else {
            viewModel.currentScript().actions(data.workflow.actions);
            viewModel.currentScript().isRunning(false);
            $(document).trigger("stopLogsRefresh");
            //$(document).trigger("showEditor");
          }
        });
      }
      else {
        $(document).trigger("stopLogsRefresh");
      }
    }

    function showMainSection(mainSection) {
      window.setTimeout(function () {
        codeMirror.refresh();
        codeMirror.setSize("100%", $(window).height() - 250);
      }, 100);

      if ($("#" + mainSection).is(":hidden")) {
        $(".mainSection").hide();
        $("#" + mainSection).show();
        highlightMainMenu(mainSection);
      }
    }

    function showSection(mainSection, section) {
      showMainSection(mainSection);
      if ($("#" + section).is(":hidden")) {
        $(".section").hide();
        $("#" + section).show();
        highlightMenu(section);
      }
    }

    function highlightMainMenu(mainSection) {
      $(".nav-pills li").removeClass("active");
      $("a[href='#" + mainSection + "']").parent().addClass("active");
    }

    function highlightMenu(section) {
      $(".nav-list li").removeClass("active");
      $("li[data-section='" + section + "']").addClass("active");
    }

    routie({
      "editor": function () {
        showMainSection("editor");
      },
      "scripts": function () {
        showMainSection("scripts");
      },
      "dashboard": function () {
        showMainSection("dashboard");
      },

      "edit": function () {
        showSection("editor", "edit");
      },
      "edit/:scriptId": function (scriptId) {
        if (scriptId !== "undefined" && scriptId != viewModel.currentScript().id()) {
          viewModel.loadScript(scriptId);
          $(document).trigger("loadEditor");
        }
        showSection("editor", "edit");
      },
      "properties": function () {
        showSection("editor", "properties");
      },
      "properties/:scriptId": function (scriptId) {
        if (scriptId !== "undefined" && scriptId != viewModel.currentScript().id()) {
          viewModel.loadScript(scriptId);
          $(document).trigger("loadEditor");
        }
        showSection("editor", "properties");
      },
      "logs": function () {
        showSection("editor", "logs");
      },
      "logs/:scriptId": function (scriptId) {
        if (scriptId !== "undefined" && scriptId != viewModel.currentScript().id()) {
          viewModel.loadScript(scriptId);
          $(document).trigger("loadEditor");
        }
        showSection("editor", "logs");
      }
    });

  });

  var _bottomAlertFade = -1;
  function showAlert(msg, extraClass) {
    var klass = "alert ";
    if (extraClass != null && extraClass != undefined) {
      klass += "alert-" + extraClass;
    }
    $(".bottomAlert").attr("class", "bottomAlert " + klass).html(msg).show();
    window.clearTimeout(_bottomAlertFade);
    _bottomAlertFade = window.setTimeout(function () {
      $(".bottomAlert").fadeOut();
    }, 3000);
  }
</script>

${ commonfooter(messages) | n,unicode }

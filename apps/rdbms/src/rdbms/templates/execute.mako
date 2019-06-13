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
  from desktop.views import commonheader, commonfooter, commonshare, _ko
  from django.utils.translation import ugettext as _
%>

<%namespace name="common" file="common.mako" />

${ commonheader(_('Query'), app_name, user, request) | n,unicode }

<%common:navbar></%common:navbar>

<div id="rdbms-query-editor">
  <div class="container-fluid">
    <div class="panel-container">
      <div class="left-panel" id="navigator">
        <ul class="nav nav-tabs" style="margin-bottom: 0">
          <li class="active"><a href="#navigatorTab" data-toggle="tab" class="sidetab">${ _('Assist') }</a></li>
        </ul>

        <div class="tab-content">
      <div class="tab-pane active" id="navigatorTab">
        <div class="card card-small card-tab" style="min-height: 470px;">
          <div class="card-body" style="margin-top: 0">
            <a href="#" title="${_('Double click on a table name or field to insert it in the editor')}" rel="tooltip" data-placement="left" class="pull-right" style="margin:10px;margin-left: 0"><i class="fa fa-question-circle"></i></a>
            <a id="refreshNavigator" href="#" title="${_('Manually refresh the table list')}" rel="tooltip" data-placement="left" class="pull-right" style="margin:10px"><i class="fa fa-refresh"></i></a>

            <ul class="nav nav-list" style="border: none; padding: 0; background-color: #FFF">
              <li class="nav-header">${_('server')}</li>
            </ul>

            <select data-bind="options: $root.servers, value: $root.chosenServer, optionsText: 'nice_name'" class="input-medium chosen-select chosen-server" data-placeholder="${_('Choose a database...')}"></select>

            <ul class="nav nav-list" style="border: none; padding: 0; background-color: #FFF">
              <li class="nav-header">${_('database')}</li>
            </ul>

            <select data-bind="options: $root.databases, value: $root.chosenDatabase" class="input-medium chosen-select chosen-db" data-placeholder="${_('Choose a database...')}"></select>

            <input id="navigatorSearch" type="text" placeholder="${ _('Table name...') }" style="width:90%; margin-top: 20px"/>
            <div id="navigatorNoTables" style="margin-top: 20px">${_('The selected database has no tables.')}</div>
            <ul id="navigatorTables" class="unstyled"></ul>
            <div id="navigatorLoader">
              <i class="fa fa-spinner fa-spin" style="font-size: 20px; color: #DDD"></i>
            </div>
          </div>
        </div>
      </div>

    </div>


      </div>
      <div class="resizer" data-bind="splitDraggable : { appName: 'rdbms', leftPanelVisible: true }"><div class="resize-bar"><i class="fa fa-ellipsis-v"></i></div></div>
      <div class="content-panel">
        <div id="query">
          <div class="card card-small">

            <div class="pull-right" style="
            % if can_edit_name:
              margin: 10px
            % else:
              margin-top: -6px; margin-right: 8px
            % endif
            ">
              <a id="collapse-editor" href="javascript:void(0)"><i class="fa fa-caret-up"></i></a>
            </div>
            <div style="margin-bottom: 10px">
              % if can_edit_name:
              <h1 class="card-heading simple">
                <a class="share-link" rel="tooltip" data-placement="bottom" style="padding-left:10px; padding-right: 10px" data-bind="click: openShareModal,
                  attr: {'data-original-title': '${ _ko("Share") } '+name},
                  css: {'baseShared': true, 'isShared': isShared()}">
                  <i class="fa fa-users"></i>
                </a>
                <a href="javascript:void(0);"
                   id="query-name"
                   data-type="text"
                   data-name="name"
                   data-value="${design.name}"
                   data-original-title="${ _('Query name') }"
                   data-placement="right">
                </a>
                <a href="javascript:void(0);"
                   id="query-description"
                   data-type="textarea"
                   data-name="description"
                   data-value="${design.desc}"
                   data-original-title="${ _('Query description') }"
                   data-placement="right" style="font-size: 14px; margin-left: 10px">
                </a>
              </h1>
              % endif
            </div>
            <div class="card-body">
              <div class="tab-content">
                <div id="queryPane">

                  <div data-bind="css: {'hide': query.errors().length == 0}" class="hide alert alert-error">
                    <p><strong>${_('Your query has the following error(s):')}</strong></p>
                    <div data-bind="foreach: { 'data': query.errors, 'afterRender': resizeTable }">
                      <p data-bind="text: $data" class="queryErrorMessage"></p>
                    </div>
                  </div>

                  <textarea class="hide" tabindex="1" name="query" id="queryField"></textarea>

                  <div class="actions">
                    <button data-bind="click: tryExecuteQuery" type="button" id="executeQuery" class="btn btn-primary disable-feedback" tabindex="2">${_('Execute')}</button>
                    <button data-bind="click: trySaveQuery, css: {'hide': !$root.query.id() || $root.query.id() == -1}" type="button" class="btn hide">${_('Save')}</button>
                    <button data-bind="click: trySaveAsQuery" type="button" class="btn">${_('Save as...')}</button>
                    <button data-bind="click: tryExplainQuery" type="button" id="explainQuery" class="btn">${_('Explain')}</button>
                    &nbsp; ${_('or create a')} &nbsp;<a type="button" class="btn" href="${ url('rdbms:execute_query') }">${_('New query')}</a>
                    <br /><br />
                </div>

                </div>
              </div>
            </div>
          </div>
        </div>
        <div data-bind="css: {'hide': rows().length == 0}" class="hide">
          <div class="card card-small scrollable">
            <table id="resultTable" class="table table-condensed resultTable" cellpadding="0" cellspacing="0" data-tablescroller-min-height-disable="true" data-tablescroller-enforce-height="true">
              <thead>
                <tr data-bind="foreach: columns">
                  <th data-bind="text: $data, css:{'datatables-counter-col': $index() == 0}"></th>
                </tr>
              </thead>
            </table>
          </div>
        </div>

        <div data-bind="css: {'hide': !resultsEmpty()}" class="hide">
          <div class="card card-small scrollable">
            <div class="row-fluid">
              <div class="span10 offset1 center empty-wrapper">
                <h1>${_('The server returned no results.')}</h1>
                <br />
              </div>
            </div>
          </div>
        </div>

        <div data-bind="css: {'hide': !isExecuting()}" class="hide">
          <div class="card card-small scrollable">
            <div class="row-fluid">
              <div class="span10 offset1 center" style="padding: 30px">
                <i class="fa fa-spinner fa-spin" style="font-size: 60px; color: #DDD"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>


  <div id="saveAsQueryModal" class="modal hide fade">
    <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
      <h2 class="modal-title">${_('Save your query')}</h2>
    </div>
    <div class="modal-body">
      <form class="form-horizontal">
        <div class="control-group" id="saveas-query-name">
          <label class="control-label">${_('Name')}</label>
          <div class="controls">
            <input data-bind="value: $root.query.name" type="text" class="input-xlarge">
          </div>
        </div>
        <div class="control-group">
          <label class="control-label">${_('Description')}</label>
          <div class="controls">
            <input data-bind="value: $root.query.description" type="text" class="input-xlarge">
          </div>
        </div>
      </form>
    </div>
    <div class="modal-footer">
      <button class="btn" data-dismiss="modal">${_('Cancel')}</button>
      <button data-bind="click: modalSaveAsQuery" class="btn btn-primary">${_('Save')}</button>
    </div>
  </div>
</div>

${ commonshare() | n,unicode }



<style type="text/css">
  h1 {
    margin-bottom: 5px;
  }

  .panel-container {
    width: 100%;
    position: relative;
  }

  .left-panel {
    position: absolute;
    outline: none !important;
  }

  .resizer {
    position: absolute;
    width: 20px;
    text-align: center;
    z-index: 1000;
  }

  .resize-bar {
    top: 50%;
    position: relative;
    cursor: ew-resize;
  }

  .content-panel {
    position: absolute;
    outline: none !important;
  }

  #filechooser {
    min-height: 100px;
    overflow-y: auto;
  }

  .control-group {
    margin-bottom: 3px!important;
  }

  .control-group label {
    float: left;
    padding-top: 5px;
    text-align: left;
    width: 40px;
  }

  .hue-breadcrumbs {
    padding: 12px 14px;
  }

  .hue-breadcrumbs-bar {
    padding: 0;
    margin: 12px;
  }

  .hue-breadcrumbs-bar a {
    color: #0B7FAD !important;
    display: inline !important;
  }

  .divider {
    color: #CCC;
  }

  .param {
    padding: 8px 8px 1px 8px;
    margin-bottom: 5px;
    border-bottom: 1px solid #EEE;
  }

  .remove {
    float: right;
  }

  .selectable {
    display: block;
    list-style: none;
    padding: 5px;
    background: white;
    cursor: pointer;
  }

  .selected, .selectable:hover {
    background: #DDDDDD;
  }

  .CodeMirror {
    border: 1px solid #eee;
    margin-bottom: 20px;
  }

  .editorError {
    color: #B94A48;
    background-color: #F2DEDE;
    padding: 4px;
    font-size: 11px;
  }

  .editable-empty, .editable-empty:hover {
    color: #666;
    font-style: normal;
  }

  .tooltip.left {
    margin-left: -13px;
  }

  .scrollable {
    overflow-x: auto;
  }

  .resultTable td, .resultTable th {
    white-space: nowrap;
  }

  #navigatorTables {
    margin: 4px;
  }

  #navigatorTables li div {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  #navigatorSearch, #navigatorNoTables {
    display: none;
  }

  #navigatorNoTables {
    padding: 6px;
  }

  #navigator .card-body {
    margin-top: 1px !important;
    padding: 6px !important;
  }

  #navigator .nav-header {
    padding-left: 0;
  }

  #navigator .control-group {
    padding-left: 0;
  }

  #navigator .nav-list > li.white, #navigator .nav-list .nav-header {
    margin: 0;
  }

</style>

<script src="${ static('rdbms/js/rdbms.vm.js') }"></script>
<script src="${ static('desktop/js/share.vm.js') }"></script>
<script src="${ static('desktop/ext/js/codemirror-3.11.js') }"></script>
<link rel="stylesheet" href="${ static('desktop/ext/css/codemirror.css') }">
<script src="${ static('desktop/ext/js/codemirror-sql.js') }"></script>
<script src="${ static('desktop/js/codemirror-sql-hint.js') }"></script>
<script src="${ static('desktop/js/codemirror-show-hint.js') }"></script>

<link href="${ static('desktop/ext/css/bootstrap-editable.css') }" rel="stylesheet">

<script src="${ static('desktop/ext/js/jquery/plugins/jquery-fieldselection.js') }" type="text/javascript"></script>
<script src="${ static('rdbms/js/autocomplete.utils.js') }" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript">
  var codeMirror, viewModel;

  var RDBMS_AUTOCOMPLETE_BASE_URL = '/rdbms/api';
  var RDBMS_AUTOCOMPLETE_FAILS_SILENTLY_ON = [500, 404]; // error codes from rdbms/views.py - autocomplete
  var RDBMS_AUTOCOMPLETE_GLOBAL_CALLBACK = $.noop;

  $(document).ready(function(){

    var queryPlaceholder = "${_('Example: SELECT * FROM tablename, or press CTRL + space')}";

    $("*[rel=tooltip]").tooltip({
      placement: 'bottom'
    });

    $("#navigatorSearch").jHueDelayedInput(function(){
      $("#navigatorTables li").removeClass("hide");
      $("#navigatorTables li").each(function () {
        if ($(this).text().toLowerCase().indexOf($("#navigatorSearch").val().toLowerCase()) == -1) {
          $(this).addClass("hide");
        }
      });
    });

    $("#navigatorTables").css("max-height", ($(window).height() - 340) + "px").css("overflow-y", "auto");

    var resizeTimeout = -1;

    var resizeNavigator = function() {
      $("#navigatorTables").css("max-height", ($(window).height() - 380) + "px").css("overflow-y", "auto");
      $(".resizer").css("height", ($(window).height() - 110) + "px");
    }

    $(window).on("resize", function () {
      codeMirror.setSize("95%", 100);
      resizeNavigator();
    });
    resizeNavigator();

    var queryEditor = $("#queryField")[0];

    var AUTOCOMPLETE_SET = CodeMirror.sqlHint;

    CodeMirror.onAutocomplete = function (data, from, to) {
      if (CodeMirror.tableFieldMagic) {
        codeMirror.replaceRange(" ", from, from);
        codeMirror.setCursor(from);
        codeMirror.execCommand("autocomplete");
      }
    };

    CodeMirror.commands.autocomplete = function (cm) {
      $(document.body).on("contextmenu", function (e) {
        e.preventDefault(); // prevents native menu on FF for Mac from being shown
      });

      var pos = cm.cursorCoords();
      $(".CodeMirror-spinner").remove();
      $("<i class='fa fa-spinner fa-spin CodeMirror-spinner'></i>").css("top", pos.top + "px").css("left", (pos.left - 4) + "px").appendTo(HUE_CONTAINER);

      if ($.totalStorage('rdbms_tables_' + viewModel.server().name() + "_" + viewModel.database()) == null) {
        CodeMirror.showHint(cm, AUTOCOMPLETE_SET);
        rdbms_getTables(viewModel.server().name(), viewModel.database(), function () {
        }); // if preload didn't work, tries again
      }
      else {
        rdbms_getTables(viewModel.server().name(), viewModel.database(), function (tables) {
          CodeMirror.catalogTables = tables;
          var _before = codeMirror.getRange({line: 0, ch: 0}, {line: codeMirror.getCursor().line, ch: codeMirror.getCursor().ch}).replace(/(\r\n|\n|\r)/gm, " ");
          CodeMirror.possibleTable = false;
          CodeMirror.tableFieldMagic = false;
          if (_before.toUpperCase().indexOf(" FROM ") > -1 && _before.toUpperCase().indexOf(" ON ") == -1 && _before.toUpperCase().indexOf(" WHERE ") == -1) {
            CodeMirror.possibleTable = true;
          }
          CodeMirror.possibleSoloField = false;
          if (_before.toUpperCase().indexOf("SELECT ") > -1 && _before.toUpperCase().indexOf(" FROM ") == -1 && !CodeMirror.fromDot) {
            if (codeMirror.getValue().toUpperCase().indexOf("FROM ") > -1) {
              fieldsAutocomplete(cm);
            }
            else {
              CodeMirror.tableFieldMagic = true;
              CodeMirror.showHint(cm, AUTOCOMPLETE_SET);
            }
          }
          else {
            if (_before.toUpperCase().indexOf("WHERE ") > -1 && !CodeMirror.fromDot && _before.match(/ON|GROUP|SORT/) == null) {
              fieldsAutocomplete(cm);
            }
            else {
              CodeMirror.showHint(cm, AUTOCOMPLETE_SET);
            }
          }
        });
      }
    }

    function fieldsAutocomplete(cm) {
      CodeMirror.possibleSoloField = true;
      try {
        var _possibleTables = $.trim(codeMirror.getValue(" ").substr(codeMirror.getValue().toUpperCase().indexOf("FROM ") + 4)).split(" ");
        var _foundTable = "";
        for (var i = 0; i < _possibleTables.length; i++) {
          if ($.trim(_possibleTables[i]) != "" && _foundTable == "") {
            _foundTable = _possibleTables[i];
          }
        }
        if (_foundTable != "") {
          if (rdbms_tableHasAlias(viewModel.server().name(), _foundTable, codeMirror.getValue())) {
            CodeMirror.possibleSoloField = false;
            CodeMirror.showHint(cm, AUTOCOMPLETE_SET);
          }
          else {
            rdbms_getTableColumns(viewModel.server().name(), viewModel.database(), _foundTable, codeMirror.getValue(),
                    function (columns) {
                      CodeMirror.catalogFields = columns;
                      CodeMirror.showHint(cm, AUTOCOMPLETE_SET);
                    });
          }
        }
      }
      catch (e) {
      }
    }

    CodeMirror.fromDot = false;

    codeMirror = CodeMirror(function (elt) {
      queryEditor.parentNode.replaceChild(elt, queryEditor);
    }, {
      value: queryEditor.value,
      readOnly: false,
      lineNumbers: true,
      mode: "text/x-sql",
      extraKeys: {
        "Ctrl-Space": function () {
          CodeMirror.fromDot = false;
          codeMirror.execCommand("autocomplete");
        },
        Tab: function (cm) {
          $("#executeQuery").focus();
        }
      },
      onKeyEvent: function (e, s) {
        if (s.type == "keyup") {
          if (s.keyCode == 190) {
            var _line = codeMirror.getLine(codeMirror.getCursor().line);
            var _partial = _line.substring(0, codeMirror.getCursor().ch);
            var _table = _partial.substring(_partial.lastIndexOf(" ") + 1, _partial.length - 1);
            if (codeMirror.getValue().toUpperCase().indexOf("FROM") > -1) {
              rdbms_getTableColumns(viewModel.server().name(), viewModel.database(), _table, codeMirror.getValue(),
                      function (columns) {
                        var _cols = columns.split(" ");
                        for (var col in _cols) {
                          _cols[col] = "." + _cols[col];
                        }
                        CodeMirror.catalogFields = _cols.join(" ");
                        CodeMirror.fromDot = true;
                        window.setTimeout(function () {
                          codeMirror.execCommand("autocomplete");
                        }, 100);  // timeout for IE8
                      });
            }
          }
        }
      }
    });

    var selectedLine = -1;
    var errorWidget = null;
    if ($(".queryErrorMessage").length > 0) {
      var err = $(".queryErrorMessage").text().toLowerCase();
      var firstPos = err.indexOf("line");
      selectedLine = $.trim(err.substring(err.indexOf(" ", firstPos), err.indexOf(":", firstPos))) * 1;
      errorWidget = codeMirror.addLineWidget(selectedLine - 1, $("<div>").addClass("editorError").html("<i class='fa fa-exclamation-circle'></i> " + err)[0], {coverGutter: true, noHScroll: true})
    }


    codeMirror.setSize("95%", 100);

    codeMirror.on("focus", function () {
      if (codeMirror.getValue() == queryPlaceholder) {
        codeMirror.setValue("");
      }
      if (errorWidget) {
        errorWidget.clear();
      }
      $("#validationResults").empty();
    });

    codeMirror.on("blur", function () {
      $(document.body).off("contextmenu");
    });

    codeMirror.on("change", function () {
      $(".query").val(codeMirror.getValue());
    });

    $("#help").popover({
      'title': "${_('Did you know?')}",
      'content': $("#help-content").html(),
      'trigger': 'hover',
      'html': true
    });

    $("#collapse-editor").on("click", function () {
      if ($("#query .card-body").is(":visible")) {
        $("#query .card-body").slideUp(100, function () {
          $(".dataTables_wrapper").jHueTableScroller();
          $(".resultTable").jHueTableExtender({
            hintElement: "#jumpToColumnAlert",
            fixedHeader: true,
            firstColumnTooltip: true
          });
        });
        $("#collapse-editor i").removeClass("fa-caret-up").addClass("fa-caret-down");
      }
      else {
        $("#query .card-body").slideDown(100, function () {
          $(".dataTables_wrapper").jHueTableScroller();
          $(".resultTable").jHueTableExtender({
            hintElement: "#jumpToColumnAlert",
            fixedHeader: true,
            firstColumnTooltip: true
          });
        });
        $("#collapse-editor i").removeClass("fa-caret-down").addClass("fa-caret-up");
      }
    });


    $(document).on("update.chosen", function(){
      $(".chosen-select").trigger("chosen:updated");
    });

  });

  function modal(el) {
    var el = $(el);
    return function() {
      el.modal('show');
    };
  }

  function getHighlightedQuery() {
    var selection = codeMirror.getSelection();
    if (selection != "") {
      return selection;
    }
    return null;
  }

  function tryExecuteQuery() {
    var query = getHighlightedQuery() || codeMirror.getValue();
    viewModel.query.query(query);
    viewModel.executeQuery();
  }

  function tryExplainQuery() {
    var query = getHighlightedQuery() || codeMirror.getValue();
    viewModel.query.query(query);
    viewModel.explainQuery();
  }

  function trySaveQuery() {
    var query = codeMirror.getValue();
    viewModel.query.query(query);
    if (viewModel.query.id() && viewModel.query.id() != -1) {
      viewModel.saveQuery();
    }
  }

  function trySaveAsQuery() {
    var query = getHighlightedQuery() || codeMirror.getValue();
    viewModel.query.query(query);
    $('#saveAsQueryModal').modal('show');
  }

  function modalSaveAsQuery() {
    if (viewModel.query.query() && viewModel.query.name()) {
      viewModel.query.id(-1);
      viewModel.saveQuery();
      $('#saveas-query-name').removeClass('error');
      $('#saveAsQueryModal').modal('hide');
    } else if (viewModel.query.name()) {
      $.jHueNotify.error("${_('No query provided to save.')}");
      $('#saveAsQueryModal').modal('hide');
    } else {
      $('#saveas-query-name').addClass('error');
    }
  }

  function checkLastDatabase(server, database) {
    var key = "hueRdbmsLastDatabase-" + server;
    if (database != $.totalStorage(key)) {
      $.totalStorage(key, database);
    }
  }

  function getLastDatabase(server) {
    var key = "hueRdbmsLastDatabase-" + server;
    return $.totalStorage(key);
  }

  $(".chosen-server").chosen({
      disable_search_threshold: 5,
      width: "100%",
      no_results_text: "${_('Oops, no server found!')}"
  });

  $(".chosen-db").chosen({
      disable_search_threshold: 5,
      width: "100%",
      no_results_text: "${_('Oops, no database found!')}"
    }).change(function (e, value) {
    if (value != null){
      var key = 'hueRdbmsLastDatabase-' + viewModel.server().name();
      viewModel.selectedDatabase(viewModel.databases.indexOf(value.selected));
      $.totalStorage(key, value.selected);
    }
  });

  // Knockout
  viewModel = new RdbmsViewModel();
  shareViewModel = initSharing("#documentShareModal");
  shareViewModel.setDocId(${doc_id});

  viewModel.fetchServers();
  viewModel.database.subscribe((function() {
    // First call skipped to avoid reset of hueRdbmsLastDatabase
    var counter = 0;
    return function(value) {
      % if design.id:
        if (counter++ == 0) {
          viewModel.fetchQuery(${design.id});
        }
      % endif
      renderNavigator();
    }
  })());
  viewModel.query.query.subscribe((function() {
    // First call skipped to avoid reset of hueRdbmsLastDatabase
    var counter = 0;
    return function(value) {
      if (counter++ == 0) {
        codeMirror.setValue(value);
      }
    }
  })());
  function resizeTable() {
    $(".resultTable").jHueTableExtender({
      hintElement: "#jumpToColumnAlert",
      fixedHeader: true,
      firstColumnTooltip: true
    });

    $("#executeQuery").button("reset");
  }
  ko.applyBindings(viewModel, $("#rdbms-query-editor")[0]);

  function resetNavigator() {
    renderNavigator();
  }

  function renderNavigator() {
    $("#navigatorTables").empty();
    $("#navigatorLoader").show();
    rdbms_getTables(viewModel.server().name(), viewModel.database(), function (data) {  //preload tables for the default db
      $(data.split(" ")).each(function (cnt, table) {
        if ($.trim(table) != "") {
          var _table = $("<li>");
          _table.html("<a href='#' title='" + table + "' class='nowrap'><i class='fa fa-table'></i> " + table + "</a><ul class='unstyled'></ul>");
          _table.data("table", table).attr("id", "navigatorTables_" + table);
          _table.find("a").on("dblclick", function () {
            codeMirror.replaceSelection($.trim($(this).text()) + ' ');
            codeMirror.setSelection(codeMirror.getCursor());
            codeMirror.focus();
          });
          _table.find("a").on("click", function () {
            if (_table.find("li").length > 0){
              _table.find("ul").empty();
            }
            else {
              _table.find(".fa-table").removeClass("fa-table").addClass("fa-spin").addClass("fa-spinner");
              rdbms_getTableColumns(viewModel.server().name(), viewModel.database(), table, "", function (columns) {
                _table.find("ul").empty();
                _table.find(".fa-spinner").removeClass("fa-spinner").removeClass("fa-spin").addClass("fa-table");
                $(columns.split(" ")).each(function (iCnt, col) {
                  if ($.trim(col) != "" && $.trim(col) != "*") {
                    var _column = $("<li>");
                    _column.html("<a href='#' style='padding-left:10px'><i class='fa fa-columns'></i> " + col + "</a>");
                    _column.appendTo(_table.find("ul"));
                    _column.on("dblclick", function () {
                      codeMirror.replaceSelection($.trim(col) + ', ');
                      codeMirror.setSelection(codeMirror.getCursor());
                      codeMirror.focus();
                    });
                  }
                });
              });
            }
          });
          _table.find("a:eq(2)").on("dblclick", function () {
            codeMirror.replaceSelection($.trim(table) + ' ');
            codeMirror.setSelection(codeMirror.getCursor());
            codeMirror.focus();
          });
          _table.appendTo($("#navigatorTables"));
        }
      });
      $("#navigatorLoader").hide();
      if ($("#navigatorTables li").length > 0) {
        $("#navigatorSearch").show();
        $("#navigatorNoTables").hide();
      }
      else {
        $("#navigatorSearch").hide();
        $("#navigatorNoTables").show();
      }
    });
  }

  $("#refreshNavigator").on("click", function () {
    resetNavigator();
  });

  // Editables
  $("#query-name").editable({
    validate: function (value) {
      if ($.trim(value) == '') {
        return "${ _('This field is required.') }";
      }
    },
    success: function(response, newValue) {
      viewModel.query.name(newValue);
    },
    emptytext: "${ _('Query name') }"
  });

  $("#query-description").editable({
    success: function(response, newValue) {
      viewModel.query.description(newValue);
    },
    emptytext: "${ _('Empty description') }"
  });


  // Events and datatables
  $(document).on('saved.query', function() {
    $.jHueNotify.info("${_('Query saved successfully!')}")
  });

  // Initial htmlEscape
  String.prototype.htmlEscape = function() {
    return $('<div/>').text(this.toString()).html();
  };

  var dataTable = null;
  function cleanResultsTable() {
    if (dataTable) {
      dataTable.fnClearTable();
      dataTable.fnDestroy();
      viewModel.columns.valueHasMutated();
      viewModel.rows.valueHasMutated();
      dataTable = null;
    }
  }

  function waitingResultsTable() {
    $("#executeQuery").attr("data-loading-text", $("#executeQuery").text() + " ...");
    $("#executeQuery").button("loading");
  }

  function addResults(viewModel, dataTable, index, pageSize) {
    $.each(viewModel.rows.slice(index, index + pageSize), function (row_index, row) {
      var ordered_row = [];
      $.each(viewModel.columns(), function (col_index, col) {
        if (col_index == 0) {
          ordered_row.push(index + row_index + 1);
        }
        else {
          ordered_row.push(row[col]).toString().htmlEscape();
        }
      });
      dataTable.fnAddData(ordered_row);
    });
  }

  function resultsTable() {
    if (!dataTable) {
      dataTable = $(".resultTable").dataTable({
        "bPaginate": false,
        "bLengthChange": false,
        "bInfo": false,
        "oLanguage": {
          "sEmptyTable": "${_('No data available')}",
          "sZeroRecords": "${_('No matching records')}"
        },
        "fnDrawCallback": function( oSettings ) {
          $(".resultTable").jHueTableExtender({
            hintElement: "#jumpToColumnAlert",
            fixedHeader: true,
            firstColumnTooltip: true
          });
        }
      });
      $(".dataTables_filter").hide();
      $(".dataTables_wrapper").jHueTableScroller();

      // Automatic results grower
      var dataTableEl = $(".dataTables_wrapper");
      var index = 0;
      var pageSize = 100;
      dataTableEl.on("scroll", function (e) {
        if (dataTableEl.scrollTop() + dataTableEl.outerHeight() + 20 > dataTableEl[0].scrollHeight && dataTable) {
          addResults(viewModel, dataTable, index, pageSize);
          index += pageSize;
        }
      });
      addResults(viewModel, dataTable, index, pageSize);
      index += pageSize;

      $(".resultTable").width($(".resultTable").parent().width());
      $("#executeQuery").button("reset");
    }
  }
  $(document).on('start_execution.query', waitingResultsTable);
  $(document).on('execute.query', cleanResultsTable);
  $(document).on('explain.query', cleanResultsTable);
  $(document).on('executed.query', resultsTable);
  $(document).on('explained.query', resultsTable);

  // Server error handling.
  $(document).on('server.error', function(e, data) {
    $(document).trigger('error', "${_('Server error occurred: ')}" + data.error);
  });
  $(document).on('server.unmanageable_error', function(e, responseText) {
    $(document).trigger('error', "${_('Unmanageable server error occurred: ')}" + responseText);
  });

</script>

${ commonfooter(request, messages) | n,unicode }

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

<%namespace name="common" file="common.mako" />

${ commonheader(_('Query'), app_name, user) | n,unicode }

${ common.navbar('editor') }

<div class="container-fluid">
  <div class="row-fluid">
    <div class="card card-small">
      <ul class="nav nav-pills hueBreadcrumbBar" id="breadcrumbs">
        <li>
          <div style="display: inline" class="dropdown">
            ${_('App name')}&nbsp;
            <!-- ko if: $root.appNames().length == 0 -->
            <a class="uploadAppModalBtn" href="javascript:void(0);">
              ${ _("None, create one?") }
            </a>
            <!-- /ko -->​
            <a data-bind="if: $root.appName" data-toggle="dropdown" href="javascript:void(0);">
              <strong data-bind="text: $root.appName().nice_name"></strong>
              <i class="fa fa-caret-down"></i>
            </a>
            <ul data-bind="foreach: $root.appNames" class="dropdown-menu">
              <li data-bind="click: $root.chooseAppName, text: nice_name" class="selectable"></li>
            </ul>
          </div>
        </li>
        <li>&nbsp;&nbsp;&nbsp;&nbsp;</li>
        <li>
            ${_('Class path')}&nbsp;
            <input type="text" data-bind="value: $root.classPath" class="input-xlarge"></input>
        </li>
        <li>&nbsp;&nbsp;&nbsp;&nbsp;</li>
        <li>
          <div style="display: inline" class="dropdown">
            ${_('Context')}&nbsp;
            <input type="checkbox" data-bind="checked: $root.autoContext" />
            <span data-bind="visible: $root.autoContext()">
              ${ _('auto') }
            </span>

            <span data-bind="visible: ! $root.autoContext()">
              <!-- ko if: $root.contexts().length == 0 -->
              <a class="createContextModalBtn" href="javascript:void(0);">
                ${ _("None, create one?") }
              </a>
              <!-- /ko -->
              <a data-bind="if: $root.context" data-toggle="dropdown" href="javascript:void(0);">
                <strong data-bind="text: $root.context().nice_name"></strong>
                <i class="fa fa-caret-down"></i>
              </a>
              <ul data-bind="foreach: $root.contexts" class="dropdown-menu">
                <li data-bind="click: $root.chooseContext, text: nice_name" class="selectable"></li>
              </ul>
            </span>
          </div>
        </li>
        <span class="pull-right">
		  <button type="button" class="btn btn-primary uploadAppModalBtn">${ _('Upload app') }</button>
		  <button type="button" class="btn btn-primary createContextModalBtn">${ _('Create context') }</button>
        </span>
      </ul>
    </div>
  </div>
  <div class="row-fluid">
    <div class="span10">
    <div id="query">
      <div class="card card-small">
        <div style="margin-bottom: 30px">
          <h1 class="card-heading simple">
            ${ _('Script Editor') }
            % if can_edit_name:
              :
              <a href="javascript:void(0);"
                 id="query-name"
                 data-type="text"
                 data-name="name"
                 data-value="${design.name}"
                 data-original-title="${ _('Query name') }"
                 data-placement="right">
              </a>
            %endif
          </h1>
          % if can_edit_name:
            <p style="margin-left: 20px">
              <a href="javascript:void(0);"
                 id="query-description"
                 data-type="textarea"
                 data-name="description"
                 data-value="${design.desc}"
                 data-original-title="${ _('Query description') }"
                 data-placement="right">
              </a>
            </p>
          % endif
        </div>
        <div class="card-body">
          <div class="tab-content">
            <div id="queryPane">

              <div data-bind="css: {'hide': query.errors().length == 0}" class="hide alert alert-error">
                <p><strong>${_('Your query has the following error(s):')}</strong></p>
                <div data-bind="foreach: query.errors">
                  <p data-bind="text: $data" class="queryErrorMessage"></p>
                </div>
              </div>

              <textarea class="hide" tabindex="2" name="query" id="queryField"></textarea>

              <div class="actions">
                <button data-bind="click: tryExecuteQuery" type="button" id="executeQuery" class="btn btn-primary" tabindex="2">${_('Execute')}</button>
                <button data-bind="click: trySaveQuery, css: {'hide': !$root.query.id() || $root.query.id() == -1}" type="button" class="btn hide">${_('Save')}</button>
                <button data-bind="click: trySaveAsQuery" type="button" class="btn">${_('Save as...')}</button>
                <button data-bind="click: tryExplainQuery" type="button" id="explainQuery" class="btn">${_('Explain')}</button>
                &nbsp; ${_('or create a')} &nbsp;<a type="button" class="btn" href="${ url('spark:editor') }">${_('New query')}</a>
                <br /><br />
            </div>

            </div>
          </div>
        </div>
      </div>
    </div>
    <div data-bind="css: {'hide': rows().length == 0}" class="hide">
      <div class="card card-small scrollable">
        <table class="table table-striped table-condensed resultTable" cellpadding="0" cellspacing="0" data-tablescroller-min-height-disable="true" data-tablescroller-enforce-height="true">
          <thead>
            <tr>
              <th>${ _('Key') }</th>
              <th>${ _('Value') }</th>
            </tr>
          </thead>
        </table>
      </div>
    </div>

    <div data-bind="css: {'hide': !resultsEmpty()}" class="hide">
      <div class="card card-small scrollable">
        <div class="row-fluid">
          <div class="span10 offset1 center empty-wrapper">
            <i class="fa fa-frown-o"></i>
            <h1>${_('The server returned no results.')}</h1>
            <br />
          </div>
        </div>
      </div>
    </div>
  </div>
  <div class="span2" id="navigator">
      <div class="card card-small">
        <a href="#" title="${_('Double click on a table name or field to insert it in the editor')}" rel="tooltip" data-placement="left" class="pull-right" style="margin:10px;margin-left: 0"><i class="fa fa-question-circle"></i></a>
        <a id="refreshNavigator" href="#" title="${_('Manually refresh the table list')}" rel="tooltip" data-placement="left" class="pull-right" style="margin:10px"><i class="fa fa-refresh"></i></a>
        <h1 class="card-heading simple"><i class="fa fa-compass"></i> ${_('History')}</h1>
        <div class="card-body">
          <p>
            <input id="navigatorSearch" type="text" placeholder="${ _('Table name...') }" style="width:90%"/>
            <span id="navigatorNoTables">${_('The selected database has no tables.')}</span>
            <ul id="navigatorTables" class="unstyled"></ul>
          </p>
        </div>
      </div>
  </div>

  </div>
</div>


<div id="saveAsQueryModal" class="modal hide fade">
  <div class="modal-header">
    <a href="#" class="close" data-dismiss="modal">&times;</a>
    <h3>${_('Save your query')}</h3>
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

<div id="uploadAppModal" class="modal hide fade">
  <form class="form-horizontal" id="uploadAppForm" action="${ url('spark:upload_app') }" method="POST" enctype="multipart/form-data">
  <div class="modal-header">
    <a href="#" class="close" data-dismiss="modal">&times;</a>
    <h3>${_('Upload application')}</h3>
  </div>
  <div class="modal-body">
	    ${ _('One class of the jar should implement SparkJob.') }
	    <div class="control-group">
	      <label class="control-label">${ _("Local jar file") }</label>
	      <div class="controls">
	        <input type="file" name="jar_file" id="jar_file">
	      </div>
	    </div>
        <div class="control-group">
          <label class="control-label">${ _("App name") }</label>
          <div class="controls">
            <input type="text" name="app_name" id="app_name">
          </div>
        </div>
  </div>
  <div class="modal-footer">
    <button class="btn" data-dismiss="modal">${_('Cancel')}</button>
    <input type="submit" class="btn btn-primary" value="${_('Upload')}"/>
    ##<button data-bind="click: $('#uploadAppForm').submit()" class="btn btn-primary">${_('Upload')}</button>
  </div>
  </form>
</div>

<div id="createContextModal" class="modal hide fade">
  <div class="modal-header">
    <a href="#" class="close" data-dismiss="modal">&times;</a>
    <h3>${_('Create context')}</h3>
  </div>
  <div class="modal-body">
      <form class="form-horizontal" id="createContextForm">
        <div class="control-group">
          <label class="control-label">${ _("Name") }</label>
          <div class="controls">
            <input type="text" name="name">
          </div>
        </div>
        <div class="control-group">
          <label class="control-label">${ _("Num cpu cores") }</label>
          <div class="controls">
            <input type="text" name="numCores"value="1">
          </div>
        </div>
        <div class="control-group">
          <label class="control-label">${ _("Memory per node") }</label>
          <div class="controls">
            <input type="text" name="memPerNode" value="512m">
          </div>
        </div>
      </form>
  </div>
  <div class="modal-footer">
    <button class="btn" data-dismiss="modal">${_('Cancel')}</button>
    <button data-bind="click: createContext" class="btn btn-primary">${_('Create')}</button>
  </div>
</div>


<style type="text/css">
  h1 {
    margin-bottom: 5px;
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

  .hueBreadcrumb {
    padding: 12px 14px;
  }

  .hueBreadcrumbBar {
    padding: 0;
    margin: 12px;
  }

  .hueBreadcrumbBar a {
    color: #338BB8 !important;
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

.CodeMirror.cm-s-default {
   height:150px;
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

  .empty-wrapper {
    margin-top: 50px;
    color: #BBB;
    line-height: 60px;
  }

  .empty-wrapper i {
    font-size: 148px;
  }

  #navigatorTables li {
    width: 95%;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  #navigatorSearch, #navigatorNoTables {
    display: none;
  }

  #navigator .card {
    padding-bottom: 30px;
  }

</style>

<script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout.mapping-2.3.2.js" type="text/javascript" charset="utf-8"></script>
<script src="/spark/static/js/spark.vm.js"></script>
<script src="/static/ext/js/codemirror-3.11.js"></script>
<link rel="stylesheet" href="/static/ext/css/codemirror.css">
<script src="/static/ext/js/codemirror-sql.js"></script>
<script src="/static/js/codemirror-sql-hint.js"></script>
<script src="/static/js/codemirror-show-hint.js"></script>

<link href="/static/ext/css/bootstrap-editable.css" rel="stylesheet">
<script src="/static/ext/js/bootstrap-editable.min.js"></script>
<script src="/static/ext/js/bootstrap-editable.min.js"></script>

<script src="/static/ext/js/jquery/plugins/jquery-fieldselection.js" type="text/javascript"></script>
<script src="/spark/static/js/autocomplete.utils.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript" charset="utf-8">
  var codeMirror, viewModel;

  var spark_AUTOCOMPLETE_BASE_URL = '/spark/api';
  var spark_AUTOCOMPLETE_FAILS_SILENTLY_ON = [500, 404]; // error codes from spark/views.py - autocomplete
  var spark_AUTOCOMPLETE_GLOBAL_CALLBACK = $.noop;

  $(document).ready(function(){

    var queryPlaceholder = "${_('Example: SELECT * FROM tablename, or press CTRL + space')}";

    $("*[rel=tooltip]").tooltip({
      placement: 'bottom'
    });

    var queryEditor = $("#queryField")[0];

    var selectedLine = -1;
    var errorWidget = null;

    $("#help").popover({
      'title': "${_('Did you know?')}",
      'content': $("#help-content").html(),
      'trigger': 'hover',
      'html': true
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
    var query = getHighlightedQuery() || codeMirror.getValue();
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

  $('.uploadAppModalBtn').click(function(){
    $('#uploadAppModal').modal('show');
  });
  $('.createContextModalBtn').click(function(){
    $('#createContextModal').modal('show');
  });

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
    var key = "huesparkLastDatabase-" + server;
    if (database != $.totalStorage(key)) {
      $.totalStorage(key, database);
    }
  }

  function getLastDatabase(server) {
    var key = "huesparkLastDatabase-" + server;
    return $.totalStorage(key);
  }

    var queryEditor = $("#queryField")[0];

    var AUTOCOMPLETE_SET = CodeMirror.sqlHint;

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


  // Knockout
  viewModel = new sparkViewModel();
  viewModel.fetchAppNames();
  viewModel.fetchContexts();
  ko.applyBindings(viewModel);


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

  // Events and datatables
  $(document).on('saved.query', function() {
    $.jHueNotify.info("${_('Query saved successfully!')}")
  });

  var dataTable = null;
  function cleanResultsTable() {
    if (dataTable) {
      dataTable.fnClearTable();
      dataTable.fnDestroy();
      viewModel.rows.valueHasMutated();
      dataTable = null;
    }
  }

  function addResults(viewModel, dataTable, index, pageSize) {
    $.each(viewModel.rows.slice(index, index + pageSize), function(row_index, row) {
      dataTable.fnAddData(row);
    });
  }

  function resultsTable() {
    if (! dataTable) {
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
    }
  }
  $(document).on('execute.query', cleanResultsTable);
  $(document).on('executed.query', resultsTable);

  $(document).on('created.context', function() {
    $('#createContextModal').modal('hide');
  });

  // Server error handling.
  $(document).on('server.error', function(e, data) {
    $(document).trigger('error', "${_('Server error occured: ')}" + data.error);
  });
  $(document).on('server.unmanageable_error', function(e, responseText) {
    $(document).trigger('error', "${_('Unmanageable server error occured: ')}" + responseText);
  });

</script>

${ commonfooter(messages) | n,unicode }

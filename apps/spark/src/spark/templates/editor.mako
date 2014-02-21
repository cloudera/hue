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
      <div style="margin-bottom: 10px">
        % if can_edit_name:
        <h1 class="card-heading simple">
          <a href="javascript:void(0);"
             id="query-name"
             data-type="text"
             data-name="name"
             data-value="${design.name}"
             data-original-title="${ _('Application name') }"
             data-placement="right">
          </a>

          <a href="javascript:void(0);"
             id="query-description"
             data-type="textarea"
             data-name="description"
             data-value="${design.desc}"
             data-original-title="${ _('Application description') }"
             data-placement="right" style="font-size: 14px; margin-left: 10px">
          </a>

        </h1>
        % endif
      </div>
      <div class="card-body">
        <p>
          <span class="pull-right">
            <button type="button" class="btn btn-primary uploadAppModalBtn">${ _('Upload app') }</button>
            <button type="button" class="btn btn-primary createContextModalBtn">${ _('Create context') }</button>
          </span>
          <div></div><!-- this is to fix IE's quirkiness /-->
          <form class="form-inline">
            <span class="dropdown">
              ${_('App name')}&nbsp;
              <!-- ko if: $root.appNames().length == 0 -->
              <a class="uploadAppModalBtn" href="javascript:void(0);">
                ${ _("Missing, add one?") }
              </a>
              <!-- /ko -->
              <a data-bind="if: $root.appName" data-toggle="dropdown" href="javascript:void(0);">
                <strong data-bind="text: $root.appName().nice_name"></strong>
                <i class="fa fa-caret-down"></i>
              </a>
              <ul data-bind="foreach: $root.appNames" class="dropdown-menu">
                <li data-bind="click: $root.chooseAppName, text: nice_name" class="selectable"></li>
              </ul>
            </span>

            <label style="margin-left: 20px; margin-right: 20px">
              ${_('Class path')}
              <input type="text" data-bind="value: $root.classPath" class="input-xlarge" placeholder="spark.jobserver.WordCountExample" />
            </label>

            ${_('Context')}&nbsp;
            <label class="radio" style="margin-top:-2px">
              <input type="radio" name="autoContext" value="true" data-bind="checked:$root.autoContext.forEditing" style="margin-right: 5px" />
              ${ _('Automatic') }
            </label>
            <label class="radio" style="margin-left: 5px;margin-top:-2px">
              <span class="dropdown" style="padding-left: 5px">
                <!-- ko if: $root.contexts().length == 0 -->
                <a class="createContextModalBtn" href="javascript:void(0);">
                  ${ _("Create one?") }
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
              <input type="radio" name="autoContext" value="false" data-bind="checked:$root.autoContext.forEditing"/>
            </label>
          </form>
        </p>
      </div>
    </div>
  </div>

  <div class="row-fluid">
    <div class="card card-small">
      <h1 class="card-heading simple">
        <a id="collapse-editor" href="javascript:void(0)" class="pull-right"><i class="fa fa-caret-up"></i></a>
        ${_('Parameters')}
      </h1>
      <div class="card-body">
        <p>
          <div id="param-pane">
          <div data-bind="css: {'hide': query.errors().length == 0}" class="hide alert alert-error">
            <p><strong>${_('Your application has the following error(s):')}</strong></p>
            <div data-bind="foreach: query.errors">
              <p data-bind="text: $data" class="queryErrorMessage"></p>
            </div>
          </div>

          <div data-bind="visible: query.params().length == 0">${_('No parameters defined yet.')}</div>

          <table class="table-condensed">
            <thead data-bind="visible: query.params().length > 0">
              <tr>
                <th>${ _('Name') }</th>
                <th>${ _('Value') }</th>
                <th/>
              </tr>
            </thead>
            <tbody data-bind="foreach: query.params">
              <tr>
                <td><input type="text" class="input-large required propKey" data-bind="value: name" /></td>
                <td>
                <div class="input-append">
                  <input type="text" data-bind="value: value" class="input-xxlarge" />
                  <button class="btn fileChooserBtn" data-bind="click: $root.showFileChooser">..</button>
                </div>
                </td>
                <td style="vertical-align: top">
                  <a class="btn" href="#" data-bind="click: $root.removeParam">${ _('Delete') }</a>
                </td>
              </tr>
            </tbody>
          </table>
          <div style="margin-top: 10px">
            <a class="btn" href="#" data-bind="click: $root.addParam">${ _('Add') }</a>
          </div>

          <div class="actions" style="margin-top: 50px; margin-bottom: 20px">
            <button data-bind="click: tryExecuteQuery, enable: $root.appNames().length > 0 && $root.classPath()"
              type="button" id="executeQuery" class="btn btn-primary disable-feedback"
              tabindex="2" data-loading-text="${ _("Executing...") }">
              ${_('Execute')}
            </button>
            <button data-bind="click: trySaveQuery, visible: ($root.query.id() && $root.query.id() != -1)" type="button" class="btn">${_('Save')}</button>
            <button data-bind="click: trySaveAsQuery, visible: $root.appNames().length > 0" type="button" class="btn">${_('Save as...')}</button>
            &nbsp; ${_('or create a')} &nbsp;<a type="button" class="btn" href="${ url('spark:editor') }">${_('New application')}</a>
            <span class="pull-right">
              <a type="button" class="btn" data-bind="visible: rows().length != 0, attr: {'href': '${ url('spark:download_result') }' + $root.query.jobId()}">${_('Download')}</a>
            </span>
          </div>
        </div>
          <div data-bind="css: {'hide': rows().length == 0}" class="hide">
            <div class="scrollable">
              <table id="resultTable" class="table table-striped table-condensed resultTable" cellpadding="0" cellspacing="0" data-tablescroller-min-height-disable="true" data-tablescroller-enforce-height="true">
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
            <div class="scrollable">
              <div class="row-fluid">
                <div class="span10 offset1 center empty-wrapper">
                  <i class="fa fa-frown-o"></i>
                  <h1>${_('The server returned no results.')}</h1>
                  <br/>
                </div>
              </div>
            </div>
          </div>

          <div id="wait-info" class="hide">
            <div class="scrollable">
              <div class="row-fluid">
                <div class="span10 offset1 center" style="padding: 30px">
                  <!--[if !IE]><!--><i class="fa fa-spinner fa-spin" style="font-size: 60px; color: #DDD"></i><!--<![endif]-->
                  <!--[if IE]><img src="/static/art/spinner.gif" /><![endif]-->
                </div>
              </div>
            </div>
          </div>
        </p>
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

<div id="chooseFile" class="modal hide fade">
  <div class="modal-header">
      <a href="#" class="close" data-dismiss="modal">&times;</a>
      <h3>${_('Choose a file')}</h3>
  </div>
  <div class="modal-body">
      <div id="filechooser">
      </div>
  </div>
  <div class="modal-footer">
  </div>
</div>


${ common.uploadAppModal() }
${ common.createContextModal() }


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

<link href="/static/ext/css/bootstrap-editable.css" rel="stylesheet">
<script src="/static/ext/js/bootstrap-editable.min.js"></script>
<script src="/static/ext/js/bootstrap-editable.min.js"></script>

<script src="/static/ext/js/jquery/plugins/jquery-fieldselection.js" type="text/javascript"></script>

<script type="text/javascript" charset="utf-8">
  var viewModel;

  $(document).ready(function(){
    $("*[rel=tooltip]").tooltip({
      placement: 'bottom'
    });

    $("#help").popover({
      'title': "${_('Did you know?')}",
      'content': $("#help-content").html(),
      'trigger': 'hover',
      'html': true
    });

    // Knockout
    viewModel = new sparkViewModel();
    viewModel.fetchAppNames();
    viewModel.fetchContexts();
    % if design_json:
      viewModel.loadDesign(${ design_json | n,unicode });
    % endif
    % if job_id:
      viewModel.openQuery("${ job_id }");
    % endif
    var hash = window.location.hash;
    if (hash != "" && hash.indexOf("=") > -1) {
      var hashKey = hash.split("=")[0].substr(1);
      var hashValue = hash.split("=")[1];
      if (hashKey == 'jobId') {
        viewModel.openQuery(hashValue);
      } else if (hashKey == 'applicationId') {
        viewModel.query.appName(hashValue);
      }

    }
    ko.applyBindings(viewModel);

    $("#collapse-editor").on("click", function () {
      if ($("#param-pane").is(":visible")) {
        $("#param-pane").slideUp(100, function () {
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
        $("#param-pane").slideDown(100, function () {
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
  });


  function modal(el) {
    var el = $(el);
    return function() {
      el.modal('show');
    };
  }

  function tryExecuteQuery() {
    viewModel.executeQuery();
  }

  function trySaveQuery() {
    if (viewModel.query.id() && viewModel.query.id() != -1) {
      viewModel.saveQuery();
    }
  }

  function trySaveAsQuery() {
    if (viewModel.appName() != null && viewModel.appName() != ""){
      $('#saveAsQueryModal').modal('show');
    }
  }

  $('.uploadAppModalBtn').click(function(){
    $('#uploadAppModal').modal('show');
  });

  $('.createContextModalBtn').click(function(){
    $('#createContextModal').modal('show');
  });

  function modalSaveAsQuery() {
    if (viewModel.query.name()) {
      viewModel.query.id(-1);
      viewModel.saveQuery();
      $('#saveas-query-name').removeClass('error');
      $('#saveAsQueryModal').modal('hide');
    } else {
      $('#saveas-query-name').addClass('error');
    }
  }

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
    emptytext: "${ _('Application name') }"
  });

  $("#query-description").editable({
    success: function(response, newValue) {
      viewModel.query.description(newValue);
    },
    emptytext: "${ _('Empty description') }"
  });


  // Events and datatables
  $(document).on('saved.query', function() {
    $.jHueNotify.info("${_('Application saved successfully!')}")
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
        "aaSorting": [],
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

  $(document).on('execute.query', function() {
    $('#wait-info').show();
    $("#executeQuery").button("loading");
    cleanResultsTable();
  });
  $(document).on('executed.query', function() {
    $('#wait-info').hide();
    $("#executeQuery").button("reset");
    resultsTable();
  });

  $(document).on("created.context", function() {
      $("#createContextModal").modal("hide");
      $("#createContextBtn").button("reset");
      $("input[data-default]").each(function(){
        $(this).val($(this).data("default"));
      });
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

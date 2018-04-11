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
  from oozie.conf import ENABLE_OOZIE_BACKEND_FILTERING
%>

<%namespace name="layout" file="../navigation-bar.mako" />
<%namespace name="utils" file="../utils.inc.mako" />

${ commonheader(_("Bundles Dashboard"), "oozie", user, request) | n,unicode }
${layout.menubar(section='bundles', dashboard=True)}


<div class="container-fluid">
  <div class="card card-small">
  <div class="card-body" style="padding-bottom: 20px">
  <p>
  <form>
    <input type="text" id="filterInput" class="input-xlarge search-query" placeholder="${ _('Search partial name, submitter or complete Id') }">

    <div class="btn-toolbar" style="display: inline; vertical-align: middle; margin-left: 10px; font-size: 12px">
      <span class="loader hide"><i class="fa fa-2x fa-spinner fa-spin muted"></i></span>
      <button class="btn bulkToolbarBtn bulk-resume" data-operation="resume" title="${ _('Resume selected') }" disabled="disabled" type="button"><i class="fa fa-play"></i> ${ _('Resume') }</button>
      <button class="btn bulkToolbarBtn bulk-suspend" data-operation="suspend" title="${ _('Suspend selected') }" disabled="disabled" type="button"><i class="fa fa-pause"></i> ${ _('Suspend') }</button>
      <button class="btn bulkToolbarBtn btn-danger bulk-kill disable-feedback" data-operation="kill" title="${ _('Kill selected') }" disabled="disabled" type="button"><i class="fa fa-times"></i> ${ _('Kill') }</button>
    </div>

    <span class="pull-right">
      <span style="padding-right:10px;float:left;margin-top:3px">
      ${ _('Show only') }
      </span>
      <span class="btn-group" style="float:left">
        <a class="btn btn-date btn-info" data-value="1">${ _('1') }</a>
        <a class="btn btn-date btn-info" data-value="7">${ _('7') }</a>
        <a class="btn btn-date btn-info" data-value="15">${ _('15') }</a>
        <a class="btn btn-date btn-info" data-value="30">${ _('30') }</a>
      </span>
      <span style="float:left;padding-left:10px;padding-right:10px;margin-top:3px">${ _('days with status') }</span>
      <span class="btn-group" style="float:left;">
        <a class="btn btn-status btn-success" data-value='SUCCEEDED'>${ _('Succeeded') }</a>
        <a class="btn btn-status btn-warning" data-value='RUNNING'>${ _('Running') }</a>
        <a class="btn btn-status btn-danger disable-feedback" data-value='ERROR'>${ _('Error') }</a>
      </span>
    </span>
  </form>

  <div style="min-height:200px">
    <h1 class="card-heading simple">${ _('Running') }</h1>
    <table class="table table-condensed" id="running-table">
      <thead>
        <tr>
          <th width="1%"><div class="select-all hue-checkbox fa"></div></th>
          <th width="14%">${ _('Kickoff Time') }</th>
          <th width="10%">${ _('Status') }</th>
          <th width="20%">${ _('Name') }</th>
          <th width="10%">${ _('Progress') }</th>
          <th width="10%">${ _('Submitter') }</th>
          <th width="10%">${ _('Created Time') }</th>
          <th width="15%">${ _('Id') }</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><i class="fa fa-2x fa-spinner fa-spin muted"></i></td>
          <td></td>
          <td></td>
          <td></td>
          <td></td>
          <td></td>
          <td></td>
          <td></td>
        </tr>
      </tbody>
    </table>

    <span class="running-info" style="padding-left: 4px"></span>

    <div class="pagination dataTables_paginate">
      <ul>
        <li class="prev"><a href="javascript:void(0)" class="btn-pagination" data-value="prev" data-table="running"><i class="fa fa-long-arrow-left"></i> ${ _('Previous') }</a></li>
        <li class="next"><a href="javascript:void(0)" class="btn-pagination" data-value="next" data-table="running">${ _('Next') } <i class="fa fa-long-arrow-right"></i></a></li>
      </ul>
    </div>

  </div>

  <div>
    <h1 class="card-heading simple">${ _('Completed') }</h1>
    <table class="table table-condensed" id="completed-table" data-tablescroller-disable="true">
      <thead>
        <tr>
          <th width="15%">${ _('Kickoff Time') }</th>
          <th width="10%">${ _('Status') }</th>
          <th width="25%">${ _('Name') }</th>
          <th width="15%">${ _('Submitter') }</th>
          <th width="15%">${ _('Created Time') }</th>
          <th width="25%">${ _('Id') }</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><i class="fa fa-2x fa-spinner fa-spin muted"></i></td>
          <td></td>
          <td></td>
          <td></td>
          <td></td>
          <td></td>
        </tr>
      </tbody>
     </table>

     <span class="completed-info" style="padding-left: 4px"></span>

     <div class="pagination dataTables_paginate">
      <ul>
        <li class="prev"><a href="javascript:void(0)" class="btn-pagination" data-value="prev" data-table="completed"><i class="fa fa-long-arrow-left"></i> ${ _('Previous') }</a></li>
        <li class="next"><a href="javascript:void(0)" class="btn-pagination" data-value="next" data-table="completed">${ _('Next') } <i class="fa fa-long-arrow-right"></i></a></li>
      </ul>
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
<script src="${ static('desktop/ext/js/datatables-paging-0.1.js') }" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript">
  var Bundle = function (bundle) {
    return {
      id: bundle.id,
      endTime: bundle.endTime,
      endTimeInMillis: bundle.endTimeInMillis,
      status: bundle.status,
      statusClass: "label " + getStatusClass(bundle.status),
      isRunning: bundle.isRunning,
      kickoffTime: bundle.kickoffTime,
      kickoffTimeInMillis: bundle.kickoffTimeInMillis,
      timeOut: bundle.timeOut,
      appName: decodeURIComponent(bundle.appName),
      progress: bundle.progress,
      progressClass: "bar " + getStatusClass(bundle.status, "bar-"),
      user: bundle.user,
      absoluteUrl: bundle.absoluteUrl,
      canEdit: bundle.canEdit,
      killUrl: bundle.killUrl,
      suspendUrl: bundle.suspendUrl,
      resumeUrl: bundle.resumeUrl,
      created: bundle.created,
      createdInMillis: bundle.createdInMillis
    }
  }

  var refreshRunning;
  var runningTableOffset = 1, completedTableOffset = 1;
  var totalRunningJobs = 0, totalCompletedJobs = 0;
  var PAGE_SIZE = 50;
  var filterTimeout = null;

  $(document).ready(function () {

    function showTableInfo(oSettings, table, tableOffset, totalJobs) {
      var _disp = oSettings.fnRecordsDisplay();
      var _tot = oSettings.fnRecordsTotal();
      var _text = "";
      if (_disp == 0) {
        _text = '${_("Showing 0 to 0 of ")}' + totalJobs + '${_(" entries")}';
      }
      else {
        _text = ' ${_("Showing ")}' + tableOffset + '${_(" to ")}' + (tableOffset + oSettings.fnDisplayEnd() - 1) + '${_(" of ")}' + totalJobs;
      }
      if (_disp != _tot) { // when filter button is selected
          _text += '${_(" (filtered from ")}' + _tot + '${_(" entries)")}';
      }
      $(table).text(_text);
    }

    var runningTable = $("#running-table").dataTable({
      "bPaginate": false,
      "iDisplayLength":PAGE_SIZE,
      "bLengthChange":false,
      "sDom":"<'row'r>t<'row'<'span6'><''p>>",
      "bAutoWidth": false,
      "aoColumns":[
        { "bSortable":false },
        { "sSortDataType":"dom-sort-value", "sType":"numeric" },
        null,
        null,
        { "sSortDataType":"dom-sort-value", "sType":"numeric" },
        null,
        { "sSortDataType":"dom-sort-value", "sType":"numeric" },
        null
      ],
      "aaSorting":[
        [ 5, "desc" ]
      ],
      "oLanguage":{
        "sZeroRecords":"${_('No matching records')}"
      },
      "fnDrawCallback":function (oSettings) {
        showTableInfo(oSettings, ".running-info", runningTableOffset, totalRunningJobs);
        $("a[data-row-selector='true']").jHueRowSelector();
      }
    });

    var completedTable = $("#completed-table").dataTable({
      "bPaginate": false,
      "iDisplayLength":PAGE_SIZE,
      "bLengthChange":false,
      "sDom":"<'row'r>t<'row'<'span6'><''p>>",
      "bAutoWidth": false,
      "aoColumns":[
        { "sSortDataType":"dom-sort-value", "sType":"numeric" },
        null,
        null,
        null,
        { "sSortDataType":"dom-sort-value", "sType":"numeric" },
        null
      ],
      "aaSorting":[
        [ 4, "desc" ]
      ],
      "oLanguage":{
        "sZeroRecords":"${_('No matching records')}"
      },
      "fnDrawCallback":function (oSettings) {
        showTableInfo(oSettings, ".completed-info", completedTableOffset, totalCompletedJobs);
        $("a[data-row-selector='true']").jHueRowSelector();
      }
    });

    $("#filterInput").keydown(function (e) {
      if (e.which == 13) {
        e.preventDefault();
        return false;
      }
    });

    $("#filterInput").keyup(function () {
      % if ENABLE_OOZIE_BACKEND_FILTERING.get():
        if (filterTimeout != null) {
          clearTimeout(filterTimeout);
        }
        filterTimeout = setTimeout(refreshTables, 500);
        refreshPagination();
      % else:
        runningTable.fnFilter($(this).val());
        completedTable.fnFilter($(this).val());
      % endif

      var hash = "#";
      if ($("a.btn-date.active").length > 0) {
        hash += "date=" + $("a.btn-date.active").text();
      }
      window.location.hash = hash;
    });

    $("a.btn-pagination").on("click", function () {
      if (!$(this).parent().hasClass("disabled")) {
        var _additionalOffset = 0;
        if ($(this).data("value") == "prev") {
          _additionalOffset = -PAGE_SIZE;
        }
        else {
          _additionalOffset = PAGE_SIZE;
        }
        if ($(this).data("table") == "running") {
          runningTableOffset += _additionalOffset;
          refreshRunning();
        }
        else {
          completedTableOffset += _additionalOffset;
          refreshCompleted();
        }
      }
    });

    $("a.btn-status").click(function () {
      refreshPagination();
      $(this).toggleClass("active");
      refreshRunning();
      refreshCompleted();
    });

    $("a.btn-date").click(function () {
      refreshPagination();
      $("a.btn-date").not(this).removeClass("active");
      $(this).toggleClass("active");
      drawTable();
    });

    var hash = window.location.hash.replace(/(<([^>]+)>)/ig, "");
    if (hash != "" && hash.indexOf("=") > -1) {
      $("a.btn-date[data-value='" + hash.split("=")[1] + "']").click();
    }

    function refreshTables() {
      refreshRunning();
      refreshCompleted();
      refreshProgress();
    }


    function getTextFilter() {
      % if not ENABLE_OOZIE_BACKEND_FILTERING.get():
        return '';
      % endif
      var filterBtn = $("#filterInput");
      var textFilter = '';
      if (filterBtn.val()) {
        textFilter = '&text=' + filterBtn.val();
      }
      return textFilter;
    }

    function refreshPagination() {
      runningTableOffset = 1;
      completedTableOffset = 1;
    }

    function drawTable() {
      runningTable.fnDraw();
      completedTable.fnDraw();

      var hash = "#";
      if ($("a.btn-date.active").length > 0) {
        hash += "date=" + $("a.btn-date.active").text();
      }
      window.location.hash = hash;
    }

    function getStatuses(type) {
      var selectedStatuses = (type == 'running') ? ['RUNNING', 'PREP', 'SUSPENDED', 'RUNNINGWITHERROR', 'PREPSUSPENDED', 'SUSPENDEDWITHERROR', 'PREPPAUSED', 'PAUSED', 'PAUSEDWITHERROR'] : ['SUCCEEDED', 'KILLED', 'FAILED', 'DONEWITHERROR'];
      var btnStatuses = [];
      var statusBtns = $("a.btn-status.active");
      $.each(statusBtns, function () {
        val = $(this).data('value');
        if (val == 'SUCCEEDED') {
          btnStatuses = btnStatuses.concat(['SUCCEEDED']);
        } else if (val == 'RUNNING') {
          btnStatuses = btnStatuses.concat(['RUNNING', 'PREP', 'SUSPENDED', 'RUNNINGWITHERROR', 'PREPSUSPENDED', 'SUSPENDEDWITHERROR', 'PREPPAUSED', 'PAUSED', 'PAUSEDWITHERROR']);
        } else if (val == 'ERROR') {
          btnStatuses = btnStatuses.concat(['KILLED', 'FAILED', 'DONEWITHERROR']);
        }
      });
      if (btnStatuses.length > 0) {
        selectedStatuses = $.makeArray($(selectedStatuses).filter(btnStatuses));
      }
      return selectedStatuses.length > 0 ? ('&status=' + selectedStatuses.join('&status=')) : '';
    }

    $.fn.dataTableExt.sErrMode = "throw";

    $.fn.dataTableExt.afnFiltering.push(DateButtonsFilters); // from dashboard-utils.js

    $(document).on("click", ".confirmationModal", function () {
      var _this = $(this);
      _this.bind("confirmation", function () {
        var _this = this;
        $.post($(this).attr("data-url"),
          { "notification":$(this).attr("data-message") },
          function (response) {
            if (response["status"] != 0) {
              $(document).trigger("error", "${ _('Problem: ') }" + response["data"]);
              $("#confirmation a.btn-danger").button("reset");
            } else {
              window.location.reload();
            }
          }
        );
        return false;
      });
      $("#confirmation .message").text(_this.attr("data-confirmation-message"));
      $("#confirmation").modal("show");
      $("#confirmation a.btn-danger").click(function () {
        _this.trigger("confirmation");
        $(this).attr("data-loading-text", $(this).text() + " ...");
        $(this).button("loading");
      });
    });


    var numRunning = 0;

    refreshRunning = function () {
      $.getJSON(window.location.pathname + "?format=json&offset=" + runningTableOffset + getStatuses('running') + getTextFilter(), function (data) {
        // Refresh pagination buttons
        totalRunningJobs = data.total_jobs;
        refreshPaginationButtons("running", totalRunningJobs);

        if (data.jobs.length > 0) {
          var nNodes = runningTable.fnGetNodes();

          // check for zombie nodes
          $(nNodes).each(function (iNode, node) {
            var nodeFound = false;
            $(data.jobs).each(function (iBundle, currentItem) {
              if ($(node).children("td").eq(7).text() == currentItem.id) {
                nodeFound = true;
              }
            });
            if (!nodeFound) {
              runningTable.fnDeleteRow(node);
              runningTable.fnDraw();
            }
          });

          $(data.jobs).each(function (iBundle, item) {
            var bundle = new Bundle(item);
            var foundRow = null;
            $(nNodes).each(function (iNode, node) {
              if ($(node).children("td").eq(7).text() == bundle.id) {
                foundRow = node;
              }
            });

            if (foundRow == null) {
              if (['RUNNING', 'PREP', 'WAITING', 'SUSPENDED', 'PREPSUSPENDED', 'PREPPAUSED', 'PAUSED', 'STARTED', 'FINISHING'].indexOf(bundle.status) > -1) {
                try {
                  runningTable.fnAddData([
                    bundle.canEdit ? '<div class="hue-checkbox fa" data-row-selector-exclude="true"></div>' : '',
                    '<span data-sort-value="'+ bundle.kickoffTimeInMillis +'" data-type="date">' + emptyStringIfNull(bundle.kickoffTime) + '</span>',
                    '<span class="' + bundle.statusClass + '" data-type="status">' + bundle.status + '</span>',
                    bundle.appName,
                    '<div class="progress"><div class="bar bar-warning" style="width:1%"></div></div>',
                    bundle.user,
                    '<span data-sort-value="'+ bundle.createdInMillis +'">' + emptyStringIfNull(bundle.created) + '</span>',
                    '<a href="' + bundle.absoluteUrl + '" data-row-selector="true">' + bundle.id + '</a>'
                  ]);
                }
                catch (error) {
                  $(document).trigger("error", error);
                }
              }

            }
            else {
              runningTable.fnUpdate('<span class="' + bundle.statusClass + '" data-type="status">' + bundle.status + '</span>', foundRow, 2, false);
            }
          });
        }
        if (data.jobs.length == 0) {
          runningTable.fnClearTable();
        }

        if (data.jobs.length != numRunning) {
          refreshCompleted();
        }
        numRunning = data.jobs.length;

        ko.bindingHandlers.multiCheck.init(runningTable[0], function() { return '#' + runningTable[0].id})
        window.setTimeout(refreshRunning, 20000);
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseJSON['detail']);
      });
    }

    function refreshPaginationButtons(tableName, totalJobs) {
      var prevBtn = $("a.btn-pagination[data-table='"+ tableName + "'][data-value='prev']");
      var nextBtn = $("a.btn-pagination[data-table='"+ tableName + "'][data-value='next']");
      var offset = runningTableOffset;
      if (tableName == 'completed') {
        offset = completedTableOffset;
      }
      if (offset == 1 || !totalJobs) {
        prevBtn.parent().addClass("disabled");
      }
      else {
        prevBtn.parent().removeClass("disabled");
      }
      if (totalJobs < (offset + PAGE_SIZE) || !totalJobs) {
        nextBtn.parent().addClass("disabled");
      }
      else if (totalJobs >= offset + PAGE_SIZE) {
        nextBtn.parent().removeClass("disabled");
      }
    }

    function refreshCompleted() {
      $.getJSON(window.location.pathname + "?format=json&offset=" + completedTableOffset + getStatuses('completed') + getTextFilter(), function (data) {
        // Refresh pagination buttons
        totalCompletedJobs = data.total_jobs;
        refreshPaginationButtons("completed", totalCompletedJobs);

        completedTable.fnClearTable();
        $(data.jobs).each(function (iWf, item) {
          var bundle = new Bundle(item);
          try {
            completedTable.fnAddData([
              '<span data-sort-value="'+ bundle.kickoffTimeInMillis +'" data-type="date">' + emptyStringIfNull(bundle.kickoffTime) + '</span>',
              '<span class="' + bundle.statusClass + '" data-type="status">' + bundle.status + '</span>',
              bundle.appName,
              bundle.user,
              '<span data-sort-value="'+ bundle.createdInMillis +'">' + emptyStringIfNull(bundle.created) + '</span>',
              '<a href="' + bundle.absoluteUrl + '" data-row-selector="true">' + bundle.id + '</a>'
            ], false);
          }
          catch (error) {
            $(document).trigger("error", error);
          }
        });
        completedTable.fnDraw();
      });
    }

    function refreshProgress() {
      $.getJSON(window.location.pathname + "?format=json&type=progress" + getStatuses('running') + getTextFilter(), function (data) {
        var nNodes = runningTable.fnGetNodes();
        $(data.jobs).each(function (iWf, item) {
            var bundle = new Bundle(item);
            var foundRow = null;
            $(nNodes).each(function (iNode, node) {
              if ($(node).children("td").eq(7).text() == bundle.id) {
                foundRow = node;
              }
            });
            if (foundRow != null) {
              runningTable.fnUpdate('<span class="' + bundle.statusClass + '" data-type="status">' + bundle.status + '</span>', foundRow, 2, false);
              if (bundle.progress == 0){
                runningTable.fnUpdate('<div class="progress"><div class="bar bar-warning" style="width: 1%"></div></div>', foundRow, 4, false);
              }
              else {
                runningTable.fnUpdate('<div class="progress"><div class="' + bundle.progressClass + '" style="width:' + bundle.progress + '%">' + bundle.progress + '%</div></div>', foundRow, 4, false);
              }
            }
          });
        window.setTimeout(refreshProgress, 20000);
      });
    }

    refreshTables();

  });
</script>

${ utils.bulk_dashboard_functions() }

${ commonfooter(request, messages) | n,unicode }

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


${ commonheader(_("Workflows Dashboard"), "oozie", user, request) | n,unicode }
${ layout.menubar(section='workflows', dashboard=True) }


<div class="container-fluid">
  <div class="card card-small">
  <div class="card-body" style="padding-bottom: 20px">
  <p>
  <form>
    <input type="text" id="filterInput" class="input-xlarge search-query" placeholder="${ _('Search partial name, submitter or complete Id') }">

    <div class="btn-toolbar" style="display: inline; vertical-align: middle; margin-left: 10px; font-size: 12px">
      <span class="loader hide"><i class="fa fa-2x fa-spinner fa-spin muted"></i></span>
      <button class="btn bulkToolbarBtn bulk-resume" data-operation="resume" title="${ _('Resume selected') }" disabled="disabled" type="button"><i class="fa fa-play"></i><span class="hide-small"> ${ _('Resume') }</span></button>
      <button class="btn bulkToolbarBtn bulk-suspend" data-operation="suspend" title="${ _('Suspend selected') }" disabled="disabled" type="button"><i class="fa fa-pause"></i><span class="hide-small"> ${ _('Suspend') }</span></button>
      <button class="btn bulkToolbarBtn btn-danger bulk-kill disable-feedback" data-operation="kill" title="${ _('Kill selected') }" disabled="disabled" type="button"><i class="fa fa-times"></i><span class="hide-small"> ${ _('Kill') }</span></button>
    </div>

    <span class="pull-right">
      <span style="padding-right:10px;float:left;margin-top:3px" class="hide-smaller">
      ${ _('Show only') }
      </span>
      <span class="btn-group" style="float:left">
        <a class="btn btn-date btn-info" data-value="1">${ _('1') }</a>
        <a class="btn btn-date btn-info" data-value="7">${ _('7') }</a>
        <a class="btn btn-date btn-info" data-value="15">${ _('15') }</a>
        <a class="btn btn-date btn-info" data-value="30">${ _('30') }</a>
      </span>
      <span style="float:left;padding-left:10px;padding-right:10px;margin-top:3px" class="hide-smaller">${ _('days with status') }</span>
      <span class="btn-group" style="float:left;">
        <a class="btn btn-status btn-success" data-value='SUCCEEDED'>${ _('Succeeded') }</a>
        <a class="btn btn-status btn-warning" data-value='RUNNING'>${ _('Running') }</a>
        <a class="btn btn-status btn-danger disable-feedback" data-value='ERROR'>${ _('Error') }</a>
      </span>
      <span style="float:left;padding-left:10px;padding-right:10px;margin-top:3px" class="hide-smaller">${ _('submitted') }</span>
      <span class="btn-group" style="float:left;">
        <a class="btn btn-submitted btn-info" data-value='MANUALLY'>${ _('Manually') }</a>
        <a class="btn btn-submitted btn-info" data-value='COORDINATOR'>${ _('Coordinator') }</a>
      </span>
    </span>
 </form>

  <div style="min-height:200px">
    <h1 class="card-heading simple">${ _('Running') }</h1>
    <table class="table table-condensed" id="running-table">
      <thead>
        <tr>
          <th width="1%"><div class="select-all hue-checkbox fa"></div></th>
          <th width="14%">${ _('Submission') }</th>
          <th width="5%">${ _('Status') }</th>
          <th width="31%">${ _('Name') }</th>
          <th width="7%">${ _('Progress') }</th>
          <th width="7%">${ _('Submitter') }</th>
          <th width="7%">${ _('Last Modified') }</th>
          <th width="23%">${ _('Id') }</th>
          <th width="5%">${ _('Parent') }</th>
          <th width="0%">${ _('Submitted Manually') }</th>
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
          <th width="15%">${ _('Completion') }</th>
          <th width="7%">${ _('Status') }</th>
          <th width="31%">${ _('Name') }</th>
          <th width="7%">${ _('Duration') }</th>
          <th width="10%">${ _('Submitter') }</th>
          <th width="25%">${ _('Id') }</th>
          <th width="5%">${ _('Parent') }</th>
          <th width="0%">${ _('Submitted Manually') }</th>
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

<style type="text/css">
@media (max-width: 1360px) {
  .hide-small {
    display: none;
  }
}
@media (max-width: 1240px) {
  .hide-smaller {
    display: none;
  }
  .btn-group {
    margin-left: 10px;
  }
}
</style>

<script src="${ static('oozie/js/dashboard-utils.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/datatables-paging-0.1.js') }" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript">
  var Workflow = function (wf) {
    return {
      id: wf.id,
      lastModTimeFormatted: wf.lastModTimeFormatted,
      lastModTimeInMillis: wf.lastModTimeInMillis,
      endTime: wf.endTime,
      endTimeInMillis: wf.endTimeInMillis,
      status: wf.status,
      statusClass: "label " + getStatusClass(wf.status),
      isRunning: wf.isRunning,
      duration: wf.duration,
      durationInMillis: wf.durationInMillis,
      appName: wf.appName,
      progress: wf.progress,
      progressClass: "bar " + getStatusClass(wf.status, "bar-"),
      user: wf.user,
      absoluteUrl: wf.absoluteUrl,
      canEdit: wf.canEdit,
      killUrl: wf.killUrl,
      suspendUrl: wf.suspendUrl,
      resumeUrl: wf.resumeUrl,
      created: wf.created,
      createdInMillis: wf.createdInMillis,
      run: wf.run,
      parentUrl: wf.parentUrl,
      submittedManually: wf.submittedManually,
    }
  }

  var refreshRunning, runningTimeout, progressTimeout, jobProgressMap = {};
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
        null,
        null,
        { "sSortDataType":"dom-sort-value", "sType":"numeric" },
        null,
        null,
        { "bVisible": false }
      ],
      "aaSorting":[
        [ 0, "desc" ]
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
        { "sSortDataType":"dom-sort-value", "sType":"numeric" },
        null,
        null,
        null,
        { "bVisible": false }
      ],
      "aaSorting":[
        [ 0, "desc" ]
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
        drawTable();
      % endif
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
          refreshProgress();
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
      refreshTables();
    });

    $("a.btn-submitted").click(function () {
      $("a.btn-submitted").not(this).removeClass("active");
      $(this).toggleClass("active");
      drawTable();
    });

    $("a.btn-date").click(function () {
      refreshPagination();
      $("a.btn-date").not(this).removeClass("active");
      $(this).toggleClass("active");
      refreshTables();
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

    function refreshPagination() {
      runningTableOffset = 1;
      completedTableOffset = 1;

      // Clear select-all
      $(".hue-checkbox").removeClass("fa-check");
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
      var selectedStatuses = (type == 'running') ? ['RUNNING', 'PREP', 'SUSPENDED'] : ['SUCCEEDED', 'KILLED', 'FAILED'];
      var btnStatuses = [];

      var statusBtns = $("a.btn-status.active");
      $.each(statusBtns, function () {
        val = $(this).data('value');
        if (val == 'SUCCEEDED') {
          btnStatuses = btnStatuses.concat(['SUCCEEDED']);
        } else if (val == 'RUNNING') {
          btnStatuses = btnStatuses.concat(['RUNNING', 'PREP', 'SUSPENDED']);
        } else if (val == 'ERROR') {
          btnStatuses = btnStatuses.concat(['KILLED', 'FAILED']);
        }
      });

      if (btnStatuses.length > 0) {
        selectedStatuses = $.makeArray($(selectedStatuses).filter(btnStatuses));
      }
      return selectedStatuses.length > 0 ? ('&status=' + selectedStatuses.join('&status=')) : '';
    }

    function getDaysFilter() {
      var dateBtn = $("a.btn-date.active");
      var daysFilter = ''
      if (dateBtn.length > 0) {
        daysFilter = '&startcreatedtime=-' + dateBtn.attr("data-value") + 'd';
      }
      return daysFilter;
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

    $.fn.dataTableExt.sErrMode = "throw";

    $.fn.dataTableExt.afnFiltering.push(PersistedButtonsFilters); // from dashboard-utils.js

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
      $("#confirmation a.btn-danger").on("click", function () {
        _this.trigger("confirmation");
        $(this).attr("data-loading-text", $(this).text() + " ...");
        $(this).button("loading");
      });
    });

    var numRunning = 0;

    refreshRunning = function () {
      window.clearTimeout(runningTimeout);
      $.getJSON(window.location.pathname + "?format=json&offset=" + runningTableOffset + getStatuses('running') + getDaysFilter() + getTextFilter(), function (data) {
        if (data.jobs.length > 0) {
          totalRunningJobs = data.total_jobs;
          refreshPaginationButtons("running", totalRunningJobs);

          var nNodes = runningTable.fnGetNodes();

          // Find previously selected jobs
          var _ids = [];
          $(".hue-checkbox.fa-check:not(.select-all)").each(function(){
            _ids.push($(this).parents("tr").find("a[data-row-selector='true']").text());
          });
          runningTable.fnClearTable();

          $(data.jobs).each(function (iWf, item) {
            var wf = new Workflow(item);

            // Restore previously selected jobs
            var foundRow = _ids.indexOf(wf.id) != -1;

            var checkboxSelected = "";
            if (foundRow) {
              checkboxSelected = "fa-check";
            }
            var progressColumn = '<div class="progress"><div class="bar bar-warning" style="width: 1%"></div></div>';
            if (wf.id in jobProgressMap) {
              progressColumn = '<div class="progress"><div class="' + jobProgressMap[wf.id]["progressClass"] + '" style="width:' + jobProgressMap[wf.id]["progress"] + '%">' + jobProgressMap[wf.id]["progress"] + '%</div></div>';
            }

            if (['RUNNING', 'PREP', 'WAITING', 'SUSPENDED', 'PREPSUSPENDED', 'PREPPAUSED', 'PAUSED', 'STARTED', 'FINISHING'].indexOf(wf.status) > -1) {
              try {
                runningTable.fnAddData([
                  wf.canEdit ? '<div class="hue-checkbox fa ' + checkboxSelected + '" data-row-selector-exclude="true"></div>':'',
                  '<span data-sort-value="'+ wf.createdInMillis +'" data-type="date">' + emptyStringIfNull(wf.created) + '</span>',
                  '<span class="' + wf.statusClass + '" data-type="status">' + wf.status + '</span>',
                  wf.appName,
                  progressColumn,
                  wf.user,
                  '<span data-sort-value="'+ wf.lastModTimeInMillis +'">' + emptyStringIfNull(wf.lastModTimeFormatted) + '</span>',
                  '<a href="' + wf.absoluteUrl + '" data-row-selector="true">' + wf.id + '</a>',
                  wf.parentUrl == '' ? '' : '<div style="text-align:center"><a href="' + wf.parentUrl + '" style="text-align:center"><img src="' + getParentImage(wf.parentUrl) + '" class="app-icon"/></a></div>',
                  wf.submittedManually
                ]);
              }
              catch (error) {
                $(document).trigger("error", error);
              }
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

        runningTable.fnDraw();
        runningTimeout = window.setTimeout(refreshRunning, 5000);
        ko.bindingHandlers.multiCheck.init(runningTable[0], function() { return '#' + runningTable[0].id})
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

    function getParentImage(parentUrl) {
      var _sub = parentUrl[parentUrl.length - 2];
      switch (_sub) {
        case "W":
          return "${static("oozie/art/icon_oozie_workflow_48.png")}"
          break;
        case "C":
          return "${static("oozie/art/icon_oozie_coordinator_48.png")}"
          break;
        case "B":
          return "${static("oozie/art/icon_oozie_bundle_48.png")}"
          break;
        default:
          return "${static("oozie/art/icon_oozie_48.png")}";
          break;
      }
    }

    function refreshCompleted() {
      $.getJSON(window.location.pathname + "?format=json&offset=" + completedTableOffset + getStatuses('completed') + getDaysFilter() + getTextFilter(), function (data) {
        if(data.jobs.length > 0) {
          totalCompletedJobs = data.total_jobs;
          refreshPaginationButtons("completed", totalCompletedJobs);
        }
        completedTable.fnClearTable();
        $(data.jobs).each(function (iWf, item) {
          var wf = new Workflow(item);
          try {
            completedTable.fnAddData([
                  '<span data-sort-value="' + wf.endTimeInMillis + '" data-type="date">' + emptyStringIfNull(wf.endTime) + '</span>',
                  '<span class="' + wf.statusClass + '" data-type="status">' + wf.status + '</span>', decodeURIComponent(wf.appName),
                  '<span data-sort-value="' + wf.durationInMillis + '">' + emptyStringIfNull(wf.duration) + '</span>',
              wf.user,
                  '<a href="' + wf.absoluteUrl + '" data-row-selector="true">' + wf.id + '</a>',
                  wf.parentUrl == '' ? '' : '<div style="text-align:center"><a href="' + wf.parentUrl + '" style="text-align:center"><img src="' + getParentImage(wf.parentUrl) + '" class="app-icon"/></a></div>',
              wf.submittedManually
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
      window.clearTimeout(progressTimeout);
      $.getJSON(window.location.pathname + "?format=json&type=progress&offset=" + runningTableOffset + getStatuses('running') + getDaysFilter() + getTextFilter(), function (data) {
        var nNodes = runningTable.fnGetNodes();
        $(data.jobs).each(function (iWf, item) {
            var wf = new Workflow(item);
            var foundRow = null;

            // Remember job progress info
            jobProgressMap[wf.id] = {"progressClass": wf.progressClass, "progress": wf.progress};
            $(nNodes).each(function (iNode, node) {
              if ($(node).children("td").eq(7).text() == wf.id) {
                foundRow = node;
              }
            });
            if (foundRow != null) {
              runningTable.fnUpdate('<span class="' + wf.statusClass + '" data-type="status">' + wf.status + '</span>', foundRow, 2, false);
              if (wf.progress == 0){
                runningTable.fnUpdate('<div class="progress"><div class="bar bar-warning" style="width: 1%"></div></div>', foundRow, 4, false);
              }
              else {
                runningTable.fnUpdate('<div class="progress"><div class="' + wf.progressClass + '" style="width:' + wf.progress + '%">' + wf.progress + '%</div></div>', foundRow, 4, false);
              }
            }
          });
        progressTimeout = window.setTimeout(refreshProgress, 20000);
      });
    }

    refreshTables();

  });

</script>

${ utils.bulk_dashboard_functions() }

${ commonfooter(request, messages) | n,unicode }

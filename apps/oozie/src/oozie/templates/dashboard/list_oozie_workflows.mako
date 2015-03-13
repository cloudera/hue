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


${ commonheader(_("Workflows Dashboard"), "oozie", user) | n,unicode }
${ layout.menubar(section='workflows', dashboard=True) }


<div class="container-fluid">
  <div class="card card-small">
  <div class="card-body">
  <p>
  <form>
    <input type="text" id="filterInput" class="input-xlarge search-query" placeholder="${ _('Search for username, name, etc...') }">

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
        <a class="btn btn-status btn-danger disable-feedback" data-value='KILLED'>${ _('Killed') }</a>
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
          <th width="1%"><div class="select-all hueCheckbox fa"></div></th>
          <th width="14%">${ _('Submission') }</th>
          <th width="5%">${ _('Status') }</th>
          <th width="31%">${ _('Name') }</th>
          <th width="7%">${ _('Progress') }</th>
          <th width="7%">${ _('Submitter') }</th>
          <th width="7%">${ _('Last Modified') }</th>
          <th width="23%">${ _('Id') }</th>
          <th width="5%">${ _('Parent') }</th>
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
        </tr>
      </tbody>
    </table>

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
        </tr>
      </tbody>
     </table>
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

<script type="text/javascript" charset="utf-8">
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
    }
  }

  var refreshRunning;

  $(document).ready(function () {
    var runningTable = $("#running-table").dataTable({
      "sPaginationType":"bootstrap",
      "iDisplayLength":50,
      "bLengthChange":false,
      "sDom":"<'row'r>t<'row'<'span6'i><''p>>",
      "aoColumns":[
        { "bSortable":false },
        { "sSortDataType":"dom-sort-value", "sType":"numeric" },
        null,
        null,
        null,
        null,
        { "sSortDataType":"dom-sort-value", "sType":"numeric" },
        null,
        null
      ],
      "aaSorting":[
        [ 0, "desc" ]
      ],
      "oLanguage":{
        "sEmptyTable":"${_('No data available')}",
        "sInfo":"${_('Showing _START_ to _END_ of _TOTAL_ entries')}",
        "sInfoEmpty":"${_('Showing 0 to 0 of 0 entries')}",
        "sInfoFiltered":"${_('(filtered from _MAX_ total entries)')}",
        "sZeroRecords":"${_('No matching records')}",
        "oPaginate":{
          "sFirst":"${_('First')}",
          "sLast":"${_('Last')}",
          "sNext":"${_('Next')}",
          "sPrevious":"${_('Previous')}"
        }
      },
      "fnDrawCallback":function (oSettings) {
        $("a[data-row-selector='true']").jHueRowSelector();
      }
    });

    var completedTable = $("#completed-table").dataTable({
      "sPaginationType":"bootstrap",
      "iDisplayLength":50,
      "bLengthChange":false,
      "sDom":"<'row'r>t<'row'<'span6'i><''p>>",
      "aoColumns":[
        { "sSortDataType":"dom-sort-value", "sType":"numeric" },
        null,
        null,
        { "sSortDataType":"dom-sort-value", "sType":"numeric" },
        null,
        null,
        null
      ],
      "aaSorting":[
        [ 0, "desc" ]
      ],
      "oLanguage":{
        "sEmptyTable":"${_('No data available')}",
        "sInfo":"${_('Showing _START_ to _END_ of _TOTAL_ entries')}",
        "sInfoEmpty":"${_('Showing 0 to 0 of 0 entries')}",
        "sInfoFiltered":"${_('(filtered from _MAX_ total entries)')}",
        "sZeroRecords":"${_('No matching records')}",
        "oPaginate":{
          "sFirst":"${_('First')}",
          "sLast":"${_('Last')}",
          "sNext":"${_('Next')}",
          "sPrevious":"${_('Previous')}"
        }
      },
      "fnDrawCallback":function (oSettings) {
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
      runningTable.fnFilter($(this).val());
      completedTable.fnFilter($(this).val());
      drawTable();
    });


    $("a.btn-status").click(function () {
      $(this).toggleClass("active");
      drawTable();
    });

    $("a.btn-submitted").click(function () {
      $("a.btn-submitted").not(this).removeClass("active");
      $(this).toggleClass("active");
      drawTable();
    });

    $("a.btn-date").click(function () {
      $("a.btn-date").not(this).removeClass("active");
      $(this).toggleClass("active");
      drawTable();
    });

    var hash = window.location.hash.replace(/(<([^>]+)>)/ig, "");
    if (hash != "" && hash.indexOf("=") > -1) {
      $("a.btn-date[data-value='" + hash.split("=")[1] + "']").click();
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
      $.getJSON(window.location.pathname + "?format=json&type=running", function (data) {
        if (data.jobs) {
          var nNodes = runningTable.fnGetNodes();

          // check for zombie nodes
          $(nNodes).each(function (iNode, node) {
            var nodeFound = false;
            $(data.jobs).each(function (iWf, currentItem) {
              if ($(node).children("td").eq(7).text() == currentItem.id) {
                nodeFound = true;
              }
            });
            if (!nodeFound) {
              runningTable.fnDeleteRow(node);
              runningTable.fnDraw();
            }
          });

          $(data.jobs).each(function (iWf, item) {
            var wf = new Workflow(item);
            var foundRow = null;
            $(nNodes).each(function (iNode, node) {
              if ($(node).children("td").eq(7).text() == wf.id) {
                foundRow = node;
              }
            });
            if (foundRow == null) {
              if (['RUNNING', 'PREP', 'WAITING', 'SUSPENDED', 'PREPSUSPENDED', 'PREPPAUSED', 'PAUSED', 'STARTED', 'FINISHING'].indexOf(wf.status) > -1) {
                try {
                  runningTable.fnAddData([
                    wf.canEdit ? '<div class="hueCheckbox fa" data-row-selector-exclude="true"></div>':'',
                    '<span data-sort-value="'+ wf.createdInMillis +'" data-type="date">' + emptyStringIfNull(wf.created) + '</span>',
                    '<span class="' + wf.statusClass + '" data-type="status">' + wf.status + '</span>',
                    wf.appName,
                    '<div class="progress"><div class="bar bar-warning" style="width: 1%"></div></div>',
                    wf.user,
                    '<span data-sort-value="'+ wf.lastModTimeInMillis +'">' + emptyStringIfNull(wf.lastModTimeFormatted) + '</span>',
                    '<a href="' + wf.absoluteUrl + '" data-row-selector="true">' + wf.id + '</a>',
                    wf.parentUrl == '' ? '' : '<div style="text-align:center"><a href="' + wf.parentUrl + '" style="text-align:center"><img src="' + getParentImage(wf.parentUrl) + '" class="app-icon"/></a></div>'
                  ]);
                }
                catch (error) {
                  $(document).trigger("error", error);
                }
              }
            }
            else {
              runningTable.fnUpdate('<span class="' + wf.statusClass + '" data-type="status">' + wf.status + '</span>', foundRow, 2, false);
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

        window.setTimeout(refreshRunning, 5000);
      });
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
      $.getJSON(window.location.pathname + "?format=json&type=completed", function (data) {
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
                  wf.parentUrl == '' ? '' : '<div style="text-align:center"><a href="' + wf.parentUrl + '" style="text-align:center"><img src="' + getParentImage(wf.parentUrl) + '" class="app-icon"/></a></div>'
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
      $.getJSON(window.location.pathname + "?format=json&type=progress", function (data) {
        var nNodes = runningTable.fnGetNodes();
        $(data.jobs).each(function (iWf, item) {
            var wf = new Workflow(item);
            var foundRow = null;
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
        window.setTimeout(refreshProgress, 20000);
      });
    }

    refreshRunning();
    refreshCompleted();
    refreshProgress();

  });

</script>

${ utils.bulk_dashboard_functions() }

${ commonfooter(messages) | n,unicode }

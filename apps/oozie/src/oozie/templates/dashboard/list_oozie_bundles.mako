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

${ commonheader(_("Bundles Dashboard"), "oozie", user) | n,unicode }
${layout.menubar(section='bundles', dashboard=True)}


<div class="container-fluid">
  <div class="card card-small">
  <div class="card-body">
  <p>
  <form>
    <input type="text" id="filterInput" class="input-xlarge search-query" placeholder="${ _('Search for username, name, etc...') }">

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
        <a class="btn btn-status btn-danger disable-feedback" data-value='KILLED'>${ _('Killed') }</a>
      </span>
    </span>
  </form>

  <div style="min-height:200px">
    <h1 class="card-heading simple">${ _('Running') }</h1>
    <table class="table table-condensed" id="running-table">
      <thead>
        <tr>
          <th width="1%"><div class="select-all hueCheckbox fa"></div></th>
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

<script src="${ static('oozie/js/dashboard-utils.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/datatables-paging-0.1.js') }" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript" charset="utf-8">
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
        { "sSortDataType":"dom-sort-value", "sType":"numeric" },
        null,
        { "sSortDataType":"dom-sort-value", "sType":"numeric" },
        null
      ],
      "aaSorting":[
        [ 5, "desc" ]
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
        null,
        { "sSortDataType":"dom-sort-value", "sType":"numeric" },
        null
      ],
      "aaSorting":[
        [ 4, "desc" ]
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

      var hash = "#";
      if ($("a.btn-date.active").length > 0) {
        hash += "date=" + $("a.btn-date.active").text();
      }
      window.location.hash = hash;
    });


    $("a.btn-status").click(function () {
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
      $("#confirmation a.btn-danger").click(function () {
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
                    bundle.canEdit ? '<div class="hueCheckbox fa" data-row-selector-exclude="true"></div>' : '',
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

        window.setTimeout(refreshRunning, 20000);
      });
    }

    function refreshCompleted() {
      $.getJSON(window.location.pathname + "?format=json&type=completed", function (data) {
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
      $.getJSON(window.location.pathname + "?format=json&type=progress", function (data) {
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

    refreshRunning();
    refreshCompleted();
    refreshProgress();

  });
</script>

${ utils.bulk_dashboard_functions() }

${ commonfooter(messages) | n,unicode }

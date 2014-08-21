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
          <th width="15%">${ _('Submission') }</th>
          <th width="5%">${ _('Status') }</th>
          <th width="21%">${ _('Name') }</th>
          <th width="7%">${ _('Progress') }</th>
          <th width="7%">${ _('Submitter') }</th>
          <th width="15%">${ _('Last Modified') }</th>
          <th width="20%">${ _('Id') }</th>
          <th width="10%">${ _('Action') }</th>
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
          <th width="15%">${ _('Completion') }</th>
          <th width="7%">${ _('Status') }</th>
          <th width="25%">${ _('Name') }</th>
          <th width="7%">${ _('Duration') }</th>
          <th width="10%">${ _('Submitter') }</th>
          <th width="15%">${ _('Last Modified') }</th>
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

<script src="/oozie/static/js/bundles.utils.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/datatables-paging-0.1.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript" charset="utf-8">
  var Workflow = function (wf) {
    return {
      id: wf.id,
      lastModTime: wf.lastModTime,
      endTime: wf.endTime,
      status: wf.status,
      statusClass: "label " + getStatusClass(wf.status),
      isRunning: wf.isRunning,
      duration: wf.duration,
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
      run: wf.run
    }
  }

  $(document).ready(function () {
    var runningTable = $("#running-table").dataTable({
      "sPaginationType":"bootstrap",
      "iDisplayLength":50,
      "bLengthChange":false,
      "sDom":"<'row'r>t<'row'<'span6'i><''p>>",
      "aoColumns":[
        { "sType":"date" },
        null,
        null,
        null,
        null,
        { "sSortDataType":"dom-sort-value", "sType":"numeric" },
        null,
        { "bSortable":false }
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
        { "sType":"date" },
        null,
        null,
        null,
        null,
        { "sSortDataType":"dom-sort-value", "sType":"numeric" },
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

    $("a.btn-date").click(function () {
      $("a.btn-date").not(this).removeClass("active");
      $(this).toggleClass("active");
      drawTable();
    });

    var hash = window.location.hash;
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

    $.fn.dataTableExt.afnFiltering.push(
      function (oSettings, aData, iDataIndex) {
        var urlHashes = ""

        var statusBtn = $("a.btn-status.active");
        var statusFilter = true;
        if (statusBtn.length > 0) {
          var statuses = []
          $.each(statusBtn, function () {
            statuses.push($(this).attr("data-value"));
          });
          statusFilter = aData[1].match(RegExp(statuses.join('|'), "i")) != null;
        }

        var dateBtn = $("a.btn-date.active");
        var dateFilter = true;
        if (dateBtn.length > 0) {
          var minAge = new Date() - parseInt(dateBtn.attr("data-value")) * 1000 * 60 * 60 * 24;
          dateFilter = Date.parse(aData[0]) >= minAge;
        }

        return statusFilter && dateFilter;
      }
    );

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

    refreshRunning();
    refreshCompleted();
    refreshProgress();

    var numRunning = 0;

    function refreshRunning() {
      $.getJSON(window.location.pathname + "?format=json&type=running", function (data) {
        if (data) {
          var nNodes = runningTable.fnGetNodes();

          // check for zombie nodes
          $(nNodes).each(function (iNode, node) {
            var nodeFound = false;
            $(data).each(function (iWf, currentItem) {
              if ($(node).children("td").eq(6).text() == currentItem.id) {
                nodeFound = true;
              }
            });
            if (!nodeFound) {
              runningTable.fnDeleteRow(node);
              runningTable.fnDraw();
            }
          });

          $(data).each(function (iWf, item) {
            var wf = new Workflow(item);
            var foundRow = null;
            $(nNodes).each(function (iNode, node) {
              if ($(node).children("td").eq(6).text() == wf.id) {
                foundRow = node;
              }
            });
            var killCell = "";
            var suspendCell = "";
            var resumeCell = "";
            if (wf.canEdit) {
              killCell = '<a class="btn btn-mini btn-danger disable-feedback confirmationModal" ' +
                      'href="javascript:void(0)" ' +
                      'data-url="' + wf.killUrl + '" ' +
                      'title="${ _('Kill') } ' + wf.id + '"' +
                      'alt="${ _('Are you sure you want to kill workflow ')}' + wf.id + '?" ' +
                      'data-message="${ _('The workflow was killed!') }" ' +
                      'data-confirmation-message="${ _('Are you sure you\'d like to kill this job?') }"' +
                      '>${ _('Kill') }</a>';
              suspendCell = '<a class="btn btn-mini confirmationModal" ' +
                      'href="javascript:void(0)" ' +
                      'data-url="' + wf.suspendUrl + '" ' +
                      'title="${ _('Suspend') } ' + wf.id + '"' +
                      'alt="${ _('Are you sure you want to suspend workflow ')}' + wf.id + '?" ' +
                      'data-message="${ _('The workflow was suspended!') }" ' +
                      'data-confirmation-message="${ _('Are you sure you\'d like to suspend this job?') }"' +
                      '>${ _('Suspend') }</a>';
              resumeCell = '<a class="btn btn-mini confirmationModal" ' +
                      'href="javascript:void(0)" ' +
                      'data-url="' + wf.resumeUrl + '" ' +
                      'title="${ _('Resume') } ' + wf.id + '"' +
                      'alt="${ _('Are you sure you want to resume workflow ')}' + wf.id + '?" ' +
                      'data-message="${ _('The workflow was resumed!') }" ' +
                      'data-confirmation-message="${ _('Are you sure you\'d like to resume this job?') }"' +
                      '>${ _('Resume') }</a>';
            }
            if (foundRow == null) {
              if (['RUNNING', 'PREP', 'WAITING', 'SUSPENDED', 'PREPSUSPENDED', 'PREPPAUSED', 'PAUSED', 'STARTED', 'FINISHING'].indexOf(wf.status) > -1) {
                try {
                  runningTable.fnAddData([
                    emptyStringIfNull(wf.lastModTime),
                    '<span class="' + wf.statusClass + '">' + wf.status + '</span>',
                    wf.appName,
                    '<div class="progress"><div class="bar bar-warning" style="width: 1%"></div></div>',
                    wf.user,
                    emptyStringIfNull(wf.lastModTime),
                    '<a href="' + wf.absoluteUrl + '" data-row-selector="true">' + wf.id + '</a>',
                    killCell + " " + (['RUNNING', 'PREP', 'WAITING'].indexOf(wf.status) > -1 ? suspendCell : resumeCell)
                  ]);
                }
                catch (error) {
                  $(document).trigger("error", error);
                }
              }
            }
            else {
              runningTable.fnUpdate('<span class="' + wf.statusClass + '">' + wf.status + '</span>', foundRow, 1, false);
              runningTable.fnUpdate(killCell + " " + (['RUNNING', 'PREP', 'WAITING'].indexOf(wf.status) > -1?suspendCell:resumeCell), foundRow, 7, false);
            }
          });
        }
        if (data.length == 0) {
          runningTable.fnClearTable();
        }

        if (data.length != numRunning) {
          refreshCompleted();
        }
        numRunning = data.length;

        window.setTimeout(refreshRunning, 5000);
      });
    }

    function refreshCompleted() {
      $.getJSON(window.location.pathname + "?format=json&type=completed", function (data) {
        completedTable.fnClearTable();
        $(data).each(function (iWf, item) {
          var wf = new Workflow(item);
          try {
            completedTable.fnAddData([
              emptyStringIfNull(wf.endTime),
              '<span class="' + wf.statusClass + '">' + wf.status + '</span>', decodeURIComponent(wf.appName),
              emptyStringIfNull(wf.duration),
              wf.user,
              emptyStringIfNull(wf.lastModTime),
              '<a href="' + wf.absoluteUrl + '" data-row-selector="true">' + wf.id + '</a>'
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
        $(data).each(function (iWf, item) {
            var wf = new Workflow(item);
            var foundRow = null;
            $(nNodes).each(function (iNode, node) {
              if ($(node).children("td").eq(6).text() == wf.id) {
                foundRow = node;
              }
            });
            if (foundRow != null) {
              runningTable.fnUpdate('<span class="' + wf.statusClass + '">' + wf.status + '</span>', foundRow, 1, false);
              if (wf.progress == 0){
                runningTable.fnUpdate('<div class="progress"><div class="bar bar-warning" style="width: 1%"></div></div>', foundRow, 3, false);
              }
              else {
                runningTable.fnUpdate('<div class="progress"><div class="' + wf.progressClass + '" style="width:' + wf.progress + '%">' + wf.progress + '%</div></div>', foundRow, 3, false);
              }
            }
          });
        window.setTimeout(refreshProgress, 20000);
      });
    }

  });

</script>

${ commonfooter(messages) | n,unicode }

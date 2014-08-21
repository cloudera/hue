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

${ commonheader(_("Coordinators Dashboard"), "oozie", user) | n,unicode }
${layout.menubar(section='coordinators', dashboard=True)}


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
          <th width="12%">${ _('Next Submission') }</th>
          <th width="5%">${ _('Status') }</th>
          <th width="20%">${ _('Name') }</th>
          <th width="5%">${ _('Progress') }</th>
          <th width="10%">${ _('Submitter') }</th>
          % if enable_cron_scheduling:
          <th width="8%">${ _('Frequency') }</th>
          % else:
          <th width="3%">${ _('Frequency') }</th>
          <th width="5%">${ _('Time Unit') }</th>
          % endif
          <th width="12%">${ _('Start Time') }</th>
          <th width="15%">${ _('Id') }</th>
          <th width="10%">${ _('Action') }</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><i class="fa fa-2x fa-spinner fa-spin muted"></i></td>
          <td></td>
          <td></td>
          <td></td>
          % if not enable_cron_scheduling:
          <td></td>
          % endif
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
          <th width="12%">${ _('Completion') }</th>
          <th width="5%">${ _('Status') }</th>
          <th width="20%">${ _('Name') }</th>
          <th width="10%">${ _('Duration') }</th>
          <th width="10%">${ _('Submitter') }</th>
          % if enable_cron_scheduling:
          <th width="10%">${ _('Frequency') }</th>
          % else:
          <th width="5%">${ _('Frequency') }</th>
          <th width="5%">${ _('Time Unit') }</th>
          % endif
          <th width="13%">${ _('Start Time') }</th>
          <th width="20%">${ _('Id') }</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><i class="fa fa-2x fa-spinner fa-spin muted"></i></td>
          <td></td>
          <td></td>
          <td></td>
          % if not enable_cron_scheduling:
          <td></td>
          % endif
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

% if enable_cron_scheduling:
<link href="/static/css/jqCron.css" rel="stylesheet" type="text/css" />
<script src="/static/js/jqCron.js" type="text/javascript"></script>
% endif

<script type="text/javascript" charset="utf-8">

  var Coordinator = function (c) {
    return {
      id: c.id,
      endTime: c.endTime,
      nextMaterializedTime: c.nextMaterializedTime,
      status: c.status,
      statusClass: "label " + getStatusClass(c.status),
      isRunning: c.isRunning,
      duration: c.duration,
      appName: decodeURIComponent(c.appName),
      progress: c.progress,
      progressClass: "bar " + getStatusClass(c.status, "bar-"),
      user: c.user,
      absoluteUrl: c.absoluteUrl,
      canEdit: c.canEdit,
      killUrl: c.killUrl,
      suspendUrl: c.suspendUrl,
      resumeUrl: c.resumeUrl,
      frequency: c.frequency,
      timeUnit: c.timeUnit,
      startTime: c.startTime
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
        { "sSortDataType":"dom-sort-value", "sType":"numeric" },
        null,
        null,
        null,
        % if not enable_cron_scheduling:
        null,
        % endif
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
        { "sSortDataType":"dom-sort-value", "sType":"numeric" },
        null,
        null,
        null,
        % if not enable_cron_scheduling:
        null,
        % endif
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
      $("#confirmation a.btn-danger").click(function () {
        _this.trigger("confirmation");
        $(this).attr("data-loading-text", $(this).text() + " ...");
        $(this).button("loading");
      });
    });

    % if enable_cron_scheduling:
    ${ utils.cron_js() }
    % endif


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
            $(data).each(function (iCoord, currentItem) {
              % if enable_cron_scheduling:
              if ($(node).children("td").eq(7).text() == currentItem.id) {
                 nodeFound = true;
              }
              % else:
              if ($(node).children("td").eq(8).text() == currentItem.id) {
                 nodeFound = true;
              }
              % endif

            });
            if (!nodeFound) {
              runningTable.fnDeleteRow(node);
              runningTable.fnDraw();
            }
          });

          $(data).each(function (iCoord, item) {
            var coord = new Coordinator(item);
            var foundRow = null;
            $(nNodes).each(function (iNode, node) {
              % if enable_cron_scheduling:
              if ($(node).children("td").eq(7).text() == coord.id) {
                foundRow = node;
              }
              % else:
              if ($(node).children("td").eq(8).text() == coord.id) {
                foundRow = node;
              }
              % endif
            });
            var killCell = "";
            var suspendCell = "";
            var resumeCell = "";
            if (coord.canEdit) {
              killCell = '<a class="btn btn-mini btn-danger disable-feedback confirmationModal" ' +
                      'href="javascript:void(0)" ' +
                      'data-url="' + coord.killUrl + '" ' +
                      'title="${ _('Kill') } ' + coord.id + '"' +
                      'alt="${ _('Are you sure you want to kill coordinator ')}' + coord.id + '?" ' +
                      'data-message="${ _('The coordinator was killed!') }" ' +
                      'data-confirmation-message="${ _('Are you sure you\'d like to kill this job?') }"' +
                      '>${ _('Kill') }</a>';
              suspendCell = '<a class="btn btn-mini confirmationModal" ' +
                      'href="javascript:void(0)" ' +
                      'data-url="' + coord.suspendUrl + '" ' +
                      'title="${ _('Suspend') } ' + coord.id + '"' +
                      'alt="${ _('Are you sure you want to suspend coordinator ')}' + coord.id + '?" ' +
                      'data-message="${ _('The coordinator was suspended!') }" ' +
                      'data-confirmation-message="${ _('Are you sure you\'d like to suspend this job?') }"' +
                      '>${ _('Suspend') }</a>';
              resumeCell = '<a class="btn btn-mini confirmationModal" ' +
                      'href="javascript:void(0)" ' +
                      'data-url="' + coord.resumeUrl + '" ' +
                      'title="${ _('Resume') } ' + coord.id + '"' +
                      'alt="${ _('Are you sure you want to resume coordinator ')}' + coord.id + '?" ' +
                      'data-message="${ _('The coordinator was resumed!') }" ' +
                      'data-confirmation-message="${ _('Are you sure you\'d like to resume this job?') }"' +
                      '>${ _('Resume') }</a>';
            }
            if (foundRow == null) {
              if (['RUNNING', 'PREP', 'WAITING', 'SUSPENDED', 'PREPSUSPENDED', 'PREPPAUSED', 'PAUSED', 'STARTED', 'FINISHING'].indexOf(coord.status) > -1) {
                try {
                  runningTable.fnAddData([
                    emptyStringIfNull(coord.nextMaterializedTime),
                    '<span class="' + coord.statusClass + '">' + coord.status + '</span>',
                    coord.appName,
                    '<div class="progress"><div class="bar bar-warning" style="width: 1%"></div></div>',
                    coord.user,
                    % if enable_cron_scheduling:
                    '<div class="cron-frequency"><input class="value" type="hidden" value="'+emptyStringIfNull(coord.frequency)+'"/></div>',
                    % else:
                    emptyStringIfNull(coord.frequency),
                    emptyStringIfNull(coord.timeUnit),
                    % endif
                    emptyStringIfNull(coord.startTime),
                    '<a href="' + coord.absoluteUrl + '" data-row-selector="true">' + coord.id + '</a>',
                    killCell + " " + (['RUNNING', 'PREP', 'WAITING'].indexOf(coord.status) > -1?suspendCell:resumeCell)
                  ]);
                }
                catch (error) {
                  $(document).trigger("error", error);
                }
              }
            }
            else {
              runningTable.fnUpdate('<span class="' + coord.statusClass + '">' + coord.status + '</span>', foundRow, 1, false);
              % if enable_cron_scheduling:
              runningTable.fnUpdate(killCell + " " + (['RUNNING', 'PREP', 'WAITING'].indexOf(coord.status) > -1?suspendCell:resumeCell), foundRow, 9, false);
              % else:
              runningTable.fnUpdate(killCell + " " + (['RUNNING', 'PREP', 'WAITING'].indexOf(coord.status) > -1?suspendCell:resumeCell), foundRow, 10, false);
              % endif

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
        % if enable_cron_scheduling:
        renderCrons(); // utils.inc.mako
        % endif
        window.setTimeout(refreshRunning, 20000);
      });
    }

    function refreshCompleted() {
      $.getJSON(window.location.pathname + "?format=json&type=completed", function (data) {
        completedTable.fnClearTable();
        $(data).each(function (iWf, item) {
          var coord = new Coordinator(item);
          try {
            completedTable.fnAddData([
              emptyStringIfNull(coord.endTime),
              '<span class="' + coord.statusClass + '">' + coord.status + '</span>',
              coord.appName,
              emptyStringIfNull(coord.duration),
              coord.user,
              % if enable_cron_scheduling:
              '<div class="cron-frequency"><input class="value" type="hidden" value="'+emptyStringIfNull(coord.frequency)+'"/></div>',
              % else:
              emptyStringIfNull(coord.frequency),
              emptyStringIfNull(coord.timeUnit),
              % endif
              emptyStringIfNull(coord.startTime),
              '<a href="' + coord.absoluteUrl + '" data-row-selector="true">' + coord.id + '</a>'
            ], false);
          }
          catch (error) {
            $(document).trigger("error", error);
          }
        });
        completedTable.fnDraw();
        % if enable_cron_scheduling:
        renderCrons(); // utils.inc.mako
        % endif
      });
    }

    function refreshProgress() {
      $.getJSON(window.location.pathname + "?format=json&type=progress", function (data) {
        var nNodes = runningTable.fnGetNodes();
          $(data).each(function (iCoord, item) {
            var coord = new Coordinator(item);
            var foundRow = null;
            $(nNodes).each(function (iNode, node) {
              % if enable_cron_scheduling:
              if ($(node).children("td").eq(7).text() == coord.id) {
                foundRow = node;
              }
              % else:
              if ($(node).children("td").eq(8).text() == coord.id) {
                foundRow = node;
              }
              % endif
            });
            if (foundRow != null) {
              if (coord.progress == 0){
                runningTable.fnUpdate('<div class="progress"><div class="bar bar-warning" style="width: 1%"></div></div>', foundRow, 3, false);
              }
              else {
                runningTable.fnUpdate('<div class="progress"><div class="' + coord.progressClass + '" style="width:' + coord.progress + '%">' + coord.progress + '%</div></div>', foundRow, 3, false);
              }
            }
          });
        window.setTimeout(refreshProgress, 30000);
      });
    }
  });
</script>

${ commonfooter(messages) | n,unicode }

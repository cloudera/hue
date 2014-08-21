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
          <th width="15%">${ _('Kickoff Time') }</th>
          <th width="10%">${ _('Status') }</th>
          <th width="20%">${ _('Name') }</th>
          <th width="10%">${ _('Progress') }</th>
          <th width="10%">${ _('Submitter') }</th>
          <th width="10%">${ _('Created Time') }</th>
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

<script src="/oozie/static/js/bundles.utils.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/datatables-paging-0.1.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript" charset="utf-8">
  var Bundle = function (bundle) {
    return {
      id: bundle.id,
      endTime: bundle.endTime,
      status: bundle.status,
      statusClass: "label " + getStatusClass(bundle.status),
      isRunning: bundle.isRunning,
      kickoffTime: bundle.kickoffTime,
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
      created: bundle.created
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
        { "bSortable":false }
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
        { "sType":"date" },
        null,
        null,
        null,
        null,
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
            $(data).each(function (iBundle, currentItem) {
              if ($(node).children("td").eq(6).text() == currentItem.id) {
                nodeFound = true;
              }
            });
            if (!nodeFound) {
              runningTable.fnDeleteRow(node);
              runningTable.fnDraw();
            }
          });

          $(data).each(function (iBundle, item) {
            var bundle = new Bundle(item);
            var foundRow = null;
            $(nNodes).each(function (iNode, node) {
              if ($(node).children("td").eq(6).text() == bundle.id) {
                foundRow = node;
              }
            });
            var killCell = "";
            var suspendCell = "";
            var resumeCell = "";
            if (bundle.canEdit) {
              killCell = '<a class="btn btn-mini btn-danger disable-feedback confirmationModal" ' +
                      'href="javascript:void(0)" ' +
                      'data-url="' + bundle.killUrl + '" ' +
                      'title="${ _('Kill') } ' + bundle.id + '"' +
                      'alt="${ _('Are you sure you want to kill bundle ')}' + bundle.id + '?" ' +
                      'data-message="${ _('The bundle was killed!') }" ' +
                      'data-confirmation-message="${ _('Are you sure you\'d like to kill this job?') }"' +
                      '>${ _('Kill') }</a>';
              suspendCell = '<a class="btn btn-mini confirmationModal" ' +
                      'href="javascript:void(0)" ' +
                      'data-url="' + bundle.suspendUrl + '" ' +
                      'title="${ _('Suspend') } ' + bundle.id + '"' +
                      'alt="${ _('Are you sure you want to suspend bundle ')}' + bundle.id + '?" ' +
                      'data-message="${ _('The bundle was suspended!') }" ' +
                      'data-confirmation-message="${ _('Are you sure you\'d like to suspend this job?') }"' +
                      '>${ _('Suspend') }</a>';
              resumeCell = '<a class="btn btn-mini confirmationModal" ' +
                      'href="javascript:void(0)" ' +
                      'data-url="' + bundle.resumeUrl + '" ' +
                      'title="${ _('Resume') } ' + bundle.id + '"' +
                      'alt="${ _('Are you sure you want to resume bundle ')}' + bundle.id + '?" ' +
                      'data-message="${ _('The bundle was resumed!') }" ' +
                      'data-confirmation-message="${ _('Are you sure you\'d like to resume this job?') }"' +
                      '>${ _('Resume') }</a>';
            }
            if (foundRow == null) {
              if (['RUNNING', 'PREP', 'WAITING', 'SUSPENDED', 'PREPSUSPENDED', 'PREPPAUSED', 'PAUSED', 'STARTED', 'FINISHING'].indexOf(bundle.status) > -1) {
                try {
                  runningTable.fnAddData([
                    emptyStringIfNull(bundle.kickoffTime),
                    '<span class="' + bundle.statusClass + '">' + bundle.status + '</span>',
                    bundle.appName,
                    '<div class="progress"><div class="bar bar-warning" style="width:1%"></div></div>',
                    bundle.user,
                    emptyStringIfNull(bundle.created),
                    '<a href="' + bundle.absoluteUrl + '" data-row-selector="true">' + bundle.id + '</a>',
                    killCell + " " + (['RUNNING', 'PREP', 'WAITING'].indexOf(bundle.status) > -1?suspendCell:resumeCell)
                  ]);
                }
                catch (error) {
                  $(document).trigger("error", error);
                }
              }

            }
            else {
              runningTable.fnUpdate('<span class="' + bundle.statusClass + '">' + bundle.status + '</span>', foundRow, 1, false);
              runningTable.fnUpdate(killCell + " " + (['RUNNING', 'PREP', 'WAITING'].indexOf(bundle.status) > -1?suspendCell:resumeCell), foundRow, 7, false);
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

        window.setTimeout(refreshRunning, 20000);
      });
    }

    function refreshCompleted() {
      $.getJSON(window.location.pathname + "?format=json&type=completed", function (data) {
        completedTable.fnClearTable();
        $(data).each(function (iWf, item) {
          var bundle = new Bundle(item);
          try {
            completedTable.fnAddData([
              emptyStringIfNull(bundle.kickoffTime),
              '<span class="' + bundle.statusClass + '">' + bundle.status + '</span>',
              bundle.appName,
              bundle.user,
              emptyStringIfNull(bundle.created),
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
        $(data).each(function (iWf, item) {
            var bundle = new Bundle(item);
            var foundRow = null;
            $(nNodes).each(function (iNode, node) {
              if ($(node).children("td").eq(6).text() == bundle.id) {
                foundRow = node;
              }
            });
            if (foundRow != null) {
              runningTable.fnUpdate('<span class="' + bundle.statusClass + '">' + bundle.status + '</span>', foundRow, 1, false);
              if (bundle.progress == 0){
                runningTable.fnUpdate('<div class="progress"><div class="bar bar-warning" style="width: 1%"></div></div>', foundRow, 3, false);
              }
              else {
                runningTable.fnUpdate('<div class="progress"><div class="' + bundle.progressClass + '" style="width:' + bundle.progress + '%">' + bundle.progress + '%</div></div>', foundRow, 3, false);
              }
            }
          });
        window.setTimeout(refreshProgress, 20000);
      });
    }

  });
</script>

${ commonfooter(messages) | n,unicode }

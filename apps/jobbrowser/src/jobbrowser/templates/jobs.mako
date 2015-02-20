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
<%
  from jobbrowser.views import get_state_link
  from django.template.defaultfilters import urlencode
  from desktop.views import commonheader, commonfooter
  from django.utils.translation import ugettext as _
%>
<%namespace name="actionbar" file="actionbar.mako" />
<%namespace name="components" file="jobbrowser_components.mako" />

${ commonheader(None, "jobbrowser", user) | n,unicode }
${ components.menubar() }

<link href="${ static('jobbrowser/css/jobbrowser.css') }" rel="stylesheet">

<div class="container-fluid">
  <div class="card card-small">

  <%actionbar:render>
    <%def name="search()">
      ${_('Username')} <input id="userFilter" type="text" class="input-medium search-query" placeholder="${_('Search for username')}" value="${ user_filter or '' }">
      &nbsp;&nbsp;${_('Text')} <input id="textFilter" type="text" class="input-xlarge search-query" placeholder="${_('Search for text')}" value="${ text_filter or '' }">
      <img id="loading" src="${ static('desktop/art/spinner.gif') }" />
    </%def>

    <%def name="creation()">
      % if not is_yarn:
      <label class="checkbox retired">
        <%
            checked = ""
            if retired == "on":
                checked = 'checked="checked"'
        %>
        <input id="showRetired" type="checkbox" ${checked}> ${_('Show retired jobs')}
      </label>
      % endif
      <span class="btn-group">
        <a class="btn btn-status btn-success" data-value="completed">${ _('Succeeded') }</a>
        <a class="btn btn-status btn-warning" data-value="running">${ _('Running') }</a>
        <a class="btn btn-status btn-danger disable-feedback" data-value="failed">${ _('Failed') }</a>
        <a class="btn btn-status btn-inverse disable-feedback" data-value="killed">${ _('Killed') }</a>
      </span>
    </%def>
  </%actionbar:render>

  <div id="noJobs" class="alert"><i class="fa fa-exclamation-triangle"></i>&nbsp; ${_('There are no jobs that match your search criteria.')}</div>

  <table id="jobsTable" class="datatables table table-condensed">
    <thead>
    <tr>
      <th>${_('Logs')}</th>
      <th>${_('ID')}</th>
      <th>${_('Name')}</th>
      <th>${_('Status')}</th>
      <th>${_('User')}</th>
      <th>${_('Maps')}</th>
      <th>${_('Reduces')}</th>
      <th>${_('Queue')}</th>
      <th>${_('Priority')}</th>
      <th>${_('Duration')}</th>
      <th>${_('Submitted')}</th>
      <th data-row-selector-exclude="true"></th>
    </tr>
    </thead>
    <tbody>
    </tbody>
  </table>
    </div>
</div>

<div id="killModal" class="modal hide fade">
  <div class="modal-header">
    <a href="#" class="close" data-dismiss="modal">&times;</a>
    <h3>${_('Confirm Kill')}</h3>
  </div>
  <div class="modal-body">
    <p>${_('Are you sure you want to kill this job?')}</p>
  </div>
  <div class="modal-footer">
    <a class="btn" data-dismiss="modal">${_('No')}</a>
    <a id="killJobBtn" class="btn btn-danger disable-feedback">${_('Yes')}</a>
  </div>
</div>

<script src="${ static('desktop/ext/js/datatables-paging-0.1.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('jobbrowser/js/utils.js') }" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript" charset="utf-8">

  $(document).ready(function () {

    var jobTable = $(".datatables").dataTable({
      "sPaginationType": "bootstrap",
      "iDisplayLength": 50,
      "bLengthChange": false,
      "bAutoWidth": false,
      "sDom": "<'row'r>t<'row-fluid'<'dt-pages'p><'dt-records'i>>",
      "aaSorting": [
        [10, "desc"]
      ],
      "bProcessing": true,
      "bDeferRender": true,
      "aoColumns": [
        {"bSortable": false, "sWidth": "20px"},
        {"sWidth": "10%"},
        null,
        {"sWidth": "5%"},
        {"sWidth": "5%"},
        { "sType": "title-numeric", "sWidth": "50px"},
        { "sType": "title-numeric", "sWidth": "50px"},
        {"sWidth": "5%"},
        {"sWidth": "4%"},
        { "sType": "title-numeric", "sWidth": "4%" },
        { "sType": "title-numeric", "sWidth": "12%" },
        {"bSortable": false, "sWidth": "20px"}
      ],
      "oLanguage": {
        "sEmptyTable": "${_('No data available')}",
        "sZeroRecords": "${_('No matching records')}"
      }
    });

    $(document).ajaxError(function (event, jqxhr, settings, exception) {
      if (jqxhr.status == 500) {
        window.clearInterval(_runningInterval);
        $(document).trigger("error", "${_('There was a problem communicating with the server: ')}" + $.parseJSON(jqxhr.responseText).message);
      }
    });

    function populateTable(data) {
      if (data != null) {
        jobTable.fnClearTable();
        $("#loading").addClass("hide");
        $("#noJobs").hide();
        $(".datatables").show();
        if (data.length == 0) {
          $("#noJobs").show();
          $(".datatables").hide();
        }
        else {
          var rows = [];
          $(data.jobs).each(function (cnt, job) {
            rows.push(getJobRow(job));
          });
          jobTable.fnAddData(rows);
          $("a[data-row-selector='true']").jHueRowSelector();
        }
      }
    }

    var isUpdating = false;
    var updateableRows = {};

    function updateRunning(data) {
      if (data != null && data.jobs != null && data.jobs.length > 0) {
        // Update finished jobs from updateableRows.
        // jobs missing from response are finished.
        $.each(updateableRows, function(job_id, job) {
          if ($.grep(data.jobs, function(new_job) {
            return new_job.shortId == job_id;
          }).length == 0 ) {
            callJobDetails(job, true);
            delete updateableRows[job_id];
          }
        });

        // Find new jobs and running jobs.
        // Update updateableRows.
        for(var i = 0; i < data.jobs.length; ++i) {
          var job = data.jobs[i];
          if (Utils.RUNNING_ARRAY.indexOf(job.status.toUpperCase()) > -1) {
            updateableRows[job.shortId] = job;

            var nNodes = jobTable.fnGetNodes();
            var foundRow = null;
            $.each(nNodes, function (iNode, node) {
              if ($(node).children("td").eq(1).text().trim() == job.shortId) {
                foundRow = node;
              }
            });
            if (foundRow == null) {
              try {
                jobTable.fnAddData(getJobRow(job));
                if ($("#noJobs").is(":visible")) {
                  $("#noJobs").hide();
                  $(".datatables").show();
                }
                $("a[data-row-selector='true']").jHueRowSelector();
              } catch (error) {
                $(document).trigger("error", error);
              }
            } else {
              updateJobRow(job, foundRow);
            }
          }
        }
      } else {
        // Update finished jobs from updateableRows.
        // all jobs have finished if hit this clause.
        $.each(updateableRows, function(job_id, job) {
          callJobDetails(job, true);
          delete updateableRows[job_id];
        });
      }
      isUpdating = false;
    }

    function getJobRow(job) {
      var _killCell = "";
      if (job.canKill) {
        _killCell = '<a class="btn btn-small btn-inverse kill" ' +
                'href="javascript:void(0)" ' +
                'data-url="' + job.url + '" ' +
                'data-killUrl="' + job.killUrl + '" ' +
                'data-shortid="' + job.shortId + '" ' +
                'title="${ _('Kill this job') }" ' +
                '>${ _('Kill') }</a>';
      }
      return [
        '<a href="' + emptyStringIfNull(job.logs) + '" data-row-selector-exclude="true"><i class="fa fa-tasks"></i></a>',
        '<a href="' + emptyStringIfNull(job.url) + '" title="${_('View this job')}" data-row-selector="true">' + emptyStringIfNull(job.shortId) + '</a>',
        emptyStringIfNull(job.name),
        '<span class="label ' + getStatusClass(job.status) + '">' + (job.isRetired && !job.isMR2 ? '<i class="fa fa-briefcase fa fa-white" title="${ _('Retired') }"></i> ' : '') + job.status + '</span>',
        emptyStringIfNull(job.user),
        '<span title="' + emptyStringIfNull(job.mapsPercentComplete) + '">' + (job.isRetired ? '${_('N/A')}' : '<div class="progress" title="' + (job.isMR2 ? job.mapsPercentComplete : job.finishedMaps + '/' + job.desiredMaps) + '"><div class="bar-label">' + job.mapsPercentComplete + '%</div><div class="' + 'bar ' + getStatusClass(job.status, "bar-") + '" style="margin-top:-20px;width:' + job.mapsPercentComplete + '%"></div></div>') + '</span>',
        '<span title="' + emptyStringIfNull(job.reducesPercentComplete) + '">' + (job.isRetired ? '${_('N/A')}' : '<div class="progress" title="' + (job.isMR2 ? job.reducesPercentComplete : job.finishedReduces + '/' + job.desiredReduces) + '"><div class="bar-label">' + job.reducesPercentComplete + '%</div><div class="' + 'bar ' + getStatusClass(job.status, "bar-") + '" style="margin-top:-20px;width:' + job.reducesPercentComplete + '%"></div></div>') + '</span>',
        emptyStringIfNull(job.queueName),
        emptyStringIfNull(job.priority),
        '<span title="' + emptyStringIfNull(job.durationMs) + '">' + (job.isRetired ? '${_('N/A')}' : emptyStringIfNull(job.durationFormatted)) + '</span>',
        '<span title="' + emptyStringIfNull(job.startTimeMs) + '">' + emptyStringIfNull(job.startTimeFormatted) + '</span>',
        _killCell
      ]
    }

    function updateJobRow(job, row, finish) {
      var mapsPercentComplete = (finish) ? 100 : job.mapsPercentComplete;
      var reducesPercentComplete = (finish) ? 100 : job.reducesPercentComplete;
      jobTable.fnUpdate('<span class="label ' + getStatusClass(job.status) + '">' + job.status + '</span>', row, 3, false);
      jobTable.fnUpdate('<span title="' + emptyStringIfNull(mapsPercentComplete) + '"><div class="progress" title="' + (job.isMR2 ? mapsPercentComplete : job.finishedMaps + '/' + job.desiredMaps) + '"><div class="bar-label">' + mapsPercentComplete + '%</div><div class="' + 'bar ' + getStatusClass(job.status, "bar-") + '" style="margin-top:-20px;width:' + mapsPercentComplete + '%"></div></div></span>', row, 5, false);
      jobTable.fnUpdate('<span title="' + emptyStringIfNull(reducesPercentComplete) + '"><div class="progress" title="' + (job.isMR2 ? reducesPercentComplete : job.finishedReduces + '/' + job.desiredReduces) + '"><div class="bar-label">' + reducesPercentComplete + '%</div><div class="' + 'bar ' + getStatusClass(job.status, "bar-") + '" style="margin-top:-20px;width:' + reducesPercentComplete + '%"></div></div></span>', row, 6, false);
      jobTable.fnUpdate('<span title="' + emptyStringIfNull(job.durationMs) + '">' + emptyStringIfNull(job.durationFormatted) + '</span>', row, 9, false);
      var _killCell = "";
      if (job.canKill) {
        _killCell = '<a class="btn btn-small btn-inverse kill" ' +
                'href="javascript:void(0)" ' +
                'data-url="' + job.url + '" ' +
                'data-killurl="' + job.killUrl + '" ' +
                'data-shortid="' + job.shortId + '" ' +
                'title="${ _('Kill this job') }" ' +
                '>${ _('Kill') }</a>';
      }
      jobTable.fnUpdate(_killCell, row, 11, false);
    }

    function callJobDetails(job, finish) {
      $.getJSON(job.url + "?format=json", function (data) {
        if (data != null && data.job) {
          var jobTableNodes = jobTable.fnGetNodes();
          var _foundRow = null;
          $(jobTableNodes).each(function (iNode, node) {
            if ($(node).children("td").eq(1).text().trim() == data.job.shortId) {
              _foundRow = node;
            }
          });
          if (_foundRow != null) {
            updateJobRow(data.job, _foundRow, finish);
          }
        }
      });
    }

    function callJsonData(callback, justRunning) {
      var _url = "?format=json";

      if (justRunning == undefined) {
        if ($(".btn-status.active").length > 0) {
          _url += "&state=" + $(".btn-status.active").data("value");
        }
        else {
          _url += "&state=all";
        }
      }
      else {
        isUpdating = true;
        if ($(".btn-status.active").length > 0) {
          _url += "&state=" + $(".btn-status.active").data("value");
        }
        else {
          _url += "&state=running";
        }
      }

      _url += "&user=" + $("#userFilter").val().trim();

      if ($("#textFilter").val().trim() != "") {
        _url += "&text=" + $("#textFilter").val().trim();
      }

      if ($("#showRetired").is(":checked")) {
        _url += "&retired=on";
      }

      $.getJSON(_url, callback);
    }

    $(".search-query").jHueDelayedInput(function(){
      $("#loading").removeClass("hide");
      callJsonData(populateTable);
    });

    $("#showRetired").change(function () {
      $("#loading").removeClass("hide");
      callJsonData(populateTable);
    });

    $(".btn-status").on("click", function () {
      $(".btn-status").not($(this)).removeClass("active");
      $(this).toggleClass("active");
      $("#loading").removeClass("hide");
      callJsonData(populateTable);
    });


    $(document).on("click", ".kill", function (e) {
      var _this = $(this);
      $("#killJobBtn").data("url", _this.data("url"));
      $("#killJobBtn").data("killurl", _this.data("killurl"));
      $("#killModal").modal({
        keyboard: true,
        show: true
      });
    });

    $("#killJobBtn").on("click", function () {
      var _this = $(this);
      _this.attr("data-loading-text", _this.text() + " ...");
      _this.button("loading");
      $.post(_this.data("killurl"), {
          "format": "json"
        },
        function (response) {
          _this.button("reset");
          $("#killModal").modal("hide");
          if (response.status != 0) {
            $(document).trigger("error", "${ _('There was a problem killing this job.') }");
          }
          else {
            callJobDetails({ url: _this.data("url")});
          }
        }
      );
    });

    // init job list
    var _initialState = getQueryStringParameter("state");
    if (_initialState != "") {
      $(".btn-status[data-value='" + _initialState + "']").addClass("active");
    }
    callJsonData(populateTable);

    var _runningInterval = window.setInterval(function () {
      if (! isUpdating) {
        callJsonData(updateRunning, true);
      }
    }, 2000);

    $("a[data-row-selector='true']").jHueRowSelector();
  });
</script>

${ commonfooter(messages) | n,unicode }

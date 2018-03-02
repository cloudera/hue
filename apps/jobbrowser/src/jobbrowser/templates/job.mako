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

<%namespace name="comps" file="jobbrowser_components.mako" />

<%!
  import os
  from hadoop.fs.exceptions import WebHdfsException
  from jobbrowser.views import format_counter_name
  from desktop.lib.view_util import location_to_url
  from desktop.views import commonheader, commonfooter
  from django.template.defaultfilters import urlencode
  from django.utils.translation import ugettext as _
%>
<%def name="task_table(dom_id, tasks)">
    <table id="${ dom_id }" class="taskTable table table-condensed">
        <thead>
        <tr>
            <th>${_('Logs')}</th>
            <th>${_('Tasks')}</th>
            <th>${_('Type')}</th>
        </tr>
        </thead>
        <tbody>
            % for task in tasks:
            <tr>
                <td data-row-selector-exclude="true">
                %if task.taskAttemptIds:
                    <a href="${ url('single_task_attempt_logs', job=task.jobId, taskid=task.taskId, attemptid=task.taskAttemptIds[-1]) }"
                        data-row-selector="true"><i class="fa fa-tasks"></i>
                    </a>
                %endif
                </td>
                <td>
                    <a title="${_('View this task')}" href="${ url('jobbrowser.views.single_task', job=job.jobId, taskid=task.taskId) }"
                        data-row-selector-exclude="true">${task.taskId_short}
                    </a>
                </td>
                <td>${task.taskType}</td>
            </tr>
            % endfor
        </tbody>
    </table>
</%def>

<%def name="rows_for_conf_vars(rows)">
    %  for k, v in sorted(rows.iteritems()):
        <tr>
            <td>${k}</td>
        <%
            splitArray = v.split(",")
        %>
        <td>
            % for i, val in enumerate(splitArray):
            <%
                url_splitted = request.fs.urlsplit(val)
                is_hdfs_uri = bool(url_splitted[1])
            %>
            % if is_hdfs_uri:
                <a href="${location_to_url(val)}" title="${val}">${val}</a>
                % if i != len(splitArray) - 1:
                  <br>
                % endif
            % else:
                ${val}
            % endif
            % endfor
        </td>
        </tr>
    % endfor
</%def>

${ commonheader(_('Job: %(jobId)s') % dict(jobId=job.jobId_short), "jobbrowser", user, request) | n,unicode }
${ comps.menubar() }

<link href="${ static('jobbrowser/css/jobbrowser.css') }" rel="stylesheet">

<style type="text/css">
  .killJob {
    display: none;
  }
  %if not failed_tasks:
    #failedTasksContainer {
      display: none;
    }
  %endif
</style>

% if job.applicationType == 'SPARK':

<div class="container-fluid">
  <div class="row-fluid">
    <div class="span2">
      <div class="sidebar-nav" style="padding-top: 0">
        <ul class="nav nav-list">
          <li class="nav-header">${_('App ID')}</li>
          <li class="white truncate-text" title="${job.jobId_short}">${job.jobId_short}</li>
          <li class="nav-header">${_('Type')}</li>
          <li class="white truncate-text" title="${job.applicationType}">${job.applicationType}</li>
          <li class="nav-header">${_('User')}</li>
          <li class="white">${job.user}</li>
          <li class="nav-header">${_('Status')}</li>
          <li class="white" id="jobStatus">&nbsp;</li>
          % if job.logs_url:
          <li class="nav-header">${_('Logs')}</li>
          <li><a href="${job.logs_url }" target="_blank"><i class="fa fa-tasks"></i> ${_('Logs')}</a></li>
          % endif
          <li class="nav-header">${_('Progress')}</li>
          <li class="white">${job.progress}%</li>
          <li class="nav-header">${_('Duration')}</li>
          <li class="white">${job.durationFormatted}</li>
          <li class="nav-header killJob">${_('Actions')}</li>
          <li id="killJobContainer" class="white killJob"></li>
        </ul>
      </div>
    </div>
    <div class="span10">
      <div class="card card-small">
        <h1 class="card-heading simple">${_(job.name)}</h1>
        <div class="card-body">
          <ul class="nav nav-tabs">
            <li  class="active"><a href="#metadata" data-toggle="tab">${_('Metadata')}</a></li>
            % if hasattr(job, 'metrics') and job.metrics:
              <li><a href="#metrics" data-toggle="tab">${_('Metrics')}</a></li>
            % endif
          </ul>
          <div class="tab-content">
            <div class="tab-pane active" id="metadata">
              <table class="table table-condensed">
                <thead>
                  <th>${_('Name')}</th>
                  <th>${_('Value')}</th>
                </thead>
                <tbody>
                  <tr>
                    <td>${_('Jobs')}</td>
                    <td><a href="${job.trackingUrl}">${job.trackingUrl}</a></td>
                  </tr>
                  % if hasattr(job, 'amHostHttpAddress'):
                  <tr>
                    <td>${_('Host')}</td>
                    <td><a href="http://${job.amHostHttpAddress}">http://${job.amHostHttpAddress}</a></td>
                  </tr>
                  % endif
                  <tr>
                    <td>${_('Queue Name')}</td>
                    <td>${job.queueName}</td>
                  </tr>
                  <tr>
                    <td>${_('Started')}</td>
                    <td>${job.startTimeFormatted}</td>
                  </tr>
                  <tr>
                    <td>${_('Finished')}</td>
                    <td>${job.finishTimeFormatted}</td>
                  </tr>
                  <tr>
                    <td>${_('Pre-empted Resource VCores')}</td>
                    <td>${job.preemptedResourceVCores}</td>
                  </tr>
                  <tr>
                    <td>${_('VCore seconds')}</td>
                    <td>${job.vcoreSeconds}</td>
                  </tr>
                  <tr>
                    <td>${_('Memory seconds')}</td>
                    <td>${job.memorySeconds}</td>
                  </tr>
                  <tr>
                    <td>${_('Diagnostics')}</td>
                    <td>${job.diagnostics}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            % if hasattr(job, 'metrics') and job.metrics:
            <div class="tab-pane" id="metrics">
              <table class="table table-condensed">
                <thead>
                  % for header in job.metrics.get('headers', []):
                  <th>${ header }</th>
                  % endfor
                </thead>
                <tbody>
                % for executor in job.metrics.get('executors', []):
                  <tr>
                    % for val in executor:
                    % if isinstance(val, dict):
                      <td>
                      % for name, link in val.items():
                        <a href="${ link }">${ name }</a>
                      % endfor
                      </td>
                    % else:
                      <td>${ val }</td>
                    % endif
                    % endfor
                  </tr>
                % endfor
                </tbody>
              </table>
            </div>
            % endif
        </div>
      </div>
    </div>
  </div>
</div>

% elif job.applicationType == 'MR2':

<div class="container-fluid">
  <div class="row-fluid">
    <div class="span2">
      <div class="sidebar-nav" style="padding-top: 0">
        <ul class="nav nav-list">
          <li class="nav-header">${_('Job ID')}</li>
          <li class="white truncate-text" title="${job.jobId_short}">${job.jobId_short}</li>
          <li class="nav-header">${_('Type')}</li>
          <li class="white truncate-text" title="${job.applicationType or 'MR2'}">${job.applicationType or 'MR2'}</li>
          <li class="nav-header">${_('User')}</li>
          <li class="white">${job.user}</li>
          % if job.conf_keys is not None and 'hive.server2.proxy.user' in job.conf_keys:
          <li class="nav-header">${_('Proxy User')}</li>
          <li class="white">${job.conf_keys['hive.server2.proxy.user']}</li>
          % endif
          <li class="nav-header">${_('Status')}</li>
          <li class="white" id="jobStatus">&nbsp;</li>
          <li class="nav-header">${_('Logs')}</li>
          <li><a href="${ url('jobbrowser.views.job_single_logs', job=job.jobId) }"><i class="fa fa-tasks"></i> ${_('Logs')}</a></li>
          % if not job.is_retired:
          <li class="nav-header">${_('Maps')}</li>
          <li class="white" id="jobMaps">&nbsp;</li>
          <li class="nav-header">${_('Reduces')}</li>
          <li class="white" id="jobReduces">&nbsp;</li>
          % endif
          <li class="nav-header">${_('Duration')}</li>
          <li class="white" id="jobDuration">&nbsp;</li>
          <%
              output_dir = job.conf_keys.get('mapredOutputDir', "")
              location_url = location_to_url(output_dir)
              basename = os.path.basename(output_dir)
              dir_name = basename.split('/')[-1]
          %>
          % if dir_name != '':
          <li class="nav-header">${_('Output')}</li>
          <li class="white">
            % if location_url != None:
            <a href="${location_url}" title="${output_dir}">
            % endif
            <i class="fa fa-folder-open"></i> ${dir_name}
            % if location_url != None:
            </a>
            % endif
          </li>
          % endif
          <li class="nav-header killJob">${_('Actions')}</li>
          <li id="killJobContainer" class="white killJob"></li>
        </ul>
      </div>
    </div>
    <div class="span10">
      <div class="card card-small">
          % if hasattr(job, 'name'):
            <h1 class="card-heading simple">${_(job.name)}</h1>
          % else:
	          <h1 class="card-heading simple">${_('Job: %(jobId)s') % dict(jobId=job.jobId_short)}</h1>
          % endif
          <div class="card-body">
            <p>

              <ul class="nav nav-tabs">
                % if job.is_mr2:
                <li class="active"><a href="#attempts" data-toggle="tab">${_('Attempts')}</a></li>
                <li><a href="#tasks" data-toggle="tab">${_('Tasks')}</a></li>
                % else:
                <li class="active"><a href="#tasks" data-toggle="tab">${_('Tasks')}</a></li>
                % endif
                <li><a href="#metadata" data-toggle="tab">${_('Metadata')}</a></li>
                % if not job.is_retired:
                <li><a href="#counters" data-toggle="tab">${_('Counters')}</a></li>
                % endif
              </ul>

              <div class="tab-content">
                % if job.is_mr2:
                <div class="tab-pane active" id="attempts">
                  <table id="jobAttemptTable" class="table table-condensed">
                    <thead>
                      <th width="20">${_('Logs')}</th>
                      <th width="30">${_('Id')}</th>
                      <th>${_('Container')}</th>
                    </thead>
                    <tbody>
                      % for attempt in job.job_attempts['jobAttempt']:
                      <tr>
                        <td>
                          <a href="${ url('job_attempt_logs', job=job.jobId, attempt_index=loop.index) }" data-row-selector="true">
                            <i class="fa fa-tasks"></i>
                          </a>
                        </td>
                        <td>${ attempt['id'] }</td>
                        <td>${ comps.get_container_link(job.status, attempt['nodeHttpAddress'], attempt['containerId']) }</td>
                      </tr>
                      % endfor
                    </tbody>
                  </table>
                </div>
                <div class="tab-pane" id="tasks">
                % else:
                <div class="tab-pane active" id="tasks">
                % endif
                % if job.is_retired:
                  ${ _('This jobs is ')} <span class="label label-warning">${ _('retired') }</span> ${ _(' and so has little information available.') }
                  <br/>
                  <br/>
                % else:
                  <div id="failedTasksContainer">
                    <a style="float:right;margin-right:10px;margin-top: 10px" href="${url('jobbrowser.views.tasks', job=job.jobId)}?taskstate=failed">${_('View All Failed Tasks')} &raquo;</a>
                    <h3>${_('Failed Tasks')}</h3>
                    <div>
                      ${task_table('failedTasks', failed_tasks)}
                    </div>
                  </div>
                  <div>
                  <a style="float:right;margin-right:10px;margin-top: 10px" href="${url('jobbrowser.views.tasks', job=job.jobId)}">${_('View All Tasks')} &raquo;</a>
                  <h3>${_('Recent Tasks')}</h3>
                  <div>
                    ${task_table('recentTasks', recent_tasks)}
                  </div>
                </div>
                % endif
              </div>
              <div id="metadata" class="tab-pane">
                <form class="form-search">
                  <input type="text" id="metadataFilter" class="input-xlarge search-query" placeholder="${_('Text Filter')}">
                </form>
                <table id="metadataTable" class="table table-condensed">
                  <thead>
                    <th>${_('Name')}</th>
                    <th>${_('Value')}</th>
                  </thead>
                  <tbody>
                    <tr>
                      <td>${_('ID')}</td>
                      <td>${job.jobId_short}</td>
                    </tr>
                    <tr>
                      <td>${_('User')}</td>
                      <td>${job.user}</td>
                    </tr>
                    % if not job.is_retired:
                    <tr>
                      <td>${_('Maps')}</td>
                      <td>${job.finishedMaps} of ${job.desiredMaps}</td>
                    </tr>
                    <tr>
                      <td>${_('Reduces')}</td>
                      <td>${job.finishedReduces} of ${job.desiredReduces}</td>
                    </tr>
                    % endif
                    <tr>
                      <td>${_('Started')}</td>
                      <td>${job.startTimeFormatted}</td>
                    </tr>
                    % if not job.is_retired:
                    <tr>
                      <td>${_('Ended')}</td>
                      <td>${job.finishTimeFormatted}</td>
                    </tr>
                    <tr>
                      <td>${_('Duration')}</td>
                      <td>${job.duration}</td>
                    </tr>
                    % endif
                    <tr>
                      <td>${_('Status')}</td>
                      <td>${job.status}</td>
                    </tr>
                    ${rows_for_conf_vars(job.conf_keys)}
                  </tbody>
                </table>
                <h3>${_('Raw configuration:')}</h3>
                <table id="rawConfigurationTable" class="table table-condensed">
                  <thead>
                    <th>${_('Name')}</th>
                    <th>${_('Value')}</th>
                  </thead>
                  <tbody>
                  % if job.is_mr2:
                    % for line in job.full_job_conf['property']:
                    <tr>
                      <td width="20%">${ line['name'] }</td>
                      <td>
                        <div class="wordbreak">
                          ${ line['value'] }
                        </div>
                      </td>
                    </tr>
                    % endfor
                  % else:
                    % for key, value in sorted(job.full_job_conf.items()):
                    <tr>
                      <td width="20%">${key}</td>
                      <td>
                        <div class="wordbreak">
                          ${value}
                        </div>
                      </td>
                    </tr>
                    % endfor
                  % endif
                  </tbody>
                </table>
              </div>
              <div id="counters" class="tab-pane">
                % if job.is_mr2:
                ${ comps.job_counters_mr2(job.counters) }
                % else:
                ${ comps.job_counters(job.counters) }
                % endif
              </div>
            </div>
          </div>
        </p>
      </div>
    </div>
  </div>
</div>

% else:

<div class="container-fluid">
  <div class="row-fluid">
    <div class="span2">
      <div class="sidebar-nav" style="padding-top: 0">
        <ul class="nav nav-list">
          <li class="nav-header">${_('App ID')}</li>
          <li class="white truncate-text" title="${job.jobId_short}">${job.jobId_short}</li>
          <li class="nav-header">${_('Type')}</li>
          <li class="white truncate-text" title="${job.applicationType}">${job.applicationType}</li>
          <li class="nav-header">${_('User')}</li>
          <li class="white">${job.user}</li>
          <li class="nav-header">${_('Status')}</li>
          <li class="white" id="jobStatus">&nbsp;</li>

          % if job.trackingUrl:
            <li class="nav-header">${_('Tracking URL')}</li>
            <li><a href="${job.trackingUrl }" target="_blank"><i class="fa fa-tasks"></i> ${_('Tracking URL')}</a></li>
          % endif

          <li class="nav-header">${_('Progress')}</li>
          <li class="white">${job.progress}%</li>
          <li class="nav-header">${_('Duration')}</li>
          <li class="white">${job.durationFormatted}</li>
          <li class="nav-header killJob">${_('Actions')}</li>
          <li id="killJobContainer" class="white killJob"></li>
        </ul>
      </div>
    </div>
    <div class="span10">
      <div class="card card-small">
        <h1 class="card-heading simple">${_(job.name)}</h1>
        <div class="card-body">
          <ul class="nav nav-tabs">
            <li class="active"><a href="#metadata" data-toggle="tab">${_('Metadata')}</a></li>
          </ul>
          <div class="tab-content">
            <div class="tab-pane active" id="metadata">
              <table class="table table-condensed">
                <thead>
                  <th>${_('Name')}</th>
                  <th>${_('Value')}</th>
                </thead>
                <tbody>

                  % if job.trackingUrl:
                  <tr>
                    <td>${_('Jobs')}</td>
                    <td><a href="${job.trackingUrl}">${job.trackingUrl}</a></td>
                  </tr>
                  % endif

                  % if hasattr(job, 'amHostHttpAddress'):
                  <tr>
                    <td>${_('Host')}</td>
                    <td><a href="http://${job.amHostHttpAddress}">http://${job.amHostHttpAddress}</a></td>
                  </tr>
                  %endif

                  <tr>
                    <td>${_('Queue Name')}</td>
                    <td>${job.queueName}</td>
                  </tr>
                  <tr>
                    <td>${_('Started')}</td>
                    <td>${job.startTimeFormatted}</td>
                  </tr>
                  <tr>
                    <td>${_('Finished')}</td>
                    <td>${job.finishTimeFormatted}</td>
                  </tr>
                  <tr>
                    <td>${_('Pre-empted Resource VCores')}</td>
                    <td>${job.preemptedResourceVCores}</td>
                  </tr>
                  <tr>
                    <td>${_('VCore seconds')}</td>
                    <td>${job.vcoreSeconds}</td>
                  </tr>
                  <tr>
                    <td>${_('Memory seconds')}</td>
                    <td>${job.memorySeconds}</td>
                  </tr>
                  <tr>
                    <td>${_('Diagnostics')}</td>
                    <td>${job.diagnostics}</td>
                  </tr>
                </tbody>
              </table>
            </div>
        </div>
      </div>
    </div>
  </div>
</div>

% endif


<div id="killModal" class="modal hide fade">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
    <h2 class="modal-title">${_('Confirm Kill')}</h2>
  </div>
  <div class="modal-body">
    <p>${_('Are you sure you want to kill this job?')}</p>
  </div>
  <div class="modal-footer">
    <a class="btn" data-dismiss="modal">${_('No')}</a>
    <a id="killJobBtn" class="btn btn-danger disable-feedback">${_('Yes')}</a>
  </div>
</div>

<script src="${ static('jobbrowser/js/utils.js') }" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript">
$(document).ready(function () {
  $(".taskTable").dataTable({
    "bPaginate": false,
    "bLengthChange": false,
    "bInfo": false,
    "bAutoWidth": false,
    "aoColumns": [
      { "sWidth": "1%", "bSortable": false },
      { "sWidth": "50%" },
      { "sWidth": "49%" }
    ],
    "aaSorting": [
      [ 1, "asc" ]
    ],
    "oLanguage": {
      "sEmptyTable": "${_('No data available')}",
      "sZeroRecords": "${_('No matching records')}"
    }
  });

  $("#metadataFilter").jHueDelayedInput(function(){
    $("#metadataTable tbody tr").removeClass("hide");
    $("#metadataTable tbody tr").each(function () {
      if ($(this).text().toLowerCase().indexOf($("#metadataFilter").val().toLowerCase()) == -1) {
        $(this).addClass("hide");
      }
    });
    $("#rawConfigurationTable tbody tr").removeClass("hide");
    $("#rawConfigurationTable tbody tr").each(function () {
      if ($(this).text().toLowerCase().indexOf($("#metadataFilter").val().toLowerCase()) == -1) {
        $(this).addClass("hide");
      }
    });
  });

  $(".jobCountersTable").dataTable({
    "bPaginate": false,
    "bLengthChange": false,
    "bInfo": false,
    "bAutoWidth": false,
    "aoColumns": [
      { "sWidth": "40%" },
      { "sWidth": "20%" },
      { "sWidth": "20%" },
      { "sWidth": "20%" }
    ],
    "oLanguage": {
      "sEmptyTable": "${_('No data available')}",
      "sZeroRecords": "${_('No matching records')}"
    }
  });

  $(".dataTables_wrapper").css("min-height", "0");
  $(".dataTables_filter").hide();

  $(document).ajaxError(function (event, jqxhr, settings, exception) {
    if (jqxhr.status == 500) {
      window.clearInterval(_runningInterval);
      $(document).trigger("error", "${_('There was a problem communicating with the server. Refresh the page.')}");
    }
  });

  var isUpdating = true;

  function callJobDetails() {
    isUpdating = true;
    $.getJSON("?format=json", function (data) {
      if (data != null && data.job != null) {
        updateJob(data.job);
        if (data.applicationType != 'SPARK') {
          updateFailedTasks(data.failedTasks);
          updateRecentTasks(data.recentTasks);
        }
      }
      isUpdating = false;
    });
  }

  function updateJob(job) {
    var killCell = "";
    if (job.canKill) {
      killCell = '<button class="btn kill" ' +
              'href="javascript:void(0)" ' +
              'data-url="' + job.url + '" ' +
              'data-killurl="' + job.killUrl + '" ' +
              'data-shortid="' + job.shortId + '" ' +
              'title="${ _('Kill this job') }" ' +
              '>${ _('Kill this job') }</button>';
      $(".killJob").show();
    }
    else {
      $(".killJob").hide();
    }
    $("#killJobContainer").html(killCell);
    $("#jobStatus").html('<span class="label ' + getStatusClass(job.status) + '">' + (job.isRetired && !job.isMR2 ? '<i class="fa fa-briefcase fa fa-white" title="${ _('Retired') }"></i> ' : '') + job.status + '</span>');
    var _title = "";
    if (job.desiredMaps > 0) {
      $("#jobMaps").html((job.isRetired ? '${_('N/A')}' : '<div class="progress" style="width:100px" title="' + (job.finishedMaps + '/' + job.desiredMaps) + '"><div class="bar-label">' + job.mapsPercentComplete + '%</div><div class="' + 'bar ' + getStatusClass(job.status, "bar-") + '" style="margin-top:-20px;width:' + job.mapsPercentComplete + '%"></div></div>'));
      _title += "M " + job.mapsPercentComplete + "%";
    }
    else {
      $("#jobMaps").html('${_('0/0')}');
    }
    if (job.desiredReduces > 0) {
      $("#jobReduces").html((job.isRetired ? '${_('N/A')}' : '<div class="progress" style="width:100px" title="' + (job.finishedReduces + '/' + job.desiredReduces) + '"><div class="bar-label">' + job.reducesPercentComplete + '%</div><div class="' + 'bar ' + getStatusClass(job.status, "bar-") + '" style="margin-top:-20px;width:' + job.reducesPercentComplete + '%"></div></div>'));
      _title += " R " + job.reducesPercentComplete + "%";;
    }
    else {
      $("#jobReduces").html('${_('0/0')}');
    }
    if (_title != ""){
      $.jHueTitleUpdater.set(_title);
    }
    $("#jobDuration").html('<span title="' + emptyStringIfNull(job.durationMs) + '">' + (job.isRetired || ! job.durationFormatted ? '${_('N/A')}' : emptyStringIfNull(job.durationFormatted)) + '</span>');

    if (Utils.RUNNING_ARRAY.indexOf(job.status.toUpperCase()) == -1) {
      window.clearInterval(_runningInterval);
      removeFailedTasksFromRecent();
      $.jHueTitleUpdater.reset();
    }
  }

  function updateFailedTasks(tasks) {
    if (tasks != null && tasks.length > 0 && $("#failedTasks").length > 0) {
      $("#failedTasksContainer").show();
      var _failedTasksTableNodes = $("#failedTasks").dataTable().fnGetNodes();
      $(tasks).each(function (cnt, task) {
        var _foundRow = null;
        $(_failedTasksTableNodes).each(function (iNode, node) {
          if ($(node).children("td").eq(1).text().trim() == task.shortId) {
            _foundRow = node;
          }
        });
        if (_foundRow == null) {
          $("#failedTasks").dataTable().fnAddData(getTaskRow(task));
        }
      });
    }
  }

  function updateRecentTasks(tasks) {
    if (tasks != null && tasks.length > 0 && $("#recentTasks").length > 0) {
      var _recentTasksTableNodes = $("#recentTasks").dataTable().fnGetNodes();
      $(tasks).each(function (cnt, task) {
        var _foundRow = null;
        $(_recentTasksTableNodes).each(function (iNode, node) {
          if ($(node).children("td").eq(1).text().trim() == task.shortId) {
            _foundRow = node;
          }
        });
        if (_foundRow == null) {
          $("#recentTasks").dataTable().fnAddData(getTaskRow(task));
        }
      });
    }
  }

  function removeFailedTasksFromRecent() {
    var _failedTasksTableNodes = $("#failedTasks").dataTable().fnGetNodes();
    var _recentTasksTableNodes = $("#recentTasks").dataTable().fnGetNodes();
    $(_failedTasksTableNodes).each(function (fCnt, fNode) {
      $(_recentTasksTableNodes).each(function (rCnt, rNode) {
        if ($(rNode).children("td").eq(1).text().trim() == $(fNode).children("td").eq(1).text().trim()) {
          $("#recentTasks").dataTable().fnDeleteRow(rCnt);
        }
      });
    });
  }

  function getTaskRow(task) {
    return [
      '<a href="' + emptyStringIfNull(task.logs) + '" data-row-selector-exclude="true"><i class="fa fa-tasks"></i></a>',
      '<a href="' + emptyStringIfNull(task.url) + '" title="${_('View this task')}" data-row-selector="true">' + emptyStringIfNull(task.shortId) + '</a>',
      emptyStringIfNull(task.type)
    ]
  }

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

  callJobDetails();

  var _runningInterval = window.setInterval(function () {
    if (!isUpdating){
      callJobDetails();
    }
  }, 2000);

  $("a[data-row-selector='true']").jHueRowSelector();
});
</script>

${ commonfooter(request, messages) | n,unicode }

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
<%namespace name="comps" file="jobbrowser_components.mako" />

${ commonheader(_('Task Attempt: %(attemptId)s') % dict(attemptId=attempt.attemptId_short), "jobbrowser", user, request) | n,unicode }
${ comps.menubar() }

<div class="container-fluid">
  <div class="row-fluid">
    <div class="span2">
      <div class="sidebar-nav" style="padding-top: 0">
        <ul class="nav nav-list">
          <li class="nav-header">${_('Attempt ID')}</li>
          <li class="white truncate-texts" title="${attempt.attemptId_short}">${attempt.attemptId_short}</li>
          <li class="nav-header">${_('Task')}</li>
          <li><a href="${url('jobbrowser.views.single_task', job=joblnk.jobId, taskid=taskid)}" class="truncate-text" title="${task.taskId_short}">${task.taskId_short}</a>
          </li>
          <li class="nav-header">${_('Job')}</li>
          <li><a href="${url('jobbrowser.views.single_job', job=joblnk.jobId)}" class="truncate-text" title="${joblnk.jobId_short}">${joblnk.jobId_short}</a></li>
          <li class="nav-header">${_('Status')}</li>
          <li class="white">
              <%
                  status = attempt.state.lower()
              %>
              % if status == 'running' or status == 'pending':
                      <span class="label label-warning">${status}</span>
              % elif status == 'succeeded':
                      <span class="label label-success">${status}</span>
              % else:
                      <span class="label">${status}</span>
              % endif
          </li>
        </ul>
      </div>
    </div>

    <div class="span10">
      <div class="card card-small">
        <h1 class="card-heading simple">${_('Task Attempt: %(attemptId)s') % dict(attemptId=attempt.attemptId_short)}</h1>
        <div class="card-body">
          <p>
            <ul class="nav nav-tabs">
              <li><a href="${ url('single_task_attempt', job=joblnk.jobId, taskid=task.taskId, attemptid=attempt.attemptId) }#tmetadata">${_('Metadata')}</a></li>
              <li><a href="${ url('single_task_attempt', job=joblnk.jobId, taskid=task.taskId, attemptid=attempt.attemptId) }#tcounters">${_('Counters')}</a></li>
              <li class="active"><a href="#logs" data-toggle="tab">${_('Logs')}</a></li>
            </ul>
            <div class="tab-content">
              <div class="tab-pane active" id="logs">
              <%def name="format_log(raw)">
                ## have to remove any indentation here or it breaks inside the pre tags
                % for line in raw.split('\n'):
  ${ line | unicode,trim }
                % endfor
              </%def>
              <%
                  log_diagnostic = logs[0]
                  log_stdout = logs[1]
                  log_stderr = logs[2]
                  log_syslog = logs[3]
              %>
              <div class="tabbable">
                <ul class="nav nav-pills">
                  <li class="${ first_log_tab == 0 and 'active' or '' }"><a href="#logsDiagnostic" data-toggle="tab">${_('task diagnostic log')}</a></li>
                  <li class="${ first_log_tab == 1 and 'active' or '' }"><a href="#logsStdOut" data-toggle="tab">${_('stdout')}</a></li>
                  <li class="${ first_log_tab == 2 and 'active' or '' }"><a href="#logsStdErr" data-toggle="tab">${_('stderr')}</a></li>
                  <li class="${ first_log_tab == 3 and 'active' or '' }"><a href="#logsSysLog" data-toggle="tab">${_('syslog')}</a></li>
                </ul>
                <div class="tab-content">
                  <div class="tab-pane ${ first_log_tab == 0 and 'active' or '' }" id="logsDiagnostic">
                      % if not log_diagnostic:
                        <pre>-- empty --</pre>
                      % else:
                        <pre></pre>
                      % endif
                  </div>
                  <div class="tab-pane ${ first_log_tab == 1 and 'active' or '' }" id="logsStdOut">
                      % if not log_stdout:
                        <pre>-- empty --</pre>
                      % else:
                        <pre></pre>
                      % endif
                  </div>
                  <div class="tab-pane ${ first_log_tab == 2 and 'active' or '' }" id="logsStdErr">
                      % if not log_stderr:
                        <pre>-- empty --</pre>
                      % else:
                        <pre></pre>
                      % endif
                  </div>
                  <div class="tab-pane ${ first_log_tab == 3 and 'active' or '' }" id="logsSysLog">
                      % if not log_syslog:
                        <pre>-- empty --</pre>
                      % else:
                        <pre></pre>
                      % endif
                  </div>
                </div>
              </div>
            </div>
            </div>
          </p>
        </div>
      </div>
    </div>
  </div>
</div>

<script src="${ static('jobbrowser/js/utils.js') }" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript">
  $(document).ready(function () {
    enableResizeLogs();

    $("#metadataTable").dataTable({
      "bPaginate": false,
      "bLengthChange": false,
      "bInfo": false,
      "bAutoWidth": false,
      "bFilter": false,
      "aoColumns": [
        { "sWidth": "30%" },
        { "sWidth": "70%" }
      ],
      "oLanguage": {
        "sEmptyTable": "${_('No data available')}",
        "sZeroRecords": "${_('No matching records')}",
      }
    });

    $(".taskCountersTable").dataTable({
      "bPaginate": false,
      "bLengthChange": false,
      "bInfo": false,
      "bFilter": false,
      "bAutoWidth": false,
      "aoColumns": [
        { "sWidth": "30%" },
        { "sWidth": "70%" }
      ],
      "oLanguage": {
        "sEmptyTable": "${_('No data available')}",
        "sZeroRecords": "${_('No matching records')}",
      }
    });

    refreshLogs();

    initLogsElement($("#logsDiagnostic pre"));
    initLogsElement($("#logsStdOut pre"));
    initLogsElement($("#logsStdErr pre"));
    initLogsElement($("#logsSysLog pre"));

    function refreshLogs() {
      $.getJSON("?format=json", function (data) {
        if (data && data.logs && data.logs.length > 3) {
          var log_diagnostic = data.logs[0];
          var log_stdout = data.logs[1];
          var log_stderr = data.logs[2];
          var log_syslog = data.logs[3];

          appendAndScroll($("#logsDiagnostic pre"), log_diagnostic);
          appendAndScroll($("#logsStdOut pre"), log_stdout);
          appendAndScroll($("#logsStdErr pre"), log_stderr);
          appendAndScroll($("#logsSysLog pre"), log_syslog);

          if (data.isRunning) {
            window.setTimeout(refreshLogs, 1000);
          }
        }
      });
    }

    $(document).on("resized", function () {
      resizeLogs($("#logsDiagnostic pre"));
      resizeLogs($("#logsStdOut pre"));
      resizeLogs($("#logsStdErr pre"));
      resizeLogs($("#logsSysLog pre"));
    });

    $("a[data-toggle='tab']").on("shown", function (e) {
      resizeLogs($($(e.target).attr("href")).find("pre"));
    });

    $.jHueScrollUp();
  });
</script>

${ commonfooter(request, messages) | n,unicode }

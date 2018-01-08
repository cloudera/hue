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

${ commonheader(_('Job Attempt: %(attempt_index)s') % {'attempt_index': attempt_index}, "jobbrowser", user, request) | n,unicode }
${ comps.menubar() }

<div class="container-fluid">
  <div class="row-fluid">
    <div class="span2">
      <div class="sidebar-nav" style="padding-top: 0">
        <ul class="nav nav-list">
          <li class="nav-header">${ _('Attempt ID') }</li>
          <li class="white truncate-text" title="${ attempt_index }">${ attempt_index }</li>
        </ul>
      </div>
    </div>

    <div class="span10">
      <div class="card card-small">
        <h1 class="card-heading simple">
          ${ _('Job') } <a href="${url('jobbrowser.views.single_job', job=job.jobId)}" title="${_('View this job')}">${ job.jobId_short }</a>
          ${ _('Attempt: %(attempt_index)s') % {'attempt_index': attempt_index} }
        </h1>
        <div class="card-body">
          <p>
            <ul class="nav nav-pills">
              <li class="active"><a href="#stdout" data-toggle="tab">${_('stdout')}</a></li>
              <li><a href="#stderr" data-toggle="tab">${_('stderr')}</a></li>
              <li><a href="#syslog" data-toggle="tab">${_('syslog')}</a></li>
            </ul>

            <div class="tab-content">
              <div class="tab-pane active" id="stdout">
                <pre id="stdout-container">
                  <i class="fa fa-spinner fa-spin"></i>
                </pre>
              </div>

              <div class="tab-pane" id="stderr">
                <pre id="stderr-container">
                  <i class="fa fa-spinner fa-spin"></i>
                </pre>
              </div>

              <div class="tab-pane" id="syslog">
                <pre id="syslog-container">
                  <i class="fa fa-spinner fa-spin"></i>
                </pre>
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
      ]
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
      ]
    });

    // From 15s to less than 5s display time with async

    refreshLogs();

    initLogsElement($("#syslog-container"));
    initLogsElement($("#stdout-container"));
    initLogsElement($("#stderr-container"));

    function refreshSyslogs() {
      $.getJSON("${ url("job_attempt_logs_json", job=job.jobId, attempt_index=attempt_index, name='syslog', offset=log_offset) }", function (data) {
        if (data && data.log) {
          appendAndScroll($("#syslog-container"), data.log);
          window.setTimeout(refreshSyslogs, 5000);
        }
      });
    }

    function refreshStdout() {
      $.getJSON("${ url("job_attempt_logs_json", job=job.jobId, attempt_index=attempt_index, name='stdout', offset=log_offset) }", function (data) {
        if (data && data.log) {
          appendAndScroll($("#stdout-container"), data.log);
          window.setTimeout(refreshStdout, 5000);
        }
      });
    }

    function refreshStderr() {
      $.getJSON("${ url("job_attempt_logs_json", job=job.jobId, attempt_index=attempt_index, name='stderr', offset=log_offset) }", function (data) {
        if (data && data.log) {
          appendAndScroll($("#stderr-container"), data.log);
          window.setTimeout(refreshStderr, 5000);
        }
      });
    }

    function refreshLogs() {
      refreshSyslogs();
      refreshStdout();
      refreshStderr();
    }

    $(document).on("resized", function () {
      resizeLogs($("#syslog-container"));
      resizeLogs($("#stdout-container"));
      resizeLogs($("#stderr-container"));
    });

    $("a[data-toggle='tab']").on("shown", function (e) {
      resizeLogs($($(e.target).attr("href")).find("pre"));
    });

    $.jHueScrollUp();
  });
</script>

${ commonfooter(request, messages) | n,unicode }

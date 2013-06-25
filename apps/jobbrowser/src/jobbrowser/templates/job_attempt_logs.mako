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

${ commonheader(_('Job Attempt: %(attempt_index)s') % {'attempt_index': attempt_index}, "jobbrowser", user) | n,unicode }

<div class="container-fluid">
    <h1>
        ${ _('Job Browser') } -
        ${ _('Job') } <a href="${url('jobbrowser.views.single_job', job=job.jobId)}" title="${_('View this job')}">${ job.jobId_short }</a>
        ${ _('Attempt: %(attempt_index)s') % {'attempt_index': attempt_index} }
    </h1>
    <br/>
    <div class="row-fluid">
        <div class="span2">
            <div class="well sidebar-nav">
                <ul class="nav nav-list">
                    <li class="nav-header">${ _('Attempt ID') }</li>
                    <li>${ attempt_index }</li>
                </ul>
            </div>
        </div>

        <div class="span10">
            <ul class="nav nav-pills">
                <li class="active"><a href="#stdout" data-toggle="tab">${_('stdout')}</a></li>
                <li><a href="#stderr" data-toggle="tab">${_('stderr')}</a></li>
                <li><a href="#syslog" data-toggle="tab">${_('syslog')}</a></li>
            </ul>

            <div class="tab-content">
                <div class="tab-pane active" id="stdout">
                    <pre id="stdout-container">
                        ${_('Loading...')} <img src="/static/art/login-spinner.gif">
                    </pre>
                </div>

                <div class="tab-pane" id="stderr">
                    <pre id="stderr-container">
                        ${_('Loading...')} <img src="/static/art/login-spinner.gif">
                    </pre>
                </div>

                <div class="tab-pane" id="syslog">
                    <pre id="syslog-container">
                        ${_('Loading...')} <img src="/static/art/login-spinner.gif">
                    </pre>
                </div>
            </div>
        </div>
    </div>
</div>

<script src="/jobbrowser/static/js/utils.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript" charset="utf-8">
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
    var logsRefreshInterval = window.setInterval(function () {
      refreshLogs();
    }, 5000);

    $(document).on("stopLogsRefresh", function () {
      window.clearInterval(logsRefreshInterval);
    });

    initLogsElement($("#syslog-container"));
    initLogsElement($("#stdout-container"));
    initLogsElement($("#stderr-container"));

    function refreshLogs() {
      $.getJSON("${ url("jobbrowser.views.job_attempt_logs_json", job=job.jobId, attempt_index=attempt_index, name='syslog', offset=0) }", function (data) {
        if (data && data.log) {
          appendAndScroll($("#syslog-container"), data.log);
        }
        else {
          $(document).trigger("stopLogsRefresh");
        }
      });
      $.getJSON("${ url("jobbrowser.views.job_attempt_logs_json", job=job.jobId, attempt_index=attempt_index, name='stdout', offset=0) }", function (data) {
        if (data && data.log) {
          appendAndScroll($("#stdout-container"), data.log);
        }
        else {
          $(document).trigger("stopLogsRefresh");
        }
      });
      $.getJSON("${ url("jobbrowser.views.job_attempt_logs_json", job=job.jobId, attempt_index=attempt_index, name='stderr', offset=0) }", function (data) {
        if (data && data.log) {
          appendAndScroll($("#stderr-container"), data.log);
        }
        else {
          $(document).trigger("stopLogsRefresh");
        }
      });
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

${ commonfooter(messages) | n,unicode }

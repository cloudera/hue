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
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext as _
%>

<%namespace name="layout" file="layout.mako" />
<%namespace name="util" file="util.mako" />

${ commonheader(_('Waiting for query...'), app_name, user, '100px') | n,unicode }
${layout.menubar(section='query')}

## Required for unit tests
<!-- <meta http-equiv="refresh" content="3;${url(app_name + ':watch_query', query.id)}?${fwd_params}" /> -->

<div class="container-fluid">
    <h1>${_('Waiting for query...')} ${util.render_query_context(query_context)}</h1>
    <div class="row-fluid">
        <div class="span3">
            % if app_name == 'impala':
              <li class="nav">
                <div class="control-group">
                  <button id="cancel-btn" class="btn btn-small" data-loading-text="${ _('Canceling...') }" rel="tooltip" data-placement="right" data-original-title="${ _('Cancel the query') }">
                    ${ _('Cancel') }
                  </button>
                </div>
              </li>
            % endif
            <div class="well sidebar-nav
                % if app_name == 'impala':
                  hide
                % endif
            ">
                <ul class="nav nav-list">
                    <%
                      n_jobs = hadoop_jobs and len(hadoop_jobs) or 0
                      mr_jobs = (n_jobs == 1) and _('MR Job') or _('MR Jobs')
                    %>
                     % if n_jobs > 0:
                        <li id="jobsHeader" class="nav-header">${mr_jobs} (${n_jobs})</li>
                        % for jobid in hadoop_jobs:
                            <li><a class="jobLink" href="${url("jobbrowser.views.single_job", job=jobid)}">${jobid.replace("job_", "")}</a></li>
                        % endfor
                    % else:
                        <li id="jobsHeader" class="nav-header">${mr_jobs}</li>
                        <li class="jobLink">${_('No Hadoop jobs were launched in running this query.')}</li>
                    % endif
                </ul>
            </div>
        </div>
        <div class="span9">
            <ul class="nav nav-tabs">
                <li class="active"><a href="#log" data-toggle="tab">${_('Log')}</a></li>
                <li><a href="#query" data-toggle="tab">${_('Query')}</a></li>
            </ul>

               <div class="tab-content">
                <div class="active tab-pane" id="log">
                    <pre>${ force_unicode(log) }</pre>
                </div>
                <div class="tab-pane" id="query">
                    <pre>${ query.get_current_statement() }</pre>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
  $(document).ready(function(){
    var fwdUrl = "${url(app_name + ':watch_query', query.id)}?${fwd_params}";
    var labels = {
      MRJOB: "${_('MR Job')}",
      MRJOBS: "${_('MR Jobs')}"
    }

    resizeLogs();
    refreshView();
    var logsAtEnd = true;

    function refreshView() {
      $.getJSON("${url(app_name + ':watch_query_refresh_json', query.id)}", function (data) {
        if (data.isSuccess || data.isFailure) {
          location.href = fwdUrl;
        }
        if (data.jobs && data.jobs.length > 0) {
          $(".jobLink").remove();
          $("#jobsHeader").text((data.jobs.length > 1 ? labels.MRJOBS : labels.MRJOB) + " (" + data.jobs.length + ")");
          for (var i = 0; i < data.jobs.length; i++) {
            $("#jobsHeader").after($("<li>").addClass("jobLink").html("<a href=\"" + data.jobUrls[data.jobs[i]] + "\">" + data.jobs[i].replace("job_", "") + "</a>"));
          }
        }
        var _logsEl = $("#log pre");
        % if app_name == 'impala':
          _logsEl.text($.trim(data.log));
        % else:
          var newLines = data.log.split("\n").slice(_logsEl.text().split("\n").length);
          _logsEl.text(_logsEl.text() + newLines.join("\n"));
        % endif

        if (logsAtEnd) {
          _logsEl.scrollTop(_logsEl[0].scrollHeight - _logsEl.height());
        }
        window.setTimeout(refreshView, 1000);
      });
    }

    $(window).resize(function () {
      resizeLogs();
    });

    $("a[href='#log']").on("shown", function () {
      resizeLogs();
    });

    $("#log pre").scroll(function () {
      if ($(this).scrollTop() + $(this).height() + 20 >= $(this)[0].scrollHeight) {
        logsAtEnd = true;
      }
      else {
        logsAtEnd = false;
      }
    });

    function resizeLogs() {
      $("#log pre").css("overflow", "auto").height($(window).height() - $("#log pre").position().top - 40);
    }

    % if app_name == 'impala':
      $("#cancel-btn").click(function() {
        var _this = this;
        $(_this).button('loading');
        $.post("${ url(app_name + ':cancel_operation', query.id) }",
          function(response) {
            if (response['status'] != 0) {
              $.jHueNotify.error("${ _('Problem: ') }" + response['message']);
            } else {
              $.jHueNotify.info("${ _('Query canceled!') }")
            }
          }
        );
        return false;
      });
    % endif
  });
</script>

${ commonfooter(messages) | n,unicode }

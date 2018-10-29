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
  from desktop.views import commonheader, commonfooter
  from django.utils.translation import ugettext as _
%>

<%namespace name="comps" file="jobbrowser_components.mako" />

${ commonheader(_('Task View: Job: %(jobId)s') % dict(jobId=job.jobId_short), "jobbrowser", user, request) | n,unicode }
${ comps.menubar() }

<%def name="selected(val, state)">
    %   if val is not None and state is not None and val in state:
        selected="true"
    %   endif
</%def>

<div class="container-fluid">
  <div class="card card-small">
    <h1 class="card-heading simple">${_('Task View: Job: %(jobId)s') % dict(jobId=job.jobId_short)}</h1>
    <div class="card-body">
      <p>
        <form method="get" action="${ url('jobbrowser.views.tasks', job=job.jobId) }">
          <b>${_('Filter tasks:')}</b>
          <select name="taskstate" class="submitter">
            <option value="">${_('All states')}</option>
            <option value="succeeded" ${selected('succeeded', taskstate)}>${_('succeeded')}</option>
            <option value="running" ${selected('running', taskstate)}>${_('running')}</option>
            <option value="failed" ${selected('failed', taskstate)}>${_('failed')}</option>
            <option value="killed" ${selected('killed', taskstate)}>${_('killed')}</option>
            <option value="pending" ${selected('pending', taskstate)}>${_('pending')}</option>
          </select>

          <select name="tasktype" class="submitter">
            <option value="">${_('All types')}</option>
            <option value="map" ${selected('map', tasktype)}>${_('maps')}</option>
            <option value="reduce" ${selected('reduce', tasktype)}>${_('reduces')}</option>
            <option value="job_cleanup" ${selected('job_cleanup', tasktype)}>${_('cleanups')}</option>
            <option value="job_setup" ${selected('job_setup', tasktype)}>${_('setups')}</option>
          </select>

          <input type="text" name="tasktext"  class="submitter" title="${_('Text filter')}" placeholder="${_('Text Filter')}"
              % if tasktext:
                 value="${tasktext}"
              % endif
          />
        </form>
      </p>

      <table class="datatables table table-condensed" id="all_tasks">
        <thead>
          <tr>
            <th>${_('Logs')}</th>
            <th>${_('Task ID')}</th>
            <th>${_('Type')}</th>
            <th>${_('Progress')}</th>
            <th>${_('Status')}</th>
            <th>${_('State')}</th>
            <th>${_('Start Time')}</th>
            <th>${_('End Time')}</th>
            <th>${_('View Attempts')}</th>
          </tr>
        </thead>
        <tbody>
        %for t in task_list:
          <tr>
            <td data-row-selector-exclude="true">
                %if t.taskAttemptIds:
                <a href="${ url('single_task_attempt_logs', job=t.jobId, taskid=t.taskId, attemptid=t.taskAttemptIds[-1]) }" data-row-selector-exclude="true"><i class="fa fa-tasks"></i></a>
                %endif
            </td>
            <td>${t.taskId_short}</td>
            <td>${t.taskType}</td>
            <td>
              <div class="bar">${ "%d" % (t.progress * 100) }%</div>
            </td>
            <td>
              <a href="${ url('jobbrowser.views.tasks', job=job.jobId) }?${ get_state_link(request, 'taskstate', t.state.lower()) }"
                 title="${ _('Show only %(state)s tasks') % dict(state=t.state.lower()) }"
                 class="${ t.state.lower() }">${ t.state.lower() }
              </a>
            </td>
            <td>${t.mostRecentState}</td>
            <td>${t.execStartTimeFormatted}</td>
            <td>${t.execFinishTimeFormatted}</td>
            <td><a href="${ url('jobbrowser.views.single_task', job=job.jobId, taskid=t.taskId) }" data-row-selector="true">${_('Attempts')}</a></td>
          </tr>
        %endfor
        </tbody>
      </table>
    </div>
  </div>
</div>

<script src="${ static('desktop/ext/js/datatables-paging-0.1.js') }" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript">
    $(document).ready(function(){
        $("#all_tasks").dataTable({
            "sPaginationType":"bootstrap",
            "iDisplayLength":100,
            "bLengthChange": false,
            "sDom":"<'row'r>t<'row'<'span6'i><''p>>",
            "bFilter": false,
            "aaSorting": [[ 1, "asc" ]],
            "aoColumns":[
              { "bSortable":false },
              null,
              null,
              null,
              null,
              null,
              null,
              null,
              { "bSortable":false }
            ],
            "oLanguage": {
              "sEmptyTable": "${_('No data available')}",
              "sZeroRecords": "${_('No matching records')}",
              "sInfo":"${_('Showing _START_ to _END_ of _TOTAL_ entries')}",
              "sInfoEmpty":"${_('Showing 0 to 0 of 0 entries')}",
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
    });
</script>

${ commonfooter(request, messages) | n,unicode }

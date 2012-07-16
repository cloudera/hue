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
  from desktop import appmanager
  from django.template.defaultfilters import urlencode
  from desktop.views import commonheader, commonfooter
  from django.utils.translation import ugettext as _
%>
<%namespace name="comps" file="jobbrowser_components.mako" />

<%def name="get_state(option, state)">
%   if option == state:
      selected="true"
%   endif
</%def>

% if len(jobs) > 0 or filtered:
${commonheader(_('Job Browser'), "jobbrowser")}
<div class="container-fluid">
<h1>${_('Job Browser')}</h1>
<div class="well hueWell">
    <form action="/jobbrowser/jobs" method="GET">
        <b>${_('Filter jobs:')}</b>
                <select name="state" class="submitter">
                    <option value="all" ${get_state('all', state_filter)}>${_('All States')}</option>
                    <option value="running" ${get_state('running', state_filter)}>${_('Running')}</option>
                    <option value="completed" ${get_state('completed', state_filter)}>${_('Completed')}</option>
                    <option value="failed" ${get_state('failed', state_filter)}>${_('Failed')}</option>
                    <option value="killed" ${get_state('killed', state_filter)}>${_('Killed')}</option>
                </select>

                <input type="text" name="user" title="${_('User Name Filter')}" value="${user_filter}" placeholder="${_('User Name Filter')}" class="submitter"/>
                <input type="text" name="text" title="${_('Text Filter')}" value="${text_filter}" placeholder="${_('Text Filter')}" class="submitter"/>
    </form>
</div>


% if len(jobs) == 0:
<p>${_('There were no jobs that match your search criteria.')}</p>
% else:
<table class="datatables table table-striped table-condensed">
    <thead>
        <tr>
            <th>${_('Id')}</th>
            <th>${_('Name')}</th>
            <th>${_('Status')}</th>
            <th>${_('User')}</th>
            <th>${_('Maps')}</th>
            <th>${_('Reduces')}</th>
            <th>${_('Queue')}</th>
            <th>${_('Priority')}</th>
            <th>${_('Duration')}</th>
            <th>${_('Date')}</th>
            <th></th>
        </tr>
    </thead>
    <tbody>
        % for job in jobs:
        <tr>
            <td>
                <div class="jobbrowser_jobid_short">${job.jobId_short}</div>
            </td>
            <td>
                ${job.jobName}
            </td>
            <td>
                <a href="${url('jobbrowser.views.jobs')}?${get_state_link(request, 'state', job.status.lower())}" title="${_('Show only %(status)s jobs') % dict(status=job.status.lower())}">
                  ${job.status.lower()}
                </a>
                % if job.is_retired:
                  </br>
                  ${_('retired')}
                % endif
            </td>
            <td>
                <a href="${url('jobbrowser.views.jobs')}?${get_state_link(request, 'user', job.user.lower())}" title="${_('Show only %(status)s jobs') % dict(status=job.user.lower())}">${job.user}</a>
            </td>
            <td>
                <span alt="${job.maps_percent_complete}">
                    % if job.is_retired:
                        ${_('N/A')}
                    % else:
                    ${comps.mr_graph_maps(job)}
                    % endif
                 </span>
            </td>
            <td>
                <span alt="${job.reduces_percent_complete}">
                    % if job.is_retired:
                        ${_('N/A')}
                    % else:
                        ${comps.mr_graph_reduces(job)}
                    % endif
                </span>
            </td>
            <td>${job.queueName}</td>
            <td>${job.priority.lower()}</td>
            <td>
                <span alt="${job.finishTimeMs-job.startTimeMs}">
                    % if job.is_retired:
                        ${_('N/A')}
                    % else:
                        ${job.durationFormatted}
                    % endif
                </span>
            </td>
            <td><span alt="${job.startTimeMs}">${job.startTimeFormatted}</span></td>
            <td>
                <a href="${url('jobbrowser.views.single_job', jobid=job.jobId)}" title="${_('View this job')}" data-row-selector="true">${_('View')}</a>
                % if job.status.lower() == 'running' or job.status.lower() == 'pending':
                % if request.user.is_superuser or request.user.username == job.user:
                - <a href="#" title="${_('Kill this job')}" onclick="$('#kill-job').submit()">${_('Kill')}</a>
                <form id="kill-job" action="${url('jobbrowser.views.kill_job', jobid=job.jobId)}?next=${request.get_full_path()|urlencode}" method="POST"></form>
                % endif
                % endif
            </td>
            </tr>
            % endfor
        </tbody>
    </table>
    % endif

    % else:
    ${commonheader(_('Job Browser'), "jobbrowser")}
    <div class="container-fluid">
    <h1>${_('Welcome to the Job Browser')}</h1>
    <div>
        <p>${_("There aren't any jobs running. Let's fix that.")}</p>
        % if appmanager.get_desktop_module('jobsub') is not None:
        <a href="/jobsub/">${_('Launch the Job Designer')}</a><br/>
        % endif
        % if appmanager.get_desktop_module('beeswax') is not None:
        <a href="/beeswax/">${_('Launch Beeswax')}</a><br/>
        % endif
    </div>
    % endif
</div>

<script type="text/javascript" charset="utf-8">
    $(document).ready(function(){
        $(".datatables").dataTable({
            "bPaginate": false,
            "bLengthChange": false,
            "bFilter": false,
            "bInfo": false,
            "aaSorting": [[ 0, "desc" ]],
            "aoColumns": [
                null,
                null,
                null,
                null,
                { "sType": "alt-numeric" },
                { "sType": "alt-numeric" },
                null,
                null,
                { "sType": "alt-numeric" },
                { "sType": "alt-numeric" },
                {"bSortable":false}
            ]
        });
        $("a[data-row-selector='true']").jHueRowSelector();
    });
</script>

${commonfooter()}

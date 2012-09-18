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
    from django.utils.translation import ugettext as _
%>

<%def name="task_counters(counters)">
    <%
        from jobbrowser.views import format_counter_name
    %>
    % for group in counters.groups:
        <h3>${format_counter_name(group.displayName)}</h3>
        <table class="taskCountersTable table table-striped table-condensed">
            <thead>
            <tr>
                <th>${_('Counter Name')}</th>
                <th>${_('Value')}</th>
            </tr>
            </thead>
        <tbody>
            % for name, counter in sorted(group.counters.iteritems()):
            <tr>
                <td>${format_counter_name(counter.displayName)}</td>
                <td>${counter.value}</td>
            </tr>
            % endfor
        </tbody>
        </table>
    % endfor
</%def>

<%def name="job_counters(counters)">
    <%
        from jobbrowser.views import format_counter_name
    %>
    % for group in counters.itervalues():
        <h3>${format_counter_name(group['displayName'])}</h3>
        <table class="jobCountersTable table table-striped table-condensed">
            <thead>
            <tr>
                <th>${_('Name')}</th>
                <th>${_('Maps Total')}</th>
                <th>${_('Reduces Total')}</th>
                <th>${_('Total')}</th>
            </tr>
            </thead>
        <tbody>
            % for name, counter in sorted(group['counters'].iteritems()):
            <%
                map_count = counter.get('map', 0)
                reduce_count = counter.get('reduce', 0)
                job_count = counter.get('job', 0)
            %>
            <tr>
                % if not job.is_retired:
	                <td>${format_counter_name(counter.get('displayName', 'n/a'))}</td>
	                <td>${map_count}</td>
	                <td>${reduce_count}</td>
	                <td>${map_count + reduce_count + job_count}</td>
                % else:
	                <td>N/A</td>
	                <td>N/A</td>
	                <td>N/A</td>
	                <td>N/A</td>
                % endif
            </tr>
            % endfor
        </tbody>
        </table>
    % endfor
</%def>

<%def name="mr_graph(job)">
    <div>
        ${mr_graph_maps(job)}
        ${mr_graph_reduces(job)}
    </div>
</%def>

<%def name="mr_graph_maps(job)">
    <div class="progress ${get_bootstrap_class(job, 'progress')}">
        <div class="bar-label">${job.finishedMaps} / ${job.desiredMaps}</div>
        <div class="bar" style="margin-top:-20px;width: ${job.maps_percent_complete}%;"></div>
    </div>
</%def>

<%def name="mr_graph_reduces(job)">
    <div class="progress ${get_bootstrap_class(job, 'progress')}">
        <div class="bar-label">${job.finishedReduces} / ${job.desiredReduces}</div>
        <div class="bar" style="margin-top:-20px;width: ${job.reduces_percent_complete}%;"></div>
    </div>
</%def>

<%def name="get_status(job)">
    <%
    additional_class = get_bootstrap_class(job, 'label')
    %>
    % if job.is_retired:
        <span class="label ${additional_class}"><i class="icon-briefcase icon-white" title="${ _('Retired') }"></i> ${job.status.lower()}</span>
    % else:
        <span class="label ${additional_class}">${job.status.lower()}</span>
    % endif
</%def>


<%def name="get_bootstrap_class(job, prefix)">
    <%
    additional_class = prefix
    status = job.status.lower()
    if status in ('succeeded', 'ok'):
        additional_class += '-success'
    elif status in ('running', 'prep'):
        additional_class += '-warning'
    elif status == 'ready':
        additional_class += '-success'
    else:
        if (prefix == 'label'):
            additional_class += '-important'
        else:
            additional_class += '-danger'
        endif
    endif
    if job.is_retired:
        additional_class += '-warning'
    endif
    return additional_class
    %>
</%def>

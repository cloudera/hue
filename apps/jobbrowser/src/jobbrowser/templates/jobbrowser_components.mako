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

<%def name="task_counters(counters,_)">
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

<%def name="job_counters(counters,_)">
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
                <td>${format_counter_name(counter.get('displayName', 'n/a'))}</td>
                <td>${map_count}</td>
                <td>${reduce_count}</td>
                <td>${map_count + reduce_count + job_count}</td>
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
    <div class="bar">${job.finishedMaps} / ${job.desiredMaps}</div>
</%def>

<%def name="mr_graph_reduces(job)">
    <div class="bar">${job.finishedReduces} / ${job.desiredReduces}</div>
</%def>

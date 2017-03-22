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
        <table class="taskCountersTable table table-condensed">
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


<%def name="task_counters_mr2(counters)">
    <%
        from jobbrowser.views import format_counter_name
    %>
    % for group in counters.get('taskCounterGroup', []):
        <h3>${ format_counter_name(group['counterGroupName']) }</h3>
        <table class="taskCountersTable table table-condensed">
            <thead>
            <tr>
                <th>${_('Counter Name')}</th>
                <th>${_('Value')}</th>
            </tr>
            </thead>
        <tbody>
            % for counter in group['counter']:
            <tr>
                <td>${format_counter_name(counter['name'])}</td>
                <td>${counter['value']}</td>
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
        <table class="jobCountersTable table table-condensed">
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

<%def name="job_counters_mr2(counters)">
    <%
        from jobbrowser.views import format_counter_name
    %>
    % for counter_group in counters.get('counterGroup', []):
        <h3>${ format_counter_name(counter_group['counterGroupName']) }</h3>
        <table class="jobCountersTable table table-condensed">
            <thead>
            <tr>
                <th>${_('Name')}</th>
                <th>${_('Maps Total')}</th>
                <th>${_('Reduces Total')}</th>
                <th>${_('Total')}</th>
            </tr>
            </thead>
        <tbody>
            % for counter in counter_group['counter']:
            <%
                map_count = counter.get('mapCounterValue', 0)
                reduce_count = counter.get('reduceCounterValue', 0)
                total_count = counter.get('totalCounterValue', 0)
            %>
            <tr>
                % if not job.is_retired:
                    <td>${ format_counter_name(counter.get('name', 'n/a')) }</td>
                    <td>${ map_count }</td>
                    <td>${ reduce_count }</td>
                    <td>${ total_count }</td>
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
        % if job.is_mr2:
            <div class="bar-label">${job.maps_percent_complete}</div>
        % else:
            <div class="bar-label">${job.finishedMaps} / ${job.desiredMaps}</div>
        % endif
        <div class="bar" style="margin-top:-20px;width: ${job.maps_percent_complete}%;"></div>
    </div>
</%def>

<%def name="mr_graph_reduces(job)">
    <div class="progress ${get_bootstrap_class(job, 'progress')}">
        % if job.is_mr2:
            <div class="bar-label">${job.maps_percent_complete}</div>
        % else:
            <div class="bar-label">${job.finishedReduces} / ${job.desiredReduces}</div>
        % endif
        <div class="bar" style="margin-top:-20px;width: ${job.reduces_percent_complete}%;"></div>
    </div>
</%def>

<%def name="get_status(job)">
    <%
    additional_class = get_bootstrap_class(job, 'label')
    %>
    % if job.is_retired and not job.is_mr2:
        <span class="label ${additional_class}"><i class="fa fa-briefcase" style="color: #fff" title="${ _('Retired') }"></i> ${job.status.lower()}</span>
    % else:
        <span class="label ${additional_class}">${job.status.lower()}</span>
    % endif
</%def>

<%def name="get_container_link(status, node_manager_http_address, container_id)">
    ## As soon as the job finishes the container disappears
    % if status.lower() in ('running', 'accepted', 'ready', 'prep', 'waiting', 'suspended', 'prepsuspended', 'preppaused', 'paused', 'submitted', 'suspendedwitherror', 'pausedwitherror', 'finishing', 'started'):
        <a href="${ url('jobbrowser.views.container', node_manager_http_address=node_manager_http_address, containerid=container_id) }" class="task_tracker_link">${ container_id }</a>
    % else:
        ${ container_id }
    % endif
</%def>

<%def name="get_bootstrap_class(job, prefix)">
    <%
    additional_class = prefix
    status = job.status.lower()

    if status in ('succeeded', 'ok'):
        additional_class += '-success'
    elif status in ('running', 'prep', 'accepted', 'finishing'):
        additional_class += '-warning'
    elif status == 'ready':
        additional_class += '-success'
    elif status == 'killed':
        additional_class += '-inverse'
    else:
        if (prefix == 'label'):
            additional_class += '-important'
        else:
            additional_class += '-danger'
        endif
    endif

    if job.is_retired and not job.is_mr2:
        additional_class += '-warning'
    endif

    return additional_class
    %>
</%def>

<%def name="menubar(hiveserver2_impersonation_enabled=True)">
  <div class="navbar hue-title-bar nokids">
      <div class="navbar-inner">
        <div class="container-fluid">
          <div class="nav-collapse">
            <ul class="nav">
              <li class="app-header">
                <a href="/${app_name}">
                  <img src="${ static('jobbrowser/art/icon_jobbrowser_48.png') }" class="app-icon" alt="${ _('Job browser icon') }"/>
                  ${ _('Job Browser') }
                </a>
              </li>
            </ul>
            % if not hiveserver2_impersonation_enabled:
              <div class="pull-right alert alert-warning" style="margin-top: 4px">${ _("Hive jobs are running as the 'hive' user") }</div>
            % endif
          </div>
        </div>
      </div>
  </div>
</%def>


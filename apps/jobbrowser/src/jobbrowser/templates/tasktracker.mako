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

${ commonheader(_('Tracker: %(trackerId)s') % dict(trackerId=tracker.trackerId), "jobbrowser", user) | n,unicode }

<div class="container-fluid">
    <h1>${_('Tracker at %(trackerHost)s on port %(trackerPort)s') % dict(trackerHost=tracker.host, trackerPort=tracker.httpPort)}</h1>
    <div>
        <dl>
            <dt>${_('ID')}</dt>
            <dd>${ tracker.trackerId }</dd>
            % if not tracker.is_mr2:
            <dt>${_('Last heard from at')}</dt>
            <dd>${ tracker.lastSeenFormatted }.</dd>
            % endif
        </dl>
    </div>

    % if tracker.is_mr2:
    <h2>${_('Memory Metrics')}</h2>
    <div>
        <dl>
            <dt>${_('Node Id')}</dt>
            <dd>${tracker.nodeId }</dd>
            <dt>${_('State')}</dt>
            <dd>${tracker.state }</dd>
            <dt>${_('User')}</dt>
            <dd>${tracker.user}</dd>
            <dt>${_('Diagnostics')}</dt>
            <dd>${tracker.diagnostics}</dd>
            <dt>${_('Total Memory Needed in MB')}</dt>
            <dd>${tracker.totalMemoryNeededMB}</dd>
            <dt>${_('Exit Code')}</dt>
            <dd>${tracker.exitCode}</dd>
        </dl>
    </div>
    % else:
    <h2>${_('Memory Metrics')}</h2>
    <div>
        <dl>
            <dt>${_('Total virtual memory:')}</dt>
            <dd>${tracker.totalVirtualMemory }</dd>
            <dt>${_('Total physical memory:')}</dt>
            <dd>${tracker.totalPhysicalMemory }</dd>
            <dt>${_('Available space:')}</dt>
            <dd>${tracker.availableSpace}</dd>
        </dl>
    </div>

    <h2>${_('Map and Reduce')}</h2>
    <div>
        <dl>
            <dt>${_('Map count:')}</dt>
            <dd>${tracker.mapCount}</dd>
            <dt>${_('Reduce count:')}</dt>
            <dd>${tracker.reduceCount}</dd>
            <dt>${_('Max map tasks:')}</dt>
            <dd>${tracker.maxMapTasks}</dd>
            <dt>${_('Max reduce tasks:')}</dt>
            <dd>${tracker.maxReduceTasks}</dd>
        </dl>
    </div>
    % endif
</div>

${ commonfooter(messages) | n,unicode }

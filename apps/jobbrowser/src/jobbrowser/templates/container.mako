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

${ commonheader(_('Container: %(trackerId)s') % dict(trackerId=tracker.trackerId), "jobbrowser", user, request) | n,unicode }
${ comps.menubar()}

<div class="container-fluid">
  <div class="row-fluid">
    <div class="span12">
      <div class="card card-home">
        <div class="card-body">
          <p>

    <h1>${_('Container at %(trackerHost)s on port %(trackerPort)s') % dict(trackerHost=tracker.host, trackerPort=tracker.httpPort)}</h1>
    <div>
        <dl>
            <dt>${_('ID')}</dt>
            <dd>${ tracker.trackerId }</dd>
        </dl>
    </div>

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

          <a class="btn" href="javascript:history.back()">${_('Back')}</a>

          </p>
        </div>
      </div>
    </div>
</div>

${ commonfooter(request, messages) | n,unicode }

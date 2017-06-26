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
${ commonheader(_('Task Trackers'), "jobbrowser", user, request) | n,unicode }
${ comps.menubar()}
<div class="container-fluid">
<div class="row-fluid">
  <div class="span12">
    <div class="card card-small">
      <h2 class="card-heading simple">${_('Task Trackers')}</h2>
      <div class="card-body">
        <p>

<table class="datatables" style="width: 100%">
    <thead>
        <tr>
            <th>${_('Name')}</th>
            <th>${_('Host')}</th>
            <th>${_('Port')}</th>
            <th>${_('Last Seen')}</th>
            <th>${_('Available Space')}</th>
            <th>${_('Failure Count')}</th>
            <th>${_('Map Count')}</th>
            <th>${_('Reduce Count')}</th>
            <th>${_('Max Map Tasks')}</th>
            <th>${_('Max Reduce Tasks')}</th>
        </tr>
    </thead>
    <tbody>
        % for t in trackers:
        <tr>
            <td><a href="/jobbrowser/trackers/${t.trackerId}">${t.trackerId}</a></td>
            <td>${t.host}</td>
            <td>${t.httpPort}</td>
            <td>${t.lastSeenFormatted}</td>
            <td>${t.availableSpace}</td>
            <td>${t.failureCount}</td>
            <td>${t.mapCount}</td>
            <td>${t.reduceCount}</td>
            <td>${t.maxMapTasks}</td>
            <td>${t.maxReduceTasks}</td>
        </tr>
        % endfor
    </tbody>
</table>

<div id="trackerDialog"></div>

        </p>
      </div>
    </div>
  </div>
</div>
</div>

<script type="text/javascript">
$(document).ready(function(){
    $(".datatables").dataTable({
        "bPaginate": false,
        "bLengthChange": false,
        "bFilter": false,
        "bInfo": false,
        "oLanguage": {
            "sEmptyTable": "${_('No data available')}",
            "sZeroRecords": "${_('No matching records')}",
        }
    });
});
</script>

${ commonfooter(request, messages) | n,unicode }

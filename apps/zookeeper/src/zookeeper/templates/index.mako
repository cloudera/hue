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

<%namespace name="shared" file="shared_components.mako" />

${ commonheader(_('View'), app_name, user, request) | n,unicode }
${ shared.menubar() }

<%
  _breadcrumbs = [
    ["Clusters", url('zookeeper:index')]
  ]
%>

% if not clusters:
  <div class="container-fluid">
    <div class="card">
      <h1 class="card-heading simple">${ _('There are currently no clusters to browse.') }</h1>
    <div class="card-body">
      <p>
        ${ _('Please contact your administrator to solve this.') }
        <br/>
        <br/>
      </p>
    </div>
    </div>
  </div>
% else:
  ${ shared.header(_breadcrumbs, clusters) }
% for c in clusters:
  <h3 class="card-heading simple simpler">${ c }</h3>
  <p>
    <br/>
    &nbsp;&nbsp;<a href="${ url('zookeeper:view', id=c) }">${ _("Znode Hierarchy") }</a> 
  </p>
  <table class="table">
    <thead>
      <tr>
        <th>${ _("Node") }</th>
        <th>${ _("Role") }</th>
        <th>${ _("Avg Latency") }</th>
        <th>${ _("Watch Count") }</th>
        <th>${ _("Version") }</th>
      </tr>
    </thead>
    <tbody>
    % for host, stats in overview[c].items():
      <tr>
      % if stats:
        <td><a href="${ url('zookeeper:clients', id=c, host=host) }" data-row-selector="true">${ host }</a></td>
        <td>${stats.get('zk_server_state', '')}</td>
        <td>${stats.get('zk_avg_latency', '')}</td>
        <td>${stats.get('zk_watch_count', '')}</td>
        <td>${stats.get('zk_version', '')}</td>
      % else:
	<td><a href="${ url('zookeeper:clients', id=c, host=host) }" style="color:red" data-row-selector="true">${ host }</a></td>
        <td>-</td>
        <td>-</td>
        <td>-</td>
        <td>-</td>
      % endif
      </tr>
    % endfor
    </tbody>
  </table>
% endfor
${ shared.footer() }
%endif


<script type="text/javascript">
  $(document).ready(function () {
    $("a[data-row-selector='true']").jHueRowSelector();
  });
</script>

${ commonfooter(request, messages) | n,unicode }

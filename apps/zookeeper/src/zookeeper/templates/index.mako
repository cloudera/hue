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

${ commonheader(_('View'), app_name, user, '60px') | n,unicode }

<%
  _breadcrumbs = [
    ["ZooKeeper Browser", url('zookeeper:index')]
  ]
%>


${ shared.header(_breadcrumbs, clusters) }

% for i, c in enumerate(clusters):
  <h3 class="card-heading simple simpler">${ _('Cluster') } <a href="${ url('zookeeper:view', id=i) }">${ c }</a></h3>
  <table class="table">
    <thead>
      <tr>
        <th>Node</th>
        <th>Role</th>
        <th>Avg Latency</th>
        <th>Watch Count</th>
        <th>Version</th>
      </tr>
    </thead>
    <tbody>
    % for host, stats in overview[c].items():
      <tr>
        <td><a href="${ url('zookeeper:clients', id=i, host=host) }" data-row-selector="true">${ host }</a></td>
        <td>${stats.get('zk_server_state', '')}</td>
        <td>${stats.get('zk_avg_latency', '')}</td>
        <td>${stats.get('zk_watch_count', '')}</td>
        <td>${stats.get('zk_version', '')}</td>
      </tr>
    % endfor
    </tbody>
  </table>
% endfor


${ shared.footer() }

<script type="text/javascript" charset="utf-8">
  $(document).ready(function () {
    $("a[data-row-selector='true']").jHueRowSelector();
  });
</script>

${ commonfooter(messages) | n,unicode }

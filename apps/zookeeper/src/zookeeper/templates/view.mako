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
    [_("Clusters"), url('zookeeper:index')],
    [cluster['nice_name'].lower(), url('zookeeper:view', id=cluster['id'])]
  ]
%>

<%def name="show_stats(stats)">
  <thead>
  <tr>
    <th width="20%">${ _('Key') }</th>
    <th>${ _('Value') }</th>
  </tr>
  </thead>
  <tr>
    <td>${ _('Version') }</td>
    <td>${stats.get('zk_version')}</td>
  </tr>

  <tr>
    <td>${ _('Latency') }</td>
    <td>
      ${ _('Min:') } ${stats.get('zk_min_latency', '')}
      ${ _('Avg:') } ${stats.get('zk_avg_latency', '')}
      ${ _('Max:') } ${stats.get('zk_max_latency', '')}
    </td>
  </tr>

  <tr>
    <td>${ _('Packets') }</td>
    <td>${ _('Sent:') } ${stats.get('zk_packets_sent', '')}
      ${ _('Received:') } ${stats.get('zk_packets_received', '')}
    </td>
  </tr>

  <tr>
    <td>${ _('Outstanding Requests') }</td>
    <td>${stats.get('zk_outstanding_requests', '')}</td>
  </tr>

  <tr>
    <td>${ _('Watch Count') }</td>
    <td>${stats.get('zk_watch_count', '')}</td>
  </tr>

  <tr>
    <td>${ _('Open FD Count') }</td>
    <td>${stats.get('zk_open_file_descriptor_count', '')}</td>
  </tr>

  <tr>
    <td>${ _('Max FD Count') }</td>
    <td>${stats.get('zk_max_file_descriptor_count', '')}</td>
  </tr>
</%def>


${ shared.header(_breadcrumbs, clusters, False) }
<div class="row-fluid" style="margin-top: 20px">
  <div class="span3">
    <div class="sidebar-nav">
      <ul class="nav nav-list" style="border: 0">
        <li class="nav-header">${ _('Znodes') }</li>
        <li><a href="${url('zookeeper:tree', id=cluster['id'], path='/')}"> ${ _('View Znode Hierarchy') }</a></li>
      </ul>
    </div>
  </div>
  <div class="span9">
    % if leader:
    <h2 class="card-heading simple simpler">${ _('General') }</h2>
    <table class="table">
      <thead>
      <tr>
        <th width="20%">${ _('Key') }</th>
        <th>${ _('Value') }</th>
      </tr>
      </thead>
      <tr>
        <td>${ _('ZNode Count') }</td>
        <td>${leader.get('zk_znode_count', '')}</td>
      </tr>

      <tr>
        <td>${ _('Ephemerals Count') }</td>
        <td>${leader.get('zk_ephemerals_count', '')}</td>
      </tr>

      <tr>
        <td>${ _('Approximate Data Size') }</td>
        <td>${leader.get('zk_approximate_data_size', '')} bytes</td>
      </tr>

    </table>
    % endif

    % if leader:
      <h2 class="card-heading simple simpler">
        <div class="pull-right"><a href="${url('zookeeper:clients', id=cluster['id'], host=leader['host'])}"><i class="fa fa-eye"></i> ${_('Client Connections')}</a></div>
        ${ _('Node') } ${leader['host']} (${ _('leader') })
      </h2>

      <table class="table">
        ${show_stats(leader)}

        <tr><td>${ _('Followers') }</td>
          <td>${leader.get('zk_followers', '')}</td>
        </tr>

        <tr><td>${ _('Synced Followers') }</td>
          <td>${leader.get('zk_synced_followers', '')}</td>
        </tr>

        <tr><td>${ _('Pending Syncs') }</td>
          <td>${leader.get('zk_pending_syncs', '')}</td>
        </tr>

      </table>
    % endif

    % for stats in followers:
      <h2 class="card-heading simple simpler">
        <div class="pull-right"><a href="${url('zookeeper:clients', id=cluster['id'], host=stats['host'])}"><i class="fa fa-eye"></i> ${ _('Client Connections') }</a></div>
      ${ _('Node') } ${stats['host']} (${ _('follower') })
      </h2>
      <table class="table">
        ${show_stats(stats)}
      </table>
    % endfor

  </div>
</div>


${ shared.footer() }

${ commonfooter(request, messages) | n,unicode }

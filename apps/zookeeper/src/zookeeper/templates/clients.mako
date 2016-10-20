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

${ commonheader(_('Clients'), app_name, user, request) | n,unicode }
${ shared.menubar() }

<%
  _breadcrumbs = [
    [_("Clusters"), url('zookeeper:index')],
    [cluster['nice_name'].lower(), url('zookeeper:view', id=cluster['id'])],
    [host + ":" + port, url('zookeeper:clients', id=cluster['id'], host=host + ":" + port)]
  ]
%>

${ shared.header(_breadcrumbs, clusters) }

% if clients:
  <table class="table">
  <thead>
    <tr>
      <th>${ _("Host") }</th>
      <th>${ _("Port") }</th>
      <th>${ _("Interest Ops") }</th>
      <th>${ _("Queued") }</th>
      <th>${ _("Received") }</th>
      <th>${ _("Sent") }</th>
  </thead>
  % for client in clients:
    <tr>
      <td>${client.host}</td>
      <td>${client.port}</td>
      <td>${client.interest_ops}</td>
      <td>${client.queued}</td>
      <td>${client.recved}</td>
      <td>${client.sent}</td>
    </tr>
  % endfor
  </table>
% endif

${ shared.footer() }

${ commonfooter(request, messages) | n,unicode }

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
  from filebrowser.views import location_to_url
  from desktop.views import commonheader, commonfooter
  from django.utils.translation import ugettext as _
%>

<%namespace name="layout" file="layout.mako" />

${ commonheader(_('Beeswax Table Partitions: %(tableName)s') % dict(tableName=table.name), app_name, user, '100px') | n,unicode }
${layout.menubar(section='tables')}

<div class="container-fluid">
<h1>${_('Partitions')}</h1>

<table class="table table-striped table-condensed datatables">
  % if partitions:
    <tr>
      % for field in table.partition_keys:
        <th>${field.name}</th>
      % endfor
      <th>${_('Path')}</th>
    </tr>
    % for partition in partitions:
      <tr>
        % for key in partition.values:
          <td>${key}</td>
        % endfor
        <td>
          <% url = location_to_url(partition.sd.location) %>
          % if url:
            <a href="${url}">${partition.sd.location}</a>
          % else:
            ${partition.sd.location}
          % endif
        </td>
      </tr>
    % endfor
  % else:
    <tr><td>${_('Table has no partitions.')}</td></tr>
  % endif
</table>

</div>

${ commonfooter(messages) | n,unicode }

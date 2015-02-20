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

<%namespace name="components" file="components.mako" />

${ commonheader(_('Table Partitions: %(tableName)s') % dict(tableName=table.name), app_name, user) | n,unicode }
${ components.menubar() }

<div class="container-fluid">
  <div class="row-fluid">
    <div class="span3">
      <div class="sidebar-nav card-small">
        <ul class="nav nav-list">
          <li class="nav-header">${_('Actions')}</li>
          <li><a href="${ url('metastore:describe_table', database=database, table=table.name) }"><i class="fa fa-reply"></i> ${_('Show Table')}</a></li>
        </ul>
      </div>
    </div>
    <div class="span9">
      <div class="card card-small">
        <h1 class="card-heading simple">${ components.breadcrumbs(breadcrumbs) }</h1>
          <div class="card-body">
            <p>
          % if partitions:
          <table class="table table-striped table-condensed datatables">
          <tr>
          % for field in table.partition_keys:
              <th>${field.name}</th>
          % endfor
            <th>${_('Path')}</th>
          </tr>
          % for partition_id, partition in enumerate(partitions):
            <tr>
            % for idx, key in enumerate(partition.values):
                <td><a href="${ url('metastore:read_partition', database=database, table=table.name, partition_id=partition_id) }" data-row-selector="true">${key}</a></td>
            % endfor
            <% location = location_to_url(partition.sd.location) %>
            % if url:
                <td data-row-selector-exclude="true">
                  <a href="${location}">${partition.sd.location}</a>
                </td>
            % else:
                <td>
                ${partition.sd.location}
                </td>
            % endif
            </tr>
          % endfor
          </table>
          % else:
              <div class="alert">${_('The table %s has no partitions.' % table.name)}</div>
          % endif
              </p>
            </div>
        </div>
    </div>
  </div>
</div>

<link rel="stylesheet" href="${ static('metastore/css/metastore.css') }" type="text/css">

<script type="text/javascript" charset="utf-8">
  $(document).ready(function () {
    $("a[data-row-selector='true']").jHueRowSelector();
  });
</script>

${ commonfooter(messages) | n,unicode }

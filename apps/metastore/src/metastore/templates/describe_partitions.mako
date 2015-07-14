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
          <form id="partition-filter" class="card-body" data-bind="submit: filter">
            ${ _('Filter by ') }
            <div data-bind="foreach: filters">
              <select data-bind="options: $root.columns"></select>
              <input type="text" data-bind="value: value"></input>
              <a href="javascript: void(0)" data-bind="click: $root.removeFilter">
                <i class="fa fa-minus"></i>
              </a>
            </div>

            <a href="javascript: void(0)" data-bind="click: addFilter">
              <i class="fa fa-plus"></i> ${ _('Add ') }
            </a>
            
            ${ _('Sort') } <input type="checkbox" data-bind="checked: sortDesc"></input>
            
            <button type="submit">Filter</button>            
          <form>

          <div class="card-body">
            <p>
          % if partitions:
          <table class="table table-striped table-condensed datatables">
          <tr>
          % for field in table.partition_keys:
              <th>${field.name}</th>
          % endfor
              <th>${_('Location')}</th>
          </tr>
          % for partition_id, partition in enumerate(partitions):
            <tr>
            % for idx, key in enumerate(partition.values):
                <td><a href="${ url('metastore:read_partition', database=database, table=table.name, partition_id=partition_id) }" data-row-selector="true">${key}</a></td>
            % endfor
                <td><a href="${ url('metastore:browse_partition', database=database, table=table.name, partition_id=partition_id) }"><i class="fa fa-share-square-o"></i> ${_('View Partition Files')}</a></td>
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

<script src="${ static('desktop/ext/js/knockout.min.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/knockout-mapping.min.js') }" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript" charset="utf-8">
  var PartitionFilterViewModel = function (partitions_json, form_data_json) {
    var self = this;

    self.sortDesc = ko.mapping.fromJS(typeof form_data_json != "undefined" && form_data_json != null ? form_data_json.sortDesc : true)
    self.filters = ko.mapping.fromJS(typeof form_data_json != "undefined" && form_data_json != null ? form_data_json.filters : [])

    self.columns = ko.mapping.fromJS(partitions_json);

    self.addFilter = function() {
      self.filters.push(ko.mapping.fromJS({'column': '', 'value': ''}));
    }

    self.removeFilter = function(data) {
      self.filters.remove(data);
    }
    
    self.filter = function(data) {
      // jsonnify sortDesc, filter into some hidden form attribute
    }
  };

  var viewModel = new PartitionFilterViewModel(${ partition_names_json | n,unicode }, ${ form_data_json | n,unicode });
  ko.applyBindings(viewModel, $("#partition-filter")[0]);

  $(document).ready(function () {
    $("a[data-row-selector='true']").jHueRowSelector();
  });
</script>

${ commonfooter(messages) | n,unicode }

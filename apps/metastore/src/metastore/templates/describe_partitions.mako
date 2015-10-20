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

<%namespace name="components" file="components.mako" />

${ commonheader(_('Table Partitions: %(tableName)s') % dict(tableName=table.name), app_name, user) | n,unicode }
${ components.menubar() }

<div class="container-fluid" id="partitions">
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
          <div class="row-fluid">
            <div class="span10">
              <div data-bind="visible: filters().length > 0">
                <div data-bind="foreach: filters">
                    <div class="filter-box">
                      <a href="javascript:void(0)" class="pull-right" data-bind="click: $root.removeFilter">
                        <i class="fa fa-times"></i>
                      </a>
                      <select class="input-small" data-bind="options: $root.keys, value: column"></select>
                      &nbsp;
                      <input class="input-small" type="text" data-bind="value: value, typeahead: { target: value, source: $root.typeaheadValues(column), triggerOnFocus: true, forceUpdateSource: true}" placeholder="${ _('Value to filter...') }" />
                  </div>
                </div>
                <div class="pull-left" style="margin-top: 4px; margin-bottom: 10px">
                  <a class="add-filter" href="javascript: void(0)" data-bind="click: addFilter">
                    <i class="fa fa-plus"></i> ${ _('Add') }
                  </a>
                  <label class="checkbox inline pulled">${ _('Sort Desc') } <input type="checkbox" data-bind="checked: sortDesc" /></label>
                  <button class="btn" data-bind="click: filter"><i class="fa fa-filter"></i> ${ _('Filter') }</button>
                </div>
              </div>
              <a class="add-filter" href="javascript: void(0)" data-bind="click: addFilter, visible: values().length > 0 && filters().length == 0" style="margin-bottom: 20px; margin-left: 14px">
                <i class="fa fa-plus"></i> ${ _('Add a filter') }
              </a>
              <div class="clearfix"></div>
            </div>
            <div class="span2">
            % if has_write_access:
              <div class="pull-right">
                <button id="dropBtn" class="btn" title="${_('Delete the selected partitions')}" disabled="disabled"><i class="fa fa-trash-o"></i>  ${_('Drop partition(s)')}</button>
              </div>
            % endif
            </div>
          </div>

          <table class="table table-striped table-condensed datatables" data-bind="visible: values().length > 0, style:{'opacity': isLoading() ? '.5': '1' }">
            <tr>
              <th width="1%"><div class="hueCheckbox selectAll fa" data-selectables="partitionCheck"></div></th>
              <!-- ko foreach: keys -->
              <th data-bind="text: $data"></th>
              <!-- /ko -->
              <th>${_('Location')}</th>
            </tr>
            <!-- ko foreach: values -->
            <tr>
              <td data-row-selector-exclude="true" width="1%">
                <div class="hueCheckbox partitionCheck fa"
                       data-bind="attr:{'data-drop-name': partitionSpec}"
                       data-row-selector-exclude="true"></div>
              </td>
              <!-- ko foreach: $data.columns -->
              <td><a data-bind="attr:{'href': $parent.readUrl}, text:$data"></a></td>
              <!-- /ko -->
              <td><a data-bind="attr:{'href': browseUrl}"><i class="fa fa-share-square-o"></i> ${_('View Partition Files')}</a></td>
            </tr>
            <!-- /ko -->
          </table>
          <div class="alert" data-bind="visible: values().length == 0">${_('The table %s has no partitions.' % table.name)}</div>
        </div>
      </div>
    </div>
  </div>

  <div id="dropPartition" class="modal hide fade">
    <form id="dropPartitionForm" action="${ url('metastore:drop_partition', database=database, table=table.name) }" method="POST">
      ${ csrf_token(request) | n,unicode }
      <div class="modal-header">
        <a href="#" class="close" data-dismiss="modal">&times;</a>
        <h3 id="dropPartitionMessage">${_('Confirm action')}</h3>
      </div>
      <div class="modal-footer">
        <input type="button" class="btn" data-dismiss="modal" value="${_('Cancel')}" />
        <input type="submit" class="btn btn-danger" value="${_('Yes')}"/>
      </div>
      <select class="hide" name="partition_selection" data-bind="options: $root.availablePartitions, selectedOptions: $root.chosenPartitions" size="5" multiple="true"></select>
    </form>
  </div>
</div>

<link rel="stylesheet" href="${ static('metastore/css/metastore.css') }" type="text/css">

<script src="${ static('desktop/ext/js/knockout.min.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/knockout-mapping.min.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/js/ko.hue-bindings.js') }" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript" charset="utf-8">
  var PartitionFilterViewModel = function (partition_keys_json, partition_values_json) {
    var self = this;

    self.isLoading = ko.observable(false);

    self.sortDesc = ko.observable(true);
    self.filters = ko.observableArray([]);

    self.keys = ko.observableArray(partition_keys_json);
    self.values = ko.observableArray(partition_values_json);

    self.availablePartitions = ko.computed(function () {
      return ko.utils.arrayMap(partition_values_json, function (partition) {
        return partition.partitionSpec;
      });
    }, self);

    self.chosenPartitions = ko.observableArray([]);

    self.typeaheadValues = function (column) {
      var _vals = [];
      self.values().forEach(function (row) {
        var _cell = row.columns[self.keys().indexOf(column())];
        if (_vals.indexOf(_cell) == -1) {
          _vals.push(_cell);
        }
      });
      return _vals
    }

    self.addFilter = function () {
      self.filters.push(ko.mapping.fromJS({'column': '', 'value': ''}));
    }

    self.removeFilter = function (data) {
      self.filters.remove(data);
      if (self.filters().length == 0) {
        self.sortDesc(true);
        self.filter();
      }
    }

    self.filter = function () {
      self.isLoading(true);
      $("#dropBtn").attr("disabled", "disabled");
      var _filters = JSON.parse(ko.toJSON(self.filters));
      var _postData = {};
      _filters.forEach(function (filter) {
        _postData[filter.column] = filter.value;
      });
      _postData["sort"] = viewModel.sortDesc() ? "desc" : "asc";

      $.ajax({
        type: "POST",
        url: "/metastore/table/default/blog/partitions",
        data: _postData,
        success: function (data) {
          self.values(data.partition_values_json);
          self.isLoading(false);
        },
        dataType: "json"
      });
    }
  };

  var viewModel = new PartitionFilterViewModel(${ partition_keys_json | n,unicode }, ${ partition_values_json | n,unicode });
  ko.applyBindings(viewModel, $("#partitions")[0]);

  $(document).ready(function () {
    $("a[data-row-selector='true']").jHueRowSelector();

    $(".selectAll").on("click", function () {
      if ($(this).attr("checked")) {
        $(this).removeAttr("checked").removeClass("fa-check");
        $("." + $(this).data("selectables")).removeClass("fa-check").removeAttr("checked");
      }
      else {
        $(this).attr("checked", "checked").addClass("fa-check");
        $("." + $(this).data("selectables")).addClass("fa-check").attr("checked", "checked");
      }
      toggleActions();
    });

    $(document).on("click", ".partitionCheck", function () {
      if ($(this).attr("checked")) {
        $(this).removeClass("fa-check").removeAttr("checked");
      }
      else {
        $(this).addClass("fa-check").attr("checked", "checked");
      }
      $(".selectAll").removeAttr("checked").removeClass("fa-check");
      toggleActions();
    });

    function toggleActions() {
      $("#dropBtn").attr("disabled", "disabled");
      var selector = $(".hueCheckbox[checked='checked']");
      if (selector.length >= 1) {
        $("#dropBtn").removeAttr("disabled");
      }
    }

    $("#dropBtn").on("click", function () {
      $.getJSON("${ url('metastore:drop_partition', database=database, table=table.name) }", function (data) {
        $("#dropPartitionMessage").text(data.title);
      });
      var _tempList = [];
      $(".hueCheckbox[checked='checked']").each(function (index) {
        _tempList.push($(this).data("drop-name"));
      });
      viewModel.chosenPartitions.removeAll();
      viewModel.chosenPartitions(_tempList);
      $("#dropPartition").modal("show");
    });
  });

</script>

${ commonfooter(messages) | n,unicode }

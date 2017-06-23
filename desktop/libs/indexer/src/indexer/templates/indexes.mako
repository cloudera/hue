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
  from django.utils.translation import ugettext as _

  from desktop.views import commonheader, commonfooter, commonshare, commonimportexport
%>


<%namespace name="actionbar" file="actionbar.mako" />

${ commonheader(_("Index Browser"), "search", user, request, "60px") | n,unicode }


<script type="text/html" id="indexes-breadcrumbs">
  <ul class="nav nav-pills hue-breadcrumbs-bar" id="breadcrumbs">
    <li>
      <a href="javascript:void(0);" data-bind="click: function() { section('list-indexes'); }">${ _('Indexes') }
        <!-- ko if: index -->
        <span class="divider">&gt;</span>
        <!-- /ko -->
      </a>
    </li>
    <!-- ko with: index -->
    <li>
      <span data-bind="text: name"></span>
    </li>
    <!-- /ko -->
  </ul>
</script>

<div class="container-fluid">
  <div class="card card-small">
    <h1 class="card-heading simple">${ _('Index Browser') }</h1>

    <!-- ko template: { name: 'indexes-breadcrumbs' }--><!-- /ko -->

    <%actionbar:render>
      <%def name="search()">
        <input data-bind="clearable: indexFilter, value: indexFilter, valueUpdate: 'afterkeydown'" type="text" class="input-xlarge search-query" placeholder="${_('Search for name...')}">
      </%def>

      <%def name="actions()">
        <div class="btn-toolbar" style="display: inline; vertical-align: middle">
          <a data-bind="click: function() { atLeastOneSelected() ? $('#deleteIndex').modal('show') : void(0) }, css: {'btn': true, 'disabled': ! atLeastOneSelected() }">
            <i class="fa fa-times"></i> ${ _('Delete') }
          </a>
        </div>
      </%def>

      <%def name="creation()">
        <a href="javascript:void(0)" class="btn" data-bind="hueLink: '/indexer/importer/prefill/all/index/default'">
          <i class="fa fa-plus-circle"></i> ${ _('Create index') }
        </a>
        <a href="javascript:void(0)" class="btn" data-bind="click: function() { alias.showCreateModal(true); }">
          <i class="fa fa-plus-circle"></i> ${ _('Create alias') }
        </a>
      </%def>
    </%actionbar:render>

    <!-- ko template: { if: alias.showCreateModal(), name: 'create-alias' }--><!-- /ko -->
    <!-- ko template: { if: section() == 'list-indexes', name: 'list-indexes' }--><!-- /ko -->
    <!-- ko template: { if: section() == 'list-index', name: 'list-index', data: index() }--><!-- /ko -->
  </div>
</div>


<script type="text/html" id="list-indexes">
  <table class="table datatables">
    <thead>
      <tr>
        <th width="1%"><div data-bind="click: selectAll, css: {hueCheckbox: true, 'fa': true, 'fa-check': allSelected}" class="select-all"></div></th>
        <th>${ _('Name') }</th>
        <th>${ _('Type') }</th>
        <th>${ _('Collections') }</th>
      </tr>
    </thead>
    <tbody data-bind="foreach: {data: indexes}">
      <tr>
        <td data-bind="click: $root.handleSelect" class="center" style="cursor: default">
          <div data-bind="css: {'hueCheckbox': true, 'fa': true, 'fa-check': isSelected}"></div>
        </td>
        <td data-bind="text: name, click: function() { $root.fetchIndex(name()); }"></td>
        <td data-bind="text: type"></td>
        <td>
          <span data-bind="text: collections"></span>
          <a data-bind="click: $root.alias.edit, visible: type() == 'alias'">
            <i class="fa fa-pencil"></i> ${ _('Edit') }
          </a>
        </td>
      </tr>
    </tbody>
  </table>
</script>


<script type="text/html" id="list-index">
  <div class="pull-right">
    <a class="inactive-action" data-bind="hueLink: '/search/browse/' + name(), tooltip: { placement: 'bottom', delay: 750 }" title="${_('Search the index')}" href="javascript:void(0)">
      <i class="fa fa-search fa-fw"></i>
    </a>

    <a class="inactive-action" data-bind="tooltip: { placement: 'bottom', delay: 750 }" title="${_('Refresh')}" href="javascript:void(0)">
      <i class="pointer fa fa-refresh fa-fw"></i>
    </a>

    <a class="inactive-action" href="javascript:void(0)" data-bind="tooltip: { placement: 'bottom', delay: 750 }" title="${_('Index Data')}">
      <i class="fa fa-upload fa-fw"></i>
    </a>

    <a class="inactive-action" href="javascript:void(0)" data-toggle="modal" data-bind="tooltip: { placement: 'bottom', delay: 750 }">
      <i class="fa fa-times fa-fw"></i>
    </a>
  </div>


  <div class="clearfix"></div>

  <ul class="nav nav-pills margin-top-30">
    <li class="active"><a href="#index-overview" data-toggle="tab" data-bind="click: function(){ $root.tab('index-overview'); }">${_('Overview')}</a></li>
    <li><a href="#index-columns" data-toggle="tab" data-bind="click: function(){ $root.tab('index-columns'); }">${_('Fields')} (<span data-bind="text: fields().length"></span>)</a></li>
    <li><a href="#index-sample" data-toggle="tab" data-bind="click: function(){ $root.tab('index-sample'); }">${_('Sample')}</a></li>
  </ul>

  <div class="tab-content margin-top-10" style="border: none; overflow: hidden">
    <div class="tab-pane active" id="index-overview">
      <!-- ko template: { if: $root.tab() == 'index-overview', name: 'indexes-index-overview' }--><!-- /ko -->
    </div>

    <div class="tab-pane" id="index-columns">
      <!-- ko if: $root.tab() == 'index-columns' -->
        <input class="input-xlarge search-query margin-left-10" type="text" placeholder="${ _('Search for a column...') }" data-bind="clearable: $root.columnFilter, value: $root.columnFilter, valueUpdate: 'afterkeydown'"/>
        <!-- ko template: 'indexes-index-fields' --><!-- /ko -->
      <!-- /ko -->
    </div>

    <div class="tab-pane" id="index-sample">
      <!-- ko template: { if: $root.tab() == 'index-sample', name: 'indexes-index-sample', data: sample() }--><!-- /ko -->
    </div>
  </div>
</script>


<script type="text/html" id="indexes-index-overview">
  <div>
    Overview

    <!-- ko template: 'indexes-index-properties' --><!-- /ko -->

    <!-- ko template: { name: 'indexes-index-fields-fields', data: fieldsPreview }--><!-- /ko -->
    <a class="pointer" data-bind="visible: fields().length > fieldsPreview().length, click: function() { $('li a[href=\'#index-columns\']').click(); }">
      ${_('View more...')}
    </a>

    <!-- ko template: { name: 'indexes-index-sample', data: samplePreview }--><!-- /ko -->
    <a class="pointer" data-bind="visible: sample().length > samplePreview().length, click: function() { $('li a[href=\'#index-sample\']').click(); }">
      ${_('View more...')}
    </a>
  </div>
</script>


<script type="text/html" id="indexes-index-properties">
  <h4>${ _('Properties') }</h4>
  <div class="row-fluid">
    <div title="${ _('Unique Key') }">
      <i class="fa fa-fw fa-key muted"></i> <span data-bind="text: uniqueKey"></span>
    </div>
  </div>
</script>


<script type="text/html" id="indexes-index-fields-fields">
  <div>
    Fields

    <table id="indexTable" class="table datatables">
      <thead>
        <tr>
          <th style="width: 1%">&nbsp;</th>
          <th width="1%"></th>
          <th></th>
          <th>${ _('Name') }</th>
          <th>${ _('Type') }</th>
          <th>${ _('Required') }</th>
          <th>${ _('Stored') }</th>
          <th>${ _('Indexed') }</th>
          <th>${ _('Multivalued') }</th>
        </tr>
      </thead>
      <tbody data-bind="foreach: $data">
        <tr>
          <td data-bind="text: $index() + 1"></td>
          <td>
            <i class="fa fa-info muted pointer analysis"></i>
          </td>
          <td>
            <div></div>
          </td>
          <td data-bind="text: name"></td>
          <td data-bind="text: type"></td>
          <td><i data-bind="visible: $data.required" class="fa fa-check muted"></i></td>
          <td><i data-bind="visible: $data.stored" class="fa fa-check muted"></i></td>
          <td><i data-bind="visible: indexed" class="fa fa-check muted"></i></td>
          <td><i data-bind="visible: $data.multiValued" class="fa fa-check muted"></i></td>
        </tr>
      </tbody>
    </table>
  </div>
</script>


<script type="text/html" id="indexes-index-fields">
  <div>
    <!-- ko template: { name: 'indexes-index-fields-fields', data: fields }--><!-- /ko -->

    Copy Fields
    <span data-bind="text: ko.mapping.toJSON(copyFields)"></span>


    Dynamic Fields
    <span data-bind="text: ko.mapping.toJSON(dynamicFields)"></span>
  </div>
</script>


<script type="text/html" id="indexes-index-sample">
  <div>
    Sample

    <a data-bind="click: $root.index().getSample">Load</a>

    <table class="table table-condensed table-nowrap sample-table">
      <thead>
        <tr>
          <th style="width: 1%">&nbsp;</th>
          <!-- ko foreach: $root.index().fields() -->
          <th data-bind="text: name"></th>
          <!-- /ko -->
        </tr>
      </thead>
      <tbody>
        <!-- ko foreach: $data -->
          <tr>
            <td data-bind="text: $index() + 1"></td>
            <!-- ko foreach: $root.index().fields() -->
              <td data-bind="text: $parent[name()]"></td>
            <!-- /ko -->
          </tr>
        <!-- /ko -->
      </tbody>
    </table>
  </div>
</script>


<script type="text/html" id="create-alias">
  <div class="snippet-settings">

    <input type="text" data-bind="value: alias.name"/>
    <select data-bind="options: alias.availableCollections, selectedOptions: alias.chosenCollections, optionsText: 'name', optionsValue: 'name'" size="5" multiple="true"></select>

    <a href="javascript:void(0)" class="btn" data-bind="click: alias.create, visible: alias.chosenCollections().length > 0">
      <i class="fa fa-plus-circle"></i> ${ _('Create') }
    </a>
    <a href="javascript:void(0)" class="btn" data-bind="click: function() { alias.showCreateModal(false) }">
      <i class="fa fa-plus-circle"></i> ${ _('Cancel') }
    </a>
  </div>
</script>


<div class="hueOverlay" data-bind="visible: isLoading">
  <i class="fa fa-spinner fa-spin big-spinner"></i>
</div>


<div id="deleteIndex" class="modal hide fade">
  <form id="deleteIndexForm" method="POST" data-bind="submit: deleteIndexes">
    ${ csrf_token(request) | n,unicode }
    <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
      <h2 id="deleteIndexMessage" class="modal-title">${ _('Delete the selected index(es)?') }</h2>
    </div>
    <div class="modal-footer">
      <a href="#" class="btn" data-dismiss="modal">${ _('No') }</a>
      <input type="submit" class="btn btn-danger" value="${ _('Yes') }"/>
    </div>
  </form>
</div>



<script type="text/javascript">

  var Alias = function (vm) {
    var self = this;

    self.showCreateModal = ko.observable(false);

    self.name = ko.observable('');
    self.chosenCollections = ko.observableArray();
    self.availableCollections = ko.computed(function() {
      return $.grep(vm.indexes(), function(index) { return index.type() == 'collection'; });
    });

    self.create = function() {
      $.post("${ url('indexer:create_alias') }", {
        "alias": self.name,
        "collections": ko.mapping.toJSON(self.chosenCollections)
      }, function() {
        window.location.reload();
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
      });
    }

    self.edit = function(alias) {
      self.name(alias.name());
      self.chosenCollections(alias.collections());

      self.showCreateModal(true);
    }
  };


  var Index = function (vm, data) {
    var self = this;

    self.name = ko.observable(data.name);
    self.uniqueKey = ko.observable(data.schema.uniqueKey);
    self.fields = ko.mapping.fromJS(data.schema.fields);
    self.fieldsPreview = ko.pureComputed(function() {
      return self.fields().splice(0, 5)
    });
    self.dynamicFields = ko.mapping.fromJS(data.schema.dynamicFields);
    self.copyFields = ko.mapping.fromJS(data.schema.copyFields);

    self.sample = ko.observableArray();
    self.samplePreview = ko.pureComputed(function() {
      return self.sample().splice(0, 5)
    });

    self.getSample = function() {
      $.post("${ url('indexer:sample_index') }", {
        name: self.name(),
        rows: 100
      }, function(data) {
        if (data.status == 0) {
          self.sample(data.sample)
        } else {
          $(document).trigger("error", data.message);
        }
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
      });
    };
  };


  var Editor = function () {
    var self = this;

    self.section = ko.observable('list-indexes');
    self.tab = ko.observable('');

    self.indexes = ko.observable([]);
    self.alias = new Alias(self);
    self.index = ko.observable();

    self.indexFilter = ko.observable('');
    self.columnFilter = ko.observable('');

    self.selectedIndexes = ko.computed(function() {
      return $.grep(self.indexes(), function(index) { return index.isSelected(); });
    });
    self.isLoading = ko.observable(false);

    self.oneSelected = ko.computed(function() {
      return self.selectedIndexes().length == 1;
    });
    self.atLeastOneSelected = ko.computed(function() {
      return self.selectedIndexes().length >= 1;
    });
    self.allSelected = ko.observable(false);

    self.handleSelect = function(index) {
      index.isSelected(! index.isSelected());
    }

    self.selectAll = function() {
      self.allSelected(! self.allSelected());
      ko.utils.arrayForEach(self.indexes(), function (index) {
        index.isSelected(self.allSelected());
      });
    }

    self.datatable = null;

    self.fetchIndexes = function() {
      $.post("${ url('indexer:list_indexes') }", {
      }, function(data) {
        if (data.status == 0) {
          var indexes = []
          data.collections.forEach(function(index) {
            index.isSelected = false;
            indexes.push(ko.mapping.fromJS(index));
          });
          self.indexes(indexes);
        } else {
          $(document).trigger("error", data.message);
        }
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
      });
    };

    self.fetchIndex = function(name) {
      $.post("${ url('indexer:list_index') }", {
        name: name
      }, function(data) {
        if (data.status == 0) {
          self.index(new Index(self, data));
          self.section('list-index');
          self.tab('index-overview');
        } else {
          $(document).trigger("error", data.message);
        }
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
      });
    };

    self.deleteIndexes = function() {
      $.post("${ url('indexer:delete_indexes') }", {
        "indexes": ko.mapping.toJSON(self.selectedIndexes)
      }, function() {
        if (data.status == 0) {
          window.location.reload();
        } else {
          $(document).trigger("error", data.message);
        }
        $('#deleteIndex').modal('hide');
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
      });
    };
  };

  var viewModel;

  $(document).ready(function () {
    viewModel = new Editor();
    ko.applyBindings(viewModel);

    viewModel.fetchIndexes();
  });
</script>

${ commonfooter(request, messages) | n,unicode }

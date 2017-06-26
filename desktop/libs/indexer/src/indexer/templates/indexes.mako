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
  from desktop.views import commonheader, commonfooter, commonshare, commonimportexport
  from django.utils.translation import ugettext as _
%>
<%namespace name="actionbar" file="actionbar.mako" />

${ commonheader(_("Solr Indexes"), "search", user, request, "60px") | n,unicode }


<div class="container-fluid">
  <div class="card card-small">
  <h1 class="card-heading simple">${ _('Solr Indexes') }</h1>

  <%actionbar:render>
    <%def name="search()">
      <input id="filterInput" type="text" class="input-xlarge search-query" placeholder="${_('Search for name, description, etc...')}">
    </%def>

    <%def name="actions()">
      <div class="btn-toolbar" style="display: inline; vertical-align: middle">
        <a data-bind="click: function() { atLeastOneSelected() ? $('#deleteIndex').modal('show') : void(0) }, css: {'btn': true, 'disabled': ! atLeastOneSelected() }">
          <i class="fa fa-times"></i> ${ _('Delete') }
        </a>
      </div>
    </%def>

    <%def name="creation()">
      <a href="javascript:void(0)" class="btn" data-bind="click: function() { index.showCreateModal(true) }">
        <i class="fa fa-plus-circle"></i> ${ _('Create index') }
      </a>
      <a href="javascript:void(0)" class="btn" data-bind="click: function() { createWizard.show(true) }">
        <i class="fa fa-plus-circle"></i> ${ _('Create index from a file') }
      </a>      
      <a href="javascript:void(0)" class="btn" data-bind="click: function() { alias.showCreateModal(true) }">
        <i class="fa fa-plus-circle"></i> ${ _('Create alias') }
      </a>
    </%def>
  </%actionbar:render>


  <table id="indexTable" class="table datatables">
    <thead>
      <tr>
        <th width="1%"><div data-bind="click: selectAll, css: {hueCheckbox: true, 'fa': true, 'fa-check': allSelected}" class="select-all"></div></th>
        <th>${ _('Name') }</th>
        <th>${ _('Type') }</th>
        <th>${ _('Collections') }</th>
        <th>${ _('Schema') }</th>
      </tr>
    </thead>
    <tbody data-bind="foreach: { data: indexes }">
      <tr>
        <td data-bind="click: $root.handleSelect" class="center" style="cursor: default" data-row-selector-exclude="true">
          <div data-bind="css: { 'hueCheckbox': true, 'fa': true, 'fa-check': isSelected }" data-row-selector-exclude="true"></div>
          ## <a data-bind="attr: { 'href': '${ url('search:index') }?index=' + id() }" data-row-selector="true"></a>
        </td>
        <td data-bind="text: name"></td>
        <td data-bind="text: type"></td>
        <td>
          <span data-bind="text: collections"></span>
          <a data-bind="click: $root.alias.edit, visible: type() == 'alias'">
            <i class="fa fa-pencil"></i> ${ _('Edit') }
          </a>
        </td>
        <td>
          <a data-bind="attr: { 'href': '/indexer/api/indexes/' + name() + '/schema/' }, visible: type() == 'collection'">
            <i class="fa fa-pencil"></i> ${ _('Edit') }
          </a>
        </td>
      </tr>
    </tbody>
  </table>

  </div>
</div>

<!-- ko template: 'create-index' --><!-- /ko -->

<script type="text/html" id="create-index">
  <div class="snippet-settings" data-bind="visible: index.showCreateModal">

    <input type="text" data-bind="value: index.name"/>

    <a href="javascript:void(0)" class="btn" data-bind="click: index.create">
      <i class="fa fa-plus-circle"></i> ${ _('Create index') }
    </a>
    <a href="javascript:void(0)" class="btn" data-bind="click: function() { index.showCreateModal(false) }">
      <i class="fa fa-plus-circle"></i> ${ _('Cancel') }
    </a>
  </div>
</script>


<!-- ko template: 'create-alias' --><!-- /ko -->

<script type="text/html" id="create-alias">
  <div class="snippet-settings" data-bind="visible: alias.showCreateModal">

    <input type="text" data-bind="value: alias.name"/>
    <select data-bind="options: alias.availableCollections, selectedOptions: alias.chosenCollections, optionsText: 'name', optionsValue: 'name'" size="5" multiple="true"></select>

    <a href="javascript:void(0)" class="btn" data-bind="click: alias.create, visible: alias.chosenCollections().length > 0">
      <i class="fa fa-plus-circle"></i> ${ _('Create or edit') }
    </a>
    <a href="javascript:void(0)" class="btn" data-bind="click: function() { alias.showCreateModal(false) }">
      <i class="fa fa-plus-circle"></i> ${ _('Cancel') }
    </a>
  </div>
</script>


<!-- ko template: 'create-index-wizard' --><!-- /ko -->

<script type="text/html" id="create-index-wizard">
  <div class="snippet-settings" data-bind="visible: createWizard.show">

    ${ _('Name') } <input type="text" data-bind="value: createWizard.name"/>
    
    <!-- ko if: createWizard.name() -->
    <select data-bind="options: createWizard.availableWizards, value: createWizard.wizard, optionsText: 'name'" size="5"></select>

    <span data-bind="template: { name: 'create-index-from-file', data: createWizard.wizard }"></span>
    <span data-bind="template: { name: 'create-index-from-hive', data: createWizard.wizard }"></span>
    
    <ul data-bind="foreach: createWizard.wizard().sample">
      <li>
        <div data-bind="foreach: $data">
          <span data-bind="text: $data"></span>
        </div>
        <a rel="tooltip" data-placement="bottom" data-bind="css: {'btn': true}" class="btn" data-original-title="Edit">
          <i class="fa fa-pencil"></i>
        </a>
      </li>
    </ul>

    <a href="javascript:void(0)" class="btn" data-bind="click: createWizard.getSample">
      <i class="fa fa-list-alt"></i> ${ _('Get Sample') }
    </a>

    <!-- /ko -->

    <br/>

    <a href="javascript:void(0)" class="btn" data-bind="visible: createWizard.showCreate, click: createWizard.create">
      <i class="fa fa-plus-circle"></i> ${ _('Create') }
    </a>
    <a href="javascript:void(0)" class="btn" data-bind="click: function() { createWizard.show(false) }">
      <i class="fa fa-plus-circle"></i> ${ _('Cancel') }
    </a>
  </div>
</script>


<script type="text/html" id="create-index-from-file">
  <!-- ko if: name() == 'file' -->
    <div class="snippet-settings" data-bind="visible: show">

      ${ _('Path') } <input type="text" data-bind="value: path"/>
      <select data-bind="visible: path, options: availableFormats, value: format" size="5"></select>

    </div>
  <!-- /ko -->
</script>


<script type="text/html" id="create-index-from-hive">
  <!-- ko if: name() == 'hive' -->
    <div class="snippet-settings" data-bind="visible: show">

      ${ _('Database') } <input type="text" data-bind="value: database"/>
      ${ _('Table') } <input type="text" data-bind="value: table"/>

    </div>
  <!-- /ko -->
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


<script src="${ static('desktop/ext/js/datatables-paging-0.1.js') }" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript">
  var Index = function () {
    var self = this;

    self.showCreateModal = ko.observable(false);

    self.name = ko.observable('');

    self.create = function() {
      $.post("${ url('indexer:create_index') }", {
        "name": self.name
      }, function() {
        window.location.reload();
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
      });
    }
  };

  var Alias = function (vm) {
    var self = this;

    self.showCreateModal = ko.observable(false);

    self.name = ko.observable('');
    self.chosenCollections = ko.observableArray();
    self.availableCollections = ko.computed(function() {
      return $.grep(vm.indexes(), function(index) { return index.type() == 'collection'; });
    });

    self.create = function() {
      $.post("${ url('indexer:create_or_edit_alias') }", {
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

  var FileWizard = function (vm) {
    var self = this;

    self.name = ko.observable('file');
    self.sample = ko.observableArray();
    self.show = ko.observable(false);

    self.path = ko.observable('');
    self.format = ko.observable('csv');
    self.availableFormats = ko.observableArray(['csv', 'log', 'apache logs', 'mailbox']);
  };

  var HiveWizard = function (vm) {
    var self = this;

    self.name = ko.observable('hive');
    self.show = ko.observable(false);

    self.database = ko.observable('');
    self.table = ko.observable('');
  };

  var CreateWizard = function (vm) {
    var self = this;

    self.show = ko.observable(false);
    self.showCreate = ko.observable(false);
    
    self.fileWizard = new FileWizard(vm);
    self.hiveWizard = new HiveWizard(vm);    

    self.name = ko.observable('');
    self.wizard = ko.observable();
    self.wizard.subscribe(function(val) {
      val.show(true);
    });
    self.wizard(self.fileWizard);
    self.availableWizards = ko.observableArray([self.fileWizard, self.hiveWizard]);

    self.getSample = function() {
      $.post("${ url('indexer:create_wizard_get_sample') }", {
        "wizard": ko.mapping.toJSON(self.wizard)
      }, function(resp) {
        self.wizard().sample(resp.data);
        self.showCreate(true);
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
      });
    }

    self.create = function() {
      $.post("${ url('indexer:create_wizard_create') }", {
        "wizard": ko.mapping.toJSON(self.wizard)
      }, function(resp) {
        self.wizard().sample(resp.data);
        self.showCreate(true);
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
      });
    }

    self.edit = function() {
      self.show(true);
    }
  };

  var Editor = function () {
    var self = this;

    self.indexes = ko.mapping.fromJS(${ indexes_json | n });

    self.index = new Index(self);
    self.alias = new Alias(self);
    self.createWizard = new CreateWizard(self);

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

    self.deleteIndexes = function() {
      $.post("${ url('indexer:delete_indexes') }", {
        "indexes": ko.mapping.toJSON(self.selectedIndexes)
      }, function() {
        window.location.reload();
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

    var oTable = $("#indexTable").dataTable({
      "sPaginationType":"bootstrap",
      'iDisplayLength':50,
      "bLengthChange":false,
      "sDom": "<'row'r>t<'row-fluid'<'dt-pages'p><'dt-records'i>>",
      "aoColumns":[
        { "bSortable":false },
        null,
        null,
        null,
        { "bSortable":false },
      ],
      "aaSorting":[
        [1, 'asc' ]
      ],
      "oLanguage":{
        "sEmptyTable":"${_('No data available')}",
        "sInfo":"${_('Showing _START_ to _END_ of _TOTAL_ entries')}",
        "sInfoEmpty":"${_('Showing 0 to 0 of 0 entries')}",
        "sInfoFiltered":"${_('(filtered from _MAX_ total entries)')}",
        "sZeroRecords":"${_('No matching records')}",
        "oPaginate":{
          "sFirst":"${_('First')}",
          "sLast":"${_('Last')}",
          "sNext":"${_('Next')}",
          "sPrevious":"${_('Previous')}"
        },
        "bDestroy": true
      },
      "fnDrawCallback":function (oSettings) {
        $("a[data-row-selector='true']").jHueRowSelector();
      }
    });

    viewModel.datatable = oTable;

    $("#filterInput").keydown(function (e) {
      if (e.which == 13) {
        e.preventDefault();
        return false;
      }
    });

    $("#filterInput").keyup(function () {
      oTable.fnFilter($(this).val());
    });

    $("a[data-row-selector='true']").jHueRowSelector();
  });
</script>


${ commonfooter(request, messages) | n,unicode }

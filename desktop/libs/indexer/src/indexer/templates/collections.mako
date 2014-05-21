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

<%namespace name="macros" file="macros.mako" />
<%namespace name="actionbar" file="actionbar.mako" />

${ commonheader(_('Collection Manager'), "indexer", user, "29px") | n,unicode }

<link rel="stylesheet" href="/static/ext/chosen/chosen.min.css">
<link rel="stylesheet" href="/indexer/static/css/admin.css">
<style type="text/css">
.hueBreadcrumb {
  padding: 12px 14px;
}

.hueBreadcrumbBar {
  padding: 0;
  margin: 12px;
}

.hueBreadcrumbBar a {
  color: #338BB8 !important;
  display: inline !important;
}

.divider {
  color: #CCC;
}

.sidebar-nav {
  padding: 0;
}

.card-heading {
  padding-left: 6px !important;
  border-bottom: none !important;
}
</style>


<div class="search-bar" style="height: 30px">  
  <div>
    <div class="pull-right" style="padding-right:50px">  
      <a class="btn" href="${ url('search:admin_collections') }" title="${ _('Collections') }" rel="tooltip" data-placement="bottom" data-bind="css: {'btn': true}">
        <i class="fa fa-tags"></i> ${ _('Dashboards') }
      </a>
    </div>  
    <h4><a href="#manage">${_('Solr Indexer')}</a></h4>
  </div>
</div>


<div class="container-fluid">
  <div class="row-fluid" data-bind="visible: isLoading()">
    <div class="span12">
      <div class="card">
        <div class="card-body offset1 center">
          <i class="fa fa-spinner fa-spin" style="font-size: 60px; color: #DDD"></i>
          <br />
          <br />
          <br />
        </div>
      </div>
    </div>
  </div>
  <div data-bind="template: {'name': page, if: !isLoading() && !!page()}" class="row-fluid" id="page"></div>
</div>


<div id="chooseFile" class="modal hide fade">
  <div class="modal-header">
    <a href="#" class="close" data-dismiss="modal">&times;</a>
    <h3>${_('Choose a file')}</h3>
  </div>
  <div class="modal-body">
    <div id="filechooser">
    </div>
  </div>
  <div class="modal-footer">
  </div>
</div>


<!-- Breadcrum component -->
<script id="breadcrum" type="text/html">
<ul data-bind="foreach: breadcrum.list" class="nav nav-pills hueBreadcrumbBar">
  <li class="nowrap">
    <!-- ko if: $index() == ( $root.breadcrum.list().length - 1 ) -->
    <span data-bind="text: label" style="padding-left:12px"></span>
    <!-- /ko -->
    <!-- ko if: $index() != ( $root.breadcrum.list().length - 1 ) -->
    <a data-bind="routie: url, text: label" href="javascript:void(0)"></a>
    <span class="divider">&gt;</span>
    <!-- /ko -->
  </li>
</ul>
</script>
<!-- /Breadcrum component -->


<!-- Manage collections page -->
<script id="manage-page" type="text/html">
<div class="span12" >
  <div class="card wizard">
    <div class="card-heading simple" data-bind="template: { 'name': 'breadcrum', 'data': $root, 'if': manage.collections().length != 0 }"></div>
    <div class="card-body" data-bind="with: manage">
      <%actionbar:render>
        <%def name="search()">
          <div data-bind="visible: collections().length > 0 && !isLoading()">
            <input type="text" data-bind="filter: { 'list': collections, 'filteredList': filteredCollections, 'test': filterTest }"
                placeholder="${_('Filter collections...')}" class="input-xlarge search-query">
            <button data-bind="click: removeCollections, clickBubble: false, disable: selectedCollections().length == 0" class="btn toolbarBtn" 
                title="${_('Delete the selected collections')}" disabled="disabled">
              <i class="fa fa-times"></i> ${_('Delete')}
            </button>
            <a href="#create" class="btn toolbarBtn pull-right">
              <i class="fa fa-plus-circle"></i> ${_('Create')}
            </a>
          </div>
        </%def>

        <%def name="creation()"></%def>
      </%actionbar:render>

      <div class="row-fluid" data-bind="visible: collections().length == 0 && !isLoading()">
        <div class="span10 offset1 center importBtn" style="cursor: pointer">
          <i class="fa fa-plus-circle waiting"></i>
          <h1 class="emptyMessage">${ _('There are currently no collections defined.') }<br/><a href="#create">${ _('Click here to add') }</a> ${ _('one or more.') }</h1>
        </div>
      </div>
      <div class="row-fluid" data-bind="visible: collections().length > 0 && !isLoading()">
        <div class="span12">
          <table class="table table-condensed">
            <thead>
              <tr>
                <th>
                  <span data-bind="click: toggleSelectAll, css: {'fa-check': !ko.utils.arrayFilter(filteredCollections(), function(collection) {return !collection.selected()}).length}" class="hueCheckbox fa"></span>
                </th>
                <th width="100%">${_('Name')}</th>
              </tr>
            </thead>
            <tbody data-bind="foreach: filteredCollections">
              <tr data-bind="routie: 'edit/' + name()" class="pointer">
                <td data-bind="click: $parent.toggleCollectionSelect.bind($parent), clickBubble: false">
                  <span data-bind="css: {'fa-check': $parent.filteredCollections()[$index()].selected()}" class="hueCheckbox fa"></span>
                </td>
                <td data-bind="text: name" style="cursor: pointer"></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</div>
</script>
<!--/ Manage collections page -->

<!-- Create by file -->
<script id="create-page" type="text/html">
<div class="span12">
  <div class="card wizard">
    <div class="card-heading simple" data-bind="template: { 'name': 'breadcrum', 'data': $root }"></div>
    <div class="card-body" data-bind="with: create">
      <form data-bind="if: wizard.currentPage()" class="form form-horizontal">
        <div data-bind="template: { 'name': wizard.currentPage().name, 'afterRender': afterRender}"></div>
        <br style="clear:both" />
        <br style="clear:both" />
        <a data-bind="routie: 'create/wizard/' + wizard.previousUrl(), visible: wizard.hasPrevious" class="btn btn-info" href="javascript:void(0)">${_('Previous')}</a>
        <a data-bind="routie: 'create/wizard/' + wizard.nextUrl(), visible: wizard.hasNext" class="btn btn-info" href="javascript:void(0)">${_('Next')}</a>
        <a data-bind="click: save, visible: !wizard.hasNext()" class="btn btn-info" href="javascript:void(0)">${_('Finish')}</a>
      </form>
    </div>
  </div>
</div>
</script>

<!-- Create wizard -->
<script type="text/html" id="create-collection-data">
  <div class="alert alert-info">
    ${ _('Pick a name and a CSV or Tab separated file with header to index from HDFS') }
  </div>
  <div class="control-group" data-bind="css: {'error': collection.name.errors().length > 0}">
    <label for="name" class="control-label">${_("Name")}</label>
    <div class="controls">
      <input data-bind="value: collection.name" name="name" type="text" placeholder="${_('Name of collection')}" />
    </div>
  </div>

  <div class="control-group" data-bind="css: {'error': file.errors().length > 0}">
    <label for="name" class="control-label">${_("Files")}</label>
    <div class="controls">
      <input data-bind="value: file" type="text" class="input-xxlarge fileChooser" placeholder="/user/hue/data.csv"/>
    </div>
  </div>

  <div class="control-group hide" data-bind="css: {'error': sourceType.errors().length > 0}">
    <label for="name" class="control-label">${_("Source type")}</label>
    <div class="controls">
      <select data-bind="options: sourceTypes, value: sourceType" name="type"></select>
    </div>
  </div>
</script>

<script type="text/html" id="create-collection-data-separated">
  <div class="alert alert-info">
    ${ _('Format of the selected file to index') }
  </div>
  <div class="control-group" data-bind="css: {'error': fieldSeparator.errors().length > 0}">
    <label for="separator" class="control-label">${_("Separator")}</label>
    <div class="controls">
      <select data-bind="options: fieldSeparators, optionsText: getCharacterLabel, value: fieldSeparator" name="separator"></select>
    </div>
  </div>

  <div class="control-group" data-bind="css: {'error': fieldQuoteCharacter.errors().length > 0}">
    <label for="quote" class="control-label">${_("Quote character")}</label>
    <div class="controls">
      <select data-bind="options: fieldQuoteCharacters, value: fieldQuoteCharacter" name="quote"></select>
    </div>
  </div>
</script>

<script type="text/html" id="create-collection-data-morphlines">
  <div class="control-group" data-bind="css: {'error': morphlines.name.errors().length > 0}">
    <label for="name" class="control-label">${_("Morphlines config name")}</label>

    <div class="controls">
      <input type="text" data-bind="value: morphlines.name" class="span6">
    </div>
  </div>

  <div class="control-group" data-bind="css: {'error': morphlines.expression.errors().length > 0}">
    <label for="name" class="control-label">${_("Morphlines config expression")}</label>

    <div class="controls">
      <textarea data-bind="value: morphlines.expression" placeholder="%{SYSLOGTIMESTAMP:timestamp} %{SYSLOGHOST:hostname} %{DATA:program}(?:\[%{POSINT:pid}\])?: %{GREEDYDATA:msg}" class="span12"></textarea>
    </div>
  </div>
</script>

<script type="text/html" id="create-collection-fields">
  <table class="table">
    <thead>
      <tr>
        <th width="25%" class="nowrap">${_('Name')}</th>
        <th width="25%" class="nowrap">${_('Type')}</th>
        <th width="0%" class="nowrap">${_('Required')}</th>
        <th width="0%" class="nowrap">${_('Indexed')}</th>
        <th width="0%" class="nowrap">${_('Stored')}</th>
        <th width="0%" class="nowrap">${_('Unique Key')}</th>
        <th width="50%"></th>
      </tr>
    </thead>
    <tbody data-bind="foreach: collection.fields">
      <tr data-bind="css: {'error': name.errors().length > 0}" class="editable">
        <td data-bind="editableText: name">
          <span class="pull-left fa fa-pencil"></span>
        </td>
        <td><select data-bind="options: $parent.fieldTypes, value: type, chosen: {}" name="type"></select></td>
        <td><p class="text-center"><input data-bind="checked: required" type="checkbox"></p></td>
        <td><p class="text-center"><input data-bind="checked: indexed" type="checkbox"></p></td>
        <td><p class="text-center"><input data-bind="checked: stored" type="checkbox"></p></td>
        <td>
          <p class="text-center">
            <input data-bind="checked: uniqueKeyField, visible: !uniqueKeyField()" name="unique-key" type="checkbox" />
            <span class="fa" data-bind="css: {'fa-check': uniqueKeyField}">
          </p>
        </td>
        <td>
          <a data-bind="click: remove, visible: editable" href="javascript:void(0)" class="btn"><i class="fa fa-minus"></i></a>
        </td>
      </tr>
    </tbody>
  </table>

  <br style="clear: both" />
  <br />
  <a data-bind="click: collection.newField" href="javascript:void(0)" class="btn btn-info"><i class="fa fa-plus"></i>&nbsp;${_("Add")}</a>
</script>
<!--/ Create wizard -->
<!--/ Create by file -->

<!-- Edit collection page -->
<script id="edit-page" type="text/html">
<div class="span3">
  <div data-bind="with: edit" class="sidebar-nav card-small">
    <ul class="nav nav-list">
      <li class="nav-header">${_('Actions')}</li>
      <li><a data-bind="attr: { href: '/search/browse/' + collection().name() }"><i class="fa fa-search"></i> ${ _('Search') }</a></li>
      <li><a data-bind="routie: 'edit/' + collection().name() + '/upload'" href="javascript:void(0)"><i class="fa fa-folder-open-o"></i> ${_('Index file')}</a></li>      
      <li><a data-bind="click: removeCollection, clickBubble: false" href="javascript:void(0)"><i class="fa fa-times"></i> ${_('Delete')}</a></li>
    </ul>
  </div>
</div>
<div class="span9">
  <div class="card wizard">
    <div class="card-heading simple" data-bind="template: { 'name': 'breadcrum', 'data': $root }"></div>
    <div data-bind="with: edit"  class="card-body">
      <form class="form">
        <table class="table">
          <thead>
            <tr>
              <th width="25%" class="nowrap">${_('Name')}</th>
              <th width="25%" class="nowrap">${_('Type')}</th>
              <th width="0%" class="nowrap">${_('Unique key field')}</th>
              <th width="0%" class="nowrap">${_('Required')}</th>
              <th width="0%" class="nowrap">${_('Indexed')}</th>
              <th width="0%" class="nowrap">${_('Stored')}</th>
              <th width="50%"></th>
            </tr>
          </thead>
          <tbody data-bind="foreach: ko.utils.arrayFilter(collection().fields(), function(field) { return field.saved() })">
            <tr class="ko_container">
              <td data-bind="text: name"></td>
              <td data-bind="text: type"></td>
              <td><p class="text-center"><span class="fa" data-bind="css: {'fa-check': uniqueKeyField}"></span></p></td>
              <td><p class="text-center"><span class="fa" data-bind="css: {'fa-check': required}"></span></p></td>
              <td><p class="text-center"><span class="fa" data-bind="css: {'fa-check': indexed}"></span></p></td>
              <td><p class="text-center"><span class="fa" data-bind="css: {'fa-check': stored}"></span></p></td>
              <td></td>
            </tr>
          </tbody>
          <tbody data-bind="foreach: ko.utils.arrayFilter(collection().fields(), function(field) { return !field.saved() })">
            <tr data-bind="css: {'error': name.errors().length > 0}"  class="ko_container editable">
              <td data-bind="editableText: name">
                <span class="pull-left fa fa-pencil"></span>
              </td>
              <td><select data-bind="options: $parent.fieldTypes, value: type, chosen: {}" name="type"></select></td>
              <td><p class="text-center"><span class="fa" data-bind="css: {'fa-check': uniqueKeyField}"></span></p></td>
              <td><p class="text-center"><input data-bind="checked: required" type="checkbox"></p></td>
              <td><p class="text-center"><input data-bind="checked: indexed" type="checkbox"></p></td>
              <td><p class="text-center"><input data-bind="checked: stored" type="checkbox"></p></td>
              <td><a data-bind="click: remove" href="javascript:void(0)" class="btn btn-danger nowrap"><i class="fa fa-minus"></i></a></td>
            </tr>
          </tbody>
        </table>
        <a data-bind="click: collection().newField" href="javascript:void(0)" class="btn btn-info"><i class="fa fa-plus"></i>&nbsp;${_("Add")}</a>
        <br />
        <br />
        <br />
        <a data-bind="click: validateAndUpdateCollection" class="btn btn-info" href="javascript:void(0)">${_('Update')}</a>
      </form>
    </div>
  </div>
</div>
</script>

<!-- Upload wizard -->
<script id="upload-page" type="text/html">
<div class="span12">
  <div class="card wizard">
    <div class="card-heading simple" data-bind="template: { 'name': 'breadcrum', 'data': $root }"></div>
    <div class="card-body" data-bind="with: edit">
      <form data-bind="if: wizard.currentPage()" class="form form-horizontal">
        <div data-bind="template: { 'name': wizard.currentPage().name, 'afterRender': afterRender}"></div>
        <br style="clear:both" />
        <br style="clear:both" />
        <a data-bind="routie: 'edit/' + collection().name() + '/upload/' + wizard.previousUrl(), visible: wizard.hasPrevious" class="btn btn-info" href="javascript:void(0)">${_('Previous')}</a>
        <a data-bind="routie: 'edit/' + collection().name() + '/upload/' + wizard.nextUrl(), visible: wizard.hasNext" class="btn btn-info" href="javascript:void(0)">${_('Next')}</a>
        <a data-bind="click: addData, visible: !wizard.hasNext()" class="btn btn-info" href="javascript:void(0)">${_('Finish')}</a>
      </form>
    </div>
  </div>
</div>
</script>

<script type="text/html" id="upload-collection-data">
  <div class="control-group" data-bind="css: {'error': file.errors().length > 0}">
    <label for="name" class="control-label">${_("Files")}</label>
    <div class="controls">
      <input data-bind="value: file" type="text" class="span7 fileChooser" placeholder="/user/hue/data.csv"/>
    </div>
  </div>

  <div class="control-group" data-bind="css: {'error': sourceType.errors().length > 0}">
    <label for="name" class="control-label">${_("Source type")}</label>
    <div class="controls">
      <select data-bind="options: sourceTypes, value: sourceType" name="type"></select>
    </div>
  </div>
</script>

<script type="text/html" id="upload-collection-data-separated">
  <div class="control-group" data-bind="css: {'error': fieldSeparator.errors().length > 0}">
    <label for="separator" class="control-label">${_("Separator")}</label>
    <div class="controls">
      <select data-bind="options: fieldSeparators, optionsText: getCharacterLabel, value: fieldSeparator" name="separator"></select>
    </div>
  </div>

  <div class="control-group" data-bind="css: {'error': fieldQuoteCharacter.errors().length > 0}">
    <label for="quote" class="control-label">${_("Quote character")}</label>
    <div class="controls">
      <select data-bind="options: fieldQuoteCharacters, value: fieldQuoteCharacter" name="quote"></select>
    </div>
  </div>
</script>
<!--/ Wizard -->
<!--/ Edit collection page -->


<script src="/static/ext/chosen/chosen.jquery.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/jquery/plugins/jquery-ui-1.10.4.draggable-droppable-sortable.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/routie-0.3.0.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout.mapping-2.3.2.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout-sortable.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/indexer/static/js/lib.js" type="text/javascript" charset="utf-8"></script>
<script src="/indexer/static/js/collections.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript">
function afterRender() {
  $(".fileChooser:not(:has(~ button))").after(getFileBrowseButton($(".fileChooser:not(:has(~ button))")));
}

function validateAndUpdateCollection() {
  if (validateFields(ko.unwrap(vm.edit.collection))) {
    vm.edit.updateCollection().done(function(data) {
      if (data.status == 0) {
        routie('/');
      }
    });
  }
  return false;
}

function chooseFileToIndex($data, e) {
  $(e.target).siblings().find('button').click();
}

function validateFileAndNameAndType() {
  var ret = validateNotNull(vm.create.collection.name, "${ _('Name is missing') }");
  var ret = validateNotNull(vm.create.file, "${ _('File path is missing') }") && ret;

  if (vm.create.sourceType() == 'log' && ret) {
    validateFetchFields()
  }

  return ret;
}

function validateFetchFields() {
  vm.create.parseFields();
  return true;
}

function validateFields(collection) {
  var ret = true;
  $.each(collection.fields(), function(index, field) {
    ret = validateNotNull(field.name, "${ _('Field name is missing') }") && ret;
    ret = validateNotNull(field.type, "${ _('Field type is missing') }") && ret;
  });
  return ret;
}

var vm = new CollectionsViewModel({
  'breadcrum': {
    'labels': {
      '': "${_('Collections')}",
      'data': "${_('Upload data')}"
    },
    'skip': ['manage', 'upload', 'edit', 'create', 'wizard']
  }
});
var create_root = vm.create.wizard.getPage('name', 'create-collection-data', 'separated', validateFileAndNameAndType);
vm.create.wizard.getPage('separated', 'create-collection-data-separated', 'fields', validateFetchFields);
// vm.create.wizard.getPage('morphlines', 'create-collection-data-morphlines', 'fields', validateFetchFields);
vm.create.wizard.getPage('fields', 'create-collection-fields', null, function() { return validateFields(vm.create.collection) });
vm.create.wizard.rootPage(create_root);
vm.create.wizard.currentPage(vm.create.wizard.rootPage());

vm.create.sourceType.subscribe(function(value) {
  if (value == 'log') {
    vm.create.wizard.getPage('name').next('fields');
  } else {
    vm.create.wizard.getPage('name').next(value);
  }
});

var edit_root = vm.edit.wizard.getPage('data', 'upload-collection-data', 'separated', function() {return validateNotNull(vm.edit.file, "${ _('File path is missing') }")});
vm.edit.wizard.getPage('separated', 'upload-collection-data-separated', null, null);
vm.edit.wizard.rootPage(edit_root);
vm.edit.wizard.currentPage(vm.edit.wizard.rootPage());

vm.edit.sourceType.subscribe(function(value) {
  if (!value) {
    // Weird bug where sourceType disappears when switching between pages
    vm.edit.sourceType(vm.edit.wizard.getPage('data').next());
  } else if (value == 'log') {
    vm.edit.wizard.getPage('data').next(null);
  } else {
    vm.edit.wizard.getPage('data').next(value);
  }
});

routie({
  "": function() {
    vm.breadcrum("manage");
    vm.page('manage-page');
  },
  "manage": function() {
    vm.breadcrum(window.location.hash.substring(1));
    vm.page('manage-page');
  },
  "create": function() {
    vm.page('create-page');
    vm.breadcrum("create/wizard/" + vm.create.wizard.currentPage().url());
  },
  "create/wizard": function() {
    vm.page('create-page');
    vm.breadcrum("create/wizard/" + vm.create.wizard.currentPage().url());
  },
  "create/wizard/:step": function(step) {
    vm.breadcrum(window.location.hash.substring(1));
    vm.page('create-page');
    vm.create.wizard.setPageByUrl(step);
    routie('create/wizard/' + vm.create.wizard.currentPage().url());
  },
  "edit/:name": function(name) {
    ko.utils.arrayForEach(vm.manage.collections(), function(collection) {
      collection.selected(ko.unwrap(collection).name() == name);
    });
    if (vm.manage.selectedCollections().length == 0) {
      routie('manage');
    } else {
      vm.breadcrum(window.location.hash.substring(1));
      vm.edit.collection(vm.manage.selectedCollections()[0]());
      vm.edit.fetchFields();
      vm.page('edit-page');
    }
  },
  "edit/:name/upload": function(name) {
    ko.utils.arrayForEach(vm.manage.collections(), function(collection) {
      collection.selected(ko.unwrap(collection).name() == name);
    });
    if (vm.manage.selectedCollections().length == 0) {
      routie('manage');
    } else {
      vm.breadcrum('edit/' + name + '/upload/' + vm.edit.wizard.currentPage().url());
      vm.edit.collection(vm.manage.selectedCollections()[0]());
      vm.page('upload-page');
    }
  },
  "edit/:name/upload/:step": function(name, step) {
    ko.utils.arrayForEach(vm.manage.collections(), function(collection) {
      collection.selected(ko.unwrap(collection).name() == name);
    });
    if (vm.manage.selectedCollections().length == 0) {
      routie('manage');
    } else {
      vm.breadcrum(window.location.hash.substring(1));
      vm.edit.collection(vm.manage.selectedCollections()[0]());
      vm.page('upload-page');
    }
    vm.edit.wizard.setPageByUrl(step);
    routie('edit/' + name + '/upload/' + vm.edit.wizard.currentPage().url());
  }
});

vm.manage.fetchCollections();

ko.applyBindings(vm);
</script>

${ commonfooter(messages) | n,unicode }

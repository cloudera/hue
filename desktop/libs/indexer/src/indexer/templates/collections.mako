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

<link rel="stylesheet" href="/indexer/static/css/admin.css">
<style type="text/css">
  #collections {
    list-style-type: none;
    margin: 0;
    padding: 0;
    width: 100%;
  }

  .placeholder {
    height: 40px;
    background-color: #F5F5F5;
    border: 1px solid #E3E3E3;
  }

  .examples {
    max-height: 700px;
    overflow: auto;
  }

  .collection-row-container {
    margin: 3px;
  }

  .collection-row-container .collection-row {
    padding: 5px;
  }

  .solr-and-hue {
    background: #f2ffe3;
    border: 1px solid #e4f3d3;
  }

  .solr-and-hue .selected {
    background: #ceff97;
  }

  .hue-only {
    background: #ffe3f2;
    border: 1px solid #f3d3e4;
  }

  .hue-only .selected {
    background: #ff97ce;
  }

  .solr-only {
    background: #e3f2ff;
    border: 1px solid #d3e4f3;
  }

  .solr-only .selected {
    background: #e3f2ff;
  }

  .fields-table {
    min-width: 500px;
  }
</style>


<div class="search-bar" style="height: 30px">
  <h4><a href="/indexer">${_('Collection Manager')}</a></h4>
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
  <div data-bind="template: {'name': page, if: !isLoading()}" class="row-fluid" id="page"></div>
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


<!-- Manage collections page -->
<script id="manage-page" type="text/html">
<div data-bind="with: manage" class="span12" >
  <div class="card wizard">
    <h1 class="card-heading simple">${_("Manage collections")}</h1>
    <div class="card-body">
      <%actionbar:render>
        <%def name="search()">
          <div data-bind="visible: collections().length > 0 && !isLoading()">
            <input type="text" data-bind="filter: { 'list': collections, 'filteredList': filteredCollections, 'test': filterTest }" placeholder="${_('Filter collections by name...')}" class="input-xlarge search-query">
            <button data-bind="click: removeCollections, clickBubble: false, disable: selectedCollections().length == 0" class="btn toolbarBtn" title="${_('Delete the selected collections')}" disabled="disabled"><i class="fa fa-times"></i> ${_('Delete collections')}</button>
            <a href="#create" class="btn toolbarBtn">${_('Add collection')}</a>
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
      <div class="row-fluid">
        <div class="span12">
          <p>
            <ul id="collections" data-bind="template: {'name': 'collection-template', 'foreach': filteredCollections, 'afterRender': afterCollectionListRender}"></ul>
          </p>
        </div>
      </div>
    </div>
  </div>
</div>
</script>

<script id="collection-template" type="text/html">
<li class="collection-row-container" data-bind="click: $parent.toggleCollectionSelect.bind($parent), clickBubble: false, css: {'hue-only': !hasSolrCollection(), 'solr-only': !hasHueCollection(), 'solr-and-hue': hasHueCollection() && hasSolrCollection()}" title="${ _('Click to edit') }">
  <div data-bind="css: {'selected': $parent.collections()[$index()].selected()}" class="collection-row">
    <div class="pull-right" style="margin-top: 10px;margin-right: 10px;">
      <a data-bind="click: $parent.removeCollections, clickBubble: false" href="javascript:void(0);"><i class="fa fa-times"></i> ${_('Delete')}</a>
    </div>

    <!-- ko if: hasHueCollection() && hasSolrCollection() -->
    <form class="pull-right" style="margin-top: 10px;margin-right: 10px;">
      <div style="display: none">
        <input class="fileChooser">
      </div>
      <a data-bind="click: chooseFileToIndex, clickBubble: false" href="javascript:void(0);"><i class="fa fa-upload"></i> ${_('Upload')}</a>
    </form>
    <div class="pull-right" style="margin-top: 10px;margin-right: 10px;">
      <a data-bind="routie: 'edit/' + name()" href="javascript:void(0);"><i class="fa fa-pencil"></i> ${_('Edit')}</a>
    </div>
    <!-- /ko -->

    <!-- ko ifnot: hasHueCollection() -->
    <div class="pull-right" style="margin-top: 10px;margin-right: 10px;">
      <a data-bind="click: $parent.importCollection" href="javascript:void(0);"><i class="fa fa-pencil"></i> ${_('Create')}</a>
    </div>
    <!-- /ko -->
    <h4><i class="fa fa-list"></i> <span data-bind="text: name"></span></h4>
  </div>
</li>
</script>
<!--/ Manage collections page -->

<!-- Create by file -->
<script id="create-page" type="text/html">
<div data-bind="with: create" class="span12">
  <div class="card wizard">
    <h1 class="card-heading simple">${_("Create collection from file")}</h1>
    <div class="card-body" data-bind="if: wizard.currentPage()">
      <form class="form form-horizontal">
        <div data-bind="template: { 'name': wizard.currentPage().name}"></div>
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
<!--/ Create by file -->

<!-- Wizard -->
<script type="text/html" id="collection-data">
  <div class="control-group" data-bind="css: {'error': collection.name.errors().length > 0}">
    <label for="name" class="control-label">${_("Name")}</label>
    <div class="controls">
      <input data-bind="value: collection.name" name="name" type="text" placeholder="${_('Name of collection')}" />
    </div>
  </div>

  <div class="control-group" data-bind="css: {'error': file.errors().length > 0}">
    <label for="name" class="control-label">${_("Files")}</label>
    <div class="controls">
      <input data-bind="value: file" type="text" class="span7 fileChooser" placeholder="/user/foo/udf.jar"/>
    </div>
  </div>

  <div class="control-group" data-bind="css: {'error': sourceType.errors().length > 0}">
    <label for="name" class="control-label">${_("Source type")}</label>
    <div class="controls">
      <select data-bind="options: sourceTypes, value: sourceType" name="type"></select>
    </div>
  </div>
</script>

<script type="text/html" id="collection-data-separated">
  <div class="control-group" data-bind="css: {'error': fieldSeparator.errors().length > 0}">
    <label for="separator" class="control-label">${_("Separator")}</label>
    <div class="controls">
      <select data-bind="options: fieldSeparators, value: fieldSeparator" name="separator"></select>
    </div>
  </div>

  <div class="control-group" data-bind="css: {'error': fieldQuoteCharacter.errors().length > 0}">
    <label for="quote" class="control-label">${_("Quote character")}</label>
    <div class="controls">
      <select data-bind="options: fieldQuoteCharacters, value: fieldQuoteCharacter" name="quote"></select>
    </div>
  </div>
</script>

<script type="text/html" id="collection-data-morphlines">
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

<script type="text/html" id="collection-fields">
  <div class="span6">
    <table class="table table-bordered fields-table">
      <thead>
        <tr>
          <th width="30%">${_('Name')}</th>
          <th width="15%">${_('Type')}</th>
          <th width="10%">${_('Required')}</th>
          <th width="10%">${_('Indexed')}</th>
          <th width="10%">${_('Stored')}</th>
          <th width="10%">${_('Unique Key')}</th>
          <th width="15%"></th>
        </tr>
      </thead>
      <tbody data-bind="sortable: collection.fields">
        <tr data-bind="css: {'error': name.errors().length > 0}" class="ko_container editable">
          <td data-bind="editableText: name">
            <span class="pull-left fa fa-pencil"></span>
          </td>
          <td><select data-bind="options: $parent.fieldTypes, value: type" name="type"></select></td>
          <td><input data-bind="checked: required" type="checkbox"></td>
          <td><input data-bind="checked: indexed" type="checkbox"></td>
          <td><input data-bind="checked: stored" type="checkbox"></td>
          <td><input data-bind="checked: uniqueKeyField" name="unique-key" type="checkbox" /></td>
          <td>
            <a data-bind="click: remove, visible: editable" href="javascript:void(0)" class="btn btn-danger"><i class="fa fa-minus"></i>&nbsp;${_("Remove")}</a>
          </td>
        </tr>
      </tbody>
    </table>

    <br style="clear: both" />
    <br />
    <a data-bind="click: collection.newField" href="javascript:void(0)" class="btn btn-info"><i class="fa fa-plus"></i>&nbsp;${_("Add field")}</a>
  </div>
  <pre data-bind="text: exampleSchema" class="span6 examples"></pre>
</script>
<!--/ Wizard -->

<!-- Edit collection page -->
<script id="edit-page" type="text/html">
<div data-bind="with: edit" class="span12">
  <div class="card wizard">
    <h1 class="card-heading simple">${_("Edit collection")}</h1>
    <div class="card-body">
      <form class="form">
        <div class="control-group" data-bind="css: {'error': sourceType.errors().length > 0}">
          <label for="name" class="control-label">${_("Source type")}</label>
          <div class="controls">
            <select data-bind="options: sourceTypes, value: sourceType" name="type"></select>
          </div>
        </div>
        <br />
        <br />
        <table class="table table-bordered fields-table">
          <thead>
            <tr>
              <th width="50%" class="nowrap">${_('Name')}</th>
              <th width="20%" class="nowrap">${_('Type')}</th>
              <th width="1%" class="nowrap">${_('Unique key field')}</th>
              <th width="1%" class="nowrap">${_('Required')}</th>
              <th width="1%" class="nowrap">${_('Indexed')}</th>
              <th width="1%" class="nowrap">${_('Stored')}</th>
              <th width="26%"></th>
            </tr>
          </thead>
          <tbody data-bind="sortable: collection().fields">
            <!-- ko if: saved() -->
            <tr class="ko_container">
              <td data-bind="text: name"></td>
              <td data-bind="text: type"></td>
              <td><span class="fa" data-bind="css: {'fa-check': uniqueKeyField, 'fa-times': !uniqueKeyField()}"></span></td>
              <td><span class="fa" data-bind="css: {'fa-check': required, 'fa-times': !required()}"></span></td>
              <td><span class="fa" data-bind="css: {'fa-check': indexed, 'fa-times': !indexed()}"></span></td>
              <td><span class="fa" data-bind="css: {'fa-check': stored, 'fa-times': !stored()}"></span></td>
              <td></td>
            </tr>
            <!-- /ko -->
            <!-- ko ifnot: saved() -->
            <tr data-bind="css: {'error': name.errors().length > 0}"  class="ko_container editable">
              <td data-bind="editableText: name">
                <span class="pull-left fa fa-pencil"></span>
              </td>
              <td><select data-bind="options: $parent.fieldTypes, value: type" name="type"></select></td>
              <td><span class="fa" data-bind="css: {'fa-check': uniqueKeyField, 'fa-times': !uniqueKeyField()}"></span></td>
              <td><input data-bind="checked: required" type="checkbox"></td>
              <td><input data-bind="checked: indexed" type="checkbox"></td>
              <td><input data-bind="checked: stored" type="checkbox"></td>
              <td><a data-bind="click: remove" href="javascript:void(0)" class="btn btn-danger nowrap"><i class="fa fa-minus"></i>&nbsp;${_("Remove field")}</a></td>
            </tr>
            <!-- /ko -->
          </tbody>
        </table>
        <br />
        <br />
        <a data-bind="click: collection().newField" href="javascript:void(0)" class="btn btn-info"><i class="fa fa-plus"></i>&nbsp;${_("Add field")}</a>
        <br />
        <br />
        <a data-bind="click: validateAndUpdateCollection" class="btn btn-info" href="javascript:void(0)">${_('Update')}</a>
        <a data-bind="routie: '/'" class="btn btn-info" href="javascript:void(0)">${_('Done')}</a>
      </form>
    </div>
  </div>
</div>
</script>

<!--/ Edit collection page -->


<script src="/static/ext/chosen/chosen.jquery.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/jquery/plugins/jquery-ui-draggable-droppable-sortable-1.8.23.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/routie-0.3.0.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout.mapping-2.3.2.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout-sortable.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/indexer/static/js/lib.js" type="text/javascript" charset="utf-8"></script>
<script src="/indexer/static/js/collections.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript">

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

function afterCollectionListRender(elements) {
  $(elements).find(".fileChooser:not(:has(~ button))").change(function(e) {
    var context = ko.contextFor(e.target);
    vm.manage.addData(context.$data, $(e.target).val());
  });
  addFileBrowseButton();
}

function addFileBrowseButton() {
  $(".fileChooser:not(:has(~ button))").after(getFileBrowseButton($(".fileChooser:not(:has(~ button))")));
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

var vm = new CollectionsViewModel();
var root = vm.create.wizard.getPage('name', 'collection-data', 'separated', validateFileAndNameAndType);
vm.create.wizard.getPage('separated', 'collection-data-separated', 'fields', validateFetchFields);
vm.create.wizard.getPage('morphlines', 'collection-data-morphlines', 'fields', validateFetchFields);
vm.create.wizard.getPage('fields', 'collection-fields', null, function() { return validateFields(vm.create.collection) });
vm.create.wizard.rootPage(root);
vm.create.wizard.currentPage(vm.create.wizard.rootPage());

vm.create.sourceType.subscribe(function(value) {
  if (value == 'log') {
    vm.create.wizard.getPage('name').next('fields');
  } else {
    vm.create.wizard.getPage('name').next(value);
  }
});

routie({
  "": function() {
    routie('manage');
  },
  "manage": function() {
    vm.page('manage-page');
  },
  "create": function() {
    vm.page('create-page');
    routie('create/wizard');
  },
  "create/wizard": function(step) {
    vm.page('create-page');
    routie('create/wizard/' + vm.create.wizard.currentPage().url());
  },
  "create/wizard/:step": function(step) {
    vm.page('create-page');
    vm.create.wizard.setPageByUrl(step);
    routie('create/wizard/' + vm.create.wizard.currentPage().url());
    $(".fileChooser:not(:has(~ button))").after(getFileBrowseButton($(".fileChooser:not(:has(~ button))")));
  },
  "edit/:name": function(name) {
    ko.utils.arrayForEach(vm.manage.collections(), function(collection) {
      collection.selected(ko.unwrap(collection).name() == name);
    });
    if (vm.manage.selectedCollections().length == 0) {
      routie('manage');
    } else {
      vm.edit.collection(vm.manage.selectedCollections()[0]());
      vm.page('edit-page');
    }
  },
  "*": function() {
    routie('manage');
  },
});

vm.manage.fetchCollections();

ko.applyBindings(vm);
</script>

${ commonfooter(messages) | n,unicode }

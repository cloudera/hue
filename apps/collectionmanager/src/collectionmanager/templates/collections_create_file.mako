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

${ commonheader(_('Collection Manager'), "collectionmanager", user, "29px") | n,unicode }

<link rel="stylesheet" href="/collectionmanager/static/css/admin.css">
<link rel="stylesheet" href="/static/ext/chosen/chosen.min.css">

<div class="search-bar" style="height: 30px">
  <h4><a href="/collectionmanager">${_('Collection Manager')}</a></h4>
</div>


<div class="container-fluid">
  <div class="row-fluid">

    <div class="span3">
      <div class="sidebar-nav card-small">
        <ul class="nav nav-list">
          <li class="nav-header">${_('Actions')}</li>
          <li><a href="/collectionmanager/import"><i class="fa fa-plus-circle"></i> ${ _('Import an existing collection') }</a></li>
          <li><a href="/collectionmanager/create/file/"><i class="fa fa-files-o"></i> ${_('Create a new collection from a file')}</a></li>
          ## <li><a href="/collectionmanager/create/manual/"><i class="fa fa-wrench"></i> ${_('Create a new collection manually')}</a></li>
        </ul>
      </div>
    </div>

    <div class="span9">
      <div class="card wizard">
        <h1 class="card-heading simple">${_("Create collection from file")}</h1>
        <div class="card-body" data-bind="if: wizard.currentPage()">
          <form class="form form-horizontal">
            <div data-bind="template: { 'name': wizard.currentPage().name }"></div>
            <br />
            <a data-bind="routie: 'wizard/' + wizard.previousUrl(), visible: wizard.hasPrevious" class="btn btn-info" href="javascript:void(0)">${_('Previous')}</a>
            <a data-bind="routie: 'wizard/' + wizard.nextUrl(), visible: wizard.hasNext" class="btn btn-info" href="javascript:void(0)">${_('Next')}</a>
            <a data-bind="click: save, visible: !wizard.hasNext()" class="btn btn-info" href="javascript:void(0)">${_('Finish')}</a>
          </form>
        </div>
      </div>
    </div>
  </div>
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


<!-- Start Wizard -->
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

  <div class="control-group" data-bind="css: {'error': fileType.errors().length > 0}">
    <label for="name" class="control-label">${_("Name")}</label>
    <div class="controls">
      <select data-bind="options: fileTypes, value: fileType" name="type"></select>
    </div>
  </div>
</script>

<script type="text/html" id="collection-data-separated">
  <div class="control-group" data-bind="css: {'error': fieldSeparator.errors().length > 0}">
    <label for="name" class="control-label">${_("Name")}</label>
    <div class="controls">
      <select data-bind="options: fieldSeparators, value: fieldSeparator" name="type"></select>
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
  <formset data-bind="foreach: collection.fields">
    <div class="control-group" data-bind="css: {'error': name.errors().length > 0}">
      <label for="name" class="control-label">${_("Name")}</label>
      <div class="controls">
        <input data-bind="value: name" name="name" type="text" placeholder="${_('Name of field')}" />
      </div>
    </div>

    <div class="control-group">
      <label for="type" class="control-label">${_("Type")}</label>
      <div class="controls">
        <select data-bind="options: $root.fieldTypes, value: type" name="type"></select>
      </div>
    </div>

    <a data-bind="click: remove" href="javascript:void(0)" class="btn btn-error"><i class="fa fa-minus"></i>&nbsp;${_("Remove field")}</a>
  </formset>

  <br />
  <br />
  <a data-bind="click: collection.newField" href="javascript:void(0)" class="btn btn-info"><i class="fa fa-plus"></i>&nbsp;${_("Add field")}</a>
</script>
<!-- End Wizard -->


<script src="/static/ext/js/routie-0.3.0.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout.mapping-2.3.2.js" type="text/javascript" charset="utf-8"></script>
<script src="/collectionmanager/static/js/collections.ko.js" type="text/javascript" charset="utf-8"></script>
<script src="/collectionmanager/static/js/create-collection.ko.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/chosen/chosen.jquery.min.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript">
function validateFileAndNameAndType() {
  var ret = validateNotNull(vm.collection.name, "${ _('Name is missing') }");
  var ret = ret && validateNotNull(vm.file, "${ _('File path is missing') }");

  if (vm.fileType() == 'log') {
    validateFetchFields()
  }

  return ret;
}

function validateFetchFields() {
  vm.fetchFields();
  return true;
}

function validateFields() {
  var ret = true;
  $.each(vm.collection.fields(), function(index, field) {
    ret = ret && validateNotNull(field.name, "${ _('Field name is missing') }");
    ret = ret && validateNotNull(field.type, "${ _('Field type is missing') }");
  });
  return ret;
}

var vm = new CreateCollectionViewModel();
var root = vm.wizard.getPage('name', 'collection-data', 'separated', validateFileAndNameAndType);
vm.wizard.getPage('separated', 'collection-data-separated', 'fields', validateFetchFields);
vm.wizard.getPage('morphlines', 'collection-data-morphlines', 'fields', validateFetchFields);
vm.wizard.getPage('fields', 'collection-fields', null, validateFields);
vm.wizard.rootPage(root);
vm.wizard.currentPage(vm.wizard.rootPage());

vm.fileType.subscribe(function(value) {
  vm.wizard.getPage('name').next(value);
});

routie({
  "wizard/:step": function(step) {
    vm.wizard.setPageByUrl(step);
    routie('wizard/' + vm.wizard.currentPage().url());
    $(".fileChooser:not(:has(~ button))").after(getFileBrowseButton($(".fileChooser:not(:has(~ button))")));
  },
  "*": function() {
    routie('wizard/name');
  },
});

ko.applyBindings(vm);

$(".fileChooser:not(:has(~ button))").after(getFileBrowseButton($(".fileChooser:not(:has(~ button))")));

</script>

${ commonfooter(messages) | n,unicode }

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
  from desktop import conf
  from desktop.views import commonheader, commonfooter, commonshare, commonimportexport
  from django.utils.translation import ugettext as _
%>

<%namespace name="actionbar" file="actionbar.mako" />
<%namespace name="assist" file="/assist.mako" />

${ commonheader(_("Solr Indexes"), "search", user, request, "60px") | n,unicode }

<span class="notebook">

# Todo lot of those
<script src="${ static('desktop/js/autocomplete/sql.js') }"></script>
<script src="${ static('desktop/js/sqlAutocompleter.js') }"></script>
<script src="${ static('desktop/js/sqlAutocompleter2.js') }"></script>
<script src="${ static('desktop/js/hdfsAutocompleter.js') }"></script>
<script src="${ static('desktop/js/autocompleter.js') }"></script>
<script src="${ static('desktop/js/hue.json.js') }"></script>


<script src="${ static('desktop/js/jquery.hiveautocomplete.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/jquery/plugins/jquery-ui-1.10.4.custom.min.js') }"></script>
<script src="${ static('desktop/js/jquery.huedatatable.js') }"></script>
<script src="${ static('desktop/ext/js/d3.v3.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/selectize.min.js') }"></script>
<script src="${ static('desktop/js/apiHelper.js') }"></script>
<script src="${ static('metastore/js/metastore.ko.js') }"></script>
<script src="${ static('desktop/js/ko.charts.js') }"></script>
<script src="${ static('desktop/ext/js/knockout-sortable.min.js') }"></script>
<script src="${ static('desktop/js/ko.editable.js') }"></script>

${ assist.assistJSModels() }

<script src="${ static('notebook/js/notebook.ko.js') }"></script>

<link rel="stylesheet" href="${ static('notebook/css/notebook.css') }">
<link rel="stylesheet" href="${ static('notebook/css/notebook-layout.css') }">
<link rel="stylesheet" href="${ static('desktop/css/wizard.css') }">

<style type="text/css">
% if conf.CUSTOM.BANNER_TOP_HTML.get():
  .show-assist {
    top: 110px!important;
  }
  .main-content {
    top: 112px!important;
  }
% endif
  .path {
    margin-bottom: 0!important;
    border-right: none!important;
  }

  .step1 label div {
    width: 50px;
    display: inline-block;
  }

  .step2.form-inline input[type='text'], .step2.form-inline select {
    margin-right: 10px;
    margin-left: 3px;
  }

  .step2.form-inline input[type='checkbox'] {
    margin-left: 10px!important;
    margin-right: 4px!important;
  }

  .field {
    padding: 4px;
    padding-left: 10px;
    border-left: 4px solid #DBE8F1;
  }

  .operation {
    border-left: 4px solid #EEE;
    padding-left: 10px;
    margin-top: 5px;
    margin-bottom: 5px;
    margin-left: 10px;
  }

  .content-panel {
    overflow-x: hidden;
  }

  .fileChooserBtn {
    height: 29px;
  }

  .form-control.path {
    vertical-align: top;
  }

  .form-actions {
    position: fixed;
    bottom: 0;
    margin: 0;
  }

  #notebook {
    height: 5px;
    margin-top: 10px;
  }

</style>

${ assist.assistPanel() }

<div class="navbar navbar-inverse navbar-fixed-top">
  <div class="navbar-inner">
    <div class="container-fluid">
      <div class="nav-collapse">
        <ul class="nav">
          <li class="currentApp">
            <a href="/indexer/indexer">
              <i class="fa fa-database app-icon"></i> ${_('Indexes')}</a>
            </a>
          </li>
        </ul>
      </div>
    </div>
  </div>
</div>

<a title="${_('Toggle Assist')}" class="pointer show-assist" data-bind="visible: !$root.isLeftPanelVisible() && $root.assistAvailable(), click: function() { $root.isLeftPanelVisible(true); }">
  <i class="fa fa-chevron-right"></i>
</a>


<div class="main-content">
  <div class="vertical-full container-fluid" data-bind="style: { 'padding-left' : $root.isLeftPanelVisible() ? '0' : '20px' }">
    <div class="vertical-full">
      <div class="vertical-full row-fluid panel-container">

        <div class="assist-container left-panel" data-bind="visible: $root.isLeftPanelVisible() && $root.assistAvailable()">
          <a title="${_('Toggle Assist')}" class="pointer hide-assist" data-bind="click: function() { $root.isLeftPanelVisible(false) }">
            <i class="fa fa-chevron-left"></i>
          </a>
          <div class="assist" data-bind="component: {
              name: 'assist-panel',
              params: {
                user: '${user.username}',
                onlySql: false,
                sql: {
                  sourceTypes: [{
                    name: 'hive',
                    type: 'hive'
                  }],
                  navigationSettings: {
                    openItem: false,
                    showStats: true
                  }
                },
                visibleAssistPanels: ['sql', 'hdfs', 'documents']
              }
            }"></div>
        </div>
        <div class="resizer" data-bind="visible: $root.isLeftPanelVisible() && $root.assistAvailable(), splitDraggable : { appName: 'notebook', leftPanelVisible: $root.isLeftPanelVisible }"><div class="resize-bar">&nbsp;</div></div>

        <div class="content-panel">
          <div style="margin: 10px; margin-bottom: 100px">
          <!-- ko template: 'create-index-wizard' --><!-- /ko -->
          </div>
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
    <div id="filechooser"></div>
  </div>
  <div class="modal-footer"></div>
</div>

<script type="text/html" id="create-index-wizard">
  <div data-bind="visible: createWizard.show">

    <ol class="list-inline text-center step-indicator">
      <li data-bind="css: { 'active': currentStep() == 1, 'active': currentStep() > 1 }, click: function() { currentStep(1) }">
        <div class="step" title="${ _('Go to Step 1') }">
          <!-- ko if: currentStep() == 1 -->
            <!-- ko if: createWizard.isGuessingFormat -->
              <span class="fa fa-spinner fa-spin"></span>
            <!-- /ko -->
            <!-- ko ifnot: createWizard.isGuessingFormat -->
              1
            <!-- /ko -->
          <!-- /ko -->
          <!-- ko ifnot: currentStep() == 1 -->
          <span class="fa fa-check"></span>
          <!-- /ko -->
        </div>
        <div class="caption">${ _('Pick data from ') }<span data-bind="text: createWizard.source.inputFormat"></span></div>
      </li>

      <li data-bind="css: { 'inactive': currentStep() == 1, 'active': currentStep() == 2, 'complete': currentStep() == 3 }, click: function() { currentStep(2) }">
        <div class="step" title="${ _('Go to Step 2') }">
          <!-- ko if: currentStep() < 2 -->
            <!-- ko if: createWizard.isGuessingFieldTypes -->
              <span class="fa fa-spinner fa-spin"></span>
            <!-- /ko -->
            <!-- ko ifnot: createWizard.isGuessingFieldTypes -->
              2
            <!-- /ko -->
          <!-- /ko -->
        </div>
        <div class="caption">${ _('Move it to ') }<span data-bind="text: createWizard.destination.ouputFormat"></span></div>
      </li>
    </ol>


    <!-- ko if: currentStep() == 1 -->
    <div class="card step1">
      <h3 class="card-heading simple">${_('Source')}</h3>
      <div class="card-body">

        <form class="form-inline">
          <div>
            <div class="control-group">
              <label for="collectionType" class="control-label"><div>${ _('Type') }</div>
                <select id="collectionType" data-bind="options: createWizard.source.inputFormats, value: createWizard.source.inputFormat"></select>
              </label>
            </div>

            <div class="control-group" data-bind="visible: createWizard.source.inputFormat() == 'file'">
              <label for="path" class="control-label"><div>${ _('Path') }</div>
                <input type="text" class="form-control path input-xxlarge" data-bind="value: createWizard.source.path, filechooser: createWizard.source.path, filechooserOptions: { linkMarkup: true, skipInitialPathIfEmpty: true }">
              </label>
            </div>

            <div class="control-group" data-bind="visible: createWizard.source.inputFormat() == 'table'">
              <label for="path" class="control-label"><div>${ _('Table') }</div>
                <input type="text" data-bind="value: createWizard.source.table, hivechooser: createWizard.source.table, skipColumns: true">
              </label>
            </div>

            <div class="control-group" data-bind="visible: createWizard.source.inputFormat() == 'query'">
              <label for="path" class="control-label"><div>${ _('Query') }</div>
                <select data-bind="options: createWizard.source.queries, value: createWizard.source.query, optionsText: 'name', optionsAfterRender: createWizard.source.selectQuery"></select>
              </label>
            </div>
          </div>

          <!-- ko if: createWizard.source.show -->
          <h3 class="card-heading simple">${_('Format')}</h3>
          <div class="card-body">
              <label>${_('File Type')} <select data-bind="options: $root.createWizard.fileTypes, optionsText: 'description', value: $root.createWizard.fileType"></select></label>

              <span data-bind="with: createWizard.source.format, visible: createWizard.source.show">
                <!-- ko template: {name: 'format-settings'} --> <!-- /ko -->
              </span>
          </div>

          <h3 class="card-heading simple">${_('Preview')}</h3>
          <div class="card-body">
            <!-- ko if: createWizard.isGuessingFieldTypes -->
            <i class="fa fa-spinner fa-spin"></i>
            <!-- /ko -->
            <div style="overflow: auto">
              <table class="table table-striped table-condensed" style="margin:auto;text-align:left">
                <thead>
                <tr data-bind="foreach: createWizard.source.sampleCols">
                  ##<!-- ko template: 'field-preview-header-template' --><!-- /ko -->
                  <th data-bind="text: name" style="padding-right:60px"></th>
                  ## TODO nested
                </tr>
                </thead>
                <tbody data-bind="foreach: createWizard.source.sample">
                <tr data-bind="foreach: $data">
                  ##<!-- ko if: $index() < $root.createWizard.source.columns().length -->
                  ##<td data-bind="visible: $root.createWizard.source.columns()[$index()].keep, text: $data"></td>
                  <td data-bind="text: $data"></td>

                  ##<!-- ko with: $root.createWizard.source.columns()[$index()] -->
                  ##  <!-- ko template: 'output-generated-field-data-template' --> <!-- /ko -->
                  ##<!-- /ko -->
                  ##<!-- /ko -->
                </tr>
                </tbody>
              </table>
            </div>
          </div>
          <!-- /ko -->

        </form>
      </div>

    </div>
    <!-- /ko -->

    <!-- ko if: currentStep() == 2 -->
    <div class="card step2">

      <div class="control-group">
        <label for="collectionType" class="control-label"><div>${ _('Type') }</div>
          <select id="collectionType" data-bind="options: createWizard.destination.ouputFormats, value: createWizard.destination.ouputFormat"></select>
        </label>
      </div>

      <div class="control-group>
        <label for="collectionName" class="control-label"><div>${ _('Name') }</div>
          <input type="text" class="form-control input-xlarge" id="collectionName" data-bind="value: createWizard.destination.name, valueUpdate: 'afterkeydown'" placeholder="${ _('Collection name') }">
          <span class="help-inline muted" data-bind="visible: createWizard.isNameAvailable()">${ _('A new collection will be created') }</span>
          <span class="help-inline muted" data-bind="visible: ! createWizard.isNameAvailable() && createWizard.destination.name().length > 0">
          ${ _('Adding data to this existing collection') }
          <a href="javascript:void(0)" data-bind="attr: {href: '${ url("indexer:collections") }' +'#edit/' + createWizard.destination.name() }, text: createWizard.destination.name" target="_blank"></a>
          </span>
        </label>
      </div>

      <h3 class="card-heading simple">${_('Fields')}</h3>
      <div class="card-body">
        <!-- ko if: createWizard.isGuessingFieldTypes -->
          <i class="fa fa-spinner fa-spin"></i>
        <!-- /ko -->

        <!-- ko if: $root.createWizard.destination.ouputFormat() == 'table' -->
          <input type="text" class="form-control input-xlarge" id="collectionName" data-bind="valueUpdate: 'afterkeydown'" placeholder="${ _('Description') }">

          <label class="checkbox">
            <input type="checkbox" checked -bind=""> ${_('Import data')}
          </label>
          <label class="checkbox">
            <input type="checkbox" checked> ${_('Default location')}
          </label>
          <label for="path" class="control-label"><div>${ _('Path') }</div>
            <input type="text" class="form-control path input-xxlarge" data-bind="value: createWizard.source.path, filechooser: createWizard.source.path, filechooserOptions: { linkMarkup: true, skipInitialPathIfEmpty: true }">
          </label>
          <label class="checkbox">
            <input type="checkbox"> ${_('Custom delimiters')}
          </label>
          ## field, coll map delimieters
          ## regexp

          <label class="checkbox">
              <input type="checkbox" checked> ${_('Use headers')}
            </label>
          <label class="checkbox">
              <input type="checkbox" checked> ${_('Bulk edit col names')}
            </label>

          <div class="control-group">
            <label for="collectionType" class="control-label"><div>${ _('Format') }</div>
              <select id="collectionType" data-bind="options: $root.createWizard.destination.tableFormats, value: $root.createWizard.destination.tableFormat"></select>
            </label>
          </div>

          <a class="pointer margin-left-20" title="${_('Add Operation')}"><i class="fa fa-plus"></i> ${_('Add partition')}</a>
        <!-- /ko -->

        <form class="form-inline" data-bind="foreach: createWizard.destination.columns">
          <!-- ko if: $root.createWizard.destination.ouputFormat() == 'table' -->
            <div data-bind="template: { name: 'table-field-template', data: $data }" class="margin-top-10 field"></div>
          <!-- /ko -->

          <!-- ko if: $root.createWizard.destination.ouputFormat() == 'index' -->
            <div data-bind="template: { name: 'index-field-template', data: $data }" class="margin-top-10 field"></div>
          <!-- /ko -->
        </form>
      </div>
    </div>
    <!-- /ko -->


    <div class="form-actions">
      <!-- ko if: previousStepVisible -->
        <button class="btn" data-bind="click: previousStep">${ _('Back') }</button>
      <!-- /ko -->

      <!-- ko if: currentStep() == 1 && createWizard.source.show -->
      <button class="btn" data-bind="click: function() { currentStep(2); }">
        ${_('Next')} <i class="fa fa-spinner fa-spin" data-bind="visible: createWizard.isGuessingFormat"></i>
      </button>
      <!-- /ko -->

      <!-- ko if: currentStep() == 2 -->
        <button href="javascript:void(0)" class="btn btn-primary disable-feedback" data-bind="click: createWizard.indexFile, enable: createWizard.readyToIndex() && ! createWizard.indexingStarted()">
          ${ _('Submit') } <i class="fa fa-spinner fa-spin" data-bind="visible: createWizard.indexingStarted"></i>
        </button>
      <!-- /ko -->

      <span data-bind="visible: createWizard.editorId">
        <a href="javascript:void(0)" class="btn btn-success" data-bind="attr: {href: '${ url('notebook:editor') }?editor=' + createWizard.editorId() }" target="_blank" title="${ _('Open') }">
          ${_('Status')}
        </a>

        ${ _('View collection') } <a href="javascript:void(0)" data-bind="attr: {href: '${ url("indexer:collections") }' +'#edit/' + createWizard.source.name() }, text: createWizard.source.name" target="_blank"></a>
      </span>

      <div id="notebook"></div>
    </div>
  </div>
</script>


<script type="text/html" id="format-settings">
  <!-- ko foreach: {data: getArguments(), as: 'argument'} -->
    <!-- ko template: {name: 'arg-' + argument.type, data:{description: argument.description, value: $parent[argument.name]}}--><!-- /ko -->
  <!-- /ko -->
</script>


<script type="text/html" id="table-field-template">
  <label>${ _('Name') }
    <input type="text" class="input-large" placeholder="${ _('Field name') }" data-bind="value: name">
  </label>
  <label>${ _('Type') }
    <select class="input-small" data-bind="options: $root.createWizard.hiveFieldTypes, value: type"></select>
  </label>

  <label data-bind="text: $root.createWizard.source.sample()[0][$index()]"></label>
  <label data-bind="text: $root.createWizard.source.sample()[1][$index()]"></label>

  <a href="javascript:void(0)" title="${ _('Show field properties') }" data-bind="click: function() {showProperties(! showProperties()) }">
    <i class="fa fa-sliders"></i>
  </a>
  <span data-bind="visible: showProperties">
    <label class="checkbox">
      <input type="checkbox" data-bind="checked: unique"> ${_('Primary key')}
    </label>
  </span>

  <a class="pointer margin-left-20" title="${_('Add Operation')}"><i class="fa fa-plus"></i> ${_('Nested')}</a>
  <a class="pointer margin-left-20" title="${_('Add Operation')}"><i class="fa fa-plus"></i> ${_('Operation')}</a>
  <a class="pointer margin-left-20" title="${_('Add Operation')}"><i class="fa fa-plus"></i> ${_('Comment')}</a>
</script>


<script type="text/html" id="index-field-template">
  <label>${ _('Name') }
    <input type="text" class="input-large" placeholder="${ _('Field name') }" data-bind="value: name">
  </label>
  <label>${ _('Type') }
    <select class="input-small" data-bind="options: $root.createWizard.fieldTypes, value: type"></select>
  </label>
  <a href="javascript:void(0)" title="${ _('Show field properties') }" data-bind="click: function() {showProperties(! showProperties()) }">
    <i class="fa fa-sliders"></i>
  </a>
  <span data-bind="visible: showProperties">
    <label class="checkbox">
      <input type="checkbox" data-bind="checked: unique"> ${_('Unique')}
    </label>
    <label class="checkbox">
      <input type="checkbox" data-bind="checked: keep"> ${_('Keep in index')}
    </label>
    <label class="checkbox">
      <input type="checkbox" data-bind="checked: required"> ${_('Required')}
    </label>
  </span>

  <!-- ko if: operations().length == 0 -->
  <a class="pointer margin-left-20" data-bind="click: $root.createWizard.addOperation" title="${_('Add Operation')}"><i class="fa fa-plus"></i> ${_('Operation')}</a>
  <!-- /ko -->

  <div data-bind="foreach: operations">
    <div data-bind="template: { name:'operation-template',data:{operation: $data, list: $parent.operations}}"></div>
  </div>

  <!-- ko if: operations().length > 0 -->
  <a class="pointer" data-bind="click: $root.createWizard.addOperation" title="${_('Add Operation')}"><i class="fa fa-plus"></i> ${_('Operation to')} <span data-bind="text: name"></span></a>
  <!-- /ko -->
</script>


<script type="text/html" id="operation-template">
  <div class="operation">
    <select data-bind="options: $root.createWizard.operationTypes.map(function(o){return o.name}), value: operation.type"></select>
    <!-- ko template: "args-template" --><!-- /ko -->
    <!-- ko if: operation.settings().outputType() == "custom_fields" -->
      <label> ${ _('Number of expected fields') }
      <input type="number" class="input-mini" data-bind="value: operation.numExpectedFields">
      </label>
    <!-- /ko -->
    <a class="pointer margin-left-20" data-bind="click: function(){$root.createWizard.removeOperation(operation, list)}" title="${ _('Remove') }"><i class="fa fa-times"></i></a>
    <div class="margin-left-20" data-bind="foreach: operation.fields">
      <div data-bind="template: { name:'index-field-template', data:$data }" class="margin-top-10 field"></div>
    </div>
  </div>
</script>

<script type="text/html" id="args-template">
  <!-- ko foreach: {data: operation.settings().getArguments(), as: 'argument'} -->
    <!-- ko template: {name: 'arg-'+argument.type, data:{description: argument.description, value: $parent.operation.settings()[argument.name]}}--><!-- /ko -->
  <!-- /ko -->
</script>

<script type="text/html" id="arg-text">
  <label>
    <span data-bind="text: description"></span>
    <input type="text" class="input-small" data-bind="attr: {placeholder: description}, value: value">
  </label>
</script>

<script type="text/html" id="arg-checkbox">
  <label>
    <input type="checkbox" data-bind="checked: value">
    <span data-bind="text: description"></span>
  </label>
</script>

<script type="text/html" id="arg-mapping">
  <!-- ko foreach: value-->
    <div>
      <input type="text" data-bind="value: key, attr: {placeholder: 'key'}">
      <input type="text" data-bind="value: value, attr: {placeholder: 'value'}">
      <button class="btn" data-bind="click: function(){$parent.value.remove($data)}">${_('Remove Pair')}</button>
    </div>
  <!-- /ko -->
  <button class="btn" data-bind="click: function(){value.push({key: ko.observable(''), value: ko.observable('')})}">${_('Add Pair')}</button>
  <br>
</script>

<script type="text/html" id="field-preview-header-template">
  <th data-bind="visible: keep, text: name" style="padding-right:60px"></th>
  <!-- ko foreach: operations -->
    <!--ko foreach: fields -->
      <!-- ko template: 'field-preview-header-template' --><!-- /ko -->
    <!-- /ko -->
  <!--/ko -->
</script>

<script type="text/html" id="output-generated-field-data-template">
  <!-- ko foreach: operations -->
    <!--ko foreach: fields -->
      <td data-bind="visible: keep">[[${_('generated')}]]</td>
      <!-- ko template: 'output-generated-field-data-template' --><!-- /ko -->
    <!-- /ko -->
  <!--/ko -->
</script>

<script type="text/html" id="notebook-progress">
  <!-- ko with: selectedNotebook  -->
    <!-- ko foreach: snippets  -->
      <div class="progress-snippet progress active" data-bind="css: {
        'progress-starting': progress() == 0 && status() == 'running',
        'progress-warning': progress() > 0 && progress() < 100,
        'progress-success': progress() == 100,
        'progress-danger': progress() == 0 && errors().length > 0}" style="background-color: #FFF; width: 100%; height: 4px">
        <div class="bar" data-bind="style: {'width': (errors().length > 0 ? 100 : Math.max(2, progress())) + '%'}"></div>
      </div>
    <!-- /ko -->
  <!-- /ko -->
</script>


<script type="text/javascript" charset="utf-8">
  (function () {
    ko.options.deferUpdates = true;

    var fieldNum = 0;

    var getNewFieldName = function () {
      fieldNum++;
      return "new_field_" + fieldNum
    };

    var createDefaultField = function () {
      var defaultField = ko.mapping.fromJS(${default_field_type | n});

      defaultField.name = ko.observable(getNewFieldName());

      return defaultField;
    };

    var Operation = function (type) {
      var self = this;

      var createArgumentValue = function (arg) {
        if (arg.type == "mapping") {
          return ko.observableArray([]);
        }
        else if (arg.type == "checkbox") {
          return ko.observable(false);
        }
        else {
          return ko.observable("");
        }
      }

      var constructSettings = function (type) {
        var settings = {};

        var operation = viewModel.createWizard.operationTypes.find(function (currOperation) {
          return currOperation.name == type;
        });

        for (var i = 0; i < operation.args.length; i++) {
          var argVal = createArgumentValue(operation.args[i]);

          if (operation.args[i].type == "checkbox" && operation.outputType == "checkbox_fields") {
            argVal.subscribe(function (newVal) {
              if (newVal) {
                self.fields.push(createDefaultField());
              }
              else {
                self.fields.pop();
              }
            });
          }

          settings[operation.args[i].name] = argVal;
        }

        settings.getArguments = function () {
          return operation.args
        };

        settings.outputType = function () {
          return operation.outputType;
        }

        return settings;
      };

      var init = function () {
        self.fields([]);
        self.numExpectedFields(0);

        self.numExpectedFields.subscribe(function (numExpectedFields) {
          if (numExpectedFields < self.fields().length) {
            self.fields(self.fields().slice(0, numExpectedFields));
          }
          else if (numExpectedFields > self.fields().length) {
            var difference = numExpectedFields - self.fields().length;

            for (var i = 0; i < difference; i++) {
              self.fields.push(createDefaultField());
            }
          }
        });
        self.settings(constructSettings(self.type()));
      }

      self.load = function (data) {
        self.numExpectedFields(data.numExpectedFields);

        var newSettings = constructSettings(data.type);
        for (var key in data.settings) {
          newSettings[key] = ko.mapping.fromJS(data.settings[key]);
        }
        self.settings(newSettings);

        data.fields.forEach(function (field) {
          self.fields.push(loadField(field));
        });
      }

      self.type = ko.observable(type);
      self.fields = ko.observableArray();
      self.numExpectedFields = ko.observable();
      self.settings = ko.observable();

      init();

      self.type.subscribe(function (newType) {
        init();
      });
    }

    var FileType = function (typeName, args) {
      var self = this;
      var type;

      var init = function () {
        self.type = ko.observable(typeName);

        var types = viewModel.createWizard.fileTypes;

        for (var i = 0; i < types.length; i++) {
          if (types[i].name == typeName) {
            type = types[i];
            break;
          }
        }

        for (var i = 0; i < type.args.length; i++) {
          self[type.args[i].name] = ko.observable();
        }

        if (args) loadFromObj(args);

        for (var i = 0; i < type.args.length; i++) {
          self[type.args[i].name].subscribe(viewModel.createWizard.guessFieldTypes);
        }
      }

      var loadFromObj = function (args) {
        for (var attr in args) {
          self[attr] = ko.mapping.fromJS(args[attr]);
        }
      }

      self.getArguments = function () {
        return type.args;
      }

      self.isCustomizable = function () {
        return type.isCustomizable;
      }

      init();
    }

    var Source = function (vm) {
      var self = this;

      self.name = ko.observable('');
      self.sample = ko.observableArray();
      self.sampleCols = ko.observableArray();

      self.inputFormat = ko.observable('file');
      self.inputFormat.subscribe(function(val) {
        if (val == 'query') {
          self.getDocuments();
        }
      });
      self.inputFormats = ko.observableArray(['file', 'text', 'table', 'query', 'dbms', 'manual']);

      // File
      self.path = ko.observable('');
      self.path.subscribe(function(val) {
        if (val) {
          vm.createWizard.guessFormat();
        }
      })

      // Table
      self.table = ko.observable('');
      self.tableName = ko.computed(function() {
        return self.table().indexOf('.') > 0 ? self.table().split('.', 2)[1] : self.table();
      });
      self.databaseName = ko.computed(function() {
        return self.table().indexOf('.') > 0 ? self.table().split('.', 2)[0] : 'default';
      });

      // Queries
      self.query = ko.observable('');
      self.queries = ko.observableArray([]);
      self.draggedQuery = ko.observable();
      self.getDocuments = function() {
        $.get('/desktop/api2/docs/', {
          type: 'query-hive',
          include_trashed: false,
          sort: '-last_modified',
          limit: 100
        }, function(data) {
          if (data && data.documents) {
            var queries = [];
            $.each(data.documents, function(index, query) {
              queries.push(ko.mapping.fromJS(query));
            });
            self.queries(queries);
          }
        });
      };

      var waitForRendered = -1;
      self.selectQuery = function () {
        window.clearTimeout(waitForRendered);
        waitForRendered = window.setTimeout(function(){
          if (self.draggedQuery()){
            self.query(ko.utils.arrayFilter(self.queries(), function(q) {
              return q.id() === self.draggedQuery();
            })[0]);
          }
        }, 50);
      }

      self.format = ko.observable();

      self.show = ko.computed(function() {
        if (self.inputFormat() == 'file') {
          return self.path().length > 0;
        } else if (self.inputFormat() == 'table') {
          return self.table().length > 0;
        } else if (self.inputFormat() == 'query') {
          return self.query();
        }
      });

      self.defaultName = ko.computed(function() {
        var name = ''

        if (self.inputFormat() == 'file') {
          if (self.path()) {
            name = self.path().split('/').pop().split('.')[0];
          }
        } else if (self.inputFormat() == 'table') {
          if (self.table().split('.', 2).length == 2) {
            name = self.tableName();
          }
        } else if (self.inputFormat() == 'query') {
          if (self.query()) {
            name = val.name();
          }
        }

        return name.replace(' ', '_');
      });
      self.defaultName.subscribe(function(newVal) {
        vm.createWizard.destination.name(newVal);
      });
    };

    var Destination = function (vm) {
      var self = this;

      self.name = ko.observable('');

      self.ouputFormat = ko.observable('table');
      self.ouputFormats = ko.observableArray(['table', 'index', 'file']);

      self.format = ko.observable();
      self.columns = ko.observableArray();

      // Table
      self.tableFormat = ko.observable('text');
      self.tableFormats = ko.observableArray(['text', 'parquet', 'json', 'orc', 'kudu']);
      self.hasHeader = ko.observable(false); // ?
      self.bulkEditColumns = ko.observable(false);
      self.partitionColumns = ko.observableArray();

      // Index
    };

    var CreateWizard = function (vm) {
      var self = this;
      var guessFieldTypesXhr;

      self.fileType = ko.observable();
      self.fileType.subscribe(function (newType) {
        if (self.source.format()) {
          self.source.format().type(newType.name);
        }
      });

      self.operationTypes = ${operators_json | n};

      self.fieldTypes = ${fields_json | n}.solr;
      self.hiveFieldTypes = ${fields_json | n}.hive;
      self.fileTypes = ${file_types_json | n};


      self.show = ko.observable(true);
      self.showCreate = ko.observable(false);

      self.source = new Source(vm);
      self.destination = new Destination(vm);

      self.editorId = ko.observable();
      self.jobId = ko.observable();
      self.editorVM = null;

      self.indexingStarted = ko.observable(false);

      self.isNameAvailable = ko.computed(function () {
        var name = self.source.name();
        return viewModel && viewModel.collectionNameAvailable(name) && name.length > 0;
      });

      self.readyToIndex = ko.computed(function () {
        var validFields = self.destination.columns().length;
        return self.destination.name().length > 0 && validFields;
      });

      self.source.format.subscribe(function () {
        for (var i = 0; i < self.fileTypes.length; i++) {
          if (self.fileTypes[i].name == self.source.format().type()) {
            self.fileType(self.fileTypes[i]);
            break;
          }
        }

        if (self.source.format().type) {
          self.source.format().type.subscribe(function (newType) {
            self.source.format(new FileType(newType));
            self.destination.columns.removeAll();
            self.guessFieldTypes();
          });
        }
      });

      self.isGuessingFormat = ko.observable(false);
      self.guessFormat = function () {
        self._guessIndexFormat();
      }
      self._guessIndexFormat = function () {
        self.isGuessingFormat(true);
        self.destination.columns.removeAll();
        $.post("${ url('indexer:guess_format') }", {
          "fileFormat": ko.mapping.toJSON(self.source)
        }, function (resp) {
          var newFormat = ko.mapping.fromJS(new FileType(resp['type'], resp));
          self.source.format(newFormat);
          self.guessFieldTypes();

          self.isGuessingFormat(false);
          viewModel.wizardEnabled(true);
        }).fail(function (xhr, textStatus, errorThrown) {
          $(document).trigger("error", xhr.responseText);
          viewModel.isLoading(false);
        });
      };

      self.isGuessingFieldTypes = ko.observable(false);
      self.guessFieldTypes = function () {
        self._guessIndexFieldTypes();
      }

      self._guessIndexFieldTypes = function () {
        if (guessFieldTypesXhr) {
          guessFieldTypesXhr.abort();
        }
        self.isGuessingFieldTypes(true);
        guessFieldTypesXhr = $.post("${ url('indexer:guess_field_types') }", {
          "fileFormat": ko.mapping.toJSON(self.source)
        }, function (resp) {
          resp.columns.forEach(function (entry, i, arr) {
            arr[i] = loadField(entry);
          });
          self.source.sampleCols(resp.sample_cols);
          self.source.sample(resp.sample);
          self.destination.columns(resp.columns);
          self.isGuessingFieldTypes(false);
        }).fail(function (xhr, textStatus, errorThrown) {
          $(document).trigger("error", xhr.responseText);
          self.isGuessingFieldTypes(false);
          viewModel.isLoading(false);
        });
      };

      self.isIndexing = ko.observable(false);
      self.indexingError = ko.observable(false);
      self.indexingSuccess = ko.observable(false);
      self.indexFile = function () {
        if (! self.readyToIndex()) {
          return;
        }

        self.indexingStarted(true);
        viewModel.isLoading(true);
        self.isIndexing(true);

        $.post("${ url('indexer:importer_submit') }", {
          "source": ko.mapping.toJSON(self.source),
          "destination": ko.mapping.toJSON(self.destination)
        }, function (resp) {
          self.showCreate(true);
          self.editorId(resp.history_id);
          self.jobId(resp.handle.id);
          $('#notebook').html($('#notebook-progress').html());

          self.editorVM = new EditorViewModel(resp.history_uuid, '', {
            user: '${ user.username }',
            userId: ${ user.id },
            languages: [{name: "Java", type: "java"}, {name: "Hive SQL", type: "hive"}], // TODO reuse
            snippetViewSettings: {
              java : {
                snippetIcon: 'fa-file-archive-o '
              },
              hive: {
                placeHolder: '${ _("Example: SELECT * FROM tablename, or press CTRL + space") }',
                aceMode: 'ace/mode/hive',
                snippetImage: '${ static("beeswax/art/icon_beeswax_48.png") }',
                sqlDialect: true
              },
              impala: {
                placeHolder: '${ _("Example: SELECT * FROM tablename, or press CTRL + space") }',
                aceMode: 'ace/mode/impala',
                snippetImage: '${ static("impala/art/icon_impala_48.png") }',
                sqlDialect: true
              }
            }
          });
          self.editorVM.editorMode(true);
          ko.cleanNode($("#notebook")[0]);
          ko.applyBindings(self.editorVM, $("#notebook")[0]);

          self.editorVM.openNotebook(resp.history_uuid, null, true, function(){
            self.editorVM.selectedNotebook().snippets()[0].progress.subscribe(function(val){
              if (val == 100){
                self.indexingStarted(false);
                self.isIndexing(false);
                self.indexingSuccess(true);
              }
            });
            self.editorVM.selectedNotebook().snippets()[0].status.subscribe(function(val){
              if (val == 'failed'){
                self.isIndexing(false);
                self.indexingStarted(false);
                self.indexingError(true);
              }
            });
            self.editorVM.selectedNotebook().snippets()[0].checkStatus();
          });
          viewModel.isLoading(false);
        }).fail(function (xhr, textStatus, errorThrown) {
          $(document).trigger("error", xhr.responseText);
          viewModel.isLoading(false);
          self.indexingStarted(false);
          self.isIndexing(false);
        });
      }

      self.removeOperation = function (operation, operationList) {
        operationList.remove(operation);
      }

      self.addOperation = function (field) {
        field.operations.push(new Operation("split"));
      }

      self.load = function (state) {
        self.source.name(state.name);
        self.source.show(state.show);
        self.source.path(state.path);
        self.destination.columns.removeAll();
        if (state.format && 'type' in state.format) {
          var koFormat = ko.mapping.fromJS(new FileType(state.format.type, state.format));
          self.source.format(koFormat);
        }
        if (state.columns) state.columns.forEach(function (currCol) {
          self.destination.columns.push(loadField(currCol));
        });
      }
    };

    var loadField = function (currField) {
      var koField = ko.mapping.fromJS(currField);

      koField.operations.removeAll();

      currField.operations.forEach(function (operationData) {
        var operation = new Operation(operationData.type);
        operation.load(operationData);

        koField.operations.push(operation);
      });

      return koField;
    }

    var IndexerViewModel = function (options) {
      var self = this;

      self.apiHelper = ApiHelper.getInstance(options);
      self.assistAvailable = ko.observable(true);
      self.isLeftPanelVisible = ko.observable();
      self.apiHelper.withTotalStorage('assist', 'assist_panel_visible', self.isLeftPanelVisible, true);

      // wizard related
      self.wizardEnabled = ko.observable(false);
      self.currentStep = ko.observable(1);
      self.previousStepVisible = ko.pureComputed(function(){
        return self.currentStep() > 1;
      });
      self.nextStepVisible = ko.pureComputed(function(){
        return self.currentStep() < 3 && self.wizardEnabled();
      });
      self.nextStep = function () {
        if (self.nextStepVisible()){
          self.currentStep(self.currentStep()+1);
        }
      }
      self.previousStep = function () {
        if (self.previousStepVisible()){
          self.currentStep(self.currentStep()-1);
        }
      }

      self.collections = ${ indexes_json | n }.
      filter(function (index) {
        return index.type == 'collection';
      });

      self.createWizard = new CreateWizard(self);
      self.isLoading = ko.observable(false);

      self.collectionNameAvailable = function (name) {
        var matchingCollections = self.collections.filter(function (collection) {
          return collection.name == name;
        });

        return matchingCollections.length == 0;
      }
    };

    var viewModel;

    $(document).ready(function () {
      var options = {
        user: '${ user.username }',
        i18n: {
          errorLoadingDatabases: "${ _('There was a problem loading the databases') }",
          errorLoadingTablePreview: "${ _('There was a problem loading the table preview.') }"
        }
      }
      viewModel = new IndexerViewModel(options);
      ko.applyBindings(viewModel);

      var draggableMeta = {};
      huePubSub.subscribe('draggable.text.meta', function (meta) {
        draggableMeta = meta;
      });

      huePubSub.subscribe('split.panel.resized', function () {
        $('.form-actions').width($('.content-panel').width() - 50);
      });

      $('.form-actions').width($('.content-panel').width() - 50);


      $('.content-panel').droppable({
        accept: ".draggableText",
        drop: function (e, ui) {
          var text = ui.helper.text();
          var generatedName = 'idx';
          switch (draggableMeta.type){
            case 'sql':
              if (draggableMeta.table !== ''){
                generatedName += draggableMeta.table;
                viewModel.createWizard.source.inputFormat('table');
                viewModel.createWizard.source.table(draggableMeta.table);
              }
              break;
            case 'hdfs':
              generatedName += draggableMeta.definition.name;
                viewModel.createWizard.source.inputFormat('file');
                viewModel.createWizard.source.path(draggableMeta.definition.path);
              break;
            case 'document':
              if (draggableMeta.definition.type === 'query-hive'){
                generatedName += draggableMeta.definition.name;
                viewModel.createWizard.source.inputFormat('query');
                viewModel.createWizard.source.draggedQuery(draggableMeta.definition.id);
              }
              break;
          }
          if (generatedName !== 'idx' && viewModel.createWizard.source.name() === ''){
            viewModel.createWizard.source.name(generatedName);
          }
          else {
            if (draggableMeta.table !== ''){
              viewModel.createWizard.source.selectQuery();
            }
          }
        }
      });
    });
  })();
</script>
</span>
${ commonfooter(request, messages) | n,unicode }

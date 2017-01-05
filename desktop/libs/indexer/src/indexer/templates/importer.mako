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

%if not is_embeddable:
${ commonheader(_("Importer"), "indexer", user, request, "60px") | n,unicode }

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
<script src="${ static('desktop/ext/js/selectize.min.js') }"></script>
<script src="${ static('desktop/js/ko.selectize.js') }"></script>

${ assist.assistJSModels() }

<script src="${ static('notebook/js/notebook.ko.js') }"></script>

<link rel="stylesheet" href="${ static('notebook/css/notebook.css') }">
<link rel="stylesheet" href="${ static('notebook/css/notebook-layout.css') }">
${ assist.assistPanel() }

<link rel="stylesheet" href="${ static('desktop/ext/css/selectize.css') }">
%endif

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

##   .step1 label > div:first-child {
##     width: 50px;
##     display: inline-block;
##   }

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

  #importerNotebook {
    height: 5px;
    margin-top: 10px;
  }

</style>

<span id="importerComponents" class="notebook">
<div class="navbar navbar-inverse navbar-fixed-top">
  <div class="navbar-inner">
    <div class="container-fluid">
      <div class="nav-collapse">
        <ul class="nav">
          <li class="currentApp">
            <a href="${ url('indexer:importer') }">
              <i class="fa fa-database app-icon"></i> ${_('Importer')}</a>
            </a>
          </li>
        </ul>
      </div>
    </div>
  </div>
</div>

%if not is_embeddable:
<a title="${_('Toggle Assist')}" class="pointer show-assist" data-bind="visible: !$root.isLeftPanelVisible() && $root.assistAvailable(), click: function() { $root.isLeftPanelVisible(true); }">
  <i class="fa fa-chevron-right"></i>
</a>
%endif

<div class="main-content">
  <div class="vertical-full container-fluid" data-bind="style: { 'padding-left' : $root.isLeftPanelVisible() ? '0' : '20px' }">
    <div class="vertical-full">
      <div class="vertical-full row-fluid panel-container">
        %if not is_embeddable:
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
        %endif
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
      <li data-bind="css: { 'active': currentStep() == 1, 'complete': currentStep() > 1 }, click: function() { currentStep(1) }">
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
          <!-- ko if: currentStep() < 3 -->
            <!-- ko if: createWizard.isGuessingFieldTypes -->
              <span class="fa fa-spinner fa-spin"></span>
            <!-- /ko -->
            <!-- ko ifnot: createWizard.isGuessingFieldTypes -->
              2
            <!-- /ko -->
          <!-- /ko -->
        </div>
        <div class="caption">${ _('Move it to ') }<span data-bind="text: createWizard.destination.outputFormat"></span></div>
      </li>
    </ol>


    <!-- ko if: currentStep() == 1 -->
    <div class="card step1">
      <h3 class="card-heading simple">${_('Source')}</h3>
      <div class="card-body">
        <div>
          <div class="control-group">
            <label for="sourceType" class="control-label"><div>${ _('Type') }</div>
              <select id="sourceType" data-bind="selectize: createWizard.source.inputFormats, value: createWizard.source.inputFormat, optionsText: 'name', optionsValue: 'value'"></select>
            </label>
          </div>

          <div class="control-group" data-bind="visible: createWizard.source.inputFormat() == 'file'">
            <label for="path" class="control-label"><div>${ _('Path') }</div>
              <input type="text" class="form-control path input-xxlarge" data-bind="value: createWizard.source.path, filechooser: createWizard.source.path, filechooserOptions: { linkMarkup: true, skipInitialPathIfEmpty: true, openOnFocus: true }" placeholder="${ _('Click or drag & drop') }">
            </label>
          </div>

          <div class="control-group" data-bind="visible: createWizard.source.inputFormat() == 'table'">
            <label for="path" class="control-label"><div>${ _('Table') }</div>
              <input type="text" data-bind="value: createWizard.source.table, hivechooser: createWizard.source.table, skipColumns: true" placeholder="${ _('Table name or <database>.<table>') }">
            </label>
          </div>

          <div class="control-group" data-bind="visible: createWizard.source.inputFormat() == 'query'">
            <label for="path" class="control-label"><div>${ _('Query') }</div>
              <select data-bind="selectize: createWizard.source.queries, value: createWizard.source.query, optionsText: 'name', optionsAfterRender: createWizard.source.selectQuery"></select>
            </label>
          </div>
        </div>
      </div>
    </div>

    <!-- ko if: createWizard.source.show() && createWizard.source.inputFormat() != 'manual' -->
    <div class="card step1">
      <!-- ko if: createWizard.isGuessingFormat -->
      <h3 class="card-heading simple">${_('Guessing format...')} <i class="fa fa-spinner fa-spin"></i></h3>
      <!-- /ko -->
      <!-- ko ifnot: createWizard.isGuessingFormat -->
      <h3 class="card-heading simple">${_('Format')}</h3>
      <div class="card-body">
        <label data-bind="visible: ! createWizard.prefill.source_type"><div>${_('File Type')}</div> <select data-bind="selectize: $root.createWizard.fileTypes, value: $root.createWizard.fileTypeName, optionsText: 'description', optionsValue: 'name'"></select></label>
        <span data-bind="with: createWizard.source.format, visible: createWizard.source.show">
          <!-- ko template: {name: 'format-settings'} --> <!-- /ko -->
        </span>
      </div>
      <!-- /ko -->
    </div>

    <div class="card step1">
      <!-- ko ifnot: createWizard.isGuessingFormat -->
      <!-- ko if: createWizard.isGuessingFieldTypes -->
      <h3 class="card-heading simple">${_('Generating preview...')} <i class="fa fa-spinner fa-spin"></i></h3>
      <!-- /ko -->
      <!-- ko ifnot: createWizard.isGuessingFieldTypes -->
      <h3 class="card-heading simple">${_('Preview')}</h3>
      <div class="card-body">
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
              <td data-bind="truncatedText: $data"></td>

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
      <!-- /ko -->
    </div>
    <!-- /ko -->

    <!-- /ko -->

    <!-- ko if: currentStep() == 2 -->

      <!-- ko with: createWizard.destination -->

      <div class="card step2">
        <h3 class="card-heading simple">${_('Destination')}</h3>
        <div class="card-body">
          <div class="control-group">
            <label for="destinationType" class="control-label" data-bind="visible: ! $parent.createWizard.prefill.target_type"><div>${ _('Type') }</div>
              <select id="destinationType" data-bind="selectize: outputFormats, value: outputFormat, optionsValue: 'value', optionsText: 'name'"></select>
            </label>

            <label for="collectionName" class="control-label"><div>${ _('Name') }</div>
              <!-- ko if: outputFormat() != 'table' && outputFormat() != 'database' -->
                <input type="text" class="form-control input-xlarge" id="collectionName" data-bind="value: name, valueUpdate: 'afterkeydown'" placeholder="${ _('Name') }">
              <!-- /ko -->

              <!-- ko if: outputFormat() == 'table' || outputFormat() == 'database' -->
                <label for="path" class="control-label">
                  <input type="text" data-bind="value: name, hivechooser: name, skipColumns: true, valueUpdate: 'afterkeydown'" placeholder="${ _('Table name or <database>.<table>') }">
                </label>
              <!-- /ko -->

              <span class="help-inline muted" data-bind="visible: ! isTargetExisting()">
                ${ _('Create a new ') } <span data-bind="text: outputFormat"></span>
              </span>
              <span class="help-inline muted" data-bind="visible: isTargetExisting()">
                ${ _('Adding data to the existing ') } <span data-bind="text: outputFormat"></span>
                <a href="javascript:void(0)" data-bind="attr: { href: existingTargetUrl() }, text: name" target="_blank"></a>
              </span>
            </label>
          </div>
        </div>
      </div>


        <!-- ko if: outputFormat() == 'table' -->
        <div class="card step2">
          <h3 class="card-heading simple">${_('Properties')}</h3>
          <div class="card-body">
            <input type="text" class="form-control input-xlarge" data-bind="value: description, valueUpdate: 'afterkeydown'" placeholder="${ _('Description') }">

            <div class="control-group">
              <label for="destinationFormat" class="control-label"><div>${ _('Format') }</div>
                <select id="destinationFormat" data-bind="selectize: tableFormats, value: tableFormat, optionsValue: 'value', optionsText: 'name'"></select>
              </label>
            </div>

            <label class="checkbox">
              <input type="checkbox" data-bind="checked: useDefaultLocation"> ${_('Default location')}
            </label>
            <span data-bind="visible: ! useDefaultLocation()">
              <label for="path" class="control-label"><div>${ _('External location') }</div>
                <input type="text" class="form-control path input-xxlarge" data-bind="value: nonDefaultLocation, filechooser: nonDefaultLocation, filechooserOptions: { linkMarkup: true, skipInitialPathIfEmpty: true }, valueUpdate: 'afterkeydown'">
              </label>
            </span>

            <label class="checkbox">
              <input type="checkbox" data-bind="checked: importData, disable: ! useDefaultLocation() && $parent.createWizard.source.path() == nonDefaultLocation();"> ${_('Import data')}
            </label>

            <label class="checkbox">
              <input type="checkbox" data-bind="checked: useCustomDelimiters"> ${_('Custom char delimiters')}
            </label>
            <span data-bind="visible: useCustomDelimiters">
              <div class="control-group">
                <label for="fieldDelimiter" class="control-label"><div>${ _('Field') }</div>
                  <select id="fieldDelimiter" data-bind="selectize: $root.createWizard.customDelimiters, selectizeOptions: { create: true, maxLength: 2 }, value: customFieldDelimiter, optionsValue: 'value', optionsText: 'name'"></select>
                </label>
              </div>
              <div class="control-group">
                <label for="collectionDelimiter" class="control-label"><div>${ _('Array, Map') }</div>
                  <select id="collectionDelimiter" data-bind="selectize: $root.createWizard.customDelimiters, selectizeOptions: { create: true, maxLength: 2 }, value: customCollectionDelimiter, optionsValue: 'value', optionsText: 'name'"></select>
                </label>
              </div>
              <div class="control-group">
                <label for="structDelimiter" class="control-label"><div>${ _('Struct') }</div>
                  <select id="structDelimiter" data-bind="selectize: $root.createWizard.customDelimiters, selectizeOptions: { create: true, maxLength: 2 }, value: customMapDelimiter, optionsValue: 'value', optionsText: 'name'"></select>
                </label>
              </div>
              <input type="text" data-bind="value: customRegexp"> ${_('Regexp')}
            </span>

            <div class="control-group" data-bind="visible: tableFormat() == 'kudu'">
              <label for="kuduPks" class="control-label"><div>${ _('Primary keys') }</div>
                ## At least one selected
                <select id="kuduPks" data-bind="selectize: columns, selectedOptions: primaryKeys, optionsValue: 'name', optionsText: 'name'" size="3" multiple="true"></select>
              </label>
            </div>

            <div class="row" style="margin-left: 8px">
              <div class="span3">
                <input type="checkbox" data-bind="checked: hasHeader">
                ${_('Use first row as column names')} <a class="btn disable-feedback"><i class="fa fa-outdent"></i></a>
              </div>
              <div class="span3" data-bind="click: function() { alert('Hello'); }">
                ${ _('Bulk edit column names') }<a class="btn"><i class="fa fa-edit"></i></a>
              </div>
            </div>

            <label for="tablePartitions" class="control-label"><div>${ _('Partitions') }</div>

              <!-- ko if: tableFormat() != 'kudu' -->
              <div class="form-inline" data-bind="foreach: partitionColumns">
                <div data-bind="template: { name: 'table-field-template', data: $data }" class="margin-top-10 field"></div>
                <a data-bind="click: function() { $parent.partitionColumns.remove($data); }"><i class="fa fa-minus"></i></a>
              </div>
              <a data-bind="click: function() { partitionColumns.push($root.loadField({operations: [], nested: [], name: '', level: 0, type: '', keyType: '', showProperties: false, isPartition: true})); }" class="pointer margin-left-20" title="${_('Add Operation')}"><i class="fa fa-plus"></i> ${_('Add partition')}</a>
              <!-- /ko -->

              <!-- ko if: tableFormat() == 'kudu' -->
              <div class="form-inline" data-bind="foreach: kuduPartitionColumns">
                ${ _('Columns') }
                <select id="kuduPks" data-bind="selectize: $parent.primaryKeys, selectedOptions: columns" size="3" multiple="true"></select>
                <select data-bind="selectize: ['RANGE BY', 'HASH'], value: name"></select>

                <!-- ko if: name() == 'HASH' -->
                  <input type="number" data-bind="value: int_val">
                <!-- /ko -->

                <!-- ko if: name() == 'RANGE BY' -->
                  <div class="form-inline" data-bind="foreach: range_partitions">
                    <!-- ko if: name() == 'VALUES' -->
                      <input type="input" data-bind="value: lower_val">
                      <input type="checkbox" data-bind="checked: include_lower_val">
                      <
                      <span data-bind="text: '=', visible: include_lower_val"></span>
                      <select data-bind="selectize: ['VALUES', 'VALUE'], value: name"></select>
                      <
                      <span data-bind="text: '=', visible: include_upper_val"></span>
                      <input type="input" data-bind="value: upper_val">
                      <input type="checkbox" data-bind="checked: include_upper_val">
                    <!-- /ko -->

                    <!-- ko if: name() == 'VALUE' -->
                      <select data-bind="selectize: ['VALUES', 'VALUE'], value: name"></select>
                      <div class="form-inline" data-bind="foreach: values">
                        <input type="text" data-bind="value: $data">
                        <a data-bind="click: function() { $parent.values.remove($data); }"><i class="fa fa-minus"></i></a>
                      </div>
                      <a data-bind="click: function() { values.push(''); }"><i class="fa fa-plus"></i></a>
                    <!-- /ko -->
                    <a data-bind="click: function() { $parent.range_partitions.remove($data); }"><i class="fa fa-minus"></i></a>
                  </div>

                  <a data-bind="click: function() { range_partitions.push(ko.mapping.fromJS({values: [''], name: 'VALUES', lower_val: 0, include_lower_val: true, upper_val: 1, include_upper_val: true})); }"><i class="fa fa-plus"></i></a>
                <!-- /ko -->

                <a data-bind="click: function() { $parent.kuduPartitionColumns.remove($data); }"><i class="fa fa-minus"></i></a>
                <a data-bind="click: function() { $parent.kuduPartitionColumns.push(ko.mapping.fromJS({columns: [], range_partitions: [], name: 'HASH', int_val: 16})); }" class="pointer margin-left-20" title="${_('Add Operation')}"><i class="fa fa-plus"></i> ${_('Add partition')}</a>
              <!-- /ko -->
            </div>
            <a data-bind="click: function() { kuduPartitionColumns.push(ko.mapping.fromJS({columns: [], range_partitions: [], name: 'HASH', int_val: 16})); }" class="pointer margin-left-20" title="${_('Add Operation')}"><i class="fa fa-plus"></i> ${_('Add partition')}</a>
            <!-- /ko -->

            </label>
          </div>
        </div>
        <!-- /ko -->

        <!-- ko if: outputFormat() == 'table' || outputFormat() == 'index' -->
          <div class="card step2">
            <h3 class="card-heading simple">${_('Fields')}</h3>
            <div class="card-body">
              <form class="form-inline" data-bind="foreach: columns">
                <!-- ko if: $parent.outputFormat() == 'table' -->
                  <div data-bind="template: { name: 'table-field-template', data: $data }" class="margin-top-10 field"></div>
                <!-- /ko -->

                <!-- ko if: $parent.outputFormat() == 'index' -->
                  <div data-bind="template: { name: 'index-field-template', data: $data }" class="margin-top-10 field"></div>
                <!-- /ko -->
              </form>

              <!-- ko if: $parent.createWizard.source.inputFormat() == 'manual' && outputFormat() == 'table' -->
                <a data-bind="click: function() { columns.push($root.loadField({operations: [], nested: [], name: '', level: 0, type: '', showProperties: false, isPartition: true})); }" class="pointer margin-left-20" title="${_('Add Operation')}"><i class="fa fa-plus"></i> ${_('Add Field')}</a>
              <!-- /ko -->
            </div>
          </div>
        <!-- /ko -->

        <!-- ko if: outputFormat() == 'database' -->
          <div class="card step2">
            <h3 class="card-heading simple">${_('Properties')}</h3>
            <div class="card-body">
              <input type="text" class="form-control input-xlarge" data-bind="value: description, valueUpdate: 'afterkeydown'" placeholder="${ _('Description') }">

              <label class="checkbox">
                <input type="checkbox" data-bind="checked: useDefaultLocation"> ${_('Default location')}
              </label>
              <span data-bind="visible: ! useDefaultLocation()">
                <label for="path" class="control-label"><div>${ _('External location') }</div>
                  <input type="text" class="form-control path input-xxlarge" data-bind="value: nonDefaultLocation, filechooser: nonDefaultLocation, filechooserOptions: { linkMarkup: true, skipInitialPathIfEmpty: true }, valueUpdate: 'afterkeydown'">
                </label>
              </span>
              </div>
          </div>
        <!-- /ko -->


    <!-- /ko -->

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

      <div id="importerNotebook"></div>
    </div>
  </div>
</script>


<script type="text/html" id="format-settings">
  <!-- ko foreach: {data: getArguments(), as: 'argument'} -->
    <!-- ko template: {name: 'arg-' + argument.type, data:{description: argument.description, value: $parent[argument.name]}}--><!-- /ko -->
  <!-- /ko -->
</script>


<script type="text/html" id="table-field-template">
  <label data-bind="visible: level() == 0 || ($parent.type() != 'array' && $parent.type() != 'map')">${ _('Name') }
    <input type="text" class="input-large" placeholder="${ _('Field name') }" data-bind="value: name">
  </label>

  <label>${ _('Type') }
  <!-- ko if: ! (level() > 0 && $parent.type() == 'map') -->
    <select class="input-small" data-bind="selectize: $root.createWizard.hiveFieldTypes, value: type"></select>
  <!-- /ko -->
  <!-- ko if: level() > 0 && $parent.type() == 'map' -->
    <select class="input-small" data-bind="selectize: $root.createWizard.hivePrimitiveFieldTypes, value: keyType"></select>
    <select class="input-small" data-bind="selectize: $root.createWizard.hiveFieldTypes, value: type"></select>

  <!-- /ko -->
  <input type="number" class="input-small" placeholder="${ _('Length') }" data-bind="value: length, visible: type() == 'varchar' || type() == 'char'">

  <!-- ko if: type() == 'array' || type() == 'map' || type() == 'struct' -->
    <div data-bind="template: { name: 'table-field-template', foreach: nested }">
    </div>
    <a data-bind="click: function() { nested.push($root.loadField({operations: [], nested: [], name: '', type: '', 'keyType': '', level: level() + 1})); }, visible: type() == 'struct'"><i class="fa fa-plus"></i></a>
  <!-- /ko -->
  </label>

  <span data-bind="visible: level() == 0 || ($parent.type() != 'array' && $parent.type() != 'map')">
    ${_('Comment')}
  </span>

  <!-- ko if: level() > 0 && $parent.type() == 'struct' && $parent.nested().length > 1 -->
    <a data-bind="click: function() { $parent.nested.remove($data); }"><i class="fa fa-minus"></i></a>
  <!-- /ko -->

  <!-- ko if: level() == 0 && typeof isPartition === 'undefined'-->
    <label data-bind="text: $root.createWizard.source.sample()[0][$index()]"></label>
    <label data-bind="text: $root.createWizard.source.sample()[1][$index()]"></label>
  <!-- /ko -->
</script>


<script type="text/html" id="index-field-template">
  <label>${ _('Name') }
    <input type="text" class="input-large" placeholder="${ _('Field name') }" data-bind="value: name">
  </label>
  <label>${ _('Type') }
    <select class="input-small" data-bind="selectize: $root.createWizard.fieldTypes, value: type"></select>
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
    <select data-bind="selectize: $root.createWizard.operationTypes.map(function(o){return o.name}), value: operation.type"></select>
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
    <!-- ko template: {name: 'arg-' + argument.type, data: {description: argument.description, value: $parent.operation.settings()[argument.name]}}--><!-- /ko -->
  <!-- /ko -->
</script>

<script type="text/html" id="arg-text">
  <label>
    <div data-bind="text: description"></div>
    <input type="text" class="input-small" data-bind="attr: {placeholder: description}, value: value">
  </label>
</script>

<script type="text/html" id="arg-text-delimiter">
  <label>
    <div data-bind="text: description"></div>
    <select data-bind="selectize: $root.createWizard.customDelimiters, selectizeOptions: { create: true, maxLength: 2 }, value: value, optionsValue: 'value', optionsText: 'name', attr: {placeholder: description}"></select>
  </label>
</script>

<script type="text/html" id="arg-checkbox">
  <label>
    <input type="checkbox" data-bind="checked: value">
    <div data-bind="text: description"></div>
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

<script type="text/html" id="importerNotebook-progress">
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

    var Source = function (vm, wizard) {
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
      self.inputFormats = ko.observableArray([
          {'value': 'file', 'name': 'File'},
          {'value': 'table', 'name': 'Table'},
          {'value': 'text', 'name': 'Paste Text'},
          {'value': 'query', 'name': 'SQL Query'},
          {'value': 'dbms', 'name': 'DBMS'},
          {'value': 'manual', 'name': 'Manually'},
      ]);
      if (wizard.prefill.source_type) {
        self.inputFormats([
            {'value': 'file', 'name': 'File'},
            {'value': 'manual', 'name': 'Manually'},
        ]);
        if (wizard.prefill.source_type() == 'manual') {
          self.inputFormat(wizard.prefill.source_type());
        }
      }

      // File
      self.path = ko.observable('');
      self.path.subscribe(function(val) {
        if (val) {
          vm.createWizard.guessFormat();
          vm.createWizard.destination.nonDefaultLocation(val);
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
        } else if (self.inputFormat() == 'manual') {
          return true;
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
            name = self.table();
          }
        } else if (self.inputFormat() == 'query') {
          if (self.query()) {
            name = val.name();
          }
        } else if (self.inputFormat() == 'manual') {
          name = wizard.prefill.target_path ? wizard.prefill.target_path() + '.' : '';
        }

        return name.replace(' ', '_');
      });
      self.defaultName.subscribe(function(newVal) {
        vm.createWizard.destination.name(newVal);
      });
    };

    var Destination = function (vm, wizard) {
      var self = this;

      self.name = ko.observable('');
      self.name.subscribe(function (name) {
        var exists = false;

        if (name.length == 0) {
          self.isTargetExisting(false);
        }
        else if (self.outputFormat() == 'file') {
          // Todo
          // self.path()
        }
        else if (self.outputFormat() == 'table') {
          $.get("/beeswax/api/autocomplete/" + self.databaseName() + '/' + self.tableName(), function (data) {
            self.isTargetExisting(data.code != 500);
          }).fail(function (xhr, textStatus, errorThrown) { self.isTargetExisting(false); });
        }
        else if (self.outputFormat() == 'index') {
          $.post("/search/get_collection", {
              name: self.name()
          }, function (data) {
            self.isTargetExisting(data.status == 0);
          }).fail(function (xhr, textStatus, errorThrown) { self.isTargetExisting(false); });
        }
      });

      self.description = ko.observable('');
      self.outputFormat = ko.observable('table');
      self.outputFormatsList = ko.observableArray([
          {'name': 'Table', 'value': 'table'},
          {'name': 'Solr index', 'value': 'index'},
          {'name': 'File', 'value': 'file'},
          {'name': 'Database', 'value': 'database'},
      ]);
      self.outputFormats = ko.computed(function() {
        return $.grep(self.outputFormatsList(), function(format) {
          if (format.value == 'database' && wizard.source.inputFormat() != 'manual') {
            return false;
          }
          else if (format.value == 'file' && wizard.source.inputFormat() != 'manual') {
            return false;
          }
          return true;
        })
      });
      if (wizard.prefill.target_type) {
        self.outputFormat(wizard.prefill.target_type());
        if (wizard.prefill.target_type() == 'database') {
          vm.currentStep(2);
        };
      }

      self.format = ko.observable();
      self.columns = ko.observableArray();

      self.isTargetExisting = ko.observable();
      self.existingTargetUrl = ko.computed(function() { // Should open generic sample popup instead
        if (self.isTargetExisting()) {
          if (self.outputFormat() == 'file') {
            // Todo
            return '';
          }
          else if (self.outputFormat() == 'table') {
            return '/metastore/table/' + self.databaseName() + '/' + self.tableName();
          }
          else if (self.outputFormat() == 'index') {
            return '${ url("indexer:collections") }#edit/' + self.name();
          }
        }
        return '';
      });

      // Table
      self.tableName = ko.computed(function() {
        return self.outputFormat() == 'table' && self.name().indexOf('.') > 0 ? self.name().split('.', 2)[1] : self.name();
      });
      self.databaseName = ko.computed(function() {
        return self.outputFormat() == 'table' && self.name().indexOf('.') > 0 ? self.name().split('.', 2)[0] : 'default';
      });
      self.tableFormat = ko.observable('text');
      self.tableFormats = ko.observableArray([
          {'value': 'text', 'name': 'Text'},
          {'value': 'parquet', 'name': 'Parquet'},
          {'value': 'json', 'name': 'Json'},
          {'value': 'kudu', 'name': 'Kudu'},
          {'value': 'orc', 'name': 'ORC'},
          {'value': 'avro', 'name': 'Avro'},
          {'value': 'rcfile', 'name': 'RCFile'},
          {'value': 'sequencefile', 'name': 'SequenceFile'}
      ]);

      self.partitionColumns = ko.observableArray();
      self.kuduPartitionColumns = ko.observableArray();
      self.primaryKeys = ko.observableArray();

      self.importData = ko.observable(true);
      self.useDefaultLocation = ko.observable(true);
      self.nonDefaultLocation = ko.observable('');

      self.hasHeader = ko.observable(true);

      self.useCustomDelimiters = ko.observable(false);
      self.customFieldDelimiter = ko.observable(',');
      self.customCollectionDelimiter = ko.observable('\\002');
      self.customMapDelimiter = ko.observable('\\003');
      self.customRegexp = ko.observable('');

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

      self.fileTypeName = ko.observable();
      self.fileTypeName.subscribe(function (newType) {
        for (var i = 0; i < self.fileTypes.length; i++) {
          if (self.fileTypes[i].name == newType) {
            self.fileType(self.fileTypes[i]);
            break;
          }
        }
      });

      self.operationTypes = ${operators_json | n};

      self.fieldTypes = ${fields_json | n}.solr;
      self.hivePrimitiveFieldTypes = ${fields_json | n}.hivePrimitive;
      self.hiveFieldTypes = ${fields_json | n}.hive;
      self.fileTypes = ${file_types_json | n};
      self.prefill = ko.mapping.fromJS(${prefill | n});

      self.show = ko.observable(true);
      self.showCreate = ko.observable(false);

      self.source = new Source(vm, self);
      self.destination = new Destination(vm, self);

      self.customDelimiters = ko.observable([
        {'value': ',', 'name': 'Comma (,)'},
        {'value': '\\t', 'name': '^Tab (\\t)'},
        {'value': '\\n', 'name': 'New line'},
        {'value': ' ', 'name': 'Space'},
        {'value': '"', 'name': 'Double Quote'},
        {'value': '\\001', 'name': '^A (\\001)'},
        {'value': '\\002', 'name': '^B (\\002)'},
        {'value': '\\003', 'name': '^C (\\003)'},
      ]);

      self.editorId = ko.observable();
      self.jobId = ko.observable();
      self.editorVM = null;

      self.indexingStarted = ko.observable(false);

      self.readyToIndex = ko.computed(function () {
        var validFields = self.destination.columns().length || self.destination.outputFormat() == 'database';
        return self.destination.name().length > 0 && validFields;
      });

      self.formatTypeSubscribed = false;

      self.source.format.subscribe(function (newVal) {
        for (var i = 0; i < self.fileTypes.length; i++) {
          if (self.fileTypes[i].name == self.source.format().type()) {
            self.fileType(self.fileTypes[i]);
            self.fileTypeName(self.fileTypes[i].name);
            break;
          }
        }

        if (self.source.format().type) {
          if (!self.formatTypeSubscribed) {
            self.formatTypeSubscribed = true;
            self.source.format().type.subscribe(function (newType) {
              self.source.format(new FileType(newType));
              self.destination.columns.removeAll();
              self.guessFieldTypes();
            });
          }
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
          $('#importerNotebook').html($('#importerNotebook-progress').html());

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
          ko.cleanNode($("#importerNotebook")[0]);
          ko.applyBindings(self.editorVM, $("#importerNotebook")[0]);

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
              } else if (val == 'available') {
                var snippet = self.editorVM.selectedNotebook().snippets()[0]; // Could be native to editor at some point
                if (! snippet.result.handle().has_more_statements) {
                  if (self.editorVM.selectedNotebook().onSuccessUrl()) {
                    window.location.href = self.editorVM.selectedNotebook().onSuccessUrl();
                  }
                } else { // Perform last DROP statement execute
                  snippet.execute();
                }
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

      var autoExpand = function(newVal) {
        if ((newVal == 'array' || newVal == 'map' || newVal == 'struct') && koField.nested().length == 0) {
          koField.nested.push(loadField({operations: [], nested: [], name: '', type: '', keyType: '', level: koField.level() + 1}));
        }
      };
      koField.type.subscribe(autoExpand);
      koField.keyType.subscribe(autoExpand);

      return koField;
    }

    var IndexerViewModel = function (options) {
      var self = this;

      self.apiHelper = ApiHelper.getInstance(options);
      self.assistAvailable = ko.observable(true);
      self.isLeftPanelVisible = ko.observable();
      self.apiHelper.withTotalStorage('assist', 'assist_panel_visible', self.isLeftPanelVisible, true);
      self.loadField = loadField;

      // Wizard related
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
          self.currentStep(self.currentStep() + 1);
        }
      }
      self.previousStep = function () {
        if (self.previousStepVisible()){
          self.currentStep(self.currentStep() - 1);
        }
      }

      self.createWizard = new CreateWizard(self);
      self.isLoading = ko.observable(false);
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
      ko.applyBindings(viewModel, $('#importerComponents')[0]);

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

%if not is_embeddable:
${ commonfooter(request, messages) | n,unicode }
%endif

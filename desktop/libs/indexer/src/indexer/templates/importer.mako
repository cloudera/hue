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

  from desktop import conf
  from desktop.views import commonheader, commonfooter, commonshare, commonimportexport, _ko
  from filebrowser.conf import SHOW_UPLOAD_BUTTON
  from beeswax import hive_site
  from impala import impala_flags
  from notebook.conf import ENABLE_SQL_INDEXER

  from indexer.conf import ENABLE_NEW_INDEXER, ENABLE_SQOOP, ENABLE_KAFKA, CONFIG_INDEXER_LIBS_PATH, ENABLE_SCALABLE_INDEXER, ENABLE_ALTUS, ENABLE_ENVELOPE, ENABLE_FIELD_EDITOR
%>

<%namespace name="actionbar" file="actionbar.mako" />

%if not is_embeddable:
${ commonheader(_("Importer"), "indexer", user, request, "60px") | n,unicode }

<link rel="stylesheet" href="${ static('notebook/css/notebook.css') }">
<link rel="stylesheet" href="${ static('notebook/css/notebook-layout.css') }">
%endif

<link rel="stylesheet" href="${ static('indexer/css/importer.css') }" type="text/css">

<style type="text/css">
% if conf.CUSTOM.BANNER_TOP_HTML.get():
  .show-assist {
    top: 110px!important;
  }
  .main-content {
    top: 112px!important;
  }
% endif
</style>

<span id="importerComponents" class="notebook importer-main" data-bind="dropzone: { url: '/filebrowser/upload/file?dest=' + DROPZONE_HOME_DIR, params: {dest: DROPZONE_HOME_DIR}, paramName: 'hdfs_file', onComplete: function(path){ createWizard.source.path(path); }, disabled: '${ not hasattr(SHOW_UPLOAD_BUTTON, 'get') or not SHOW_UPLOAD_BUTTON.get() }' === 'True'  }">
<div class="dz-message" data-dz-message></div>
<div class="navbar hue-title-bar">
  <div class="navbar-inner">
    <div class="container-fluid">
      <div class="nav-collapse">
        <ul class="nav">
          <li class="app-header">
            <a href="${ url('indexer:importer') }">
              <!-- ko if: createWizard.prefill.target_type().length == 0 -->
              <i class="fa fa-database app-icon"></i> ${_('Importer')}
              <!-- /ko -->
              <!-- ko ifnot: createWizard.prefill.target_type().length == 0 -->
                <!-- ko if: createWizard.prefill.target_type() === 'index' -->
                  <i class="fa fa-search app-icon"></i> ${_('Import to index')}
                <!-- /ko -->
                <!-- ko if: createWizard.prefill.target_type() === 'table' -->
                  <i class="fa fa-database app-icon"></i> ${_('Import to table')}
                <!-- /ko -->
                <!-- ko if: createWizard.prefill.target_type() === 'database' -->
                  <i class="fa fa-database app-icon"></i> ${_('Create a new database')}
                <!-- /ko -->
              <!-- /ko -->
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
        <div class="content-panel importer-droppable">
          <div class="content-panel-inner">
          <!-- ko template: 'create-index-wizard' --><!-- /ko -->
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<script type="text/html" id="create-index-wizard">
  <div data-bind="visible: createWizard.show">
    <div class="step-indicator-fixed">
      <ol class="list-inline text-center step-indicator">
        <li data-bind="css: { 'active': currentStep() == 1, 'complete': currentStep() > 1, 'pointer': currentStep() > 1 }, click: function() { currentStep(1) }">
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
          <div class="caption">
            <!-- ko if: createWizard.source.inputFormat() != 'manual' -->
              ${ _('Pick data from ') }<span data-bind="text: createWizard.source.inputFormat"></span>
              <!-- ko if: createWizard.source.inputFormat() == 'file' -->
                <span data-bind="text: createWizard.source.path"></span>
              <!-- /ko -->
              <!-- ko if: createWizard.source.inputFormat() == 'stream' -->
                <!-- ko if: createWizard.source.streamSelection() == 'kafka' -->
                  <span data-bind="text: createWizard.source.kafkaSelectedTopics"></span>
                <!-- /ko -->
                <!-- ko if: createWizard.source.streamSelection() != 'kafka' -->
                  <span data-bind="text: createWizard.source.streamSelection"></span>
                <!-- /ko -->
              <!-- /ko -->
            <!-- /ko -->
            <!-- ko if: createWizard.source.inputFormat() == 'manual' -->
            ${ _('No source data') }
          <!-- /ko -->
          </div>
        </li>

        <li class="arrow muted"><i class="fa fa-fw fa-angle-double-right"></i></li>

        <li data-bind="css: { 'inactive': currentStep() == 1, 'active': currentStep() == 2, 'complete': currentStep() == 3, 'pointer': currentStep() == 1 && !createWizard.isGuessingFormat() && createWizard.source.show() }, click: function() { if (!createWizard.isGuessingFormat() && createWizard.source.show()){ currentStep(2); }}">
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
          <div class="caption">
            <!-- ko if: createWizard.source.inputFormat() != 'manual' -->
              ${ _('Move it to ') }
            <!-- /ko -->
            <!-- ko if: createWizard.source.inputFormat() == 'manual' -->
              ${ _('Create') }
            <!-- /ko -->
            <span data-bind="text: createWizard.destination.outputFormat"></span>
            <span data-bind="text: createWizard.destination.name"></span>
            <!-- ko if: createWizard.destination.outputFormat() == 'altus' -->
              ${ _('in') } <span data-bind="text: createWizard.destination.namespace"></span>
            <!-- /ko -->
          </div>
        </li>
      </ol>
    </div>

    <div class="vertical-spacer"></div>

    <!-- ko if: currentStep() == 1 -->
    <div class="card step">
      <h4>${_('Source')}</h4>
      <div class="card-body">
        <div>
          <div class="control-group" data-bind="visible: createWizard.prefill.target_type().length == 0 || createWizard.prefill.source_type() == 'all'">
            <label for="sourceType" class="control-label"><div>${ _('Type') }</div>
              <select id="sourceType" data-bind="selectize: createWizard.source.inputFormats, value: createWizard.source.inputFormat, optionsText: 'name', optionsValue: 'value'"></select>
            </label>
          </div>
          <div class="control-group" data-bind="visible: createWizard.source.inputFormat() == 'rdbms'">
            <label for="rdbmsMode" class="control-label"><div>${ _('Mode') }</div>
              <label class="radio inline-block margin-right-20">
                <input type="radio" name="rdbmsMode" value="customRdbms" data-bind="checked: createWizard.source.rdbmsMode" /> ${_('Custom')}
              </label>
              <label class="radio inline-block">
                <input type="radio" name="rdbmsMode" value="configRdbms" data-bind="checked: createWizard.source.rdbmsMode" /> ${_('Configured')}
              </label>
            </label>
          </div>

          <div class="control-group" data-bind="visible: createWizard.prefill.target_type() == 'database'">
            <label for="sourceType" class="control-label">${ _('No source is needed for creating a database.') }</label>
          </div>

          <div class="control-group input-append" data-bind="visible: createWizard.source.inputFormat() == 'file'">
            <label for="path" class="control-label"><div>${ _('Path') }</div>
              <input type="text" class="form-control path filechooser-input input-xxlarge" data-bind="value: createWizard.source.path, filechooser: createWizard.source.path, filechooserOptions: { linkMarkup: true, skipInitialPathIfEmpty: true, openOnFocus: true, selectFolder: false }" placeholder="${ _('Click or drag from the assist') }">
            </label>
            <!-- ko if: createWizard.source.path().length > 0 -->
              <a data-bind="storageContextPopover: { path: createWizard.source.path(), offset: { right: 5 } }" title="${ _('Preview') }" style="font-size: 14px" class="margin-left-10">
                <i class="fa fa-fw fa-info"></i>
              </a>
            <!-- /ko -->
          </div>

          <!-- ko if: createWizard.source.inputFormat() == 'rdbms' -->

            <!-- ko if: createWizard.source.rdbmsMode() -->
            <div class="control-group">
              <label for="rdbmsType" class="control-label"><div>${ _('Driver') }</div>
                <select id="rdbmsType" data-bind="selectize: createWizard.source.rdbmsTypes, value: createWizard.source.rdbmsType, optionsText: 'name', optionsValue: 'value'"></select>
              </label>
            </div>
            <!-- /ko -->

            <!-- ko if: createWizard.source.rdbmsMode() == 'customRdbms' -->
              <!-- ko if: createWizard.source.rdbmsType() != 'jdbc' -->
              <div class="control-group">
                <label for="rdbmsHostname" class="control-label"><div>${ _('Hostname') }</div>
                  <input type="text" class="input-xxlarge" data-bind="value: createWizard.source.rdbmsHostname" placeholder="${ _('Enter host/ip here e.g. mysql.domain.com or 123.123.123.123') }">
                </label>
              </div>
              <!-- /ko -->
              <!-- ko if: createWizard.source.rdbmsType() == 'jdbc' -->
              <div class="control-group">
                <label for="rdbmsHostname" class="control-label"><div>${ _('Url') }</div>
                  <input type="text" class="input-xxlarge" data-bind="value: createWizard.source.rdbmsHostname" placeholder="${ _('jdbc:mysql://localhost:3306') }">
                </label>
              </div>
              <!-- /ko -->

              <!-- ko if: createWizard.source.rdbmsType() == 'jdbc' -->
              <div class="control-group">
                <label for="rdbmsJdbcDriver" class="control-label"><div>${ _('JDBC Driver') }</div>
                  <input type="text" class="input-xxlarge" data-bind="value: createWizard.source.rdbmsJdbcDriver">
                </label>
              </div>
              <!-- /ko -->

              <!-- ko if: createWizard.source.rdbmsType() != 'jdbc' -->
              <div class="control-group">
                <label for="rdbmsPort" class="control-label"><div>${ _('Port') }</div>
                  <input type="text" class="input-xxlarge" data-bind="value: createWizard.source.rdbmsPort" placeholder="${ _('Enter port number here e.g. 3306') }">
                </label>
              </div>
              <!-- /ko -->
              <div class="control-group">
                <label for="rdbmsUsername" class="control-label"><div>${ _('Username') }</div>
                  <input type="text" class="input-xxlarge" data-bind="value: createWizard.source.rdbmsUsername" placeholder="${ _('Enter username here') }">
                </label>
              </div>

              <div class="control-group no-margin-bottom">
                <label for="rdbmsPassword" class="control-label"><div>${ _('Password') }</div>
                  <input type="password" class="input-xxlarge" data-bind="value: createWizard.source.rdbmsPassword" placeholder="${ _('Enter password here') }">
                </label>
              </div>

              <div class="control-group">
                <button class="btn" data-bind="click: createWizard.source.rdbmsCheckConnection">
                  ${_('Test Connection')}
                </button>
              </div>
            <!-- /ko -->

            <!-- ko if: createWizard.source.rdbmsMode() == 'configRdbms' || (createWizard.source.rdbmsMode() == 'customRdbms' && createWizard.source.rdbmsDbIsValid()) -->
              <!-- ko if: createWizard.source.rdbmsMode() == 'configRdbms' && createWizard.source.rdbmsType() == 'jdbc' -->
              <div class="control-group">
                <label for="rdbmsJdbcDriverName" class="control-label"><div>${ _('Options') }</div>
                  <select id="rdbmsJdbcDriverName" data-bind="selectize: createWizard.source.rdbmsJdbcDriverNames, value: createWizard.source.rdbmsJdbcDriverName, optionsText: 'name', optionsValue: 'value'"></select>
                  <!-- ko hueSpinner: { spin: createWizard.source.isFetchingDriverNames, inline: true } --><!-- /ko -->
                </label>
              </div>
              <!-- /ko -->

              <!-- ko if: createWizard.source.rdbmsTypes -->
              <div class="control-group input-append">
                <label for="rdbmsDatabaseName" class="control-label"><div>${ _('Database Name') }</div>
                  <select id="rdbmsDatabaseName" data-bind="selectize: createWizard.source.rdbmsDatabaseNames, value: createWizard.source.rdbmsDatabaseName, optionsText: 'name', optionsValue: 'value'"></select>
                  <!-- ko hueSpinner: { spin: createWizard.source.isFetchingDatabaseNames, inline: true } --><!-- /ko -->
                </label>
              </div>
              <!-- /ko -->

              <!-- ko if: createWizard.source.rdbmsDatabaseName -->
              <div class="control-group">
                <div>
                  <label class="checkbox inline-block">
                    <input type="checkbox" data-bind="checked: createWizard.source.rdbmsIsAllTables"> ${_('All Tables')}
                  </label>
                </div>
                <!-- ko ifnot: createWizard.source.rdbmsIsAllTables() -->
                <label for="rdbmsTableName" class="control-label"><div>${ _('Table Name') }</div>
                  <select id="rdbmsTableName" multiple="multiple" data-bind="selectize: createWizard.source.rdbmsTableNames, selectedObjects: createWizard.source.tables, selectedOptions: createWizard.source.tablesNames, optionsText: 'name', optionsValue: 'value'"></select>
                  <!-- ko hueSpinner: { spin: createWizard.source.isFetchingTableNames, inline: true } --><!-- /ko -->
                </label>
                <!-- /ko -->
              </div>
              <!-- /ko -->
            <!-- /ko -->

          <!-- /ko -->

          <!-- ko if: createWizard.source.inputFormat() == 'stream' -->
            <div class="control-group">
              <label class="control-label"><div>${ _('List') }</div>
                <select data-bind="selectize: createWizard.source.publicStreams, value: createWizard.source.streamSelection, optionsText: 'name', optionsValue: 'value'" placeholder="${ _('The list of streams to consume, e.g. SFDC, Jiras...') }"></select>
              </label>
            </div>

            <!-- ko if: createWizard.source.streamSelection() == 'kafka' -->
              <div data-bind="template: { name: 'kafka-topic-template', data: $data }" class="margin-top-10 field inline-block"></div>
            <!-- /ko -->

            <!-- ko if: createWizard.source.streamSelection() == 'flume' -->
              <div class="control-group">

                <label class="control-label"><div>${ _('Type') }</div>
                  <select class="input-medium" data-bind="selectize: createWizard.source.channelSourceTypes, value: createWizard.source.channelSourceType, optionsText: 'name', optionsValue: 'value'"></select>
                </label>
                <!-- ko if: ['directory', 'exec', 'syslogs'].indexOf(createWizard.source.channelSourceType()) != -1 -->
                <label class="control-label"><div>${ _('Hosts') }</div>
                  <select class="input-xxlarge" data-bind="selectize: createWizard.source.channelSourceHosts, selectedOptions: createWizard.source.channelSourceSelectedHosts" multiple="true"></select>
                </label>
                <!-- /ko -->
                <!-- ko if: createWizard.source.channelSourceType() == 'directory' -->
                <label class="control-label"><div>${ _('Path') }</div>
                  <input type="text" class="input-xxlarge" data-bind="value: createWizard.source.channelSourcePath" placeholder="${ _('The path to watch and consume') }">
                </label>
                <!-- /ko -->

                <!-- ko if: createWizard.source.channelSourceType() -->
                <input data-bind="click: function() { createWizard.source.channelSourceType(null); }" class="btn" value="${ _('Clear') }"/>
                <!-- /ko -->

              </div>
            <!-- /ko -->
          <!-- /ko -->

          <!-- ko if: createWizard.source.inputFormat() == 'connector' -->
            <div class="control-group">
              <label class="control-label"><div>${ _('List') }</div>
                <select data-bind="selectize: createWizard.source.connectorList, value: createWizard.source.connectorSelection, optionsText: 'name', optionsValue: 'value'" placeholder="${ _('The connector to use, e.g. SFDC, Jiras...') }"></select>
              </label>
            </div>

            <!-- ko if: createWizard.source.connectorSelection() == 'sfdc' -->
            <div class="control-group">
              <label class="control-label"><div>${ _('Username') }</div>
                <input type="text" class="input-xxlarge" data-bind="value: createWizard.source.streamUsername" placeholder="user@company.com">
              </label>

              <label class="control-label"><div>${ _('Password') }</div>
                <input type="password" class="input-xxlarge" data-bind="value: createWizard.source.streamPassword">
              </label>

              <label class="control-label"><div>${ _('Token') }</div>
                <input type="password" class="input-xxlarge" data-bind="value: createWizard.source.streamToken">
              </label>

              <label class="control-label"><div>${ _('End point URL') }</div>
                <input type="text" class="input-xxlarge" data-bind="value: createWizard.source.streamEndpointUrl">
              </label>

              <br/>
              <!-- ko if: createWizard.source.streamUsername() && createWizard.source.streamPassword() && createWizard.source.streamToken() -->
              <label class="control-label"><div>${ _('Object') }</div>
                <select class="input-xxlarge" data-bind="options: createWizard.source.streamObjects,
                      value: createWizard.source.streamObject,
                      optionsCaption: '${ _("Choose...") }'"
                      placeholder="${ _('The SFDC object to import, e.g. Account, Opportunity') }"></select>
              </label>
              <!-- /ko -->
            </div>
            <!-- /ko -->

          <!-- /ko -->

          <div class="control-group" data-bind="visible: createWizard.source.inputFormat() == 'table'">

            <!-- ko foreach: $root.createWizard.source.tables -->
              <div>
                <label class="control-label">
                  <div><!-- ko if: $index() === 0 -->${ _('Table') }<!-- /ko --></div>
                  <input type="text" class="input-xlarge" data-bind="hiveChooser: name, skipInvalids:true, pathChangeLevel: 'table', skipColumns: true, apiHelperUser: '${ user }', namespace: $root.createWizard.source.namespace, compute: $root.createWizard.source.compute, apiHelperType: $root.createWizard.source.sourceType, mainScrollable: $(MAIN_SCROLLABLE)" placeholder="${ _('Table name or <database>.<table>') }">
                  <a class="pointer pull-right margin-left-5" style="margin-top: 7px" data-bind="click: function() { $root.createWizard.source.tables.remove(this); }, visible: $root.createWizard.source.tables().length > 1"><i class="fa fa-minus"></i></a>
                </label>
              </div>
            <!-- /ko -->
            <div>
              <label class="control-label">
                <div>&nbsp;</div>
                <a class="pointer" data-bind="click: function() { createWizard.source.tables.push(ko.mapping.fromJS({name: ''})); }" title="${_('Add Table')}"><i class="fa fa-plus fa-padding-top"></i> ${_('Add table')}</a>
              </label>
            </div>
          </div>

          <div class="control-group" data-bind="visible: createWizard.source.inputFormat() == 'query'">
            <label for="path" class="control-label"><div>${ _('Query') }
              <!-- ko if: createWizard.source.query() && createWizard.source.query().name -->
              <span data-bind="text: createWizard.source.query().name"></span>
              <!-- /ko -->
              </div>
              ## No dropdown for now
              ## <select placeholder="${ _('Search your documents...') }" data-bind="documentChooser: { dependentValue: createWizard.source.draggedQuery, mappedDocument: createWizard.source.query }"></select>
            </label>
          </div>
        </div>
      </div>
    </div>

    <!-- ko if: createWizard.source.show() && createWizard.source.inputFormat() != 'manual' -->
    <div class="card step" data-bind="visible: createWizard.source.inputFormat() == 'file' || createWizard.source.inputFormat() == 'stream'">
      <!-- ko if: createWizard.isGuessingFormat -->
      <h4>${_('Guessing format...')} <i class="fa fa-spinner fa-spin"></i></h4>
      <!-- /ko -->
      <!-- ko ifnot: createWizard.isGuessingFormat -->
      <h4>${_('Format')}</h4>
      <div class="card-body">
        <label data-bind="visible: (createWizard.prefill.source_type().length == 0 || createWizard.prefill.target_type() == 'index') && (createWizard.source.inputFormat() == 'file' || createWizard.source.inputFormat() == 'stream')">
          <div>${_('File Type')}</div>
          <select data-bind="selectize: $root.createWizard.fileTypes, value: $root.createWizard.fileTypeName, optionsText: 'description', optionsValue: 'name'"></select>
        </label>
        <span class="inline-labels" data-bind="with: createWizard.source.format, visible: createWizard.source.show">
          <span data-bind="foreach: getArguments()">
            <!-- ko template: {name: 'arg-' + $data.type, data: {description: $data.description, value: $parent[$data.name]}}--><!-- /ko -->
          </span>
        </span>
      </div>
      <!-- /ko -->
    </div>

    <!-- ko ifnot: createWizard.source.inputFormat() == 'rdbms' && createWizard.source.rdbmsIsAllTables() -->
    <div class="card step" style="min-height: 310px;">
      <!-- ko if: $root.createWizard.source.inputFormat() === 'table' || ($root.createWizard.source.inputFormat() !== 'table' && !createWizard.isGuessingFormat()) -->
      <h4>${_('Preview')}
        <!-- ko if: $root.createWizard.source.inputFormat() !== 'table' && createWizard.isGuessingFieldTypes() -->
        <i class="fa fa-spinner fa-spin"></i>
        <!-- /ko -->
      </h4>
      <!-- /ko -->

      <!-- ko if: createWizard.source.inputFormat() == 'query' && createWizard.source.sample().length == 0 -->
        ${ _('Add sample data') } <i class="fa fa-fw fa-play"></i>
      <!-- /ko -->
      <div class="card-body">
        <!-- ko if: ['table', 'rdbms'].indexOf($root.createWizard.source.inputFormat()) >= 0 && $root.createWizard.source.tables().length > 1 -->
        <ul class="nav nav-tabs" style="margin-top: -14px">
          <!-- ko foreach: $root.createWizard.source.tables -->
          <li data-bind="css: { 'active': $root.createWizard.source.selectedTableIndex() === $index() }"><a href="javascript: void(0)" data-bind="text: name, click: function(){ $root.createWizard.source.selectedTableIndex($index()) }"></a></li>
          <!-- /ko -->
        </ul>
        <!-- /ko -->

        <!-- ko if: ['table', 'rdbms'].indexOf($root.createWizard.source.inputFormat()) >= 0 -->
        <!-- ko hueSpinner: { spin: createWizard.isGuessingFormat() || createWizard.isGuessingFieldTypes() , inline: true } --><!-- /ko -->
        <!-- /ko -->

        <!-- ko ifnot: createWizard.isGuessingFormat -->
          <!-- ko ifnot: createWizard.isGuessingFieldTypes -->
          <div data-bind="delayedOverflow">
            <table class="table table-condensed table-preview">
              <thead>
              <tr data-bind="foreach: createWizard.source.sampleCols">
                ##<!-- ko template: 'field-preview-header-template' --><!-- /ko -->
                <th data-bind="truncatedText: name" style="padding-right: 60px"></th>
                ## TODO nested
              </tr>
              </thead>
              <tbody data-bind="foreach: createWizard.source.sample">
              <tr data-bind="foreach: $data">
                <td data-bind="truncatedText: $data"></td>
              </tr>
              </tbody>
            </table>
          </div>
          <!-- /ko -->
        <!-- /ko -->
      </div>
    </div>
    <!-- /ko -->
    <!-- /ko -->

    <!-- /ko -->


    <!-- ko if: currentStep() == 2 -->
      <!-- ko with: createWizard.destination -->

      <div class="card step">
        <h4>${_('Destination')}</h4>
        <div class="card-body">
          <div class="control-group">
            <label for="destinationType" class="control-label" data-bind="visible: $parent.createWizard.prefill.target_type().length == 0"><div>${ _('Type') }</div>
              <select id="destinationType" data-bind="selectize: outputFormats, value: outputFormat, optionsValue: 'value', optionsText: 'name'"></select>
            </label>
          </div>

          <div class="control-group">
            <!-- ko if: outputFormat() == 'file' -->
            <label for="collectionName" class="control-label "><div>${ _('Name') }</div></label>
            <input type="text" class="form-control name input-xxlarge" id="collectionName" data-bind="value: name, filechooser: name, filechooserOptions: { linkMarkup: true, skipInitialPathIfEmpty: true, openOnFocus: true, selectFolder: true, displayOnlyFolders: true, uploadFile: false}" placeholder="${ _('Name') }" title="${ _('Directory must not exist in the path') }">
            <!-- /ko -->

            <!-- ko if: outputFormat() == 'index' -->
            <label for="collectionName" class="control-label "><div>${ _('Name') }</div></label>
            <input type="text" class="form-control input-xlarge" id="collectionName" data-bind="value: name, valueUpdate: 'afterkeydown'" placeholder="${ _('Name') }">
            <!-- /ko -->

            <!-- ko if: ['table', 'database'].indexOf(outputFormat()) != -1 -->
            <label for="collectionName" class="control-label "><div>${ _('Name') }</div></label>
            <input type="text" class="input-xxlarge" data-bind="value: name, hiveChooser: name, namespace: namespace, compute: compute, skipColumns: true, skipTables: outputFormat() == 'database', valueUpdate: 'afterkeydown', apiHelperUser: '${ user }', apiHelperType: sourceType, mainScrollable: $(MAIN_SCROLLABLE), attr: { 'placeholder': outputFormat() == 'table' ? '${  _ko('Table name or <database>.<table>') }' : '${  _ko('Database name') }' }" pattern="^([a-zA-Z0-9_]+\.)?[a-zA-Z0-9_]*$" title="${ _('Only alphanumeric and underscore characters') }">
            <!-- /ko -->

            <!-- ko if: outputFormat() == 'altus' -->
              <label for="collectionName" class="control-label"><div>${ _('Namespace') }</div></label>
              <div class="namespace-selection">
              <select data-bind="selectize: namespaces, value: targetNamespaceId, optionsValue: 'id', optionsText: 'name'" class="input-medium"></select>
              </div>
              <label class="checkbox inline-block"><input type="checkbox"> ${_('Copy Sentry privileges')}</label>
              <br/>

              <label class="control-label "><div>${ _('Database') }</div></label>
              <input type="text" class="form-control input-xlarge" data-bind="value: name" placeholder="${ _('Database') }">
              <a href="javascript:void(0);" data-bind="sqlContextPopover: { sourceType: $root.createWizard.source.sourceType, namespace: namespace, compute: compute, path: 'default', offset: { top: -3, left: 3 }}">
                <i class="fa fa-info"></i>
              </a>
            <!-- /ko -->

            <!-- ko if: outputFormat() == 'stream' -->
            <label for="collectionName" class="control-label "><div>${ _('Name') }</div></label>
              <!-- ko with: $root -->
                <input type="text" data-bind="value: createWizard.source.kafkaSelectedTopics">
                ## <div data-bind="template: { name: 'kafka-topic-template' }" class="margin-top-10 field inline-block"></div>
              <!-- /ko -->
            <!-- /ko -->

            <!-- ko if: outputFormat() == 'flume' -->

            <h4>${ _('Sink') }</h4>
            <div class="row-fluid">
              <div>
                <label class="control-label"><div>${ _('Type') }</div>
                  <select class="input-medium" data-bind="selectize: channelSinkTypes, value: channelSinkType, optionsText: 'name', optionsValue: 'value'"></select>
                </label>
                <!-- ko if: channelSinkType() == 'solr' -->
                <label class="control-label"><div>${ _('Collection') }</div>
                  <select class="input-xxlarge" data-bind="selectize: ['logIndex', 'apacheLogs'], value: channelSinkPath"></select>
                </label>
                <!-- /ko -->

                <!-- ko if: channelSinkType() -->
                <input data-bind="click: function() { channelSourceType(null); }" class="btn" value="${ _('Clear') }"/>
                <!-- /ko -->
              </div>
            </div>
            <!-- /ko -->

            <span class="help-inline muted" data-bind="visible: !isTargetExisting() && isTargetChecking()">
              <i class="fa fa-spinner fa-spin"></i>
            </span>
            <span class="help-inline muted" data-bind="visible: !$parent.createWizard.isValidDestination()">
              <i class="fa fa-warning" style="color: #c09853"></i>
              <!-- ko if: name() -->
                ${ _('Invalid characters') }
              <!-- /ko -->
              <!-- ko if: !name() -->
                ${ _('Empty name') }
              <!-- /ko -->
            </span>
            <span class="help-inline muted" data-bind="visible: isTargetExisting() && outputFormat() != 'altus'">
              <i class="fa fa-warning" style="color: #c09853"></i> ${ _('Already existing') } <span data-bind="text: outputFormat"></span>
              <a href="javascript:void(0)" data-bind="hueLink: existingTargetUrl(), text: name" title="${ _('Open') }"></a>
            </span>
            <span class="help-inline muted" data-bind="visible: !isTargetExisting() && $parent.createWizard.source.inputFormat() === 'rdbms' && outputFormat() == 'database' ">
              <i class="fa fa-warning" style="color: #c09853"></i> ${ _('Does not exist') } <span data-bind="text: outputFormat"></span>
            </span>
          </div>
        </div>
      </div>


        <!-- ko if: outputFormat() == 'table' && $root.createWizard.source.inputFormat() != 'rdbms' -->
        <div class="card step">
          <h4>${_('Properties')}</h4>
          <div class="card-body">
            <div class="control-group">
              <label for="destinationFormat" class="control-label"><div>${ _('Format') }</div>
                <select id="destinationFormat" data-bind="selectize: tableFormats, value: tableFormat, optionsValue: 'value', optionsText: 'name'"></select>
              </label>
            </div>

            <div class="control-group">
              <label class="control-label"><div>${ _('Extras') }</div>
                <a href="javascript:void(0)" data-bind="css: { 'inactive-action': !showProperties() }, toggle: showProperties" title="${ _('Show extra properties') }">
                  <i class="fa fa-sliders fa-padding-top"></i>
                </a>
              </label>
            </div>

            <span data-bind="visible: showProperties">
              <div class="control-group">
                <label class="checkbox inline-block" data-bind="visible: tableFormat() != 'kudu'">
                  <input type="checkbox" data-bind="checked: useDefaultLocation"> ${_('Store in Default location')}
                </label>
              </div>
              <div class="control-group" data-bind="visible: isTransactionalVisible">
                <label class="checkbox inline-block">
                  <input type="checkbox" data-bind="checked: isTransactional"> ${_('Transactional table')}
                </label>
                <label class="checkbox inline-block" title="${_('Full transactional support available in Hive with ORC')}">
                  <input type="checkbox" data-bind="checked: isInsertOnly, enable: isTransactionalUpdateEnabled"> ${_('Insert only')}
                </label>
              </div>

              <div class="control-group" data-bind="visible: !useDefaultLocation()">
                <label for="path" class="control-label"><div>${ _('External location') }</div>
                  <input type="text" class="form-control path filechooser-input input-xxlarge" data-bind="value: nonDefaultLocation, filechooser: nonDefaultLocation, filechooserOptions: { linkMarkup: true, skipInitialPathIfEmpty: true }, valueUpdate: 'afterkeydown'">
                </label>
              </div>

              <div class="control-group">
                <label class="checkbox inline-block" data-bind="visible: $root.createWizard.source.inputFormat() != 'manual'">
                  <input type="checkbox" data-bind="checked: importData, disable: !useDefaultLocation() && $parent.createWizard.source.path() == nonDefaultLocation();"> ${_('Import data')}
                </label>
              </div>
              <div class="control-group">
                <label><div>${ _('Description') }</div>
                    <input type="text" class="form-control input-xxlarge" data-bind="value: description, valueUpdate: 'afterkeydown'" placeholder="${ _('Description') }">
                </label>
              </div>
              <div class="control-group" data-bind="visible: $root.createWizard.source.inputFormat() == 'file'">
                <label class="checkbox inline-block">
                  <input type="checkbox" data-bind="checked: hasHeader"> ${_('Use first row as header')}
                </label>
              </div>
              <div class="control-group" data-bind="visible: tableFormat() == 'text'">
                <label class="checkbox inline-block">
                  <input type="checkbox" data-bind="checked: useCustomDelimiters"> ${_('Custom char delimiters')}
                </label>
              </div>
              <span class="inline-labels" data-bind="visible: tableFormat() == 'text' && useCustomDelimiters()">
                <label for="fieldDelimiter" class="control-label"><div>${ _('Field') }</div>
                  <select id="fieldDelimiter" data-bind="selectize: $root.createWizard.customDelimiters, selectizeOptions: { onOptionAdd: function(value){ $root.createWizard.customDelimiters.push({ 'value': value, 'name': value }) }, create: true, maxLength: 2 }, value: customFieldDelimiter, optionsValue: 'value', optionsText: 'name'"></select>
                </label>
                <label for="collectionDelimiter" class="control-label"><div>${ _('Array, Map') }</div>
                  <select id="collectionDelimiter" data-bind="selectize: $root.createWizard.customDelimiters, selectizeOptions: { onOptionAdd: function(value){ $root.createWizard.customDelimiters.push({ 'value': value, 'name': value }) }, create: true, maxLength: 2 }, value: customCollectionDelimiter, optionsValue: 'value', optionsText: 'name'"></select>
                </label>
                <label for="structDelimiter" class="control-label"><div>${ _('Struct') }</div>
                  <select id="structDelimiter" data-bind="selectize: $root.createWizard.customDelimiters, selectizeOptions: { onOptionAdd: function(value){ $root.createWizard.customDelimiters.push({ 'value': value, 'name': value }) }, create: true, maxLength: 2 }, value: customMapDelimiter, optionsValue: 'value', optionsText: 'name'"></select>
                </label>
              </span>
            </span>

            <div class="control-group" data-bind="visible: tableFormat() == 'regexp'">
              <label for="customRegexp" class="control-label"><div>${ _('Regexp') }</div>
                <input id="customRegexp" class="input-xxlarge" type="text" data-bind="value: customRegexp" placeholder='([^]*) ([^]*) ([^]*) (-|\\[^\\]*\\]) ([^ \"]*|\"[^\"]*\") (-|[0-9]*) (-|[0-9]*)(?: ([^ \"]*|\".*\") ([^ \"]*|\".*\"))?'>
              </label>
            </div>

            <div class="control-group" data-bind="visible: tableFormat() == 'kudu'">
              <label for="kuduPksTable" class="control-label"><div>${ _('Primary keys') }</div>
                ## At least one selected
                <select id="kuduPksTable" data-bind="selectize: columns, selectedOptions: primaryKeys, selectedObjects: primaryKeyObjects, optionsValue: 'name', optionsText: 'name', innerSubscriber: 'name'" size="3" multiple="true"></select>
              </label>
            </div>

            <label class="control-label"><div>${ _('Partitions') }</div>

              <!-- ko if: tableFormat() != 'kudu' && $root.createWizard.source.inputFormat() != 'rdbms' -->
              <div class="inline-table">
                <div class="form-inline" data-bind="foreach: partitionColumns">
                  <a class="pointer pull-right margin-top-20" data-bind="click: function() { $parent.partitionColumns.remove($data); }"><i class="fa fa-minus"></i></a>
                  <div data-bind="template: { name: 'table-field-template', data: $data }" class="margin-top-10 field inline-block"></div>
                  <div class="clearfix"></div>
                </div>
                <a data-bind="click: function() { partitionColumns.push($root.loadDefaultField({isPartition: true})); }" class="pointer" title="${_('Add Partition')}"><i class="fa fa-plus fa-padding-top"></i> ${_('Add partition')}</a>
              </div>
              <!-- /ko -->

              <!-- ko if: tableFormat() == 'kudu' -->
              <div class="form-inline inline-table">
                <ul class="unstyled kudu-partitions" data-bind="foreach: kuduPartitionColumns">
                  <li>
                  <a class="pointer pull-right" data-bind="click: function() { $parent.kuduPartitionColumns.remove($data); }"><i class="fa fa-minus"></i></a>

                  <select data-bind="selectize: $parent.primaryKeyObjects, selectedOptions: columns, optionsValue: 'name', optionsText: 'name', selectizeOptions: { placeholder: '${ _ko('Columns...') }' }" size="3" multiple="true"></select>
                  <select data-bind="selectize: ['RANGE BY', 'HASH'], value: name"></select>

                  <!-- ko if: name() == 'HASH' -->
                    <input class="input-small" type="number" data-bind="value: int_val">
                  <!-- /ko -->

                  <!-- ko if: name() == 'RANGE BY' -->
                    <div class="form-inline" data-bind="foreach: range_partitions">
                      <div class="range-partition">
                        <a class="pull-right" data-bind="click: function() { $parent.range_partitions.remove($data); }"><i class="fa fa-minus"></i></a>
                        <!-- ko if: name() == 'VALUES' -->
                          <input type="text" class="input-small" data-bind="value: lower_val">
                          <select data-bind="selectize: ['<', '<='], value: include_lower_val"></select>
                          <select data-bind="selectize: ['VALUES', 'VALUE'], value: name"></select>
                          <select data-bind="selectize: ['<', '<='], value: include_upper_val"></select>
                          <input type="text" class="input-small" data-bind="value: upper_val">
                        <!-- /ko -->

                        <!-- ko if: name() == 'VALUE' -->
                          <select data-bind="selectize: ['VALUES', 'VALUE'], value: name"></select>
                          <div class="inline-block" data-bind="foreach: values" style="max-width: 370px">
                            <input class="input-small" type="text" data-bind="textInput: value" style="margin-bottom: 5px">
                            <a data-bind="click: function() { $parent.values.remove($data); }"><i class="fa fa-minus"></i></a>
                          </div>
                          <a class="inline-block" data-bind="click: function() { values.push(ko.mapping.fromJS({value: ''})); }" title="${_('Add value')}"><i class="fa fa-plus"></i></a>
                          <div class="clearfix"></div>
                        <!-- /ko -->
                      </div>
                    </div>

                    <a data-bind="click: function() { range_partitions.push(ko.mapping.fromJS($parent.KUDU_DEFAULT_RANGE_PARTITION_COLUMN)); }" title="${_('Add column')}"><i class="fa fa-plus"></i></a>
                  <!-- /ko -->

                  <!-- /ko -->
                  </li>
                </ul>
                <a data-bind="click: function() { kuduPartitionColumns.push(ko.mapping.fromJS(KUDU_DEFAULT_PARTITION_COLUMN)); }" class="pointer" title="${_('Add partition')}"><i class="fa fa-plus"></i> ${_('Add partition')}</a>
              </div>
            <!-- /ko -->

            </label>
          </div>
        </div>
        <!-- /ko -->

        <!-- ko if: outputFormat() == 'index' -->
        <div class="card step">
          <h4>${_('Properties')}</h4>
          <div class="card-body">
            % if ENABLE_SCALABLE_INDEXER.get():
            <div class="control-group">
              <label class="checkbox inline-block" title="${ _('Execute a cluster job to index a large dataset.') }" data-bind="visible: $root.createWizard.source.inputFormat() == 'file'">
                <input type="checkbox" data-bind="checked: indexerRunJob"> ${_('Index with a job')}
              </label>

              <label for="path" class="control-label" data-bind="visible: indexerRunJob"><div>${ _('Libs') }</div>
                <input type="text" class="form-control path filechooser-input input-xlarge" data-bind="value: indexerJobLibPath, filechooser: indexerJobLibPath, filechooserOptions: { linkMarkup: true, skipInitialPathIfEmpty: true }, valueUpdate: 'afterkeydown'">
              </label>
              <!-- ko if: indexerRunJob() && indexerJobLibPath().length > 0 -->
                <a data-bind="hueLink: '/filebrowser/view=' + indexerJobLibPath()" title="${ _('Open') }" style="font-size: 14px" class="margin-left-10">
                  <i class="fa fa-external-link-square"></i>
                </a>
              <!-- /ko -->
            </div>
            % endif

            <div class="control-group">
              <label for="kuduPksIndex" class="control-label"><div>${ _('Primary key') }</div>
                <select id="kuduPksIndex" data-bind="selectize: columns, selectedOptions: indexerPrimaryKey, selectedObjects: indexerPrimaryKeyObject, optionsValue: 'name', optionsText: 'name', innerSubscriber: 'name'" size="1" multiple="false"></select>
              </label>
            </div>

            <div class="control-group">
              <label for="kuduDefaultField" class="control-label"><div>${ _('Default field') }</div>
                <select id="kuduDefaultField" data-bind="selectize: columns, selectedOptions: indexerDefaultField, selectedObjects: indexerDefaultFieldObject, optionsValue: 'name', optionsText: 'name', innerSubscriber: 'name'" size="1" multiple="false"></select>
              </label>
            </div>

            <div class="control-group">
              <label class="control-label"><div>${ _('Extras') }</div>
                <a href="javascript:void(0)" data-bind="css: { 'inactive-action': !showProperties() }, toggle: showProperties" title="${ _('Show extra properties') }">
                  <i class="fa fa-sliders fa-padding-top"></i>
                </a>
              </label>
            </div>

            <span data-bind="visible: showProperties">
              <div class="control-group">
                <label for="destinationFormatIndex" class="control-label"><div>${ _('Config set') }</div>
                  <select id="destinationFormatIndex" data-bind="selectize: indexerConfigSets, value: indexerConfigSet, optionsValue: 'value', optionsText: 'name'"></select>
                </label>
              </div>

              <div class="control-group">
                <label for="indexerNumShards" class="control-label"><div>${ _('Num shards') }</div>
                  <input type="number" class="input-small" placeholder="1" data-bind="value: indexerNumShards">
                </label>
              </div>

              <div class="control-group">
                <label for="indexerReplicationFactor" class="control-label"><div>${ _('Replication factor') }</div>
                  <input type="number" class="input-small" placeholder="1" data-bind="value: indexerReplicationFactor">
                </label>
              </div>

              ## Router, maxShardsPer, shards, routerField

              <div class="control-group" data-bind="visible: $root.createWizard.source.inputFormat() == 'file'">
                <label class="checkbox inline-block">
                  <input type="checkbox" data-bind="checked: hasHeader"> ${_('Use first row as header')}
                </label>
              </div>
            </span>
          </div>
        </div>
        <!-- /ko -->

        <!-- ko if: $root.createWizard.source.inputFormat() == 'rdbms' && ['database', 'file', 'table', 'hbase'].indexOf(outputFormat()) != -1 -->
        <div class="card step">
          <h4>${_('Properties')}</h4>

          <div class="card-body">
            <label class="control-label"><div>${ _('Libs') }</div>
              <div class="inline-table">
                <ul data-bind="sortable: { data: sqoopJobLibPaths, options: { axis: 'y', containment: 'parent', handle: '.move-widget' }}, visible: sqoopJobLibPaths().length" class="unstyled">
                  <li>
                    <div class="input-append" style="margin-bottom: 4px">
                      <input type="text" class="filechooser-input input-xxlarge" data-bind="value: path, valueUpdate:'afterkeydown', filechooser: { value: path, isAddon: true }, filechooserOptions: { skipInitialPathIfEmpty: true }" placeholder="${ _('Path to the file, e.g. hdfs://localhost:8020/user/hue/file.hue') }"/>
                      <span class="add-on move-widget muted" data-bind="visible: $parent.sqoopJobLibPaths().length > 1"><i class="fa fa-arrows"></i></span>
                      <a class="add-on muted" href="javascript: void(0);" data-bind="click: function(){ $parent.removeSqoopJobLibPath($data); }"><i class="fa fa-minus"></i></a>
                    </div>
                  </li>
                </ul>
                <div class="config-property-add-value" style="margin-top: 5px;">
                  <a class="inactive-action pointer" style="padding: 3px 10px 3px 3px;;" data-bind="click: addSqoopJobLibPath">
                    <i class="fa fa-plus"></i>
                  </a>
                </div>
              </div>
            </label>
          </div>

          <div class="control-group">
            <label class="control-label"><div>${ _('Extras') }</div>
              <a href="javascript:void(0)" data-bind="css: { 'inactive-action': !showProperties() }, toggle: showProperties" title="${ _('Show extra properties') }">
                <i class="fa fa-sliders fa-padding-top"></i>
              </a>
            </label>
          </div>

          <span data-bind="visible: showProperties">
            <div class="control-group">
              <label><div>${ _('Mappers') }</div>
                <input type="number" class="form-control input-small" data-bind="textInput: numMappers">
              </label>
            </div>
            <div class="control-group">
              <!-- ko if: !$root.createWizard.source.rdbmsAllTablesSelected() -->
                <label for="rdbmsSplitBy" class="control-label"><div>${ _('Split By') }</div>
                  <select id="rdbmsSplitBy" data-bind="selectize: columns, value: rdbmsSplitByColumn, optionsValue: 'name', optionsText: 'name'"></select>
                </label>
              <!-- /ko -->
            </div>
            <div class="control-group" data-bind="visible: outputFormat() == 'file' && !$root.createWizard.source.rdbmsAllTablesSelected()">
              <label for="destinationFormat" class="control-label"><div>${ _('Format') }</div>
                <select id="destinationFormat" data-bind="selectize: rdbmsFileOutputFormats, value: rdbmsFileOutputFormat, optionsValue: 'value', optionsText: 'name'"></select>
              </label>
            </div>
            <span class="inline-labels" data-bind="visible: rdbmsFileOutputFormat() == 'text' && outputFormat() == 'file' && !$root.createWizard.source.rdbmsAllTablesSelected()">
              <label for="fieldDelimiter" class="control-label"><div>${ _('Fields') }</div>
                <select id="fieldDelimiter" data-bind="selectize: $root.createWizard.customDelimiters, selectizeOptions: { onOptionAdd: function(value){ $root.createWizard.customDelimiters.push({ 'value': value, 'name': value }) }, create: true, maxLength: 2 }, value: customFieldsDelimiter, optionsValue: 'value', optionsText: 'name'"></select>
              </label>
              <label for="collectionDelimiter" class="control-label"><div>${ _('Line') }</div>
                <select id="collectionDelimiter" data-bind="selectize: $root.createWizard.customDelimiters, selectizeOptions: { onOptionAdd: function(value){ $root.createWizard.customDelimiters.push({ 'value': value, 'name': value }) }, create: true, maxLength: 2 }, value: customLineDelimiter, optionsValue: 'value', optionsText: 'name'"></select>
              </label>
              <label for="structDelimiter" class="control-label"><div>${ _('Optionally Enclosed By') }</div>
                <select id="structDelimiter" data-bind="selectize: $root.createWizard.customDelimiters, selectizeOptions: { onOptionAdd: function(value){ $root.createWizard.customDelimiters.push({ 'value': value, 'name': value }) }, create: true, maxLength: 2 }, value: customEnclosedByDelimiter, optionsValue: 'value', optionsText: 'name'"></select>
              </label>
            </span>
            <!-- ko if: outputFormat() === 'database' -->
            <span>
              <label class="checkbox">
              <input type="checkbox" data-bind="checked: useDefaultLocation"> ${_('Default location')}
              </label>
              <span data-bind="visible: !useDefaultLocation()">
                <label for="path" class="control-label"><div>${ _('External location') }</div>
                  <input type="text" class="form-control path filechooser-input input-xxlarge" data-bind="value: nonDefaultLocation, filechooser: nonDefaultLocation, filechooserOptions: { linkMarkup: true, skipInitialPathIfEmpty: true }, valueUpdate: 'afterkeydown'">
                </label>
              </span>
            </span>
            <!-- /ko -->
          </span>

        </div>
        <!-- /ko -->

        <!-- ko if: $root.createWizard.source.inputFormat() == 'kafka' -->
        <div class="card step">
          <h4>${_('Properties')}</h4>

          <div class="card-body">
            <label class="control-label"><div>${ _('Libs') }</div>
              <div class="inline-table">
                <ul data-bind="sortable: { data: sqoopJobLibPaths, options: { axis: 'y', containment: 'parent', handle: '.move-widget' }}, visible: sqoopJobLibPaths().length" class="unstyled">
                  <li>
                    <div class="input-append" style="margin-bottom: 4px">
                      <input type="text" class="filechooser-input input-xxlarge" data-bind="value: path, valueUpdate:'afterkeydown', filechooser: { value: path, isAddon: true }, filechooserOptions: { skipInitialPathIfEmpty: true }" placeholder="${ _('Path to the file, e.g. hdfs://localhost:8020/user/hue/file.hue') }"/>
                      <span class="add-on move-widget muted" data-bind="visible: $parent.sqoopJobLibPaths().length > 1"><i class="fa fa-arrows"></i></span>
                      <a class="add-on muted" href="javascript: void(0);" data-bind="click: function(){ $parent.removeSqoopJobLibPath($data); }"><i class="fa fa-minus"></i></a>
                    </div>
                  </li>
                </ul>
                <div class="config-property-add-value" style="margin-top: 5px;">
                  <a class="inactive-action pointer" style="padding: 3px 10px 3px 3px;" data-bind="click: addSqoopJobLibPath">
                    <i class="fa fa-plus"></i>
                  </a>
                </div>
              </div>
            </label>
          </div>
        </div>
        <!-- /ko -->

        <!-- ko if: ['table', 'index', 'hbase'].indexOf(outputFormat()) != -1 -->
          <div class="card step">
            <h4>
              <!-- ko if: fieldEditorEnabled -->
                <!-- ko if: useFieldEditor -->
                <a class="inactive-action" href="javascript:void(0);" data-bind="toggle: useFieldEditor">${_('Fields')} /</a> ${_('Editor')}
                <!-- /ko -->
                <!-- ko ifnot: useFieldEditor -->
                  ${_('Fields')} / <a class="inactive-action" href="javascript:void(0);" data-bind="toggle: useFieldEditor">${_('Editor')}</a>
                <!-- /ko -->
              <!-- /ko -->
              <!-- ko ifnot: fieldEditorEnabled -->
                ${_('Fields')} <!-- ko if: $root.createWizard.isGuessingFieldTypes --><i class="fa fa-spinner fa-spin"></i><!-- /ko -->
                <a class="inactive-action pointer" data-bind="visible: columns().length > 0, publish: 'importer.show.bulkeditor'" href="javascript:void(0)">
                  <i class="fa fa-edit"></i>
                </a>
              <!-- /ko -->
            </h4>
            <div class="card-body no-margin-top columns-form">
              <!-- ko if: useFieldEditor -->
              <div class="control-group" style="margin-bottom: 5px;">
                <label class="control-label"><div style="width: initial">${ _('Language') }</div>
                  <select>
                    <option value="sql">SQL</option>
                    <option value="morphline">Morphline</option>
                  </select>
                </label>
              </div>

              <div data-bind="component: { name: 'hue-simple-ace-editor-multi', params: {
                  value: fieldEditorValue,
                  placeHolder: fieldEditorPlaceHolder,
                  autocomplete: { type: sourceType },
                  lines: 5,
                  aceOptions: {
                    minLines: 10,
                    maxLines: 25
                  },
                  database: fieldEditorDatabase,
                  namespace: namespace,
                  compute: compute,
                  temporaryOnly: true,
                  mode: sourceType
                }}"></div>
              <!-- /ko -->
              <!-- ko ifnot: useFieldEditor -->
              <!-- ko if: $root.createWizard.source.inputFormat() === 'manual' -->
                <form class="form-inline inline-table" data-bind="foreach: columns">
                  <!-- ko if: $parent.outputFormat() == 'table' -->
                    <a class="pointer pull-right margin-top-20" data-bind="click: function() { $parent.columns.remove($data); }"><i class="fa fa-minus"></i></a>
                    <div data-bind="template: { name: 'table-field-template', data: $data }" class="margin-top-10 field inline-block"></div>
                    <div class="clearfix"></div>
                  <!-- /ko -->

                  <!-- ko if: $parent.outputFormat() == 'index' -->
                    <a class="pointer pull-right margin-top-20" data-bind="click: function() { $parent.columns.remove($data); }"><i class="fa fa-minus"></i></a>
                    <div data-bind="template: { name: 'index-field-template', data: $data }, css: { 'disabled': !keep() }" class="margin-top-10 field inline-block index-field"></div>
                    <div class="clearfix"></div>
                  <!-- /ko -->
                </form>

                <div class="clearfix"></div>

                <!-- ko if: outputFormat() == 'table' || outputFormat() == 'index' -->
                  <a data-bind="click: function() { columns.push($root.loadDefaultField({})); }" class="pointer" title="${_('Add Field')}"><i class="fa fa-plus"></i> ${_('Add Field')}</a>
                <!-- /ko -->
              <!-- /ko -->

              <!-- ko ifnot: $root.createWizard.source.inputFormat() === 'manual' -->
              <form class="form-inline inline-table" data-bind="foreachVisible: { data: columns, minHeight: 54, container: MAIN_SCROLLABLE }">
                <!-- ko if: $parent.outputFormat() == 'table' && $root.createWizard.source.inputFormat() != 'rdbms' -->
                  <div data-bind="template: { name: 'table-field-template', data: $data }" class="margin-top-10 field"></div>
                <!-- /ko -->

                <!-- ko if: (['file', 'table', 'hbase'].indexOf($parent.outputFormat()) != -1 && $root.createWizard.source.inputFormat() == 'rdbms') || $parent.outputFormat() == 'index' -->
                  <div data-bind="template: { name: 'index-field-template', data: $data }, css: { 'disabled': !keep() }" class="margin-top-10 field index-field"></div>
                <!-- /ko -->
              </form>

              <div class="clearfix"></div>
              <!-- /ko -->
              <!-- /ko -->
            </div>
          </div>
        <!-- /ko -->

        <!-- ko if: outputFormat() == 'database' && $root.createWizard.source.inputFormat() !== 'rdbms' -->
          <div class="card step">
            <h4>${_('Properties')}</h4>
            <div class="card-body">
              <label><div>${ _('Description') }</div>
              <input type="text" class="form-control input-xlarge" data-bind="value: description, valueUpdate: 'afterkeydown'" placeholder="${ _('Description') }">
              </label>

              <label class="checkbox">
                <input type="checkbox" data-bind="checked: useDefaultLocation"> ${_('Default location')}
              </label>
              <span data-bind="visible: !useDefaultLocation()">
                <label for="path" class="control-label"><div>${ _('External location') }</div>
                  <input type="text" class="form-control path filechooser-input input-xxlarge" data-bind="value: nonDefaultLocation, filechooser: nonDefaultLocation, filechooserOptions: { linkMarkup: true, skipInitialPathIfEmpty: true }, valueUpdate: 'afterkeydown'">
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

      <!-- ko if: currentStep() == 1 -->
      <button class="btn" data-bind="enable: !createWizard.isGuessingFormat() && createWizard.source.show(), click: function() { currentStep(2); }">
        ${_('Next')}
      </button>
      <!-- /ko -->

      <!-- ko if: currentStep() == 2 -->
        <button class="btn btn-primary disable-feedback" data-bind="click: function() { createWizard.indexFile(); }, enable: createWizard.readyToIndex() && !createWizard.indexingStarted()">
          ${ _('Submit') } <i class="fa fa-spinner fa-spin" data-bind="visible: createWizard.indexingStarted"></i>
        </button>

        % if ENABLE_ENVELOPE.get():
        <button class="btn disable-feedback" data-bind="click: createWizard.showCommands, enable: createWizard.readyToIndex()">
          ${ _('Show Commands') }
        </button>
        <button class="btn disable-feedback">
          ${ _('Save') }
        </button>
        % endif
      <!-- /ko -->

      <span data-bind="visible: createWizard.editorId">
        <button class="btn btn-success" data-bind="click: function(){ window.open('${ url('notebook:editor') }?editor=' + createWizard.editorId()) }" title="${ _('Open') }">
          ${_('Check status')}
        </button>
      </span>

      <div id="importerNotebook"></div>
    </div>
  </div>

  <div id="fieldsBulkEditor" class="modal hide fade">
    <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
      <h2 class="modal-title">${ _('Write or paste comma separated field names') }</h2>
    </div>
    <div class="modal-body">
      <input type="text" class="input-xxlarge" placeholder="${ _('e.g. id, name, salary') }" data-bind="textInput: createWizard.destination.bulkColumnNames">
    </div>
    <div class="modal-footer">
      <button class="btn" data-dismiss="modal" aria-hidden="true">${ _('Cancel') }</button>
      <button class="btn btn-primary" data-bind="click: createWizard.destination.processBulkColumnNames">${ _('Change field names') }</button>
    </div>
  </div>

</script>


<script type="text/html" id="table-field-template">
  <div>
    <label data-bind="visible: level() == 0 || ($parent.type() != 'array' && $parent.type() != 'map')">${ _('Name') }&nbsp;
      <input type="text" class="input-large" placeholder="${ _('Field name') }" required data-bind="textInput: name">
    </label>

    <label class="margin-left-5">${ _('Type') }&nbsp;
    <!-- ko if: !(level() > 0 && $parent.type() == 'map') -->
      <select class="input-small" data-bind="browserAwareSelectize: $root.createWizard.hiveFieldTypes, value: type"></select>
    <!-- /ko -->
    <!-- ko if: level() > 0 && $parent.type() == 'map' -->
      <select class="input-small" data-bind="browserAwareSelectize: $root.createWizard.hivePrimitiveFieldTypes, value: keyType"></select>
      <select class="input-small" data-bind="browserAwareSelectize: $root.createWizard.hiveFieldTypes, value: type"></select>
    <!-- /ko -->

      <input type="number" class="input-small" placeholder="${ _('Length') }" data-bind="value: length, visible: type() == 'varchar' || type() == 'char'">
      <!-- ko if: $parent.type() == 'decimal' -->
        <input type="number" class="input-small" placeholder="${ _('Precision') }" data-bind="value: precision">
        <input type="number" class="input-small" placeholder="${ _('Scale') }" data-bind="value: scale">
      <!-- /ko -->
    </label>

    <!-- ko if: $root.createWizard.source.inputFormat() != 'manual' && typeof isPartition !== 'undefined' && isPartition() -->
      <label class="margin-left-5">${ _('Value') }&nbsp;
        <input type="text" class="input-medium margin-left-5" placeholder="${ _('Partition value') }" data-bind="value: partitionValue">
      </label>
    <!-- /ko -->

    <span data-bind="visible: level() == 0 || ($parent.type() != 'array' && $parent.type() != 'map')">
      <a href="javascript:void(0)" title="${ _('Show field properties') }" data-bind="css: {'inactive-action': !showProperties()}, click: function() {showProperties(!showProperties()) }"><i class="fa fa-sliders"></i></a>

      <span data-bind="visible: showProperties">
        <input type="text" class="input-medium margin-left-5" placeholder="${ _('Field comment') }" data-bind="value: comment">
        <label class="checkbox" data-bind="visible: $root.createWizard.destination.tableFormat() == 'kudu'">
          <input type="checkbox" data-bind="checked: keep"> ${_('Keep')}
        </label>
      </span>
    </span>

    <!-- ko if: level() > 0 && $parent.type() == 'struct' && $parent.nested().length > 1 -->
      <a data-bind="click: function() { $parent.nested.remove($data); }"><i class="fa fa-minus"></i></a>
    <!-- /ko -->

    <div class="inline-block" data-bind="template: { name:'field-column-example' }"></div>

    <!-- ko if: type() == 'array' || type() == 'map' || type() == 'struct' -->
      <div class="operation" data-bind="template: { name: 'table-field-template', foreach: nested }"></div>
      <a data-bind="click: function() { nested.push($root.loadDefaultField({level: level() + 1})); }, visible: type() == 'struct'"><i class="fa fa-plus"></i></a>
    <!-- /ko -->
  </div>
</script>


<script type="text/html" id="index-field-template">
  <label>${ _('Name') }&nbsp;
    <input type="text" class="input-large" placeholder="${ _('Field name') }" data-bind="value: name, enable: keep" pattern="^(?!_version_)[a-zA-Z_][a-zA-Z0-9_]*$" title="${ _('Only alphanumeric and underscore characters and not _version_') }">
  </label>
  <!-- ko if: $root.createWizard.source.inputFormat() != 'rdbms' -->
  <label class="margin-left-5">${ _('Type') }&nbsp;
    <select class="input-small" data-bind="browserAwareSelectize: $root.createWizard.fieldTypes, value: type"></select>
  </label>
  <!-- /ko -->
  <!-- ko if: $root.createWizard.source.inputFormat() == 'rdbms' -->
  <label class="margin-left-5">${ _('Type') }&nbsp;
    <input type="text" class="input-small" placeholder="${ _('Field Type') }" data-bind="value: type, enable: false">
  </label>
  <!-- /ko -->
  <a href="javascript:void(0)" title="${ _('Show field properties') }" data-bind="css: {'inactive-action': !showProperties()}, click: function() {showProperties(!showProperties()) }"><i class="fa fa-sliders"></i></a>
  <span data-bind="visible: showProperties" class="field-properties">
    <!-- ko if: $root.createWizard.source.inputFormat() != 'rdbms' -->
    <label class="checkbox">
      <input type="checkbox" data-bind="checked: unique"> ${_('Unique')}
    </label>
    <label class="checkbox">
      <input type="checkbox" data-bind="checked: required"> ${_('Required')}
    </label>
    <!-- /ko -->
    <label class="checkbox">
      <input type="checkbox" data-bind="checked: keep"> ${_('Keep')}
    </label>
  </span>

  <!-- ko if: operations().length == 0 -->
  <a class="pointer margin-left-20" data-bind="click: $root.createWizard.addOperation, visible: $root.createWizard.destination.outputFormat() == 'index'" title="${_('Add Operation')}">
    <i class="fa fa-plus"></i> ${_('Operation')}
  </a>
  <!-- /ko -->

  <div class="inline-block" data-bind="template: { name: 'field-column-example' }"></div>

  <div data-bind="foreach: operations">
    <div data-bind="template: { name:'operation-template',data: { operation: $data, list: $parent.operations } }"></div>
  </div>

  <!-- ko if: operations().length > 0 -->
  <a class="pointer" data-bind="click: $root.createWizard.addOperation" title="${_('Add Operation')}"><i class="fa fa-plus"></i> ${_('Operation to')} <span data-bind="text: name"></span></a>
  <!-- /ko -->

</script>


<script type="text/html" id="field-column-example">
  <!-- ko if: $root.createWizard.source.inputFormat() != 'manual' && level() == 0 && (typeof isPartition === 'undefined' || !isPartition()) -->
    <!-- ko if: $root.createWizard.source.sample() && $root.createWizard.source.sample().length > 0 -->
      <div class="inline-block muted field-content-preview" data-bind="truncatedText: $root.createWizard.source.sample()[0][$index()]"></div>
      <!-- ko if: $root.createWizard.source.sample().length > 1 -->
      <div class="inline-block muted field-content-preview" data-bind="truncatedText: $root.createWizard.source.sample()[1][$index()]"></div>
      <!-- /ko -->
    <!-- /ko -->
    <!-- ko if: !$root.createWizard.source.sample() || $root.createWizard.source.sample().length === 0 -->
    <div class="inline-block muted field-content-preview">${ _("No sample to be shown") }</div>
    <!-- /ko -->
  <!-- /ko -->
</script>


<script type="text/html" id="operation-template">
  <div class="operation">
    <select data-bind="browserAwareSelectize: $root.createWizard.operationTypesFiltered, value: operation.type"></select>
    <!-- ko template: "args-template" --><!-- /ko -->
    <!-- ko if: operation.settings().outputType() == "custom_fields" -->
      <label class="margin-left-5">${ _('Number of expected fields') }
      <input type="number" class="input-mini" data-bind="value: operation.numExpectedFields">
      </label>
    <!-- /ko -->
    <a class="pointer margin-left-20" data-bind="click: function(){$root.createWizard.removeOperation(operation, list)}" title="${ _('Remove') }"><i class="fa fa-times"></i></a>
    <div class="margin-left-20" data-bind="foreach: operation.fields">
      <div data-bind="template: { name: 'index-field-template', data: $data }, css:{ 'disabled': !keep() }" class="margin-top-10 field index-field"></div>
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
    <input type="text" class="input" data-bind="attr: {placeholder: description}, value: value">
  </label>
</script>

<script type="text/html" id="arg-text-delimiter">
  <label>
    <div data-bind="text: description"></div>
    <select data-bind="selectize: $root.createWizard.customDelimiters, selectizeOptions: { onOptionAdd: function(value){ $root.createWizard.customDelimiters.push({ 'value': value, 'name': value }) }, create: true, maxLength: 2 }, value: value, optionsValue: 'value', optionsText: 'name', attr: {placeholder: description}"></select>
  </label>
</script>

<script type="text/html" id="arg-checkbox">
  <label class="checkbox">
    <input type="checkbox" data-bind="checked: value">
    <span data-bind="text: description" style="vertical-align: middle"></span>
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
      <div class="progress-snippet progress" data-bind="css: {
        'progress-starting': progress() == 0 && status() == 'running',
        'progress-warning': progress() > 0 && progress() < 100,
        'progress-success': progress() == 100,
        'progress-danger': progress() == 0 && errors().length > 0}" style="background-color: #FFF; width: 100%; height: 4px">
        <div class="bar" data-bind="style: {'width': (errors().length > 0 ? 100 : Math.max(2, progress())) + '%'}"></div>
      </div>
    <div class="snippet-error-container alert alert-error alert-error-gradient" data-bind="visible: errors().length > 0">
      <ul class="unstyled" data-bind="foreach: errors">
        <li data-bind="text: message"></li>
      </ul>
    </div>
    <!-- /ko -->
  <!-- /ko -->
</script>

<script type="text/html" id="kafka-topic-template">
  <div class="control-group">
    <label class="control-label"><div>${ _('Topics') }</div>
      <select class="input-xxlarge" data-bind="options: createWizard.source.kafkaTopics,
            value: createWizard.source.kafkaSelectedTopics,
            optionsCaption: '${ _("Choose...") }'"
            placeholder="${ _('The list of topics to consume, e.g. orders,returns') }">
      </select>
      ## <select data-bind="selectize: createWizard.source.kafkaTopics, value: createWizard.source.kafkaSelectedTopics" placeholder="${ _('The list of topics to consume, e.g. orders,returns') }"></select>
    </label>

    <br/>

    <label class="control-group" data-bind="visible: createWizard.source.kafkaSelectedTopics">
      <label class="control-label"><div>${ _('Schema') }</div>
        <label class="radio margin-right-10">
          <input type="radio" name="kafkaSchemaManual" value="manual" data-bind="checked: createWizard.source.kafkaSchemaManual" /> ${_('Manual')}
        </label>
        <label class="radio">
          <input type="radio" name="kafkaSchemaManual" value="detect" data-bind="checked: createWizard.source.kafkaSchemaManual" /> ${_('Guess')}
        </label>
      </label>

      <!-- ko if: createWizard.source.kafkaSchemaManual() == 'manual' -->
      ##<label class="control-label"><div>${ _('Encoding') }</div>
      ##  <input type="text" class="input-xxlarge" data-bind="value: createWizard.source.kafkaFieldType">
      ##</label>
      <br/>
      <label class="control-label"><div>${ _('Type') }</div>
        <select class="input-medium" data-bind="options: ['delimited', 'bitarray'], value: createWizard.source.kafkaFieldType"></select>
      </label>
      <label class="control-label"><div>${ _('Delimiter') }</div>
        <input type="text" class="input-small" data-bind="value: createWizard.source.kafkaFieldDelimiter">
      </label>
      <br/>
      <label class="control-label"><div>${ _('Field names') }</div>
        <input type="text" class="input-xxlarge" data-bind="value: createWizard.source.kafkaFieldNames" placeholder="${ _('The list of fields to consume, e.g. orders,returns') }">
      </label>
      <br/>
      <label class="control-label"><div>${ _('Field types') }</div>
        <input type="text" class="input-xxlarge" data-bind="value: createWizard.source.kafkaFieldTypes" placeholder="${ _('The list of field typs, e.g. string,int') }">
      </label>
      <br/>
      <label class="control-label" data-bind="visible: createWizard.source.hasStreamSelected"><div></div>
        <button class="btn" data-bind="click: createWizard.source.streamCheckConnection">${_('Test')}</button>
      </label>
      <!-- /ko -->
    </div>
  </div>
</script>

<div id="showCommandsModal" class="modal transparent-modal hide" data-backdrop="true" style="width:980px; margin-left:-510px!important">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
    <h2 class="modal-title">${_('Commands')}</h2>
  </div>
  <div class="modal-body">
    <div class="editor-help two-pane">
      <div class="tab-content">
        <div class="tab-pane active" id="help-editor-syntax">
          <ul class="nav nav-tabs">
            <li class="active">
              <a href="#help-editor-syntax-comment" data-bind="click: function(){ $('a[href=\'#help-editor-syntax-comment\']').tab('show'); }">
                ${ _('Commands')}
              </a>
            </li>
            <li>
              <a href="#help-editor-syntax-click" data-bind="click: function(){ $('a[href=\'#help-editor-syntax-click\']').tab('show'); }">
                ${ _('Shell')}
              </a>
            </li>
            <li>
              <a href="#help-editor-syntax-multiquery" data-bind="click: function(){ $('a[href=\'#help-editor-syntax-multiquery\']').tab('show'); }">
                ${ _('REST')}
              </a>
            </li>
          </ul>
          <div class="tab-content">
            <div class="tab-pane active" id="help-editor-syntax-comment">
              <div data-bind="text: createWizard.commands" style="white-space: pre-wrap;">
              </div>
            </div>
            <div class="tab-pane" id="help-editor-syntax-click">
              <ul class="nav help-list-spacing">
              </ul>
            </div>
            <div class="tab-pane" id="help-editor-syntax-multiquery">
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div class="modal-footer">
    <a href="javascript: void(0)" class="btn" data-dismiss="modal">${_('Close')}</a>
  </div>
</div>


<script type="text/javascript">
  % if is_embeddable:
  var MAIN_SCROLLABLE = '.page-content';
  % else:
  var MAIN_SCROLLABLE = '.content-panel';
  % endif

  (function () {
    if (ko.options) {
      ko.options.deferUpdates = true;
    }

    var MAPPINGS = {
      SOLR_TO_HIVE: {
        "string": "string",
        "plong": "bigint",
        "pdouble": "double",
        "pdate": "timestamp",
        "long": "bigint",
        "double": "double",
        "date": "timestamp",
        "boolean": "boolean",
      },
      HIVE_TO_SOLR: {
        "bigint": "plong"
      },
      get: function(type, key, defaultValue) {
        return type[key] || defaultValue
      }
    };

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
        if (arg.type === "mapping") {
          return ko.observableArray([]);
        }
        if (arg.type === "checkbox") {
          return ko.observable(false);
        }
        return ko.observable("");
      };

      var constructSettings = function (type) {
        var settings = {};

        var operation = viewModel.createWizard.operationTypes.find(function (currOperation) {
          return currOperation.name === type;
        });

        for (var i = 0; i < operation.args.length; i++) {
          var argVal = createArgumentValue(operation.args[i]);

          if (operation.args[i].type === "checkbox" && operation.outputType === "checkbox_fields") {
            argVal.subscribe(function (newVal) {
              if (newVal) {
                self.fields.push(createDefaultField());
              } else {
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
        };

        return settings;
      };

      var init = function () {
        self.fields([]);
        self.numExpectedFields(0);

        self.numExpectedFields.subscribe(function (numExpectedFields) {
          if (numExpectedFields < self.fields().length) {
            self.fields(self.fields().slice(0, numExpectedFields));
          } else if (numExpectedFields > self.fields().length) {
            var difference = numExpectedFields - self.fields().length;

            for (var i = 0; i < difference; i++) {
              self.fields.push(createDefaultField());
            }
          }
        });
        self.settings(constructSettings(self.type()));
      };

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
      };

      self.type = ko.observable(type);
      self.fields = ko.observableArray();
      self.numExpectedFields = ko.observable();
      self.settings = ko.observable();

      init();

      self.type.subscribe(function () {
        init();
      });
    };

    var FileType = function (typeName, args) {
      var self = this;
      var type;

      var init = function () {
        self.type = ko.observable(typeName);
        var types = viewModel.createWizard.fileTypes;

        for (var i = 0; i < types.length; i++) {
          if (types[i].name === typeName) {
            type = types[i];
            break;
          }
        }

        if (type) {
          for (var i = 0; i < type.args.length; i++) {
            self[type.args[i].name] = ko.observable();
          }

          if (args) {
            loadFromObj(args);
          }

          setTimeout(function () {
            var types = type.args.filter(function (x){
              return x && (x.type !== 'checkbox' || x.name === 'hasHeader');
            });
            for (var i = 0; i < types.length; i++) {
              self[types[i].name].subscribe(function() {
                // Update the data preview when tweaking Format options on step 1
                viewModel.createWizard.guessFieldTypes();
              });
            }
          }); // Prevent notification on start
        }
      };

      var loadFromObj = function (args) {
        for (var attr in args) {
          self[attr] = ko.mapping.fromJS(args[attr]);
        }
      };

      self.getArguments = function () {
        return type ? type.args : [];
      };

      self.isCustomizable = function () {
        return type.isCustomizable;
      };

      init();
    };

    var Source = function (vm, wizard) {
      var self = this;

      self.sourceType = vm.sourceType;
      self.name = ko.observable('');
      self.sample = ko.observableArray();
      self.sampleCols = ko.observableArray();
      self.namespace = wizard.namespace;
      self.compute = wizard.compute;

      var refreshThrottle = -1;
      var sampleColSubDisposals = [];
      var lastStatement = '';
      var refreshTemporaryTable = function (sampleCols) {
        window.clearTimeout(refreshThrottle);
        window.setTimeout(function () {
          while (sampleColSubDisposals.length) {
            sampleColSubDisposals.pop()();
          }
          if (!self.sampleCols().length) {
            return;
          }

          var tableName = 'input';
          switch (self.inputFormat()) {
            case 'stream':
              if (self.streamSelection() === 'kafka' && self.kafkaSelectedTopics()) {
                tableName = self.kafkaSelectedTopics();
              }
              break;
            case 'file' :
              tableName = self.path().split('/').pop();
              break;
            case 'table':
            case 'rdbms':
              tableName = self.tableName();
          }

          var statementCols = [];
          var temporaryColumns = [];

          var deferreds = []; // TODO: Move to async/await when in webpack

          sampleCols.forEach(function (sampleCol) {
            var deferred = $.Deferred();
            deferreds.push(deferred);
            sqlUtils.backTickIfNeeded({ id: self.sourceType, dialect: self.sourceType }, sampleCol.name()).then(function (value) {
              statementCols.push(value);
              var col = {
                name: sampleCol.name(),
                type: sampleCol.type()
              };
              temporaryColumns.push(col);
              var colNameSub = sampleCol.name.subscribe(function () {
                refreshTemporaryTable(self.sampleCols())
              });
              var colTypeSub = sampleCol.type.subscribe(function () {
                refreshTemporaryTable(self.sampleCols())
              });
              sampleColSubDisposals.push(function () {
                colNameSub.dispose();
                colTypeSub.dispose();
              })
              deferred.resolve();
            }).catch(deferred.reject);
          });

          $.when.apply($, deferreds).done(function () {
            var statement = 'SELECT ';
            statement += statementCols.join(',\n    ');
            statement += '\n FROM ' + sqlUtils.backTickIfNeeded({ id: self.sourceType, dialect: self.sourceType }, tableName) + ';';
            if (!wizard.destination.fieldEditorValue() || wizard.destination.fieldEditorValue() === lastStatement) {
              wizard.destination.fieldEditorValue(statement);
            }
            lastStatement = statement;
            wizard.destination.fieldEditorPlaceHolder('${ _('Example: SELECT') }' + ' * FROM ' + sqlUtils.backTickIfNeeded({ id: self.sourceType, dialect: self.sourceType }, tableName));

            var handle = dataCatalog.addTemporaryTable({
              namespace: self.namespace(),
              compute: self.compute(),
              connector: { id: self.sourceType }, // TODO: Migrate importer to connectors
              name: tableName,
              columns: temporaryColumns,
              sample: self.sample()
            });
            sampleColSubDisposals.push(function () {
              handle.delete();
            })
          })
        }, 500)
      };


      self.sampleCols.subscribe(refreshTemporaryTable);
      self.inputFormat = ko.observable(wizard.prefill.source_type() ? wizard.prefill.source_type() : 'file');

      self.inputFormat.subscribe(function(val) {
        wizard.destination.columns.removeAll();
        if (self.sample()) {
          self.sample.removeAll();
        }
        self.path('');
        resizeElements();
        if (val === 'stream') {
          if (self.streamSelection() === 'kafka') {
            wizard.guessFormat();
            wizard.destination.tableFormat('kudu');
          } else {
            wizard.destination.tableFormat('text');
          }
        } else if (val === 'table') {
          wizard.destination.outputFormat('altus');
        } else if (val === 'rdbms') {
          self.rdbmsMode('customRdbms');
        }
      });
      self.inputFormatsAll = ko.observableArray([
          % if request.fs:
          {'value': 'file', 'name': 'File'},
          % endif
          % if ENABLE_SQOOP.get():
          {'value': 'rdbms', 'name': 'External Database'},
          % endif
          % if ENABLE_KAFKA.get():
          {'value': 'stream', 'name': 'Stream'},
          % endif
          % if ENABLE_ALTUS.get():
          {'value': 'table', 'name': 'Table'},
          % endif
          % if ENABLE_SQL_INDEXER.get():
          {'value': 'query', 'name': 'SQL Query'},
          % endif
          ## TODO: Rename to 'Connectors'
          % if ENABLE_ENVELOPE.get():
          {'value': 'connector', 'name': 'Connectors'},
          % endif
          {'value': 'manual', 'name': 'Manually'}
          ##{'value': 'text', 'name': 'Paste Text'},
      ]);
      self.inputFormatsManual = ko.observableArray([
          {'value': 'manual', 'name': 'Manually'}
      ]);
      self.inputFormats = ko.pureComputed(function() {
        if (wizard.prefill.source_type() === 'manual') {
          return self.inputFormatsManual();
        }
        return self.inputFormatsAll();
      });

      // File
      self.path = ko.observable('');
      self.path.subscribe(function(val) {
        if (val) {
          wizard.guessFormat();
          wizard.destination.nonDefaultLocation(val);
        }
        resizeElements();
      });
      self.isObjectStore = ko.pureComputed(function() {
        return self.inputFormat() === 'file' && /^(s3a|adl|abfs):\/.*$/.test(self.path());
      });
      self.isObjectStore.subscribe(function(newVal) {
        wizard.destination.useDefaultLocation(!newVal);
      });

      // Rdbms
      self.rdbmsMode = ko.observable();
      self.rdbmsMode.subscribe(function (val) {
        self.rdbmsTypes(null);
        self.rdbmsType('');
        self.rdbmsDatabaseName('');
        self.rdbmsIsAllTables(false);
        self.rdbmsJdbcDriver('');
        self.rdbmsJdbcDriverName('');
        self.rdbmsHostname('');
        self.rdbmsPort('');
        self.rdbmsUsername('');
        self.rdbmsPassword('');
        self.rdbmsDbIsValid(false);
        if (val === 'configRdbms') {
          $.post("${ url('indexer:get_drivers') }", {}, function (resp) {
            if (resp.data) {
              self.rdbmsTypes(resp.data);
              window.setTimeout(function(){
                self.rdbmsType(self.rdbmsTypes()[0].value);
              }, 0);
            }
          });
        } else if (val === 'customRdbms') {
          self.rdbmsTypes([
            {'value': 'jdbc', 'name': 'JDBC'},
            {'value': 'mysql', 'name': 'MySQL'},
            {'value': 'oracle', 'name': 'Oracle'},
            {'value': 'postgresql', 'name': 'PostgreSQL'}
          ]);
          window.setTimeout(function(){
            self.rdbmsType(self.rdbmsTypes()[0].value);
          }, 0);

        }
      });
      self.rdbmsTypes = ko.observableArray();

      self.rdbmsType = ko.observable(null);
      self.rdbmsType.subscribe(function (val) {
        self.path('');
        self.rdbmsDatabaseNames([]);
        self.rdbmsDatabaseName('');
        resizeElements();
        if(self.rdbmsMode() === 'configRdbms' && val !== 'jdbc') {
          self.isFetchingDatabaseNames(true);
          $.post("${ url('indexer:get_db_component') }", {
            "source": ko.mapping.toJSON(self)
          }, function (resp) {
            if (resp.data) {
              self.rdbmsDatabaseNames(resp.data);
            }
          }).always(function(){
            self.isFetchingDatabaseNames(false);
          });
        } else if(self.rdbmsMode() === 'configRdbms' && val === 'jdbc') {
          self.isFetchingDriverNames(true);
          $.post("${ url('indexer:jdbc_db_list') }", {
            "source": ko.mapping.toJSON(self)
          }, function (resp) {
            if (resp.data) {
              self.rdbmsJdbcDriverNames(resp.data);
            }
          }).always(function() {
            self.isFetchingDriverNames(false);
          });
        }
      });
      self.rdbmsDatabaseName = ko.observable('');
      self.rdbmsDatabaseName.subscribe(function (val) {
        if (val !== '') {
          self.isFetchingTableNames(true);
          $.post("${ url('indexer:get_db_component') }", {
            "source": ko.mapping.toJSON(self)
          }, function (resp) {
            if (resp.data) {
              self.rdbmsTableNames(resp.data.map(function(opt) {
                return ko.mapping.fromJS(opt);
              }));
            }
          }).always(function(){
            self.isFetchingTableNames(false);
          });
        }
      });
      self.rdbmsDatabaseNames = ko.observableArray();
      self.isFetchingDatabaseNames = ko.observable(false);
      self.rdbmsJdbcDriverNames = ko.observableArray();
      self.isFetchingDriverNames = ko.observable(false);
      self.rdbmsJdbcDriverName = ko.observable();
      self.rdbmsJdbcDriverName.subscribe(function () {
        self.rdbmsDatabaseNames([]);
        self.rdbmsDatabaseName('');
        self.isFetchingDatabaseNames(true);
        $.post("${ url('indexer:get_db_component') }", {
          "source": ko.mapping.toJSON(self)
        }, function (resp) {
          if (resp.data) {
            self.rdbmsDatabaseNames(resp.data);
          }
        }).always(function(){
          self.isFetchingDatabaseNames(false);
        });
      });
      self.rdbmsJdbcDriver = ko.observable('');
      self.rdbmsJdbcDriver.subscribe(function () {
        self.rdbmsDatabaseNames([]);
      });
      self.isFetchingTableNames = ko.observable(false);
      self.rdbmsTableNames = ko.observableArray();

      self.rdbmsHostname = ko.observable('');
      self.rdbmsHostname.subscribe(function () {
        self.rdbmsDatabaseNames([]);
      });
      self.rdbmsPort = ko.observable('');
      self.rdbmsPort.subscribe(function () {
        self.rdbmsDatabaseNames([]);
      });
      self.rdbmsUsername = ko.observable('');
      self.rdbmsUsername.subscribe(function () {
        self.rdbmsDatabaseNames([]);
      });
      self.rdbmsPassword = ko.observable('');
      self.rdbmsPassword.subscribe(function () {
        self.rdbmsDatabaseNames([]);
      });
      self.rdbmsIsAllTables = ko.observable(false);
      self.rdbmsIsAllTables.subscribe(function(newVal) {
        if (newVal) {
          wizard.destination.name(self.rdbmsDatabaseName());
        } else {
          wizard.destination.name(self.tables()[0] && self.tables()[0].name() || '');
        }
      });
      self.rdbmsAllTablesSelected = ko.pureComputed(function () {
        return self.rdbmsIsAllTables() || self.tables().length > 1;
      });
      self.rdbmsTablesExclude = ko.pureComputed(function () {
        var rdbmsTables = self.rdbmsTableNames();
        var tables = self.tables();
        if (tables.length <= 1) {
          return [];
        }
        var map = tables.reduce(function (map, table) {
          map[table.name()] = 1;
          return map;
        }, {});
        return rdbmsTables.map(function (table) {
          return table.name();
        }).filter(function (name) {
          return !map[name];
        });
      });
      self.rdbmsDbIsValid = ko.observable(false);
      self.rdbmsCheckConnection = function() {
        self.isFetchingDatabaseNames(true);
        self.rdbmsDatabaseNames([]);
        self.rdbmsDatabaseName(''); // Need to clear or else get_db_component will return list of tables
        $.post("${ url('indexer:get_db_component') }", {
          "source": ko.mapping.toJSON(self)
        }, function (resp) {
          if (resp.status === 0 && resp.data) {
            self.rdbmsDbIsValid(true);
            self.rdbmsDatabaseNames(resp.data);
          } else if (resp.status === 1) {
            $(document).trigger("error", "${ _('Connection Failed: ') }" + resp.message);
            self.rdbmsDbIsValid(false);
          }
        }).always(function(){
          self.isFetchingDatabaseNames(false);
        });
      };

      // Table
      self.tables = ko.observableArray([
        ko.mapping.fromJS({ name: '' })
      ]);
      self.tables.subscribe(function(newVal) {
        if (newVal.length == 0) {
          wizard.destination.name('');
        } else if (newVal.length == 1) {
          wizard.destination.name(self.tables()[0].name() || ''); // TODO: db prefix and check if DB exists
        } else {
          wizard.destination.name(self.rdbmsDatabaseName());
        }
      });
      self.tablesNames = ko.observableArray([]);
      self.selectedTableIndex = ko.observable(0);
      self.table = ko.pureComputed(function() {
        var index = Math.min(self.selectedTableIndex(), self.tables().length - 1);
        return self.tables().length > 0 ? self.tables()[index].name() : ''
      });
      self.tableName = ko.pureComputed(function() {
        return self.table().indexOf('.') > 0 ? self.table().split('.', 2)[1] : self.table();
      });
      self.databaseName = ko.pureComputed(function() {
        return self.table().indexOf('.') > 0 ? self.table().split('.', 2)[0] : 'default';
      });
      self.table.subscribe(function(val) {
        if (val) {
          wizard.guessFormat();
          wizard.destination.nonDefaultLocation(val);
        }
        resizeElements();
      });

      // Queries
      self.query = ko.observable('');
      self.query.subscribe(function(newValue) {
        if (newValue) {
          viewModel.createWizard.guessFieldTypes();
        }
      });
      self.draggedQuery = ko.observable();

      // Connectors
      self.connectorList = ko.observable([
        {'value': 'sfdc', 'name': 'Salesforce'}
      ]);
      self.connectorSelection = ko.observable(self.connectorList()[0]['value']);

      // Streams, Kafka, Flume
      self.publicStreams = ko.observable([
        {'value': 'kafka', 'name': 'Kafka Topics'},
        {'value': 'flume', 'name': 'Flume Agent'}
      ]);
      self.streamSelection = ko.observable(self.publicStreams()[0]['value']);
      self.streamSelection.subscribe(function(newValue) {
        if (newValue == 'flume') {
          $.post("${ url('metadata:manager_hosts') }", {
            "service": "flume"
          }, function (resp) {
            if (resp.status === 0 && resp.hosts) {
              self.channelSourceHosts(resp.hosts);
            } else {
              $(document).trigger("error", "${ _('Error getting hosts') }" + resp.message);
            }
          });
        }
      });

      self.kafkaTopics = ko.observableArray();
      self.kafkaSelectedTopics = ko.observable(''); // Currently designed just for one
      self.kafkaSelectedTopics.subscribe(function(newValue) {
        if (newValue) {
          viewModel.createWizard.guessFieldTypes();
          self.kafkaFieldNames($.totalStorage('pai' + '_kafka_topics_' + newValue + '_kafkaFieldNames'));
          self.kafkaFieldTypes($.totalStorage('pai' + '_kafka_topics_' + newValue + '_kafkaFieldTypes'));
        }
      });
      self.kafkaSchemaManual = ko.observable('manual');
      self.kafkaFieldType = ko.observable('delimited');
      self.kafkaFieldDelimiter = ko.observable(',');
      self.kafkaFieldNames = ko.observable('');
      self.kafkaFieldNames.subscribe(function(newValue) {
        $.totalStorage('pai' + '_kafka_topics_' + self.kafkaSelectedTopics() + '_kafkaFieldNames', newValue);
        viewModel.createWizard.guessFieldTypes();
      });
      self.kafkaFieldTypes = ko.observable('');
      self.kafkaFieldTypes.subscribe(function(newValue) {
        $.totalStorage('pai' + '_kafka_topics_' + self.kafkaSelectedTopics() + '_kafkaFieldTypes', newValue);
        viewModel.createWizard.guessFieldTypes();
      });
      self.kafkaFieldSchemaPath = ko.observable('');

      self.channelSourceTypes = ko.observableArray([
        {'name': '${ _("Directory or File") }', 'value': 'directory'},
        {'name': '${ _("Program") }', 'value': 'exec'},
        {'name': '${ _("Syslogs") }', 'value': 'syslogs'},
        {'name': '${ _("HTTP") }', 'value': 'http'}
      ]);
      self.channelSourceType = ko.observable();
      self.channelSourceHosts = ko.observableArray();
      self.channelSourceSelectedHosts = ko.observableArray([]);
      self.channelSourceSelectedHosts.subscribe(function(newVal) {
        if (newVal) {
          viewModel.createWizard.guessFieldTypes();
        }
      })
      self.channelSourcePath = ko.observable('/var/log/hue-httpd/access_log');

      self.streamUsername = ko.observable('');
      self.streamPassword = ko.observable('');
      self.streamToken = ko.observable('');
      self.streamToken.subscribe(function(newVal) {
        if (newVal) {
          wizard.guessFormat(); // Todo
        }
      });
      self.streamEndpointUrl = ko.observable('https://login.salesforce.com/services/Soap/u/42.0');
      self.streamObjects = ko.observableArray();
      self.streamObject = ko.observable();
      self.streamObject.subscribe(function(newValue) {
        if (newValue) {
          wizard.guessFieldTypes();
        }
      });
      self.hasStreamSelected = ko.pureComputed(function() {
        return (self.streamSelection() === 'kafka' && self.kafkaSelectedTopics()) ||
           (self.streamSelection() === 'sfdc' && self.streamObject())
      });
      self.hasStreamSelected.subscribe(function(newValue) {
        if (newValue) {
          wizard.guessFormat();
          if (self.streamSelection() === 'kafka') {
            wizard.destination.tableFormat('kudu');
          } else {
            wizard.destination.tableFormat('text');
          }
        }
      });
      self.streamCheckConnection = function() {
        $(".jHueNotify").remove();
        $.post("${ url('indexer:get_db_component') }", {
          "source": ko.mapping.toJSON(self)
        }, function (resp) {
          if (resp.status === 0 && resp.data) {
            huePubSub.publish('notebook.task.submitted', resp);
          } else if (resp.status === 1) {
            $(document).trigger("error", "${ _('Connection Failed: ') }" + resp.message);
            self.rdbmsDbIsValid(false);
          }
        });
      };

      self.format = ko.observable();
      self.format.subscribe(function(newVal) {
        if (typeof newVal.hasHeader !== 'undefined') {
          wizard.destination.hasHeader(newVal.hasHeader());
          newVal.hasHeader.subscribe(function(newVal) {
            wizard.destination.hasHeader(newVal);
          });
        }

        if (typeof newVal.fieldSeparator !== 'undefined') {
          wizard.destination.useCustomDelimiters(newVal.fieldSeparator() !== ',');
          wizard.destination.customFieldDelimiter(newVal.fieldSeparator());
          newVal.fieldSeparator.subscribe(function(newVal) {
            if (newVal !== '') {
              wizard.destination.customFieldDelimiter(newVal);
            }
          });
        }
      });

      self.show = ko.pureComputed(function() {
        if (self.inputFormat() === 'file') {
          return self.path().length > 0;
        }
        if (self.inputFormat() === 'table') {
          return self.tableName().length > 0;
        }
        if (self.inputFormat() === 'query') {
          return self.query();
        }
        if (self.inputFormat() === 'manual') {
          return true;
        }
        if (self.inputFormat() === 'stream') {
          if (self.streamSelection() === 'kafka') {
            return self.kafkaSelectedTopics() && self.kafkaSelectedTopics().length > 0;
          } else if (self.streamSelection() === 'flume') {
            return self.channelSourceSelectedHosts().length > 0;
          }
        }
        if (self.inputFormat() === 'sfdc') {
          return self.streamUsername().length > 0 &&
              self.streamPassword().length > 0 &&
              self.streamToken().length > 0 &&
              self.streamEndpointUrl().length > 0 &&
              self.streamObject();
        }
        if (self.inputFormat() === 'rdbms') {
          return (self.rdbmsDatabaseName().length > 0 && self.tables().length > 0) || self.rdbmsAllTablesSelected();
        }
      });
    };

    var Destination = function (vm, wizard) {
      var self = this;
      self.apiHelperType = self.sourceType = vm.sourceType;

      self.name = ko.observable('').extend({ throttle: 500 });
      self.nameChanged = function(name) {
        var exists = false;

        var checkDbEntryExists = function () {
          wizard.computeSetDeferred.done(function () {
            dataCatalog.getEntry({
              compute: wizard.compute(),
              connector: { id: self.sourceType }, // TODO: Use connectors in the importer
              namespace: wizard.namespace(),
              path: self.outputFormat() === 'table' ? [self.databaseName(), self.tableName()] : [],
            }).done(function (catalogEntry) {
              catalogEntry.getSourceMeta({ silenceErrors: true }).done(function (sourceMeta) {
                self.isTargetExisting(self.outputFormat() === 'table' ? !sourceMeta.notFound : (sourceMeta.databases || []).indexOf(self.databaseName()) >= 0);
                self.isTargetChecking(false);
              }).fail(function () {
                self.isTargetExisting(false);
                self.isTargetChecking(false);
              })
            });
          })
        };

        if (name.length === 0) {
          self.isTargetExisting(false);
          self.isTargetChecking(false);
        } else if (self.outputFormat() === 'file') {
          // self.path()
        } else if (self.outputFormat() === 'table' && wizard.isValidDestination()) {
          if (self.tableName() !== '') {
            self.isTargetExisting(false);
            self.isTargetChecking(true);
            checkDbEntryExists();
          } else {
            self.isTargetExisting(false);
            self.isTargetChecking(false);
          }
        } else if (self.outputFormat() === 'hbase') {
          // Todo once autocomplete is implemented for hbase
        } else if (self.outputFormat() === 'database' && wizard.isValidDestination()) {
          if (self.databaseName() !== '') {
            self.isTargetExisting(false);
            self.isTargetChecking(true);
            checkDbEntryExists();
          } else {
            self.isTargetExisting(false);
            self.isTargetChecking(false);
          }
        } else if (self.outputFormat() === 'index') {
          $.post("${ url('indexer:list_index') }", {
              name: self.name()
          }, function (data) {
            self.isTargetExisting(data.status === 0);
            self.isTargetChecking(false);
          }).fail(function (xhr, textStatus, errorThrown) {
            self.isTargetExisting(false);
            self.isTargetChecking(false);
          });
          $.post("/indexer/api/configs/list/", function (data) {
            if (data.status === 0) {
              self.indexerConfigSets(data.configs.map(function (config) {
                return {'name': config, 'value': config};
              }));
            } else {
              $(document).trigger("error", data.message);
            }
          });
        }
        resizeElements();
      };
      self.name.subscribe(self.nameChanged);

      self.description = ko.observable('');
      self.outputFormat = ko.observable(wizard.prefill.target_type() || 'table');
      self.outputFormat.subscribe(function (newValue) {
        if (newValue && newValue !== 'database' && ((['table', 'rdbms', 'index'].indexOf(newValue) >= 0) && wizard.source.table().length > 0)) {
          self.nameChanged(self.name());
          wizard.guessFieldTypes();
          resizeElements();
        }
      });
      self.outputFormatsList = ko.observableArray([
          {'name': '${ _("Table") }', 'value': 'table'},
          % if ENABLE_NEW_INDEXER.get():
          {'name': '${ _("Search index") }', 'value': 'index'},
          % endif
          {'name': '${ _("Database") }', 'value': 'database'},
          % if ENABLE_SQOOP.get() or ENABLE_KAFKA.get():
          {'name': '${ _("Folder") }', 'value': 'file'},
          % endif
          % if ENABLE_KAFKA.get():
          {'name': '${ _("Stream") }', 'value': 'stream'},
          % endif
          % if ENABLE_ALTUS.get():
          {'name': '${ _("Altus SDX") }', 'value': 'altus'},
          % endif
          % if ENABLE_SQOOP.get():
          {'name': '${ _("HBase Table") }', 'value': 'hbase'},
          % endif
      ]);
      self.outputFormats = ko.pureComputed(function() {
        return $.grep(self.outputFormatsList(), function(format) {
          if (format.value === 'database' && wizard.source.inputFormat() !== 'manual' && (wizard.source.inputFormat() !== 'rdbms' || !wizard.source.rdbmsAllTablesSelected())) {
            return false;
          }
          if (format.value === 'file' && ['manual', 'rdbms', 'stream'].indexOf(wizard.source.inputFormat()) === -1) {
            return false;
          }
          if (format.value === 'index' && ['file', 'query', 'stream', 'manual'].indexOf(wizard.source.inputFormat()) === -1) {
            return false;
          }
          if (format.value === 'table' && (wizard.source.inputFormat() === 'table' || (wizard.source.inputFormat() === 'rdbms' && wizard.source.rdbmsAllTablesSelected()))) {
            return false;
          }
          if (format.value === 'altus' && ['table'].indexOf(wizard.source.inputFormat()) === -1) {
            return false;
          }
          if (format.value === 'stream' && ['file', 'stream'].indexOf(wizard.source.inputFormat()) === -1) {
            return false;
          }
          if (format.value === 'hbase' && (wizard.source.inputFormat() !== 'rdbms' || wizard.source.rdbmsAllTablesSelected())) {
            return false;
          }
          return true;
        })
      });
      self.outputFormats.subscribe(function (newValue) {
        if (newValue.length && newValue.map(function (entry) { return entry.value; }).indexOf(self.outputFormat()) < 0) {
          self.outputFormat(newValue && newValue[0].value);
        }
      });
      wizard.prefill.target_type.subscribe(function(newValue) {
        setTimeout(function() { // target_type gets updated by the router (onePageViewModelModel.js) and delaying allow the notification to go through
          self.outputFormat(newValue || 'table');
        },0);
        if (newValue === 'database') {
          vm.currentStep(2);
        } else {
          vm.currentStep(1);
        }
      });
      self.defaultName = ko.pureComputed(function() {
        var name = '';

        if (wizard.source.inputFormat() === 'file' || wizard.source.inputFormat() === 'stream') {
          if (self.outputFormat() === 'table') {
            name = wizard.prefill.target_path().length > 0 ? wizard.prefill.target_path() : 'default';

            if (wizard.source.inputFormat() === 'stream') {
              if (wizard.source.streamSelection() === 'kafka') {
                name += '.' + wizard.source.kafkaSelectedTopics();
              } else {
                name += '.' + wizard.source.streamObject();
              }
            } else if (wizard.source.path()) {
              name += '.' + wizard.source.path().split('/').pop().split('.')[0];
            }
          } else { // Index
            name = wizard.prefill.target_path().length > 0 ? wizard.prefill.target_path() : wizard.source.path().split('/').pop().split('.')[0];
          }
        } else if (wizard.source.inputFormat() === 'table') {
           name = wizard.source.databaseName();
        } else if (wizard.source.inputFormat() === 'query') {
          if (wizard.source.query()) {
            name = wizard.source.name();
          }
          if (wizard.prefill.target_path().length > 0) {
            name = wizard.prefill.target_path();
          }
        } else if (wizard.source.inputFormat() === 'manual') {
          name = wizard.prefill.target_path().length > 0 ? wizard.prefill.target_path() + '.' : '';
        }

        return name.replace(/ /g, '_').toLowerCase();
      });
      self.defaultName.subscribe(function(newVal) {
        self.name(newVal);
      });

      self.format = ko.observable();
      self.columns = ko.observableArray();

      self.namespaces = wizard.namespaces;
      self.namespace = wizard.namespace;
      self.compute = wizard.compute;
      self.targetNamespaceId = ko.observable(self.namespace() ? self.namespace().id : undefined);

      self.namespace.subscribe(function (namespace) {
        if (namespace && namespace.id !== self.targetNamespaceId) {
          self.targetNamespaceId(namespace.id);
        }
      })

      self.targetNamespaceId.subscribe(function (namespaceId) {
        if (namespaceId && (!self.namespace() || self.namespace().id !== namespaceId)) {
          self.namespaces().some(function (namespace) {
            if (namespaceId === namespace.id) {
              self.namespace(namespace);
              return true;
            }
          })
        }
      });

      // UI
      self.bulkColumnNames = ko.observable('');
      self.showProperties = ko.observable(false);

      self.columns.subscribe(function (newVal) {
        self.bulkColumnNames(newVal.map(function (item) {
          return item.name()
        }).join(','));
      });

      self.processBulkColumnNames = function () {
        var val = self.bulkColumnNames();
        try {
          if (val.indexOf("\"") === -1 && val.indexOf("'") === -1) {
            val = '"' + val.replace(/,/gi, '","') + '"';
          }
          if (val.indexOf("[") === -1) {
            val = "[" + val + "]";
          }
          var parsed = JSON.parse(val);
          self.columns().forEach(function (item, cnt) {
            if ($.trim(parsed[cnt]) !== '') {
              item.name($.trim(parsed[cnt]));
            }
          });
        }
        catch (err) {
        }
        $('#fieldsBulkEditor').modal('hide');
      };

      self.isTargetExisting = ko.observable();
      self.isTargetChecking = ko.observable(false);
      self.existingTargetUrl = ko.pureComputed(function() { // Should open generic sample popup instead
        if (self.isTargetExisting()) {
          if (self.outputFormat() === 'file') {
            // Todo
            return '';
          }
          if (self.outputFormat() === 'table') {
            return '/metastore/table/' + self.databaseName() + '/' + self.tableName();
          }
          if (self.outputFormat() === 'database') {
            return '/metastore/tables/' + self.databaseName();
          }
          if (self.outputFormat() === 'index') {
            return '/indexer/indexes/' + self.name();
          }
        }
        return '';
      });

      // Table
      self.tableName = ko.pureComputed(function() {
        return self.outputFormat() === 'table' && self.name().indexOf('.') > 0 ? self.name().split('.', 2)[1] : self.name();
      });
      self.databaseName = ko.pureComputed(function() {
        return self.outputFormat() === 'database' ? self.name() : (self.outputFormat() === 'table' && self.name().indexOf('.') > 0 ? self.name().split('.', 2)[0] : 'default');
      });
      self.tableFormat = ko.observable('text');
      self.KUDU_DEFAULT_RANGE_PARTITION_COLUMN = {values: [{value: ''}], name: 'VALUES', lower_val: 0, include_lower_val: '<=', upper_val: 1, include_upper_val: '<='};
      self.KUDU_DEFAULT_PARTITION_COLUMN = {columns: [], range_partitions: [self.KUDU_DEFAULT_RANGE_PARTITION_COLUMN], name: 'HASH', int_val: 16};

      self.tableFormats = ko.pureComputed(function() {
        if (wizard.source.inputFormat() === 'kafka') {
          return [{'value': 'kudu', 'name': 'Kudu'}];
        } else if (vm.sourceType == 'impala') { // Impala supports Kudu
          return [
            {'value': 'text', 'name': 'Text'},
            {'value': 'parquet', 'name': 'Parquet'},
            {'value': 'kudu', 'name': 'Kudu'},
            {'value': 'csv', 'name': 'Csv'},
            {'value': 'avro', 'name': 'Avro'},
            {'value': 'json', 'name': 'Json'},
            {'value': 'regexp', 'name': 'Regexp'},
            {'value': 'orc', 'name': 'ORC'},
          ];
        }
        return [
          {'value': 'text', 'name': 'Text'},
          {'value': 'parquet', 'name': 'Parquet'},
          {'value': 'csv', 'name': 'Csv'},
          {'value': 'avro', 'name': 'Avro'},
          {'value': 'json', 'name': 'Json'},
          {'value': 'regexp', 'name': 'Regexp'},
          {'value': 'orc', 'name': 'ORC'},
        ]
      });

      self.partitionColumns = ko.observableArray();
      self.kuduPartitionColumns = ko.observableArray();
      self.primaryKeys = ko.observableArray();
      self.primaryKeyObjects = ko.observableArray();

      self.useFieldEditor = ko.observable(false);
      // TODO: Figure out the database to use for field editor autocomplete
      self.fieldEditorDatabase = ko.observable('default');
      // TODO: Do something with the editor value
      self.fieldEditorValue = ko.observable();
      self.fieldEditorPlaceHolder = ko.observable();
      self.fieldEditorEnabled = ko.pureComputed(function () {
        return '${ ENABLE_FIELD_EDITOR.get() }' == 'True';
      });

      self.importData = ko.observable(true);
      self.useDefaultLocation = ko.observable(true);
      self.nonDefaultLocation = ko.observable('');

      var isTransactionalVisibleImpala = '${ impala_flags.is_transactional() }'.toLowerCase() == 'true';
      var isTransactionalVisibleHive = '${ hive_site.has_concurrency_support() }'.toLowerCase() == 'true';
      var transactionalDefaultType = '${ impala_flags.default_transactional_type() }'.toLowerCase();

      self.isTransactionalVisible = ko.observable((vm.sourceType == 'impala' && isTransactionalVisibleImpala) || (vm.sourceType == 'hive' && isTransactionalVisibleHive));
      self.isTransactional = ko.observable(self.isTransactionalVisible());
      self.isInsertOnly = ko.observable(true); // Impala doesn't have yet full support.
      self.isTransactionalUpdateEnabled = ko.pureComputed(function() {
        var enabled = self.tableFormat() == 'orc' && (vm.sourceType == 'hive' || (vm.sourceType == 'impala' && transactionalDefaultType.length && transactionalDefaultType != 'insert_only'));
        if (!enabled) {
          self.isInsertOnly(true);
        }
        return enabled;
      });

      self.hasHeader = ko.observable(false);

      self.useCustomDelimiters = ko.observable(false);
      self.customFieldDelimiter = ko.observable(',');
      self.customCollectionDelimiter = ko.observable('\\002');
      self.customMapDelimiter = ko.observable('\\003');
      self.customRegexp = ko.observable('');

      // Index
      self.indexerRunJob = ko.observable(false);
      self.indexerJobLibPath = ko.observable('${ CONFIG_INDEXER_LIBS_PATH.get() }');
      self.indexerConfigSet = ko.observable('');
      self.indexerConfigSets = ko.observableArray([]);
      self.indexerNumShards = ko.observable(1);
      self.indexerReplicationFactor = ko.observable(1);
      self.indexerPrimaryKey = ko.observableArray();
      self.indexerPrimaryKeyObject = ko.observableArray();
      self.indexerDefaultField = ko.observableArray();
      self.indexerDefaultFieldObject = ko.observableArray();

      // File, Table, HBase
      self.sqoopJobLibPaths = ko.observableArray([]);
      self.addSqoopJobLibPath = function() {
        var newValue = {
          path: ko.observable('')
        };
        self.sqoopJobLibPaths.push(newValue);
      };
      self.addSqoopJobLibPath();
      self.removeSqoopJobLibPath = function (valueToRemove) {
        self.sqoopJobLibPaths.remove(valueToRemove);
      };
      self.numMappers = ko.observable(1);
      self.customFieldsDelimiter = ko.observable(',');
      self.customLineDelimiter = ko.observable('\\n');
      self.customEnclosedByDelimiter = ko.observable('\'');
      self.rdbmsFileOutputFormat = ko.observable('text');
      self.rdbmsFileOutputFormats = ko.observableArray([
          {'value': 'text', 'name': 'text'},
          {'value': 'sequence', 'name': 'sequence'},
          {'value': 'avro', 'name': 'avro'}
      ]);
      self.rdbmsSplitByColumn = ko.observableArray();

      // Flume
      self.channelSinkTypes = ko.observableArray([
        {'name': '${ _("This topic") }', 'value': 'kafka'},
        {'name': '${ _("Solr") }', 'value': 'solr'},
        {'name': '${ _("HDFS") }', 'value': 'hdfs'}
      ]);
      self.channelSinkType = ko.observable();
      self.channelSinkPath = ko.observable();
    };

    var CreateWizard = function (vm) {
      var self = this;
      var guessFieldTypesXhr;

      self.namespaces = ko.observableArray();
      self.namespace = ko.observable();
      self.compute = ko.observable();

      self.computeSetDeferred = $.Deferred();

      // TODO: Use connectors in the importer
      contextCatalog.getNamespaces({ connector: { id: vm.sourceType } }).done(function (context) {
        self.namespaces(context.namespaces);
        if (!vm.namespaceId || !context.namespaces.some(function (namespace) {
          if (namespace.id === vm.namespaceId) {
            self.namespace(namespace);
            return true;
          }
        })) {
          self.namespace(context.namespaces[0]);
        }

        if (!vm.computeId || !self.namespace().computes.some(function (compute) {
          if (compute.id === vm.computeId) {
            self.compute(compute);
            return true;
          }
        })) {
          self.compute(self.namespace().computes[0]);
        }
        self.namespace.subscribe(function (namespace) {
          if (!namespace) {
            self.compute(undefined);
            return;
          }
          if (!self.compute() || !namespace.computes.some(function (compute) {
            if (compute.id === self.compute()) {
              return true;
            }
          })) {
            if (namespace.computes.length) {
              self.compute(namespace.computes[0]);
            }
          }
        })
        self.computeSetDeferred.resolve();
      });

      self.fileType = ko.observable();
      self.fileType.subscribe(function (newType) {
        if (self.source.format()) {
          self.source.format().type(newType.name);
        }
      });

      self.fileTypeName = ko.observable();
      self.fileTypeName.subscribe(function (newType) {
        for (var i = 0; i < self.fileTypes.length; i++) {
          if (self.fileTypes[i].name === newType) {
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

      self.prefill.source_type.subscribe(function(newValue) {
        self.source.inputFormat(newValue ? newValue : 'file');
      });

      self.show = ko.observable(true);
      self.showCreate = ko.observable(false);

      self.source = new Source(vm, self);
      self.destination = new Destination(vm, self);

      self.customDelimiters = ko.observableArray([
        {'value': ',', 'name': '${ _("Comma (,)") }'},
        {'value': '\\t', 'name': '${ _("^Tab (\\t)") }'},
        {'value': '\\n', 'name': '${ _("New line") }'},
        {'value': '|', 'name': '${ _("Pipe") }'},
        {'value': '\"', 'name': '${ _("Double Quote") }'},
        {'value': '\'', 'name': '${ _("Single Quote") }'},
        {'value': '\x00', 'name': '${ _("^0") }'},
        {'value': '\x01', 'name': '${ _("^A (\\001)") }'},
        {'value': '\x02', 'name': '${ _("^B (\\002)") }'},
        {'value': '\x03', 'name': '${ _("^C (\\003)") }'},
        {'value': '\x01', 'name': '${ _("^A (\\x01)") }'}
      ]);

      self.editorId = ko.observable();
      self.jobId = ko.observable();
      self.editorVM = null;

      self.indexingStarted = ko.observable(false);

      self.isValidDestination = ko.pureComputed(function() {
        return self.destination.name().length > 0 && (
          (['table', 'database'].indexOf(self.destination.outputFormat()) === -1 || /^([a-zA-Z0-9_]+\.)?[a-zA-Z0-9_]+$/.test(self.destination.name())) &&
          (['index'].indexOf(self.destination.outputFormat()) === -1 || /^[^\\/:]+$/.test(self.destination.name()))
        );
      });
      self.readyToIndex = ko.pureComputed(function () {
        var validFields = self.destination.columns().length || self.destination.outputFormat() === 'database';
        var validTableColumns = self.destination.outputFormat() !== 'table' || ($.grep(self.destination.columns(), function(column) {
            return column.name().length === 0;
          }).length === 0
          && $.grep(self.destination.partitionColumns(), function(column) {
            return column.name().length === 0 || (self.source.inputFormat() !== 'manual' && column.partitionValue().length === 0);
          }).length === 0
        );
        var isTargetAlreadyExisting;
        if (self.destination.outputFormat() === 'database' && self.source.inputFormat() === 'rdbms') {
          isTargetAlreadyExisting = self.destination.isTargetExisting();
        } else {
          isTargetAlreadyExisting = !self.destination.isTargetExisting()
            || self.destination.outputFormat() === 'index'
            ## Authorize submission but should check if schema is compatible
            || (self.source.inputFormat() === 'stream' && self.destination.outputFormat() === 'table' && self.destination.tableFormat() === 'kudu')
          ;
        }
        var isValidTable = self.destination.outputFormat() !== 'table' || (
          self.destination.tableFormat() !== 'kudu' || (
              $.grep(self.destination.kuduPartitionColumns(), function(partition) {
                return partition.columns().length > 0
              }).length === self.destination.kuduPartitionColumns().length && self.destination.primaryKeys().length > 0
          )
        );
        var validIndexFields = self.destination.outputFormat() !== 'index' || ($.grep(self.destination.columns(), function(column) {
            return ! (/^[a-zA-Z_][a-zA-Z0-9_]*$/.test(column.name()) && column.name() !== '_version_');
          }).length === 0
        ) || self.destination.indexerConfigSet();

        return self.isValidDestination() && validFields && validTableColumns && validIndexFields && isTargetAlreadyExisting && isValidTable;
      });

      self.formatTypeSubscribed = false;

      self.source.format.subscribe(function () {
        for (var i = 0; i < self.fileTypes.length; i++) {
          if (self.fileTypes[i].name === self.source.format().type()) {
            self.fileType(self.fileTypes[i]);
            self.fileTypeName(self.fileTypes[i].name);
            break;
          }
        }

        if (self.source.format().type) {
          if (! self.formatTypeSubscribed) {
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
        self.isGuessingFormat(true);
        self.destination.columns.removeAll();
        $.post("${ url('indexer:guess_format') }", {
          "fileFormat": ko.mapping.toJSON(self.source)
        }, function (resp) {
          if (resp.status !== 0) {
            $(document).trigger("error", resp.message);
          } else {
            var newFormat = ko.mapping.fromJS(new FileType(resp['type'], resp));
            self.source.format(newFormat);
            if (self.source.inputFormat() === 'stream') {
              if (self.source.streamSelection() === 'kafka') {
                self.source.kafkaTopics(resp['topics']);
              } else if (self.source.streamSelection() === 'flume') {
                self.source.streamObjects(resp['objects']);
              }
            } else if (self.source.inputFormat() === 'connector') {
              // Assumes selectectedConnector == 'sfdc'
              self.source.streamObjects(resp['objects']);
            }

            if (self.source.inputFormat() !== 'stream' && self.source.inputFormat() !== 'connector') {
              self.guessFieldTypes();
            }
          }

          self.isGuessingFormat(false);
          viewModel.wizardEnabled(true);
        }).fail(function (xhr) {
          $(document).trigger("error", xhr.responseText);
          viewModel.isLoading(false);
          self.isGuessingFormat(false);
        });
      };

      self.isGuessingFieldTypes = ko.observable(false);

      self.guessFieldTypes = function () {
        if (guessFieldTypesXhr) {
          guessFieldTypesXhr.abort();
        }
        self.isGuessingFieldTypes(true);
        guessFieldTypesXhr = $.post("${ url('indexer:guess_field_types') }", {
          "fileFormat": ko.mapping.toJSON(self.source)
        }, function (resp) {
          self.loadSampleData(resp);
          self.isGuessingFieldTypes(false);
          guessFieldTypesXhr = null;
        }).fail(function (xhr) {
          self.loadSampleData({sample_cols: [], columns: [], sample: []});
          $(document).trigger("error", xhr.responseText);
          self.isGuessingFieldTypes(false);
          viewModel.isLoading(false);
          guessFieldTypesXhr = null;
        });
      };
      self.loadSampleData = function(resp) {
        resp.columns.forEach(function (entry, i, arr) {
          if (self.destination.outputFormat() === 'table' && self.source.inputFormat() != 'rdbms') {
            entry.type = MAPPINGS.get(MAPPINGS.SOLR_TO_HIVE, entry.type, 'string');
          } else if (self.destination.outputFormat() === 'index') {
            entry.type = MAPPINGS.get(MAPPINGS.HIVE_TO_SOLR, entry.type, entry.type);
          }
          arr[i] = loadField(entry, self.destination, i);
        });
        self.source.sampleCols(resp.sample_cols ? resp.sample_cols : resp.columns);
        self.source.sample(resp.sample);
        self.destination.columns(resp.columns);
        if (self.destination.tableFormat() == 'kudu' && $.grep(resp.columns, function(column) { return column.name() == 'id' }).length > 0) {
          self.destination.primaryKeys(['id']); // Auto select ID column
        }
      };
      self.isIndexing = ko.observable(false);
      self.indexingError = ko.observable(false);
      self.indexingSuccess = ko.observable(false);
      self.destination.indexerRunJob.subscribe(function () {
        self.destination.columns().forEach(function (column) {
          column.operations.removeAll();
        });
      });
      self.operationTypesFiltered = ko.pureComputed(function () {
        var indexerRunJob = self.destination.indexerRunJob();
        return self.operationTypes.filter(function (operation) {
          return indexerRunJob || operation.name === 'split'; // We only support split for now with CSV API
        }).map(function (o) {
          return o.name;
        });
      });
      self.commands = ko.observable([]);
      self.showCommands = function() {
        self.indexFile({show: true});
      };
      self.indexFile = function (options) {
        var options = options || {};
        if (!self.readyToIndex()) {
          return;
        }
        $(".jHueNotify").remove();

        self.indexingStarted(true);
%if not is_embeddable:
        viewModel.isLoading(true);
        self.isIndexing(true);

        $.post("${ url('indexer:importer_submit') }", {
          "source": ko.mapping.toJSON(self.source),
          "destination": ko.mapping.toJSON(self.destination)
        }, function (resp) {
          if (resp.status !== 0) {
            $(document).trigger("error", resp.message);
            self.indexingStarted(false);
            self.isIndexing(false);
          } else if (resp.on_success_url) {
            $.jHueNotify.info("${ _('Creation success.') }");
            if (resp.pubSubUrl) {
              huePubSub.publish(notebook.pubSubUrl);
            }
            huePubSub.publish('open.link', resp.on_success_url);
          } else {
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
                },
                sqoop1: {
                  placeHolder: '${ _("Example: import  --connect jdbc:hsqldb:file:db.hsqldb --table TT --target-dir hdfs://localhost:8020/user/foo -m 1") }',
                  snippetImage: '${ static("sqoop/art/icon_sqoop_48.png") }'
                }
              }
            });
            self.editorVM.editorMode(true);
            self.editorVM.isNotificationManager(true);
            ko.cleanNode($("#importerNotebook")[0]);
            ko.applyBindings(self.editorVM, $("#importerNotebook")[0]);

            self.editorVM.openNotebook(resp.history_uuid, null, true, function(){
              self.editorVM.selectedNotebook().snippets()[0].progress.subscribe(function(val){
                if (val === 100) {
                  self.indexingStarted(false);
                  self.isIndexing(false);
                  self.indexingSuccess(true);
                }
              });
              self.editorVM.selectedNotebook().snippets()[0].status.subscribe(function(val){
                if (val === 'failed') {
                  self.isIndexing(false);
                  self.indexingStarted(false);
                  self.indexingError(true);
                } else if (val === 'available') {
                  var snippet = self.editorVM.selectedNotebook().snippets()[0]; // Could be native to editor at some point
                  if (!snippet.result.handle().has_more_statements) {
                    if (self.editorVM.selectedNotebook().onSuccessUrl()) {
                      var match = snippet.statement_raw().match(/CREATE TABLE `([^`]+)`/i);
                      if (match) {
                        var db = match[1];
                        dataCatalog.getEntry({ connector: snippet.connector(), namespace: self.namespace(), compute: self.compute(), path: [ db ]}).done(function (dbEntry) {
                          dbEntry.clearCache({ silenceErrors: true }).done(function () {
                            huePubSub.publish('open.link', self.editorVM.selectedNotebook().onSuccessUrl());
                          })
                        });
                      } else {
                        dataCatalog.getEntry({ connector: snippet.connector(), namespace: self.namespace(), compute: self.compute(), path: []}).done(function (sourceEntry) {
                          sourceEntry.clearCache({ silenceErrors: true }).done(function () {
                            huePubSub.publish('open.link', self.editorVM.selectedNotebook().onSuccessUrl());
                          })
                        });
                      }
                    }
                  } else { // Perform last DROP statement execute
                    snippet.execute();
                  }
                }
              });
              self.editorVM.selectedNotebook().snippets()[0].checkStatus();
            });
          }
          viewModel.isLoading(false);
        }).fail(function (xhr, textStatus, errorThrown) {
          $(document).trigger("error", xhr.responseText);
          viewModel.isLoading(false);
          self.indexingStarted(false);
          self.isIndexing(false);
        });
% else:
        $.post("${ url('indexer:importer_submit') }", {
          "source": ko.mapping.toJSON(self.source),
          "destination": ko.mapping.toJSON(self.destination),
          "start_time": ko.mapping.toJSON((new Date()).getTime()),
          "show_command": options.show || ''
        }, function (resp) {
          self.indexingStarted(false);
          if (resp.status === 0) {
            if (resp.history_uuid) {
              $.jHueNotify.info("${ _('Task submitted') }");
              huePubSub.publish('notebook.task.submitted', resp);
            } else if (resp.on_success_url) {
              if (resp.pub_sub_url) {
                huePubSub.publish(resp.pub_sub_url);
              }
              $.jHueNotify.info("${ _('Creation success') }");
              if (resp.errors && resp.errors.length) {
                $.jHueNotify.warn("${ _('Skipped records: ') }" + resp.errors.join(', '));
              }
              huePubSub.publish('open.link', resp.on_success_url);
            } else if (resp.commands) {
              self.commands(resp.commands);
              $('#showCommandsModal').modal('show');
            }
          } else {
            $(document).trigger("error", resp && resp.message ? resp.message : '${ _("Error importing") }');
          }
        }).fail(function (xhr) {
          self.indexingStarted(false);
          $(document).trigger("error", xhr.responseText);
        });
% endif

        hueAnalytics.log('importer', 'submit/' + self.source.inputFormat() + '/' + self.destination.outputFormat());
      };

      self.removeOperation = function (operation, operationList) {
        operationList.remove(operation);
        hueAnalytics.log('importer', 'step/removeOperation');
      };

      self.addOperation = function (field) {
        field.operations.push(new Operation("split"));
        hueAnalytics.log('importer', 'step/addOperation');
      };

      self.load = function (state) {
        self.source.name(state.name);
        self.source.show(state.show);
        self.source.path(state.path);
        self.destination.columns.removeAll();
        if (state.format && 'type' in state.format) {
          var koFormat = ko.mapping.fromJS(new FileType(state.format.type, state.format));
          self.source.format(koFormat);
        }
        if (state.columns) {
          state.columns.forEach(function (currCol) {
            self.destination.columns.push(loadField(currCol));
          });
        }
      }
    };

    var loadDefaultField = function (options) {
      if (!options.name) {
        options.name = getNewFieldName();
      }
      return loadField($.extend({}, ${default_field_type | n}, options));
    };

    var loadField = function (currField, parent, idx) {
      var koField = ko.mapping.fromJS(currField);
      if (koField.name && parent) {
        koField.name.subscribe(function (newVal) {
          if (newVal.indexOf(',') > -1) {
            var fields = newVal.split(',');
            fields.forEach(function (val, i) {
              if (i + idx < parent.columns().length) {
                parent.columns()[i + idx].name(val);
              }
            });
          }
          parent.bulkColumnNames(parent.columns().map(function (item) {
            return item.name()
          }).join(','));
        });
      }

      koField.operations.removeAll();

      currField.operations.forEach(function (operationData) {
        var operation = new Operation(operationData.type);
        operation.load(operationData);

        koField.operations.push(operation);
      });

      var autoExpand = function (newVal) {
        if ((newVal === 'array' || newVal === 'map' || newVal === 'struct') && koField.nested().length === 0) {
          koField.nested.push(loadDefaultField({level: koField.level() + 1}));
        }
      };
      koField.type.subscribe(autoExpand);
      koField.keyType.subscribe(autoExpand);

      return koField;
    };

    var IndexerViewModel = function () {
      var self = this;

      self.apiHelper = window.apiHelper;
      self.sourceType = window.location.getParameter('sourceType', true) || '${ source_type }';
      self.namespaceId = window.location.getParameter('namespace', true);
      self.computeId =  window.location.getParameter('compute', true);

      self.assistAvailable = ko.observable(true);
      self.isLeftPanelVisible = ko.observable();
      self.apiHelper.withTotalStorage('assist', 'assist_panel_visible', self.isLeftPanelVisible, true);
      self.loadDefaultField = loadDefaultField;

      self.createWizard = new CreateWizard(self);

      // Wizard related
      self.wizardEnabled = ko.observable(false);
      self.currentStep = ko.observable(self.createWizard.prefill.target_type() === 'database' ? 2 : 1);
      self.currentStep.subscribe(function () {
        %if is_embeddable:
        $('.page-content').scrollTop(0);
        %else:
        $('.content-panel').scrollTop(0);
        %endif
      });
      self.previousStepVisible = ko.pureComputed(function(){
        return self.currentStep() > 1 && (self.createWizard.destination.outputFormat() !== 'database' || self.createWizard.source.inputFormat() === 'rdbms');
      });
      self.nextStepVisible = ko.pureComputed(function(){
        return self.currentStep() < 3 && self.wizardEnabled();
      });
      self.nextStep = function () {
        if (self.nextStepVisible()) {
          self.currentStep(self.currentStep() + 1);
          hueAnalytics.log('importer', 'step/' + self.currentStep());
        }
      };
      self.previousStep = function () {
        if (self.previousStepVisible()) {
          self.currentStep(self.currentStep() - 1);
          hueAnalytics.log('importer', 'step/' + self.currentStep());
        }
      };

      self.isLoading = ko.observable(false);

    };

    var viewModel;

    function resizeElements () {
      var $contentPanel = $('#importerComponents').find('.content-panel-inner');
      $('.step-indicator-fixed').width($contentPanel.width());
      document.styleSheets[0].addRule('.form-actions','margin-left: -11px !important');
      document.styleSheets[0].addRule('.step-indicator li:first-child:before','max-width: ' + ($contentPanel.find('.step-indicator li:first-child .caption').width()) + 'px');
      document.styleSheets[0].addRule('.step-indicator li:first-child:before','left: ' + ($contentPanel.find('.step-indicator li:first-child .caption').width()/2) + 'px');
      document.styleSheets[0].addRule('.step-indicator li:last-child:before','max-width: ' + ($contentPanel.find('.step-indicator li:last-child .caption').width()) + 'px');
      document.styleSheets[0].addRule('.step-indicator li:last-child:before','right: ' + ($contentPanel.find('.step-indicator li:last-child .caption').width()/2) + 'px');
    }

    $(document).ready(function () {
      viewModel = new IndexerViewModel();
      ko.applyBindings(viewModel, $('#importerComponents')[0]);


      var draggableMeta = {};
      huePubSub.subscribe('draggable.text.meta', function (meta) {
        draggableMeta = meta;
      });

      huePubSub.subscribe('importer.show.bulkeditor', function (meta) {
        $('#fieldsBulkEditor').modal('show');
      }, 'importer');

      huePubSub.subscribe('split.panel.resized', resizeElements);

      hueUtils.waitForRendered('.step-indicator li:first-child .caption', function(el){ return el.width() < $('#importerComponents').find('.content-panel-inner').width()/2 }, resizeElements);

      $(window).on('resize', resizeElements);

      $('.importer-droppable').droppable({
        accept: ".draggableText",
        drop: function (e, ui) {
          var text = ui.helper.text();
          var generatedName = 'idx';
          switch (draggableMeta.type){
            case 'sql':
              if (draggableMeta.table !== '') {
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
              if (draggableMeta.definition.type === 'query-hive') {
                generatedName += draggableMeta.definition.name;
                viewModel.createWizard.source.inputFormat('query');
                viewModel.createWizard.source.draggedQuery(draggableMeta.definition.uuid);
              }
              break;
          }
          if (generatedName !== 'idx' && viewModel.createWizard.source.name() === '') {
            viewModel.createWizard.source.name(generatedName);
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

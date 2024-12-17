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
  import sys
  import json
  from desktop import conf
  from desktop.views import commonheader, commonfooter, commonshare, commonimportexport, _ko
  from filebrowser.conf import SHOW_UPLOAD_BUTTON
  from beeswax import hive_site
  from impala import impala_flags
  from notebook.conf import ENABLE_SQL_INDEXER

  from indexer.conf import ENABLE_NEW_INDEXER, ENABLE_SQOOP, ENABLE_KAFKA, CONFIG_INDEXER_LIBS_PATH, ENABLE_SCALABLE_INDEXER, ENABLE_ALTUS, ENABLE_ENVELOPE, ENABLE_FIELD_EDITOR, ENABLE_DIRECT_UPLOAD

  if sys.version_info[0] > 2:
    from django.utils.translation import gettext as _
  else:
    from django.utils.translation import ugettext as _
%>

<%namespace name="actionbar" file="actionbar.mako" />

% if not is_embeddable:
${ commonheader(_("Importer"), "indexer", user, request, "60px") | n,unicode }

<link rel="stylesheet" href="${ static('notebook/css/notebook.css') }">
<link rel="stylesheet" href="${ static('notebook/css/notebook-layout.css') }">
% endif

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

% if not is_embeddable:
<a title="${_('Toggle Assist')}" class="pointer show-assist" data-bind="visible: !$root.isLeftPanelVisible() && $root.assistAvailable(), click: function() { $root.isLeftPanelVisible(true); }">
  <i class="fa fa-chevron-right"></i>
</a>
% endif

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
          <div class="control-group" data-bind="visible: ((createWizard.prefill.target_type().length == 0 || createWizard.prefill.source_type() == 'all') && createWizard.source.inputFormats().length > 1)">
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
                <i data-hue-analytics="importer:preview-path-btn-click" class="fa fa-fw fa-info"></i>
              </a>
            <!-- /ko -->
          </div>

          <div data-bind="visible: createWizard.source.inputFormat() == 'localfile'">
              <form method="post" action="" enctype="multipart/form-data" id="uploadform">
                <div >
                    <input type="file" id="inputfile" name="inputfile" style="margin-left: 130px" accept=".csv, .xlsx, .xls">
                </div>
            </form>
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
            ## <div class="control-group">
            ##  <label class="control-label"><div>${ _('List') }</div>
            ##    <select data-bind="selectize: createWizard.source.publicStreams, value: createWizard.source.streamSelection, optionsText: 'name', optionsValue: 'value'" placeholder="${ _('The list of streams to consume, e.g. SFDC, Jiras...') }"></select>
            ##  </label>
            ## s</div>

            <!-- ko if: createWizard.source.streamSelection() == 'kafka' -->
              <div data-bind="template: { name: 'kafka-cluster-template', data: $data }" class="margin-top-10 field inline-block"></div>

              <br>

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
                  <input type="text" class="input-xlarge" data-bind="hiveChooser: name, skipInvalids:true, pathChangeLevel: 'table', skipColumns: true, apiHelperUser: '${ user }', namespace: $root.createWizard.source.namespace, compute: $root.createWizard.source.compute, apiHelperType: $root.createWizard.source.sourceType(), mainScrollable: $(MAIN_SCROLLABLE)" placeholder="${ _('Table name or <database>.<table>') }">
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
    <div class="card step" data-bind="visible: createWizard.source.inputFormat() == 'file' || createWizard.source.inputFormat() == 'localfile' || createWizard.source.inputFormat() == 'stream'">
      <!-- ko if: createWizard.isGuessingFormat -->
      <h4>${_('Guessing format...')} <i class="fa fa-spinner fa-spin"></i></h4>
      <!-- /ko -->
      <!-- ko ifnot: createWizard.isGuessingFormat -->
      <h4>${_('Format')}</h4>
      <div class="card-body">
        <label data-bind="visible: (createWizard.prefill.source_type().length > 0 && createWizard.prefill.target_type().length > 0) || ((createWizard.prefill.source_type().length == 0 || createWizard.prefill.target_type() == 'index') &&
            (createWizard.source.inputFormat() == 'file' || createWizard.source.inputFormat() == 'localfile' || createWizard.source.inputFormat() == 'stream'))">
          <div>${_('File Type')}</div>
          <select data-bind="selectize: $root.createWizard.fileTypes, value: $root.createWizard.fileTypeName,
              optionsText: 'description', optionsValue: 'name'"></select>
        </label>
        <span class="inline-labels" data-bind="with: createWizard.source.format, visible: createWizard.source.show">
          <span data-bind="foreach: getArguments()">
            <!-- ko template: { name: 'arg-' + $data.type, data: {description: $data.description, value: $parent[$data.name]} }-->
            <!-- /ko -->
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
            <label for="destinationType" class="control-label" data-bind="visible: $parent.createWizard.prefill.target_type().length == 0 && outputFormats().length > 1"><div>${ _('Type') }</div>
              <select id="destinationType" data-bind="selectize: outputFormats, value: outputFormat, optionsValue: 'value', optionsText: 'name'"></select>
            </label>
          </div>

          <div class="control-group">
            <!-- ko if: outputFormat() == 'file' -->
            <label for="collectionName" class="control-label "><div>${ _('Name') }</div></label>
            <input type="text" class="form-control name input-xxlarge" id="collectionName" data-bind="value: name, filechooser: name, filechooserOptions: { linkMarkup: true, skipInitialPathIfEmpty: true, openOnFocus: true, selectFolder: true, displayOnlyFolders: true, uploadFile: false}" placeholder="${ _('Name') }" title="${ _('Directory must not exist in the path') }">
            <!-- /ko -->

            <!-- ko if: ['index', 'big-table', 'stream-table'].indexOf(outputFormat()) != -1 -->
            <label for="collectionName" class="control-label "><div>${ _('Name') }</div></label>
            <input type="text" class="form-control input-xlarge" id="collectionName" data-bind="value: name, valueUpdate: 'afterkeydown'" placeholder="${ _('Name') }">
            <!-- /ko -->

            <!-- ko if: ['table', 'database'].indexOf(outputFormat()) != -1 -->
            <div data-bind="visible: $parent.createWizard.source.inputFormat() == 'localfile'">
              <label for="dialectType" class="control-label "><div>${ _('Dialect') }</div>
                <select  id="dialectType" data-bind="selectize: $parent.createWizard.source.interpreters, value: $parent.createWizard.source.interpreter, optionsText: 'name', optionsValue: 'type'"></select>
              </label>
            </div>
            <label for="collectionName" class="control-label "><div>${ _('Name') }</div></label>
            <input type="text" class="input-xxlarge" data-bind="value: name, hiveChooser: name, namespace: namespace, compute: compute, skipColumns: true, skipTables: outputFormat() == 'database', valueUpdate: 'afterkeydown', apiHelperUser: '${ user }', apiHelperType: sourceType(), mainScrollable: $(MAIN_SCROLLABLE), attr: { 'placeholder': outputFormat() == 'table' ? '${  _ko('Table name or <database>.<table>') }' : '${  _ko('Database name') }' }" pattern="^([a-zA-Z0-9_]+\.)?[a-zA-Z0-9_]*$" title="${ _('Only alphanumeric and underscore characters') }">
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
              <a href="javascript:void(0);" data-bind="sqlContextPopover: { sourceType: $root.createWizard.source.sourceType(), namespace: namespace, compute: compute, path: 'default', offset: { top: -3, left: 3 }}">
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

          <!-- ko if: namespace().computes.length > 1 || window.getLastKnownConfig().has_computes -->
          <div class="control-group">
            <label for="computeName" class="control-label"><div>${ _('Compute') }</div>
              <select id="computeName" data-bind="selectize: namespace().computes, value: $parent.createWizard.source.selectedComputeId, optionsValue: 'name', optionsText: 'name'" placeHolder="Select Compute"></select>
            </label>
            <!-- ko if: !$parent.createWizard.source.selectedComputeId() -->
              <span class="help-inline muted">
                <i class="fa fa-warning" style="color: #c09853"></i>
                  ${ _('Empty compute') }
              </span>
            <!-- /ko -->
          </div>
          <!-- /ko -->
        </div>
      </div>


        <!-- ko if: ['table'].indexOf(outputFormat()) != -1 && $root.createWizard.source.inputFormat() != 'rdbms' -->
        <div class="card step">
          <h4>${_('Properties')}</h4>
          <div class="card-body">
            <div class="control-group">
              <label for="destinationFormat" class="control-label"><div>${ _('Format') }</div>
                ## we need only few options when isIceberg is selected and looks like ko.selectize.custom.js has some issue so adding this workaround
                <!-- ko if: !isIceberg() -->
                <select id="destinationFormat" data-bind="selectize: tableFormats, value: tableFormat, optionsValue: 'value', optionsText: 'name'"></select>
                <!-- /ko -->
                <!-- ko if: isIceberg() && $root.createWizard.source.sourceType() === 'hive' -->
                <select id="destinationFormat" data-bind="selectize: [{value: 'parquet', name: 'Parquet'}, {'value': 'avro', 'name': 'Avro'}, {'value': 'orc', 'name': 'ORC'}], value: tableFormat, optionsValue: 'value', optionsText: 'name'"></select>
                <!-- /ko -->
                <!-- ko if: isIceberg() && $root.createWizard.source.sourceType() === 'impala' -->
                <select id="destinationFormat" data-bind="selectize: [{value: 'parquet', name: 'Parquet'}], value: tableFormat, optionsValue: 'value', optionsText: 'name'"></select>
                <!-- /ko -->
              </label>
            </div>

            <div class="control-group">
              <label class="control-label"><div>${ _('Extras') }</div>
                <a href="javascript:void(0)" data-bind="css: { 'inactive-action': !showProperties() }, toggle: showProperties" title="${ _('Show extra properties') }">
                  <i data-hue-analytics="importer:show-extras-btn-click" class="fa fa-sliders fa-padding-top"></i>
                </a>
              </label>
            </div>

            <span data-bind="visible: showProperties">
              <div class="control-group">
                <label class="checkbox inline-block" data-bind="visible: tableFormat() != 'kudu'">
                  <input data-hue-analytics="importer:store-in-default-localtion-checkbox-interaction" type="checkbox" data-bind="checked: useDefaultLocation, disable: isIceberg() || useCopy()"> ${_('Store in Default location')}
                </label>
              </div>
              <div class="control-group" data-bind="visible: isTransactionalVisible">
                <label class="checkbox inline-block">
                  <input type="checkbox" data-hue-analytics="importer:is-transactional-checkbox-interaction" data-bind="checked: isTransactional, disable: isIceberg() || useCopy()"> ${_('Transactional table')}
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
                  <input data-hue-analytics="importer:import-data-checkbox-interaction" type="checkbox" data-bind="checked: importData, disable: !useDefaultLocation() && $parent.createWizard.source.path() == nonDefaultLocation();"> ${_('Import data')}
                </label>
              </div>

              <div class="control-group" data-bind="visible: icebergEnabled && $root.createWizard.source.inputFormat() === 'file'">
                <label class="checkbox inline-block">
                  <input data-hue-analytics="importer:is-iceberg-checkbox-interaction" type="checkbox" data-bind="checked: isIceberg"> ${_('Iceberg table')}
                </label>
              </div>

              <div class="control-group" data-bind="visible: !useDefaultLocation() && !isTransactional() && $root.createWizard.source.inputFormat() === 'file'">
                <label class="checkbox inline-block">
                  <input data-hue-analytics="importer:useCopy-checkbox-interaction" type="checkbox" data-bind="checked: useCopy"> ${_('Copy file')}
                </label>
                <a href="javascript:void(0)" style="display: inline" data-trigger="hover" data-toggle="popover" data-placement="right" rel="popover" title="${ _('Choosing this option will copy the file instead of moving it to the new location, and ensuring the original file remains unchanged.') }">
                  <i class="fa fa-info-circle"></i>
                </a>
              </div>

              <div class="control-group">
                <label><div>${ _('Description') }</div>
                    <input type="text" class="form-control input-xxlarge" data-bind="value: description, valueUpdate: 'afterkeydown'" placeholder="${ _('Description') }">
                </label>
              </div>
              <div class="control-group" data-bind="visible: $root.createWizard.source.inputFormat() == 'file'">
                <label class="checkbox inline-block">
                  <input data-hue-analytics="importer:use-first-row-as-header-interaction" type="checkbox" data-bind="checked: hasHeader"> ${_('Use first row as header')}
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

            <div class="control-group" data-bind="visible: (tableFormat() == 'kudu' || $root.createWizard.destination.dialect() == 'phoenix')">
              <label for="kuduPksTable" class="control-label"><div>${ _('Primary keys') }</div>
                ## At least one selected
                <select id="kuduPksTable" data-bind="selectize: columns, selectedOptions: primaryKeys, selectedObjects: primaryKeyObjects, optionsValue: 'name', optionsText: 'name', innerSubscriber: 'name'" size="3" multiple="true"></select>
              </label>
            </div>

            <label class="control-label"><div>${ _('Partitions') }</div>
              <!-- ko if: tableFormat() != 'kudu' && $root.createWizard.source.inputFormat() != 'rdbms' -->
              <div class="inline-table">
                <div class="form-inline" data-bind="foreach: partitionColumns">
                  <a class="pointer pull-right margin-top-20" data-bind="click: function() { 
                    $parent.partitionColumns.remove($data);
                    window.hueAnalytics.log('importer', 'remove-partiction-btn-click');
                  }"><i class="fa fa-minus"></i></a>
                  <div data-bind="template: { name: 'table-field-template', data: $data }" class="margin-top-10 field inline-block"></div>
                  <div class="clearfix"></div>
                </div>
                <a data-hue-analytics="importer:add-partiction-btn-click" data-bind="click: function() { partitionColumns.push($root.loadDefaultField({isPartition: true})); }" class="pointer" title="${_('Add Partition')}"><i class="fa fa-plus fa-padding-top"></i> ${_('Add partition')}</a>
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

        <!-- ko if: ['index', 'big-table'].indexOf(outputFormat()) != -1 -->
        <div class="card step">
          <h4>${_('Properties')}</h4>
          <div class="card-body">
            % if ENABLE_SCALABLE_INDEXER.get():
            <div class="control-group">
              <label class="checkbox inline-block" title="${ _('Execute a cluster job to index a large dataset.') }" data-bind="visible: (['file', 'localfile'].indexOf($root.createWizard.source.inputFormat()) != -1)">
                <input type="checkbox" data-bind="checked: indexerRunJob">
                  <!-- ko if: outputFormat() == 'index' -->
                    ${_('Index with a job')}
                  <!-- /ko -->
                  <!-- ko if: outputFormat() == 'big-table' -->
                    ${_('Load data')}
                  <!-- /ko -->
              </label>

              <!-- ko if: outputFormat() == 'index' -->
              <label for="path" class="control-label" data-bind="visible: indexerRunJob"><div>${ _('Libs') }</div>
                <input type="text" class="form-control path filechooser-input input-xlarge" data-bind="value: indexerJobLibPath, filechooser: indexerJobLibPath, filechooserOptions: { linkMarkup: true, skipInitialPathIfEmpty: true }, valueUpdate: 'afterkeydown'">
              </label>
              <!-- ko if: indexerRunJob() && indexerJobLibPath().length > 0 -->
                <a data-bind="hueLink: '/filebrowser/view=' + indexerJobLibPath()" title="${ _('Open') }" style="font-size: 14px" class="margin-left-10">
                  <i class="fa fa-external-link-square"></i>
                </a>
              <!-- /ko -->
              <!-- /ko -->
            </div>
            % endif

            <div class="control-group">
              <label for="kuduPksIndex" class="control-label"><div>${ _('Primary key') }</div>
                <select id="kuduPksIndex" data-bind="selectize: columns, selectedOptions: indexerPrimaryKey, selectedObjects: indexerPrimaryKeyObject, optionsValue: 'name', optionsText: 'name', innerSubscriber: 'name'" size="1" multiple="false"></select>
              </label>
            </div>

            <!-- ko if: ['index'].indexOf(outputFormat()) != -1 -->
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
            <!-- /ko -->
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

        <!-- ko if: ['table', 'index', 'hbase', 'big-table', 'stream-table'].indexOf(outputFormat()) != -1 -->
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
                  <i data-hue-analytics="importer:bulk-field-editor-show" class="fa fa-edit"></i>
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
                  autocomplete: { type: sourceType() },
                  lines: 5,
                  aceOptions: {
                    minLines: 10,
                    maxLines: 25
                  },
                  database: fieldEditorDatabase,
                  namespace: namespace,
                  compute: compute,
                  temporaryOnly: true,
                  mode: sourceType()
                }}"></div>
              <!-- /ko -->

              <!-- ko ifnot: useFieldEditor -->
              <!-- ko if: $root.createWizard.source.inputFormat() === 'manual' -->

                <form class="form-inline inline-table" data-bind="foreach: columns">
                  <!-- ko if: $parent.outputFormat() === 'table' -->
                    <a class="pointer pull-right margin-top-20" data-bind="click: function() { $parent.columns.remove($data); }">
                      <i class="fa fa-minus"></i>
                    </a>
                    <div data-bind="template: { name: 'table-field-template', data: $data }" class="margin-top-10 field inline-block"></div>
                    <div class="clearfix"></div>
                  <!-- /ko -->

                  <!-- ko if: $parent.outputFormat() == 'index' -->
                    <a class="pointer pull-right margin-top-20" data-bind="click: function() { $parent.columns.remove($data); }">
                      <i class="fa fa-minus"></i>
                    </a>
                    <div data-bind="template: { name: 'index-field-template', data: $data }, css: { 'disabled': !keep() }" class="margin-top-10 field inline-block index-field"></div>
                    <div class="clearfix"></div>
                  <!-- /ko -->
                </form>

                <div class="clearfix"></div>

                <!-- ko if: outputFormat() == 'table' || outputFormat() == 'index' -->
                  <a data-bind="click: function() { columns.push($root.loadDefaultField({})); }" class="pointer" title="${_('Add Field')}">
                  <i class="fa fa-plus"></i> ${_('Add Field')}</a>
                <!-- /ko -->
              <!-- /ko -->

              <!-- ko if: $root.createWizard.source.inputFormat() !== 'manual' -->
              <form class="form-inline inline-table" data-bind="foreachVisible: { data: columns, minHeight: 54, container: MAIN_SCROLLABLE }">
                <!-- ko if: ['table', 'big-table', 'stream-table'].indexOf($parent.outputFormat()) != -1 && $root.createWizard.source.inputFormat() != 'rdbms' -->
                  <div data-bind="template: { name: 'table-field-template', data: $data }" class="margin-top-10 field"></div>
                <!-- /ko -->

                <!-- ko if: ['index'].indexOf($parent.outputFormat()) != -1 || (['file', 'table', 'hbase'].indexOf($parent.outputFormat()) != -1 && $root.createWizard.source.inputFormat() == 'rdbms') -->
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
      <button class="btn" data-bind="enable: !createWizard.isGuessingFormat() && createWizard.source.show(), click: function() { 
        currentStep(2);
        window.hueAnalytics.log('importer', 'next-btn-click/' +  createWizard?.source?.inputFormat());
        }">
        ${_('Next')}
      </button>
      <!-- /ko -->

      <!-- ko if: currentStep() == 2 -->
        <button data-hue-analytics="importer:submit-btn-click" class="btn btn-primary disable-feedback" data-bind="click: function() { createWizard.indexFile(); }, enable: createWizard.readyToIndex() && !createWizard.indexingStarted()">
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
      <button data-hue-analytics="importer:bulk-field-editor-cancel" class="btn" data-dismiss="modal" aria-hidden="true">${ _('Cancel') }</button>
      <button data-hue-analytics="importer:bulk-field-editor-change" class="btn btn-primary" data-bind="click: createWizard.destination.processBulkColumnNames">${ _('Change field names') }</button>
    </div>
  </div>

</script>


<script type="text/html" id="table-field-template">
  <div>
    <label data-bind="visible: level() == 0 || ($parent.type() != 'array' && $parent.type() != 'map')">${ _('Name') }&nbsp;
      <input data-hue-analytics="importer:field-name-click" type="text" class="input-large" placeholder="${ _('Field name') }" required data-bind="textInput: name" pattern="^[a-zA-Z0-9_]+$" title="${ _('Only alphanumeric and underscore characters') }">
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
      <a href="javascript:void(0)" title="${ _('Show field properties') }" data-bind="css: {'inactive-action': !showProperties()}, click: function() {showProperties(!showProperties()) }"><i data-hue-analytics="importer:toggle-field-properties" class="fa fa-sliders"></i></a>

      <span data-bind="visible: showProperties">
        <input type="text" class="input-medium margin-left-5" placeholder="${ _('Field comment') }" data-bind="value: comment">
        <label class="checkbox" data-bind="visible: $root.createWizard.destination.tableFormat() == 'kudu' || $root.createWizard.source.inputFormat() == 'localfile'">
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

<script type="text/html" id="kafka-cluster-template">
  <div class="control-group">
    <label class="control-label"><div>${ _('Clusters') }</div>
      <select class="input-xxlarge" data-bind="options: createWizard.source.kafkaClusters,
            value: createWizard.source.kafkaSelectedCluster,
            optionsCaption: '${ _("Choose...") }'"
            placeholder="${ _('The list of Kafka cluster to consume topics from') }">
      </select>

    </label>

    <br/>

    ## <label class="control-group" data-bind="visible: createWizard.source.kafkaSelectedCluster">
    ##  <label class="control-label"><div>${ _('Username') }</div>
    ##    <input type="text" class="input-small" data-bind="value: createWizard.source.kafkaSelectedClusterUsername">
    ##  </label>
    ##  <label class="control-label"><div>${ _('Password') }</div>
    ##    <input type="text" class="input-small" data-bind="value: createWizard.source.kafkaSelectedClusterPassword">
    ##  </label>
  </div>
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
        <label class="radio">
          <input type="radio" name="kafkaSchemaManual" value="detect" data-bind="checked: createWizard.source.kafkaSchemaManual" />
          ${_('Guess')}
        </label>
        <label class="radio margin-right-10">
          <input type="radio" name="kafkaSchemaManual" value="manual" data-bind="checked: createWizard.source.kafkaSchemaManual" />
          ${_('Manual')}
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
        <input type="text" class="input-xxlarge" data-bind="value: createWizard.source.kafkaFieldNames"
          placeholder="${ _('The list of fields to consume, e.g. orders,returns') }">
      </label>
      <br/>
      <label class="control-label"><div>${ _('Field types') }</div>
        <input type="text" class="input-xxlarge"
          data-bind="value: createWizard.source.kafkaFieldTypes" placeholder="${ _('The list of field typs, e.g. string,int') }">
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

<script type="application/json" id="importerOptionsJson">
  ${ options_json | n,unicode }
</script>

<script src="${ static('desktop/js/importer-inline.js') }" type="text/javascript"></script>
</span>

%if not is_embeddable:
${ commonfooter(request, messages) | n,unicode }
%endif

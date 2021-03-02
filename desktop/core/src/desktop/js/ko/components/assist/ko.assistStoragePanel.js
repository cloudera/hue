// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import * as ko from 'knockout';

import AssistStorageEntry from './assistStorageEntry';
import apiHelper from 'api/apiHelper';
import componentUtils from 'ko/components/componentUtils';
import { getRootFilePath } from 'config/hueConfig';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';
import { getFromLocalStorage, setInLocalStorage } from 'utils/storageUtils';

// prettier-ignore
const TEMPLATE = `
  <script type="text/html" id="storage-context-items">
    <li><a href="javascript:void(0);" data-bind="click: function (data) { showContextPopover(data, { target: $parentContext.$contextSourceElement }, { left: -15, top: 2 }); }"><i class="fa fa-fw fa-info"></i> ${I18n(
      'Show details'
    )}</a></li>
    <li><a href="javascript:void(0);" data-bind="hueLink: definition.url"><i class="fa fa-fw" data-bind="css: {'fa-folder-open-o': definition.type === 'dir', 'fa-file-text-o': definition.type === 'file'}"></i> ${I18n(
      'Open in Browser'
    )}</a></li>
    <!-- ko if: definition.type === 'file' -->
    <li><a href="javascript:void(0);" data-bind="click: openInImporter"><!-- ko template: { name: 'app-icon-template', data: { icon: 'importer' } } --><!-- /ko --> ${I18n(
      'Open in Importer'
    )}</a></li>
    <!-- /ko -->
    <!-- ko if: $currentApp() === 'editor' -->
    <li><a href="javascript:void(0);" data-bind="click: dblClick"><i class="fa fa-fw fa-paste"></i> ${I18n(
      'Insert at cursor'
    )}</a></li>
    <!-- /ko -->
  </script>

  <script type="text/html" id="assist-storage-header-actions">
    <div class="assist-db-header-actions">
      <!-- ko if: source.type !== 's3' && source.type !== 'abfs' -->
      <a class="inactive-action" href="javascript:void(0)" data-bind="click: goHome, attr: { title: I18n('Go to ' + window.USER_HOME_DIR) }"><i class="pointer fa fa-home"></i></a>
      <!-- ko if: window.SHOW_UPLOAD_BUTTON -->
      <a class="inactive-action" data-bind="dropzone: {
            url: '/filebrowser/upload/file?dest=' + (source.type === 'adls' ? 'adl:' : '') + path,
            params: { dest: path },
            paramName: 'hdfs_file',
            onError: function(x, e){ $(document).trigger('error', e); },
            onComplete: function () { huePubSub.publish('assist.storage.refresh'); } }" title="${I18n(
              'Upload file'
            )}" href="javascript:void(0)">
        <div class="dz-message inline" data-dz-message><i class="pointer fa fa-plus" title="${I18n(
          'Upload file'
        )}"></i></div>
      </a>
      <!-- /ko -->
      <!-- /ko -->
      <!-- ko if: source.type === 'abfs' && path !== '/' && window.SHOW_UPLOAD_BUTTON -->
      <a class="inactive-action" data-bind="dropzone: {
            url: '/filebrowser/upload/file?dest=' + abfsPath,
            params: { dest: abfsPath },
            paramName: 'hdfs_file',
            onError: function(x, e){ $(document).trigger('error', e); },
            onComplete: function () { huePubSub.publish('assist.storage.refresh'); } }" title="${I18n(
              'Upload file'
            )}" href="javascript:void(0)">
        <div class="dz-message inline" data-dz-message><i class="pointer fa fa-plus" title="${I18n(
          'Upload file'
        )}"></i></div>
      </a>
      <!-- /ko -->
      <a class="inactive-action" href="javascript:void(0)" data-bind="click: function () { huePubSub.publish('assist.storage.refresh'); }" title="${I18n(
        'Manual refresh'
      )}"><i class="pointer fa fa-refresh" data-bind="css: { 'fa-spin blue' : loading }"></i></a>
    </div>
  </script>

  <!-- ko hueSpinner: { spin: loading, center: true, size: 'large' } --><!-- /ko -->

  <!-- ko ifnot: activeSource -->
  <div class="assist-flex-header">
    <div class="assist-inner-header">
      ${I18n('Sources')}
    </div>
  </div>
  <div class="assist-flex-fill">
    <ul class="assist-tables" data-bind="foreach: sources">
      <li class="assist-table">
        <a class="assist-table-link" href="javascript: void(0);" data-bind="click: function () { $parent.activeSource($data); }"><i class="fa fa-fw fa-server muted valign-middle"></i> <span data-bind="text: $data.displayName"></span></a>
      </li>
    </ul>
  </div>
  <!-- /ko -->

  <!-- ko if: activeSource -->
  <!-- ko with: selectedStorageEntry -->
  <div class="assist-flex-header assist-breadcrumb" >
    <!-- ko if: parent !== null -->
    <a href="javascript: void(0);" data-bind="appAwareTemplateContextMenu: {
      template: 'storage-context-items',
      scrollContainer: '.assist-files-scrollable'
    }, click: function () {
      huePubSub.publish('assist.selectStorageEntry', parent);
    }">
      <i class="fa fa-fw fa-chevron-left"></i>
      <i class="fa fa-fw fa-folder-o"></i>
      <span data-bind="text: definition.name, tooltip: {'title': path, 'placement': 'top' }"></span>
    </a>
    <!-- /ko -->
    <!-- ko if: parent === null -->
    <a href="javascript: void(0);" data-bind="click: function () { $parent.activeSource(undefined) }">
      <i class="fa fa-fw fa-chevron-left"></i>
      <i class="fa fa-fw fa-server"></i>
      <span data-bind="text: $parent.activeSource().displayName"></span>
    </a>
    <!-- /ko -->
    <!-- ko template: 'assist-storage-header-actions' --><!-- /ko -->
  </div>
  <div class="assist-flex-search">
    <div class="assist-filter">
      <form autocomplete="off">
        <input class="clearable" type="text" placeholder="${I18n(
          'Filter...'
        )}" ${ window.PREVENT_AUTOFILL_INPUT_ATTRS }
        data-bind="clearable: filter, value: filter, valueUpdate: 'afterkeydown'"/>
      </form>
    </div>
  </div>

  <div class="assist-flex-fill assist-storage-scrollable" data-bind="delayedOverflow">
    <div data-bind="visible: ! loading() && ! hasErrors()" style="position: relative;">
      <!-- ko hueSpinner: { spin: loadingMore, overlay: true } --><!-- /ko -->
      <ul class="assist-tables" data-bind="foreachVisible: { data: entries, minHeight: 22, container: '.assist-storage-scrollable', fetchMore: $data.fetchMore.bind($data) }">
        <li class="assist-entry assist-table-link" style="position: relative;" data-bind="appAwareTemplateContextMenu: { template: 'storage-context-items', scrollContainer: '.assist-storage-scrollable' }, visibleOnHover: { override: contextPopoverVisible, 'selector': '.assist-actions' }">
          <div class="assist-actions table-actions" style="opacity: 0;" >
            <a style="padding: 0 3px;" class="inactive-action" href="javascript:void(0);" data-bind="popoverOnHover: showContextPopover, css: { 'blue': contextPopoverVisible }">
              <i class='fa fa-info' title="${I18n('Details')}"></i>
            </a>
          </div>

          <a href="javascript:void(0)" class="assist-entry assist-table-link" data-bind="multiClick: { click: toggleOpen, dblClick: dblClick }, attr: {'title': definition.name }">
            <!-- ko if: definition.type === 'dir' -->
            <i class="fa fa-fw fa-folder-o muted valign-middle"></i>
            <!-- /ko -->
            <!-- ko if: definition.type === 'file' -->
            <i class="fa fa-fw fa-file-o muted valign-middle"></i>
            <!-- /ko -->
            <span draggable="true" data-bind="text: definition.name, draggableText: { text: '\\'' + path + '\\'', meta: {'type': source.type, 'definition': definition} }"></span>
          </a>
        </li>
      </ul>
      <!-- ko if: !loading() && entries().length === 0 -->
      <ul class="assist-tables">
        <li class="assist-entry"><span class="assist-no-entries"><!-- ko if: filter() -->${I18n(
          'No results found'
        )}<!-- /ko --><!-- ko ifnot: filter() -->${I18n('Empty directory')}<!-- /ko --></span></li>
      </ul>
      <!-- /ko -->
    </div>
    <!-- ko hueSpinner: { spin: loading, center: true, size: 'large' } --><!-- /ko -->
    <span class="assist-errors" data-bind="visible: ! loading() && hasErrors(), text: errorText() || '${I18n(
      'Error loading contents.'
    )}'">
    </span>
  </div>
  <!-- /ko -->
  <!-- /ko -->
`;

class AssistStoragePanel {
  /**
   * @param {Object} options
   * @param {Interpreter[]} options.sources
   * @constructor
   **/
  constructor(options) {
    this.sources = ko.observableArray(options.sources);

    const lastSourceType = getFromLocalStorage('assist.lastStorageSource', 'hdfs');

    let foundLastSource = this.sources().find(source => source.type === lastSourceType);

    if (!foundLastSource && this.sources().length) {
      foundLastSource = this.sources().find(source => source.type === 'hdfs') || this.sources()[0];
    }

    this.activeSource = ko.observable(foundLastSource);
    this.loading = ko.observable();
    this.initialized = false;
    this.rootPath = getRootFilePath(this.activeSource());

    this.selectedStorageEntry = ko.observable();

    this.activeSource.subscribe(newValue => {
      if (newValue) {
        this.rootPath = getRootFilePath(this.activeSource());
        setInLocalStorage('assist.lastStorageSource', newValue.type);
        this.selectedStorageEntry(undefined);
        this.reload();
      }
    });

    huePubSub.subscribe('assist.selectStorageEntry', entry => {
      this.selectedStorageEntry(entry);
      setInLocalStorage('assist.currentStoragePath_' + entry.source.type, entry.path);
    });

    huePubSub.subscribe('assist.storage.refresh', () => {
      apiHelper.clearStorageCache(this.activeSource().type);
      this.reload();
    });

    huePubSub.subscribe('assist.storage.go.home', () => {
      const path =
        this.activeSource().type === 's3' || this.activeSource().type === 'abfs'
          ? '/'
          : window.USER_HOME_DIR;
      this.loadPath(path);
      setInLocalStorage('assist.currentStoragePath_' + this.activeSource().type, path);
    });

    this.init();
  }

  loadPath(path) {
    this.loading(true);
    let relativePath = path;
    if (this.rootPath) {
      relativePath = relativePath.replace(this.rootPath, '/');
    }
    const parts = relativePath.split('/');
    parts.shift();

    const currentEntry = new AssistStorageEntry({
      source: this.activeSource(),
      rootPath: this.rootPath,
      definition: {
        name: this.rootPath,
        type: 'dir'
      },
      parent: null
    });

    currentEntry.loadDeep(parts, entry => {
      this.selectedStorageEntry(entry);
      entry.open(true);
      this.loading(false);
    });
  }

  reload() {
    this.loadPath(
      getFromLocalStorage(
        'assist.currentStoragePath_' + this.activeSource().type,
        this.activeSource().type === 'hdfs' ? window.USER_HOME_DIR : '/'
      )
    );
  }

  init() {
    if (this.initialized) {
      return;
    }
    this.reload();
    this.initialized = true;
  }
}

componentUtils.registerStaticComponent('hue-assist-storage-panel', AssistStoragePanel, TEMPLATE);

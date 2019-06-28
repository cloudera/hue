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

import ko from 'knockout';

import apiHelper from 'api/apiHelper';
import AssistStorageEntry from 'ko/components/assist/assistStorageEntry';
import componentUtils from 'ko/components/componentUtils';
import HDFS_CONTEXT_ITEMS_TEMPLATE from 'ko/components/assist/ko.assistHdfsPanel';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';

const TEMPLATE =
  HDFS_CONTEXT_ITEMS_TEMPLATE +
  `
  <script type="text/html" id="assist-s3-header-actions">
    <div class="assist-db-header-actions">
      <a class="inactive-action" href="javascript:void(0)" data-bind="click: function () { huePubSub.publish('assist.s3.refresh'); }"><i class="pointer fa fa-refresh" data-bind="css: { 'fa-spin blue' : loading }" title="${I18n(
        'Manual refresh'
      )}"></i></a>
    </div>
  </script>

  <!-- ko hueSpinner: { spin: loading, center: true, size: 'large' } --><!-- /ko -->
  <!-- ko with: selectedS3Entry -->
  <div class="assist-flex-header assist-breadcrumb" >
    <!-- ko if: parent !== null -->
    <a href="javascript: void(0);" data-bind="appAwareTemplateContextMenu: { template: 'hdfs-context-items', scrollContainer: '.assist-s3-scrollable' }, click: function () { huePubSub.publish('assist.selectS3Entry', parent); }">
      <i class="fa fa-fw fa-chevron-left"></i>
      <i class="fa fa-fw fa-folder-o"></i>
      <span data-bind="text: definition.name, tooltip: {'title': path, 'placement': 'top' }"></span>
    </a>
    <!-- /ko -->
    <!-- ko if: parent === null -->
    <div>
      <i class="fa fa-fw fa-folder-o"></i>
      <span data-bind="text: path"></span>
    </div>
    <!-- /ko -->
    <!-- ko template: 'assist-s3-header-actions' --><!-- /ko -->
  </div>
  <div class="assist-flex-search">
    <div class="assist-filter"><input class="clearable" type="text" placeholder="${I18n(
      'Filter...'
    )}" data-bind="clearable: filter, value: filter, valueUpdate: 'afterkeydown'"/></div>
  </div>
  <div class="assist-flex-fill assist-s3-scrollable" data-bind="delayedOverflow">
    <div data-bind="visible: ! loading() && ! hasErrors()" style="position: relative;">
      <!-- ko hueSpinner: { spin: loadingMore, overlay: true } --><!-- /ko -->
      <ul class="assist-tables" data-bind="foreachVisible: { data: entries, minHeight: 22, container: '.assist-s3-scrollable', fetchMore: $data.fetchMore.bind($data) }">
        <li class="assist-entry assist-table-link" style="position: relative;" data-bind="appAwareTemplateContextMenu: { template: 'hdfs-context-items', scrollContainer: '.assist-s3-scrollable' }, visibleOnHover: { override: contextPopoverVisible, 'selector': '.assist-actions' }">
          <div class="assist-actions table-actions" style="opacity: 0;" >
            <a style="padding: 0 3px;" class="inactive-action" href="javascript:void(0);" data-bind="click: showContextPopover, css: { 'blue': contextPopoverVisible }">
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
            <span draggable="true" data-bind="text: definition.name, draggableText: { text: '\\\\'' + path + '\\\\'', meta: {'type': 's3', 'definition': definition} }"></span>
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
    <div class="assist-errors" data-bind="visible: ! loading() && hasErrors()">
      <span>${I18n('Error loading contents.')}</span>
    </div>
  </div>
  <!-- /ko -->
`;

class AssistS3Panel {
  /**
   * @param {Object} options
   * @constructor
   **/
  constructor(options) {
    const self = this;

    self.selectedS3Entry = ko.observable();
    self.loading = ko.observable();
    self.initialized = false;

    self.reload = () => {
      self.loading(true);
      const lastKnownPath = apiHelper.getFromTotalStorage('assist', 'currentS3Path', '/');
      const parts = lastKnownPath.split('/');
      parts.shift();

      const currentEntry = new AssistStorageEntry({
        type: 's3',
        definition: {
          name: '/',
          type: 'dir'
        },
        parent: null
      });

      currentEntry.loadDeep(parts, entry => {
        self.selectedS3Entry(entry);
        entry.open(true);
        self.loading(false);
      });
    };

    huePubSub.subscribe('assist.selectS3Entry', entry => {
      self.selectedS3Entry(entry);
      apiHelper.setInTotalStorage('assist', 'currentS3Path', entry.path);
    });

    huePubSub.subscribe('assist.s3.refresh', () => {
      huePubSub.publish('assist.clear.s3.cache');
      self.reload();
    });
  }

  init() {
    const self = this;
    if (self.initialized) {
      return;
    }
    self.reload();
    self.initialized = true;
  }
}

componentUtils.registerComponent('hue-assist-s3-panel', AssistS3Panel, TEMPLATE);

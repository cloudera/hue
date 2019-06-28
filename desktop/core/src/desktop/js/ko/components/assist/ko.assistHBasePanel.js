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
import AssistHBaseEntry from 'ko/components/assist/assistHBaseEntry';
import componentUtils from 'ko/components/componentUtils';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';

const TEMPLATE = `
  <script type="text/html" id="hbase-context-items">
    <!-- ko if: definition.host -->
    <li><a href="javascript: void(0);" data-bind="click: open"><i class="fa fa-fw fa-folder-open-o"></i> ${I18n(
      'Open cluster'
    )}</a></li>
    <!-- /ko -->
    <!-- ko ifnot: definition.host -->
    <li><a href="javascript: void(0);" data-bind="click: open"><!-- ko template: { name: 'app-icon-template', data: { icon: 'hbase' } } --><!-- /ko --> ${I18n(
      'Open in HBase'
    )}</a></li>
    <!-- /ko -->
  </script>
  
  <script type="text/html" id="assist-hbase-header-actions">
    <div class="assist-db-header-actions">
      <a class="inactive-action" href="javascript:void(0)" data-bind="click: function () { huePubSub.publish('assist.hbase.refresh'); }"><i class="pointer fa fa-refresh" data-bind="css: { 'fa-spin blue' : loading }" title="${I18n(
        'Manual refresh'
      )}"></i></a>
    </div>
  </script>

  <!-- ko with: selectedHBaseEntry -->
  <div class="assist-inner-header assist-breadcrumb" >
    <!-- ko if: definition.host !== '' -->
    <a href="javascript: void(0);" data-bind="click: function () { huePubSub.publish('assist.clickHBaseRootItem'); }">
      <i class="fa fa-fw fa-chevron-left"></i>
      <i class="fa fa-fw fa-th-large"></i>
      <span data-bind="text: definition.name"></span>
    </a>
    <!-- /ko -->
    <!-- ko if: definition.host === '' -->
    ${I18n('Clusters')}
    <!-- /ko -->
    <!-- ko template: 'assist-hbase-header-actions' --><!-- /ko -->
  </div>
  <div class="assist-flex-fill assist-hbase-scrollable" data-bind="delayedOverflow">
    <div data-bind="visible: ! loading() && ! hasErrors()" style="position: relative;">
      <ul class="assist-tables" data-bind="foreachVisible: { data: entries, minHeight: 22, container: '.assist-hbase-scrollable' }">
        <li class="assist-entry assist-table-link" style="position: relative;" data-bind="appAwareTemplateContextMenu: { template: 'hbase-context-items', scrollContainer: '.assist-hbase-scrollable' }, visibleOnHover: { 'selector': '.assist-actions' }">
          <a href="javascript:void(0)" class="assist-entry assist-table-link" data-bind="multiClick: { click: click, dblClick: dblClick }, attr: {'title': definition.name }">
            <!-- ko if: definition.host -->
            <i class="fa fa-fw fa-th-large muted valign-middle"></i>
            <!-- /ko -->
            <!-- ko ifnot: definition.host -->
            <i class="fa fa-fw fa-th muted valign-middle"></i>
            <!-- /ko -->
            <span draggable="true" data-bind="text: definition.name, draggableText: { text: '\\\\'' + definition.name + '\\\\'', meta: {'type': 'collection', 'definition': definition} }"></span>
          </a>
        </li>
      </ul>
      <!-- ko if: !loading() && entries().length === 0 -->
      <ul class="assist-tables">
        <li class="assist-entry">
          <span class="assist-no-entries">
          <!-- ko if: definition.host === '' -->
          ${I18n('No clusters available.')}
          <!-- /ko -->
          <!-- ko if: definition.host !== '' -->
          ${I18n('No tables available.')}
          <!-- /ko -->
          </span>
        </li>
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

class AssistHBasePanel {
  /**
   * @param {Object} options
   * @constructor
   **/
  constructor(options) {
    const self = this;
    self.initialized = false;

    const root = new AssistHBaseEntry({
      definition: {
        host: '',
        name: '',
        port: 0
      }
    });

    self.selectedHBaseEntry = ko.observable();
    self.reload = () => {
      self.selectedHBaseEntry(root);
      root.loadEntries(() => {
        const lastOpenendPath = apiHelper.getFromTotalStorage(
          'assist',
          'last.opened.hbase.entry',
          null
        );
        if (lastOpenendPath) {
          root.entries().every(entry => {
            if (entry.path === lastOpenendPath) {
              entry.open();
              return false;
            }
            return true;
          });
        }
      });
    };

    self.selectedHBaseEntry.subscribe(newEntry => {
      if (newEntry !== root || (newEntry === root && newEntry.loaded)) {
        apiHelper.setInTotalStorage('assist', 'last.opened.hbase.entry', newEntry.path);
      }
    });

    huePubSub.subscribe('assist.clickHBaseItem', entry => {
      if (entry.definition.host) {
        entry.loadEntries();
        self.selectedHBaseEntry(entry);
      } else {
        huePubSub.publish('assist.dblClickHBaseItem', entry);
      }
    });

    huePubSub.subscribe('assist.clickHBaseRootItem', () => {
      self.reload();
    });

    const delayChangeHash = hash => {
      window.setTimeout(() => {
        window.location.hash = hash;
      }, 0);
    };

    self.lastClickeHBaseEntry = null;
    self.HBaseLoaded = false;

    huePubSub.subscribeOnce('hbase.app.loaded', () => {
      if (self.selectedHBaseEntry() && self.lastClickeHBaseEntry) {
        delayChangeHash(
          self.selectedHBaseEntry().definition.name +
            '/' +
            self.lastClickeHBaseEntry.definition.name
        );
      }
      self.HBaseLoaded = true;
    });

    huePubSub.subscribe('assist.dblClickHBaseItem', entry => {
      const hash = self.selectedHBaseEntry().definition.name + '/' + entry.definition.name;
      if (window.location.pathname.startsWith('/hue/hbase')) {
        window.location.hash = hash;
      } else {
        self.lastClickeHBaseEntry = entry;
        huePubSub.subscribeOnce('app.gained.focus', app => {
          if (app === 'hbase' && self.HBaseLoaded) {
            delayChangeHash(hash);
          }
        });
        huePubSub.publish('open.link', '/hbase');
      }
    });

    huePubSub.subscribe('assist.hbase.refresh', () => {
      huePubSub.publish('assist.clear.hbase.cache');
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

componentUtils.registerComponent('hue-assist-hbase-panel', AssistHBasePanel, TEMPLATE);

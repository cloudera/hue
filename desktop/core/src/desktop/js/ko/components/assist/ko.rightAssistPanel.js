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

import {
  ASSIST_LANG_REF_PANEL_SHOW_TOPIC_EVENT,
  ASSIST_LANG_REF_SHOW_TOPIC_EVENT,
  SHOW_RIGHT_ASSIST_EVENT
} from './events';
import { ACTIVE_SNIPPET_CONNECTOR_CHANGED_EVENT } from 'apps/editor/events';
import componentUtils from 'ko/components/componentUtils';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';
import { withLocalStorage } from 'utils/storageUtils';

const EDITOR_ASSISTANT_TAB = 'editorAssistant';
const DASHBOARD_ASSISTANT_TAB = 'dashboardAssistant';
const FUNCTIONS_TAB = 'functions';
const SCHEDULES_TAB = 'schedules';
const LANG_REF_TAB = 'langRef';

const TEMPLATE = `
  <div class="right-assist-tabs" data-bind="splitFlexDraggable : {
      containerSelector: '.content-wrapper',
      sidePanelSelector: '.right-panel',
      sidePanelVisible: visible,
      orientation: 'right',
      onPosition: function() { huePubSub.publish('split.draggable.position') }
    }">
    <div class="right-assist-tab" data-bind="visible: editorAssistantTabAvailable" style="display:none;"><a class="inactive-action" href="javascript: void(0);" title="${I18n(
      'Assistant'
    )}" data-bind="css: { 'blue' : activeTab() === 'editorAssistant' }, tooltip: { placement: 'left' }, click: editorAssistantTabClick"><i class="fa fa-fw fa-compass"></i></a></div>
    <div class="right-assist-tab" data-bind="visible: dashboardAssistantTabAvailable" style="display:none;"><a class="inactive-action" href="javascript: void(0);" title="${I18n(
      'Assistant'
    )}" data-bind="css: { 'blue' : activeTab() === 'dashboardAssistant' }, tooltip: { placement: 'left' }, click: dashboardAssistantTabClick"><i class="fa fa-fw fa-compass"></i></a></div>
    <div class="right-assist-tab" data-bind="visible: functionsTabAvailable" style="display:none;"><a class="inactive-action" href="javascript: void(0);" title="${I18n(
      'Functions'
    )}" data-bind="css: { 'blue' : activeTab() === 'functions' }, tooltip: { placement: 'left' }, click: functionsTabClick"><i class="fa fa-fw fa-superscript"></i></a></div>
    <div class="right-assist-tab" data-bind="visible: langRefTabAvailable" style="display:none;"><a class="inactive-action" href="javascript: void(0);" title="${I18n(
      'Language Reference'
    )}" data-bind="css: { 'blue' : activeTab() === 'langRef' }, tooltip: { placement: 'left' }, click: langRefTabClick"><i class="fa fa-fw fa-book"></i></a></div>
    <div class="right-assist-tab" data-bind="visible: schedulesTabAvailable" style="display:none;"><a class="inactive-action" href="javascript: void(0);" title="${I18n(
      'Schedule'
    )}" data-bind="css: { 'blue' : activeTab() === 'schedules' }, tooltip: { placement: 'left' }, click: schedulesTabClick"><i class="fa fa-fw fa-calendar"></i></a></div>
  </div>

  <!-- ko if: visible -->
  <div class="right-assist-contents">
    <!-- ko if: editorAssistantTabAvailable-->
    <div data-bind="
        component: { 
          name: 'assist-editor-context-panel', 
          params: { 
            activeTab: activeTab, 
            connector: connector 
          }
        },
        visible: activeTab() === 'editorAssistant'
      "></div>
    <!-- /ko -->

    <!-- ko if: functionsTabAvailable -->
    <div data-bind="
        component: {
          name: 'assist-functions-panel',
          params: {
            activeConnector: connector
          }
        },
        visible: activeTab() === 'functions'
      "></div>
    <!-- /ko -->

    <!-- ko if: langRefTabAvailable -->
    <div data-bind="
        component: {
          name: 'assist-language-reference-panel',
          params: {
            connector: connector
          }
        },
        visible: activeTab() === 'langRef'
      "></div>
    <!-- /ko -->

    <!-- ko if: dashboardAssistantTabAvailable -->
    <div data-bind="component: { name: 'assist-dashboard-panel' }, visible: activeTab() === 'dashboardAssistant'"></div>
    <!-- /ko -->

    <div data-bind="component: { name: 'assist-schedule-panel' }, visible: activeTab() === 'schedules'" style="display:none;"></div>
  </div>
  <!-- /ko -->
`;

class RightAssistPanel {
  constructor(params) {
    this.activeTab = ko.observable();
    this.visible = params.visible;
    this.connector = ko.observable();

    this.editorAssistantTabAvailable = ko.pureComputed(
      () => this.connector() && this.connector().is_sql
    );
    this.dashboardAssistantTabAvailable = ko.pureComputed(
      () => this.connector() && this.connector().id === 'dashboard'
    );
    this.functionsTabAvailable = ko.pureComputed(
      () =>
        this.connector() &&
        (this.connector().dialect === 'hive' ||
          this.connector().dialect === 'impala' ||
          this.connector().dialect === 'pig' ||
          this.connector().dialect === 'flink')
    );
    this.langRefTabAvailable = ko.pureComputed(
      () =>
        this.connector() &&
        (this.connector().dialect === 'hive' || this.connector().dialect === 'impala')
    );
    this.schedulesTabAvailable = ko.observable(false);

    this.lastActiveTabEditor = ko.observable();
    withLocalStorage(
      'assist.last.open.right.panel',
      this.lastActiveTabEditor,
      EDITOR_ASSISTANT_TAB
    );
    this.lastActiveTabDashboard = ko.observable();
    withLocalStorage(
      'assist.last.open.right.panel.dashboard',
      this.lastActiveTabDashboard,
      DASHBOARD_ASSISTANT_TAB
    );

    huePubSub.subscribe('assist.highlight.risk.suggestions', () => {
      if (this.editorAssistantTabAvailable() && this.activeTab() !== EDITOR_ASSISTANT_TAB) {
        this.activeTab(EDITOR_ASSISTANT_TAB);
      }
    });

    huePubSub.subscribe(ASSIST_LANG_REF_SHOW_TOPIC_EVENT, targetTopic => {
      huePubSub.publish(SHOW_RIGHT_ASSIST_EVENT);
      if (this.langRefTabAvailable() && this.activeTab() !== LANG_REF_TAB) {
        this.activeTab(LANG_REF_TAB);
      }
      huePubSub.publish(ASSIST_LANG_REF_PANEL_SHOW_TOPIC_EVENT, targetTopic);
    });

    const updateTabs = () => {
      if (!this.visible()) {
        this.activeTab(undefined);
        return;
      }
      if (this.lastActiveTabEditor() === FUNCTIONS_TAB && this.functionsTabAvailable()) {
        this.activeTab(FUNCTIONS_TAB);
      } else if (this.lastActiveTabEditor() === SCHEDULES_TAB && this.schedulesTabAvailable()) {
        this.activeTab(SCHEDULES_TAB);
      } else if (this.lastActiveTabEditor() === LANG_REF_TAB && this.langRefTabAvailable()) {
        this.activeTab(LANG_REF_TAB);
      } else if (this.editorAssistantTabAvailable()) {
        this.activeTab(EDITOR_ASSISTANT_TAB);
      } else if (this.functionsTabAvailable()) {
        this.activeTab(FUNCTIONS_TAB);
      } else if (this.schedulesTabAvailable()) {
        this.activeTab(SCHEDULES_TAB);
      } else if (this.dashboardAssistantTabAvailable()) {
        this.activeTab(DASHBOARD_ASSISTANT_TAB);
      } else {
        this.activeTab(undefined);
      }
    };

    const updateContentsForConnector = connector => {
      this.connector(connector);
      this.schedulesTabAvailable(false);
      if (connector && connector.id !== 'dashboard') {
        if (window.ENABLE_QUERY_SCHEDULING) {
          huePubSub.subscribeOnce('set.current.app.view.model', viewModel => {
            // Async
            this.schedulesTabAvailable(!!viewModel.selectedNotebook);
            updateTabs();
          });
          huePubSub.publish('get.current.app.view.model');
        } else {
          this.schedulesTabAvailable(false);
        }
      }
      updateTabs();
    };

    huePubSub.subscribe(ACTIVE_SNIPPET_CONNECTOR_CHANGED_EVENT, updateContentsForConnector);

    const onAppChange = appName => {
      if (appName === 'dashboard') {
        updateContentsForConnector({ id: appName, is_sql: false });
      }
    };
    huePubSub.publish('get.current.app.name', onAppChange);
    huePubSub.subscribe('set.current.app.name', onAppChange);
    updateTabs();
  }

  switchTab(tabName) {
    if (this.activeTab() === tabName) {
      this.visible(false);
      this.activeTab(undefined);
    } else {
      this.activeTab(tabName);
      if (!this.visible()) {
        this.visible(true);
      }
    }
  }

  editorAssistantTabClick() {
    this.lastActiveTabEditor(EDITOR_ASSISTANT_TAB);
    this.switchTab(EDITOR_ASSISTANT_TAB);
  }

  dashboardAssistantTabClick() {
    this.lastActiveTabDashboard(DASHBOARD_ASSISTANT_TAB);
    this.switchTab(DASHBOARD_ASSISTANT_TAB);
  }

  functionsTabClick() {
    this.lastActiveTabEditor(FUNCTIONS_TAB);
    this.switchTab(FUNCTIONS_TAB);
  }

  langRefTabClick() {
    this.lastActiveTabEditor(LANG_REF_TAB);
    this.switchTab(LANG_REF_TAB);
  }

  schedulesTabClick() {
    this.lastActiveTabEditor(SCHEDULES_TAB);
    this.switchTab(SCHEDULES_TAB);
  }
}

componentUtils.registerStaticComponent('right-assist-panel', RightAssistPanel, TEMPLATE);

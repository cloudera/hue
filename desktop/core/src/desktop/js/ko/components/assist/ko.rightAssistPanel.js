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

import apiHelper from 'api/apiHelper';
import componentUtils from 'ko/components/componentUtils';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';

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
    <div data-bind="component: { name: 'assist-editor-context-panel', params: { activeTab: activeTab, sourceType: sourceType } }, visible: activeTab() === 'editorAssistant'"></div>
    <!-- /ko -->

    <!-- ko if: functionsTabAvailable -->
    <div data-bind="component: { name: 'assist-functions-panel' }, visible: activeTab() === 'functions'"></div>
    <!-- /ko -->

    <!-- ko if: langRefTabAvailable -->
    <div data-bind="component: { name: 'assist-language-reference-panel' }, visible: activeTab() === 'langRef'"></div>
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
    this.disposals = [];

    this.activeTab = ko.observable();
    this.visible = params.visible;
    this.sourceType = ko.observable();

    this.editorAssistantTabAvailable = ko.observable(false);
    this.dashboardAssistantTabAvailable = ko.observable(false);
    this.functionsTabAvailable = ko.observable(false);
    this.langRefTabAvailable = ko.observable(false);
    this.schedulesTabAvailable = ko.observable(false);

    this.lastActiveTabEditor = apiHelper.withTotalStorage(
      'assist',
      'last.open.right.panel',
      ko.observable(),
      EDITOR_ASSISTANT_TAB
    );
    this.lastActiveTabDashboard = apiHelper.withTotalStorage(
      'assist',
      'last.open.right.panel.dashboard',
      ko.observable(),
      DASHBOARD_ASSISTANT_TAB
    );

    huePubSub.subscribe('assist.highlight.risk.suggestions', () => {
      if (this.editorAssistantTabAvailable() && this.activeTab() !== EDITOR_ASSISTANT_TAB) {
        this.activeTab(EDITOR_ASSISTANT_TAB);
      }
    });

    huePubSub.subscribe('assist.lang.ref.show.topic', targetTopic => {
      huePubSub.publish('right.assist.show');
      if (this.langRefTabAvailable() && this.activeTab() !== LANG_REF_TAB) {
        this.activeTab(LANG_REF_TAB);
      }
      huePubSub.publish('assist.lang.ref.panel.show.topic', targetTopic);
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

    const updateContentsForType = (type, isSqlDialect) => {
      this.sourceType(type);

      // TODO: Get these dynamically from langref and functions modules when moved to webpack
      this.functionsTabAvailable(type === 'hive' || type === 'impala' || type === 'pig');
      this.langRefTabAvailable(type === 'hive' || type === 'impala');
      this.editorAssistantTabAvailable(isSqlDialect);
      this.dashboardAssistantTabAvailable(type === 'dashboard');
      this.schedulesTabAvailable(false);
      if (type !== 'dashboard') {
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

    const snippetTypeSub = huePubSub.subscribe('active.snippet.type.changed', details => {
      updateContentsForType(details.type, details.isSqlDialect);
    });
    this.disposals.push(snippetTypeSub.remove.bind(snippetTypeSub));

    huePubSub.subscribe('set.current.app.name', appName => {
      if (appName === 'dashboard') {
        updateContentsForType(appName, false);
      }
    });
    huePubSub.publish('get.current.app.name');
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

  dispose() {
    this.disposals.forEach(dispose => {
      dispose();
    });
  }
}

componentUtils.registerStaticComponent('right-assist-panel', RightAssistPanel, TEMPLATE);

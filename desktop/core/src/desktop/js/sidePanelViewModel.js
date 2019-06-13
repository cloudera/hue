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

import $ from 'jquery';
import ko from 'knockout';

import apiHelper from 'api/apiHelper';
import hueAnalytics from 'utils/hueAnalytics';
import huePubSub from 'utils/huePubSub';

class SidePanelViewModel {
  constructor() {
    const self = this;
    self.assistWithoutStorage = ko.observable(false);
    self.leftAssistVisible = ko.observable(
      apiHelper.getFromTotalStorage('assist', 'left_assist_panel_visible', true)
    );
    self.leftAssistVisible.subscribe(val => {
      if (!self.assistWithoutStorage()) {
        apiHelper.setInTotalStorage('assist', 'left_assist_panel_visible', val);
      }
      hueAnalytics.convert('hue', 'leftAssistVisible/' + val);
      window.setTimeout(() => {
        huePubSub.publish('split.panel.resized');
        $(window).trigger('resize');
      }, 0);
    });

    self.rightAssistVisible = ko.observable(
      apiHelper.getFromTotalStorage('assist', 'right_assist_panel_visible', true)
    );
    self.rightAssistVisible.subscribe(val => {
      if (!self.assistWithoutStorage()) {
        apiHelper.setInTotalStorage('assist', 'right_assist_panel_visible', val);
      }
      hueAnalytics.convert('hue', 'rightAssistVisible/' + val);
      window.setTimeout(() => {
        huePubSub.publish('reposition.scroll.anchor.up');
        huePubSub.publish('split.panel.resized');
        $(window).trigger('resize');
      }, 0);
    });
    self.rightAssistAvailable = ko.observable(false);

    huePubSub.subscribe('assist.highlight.risk.suggestions', () => {
      if (self.rightAssistAvailable() && !self.rightAssistVisible()) {
        self.rightAssistVisible(true);
      }
    });

    huePubSub.subscribe('set.current.app.name', appName => {
      if (appName === 'dashboard') {
        self.rightAssistAvailable(true);
      } else if (appName !== 'editor' && appName !== 'notebook') {
        self.rightAssistAvailable(false);
      }
    });

    huePubSub.subscribe('active.snippet.type.changed', details => {
      self.rightAssistAvailable(details.isSqlDialect || details.type === 'pig');
    });

    huePubSub.publish('get.current.app.name');

    self.activeAppViewModel = ko.observable();
    self.currentApp = ko.observable('');
    self.templateApp = ko.pureComputed(() => {
      if (['editor', 'notebook'].indexOf(self.currentApp()) > -1) {
        return self.currentApp();
      } else {
        return '';
      }
    });

    self.contextPanelVisible = ko.observable(false);
    self.contextPanelVisible.subscribe(() => {
      let $el = $('.snippet .ace-editor:visible');
      if ($el.length === 0) {
        $el = $('.content-panel:visible');
      }
      $('.context-panel')
        .width($el.width())
        .css('left', $el.offset().left);
    });

    self.sessionsAvailable = ko.observable(false);

    self.activeAppViewModel.subscribe(viewModel => {
      self.sessionsAvailable(typeof viewModel.selectedNotebook !== 'undefined');
    });

    huePubSub.subscribe('context.panel.visible', visible => {
      self.contextPanelVisible(visible);
    });

    huePubSub.subscribe('set.current.app.view.model', self.activeAppViewModel);
    huePubSub.subscribe('app.dom.loaded', self.currentApp);

    huePubSub.publish('get.current.app.view.model');

    let previousVisibilityValues = {};
    huePubSub.subscribe('both.assists.hide', withoutStorage => {
      previousVisibilityValues = {
        left: self.leftAssistVisible(),
        right: self.rightAssistVisible()
      };
      self.assistWithoutStorage(withoutStorage);
      self.leftAssistVisible(false);
      self.rightAssistVisible(false);
      window.setTimeout(() => {
        self.assistWithoutStorage(false);
      }, 0);
    });

    huePubSub.subscribe('both.assists.show', withoutStorage => {
      self.assistWithoutStorage(withoutStorage);
      self.leftAssistVisible(previousVisibilityValues.left);
      self.rightAssistVisible(previousVisibilityValues.right);
      window.setTimeout(() => {
        self.assistWithoutStorage(false);
      }, 0);
    });

    huePubSub.subscribe('right.assist.hide', withoutStorage => {
      previousVisibilityValues = {
        left: self.leftAssistVisible(),
        right: self.rightAssistVisible()
      };
      self.assistWithoutStorage(withoutStorage);
      self.rightAssistVisible(false);
      window.setTimeout(() => {
        self.assistWithoutStorage(false);
      }, 0);
    });

    huePubSub.subscribe('right.assist.show', () => {
      if (!self.rightAssistVisible()) {
        self.rightAssistVisible(true);
      }
    });

    huePubSub.subscribe('left.assist.show', () => {
      if (!self.leftAssistVisible()) {
        self.leftAssistVisible(true);
      }
    });
  }
}

export default SidePanelViewModel;

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
import * as ko from 'knockout';

import hueAnalytics from 'utils/hueAnalytics';
import huePubSub from 'utils/huePubSub';
import { ACTIVE_SNIPPET_CONNECTOR_CHANGED_EVENT } from 'apps/editor/events';
import {
  SHOW_LEFT_ASSIST_EVENT,
  SHOW_RIGHT_ASSIST_EVENT,
  BOTH_ASSIST_TOGGLE_EVENT
} from 'ko/components/assist/events';
import { getFromLocalStorage, setInLocalStorage } from 'utils/storageUtils';
import defer from 'utils/timing/defer';

class SidePanelViewModel {
  constructor() {
    const self = this;
    self.assistWithoutStorage = ko.observable(false);
    self.leftAssistVisible = ko.observable(
      getFromLocalStorage('assist.left_assist_panel_visible', true)
    );
    self.leftAssistVisible.subscribe(val => {
      if (!self.assistWithoutStorage()) {
        setInLocalStorage('assist.left_assist_panel_visible', val);
      }
      hueAnalytics.convert('hue', 'leftAssistVisible/' + val);
      window.setTimeout(() => {
        huePubSub.publish('split.panel.resized');
        $(window).trigger('resize');
      }, 0);
    });

    self.rightAssistVisible = ko.observable(
      getFromLocalStorage('assist.right_assist_panel_visible', true)
    );
    self.rightAssistVisible.subscribe(val => {
      if (!self.assistWithoutStorage()) {
        setInLocalStorage('assist.right_assist_panel_visible', val);
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

    const onAppChange = appName => {
      self.rightAssistAvailable(
        appName === 'dashboard' || appName === 'editor' || appName === 'notebook'
      );
    };

    huePubSub.subscribe('set.current.app.name', onAppChange);
    huePubSub.publish('get.current.app.name', onAppChange);

    huePubSub.subscribe(ACTIVE_SNIPPET_CONNECTOR_CHANGED_EVENT, connector => {
      self.rightAssistAvailable(connector && (connector.is_sql || connector.dialect === 'pig'));
    });

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
      $('.context-panel').width($el.width()).css('left', $el.offset().left);
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

    const previousVisibilityValues = {
      left: undefined,
      right: undefined
    };

    const hideAssists = (left, right, preventStorage) => {
      previousVisibilityValues.left = undefined;
      previousVisibilityValues.right = undefined;
      self.assistWithoutStorage(preventStorage);
      if (left) {
        previousVisibilityValues.left = self.leftAssistVisible();
        self.leftAssistVisible(false);
      }
      if (right) {
        previousVisibilityValues.right = self.rightAssistVisible();
        self.rightAssistVisible(false);
      }
      defer(() => {
        self.assistWithoutStorage(false);
      });
    };

    huePubSub.subscribe(BOTH_ASSIST_TOGGLE_EVENT, () => {
      const hideBoth = self.rightAssistVisible() || self.leftAssistVisible();
      if (hideBoth) {
        hideAssists(true, true);
      } else {
        self.leftAssistVisible(true);
        self.rightAssistVisible(true);
      }
    });

    huePubSub.subscribe('both.assists.hide', preventStorage => {
      hideAssists(true, true, preventStorage);
    });

    huePubSub.subscribe('right.assist.hide', preventStorage => {
      hideAssists(false, true, preventStorage);
    });

    huePubSub.subscribe('left.assist.hide', preventStorage => {
      hideAssists(true, false, preventStorage);
    });

    huePubSub.subscribe('both.assists.revert', preventStorage => {
      self.assistWithoutStorage(preventStorage);
      if (typeof previousVisibilityValues.left !== 'undefined') {
        self.leftAssistVisible(previousVisibilityValues.left);
      }
      if (typeof previousVisibilityValues.right !== 'undefined' && self.rightAssistAvailable()) {
        self.rightAssistVisible(previousVisibilityValues.right);
      }
      window.setTimeout(() => {
        self.assistWithoutStorage(false);
      }, 0);
    });

    huePubSub.subscribe(SHOW_RIGHT_ASSIST_EVENT, () => {
      if (!self.rightAssistVisible()) {
        self.rightAssistVisible(true);
      }
    });

    huePubSub.subscribe(SHOW_LEFT_ASSIST_EVENT, () => {
      if (!self.leftAssistVisible()) {
        self.leftAssistVisible(true);
      }
    });
  }
}

export default SidePanelViewModel;

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
import huePubSub from 'utils/huePubSub';
import {
  CONFIG_REFRESHED_EVENT,
  GET_KNOWN_CONFIG_EVENT,
  REFRESH_CONFIG_EVENT
} from 'utils/hueConfig';

class TopNavViewModel {
  constructor(onePageViewModel) {
    const self = this;
    self.onePageViewModel = onePageViewModel;

    // TODO: Drop. Just for PoC
    self.pocClusterMode = ko.observable();
    apiHelper.withTotalStorage('topNav', 'multiCluster', self.pocClusterMode, 'dw');
    huePubSub.subscribe('set.multi.cluster.mode', self.pocClusterMode);

    self.hasJobBrowser = ko.observable(window.HAS_JOB_BROWSER);
    self.clusters = ko.observableArray();

    const configUpdated = config => {
      if (config && config.clusters) {
        self.clusters(config.clusters);
      }

      self.hasJobBrowser(
        window.HAS_JOB_BROWSER &&
          config &&
          config.app_config &&
          config.app_config.browser &&
          (config.app_config.browser.interpreter_names.indexOf('yarn') !== -1 ||
            config.app_config.editor.interpreter_names.indexOf('impala') !== -1 ||
            config.app_config.browser.interpreter_names.indexOf('dataeng') !== -1)
      );
    };

    huePubSub.publish(GET_KNOWN_CONFIG_EVENT, configUpdated);
    huePubSub.subscribe(CONFIG_REFRESHED_EVENT, configUpdated);

    huePubSub.subscribe('hue.new.default.app', () => {
      huePubSub.publish(REFRESH_CONFIG_EVENT);
    });
  }
}

export default TopNavViewModel;

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
import AssistStorageEntry from 'assist/assistStorageEntry';
import huePubSub from 'utils/huePubSub';

class AssistAdlsPanel {
  constructor(options) {
    const self = this;
    self.selectedAdlsEntry = ko.observable();
    self.loading = ko.observable();
    self.initialized = false;

    const loadPath = path => {
      self.loading(true);
      const parts = path.split('/');
      parts.shift();

      const currentEntry = new AssistStorageEntry({
        type: 'adls',
        definition: {
          name: '/',
          type: 'dir'
        },
        parent: null
      });

      currentEntry.loadDeep(parts, entry => {
        self.selectedAdlsEntry(entry);
        entry.open(true);
        self.loading(false);
      });
    };

    self.reload = () => {
      loadPath(apiHelper.getFromTotalStorage('assist', 'currentAdlsPath', '/'));
    };

    huePubSub.subscribe('assist.adls.go.home', () => {
      loadPath(window.USER_HOME_DIR);
      apiHelper.setInTotalStorage('assist', 'currentAdlsPath', window.USER_HOME_DIR);
    });

    huePubSub.subscribe('assist.selectAdlsEntry', entry => {
      self.selectedAdlsEntry(entry);
      apiHelper.setInTotalStorage('assist', 'currentAdlsPath', entry.path);
    });

    huePubSub.subscribe('assist.adls.refresh', () => {
      huePubSub.publish('assist.clear.adls.cache');
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

export default AssistAdlsPanel;

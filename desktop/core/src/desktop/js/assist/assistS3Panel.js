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

export default AssistS3Panel;

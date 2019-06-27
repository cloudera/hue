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
import AssistGitEntry from 'assist/assistGitEntry';
import huePubSub from 'utils/huePubSub';

class AssistGitPanel {
  /**
   * @param {Object} options
   * @constructor
   **/
  constructor(options) {
    const self = this;

    self.selectedGitEntry = ko.observable();
    self.reload = function() {
      const lastKnownPath = apiHelper.getFromTotalStorage(
        'assist',
        'currentGitPath',
        window.USER_HOME_DIR
      );
      const parts = lastKnownPath.split('/');
      parts.shift();

      const currentEntry = new AssistGitEntry({
        definition: {
          name: '/',
          type: 'dir'
        },
        parent: null
      });

      currentEntry.loadDeep(parts, entry => {
        self.selectedGitEntry(entry);
        entry.open(true);
      });
    };

    huePubSub.subscribe('assist.selectGitEntry', entry => {
      self.selectedGitEntry(entry);
      apiHelper.setInTotalStorage('assist', 'currentGitPath', entry.path);
    });

    huePubSub.subscribe('assist.git.refresh', () => {
      huePubSub.publish('assist.clear.git.cache');
      self.reload();
    });
  }

  init() {
    this.reload();
  }
}

export default AssistGitPanel;

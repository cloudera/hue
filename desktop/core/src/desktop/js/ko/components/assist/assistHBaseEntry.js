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
import huePubSub from 'utils/huePubSub';

class AssistHBaseEntry {
  /**
   * @param {object} options
   * @param {object} options.definition
   * @param {string} options.definition.name
   * @constructor
   */
  constructor(options) {
    const self = this;

    self.definition = options.definition;
    self.path = self.definition.name;

    self.entries = ko.observableArray([]);

    self.loaded = false;
    self.loading = ko.observable(false);
    self.hasErrors = ko.observable(false);

    self.hasEntries = ko.pureComputed(() => self.entries().length > 0);
  }

  loadEntries(callback) {
    const self = this;
    if (self.loading()) {
      return;
    }
    self.loading(true);
    self.hasErrors(false);

    apiHelper.fetchHBase({
      parent: self.definition,
      successCallback: data => {
        self.entries(
          data.data.map(
            obj =>
              new AssistHBaseEntry({
                definition: obj
              })
          )
        );
        self.loaded = true;
        self.loading(false);
        if (callback) {
          callback();
        }
      },
      errorCallback: () => {
        self.hasErrors(true);
        self.loading(false);
        if (callback) {
          callback();
        }
      }
    });
  }

  open() {
    huePubSub.publish('assist.clickHBaseItem', this);
  }

  click() {
    huePubSub.publish('assist.clickHBaseItem', this);
  }

  dblClick() {
    huePubSub.publish('assist.dblClickHBaseItem', this);
  }
}

export default AssistHBaseEntry;

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
import AssistHBaseEntry from 'assist/assistHBaseEntry';
import huePubSub from 'utils/huePubSub';

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

export default AssistHBasePanel;

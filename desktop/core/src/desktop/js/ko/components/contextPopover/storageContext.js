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

import AssistStorageEntry from 'ko/components/assist/assistStorageEntry';
import huePubSub from 'utils/huePubSub';

class StorageContext {
  constructor(options) {
    const self = this;

    self.popover = options.popover;
    self.storageEntry = ko.observable();
    self.editorLocation = options.editorLocation;

    self.loading = ko.pureComputed(() => {
      return self.storageEntry() && self.storageEntry().loading();
    });

    self.storageEntry.subscribe(newVal => {
      if (!newVal.loaded && !newVal.loading()) {
        if (newVal.definition.type === 'dir') {
          newVal.open(true);
        } else {
          newVal.loadPreview();
        }
      }
    });

    self.storageEntry(options.storageEntry);

    self.breadCrumbs = ko.pureComputed(() => {
      const result = [];
      let currentEntry = self.storageEntry();
      do {
        result.unshift({
          name: currentEntry.definition.name,
          isActive: currentEntry === self.storageEntry(),
          storageEntry: currentEntry,
          makeActive: function() {
            self.storageEntry(this.storageEntry);
          }
        });

        currentEntry = currentEntry.parent;
      } while (currentEntry);
      return result;
    });
  }

  openInFileBrowser(entry) {
    huePubSub.publish('open.link', entry.definition.url);
    huePubSub.publish('context.popover.hide');
    huePubSub.publish('global.search.close');
  }

  replaceInEditor(entry, storageContext) {
    const text = entry.originalType ? entry.originalType + ':/' + entry.path : entry.path;
    huePubSub.publish('ace.replace', {
      location: storageContext.editorLocation,
      text: text
    });
    huePubSub.publish('context.popover.hide');
  }

  goHome() {
    const self = this;
    AssistStorageEntry.getEntry(window.USER_HOME_DIR, self.storageEntry().type).done(
      self.storageEntry
    );
  }
}

export default StorageContext;

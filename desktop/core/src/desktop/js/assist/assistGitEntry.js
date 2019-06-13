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

class AssistGitEntry {
  /**
   * @param {object} options
   * @param {object} options.definition
   * @param {string} options.definition.name
   * @param {string} options.definition.type (file, dir)
   * @param {AssistGitEntry} options.parent
   * @constructor
   */
  constructor(options) {
    const self = this;

    self.definition = options.definition;
    self.parent = options.parent;
    self.path = '';
    if (self.parent !== null) {
      self.path = self.parent.path;
      if (self.parent.path !== '/') {
        self.path += '/';
      }
    }
    self.path += self.definition.name;

    self.fileContent = ko.observable('');

    self.entries = ko.observableArray([]);

    self.loaded = false;
    self.loading = ko.observable(false);
    self.loadingMore = ko.observable(false);
    self.hasErrors = ko.observable(false);
    self.open = ko.observable(false);

    self.open.subscribe(newValue => {
      if (newValue && self.entries().length === 0) {
        self.loadEntries();
      }
    });

    self.hasEntries = ko.pureComputed(() => {
      return self.entries().length > 0;
    });
  }

  dblClick() {
    const self = this;
    if (self.definition.type !== 'file') {
      return;
    }
    self.hasErrors(false);

    apiHelper.fetchGitContents({
      pathParts: self.getHierarchy(),
      fileType: self.definition.type,
      successCallback: data => {
        self.fileContent(data.content);
        huePubSub.publish('assist.dblClickGitItem', self);
      },
      errorCallback: () => {
        self.hasErrors(true);
        self.loading(false);
      }
    });
  }

  loadEntries(callback) {
    const self = this;
    if (self.loading()) {
      return;
    }
    self.loading(true);
    self.hasErrors(false);

    apiHelper.fetchGitContents({
      pathParts: self.getHierarchy(),
      fileType: self.definition.type,
      successCallback: data => {
        const filteredFiles = data.files.filter(file => file.name !== '.' && file.name !== '..');
        self.entries(
          filteredFiles.map(
            file =>
              new AssistGitEntry({
                definition: file,
                parent: self
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

  loadDeep(folders, callback) {
    const self = this;

    if (folders.length === 0) {
      callback(self);
      return;
    }

    const findNextAndLoadDeep = () => {
      const nextName = folders.shift();
      const foundEntry = self
        .entries()
        .filter(entry => entry.definition.name === nextName && entry.definition.type === 'dir');
      if (foundEntry.length === 1) {
        foundEntry[0].loadDeep(folders, callback);
      } else if (!self.hasErrors()) {
        callback(self);
      }
    };

    if (!self.loaded) {
      self.loadEntries(findNextAndLoadDeep);
    } else {
      findNextAndLoadDeep();
    }
  }

  getHierarchy() {
    const self = this;
    const parts = [];
    let entry = self;
    while (entry != null) {
      parts.push(entry.definition.name);
      entry = entry.parent;
    }
    parts.reverse();
    return parts;
  }

  toggleOpen() {
    const self = this;
    if (self.definition.type !== 'dir') {
      return;
    }
    self.open(!self.open());
    if (self.definition.name === '..') {
      if (self.parent.parent) {
        huePubSub.publish('assist.selectGitEntry', self.parent.parent);
      }
    } else {
      huePubSub.publish('assist.selectGitEntry', self);
    }
  }
}

export default AssistGitEntry;

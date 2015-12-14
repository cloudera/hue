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

(function (root, factory) {
  if(typeof define === "function" && define.amd) {
    define(['knockout'], factory);
  } else {
    root.AssistHdfsEntry = factory(ko);
  }
}(this, function (ko) {

  /**
   * @param {object} options
   * @param {object} options.definition
   * @param {string} options.definition.name
   * @param {string} options.definition.type (file, dir)
   * @param {AssistHdfsEntry} options.parent
   * @param {AssistHelper} options.assistHelper
   * @constructor
   */
  function AssistHdfsEntry (options) {
    var self = this;

    self.definition = options.definition;
    self.assistHelper = options.assistHelper;
    self.parent = options.parent;
    self.path = self.parent !== null ? self.parent.path + self.definition.name + '/' : self.definition.name;

    self.entries = ko.observableArray([]);

    self.loading = ko.observable(false);
    self.open = ko.observable(false);

    self.open.subscribe(function(newValue) {
      if (newValue && self.entries().length == 0) {
        self.loadEntries();
      }
    });

    self.hasEntries = ko.computed(function() {
      return self.entries().length > 0;
    });
  }

  AssistHdfsEntry.prototype.loadEntries = function() {
    var self = this;
    if (self.loading()) {
      return;
    }
    self.loading(true);

    var successCallback = function(data) {
      self.entries($.map(data.files, function (file) {
        return new AssistHdfsEntry({
          definition: file,
          parent: self,
          assistHelper: self.assistHelper
        })
      }));
      self.loading(false);
    };

    var errorCallback = function () {
      console.log(data);
      self.loading(false);
    };

    self.assistHelper.fetchHdfsPath(self.getHierarchy(), successCallback, errorCallback)
  };

  AssistHdfsEntry.prototype.getHierarchy = function () {
    var self = this;
    var parts = [];
    var entry = self;
    while (entry != null) {
      parts.push(entry.definition.name);
      entry = entry.parent;
    }
    parts.reverse();
    return parts;
  };

  AssistHdfsEntry.prototype.toggleOpen = function () {
    var self = this;
    if (self.definition.type === 'file') {
      return;
    }
    self.open(!self.open());
    if (self.definition.name === '..') {
      if (self.parent.parent) {
        huePubSub.publish('assist.selectHdfsEntry', self.parent.parent);
      }
    } else {
      huePubSub.publish('assist.selectHdfsEntry', self);
    }
  };

  return AssistHdfsEntry;
}));

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

var AssistS3Entry = (function () {

  var PAGE_SIZE = 50;

  /**
   * @param {object} options
   * @param {object} options.definition
   * @param {string} options.definition.name
   * @param {string} options.definition.type (file, dir)
   * @param {AssistS3Entry} options.parent
   * @param {ApiHelper} options.apiHelper
   * @constructor
   */
  function AssistS3Entry (options) {
    var self = this;

    self.definition = options.definition;
    self.apiHelper = options.apiHelper;
    self.parent = options.parent;
    self.path = '';
    if (self.parent !== null) {
      self.path = self.parent.path;
      if (self.parent.path !== '/') {
        self.path += '/'
      }
    }
    self.path += self.definition.name;
    self.currentPage = 1;
    self.hasMorePages = true;

    self.entries = ko.observableArray([]);

    self.loaded = false;
    self.loading = ko.observable(false);
    self.loadingMore = ko.observable(false);
    self.hasErrors = ko.observable(false);
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

  AssistS3Entry.prototype.dblClick = function () {
    var self = this;
    huePubSub.publish('assist.dblClickS3Item', self);
  };

  AssistS3Entry.prototype.loadEntries = function(callback) {
    var self = this;
    if (self.loading()) {
      return;
    }
    self.loading(true);
    self.hasErrors(false);

    var successCallback = function(data) {
      self.hasMorePages = data.page.next_page_number > self.currentPage;
      var filteredFiles = $.grep(data.files, function (file) {
        return file.name !== '.' && file.name !== '..';
      });
      self.entries($.map(filteredFiles, function (file) {
        return new AssistS3Entry({
          definition: file,
          parent: self,
          apiHelper: self.apiHelper
        })
      }));
      self.loaded = true;
      self.loading(false);
      if (callback) {
        callback();
      }
    };

    var errorCallback = function () {
      self.hasErrors(true);
      self.loading(false);
      if (callback) {
        callback();
      }
    };

    self.apiHelper.fetchS3Path({
      pageSize: PAGE_SIZE,
      page: self.currentPage,
      pathParts: self.getHierarchy(),
      successCallback: successCallback,
      errorCallback: errorCallback
    })
  };

  AssistS3Entry.prototype.loadDeep = function(folders, callback) {
    var self = this;

    if (folders.length === 0) {
      callback(self);
      return;
    }

    var findNextAndLoadDeep = function () {
      var nextName = folders.shift();
      var foundEntry = $.grep(self.entries(), function (entry) {
        return entry.definition.name === nextName && entry.definition.type === 'dir';
      });
      if (foundEntry.length === 1) {
        foundEntry[0].loadDeep(folders, callback);
      } else if (! self.hasErrors()) {
        callback(self);
      }
    };

    if (! self.loaded) {
      self.loadEntries(findNextAndLoadDeep);
    } else {
      findNextAndLoadDeep();
    }
  };

  AssistS3Entry.prototype.getHierarchy = function () {
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

  AssistS3Entry.prototype.toggleOpen = function () {
    var self = this;
    if (self.definition.type === 'file') {
      return;
    }
    self.open(!self.open());
    if (self.definition.name === '..') {
      if (self.parent.parent) {
        huePubSub.publish('assist.selectS3Entry', self.parent.parent);
      }
    } else {
      huePubSub.publish('assist.selectS3Entry', self);
    }
  };

  AssistS3Entry.prototype.fetchMore = function () {
    var self = this;
    if (!self.hasMorePages || self.loadingMore()) {
      return;
    }
    self.currentPage++;
    self.loadingMore(true);
    self.hasErrors(false);
    self.apiHelper.fetchS3Path({
      pageSize: PAGE_SIZE,
      page: self.currentPage,
      pathParts: self.getHierarchy(),
      successCallback: function (data) {
        self.hasMorePages = data.page.next_page_number > self.currentPage;
        var filteredFiles = $.grep(data.files, function (file) {
          return file.name !== '.' && file.name !== '..';
        });
        self.entries(self.entries().concat($.map(filteredFiles, function (file) {
          return new AssistS3Entry({
            definition: file,
            parent: self,
            apiHelper: self.apiHelper
          })
        })));
        self.loadingMore(false);
      },
      errorCallback: function () {
        self.hasErrors(true);
      }
    });
  };

  return AssistS3Entry;
})();

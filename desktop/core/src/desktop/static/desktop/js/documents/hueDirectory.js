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
    define([
      'knockout'
    ], factory);
  } else {
    root.HueDirectory = factory(ko);
  }
}(this, function (ko) {

  /**
   *
   * @param {Object} options
   * @param {AssistHelper} options.assistHelper
   * @param {Object} options.definition
   * @param {HueFolder} options.parent
   * @param {string} options.app - Currently only 'documents' is supported
   *
   * @constructor
   */
  function HueDirectory (options) {
    var self = this;
    self.parent = options.parent;
    self.definition = options.definition;
    self.assistHelper = options.assistHelper;
    self.name = self.definition.name.substring(self.definition.name.lastIndexOf('/') + 1);
    self.isRoot = self.name === '';
    self.path = self.definition.name;
    self.app = options.app;

    self.loaded = ko.observable(false);
    self.loading = ko.observable(false);
    self.hasErrors = ko.observable(false);
    self.open = ko.observable(false);
    self.entries = ko.observableArray([]);

    self.breadcrumbs = [];
    var lastParent = self.parent;
    while (lastParent) {
      self.breadcrumbs.unshift(lastParent);
      lastParent = lastParent.parent;
    }

    self.open.subscribe(function () {
      if (! self.loaded()) {
        self.load();
      }
    })
  }

  HueDirectory.prototype.load = function () {
    var self = this;
    if (self.loading()) {
      return;
    }
    self.loading(true);

    if (self.app === 'documents') {
      self.assistHelper.fetchDocuments({
        path: self.path,
        successCallback: function(data) {
          self.hasErrors(false);
          var cleanEntries = $.grep(data.documents, function (definition) {
            return definition.name !== '/';
          });
          self.entries($.map(cleanEntries, function (definition) {
            if (definition.type === "directory") {
              return new HueDirectory({
                assistHelper: self.assistHelper,
                definition: definition,
                app: self.app,
                parent: self
              })
            } else {
              return {
                definition: definition,
                path: self.path + definition.name
              }
            }
          }));
          self.loading(false);
          self.loaded(true);
        },
        errorCallback: function () {
          self.hasErrors(true);
          self.loading(false);
          self.loaded(true);
        }
      });
    }
  };

  HueDirectory.prototype.delete = function () {
    var self = this;
    if (self.app === 'documents') {
      self.assistHelper.deleteDocument({
        successCallback: self.parent.load.bind(self.parent),
        id: self.definition.id
      });
    }
  };

  HueDirectory.prototype.createDirectory = function (name) {
    var self = this;
    if (self.app === 'documents') {
      self.assistHelper.createDocumentsFolder({
        successCallback: self.load.bind(self),
        path: self.path,
        name: name
      });
    }
  };

  return HueDirectory;
}));

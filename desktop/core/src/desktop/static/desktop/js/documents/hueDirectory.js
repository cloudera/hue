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
   *
   * @constructor
   */
  function HueDirectory (options) {
    var self = this;
    self.parent = options.parent;
    self.definition = options.definition;
    self.assistHelper = options.assistHelper;
    self.path = self.parent ? self.parent.path + self.definition.name : self.definition.name;

    self.loaded = ko.observable(false);
    self.loading = ko.observable(false);
    self.hasErrors = ko.observable(false);
    self.open = ko.observable(false);
    self.entries = ko.observableArray([]);

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

    self.assistHelper.fetchDocuments({
      successCallback: function(data) {
        self.hasErrors(false);
        self.entries($.map(data.documents, function (definition) {
          if (definition.type === "directory") {
            return new HueDirectory({
              assistHelper: self.assistHelper,
              definition: definition,
              parent: self
            })
          } else {
            return {
              definition: definition,
              path: self.path + definition.name
            }
          }
        }));
        $.each(data.documents, function (idx, document) {
          console.log(document);
        });
        self.loading(false);
        self.loaded(true);
      },
      errorCallback: function () {
        self.hasErrors(true);
        self.loading(false);
        self.loaded(true);
      }
    });
  };

  return HueDirectory;
}));

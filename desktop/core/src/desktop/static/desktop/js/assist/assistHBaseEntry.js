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

var AssistHBaseEntry = (function () {

  /**
   * @param {object} options
   * @param {object} options.definition
   * @param {string} options.definition.name
   * @param {ApiHelper} options.apiHelper
   * @constructor
   */
  function AssistHBaseEntry (options) {
    var self = this;

    self.definition = options.definition;
    self.apiHelper = options.apiHelper;
    self.path = self.definition.name;

    self.entries = ko.observableArray([]);

    self.loaded = false;
    self.loading = ko.observable(false);
    self.hasErrors = ko.observable(false);

    self.hasEntries = ko.computed(function() {
      return self.entries().length > 0;
    });
  }

  AssistHBaseEntry.prototype.loadEntries = function(callback) {
    var self = this;
    if (self.loading()) {
      return;
    }
    self.loading(true);
    self.hasErrors(false);

    var successCallback = function(data) {
      self.entries($.map(data.data, function (obj) {
        return new AssistHBaseEntry({
          definition: obj,
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

    self.apiHelper.fetchHBase({
      parent: self.definition,
      successCallback: successCallback,
      errorCallback: errorCallback
    })
  };

  AssistHBaseEntry.prototype.open = function () {
    huePubSub.publish('assist.clickHBaseItem', this);
  };

  AssistHBaseEntry.prototype.click = function () {
    huePubSub.publish('assist.clickHBaseItem', this);
  };

  AssistHBaseEntry.prototype.dblClick = function () {
    huePubSub.publish('assist.dblClickHBaseItem', this);
  };

  return AssistHBaseEntry;
})();

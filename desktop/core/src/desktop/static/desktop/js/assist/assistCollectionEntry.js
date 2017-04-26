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

var AssistCollectionEntry = (function () {

  /**
   * @param {object} options
   * @param {object} options.definition
   * @param {string} options.definition.name
   * @param {ApiHelper} options.apiHelper
   * @constructor
   */
  function AssistCollectionEntry (options, filter, showCores) {
    var self = this;

    self.definition = options.definition;
    self.apiHelper = options.apiHelper;
    self.path = self.definition.name;
    self.filter = filter;
    self.showCores = showCores;

    self.entries = ko.observableArray([]);
    self.filteredEntries = ko.pureComputed(function(){
      var result = [];
      $.each(self.entries(), function (index, entry) {
        if (entry.definition.name.toLowerCase().indexOf(self.filter().toLowerCase()) > -1){
          if (self.showCores() || (!self.showCores() && !entry.definition.isCoreOnly)){
            result.push(entry);
          }
        }
      });
      return result;
    });

    self.loaded = false;
    self.loading = ko.observable(false);
    self.hasErrors = ko.observable(false);

    self.hasOnlyCores = ko.computed(function () {
      return ko.utils.arrayFilter(self.filteredEntries(), function (entry) {
          return entry.definition.isCoreOnly;
        }).length === self.filteredEntries().length;
    });

    self.hasEntries = ko.computed(function() {
      return self.entries().length > 0;
    });
  }

  AssistCollectionEntry.prototype.loadEntries = function(callback) {
    var self = this;
    if (self.loading()) {
      return;
    }
    self.loading(true);
    self.hasErrors(false);

    var successCallback = function(data) {
      self.entries($.map(data.collections, function (collection) {
        return new AssistCollectionEntry({
          definition: collection,
          apiHelper: self.apiHelper
        }, self.filter, self.showCores)
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

    self.apiHelper.fetchSolrCollections({
      successCallback: successCallback,
      errorCallback: errorCallback
    })
  };

  AssistCollectionEntry.prototype.open = function () {
    huePubSub.publish('assist.clickCollectionItem', this);
  };

  AssistCollectionEntry.prototype.click = function () {
    huePubSub.publish('assist.clickCollectionItem', this);
  };

  AssistCollectionEntry.prototype.dblClick = function () {
    huePubSub.publish('assist.dblClickCollectionItem', this);
  };

  return AssistCollectionEntry;
})();

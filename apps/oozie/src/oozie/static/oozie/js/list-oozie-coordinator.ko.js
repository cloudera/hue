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

var RunningCoordinatorModel = (function () {

  var RunningCoordinatorModel = function (actions) {

    var self = this;

    self.Action = function (action) {
      return {
        id: action.id,
        url: action.url,
        number: action.number,
        type: action.type,
        status: action.status,
        statusClass: "label " + getStatusClass(action.status),
        externalId: action.externalId,
        externalIdUrl: action.externalIdUrl,
        title: action.title,
        nominalTime: action.nominalTime,
        createdTime: action.createdTime,
        lastModifiedTime: action.lastModifiedTime,
        errorMessage: action.errorMessage,
        errorCode: action.errorCode,
        missingDependencies: action.missingDependencies,
        selected: ko.observable(false),
        handleSelect: function (row, e) {
          e.stopPropagation();
          this.selected(!this.selected());
          self.allSelected(false);
        }
      };
    };

    self.isLoading = ko.observable(true);

    self.actions = ko.observableArray(ko.utils.arrayMap(actions, function (action) {
      return new self.Action(action);
    }));

    self.setActions = function (actions) {
      self.actions(ko.utils.arrayMap(actions, function (action) {
        return new self.Action(action);
      }));
    }

    self.allSelected = ko.observable(false);

    self.filter = ko.observableArray([]);

    self.searchFilter = ko.observable("");

    self.isRefreshingLogs = ko.observable(false);
    self.logFilterRecentHours = ko.observable("");
    self.logFilterRecentMinutes = ko.observable("");
    self.logFilterRecent = ko.computed(function () {
      var _h = self.logFilterRecentHours();
      var _m = self.logFilterRecentMinutes();
      return (_h != "" ? _h + "h" : "") + (_h != "" && _m != "" ? ":" : "") + (_m != "" ? _m + "m" : "");
    }).extend({throttle: 500});

    self.logFilterLimit = ko.observable("5000").extend({throttle: 500});

    self.logFilterText = ko.observable("").extend({throttle: 500});

    self.logFilterRecent.subscribe(function () {
      refreshLogs();
    });

    self.logFilterLimit.subscribe(function () {
      refreshLogs();
    });

    self.logFilterText.subscribe(function () {
      refreshLogs();
    });

    self.isLogFilterVisible = ko.observable(false);

    self.toggleLogFilterVisible = function () {
      self.isLogFilterVisible(!self.isLogFilterVisible());
    };

    self.select = function (filter) {
      ko.utils.arrayFilter(self.actions(), function (action) {
        if (action.status.toLowerCase() === filter) {
          action.selected(true);
        }
      });
    };

    self.clearAllSelections = function () {
      ko.utils.arrayFilter(self.actions(), function (action) {
        action.selected(false);
      });
      self.allSelected(false);
    };

    self.clearSelections = function (filter) {
      ko.utils.arrayFilter(self.actions(), function (action) {
        if (action.status.toLowerCase() === filter) {
          action.selected(false);
        }
      });
      self.allSelected(false);
    };

    self.selectAll = function () {
      var regexp;

      if (!Array.isArray(self.filter())) {
        ko.utils.arrayForEach(self.actions(), function (action) {
          regexp = new RegExp(self.filter());

          self.allSelected(!self.allSelected());

          if (regexp.test(action.title.toLowerCase())) {
            action.selected(!action.selected());
          }
        });
        return true;
      }

      self.allSelected(!self.allSelected());

      ko.utils.arrayForEach(self.actions(), function (action) {
        if (action.id) {
          action.selected(self.allSelected());
        }
      });
      return true;
    };

    self.selectedActions = ko.computed(function () {
      var actionlist = [];

      ko.utils.arrayFilter(self.actions(), function (action) {
        if (action.selected()) {
          actionlist.push(action.number.toString());
        }
      });
      return actionlist;
    });

    self.searchFilter.subscribe(function () {
      if (self.searchFilter().length === 0) {
        self.filter([]);
      } else {
        self.filter(self.searchFilter().toLowerCase());
      }

      if (self.selectedActions().length === self.actions().length) {
        self.allSelected(true);
      } else {
        self.allSelected(false);
      }
    });

    self.filteredActions = ko.pureComputed(function () {
      var filter = self.filter(),
        actions = [],
        regexp,
        data;

      if (self.filter().length === 0) {
        return self.actions();
      }

      ko.utils.arrayFilter(self.actions(), function (action) {
        if ($.inArray(filter.toString(), ['succeeded', 'running', 'failed']) === -1) {
          regexp = new RegExp(filter);
          if (regexp.test(action.title.toLowerCase())) {
            actions.push(action);
          }
        }
      });

      if (Array.isArray(self.filter())) {
        data = self.actions()
      } else {
        data = actions;
      }

      return data;
    });
  };

  return RunningCoordinatorModel;
})();

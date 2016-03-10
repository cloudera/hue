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
    root.TableStats = factory(ko);
  }
}(this, function (ko) {

  /**
   *
   * @param {Object} options
   * @param {Object} options.i18n
   * @param {string} options.i18n.errorLoadingStats
   * @param {string} options.i18n.errorLoadingTerms
   * @param {string} options.i18n.errorRefreshingStats
   * @param {AssistHelper} options.assistHelper
   * @param {string} options.sourceType
   * @param {string} options.databaseName
   * @param {string} options.tableName
   * @param {string} options.columnName
   * @param {string} options.type
   * @constructor
   */
  function TableStats (options) {
    var self = this;
    self.i18n = options.i18n;
    self.sourceType = options.sourceType;
    self.database = options.databaseName;
    self.table = options.tableName;
    self.column = options.columnName;
    self.assistHelper = options.assistHelper;
    self.type = options.type;
    self.isComplexType = /^(map|array|struct)/i.test(options.type);
    self.isView = /view/i.test(options.type);

<<<<<<< HEAD
    self.loading = ko.observable(false);
    self.hasError = ko.observable(false);
=======
    self.loadingStats = ko.observable(false);
    self.statsHasError = ko.observable(false);
>>>>>>> upstream/master
    self.refreshing = ko.observable(false);
    self.loadingTerms = ko.observable(false);
    self.inaccurate = ko.observable(false);
    self.statRows = ko.observableArray();
    self.terms = ko.observableArray();
    self.termsTabActive = ko.observable(false);
    self.prefixFilter = ko.observable().extend({'throttle': 500});

<<<<<<< HEAD
=======
    self.activeTab = ko.observable("sample");
    self.loadingSamples = ko.observable(false);
    self.samples = ko.observable(null);

    self.activeTab.subscribe(function (newValue) {
      if (newValue === "analysis" && self.statRows().length === 0) {
        self.fetchData();
      }
    });

>>>>>>> upstream/master
    self.prefixFilter.subscribe(function (newValue) {
      self.fetchTerms();
    });

    self.termsTabActive.subscribe(function (newValue) {
      if (self.terms().length == 0 && newValue) {
        self.fetchTerms();
      }
    });

<<<<<<< HEAD
    self.fetchData();
=======
    if (typeof self.column === 'undefined' || self.column === null) {
      self.fetchSamples();
    } else {
      self.fetchData();
    }
>>>>>>> upstream/master
  }

  TableStats.prototype.fetchData = function () {
    var self = this;
<<<<<<< HEAD
    self.loading(true);
    self.hasError(false);
=======
    self.loadingStats(true);
    self.statsHasError(false);
>>>>>>> upstream/master

    var successCallback = function (data) {
      if (data && data.status == 0) {
        self.statRows(data.stats);
        var inaccurate = true;
        for(var i = 0; i < data.stats.length; i++) {
          if (data.stats[i].data_type == "COLUMN_STATS_ACCURATE" && data.stats[i].comment == "true") {
            inaccurate = false;
            break;
          }
        }
        self.inaccurate(inaccurate);
      } else if (data && data.message) {
        $(document).trigger("error", data.message);
<<<<<<< HEAD
        self.hasError(true);
      } else {
        $(document).trigger("error", self.i18n.errorLoadingStats);
        self.hasError(true);
      }
      self.loading(false);
    };

    var errorCallback = function (e) {
      self.hasError(true);
      self.loading(false);
=======
        self.statsHasError(true);
      } else {
        $(document).trigger("error", self.i18n.errorLoadingStats);
        self.statsHasError(true);
      }
      self.loadingStats(false);
    };

    var errorCallback = function (e) {
      self.statsHasError(true);
      self.loadingStats(false);
>>>>>>> upstream/master
    };

    self.assistHelper.fetchStats({
      sourceType: self.sourceType === "hive" ? "beeswax" : self.sourceType,
      databaseName: ko.isObservable(self.database) ? self.database() : self.database,
      tableName: ko.isObservable(self.table) ? self.table() : self.table,
      columnName: ko.isObservable(self.column) ? self.column() : self.column,
      successCallback: successCallback,
      errorCallback: errorCallback
    });
  };

  TableStats.prototype.refresh = function () {
    var self = this;
    if (self.refreshing()) {
      return;
    }
<<<<<<< HEAD
    var shouldFetchTerms = self.termsTabActive() || self.terms().length > 0;
    self.refreshing(true);

    self.assistHelper.refreshTableStats({
      sourceType: self.sourceType === "hive" ? "beeswax" : self.sourceType,
      databaseName: ko.isObservable(self.database) ? self.database() : self.database,
      tableName: ko.isObservable(self.table) ? self.table() : self.table,
      columnName: ko.isObservable(self.column) ? self.column() : self.column,
      successCallback: function() {
        self.refreshing(false);
        self.fetchData();
        if (shouldFetchTerms) {
          self.fetchTerms();
        }
      },
      errorCallback: function(message) {
        self.refreshing(false);
        $(document).trigger("error", message || self.i18n.errorRefreshingStats);
      }
    });
=======
    self.refreshing(true);

    if (self.activeTab() === "sample") {
      self.samples(null);
      self.fetchSamples();
    } else {
      var shouldFetchTerms = self.termsTabActive() || self.terms().length > 0;
      self.assistHelper.refreshTableStats({
        sourceType: self.sourceType === "hive" ? "beeswax" : self.sourceType,
        databaseName: ko.isObservable(self.database) ? self.database() : self.database,
        tableName: ko.isObservable(self.table) ? self.table() : self.table,
        columnName: ko.isObservable(self.column) ? self.column() : self.column,
        successCallback: function() {
          self.refreshing(false);
          self.fetchData();
          if (shouldFetchTerms) {
            self.fetchTerms();
          }
        },
        errorCallback: function(message) {
          self.refreshing(false);
          $(document).trigger("error", message || self.i18n.errorRefreshingStats);
        }
      });
    }
>>>>>>> upstream/master
  };

  TableStats.prototype.fetchTerms = function () {
    var self = this;
    if ((ko.isObservable(self.column) && self.column() == null) || self.column == null || (self.isComplexType && self.sourceType == "impala")) {
      return;
    }

    self.loadingTerms(true);
    self.assistHelper.fetchTerms({
      sourceType: self.sourceType === "hive" ? "beeswax" : self.sourceType,
      databaseName: ko.isObservable(self.database) ? self.database() : self.database,
      tableName: ko.isObservable(self.table) ? self.table() : self.table,
      columnName: ko.isObservable(self.column) ? self.column() : self.column,
      prefixFilter: self.prefixFilter(),
      successCallback: function (data) {
        if (data && data.status == 0) {
          self.terms($.map(data.terms, function (term) {
            return {
              name: term[0],
              count: term[1],
              percent: (parseFloat(term[1]) / parseFloat(data.terms[0][1])) * 100
            }
          }));
        } else if (data && data.message) {
          $(document).trigger("error", data.message);
        } else {
          $(document).trigger("error", self.i18n.errorLoadingTerms);
        }
        self.loadingTerms(false);
      },
      errorCallback: function (e) {
        self.loadingTerms(false);
      }
    });
  };

<<<<<<< HEAD
=======
  TableStats.prototype.fetchSamples = function () {
    var self = this;
    if (self.loadingSamples()) {
      return;
    }

    self.loadingSamples(true);
    self.samples({});

    self.assistHelper.fetchTableSample({
      sourceType: self.sourceType,
      databaseName: ko.isObservable(self.database) ? self.database() : self.database,
      tableName: ko.isObservable(self.table) ? self.table() : self.table,
      successCallback: function(data) {
        if (! data.rows) {
          data.rows = [];
        } else if (! data.headers) {
          data.headers = [];
        }
        self.samples(data);
        self.loadingSamples(false);
        self.refreshing(false);
      },
      errorCallback: function() {
        self.loadingSamples(false);
        self.refreshing(false);
      }
    });
  };

>>>>>>> upstream/master
  return TableStats;
}));

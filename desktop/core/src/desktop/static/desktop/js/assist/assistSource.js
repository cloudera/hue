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
    define(['knockout', 'desktop/js/assist/assistEntry'], factory);
  } else {
    root.AssistSource = factory(ko, AssistEntry);
  }
}(this, function (ko, AssistEntry) {

  function AssistSource(snippet, i18n) {
    var self = this;
    self.name = snippet.name();
    self.i18n = i18n;
    self.snippet = snippet;
    self.assistHelper = snippet.getAssistHelper();

    self.hasErrors = ko.observable(false);
    self.simpleStyles = ko.observable(false);

    self.filter = ko.observable("").extend({ rateLimit: 150 });

    self.filterActive = ko.computed(function () {
      return self.filter().length !== 0;
    });

    self.options = ko.mapping.fromJS($.extend({
      isSearchVisible: false
    }, $.totalStorage(snippet.type() + ".assist.options") || {}));

    $.each(Object.keys(self.options), function (index, key) {
      if (ko.isObservable(self.options[key])) {
        self.options[key].subscribe(function() {
          $.totalStorage(snippet.type() + ".assist.options", ko.mapping.toJS(self.options))
        });
      }
    });

    self.databases = ko.observableArray();
    self.selectedDatabase = ko.observable();

    self.reloading = ko.observable(false);

    self.loadingTables = ko.computed(function() {
      return typeof self.selectedDatabase() != "undefined" && self.selectedDatabase() !== null && self.selectedDatabase().loading();
    });

    self.selectedDatabase.subscribe(function (newValue) {
      if (newValue != null && !newValue.hasEntries() && !newValue.loading()) {
        newValue.loadEntries()
      }
    });

    var dbIndex = {};
    var updateDatabases = function (names) {
      dbIndex = {};
      self.databases($.map(names, function(name) {
        var database = new AssistEntry({
          name: name,
          displayName: name,
          title: name,
          isDatabase: true
        }, null, self, self.filter, self.i18n);
        dbIndex[name] = database;
        return database;
      }));
    };

    if (dbIndex[self.assistHelper.activeDatabase()]) {
      self.selectedDatabase(dbIndex[self.assistHelper.activeDatabase()]);
    }

    var subscribed = false;

    var updateDbFromAssistHelper = function () {
      var assistDb = self.assistHelper.activeDatabase();
      if (dbIndex[assistDb] && (! self.selectedDatabase() || self.selectedDatabase().name !== assistDb)) {
        self.selectedDatabase(dbIndex[assistDb]);
      }
    };

    self.assistHelper.activeDatabase.subscribe(function (newValue) {
      updateDbFromAssistHelper();
    });

    var initDatabases = function () {
      if (self.assistHelper.loaded()) {
        updateDatabases(self.assistHelper.availableDatabases());
        updateDbFromAssistHelper();
      }
    };

    self.assistHelper.loaded.subscribe(function (newValue) {
      if (newValue) {
        initDatabases();
      }
    });

    initDatabases();

    self.selectedDatabase.subscribe(function (newDatabase) {
      if (newDatabase !== null) {
        self.assistHelper.activeDatabase(newDatabase.definition.name);
      }
    });

    self.modalItem = ko.observable();
    self.analysisStats = ko.observable();

    var lastOffset = { top: -1, left: -1 };
    self.refreshPosition = function () {
      if (self.analysisStats() == null) {
        return;
      }
      var $tableAnalysis = $("#tableAnalysis");
      var targetElement = $tableAnalysis.data("targetElement");
      if (targetElement != null && targetElement.is(":visible")) {
        var newTop = targetElement.offset().top - $(window).scrollTop();
        if (targetElement != null && (lastOffset.left != targetElement.offset().left || lastOffset.top != newTop)) {
          lastOffset.left = targetElement.offset().left;
          lastOffset.top = newTop;
          var newCssTop = lastOffset.top - $tableAnalysis.outerHeight() / 2 + targetElement.outerHeight() / 2;
          $tableAnalysis.css("top", newCssTop).css("left", lastOffset.left + targetElement.outerWidth());
          if ((newCssTop + $tableAnalysis.outerHeight() / 2) < 70) {
            $tableAnalysis.hide();
          } else {
            $tableAnalysis.show();
          }
        }
      } else {
        $tableAnalysis.hide();
      }
    };
    window.setInterval(self.refreshPosition, 200);

    self.repositionActions = function(data, event) {
      if (data.definition.isDatabase) {
        var $container = $(event.target);
        $container.find(".assist-actions").css('right', -$container.scrollLeft() + 'px');
      }
    };
  }

  AssistSource.prototype.reloadAssist = function() {
    var self = this;
    self.reloading(true);
    self.selectedDatabase(null);
    self.assistHelper.clearCache(self.snippet);
    self.assistHelper.load(self.snippet, function() {
      self.reloading(false);
    });
  };

  return AssistSource;
}));

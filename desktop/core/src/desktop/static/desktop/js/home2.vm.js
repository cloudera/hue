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
      'knockout',
      'desktop/js/assist/assistHelper',
      'desktop/js/fileBrowser/hueFileEntry',
      'knockout-mapping'
    ], factory);
  } else {
    root.HomeViewModel = factory(ko, assistHelper, HueFileEntry);
  }
}(this, function (ko, AssistHelper, HueFileEntry) {

  function HomeViewModel(options) {
    var self = this;

    self.assistHelper = AssistHelper.getInstance(options);
    self.isLeftPanelVisible = ko.observable();
    self.assistHelper.withTotalStorage('assist', 'assist_panel_visible', self.isLeftPanelVisible, true);

    self.activeEntry = ko.observable();
    self.trashEntry = ko.observable();
    self.activeEntry(new HueFileEntry({
      activeEntry: self.activeEntry,
      trashEntry: self.trashEntry,
      assistHelper: self.assistHelper,
      app: 'documents',
      definition: {
        name: '/'
      }
    }));

    self.shareFormDocId = ko.observable('');
    self.exportFormDocIds = ko.observable('');

    self.exportDocuments = function() {
      $('#export-documents').find('input[name=\'documents\']').val(ko.mapping.toJSON(self.exportFormDocIds().split(",")));
      $('#export-documents').find('form').submit();
    };
  }

  HomeViewModel.prototype.openUuid = function (uuid) {
    var self = this;
    self.activeEntry(undefined);
    var entry = new HueFileEntry({
      activeEntry: self.activeEntry,
      trashEntry: self.trashEntry,
      assistHelper: self.assistHelper,
      app: 'documents',
      definition: {
        uuid: location.getParameter('uuid'),
        name: 'unknown',
        type: 'directory',
        path: '/unknown'
      }
    });

    var lastParent = entry;

    var loadParents = function () {
      if (lastParent.parent) {
        lastParent = lastParent.parent;
        lastParent.load(loadParents);
      } else {
        self.activeEntry(entry);
      }
    };

    entry.load(loadParents);
  };

  HomeViewModel.prototype.openPath = function (path) {
    var self = this;
    var parts = path.split('/');
    parts.shift(); // Remove root
    self.activeEntry(undefined);
    var lastChild = new HueFileEntry({
      activeEntry: self.activeEntry,
      trashEntry: self.trashEntry,
      assistHelper: self.assistHelper,
      app: 'documents',
      definition: {
        name: '',
        type: 'directory',
        path: '/'
      }
    });

    var loadDeep = function () {
      if (parts.length > 0) {
        var targetDir = parts.shift();
        var foundDirs = $.grep(lastChild.entries(), function (entry) {
          return entry.definition().name === targetDir;
        });
        if (foundDirs.length === 1) {
          lastChild = foundDirs[0];
          lastChild.load(loadDeep);
          return;
        }
      }
      self.activeEntry(lastChild);
    };

    lastChild.load(loadDeep);
  };

  return HomeViewModel;
}));

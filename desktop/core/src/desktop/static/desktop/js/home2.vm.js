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

var HomeViewModel = (function () {

  /**
   * @param {Object} options
   * @param {string} options.user
   * @param {Object} options.i18n
   *
   * @constructor
   */
  function HomeViewModel(options) {
    var self = this;

    self.user = options.user;
    self.superuser = options.superuser;
    self.apiHelper = window.apiHelper;
    self.isLeftPanelVisible = ko.observable(false);
    // Uncomment to enable the assist panel
    // self.apiHelper.withTotalStorage('assist', 'assist_panel_visible', self.isLeftPanelVisible, true);

    self.serverTypeFilter = ko.observable();

    var initialType = window.location.getParameter('type') !== '' ? window.location.getParameter('type') : 'all';

    DOCUMENT_TYPES.some(function (docType) {
      if (docType.type === initialType) {
        self.serverTypeFilter(docType);
        return true;
      }
    });

    if (!self.serverTypeFilter()) {
      self.serverTypeFilter(DOCUMENT_TYPES[0]);
    }

    self.activeEntry = ko.observable();
    self.trashEntry = ko.observable();

    self.defaultFileEntry = new HueFileEntry({
      serverTypeFilter: self.serverTypeFilter,
      activeEntry: self.activeEntry,
      trashEntry: self.trashEntry,
      apiHelper: self.apiHelper,
      app: 'documents',
      user: self.user,
      superuser: self.superuser,
      activeSort: ko.observable('defaultAsc'),
      definition: {
        name: '/'
      }
    });

    self.activeEntry(self.defaultFileEntry);

    self.serverTypeFilter.subscribe(function (newVal) {
      if (self.activeEntry()) {
        self.activeEntry().entries([]);
        self.activeEntry().load();
        if (!newVal || newVal.type === 'all') {
          if (location.getParameter('type')) {
            hueUtils.removeURLParameter('type');
          }
        } else {
          if (!location.getParameter('type') || location.getParameter('type') !== newVal.type) {
            hueUtils.changeURLParameter('type', newVal.type);
          }
        }
      }
    });

    self.shareFormDocId = ko.observable('');
    self.exportFormDocIds = ko.observable('');

    self.exportDocuments = function() {
      $('#export-documents').find('input[name=\'documents\']').val(ko.mapping.toJSON(self.exportFormDocIds().split(",")));
      $('#export-documents').find('form').submit();
    };
  }

  HomeViewModel.prototype.openUuid = function (uuid) {
    var self = this;
    var entry = self.activeEntry().createNewEntry({
      definition: {
        uuid: uuid || location.getParameter('uuid'),
        name: 'unknown',
        type: 'directory',
        path: '/unknown'
      },
      parent: null
    });
    self.activeEntry(undefined);

    var lastParent = entry;

    var openDefault = function () {
      self.activeEntry(self.defaultFileEntry);
      self.activeEntry().load();
    }

    var loadParents = function () {
      if (lastParent.parent) {
        lastParent = lastParent.parent;
        lastParent.load(loadParents, openDefault);
      } else {
        self.activeEntry(entry);
      }
    };

    entry.load(loadParents, openDefault);
  };

  HomeViewModel.prototype.openPath = function (path) {
    var self = this;
    var parts = path.split('/');
    parts.shift(); // Remove root
    var lastChild = self.activeEntry().createNewEntry({
      definition: {
        name: '',
        type: 'directory',
        path: '/'
      },
      parent: null
    });
    self.activeEntry(undefined);

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
})();

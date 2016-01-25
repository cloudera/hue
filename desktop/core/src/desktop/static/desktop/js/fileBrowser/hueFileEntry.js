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
      'desktop/js/fileBrowser/hueDocument'
    ], factory);
  } else {
    root.HueFileEntry = factory(ko);
  }
}(this, function (ko, HueDocument) {

  /**
   *
   * @param {Object} options
   * @param {AssistHelper} options.assistHelper
   * @param {Object} options.definition
   * @param {Function} options.activeEntry - The observable keeping track of the current open directory
   * @param {HueFolder} options.parent
   * @param {string} options.app - Currently only 'documents' is supported
   *
   * @constructor
   */
  function HueFileEntry (options) {
    var self = this;
    self.activeEntry = options.activeEntry;
    self.parent = options.parent;
    self.definition = options.definition;
    self.assistHelper = options.assistHelper;
    self.name = self.definition.name.substring(self.definition.name.lastIndexOf('/') + 1);
    self.isRoot = self.name === '';
    self.isDirectory = self.definition.type === 'directory';
    self.path = self.definition.name;
    self.app = options.app;

    self.document = ko.observable();

    self.entriesToDelete = ko.observableArray();

    self.selected = ko.observable(false);

    self.loaded = ko.observable(false);
    self.loading = ko.observable(false);
    self.hasErrors = ko.observable(false);

    self.uploading = ko.observable(false);
    self.uploadComplete = ko.observable(false);
    self.uploadFailed = ko.observable(false);

    self.entries = ko.observableArray([]);

    self.selectedEntries = ko.pureComputed(function () {
      return $.grep(self.entries(), function (entry) {
        return entry.selected();
      });
    });

    self.selectedEntry = ko.pureComputed(function () {
      if (self.selectedEntries().length === 1) {
        return self.selectedEntries()[0];
      }
      return null;
    });

    self.breadcrumbs = [];
    var lastParent = self.parent;
    while (lastParent) {
      self.breadcrumbs.unshift(lastParent);
      lastParent = lastParent.parent;
    }
  }

  HueFileEntry.prototype.beforeContextOpen = function () {
    var self = this;
    if (! self.selected()) {
      $.each(self.parent.selectedEntries(), function (idx, entry) {
        entry.selected(false);
      });
      self.selected(true);
    }
  };

  HueFileEntry.prototype.showSharingModal = function () {
    var self = this;
    if (self.selectedEntry()) {
      if (! self.selectedEntry().document()) {
        self.selectedEntry().loadDocument();
      }
      $('#shareDocumentModal').modal('show');
    }
  };

  HueFileEntry.prototype.loadDocument = function () {
    var self = this;
    self.document(new HueDocument({
      assistHelper: self.assistHelper,
      fileEntry: self
    }));
    self.document().load();
  };

  /**
   * @param {HueFileEntry[]} entries
   */
  HueFileEntry.prototype.moveHere = function (entries) {
    var self = this;
    if (self.app === "documents") {
      var moveNext = function () {
        if (entries.length > 0) {
          var nextId = entries.shift().definition.id;
          self.assistHelper.moveDocument({
            successCallback: function () {
              moveNext();
            },
            errorCallback: function () {
              self.activeEntry().load();
            },
            sourceId: nextId,
            destinationId: self.definition.id
          });
        } else {
          if (self !== self.activeEntry()) {
            self.load();
          }
          self.activeEntry().load();
        }
      };
    };
    moveNext();
  };

  HueFileEntry.prototype.toggleSelected = function () {
    var self = this;
    self.selected(! self.selected());
  };

  HueFileEntry.prototype.open = function () {
    var self = this;
    if (self.definition.type === 'directory') {
      self.makeActive();
      if (! self.loaded()) {
        self.load();
      }
    } else {
      window.location.href = self.definition.absoluteUrl;
    }
  };

  HueFileEntry.prototype.load = function (callback) {
    var self = this;
    if (self.loading()) {
      return;
    }
    self.loading(true);

    if (self.app === 'documents') {
      self.assistHelper.fetchDocuments({
        path: self.path,
        successCallback: function(data) {
          self.definition = data.directory;
          self.hasErrors(false);
          self.entries($.map(data.documents, function (definition) {
            return new HueFileEntry({
              activeEntry: self.activeEntry,
              assistHelper: self.assistHelper,
              definition: definition,
              app: self.app,
              parent: self
            })
          }));
          if (! self.parent && data.parent) {
            self.parent = new HueFileEntry({
              activeEntry: self.activeEntry,
              assistHelper: self.assistHelper,
              definition: data.parent,
              app: self.app,
              parent: null
            });
          }
          self.loading(false);
          self.loaded(true);
          if (callback && typeof callback === 'function') {
            callback();
          }
        },
        errorCallback: function () {
          self.hasErrors(true);
          self.loading(false);
          self.loaded(true);
        }
      });
    }
  };

  HueFileEntry.prototype.showDeleteConfirmation = function () {
    var self = this;
    if (self.selectedEntries().length > 0 ) {
      self.entriesToDelete(self.selectedEntries());
      $('#deleteEntriesModal').modal('show');
    }
  };

  HueFileEntry.prototype.performDelete = function () {
    var self = this;
    if (self.app === 'documents') {
      if (self.entriesToDelete().indexOf(self) !== -1) {
        self.activeEntry(self.parent);
      }

      var deleteNext = function () {
        if (self.entriesToDelete().length > 0) {
          var nextId = self.entriesToDelete().shift().definition.id;
          self.assistHelper.deleteDocument({
            successCallback: function () {
              deleteNext();
            },
            errorCallback: function () {
              self.activeEntry().load();
            },
            id: nextId
          });
        } else {
          self.activeEntry().load();
        }
      };
    };
    deleteNext();
    $('#deleteEntriesModal').modal('hide');
  };


  HueFileEntry.prototype.closeUploadModal = function () {
    var self = this;
    if (self.app === 'documents') {
      $('#importDocumentsModal').modal('hide');
      $('#importDocumentInput').val('');
    }
    // Allow the modal to hide
    window.setTimeout(function () {
      self.uploading(false);
      self.uploadComplete(false);
      self.uploadFailed(false);
    }, 400);
  };

  HueFileEntry.prototype.upload = function () {
    var self = this;
    if (self.app === 'documents') {
      self.uploading(true);
      self.uploadComplete(false);
      self.uploadFailed(false);
      self.assistHelper.uploadDocument({
        formData: new FormData($('#importDocumentsForm')[0]),
        successCallback: function () {
          self.uploading(false);
          self.uploadComplete(true);
          self.load();
        },
        progressHandler: function (event) {
          $("#importDocumentsProgress").val(Math.round((event.loaded / event.total) * 100));
        },
        errorCallback: function () {
          self.uploading(false);
          self.uploadComplete(true);
          self.uploadFailed(true);
        }
      });
    }
  };

  HueFileEntry.prototype.makeActive = function () {
    var self = this;
    self.activeEntry(this);
  };

  HueFileEntry.prototype.showUploadModal = function () {
    if (self.app = 'documents') {
      $('#importDocumentsModal').modal('show');
    }
  };

  HueFileEntry.prototype.contextMenuDownload = function () {
    var self = this;
    if (self.selected()) {
      self.parent.download();
    } else {
      self.downloadThis();
    }
  };

  HueFileEntry.prototype.downloadThis = function () {
    var self = this;
    window.location.href = '/desktop/api2/doc/export?documents=' + ko.mapping.toJSON([ self.definition.id ]);
  };

  HueFileEntry.prototype.download = function () {
    var self = this;
    if (self.app = 'documents') {
      if (self.selectedEntries().length > 0) {
        var ids = self.selectedEntries().map(function (entry) {
          return entry.definition.id;
        })
        window.location.href = '/desktop/api2/doc/export?documents=' + ko.mapping.toJSON(ids);
      } else {
        self.downloadThis();
      }
    };
  };

  HueFileEntry.prototype.createDirectory = function (name) {
    var self = this;
    if (self.app === 'documents') {
      self.assistHelper.createDocumentsFolder({
        successCallback: self.load.bind(self),
        path: self.path,
        name: name
      });
    }
  };

  return HueFileEntry;
}));

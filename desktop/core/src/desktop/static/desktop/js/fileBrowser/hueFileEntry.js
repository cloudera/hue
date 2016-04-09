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
   * @param {Function} options.trashEntry - The observable keeping track of the trash directory
   * @param {HueFolder} options.parent
   * @param {string} options.app - Currently only 'documents' is supported
   * @param {string} options.user
   *
   * @constructor
   */
  function HueFileEntry (options) {
    var self = this;
    self.activeEntry = options.activeEntry;
    self.trashEntry = options.trashEntry;
    self.parent = options.parent;
    self.definition = ko.observable(options.definition);
    self.assistHelper = options.assistHelper;
    self.app = options.app;
    self.user = options.user;
    self.userGroups = options.userGroups;
    self.superuser = options.superuser;

    self.document = ko.observable();

    self.isTrash = ko.pureComputed(function () {
      return self.definition().name === '.Trash';
    });

    self.isTrashed = ko.pureComputed(function () {
      if (typeof self.parent !== 'undefined' && self.parent !== null) {
        return self.parent.isTrash() || self.parent.isTrashed();
      }
      return false;
    });

    self.isRoot = ko.pureComputed(function () {
      return self.definition().name === '';
    });

    self.isDirectory = ko.pureComputed(function () {
      return self.definition().type === 'directory';
    });

    self.isShared = ko.pureComputed(function () {
      var perms = self.definition().perms;
      return perms && (perms.read.users.length > 0 || perms.read.groups.length > 0 || perms.write.users.length > 0 || perms.write.groups.length > 0);
    });

    self.isSharedWithMe = ko.pureComputed(function () {
      return self.user !== self.definition().owner;
    });

    self.canModify = ko.pureComputed(function () {
      var perms = self.definition().perms;
      return !self.isSharedWithMe() || self.superuser || (perms && (perms.write.users.filter(function (user) {
            return user.username == self.user;
          }).length > 0
          || perms.write.groups.filter(function (writeGroup) {
            return self.userGroups.indexOf(writeGroup) !== -1
          }).length > 0));
    });

    self.canReshare = ko.pureComputed(function () {
      if (! self.isSharedWithMe()) {
        return true;
      }
      var activePerms = {};
      var target = self;
      while (target.parent && !target.isShared()) {
        target = target.parent;
      }
      return target.canModify();
    });

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

    self.sharedWithMeSelected = ko.pureComputed(function () {
      return self.selectedEntries().filter(function (entry) {
        return entry.isSharedWithMe();
      }).length > 0;
    });

    self.selectedEntry = ko.pureComputed(function () {
      if (self.selectedEntries().length === 1) {
        return self.selectedEntries()[0];
      }
      return null;
    });

    self.breadcrumbs = ko.pureComputed(function () {
      var result = [];
      var lastParent = self.parent;
      while (lastParent) {
        result.unshift(lastParent);
        lastParent = lastParent.parent;
      }
      return result;
    });
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

  HueFileEntry.prototype.showNewDirectoryModal = function () {
    var self = this;
    if (! self.isTrash() && ! self.isTrashed()) {
      $('#createDirectoryModal').modal('show');
    }
  }

  HueFileEntry.prototype.showSharingModal = function (entry) {
    var self = this;
    if (entry) {
      $.each(self.selectedEntries(), function (idx, otherEntry) {
        if (otherEntry !== entry) {
          otherEntry.selected(false);
        }
      });
      entry.selected(true);
    }
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
          var nextId = entries.shift().definition().uuid;
          self.assistHelper.moveDocument({
            successCallback: function () {
              moveNext();
            },
            errorCallback: function () {
              self.activeEntry().load();
            },
            sourceId: nextId,
            destinationId: self.definition().uuid
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

  HueFileEntry.prototype.createNewEntry = function (options) {
    var self = this;
    return new HueFileEntry($.extend({
      activeEntry: self.activeEntry,
      trashEntry: self.trashEntry,
      assistHelper: self.assistHelper,
      app: self.app,
      user: self.user,
      superuser: self.superuser
    }, options));
  };

  HueFileEntry.prototype.search = function (query) {
    var self = this;

    var owner = self.definition().isSearchResult ? self.parent : self;

    if (! query) {
      if (self.definition().isSearchResult) {
        self.activeEntry(self.parent);
      }
      return;
    }

    var resultEntry = self.createNewEntry({
      definition: {
        isSearchResult: true,
        name: '"' + query + '"'
      },
      parent: owner
    });

    self.activeEntry(resultEntry);

    resultEntry.loading(true);

    self.assistHelper.searchDocuments({
      uuid: owner.uuid,
      query: query,
      successCallback: function (data) {
        resultEntry.hasErrors(false);
        var newEntries = [];

        $.each(data.documents, function (idx, definition) {
          var entry = self.createNewEntry({
            definition: definition,
            parent: self
          });
          if (!entry.isTrash()) {
            newEntries.push(entry);
          }
        });

        resultEntry.entries(newEntries);
        resultEntry.loading(false);
        resultEntry.loaded(true);
      },
      errorCallback: function () {
        resultEntry.hasErrors(true);
        resultEntry.loading(false);
        resultEntry.loaded(true);
      }
    });
  };

  HueFileEntry.prototype.toggleSelected = function () {
    var self = this;
    self.selected(! self.selected());
  };

  HueFileEntry.prototype.openSelected = function () {
    var self = this;
    if (self.selectedEntries().length === 1) {
      self.selectedEntry().open();
    }
  };

  HueFileEntry.prototype.open = function () {
    var self = this;
    if (self.definition().type === 'directory') {
      self.makeActive();
      huePubSub.publish('file.browser.directory.opened');
      if (! self.loaded()) {
        self.load();
      }
    } else {
      window.location.href = self.definition().absoluteUrl;
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
        uuid: self.definition().uuid,
        successCallback: function(data) {
          self.definition(data.document);
          self.hasErrors(false);
          var newEntries = [];

          $.each(data.children, function (idx, definition) {
            var entry = self.createNewEntry({
              definition: definition,
              parent: self
            });
            if (entry.isTrash()) {
              self.trashEntry(entry);
            } else {
              newEntries.push(entry);
            }
          });

          newEntries.sort(function (a, b) {
            if (a.isDirectory() && ! b.isDirectory()) {
              return -1;
            }
            if (b.isDirectory() && ! a.isDirectory()) {
              return 1;
            }
            return a.definition().name.localeCompare(b.definition().name);
          });
          self.entries(newEntries);
          if (! self.parent && data.parent) {
            self.parent = self.createNewEntry({
              definition: data.parent.path === '/' && self.isSharedWithMe() ? { name: '/' } : data.parent,
              parent: null
            });
          }
          self.loading(false);
          self.loaded(true);

          if (self.isRoot() && self.entries().length === 1 && self.entries()[0].definition().type === 'directory' && self.entries()[0].isSharedWithMe()) {
            self.activeEntry(self.entries()[0]);
            self.activeEntry().load(callback);
          } else if (callback && typeof callback === 'function') {
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

  HueFileEntry.prototype.showTrash = function () {
    var self = this;
    if (self.trashEntry()) {
      self.trashEntry().open();
    }
  };

  HueFileEntry.prototype.moveToTrash = function () {
    var self = this;
    if (self.selectedEntries().length > 0 && (self.superuser || !self.sharedWithMeSelected())) {
      self.entriesToDelete(self.selectedEntries());
      self.removeDocuments(false);
    }
  };

  HueFileEntry.prototype.showDeleteConfirmation = function () {
    var self = this;
    if (self.selectedEntries().length > 0 && (self.superuser || !self.sharedWithMeSelected())) {
      self.entriesToDelete(self.selectedEntries());
      $('#deleteEntriesModal').modal('show');
    }
  };

  HueFileEntry.prototype.removeDocuments = function (deleteForever) {
    var self = this;
    if (self.app === 'documents') {
      if (self.entriesToDelete().indexOf(self) !== -1) {
        self.activeEntry(self.parent);
      }

      var deleteNext = function () {
        if (self.entriesToDelete().length > 0) {
          var nextUuid = self.entriesToDelete().shift().definition().uuid;
          self.assistHelper.deleteDocument({
            uuid: nextUuid,
            skipTrash: deleteForever,
            successCallback: function () {
              deleteNext();
            },
            errorCallback: function () {
              self.activeEntry().load();
            }
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
    if (document.getElementById("importDocumentInput").files.length > 0 && self.app === 'documents') {
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
    var self = this;
    if (self.app == 'documents' && ! self.isTrash() && ! self.isTrashed()) {
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
    window.location.href = '/desktop/api2/doc/export?documents=' + ko.mapping.toJSON([ self.definition().id ]);
  };

  HueFileEntry.prototype.download = function () {
    var self = this;
    if (self.app = 'documents') {
      if (self.selectedEntries().length > 0) {
        var ids = self.selectedEntries().map(function (entry) {
          return entry.definition().id;
        });
        window.location.href = '/desktop/api2/doc/export?documents=' + ko.mapping.toJSON(ids);
      } else {
        self.downloadThis();
      }
    };
  };

  HueFileEntry.prototype.createDirectory = function (name) {
    var self = this;
    if (name && self.app === 'documents') {
      self.assistHelper.createDocumentsFolder({
        successCallback: self.load.bind(self),
        parentUuid: self.definition().uuid,
        name: name
      });
    }
  };

  return HueFileEntry;
}));

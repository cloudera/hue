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

var HueFileEntry = (function () {
  var self = this;
  self.loading = ko.observable(false);

  var sorts = {
    defaultAsc: function (a, b) {
      if (a.isDirectory() && !b.isDirectory()) {
        return -1;
      }
      if (!a.isDirectory() && b.isDirectory()) {
        return 1;
      }
      if (a.isDirectory() && b.isDirectory()) {
        return sorts.nameAsc(a, b);
      }
      return sorts.lastModifiedDesc(a, b);
    },
    nameAsc: function (a, b) {
      return a.definition().name.localeCompare(b.definition().name);
    },
    nameDesc: function (a, b) {
      return sorts.nameAsc(b, a);
    },
    descriptionAsc: function (a, b) {
      return a.definition().description.localeCompare(b.definition().description);
    },
    descriptionDesc: function (a, b) {
      return sorts.descriptionAsc(b, a);
    },
    typeAsc: function (a, b) {
      return a.definition().type.localeCompare(b.definition().type);
    },
    typeDesc: function (a, b) {
      return sorts.typeAsc(b, a);
    },
    ownerAsc: function (a, b) {
      return a.definition().owner.localeCompare(b.definition().owner);
    },
    ownerDesc: function (a, b) {
      return sorts.ownerAsc(b, a);
    },
    lastModifiedAsc: function (a, b) {
      return a.definition().last_modified_ts - b.definition().last_modified_ts;
    },
    lastModifiedDesc: function (a, b) {
      return sorts.lastModifiedAsc(b, a);
    }
  };

  /**
   *
   * @param {Object} options
   * @param {ApiHelper} options.apiHelper
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
    self.apiHelper = options.apiHelper;
    self.app = options.app;
    self.user = options.user;
    self.superuser = options.superuser;
    self.serverTypeFilter = options.serverTypeFilter || ko.observable({ type: 'all' });
    self.statsVisible = ko.observable(false);
    self.highlight = ko.observable(false);

    self.document = ko.observable();
    self.selectedDocsWithDependents = ko.observable([]);
    self.importedDocSummary = ko.observable();
    self.showTable = ko.observable();
    self.entries = ko.observableArray([]);

    // Filter is only used in the assist panel at the moment
    self.isFilterVisible = ko.observable(false);
    self.filter = ko.observable('').extend({ rateLimit: 400 });

    self.typeFilter = options.typeFilter || ko.observable(DOCUMENT_TYPES[0]); // First one is always 'all'

    self.isFilterVisible.subscribe(function (newValue) {
      if (!newValue && self.filter()) {
        self.filter('');
      }
    });

    self.filteredEntries = ko.pureComputed(function () {
      var filter = self.filter().toLowerCase();
      var typeFilter = self.typeFilter().type;
      if (filter || typeFilter !== 'all') {
        return self.entries().filter(function (entry) {
          var entryType = entry.definition().type;
          return (typeFilter === 'all' || entryType === typeFilter || entryType === 'directory')
            && (!filter || entry.definition().name.toLowerCase().indexOf(filter) !== -1 ||
            (window.DOCUMENT_TYPE_I18n[entryType] && window.DOCUMENT_TYPE_I18n[entryType].toLowerCase().indexOf(filter) !== -1) ||
            entry.definition().description.toLowerCase().indexOf(filter) !== -1);
        })
      }
      return self.entries();
    });

    self.getSelectedDocsWithDependents = function() {
      self.selectedDocsWithDependents([]);
      var uuids = self.selectedEntries().map(function(entry) {
        return entry.definition().uuid;
      }).join(',');

      var data = {
        'uuids': uuids,
        'data': 'false',
        'dependencies': 'true'
      };

      $.get('/desktop/api2/doc/', data, function (response) {
        var docsWithDependents = [];
        if (response && response.data_list) {
          for (var index = 0; index < response.data_list.length; index++) {
            docsWithDependents.push({'name': response.data_list[index].document.name, 'dependents': response.data_list[index].dependents})
          }
        }
        self.selectedDocsWithDependents(docsWithDependents);
      }).fail(function (response) {
        $(document).trigger("error", "Error getting document data: " + response.responseText);
      });
    };

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
            return LOGGED_USERGROUPS.indexOf(writeGroup.name) !== -1
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
    self.deletingEntries = ko.observable(false);

    self.selected = ko.observable(false);

    self.loaded = ko.observable(false);
    self.loading = ko.observable(false);
    self.hasErrors = ko.observable(false);

    self.uploading = ko.observable(false);
    self.uploadComplete = ko.observable(false);
    self.uploadFailed = ko.observable(false);
    self.selectedImportFile = ko.observable('');

    self.importEnabled = ko.pureComputed(function () {
      return self.selectedImportFile() !== '';
    });

    self.activeSort = options.activeSort;

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

    self.directorySelected = ko.pureComputed(function () {
      return self.selectedEntries().filter(function (entry) {
        return entry.isDirectory();
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

  HueFileEntry.prototype.getDirectory = function () {
    var self = this;

    if (! self.definition() || self.isRoot()) {
      return null;
    }
    else {
      return self.definition().uuid;
    }
  };

  HueFileEntry.prototype.highlightInside = function (uuid) {
    var self = this;
    self.typeFilter(DOCUMENT_TYPES[0]);
    var foundEntry;
    self.entries().forEach(function (entry) {
      entry.highlight(false);
      if (entry.definition() && entry.definition().uuid === uuid) {
        foundEntry = entry;
      }
    });
    if (foundEntry) {
      if (foundEntry.definition().type === 'directory') {
        self.activeEntry(foundEntry);
        if (!foundEntry.entries().length) {
          foundEntry.load();
        }
      } else {
        window.setTimeout(function () {
          huePubSub.subscribeOnce('assist.db.scrollToComplete', function () {
            foundEntry.highlight(true);
            // Timeout is for animation effect
            window.setTimeout(function () {
              foundEntry.highlight(false);
            }, 1800);
          });
          huePubSub.publish('assist.db.scrollTo', foundEntry);
        }, 0);
      }
    }
  };

  HueFileEntry.prototype.showContextPopover = function (entry, event, positionAdjustment) {
    var self = this;
    var $source = $(event.target);
    var offset = $source.offset();
    if (positionAdjustment) {
      offset.left += positionAdjustment.left;
      offset.top += positionAdjustment.top;
    }

    self.statsVisible(true);
    huePubSub.publish('context.popover.show', {
      data: {
        type: 'hue',
        definition: self.definition()
      },
      showInAssistEnabled: false,
      orientation: 'right',
      pinEnabled: false,
      source: {
        element: event.target,
        left: offset.left,
        top: offset.top - 3,
        right: offset.left + $source.width() + 1,
        bottom: offset.top + $source.height() - 3
      }
    });
    huePubSub.subscribeOnce('context.popover.hidden', function () {
      self.statsVisible(false);
    });
  };

  HueFileEntry.prototype.addDirectoryParamToUrl = function (url) {
    var self = this;

    var directoryId = self.getDirectory();

    if (! directoryId) {
      return url;
    }
    else if (url.indexOf('?') !== -1) {
      return url + '&directory_uuid=' + self.definition().uuid;
    }
    else {
      return url + '?directory_uuid=' + self.definition().uuid;
    }
  };

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
    if (! self.isTrash() && ! self.isTrashed() && self.canModify()) {
      $('#createDirectoryModal').modal('show');
    }
  };

  HueFileEntry.prototype.showRenameDirectoryModal = function () {
    var self = this;
    if (!self.selected()) {
      self = self.selectedEntry();
    }
    if (! self.isTrash() && ! self.isTrashed() && self.canModify()) {
      $('#renameDirectoryName').val(self.definition().name);
      $('#renameDirectoryModal').modal('show');
    }
  };

  HueFileEntry.prototype.setSort = function (name) {
    var self = this;
    if (self.activeSort().indexOf(name) === -1) {
      if (name === 'lastModified') {
        self.activeSort('lastModifiedDesc');
      } else {
        self.activeSort(name + 'Asc')
      }
    } else if (name !== 'lastModified' && self.activeSort().indexOf('Asc') !== -1) {
      self.activeSort(name + 'Desc');
    } else if (name === 'lastModified' && self.activeSort().indexOf('Desc') !== -1) {
      self.activeSort('lastModifiedAsc');
    } else {
      self.activeSort('defaultAsc');
    }
    self.entries.sort(sorts[self.activeSort()]);
  };

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
      self.selectedEntry().loadDocument();
      $('#shareDocumentModal').modal('show');
    }
  };

  HueFileEntry.prototype.copy = function () {
    var self = this;
    if (self.selectedEntries().indexOf(self) !== -1) {
      self.activeEntry(self.parent);
    }
    var copyNext = function () {
      if (self.selectedEntries().length > 0) {
        var nextUuid = self.selectedEntries().shift().definition().uuid;
        self.apiHelper.copyDocument({
          uuid: nextUuid,
          successCallback: function () {
            copyNext();
          },
          errorCallback: function () {
            self.activeEntry().load();
          }
        });
      } else {
        huePubSub.publish('assist.document.refresh');
        self.activeEntry().load();
      }
    };
    copyNext();
  };

  HueFileEntry.prototype.loadDocument = function () {
    var self = this;
    self.document(new HueDocument({
      apiHelper: self.apiHelper,
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
          self.apiHelper.moveDocument({
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
          huePubSub.publish('assist.document.refresh');
          if (self !== self.activeEntry()) {
            self.load();
          }
          self.activeEntry().load();
        }
      };
    }
    moveNext();
  };

  HueFileEntry.prototype.createNewEntry = function (options) {
    var self = this;
    return new HueFileEntry($.extend({
      activeEntry: self.activeEntry,
      activeSort: self.activeSort,
      trashEntry: self.trashEntry,
      apiHelper: self.apiHelper,
      serverTypeFilter: self.serverTypeFilter,
      typeFilter: self.typeFilter,
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

    self.apiHelper.searchDocuments({
      uuid: owner.uuid,
      query: query,
      type: self.serverTypeFilter().type,
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

  HueFileEntry.prototype.open = function (entry, e) {
    var self = this;
    if (self.definition().type === 'directory') {
      self.makeActive();
      huePubSub.publish('file.browser.directory.opened');
      if (!self.loaded()) {
        self.load();
      }
    } else {
      huePubSub.publish('open.link', self.definition().absoluteUrl);
    }
  };

  HueFileEntry.prototype.load = function (successCallback, errorCallback, silenceErrors) {
    var self = this;
    if (self.loading()) {
      return;
    }
    self.loading(true);

    if (self.app === 'documents') {
      self.apiHelper.fetchDocuments({
        uuid: self.definition().uuid,
        type: self.serverTypeFilter().type,
        silenceErrors: !!silenceErrors,
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

          newEntries.sort(sorts[self.activeSort()]);
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
            self.activeEntry().load(successCallback);
          } else if (successCallback && typeof successCallback === 'function') {
            successCallback();
          }
        },
        errorCallback: function () {
          self.hasErrors(true);
          self.loading(false);
          self.loaded(true);
          if (errorCallback) {
            errorCallback();
          }
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

  HueFileEntry.prototype.emptyTrash = function () {
    var self = this;
    if (self.trashEntry()) {
      if (! self.trashEntry().loaded()) {
        self.trashEntry().load(function () {
          self.entriesToDelete(self.trashEntry().entries());
          $('#deleteEntriesModal').modal('show');
        })
      } else {
        self.entriesToDelete(self.trashEntry().entries());
        $('#deleteEntriesModal').modal('show');
      }
    }
  };

  HueFileEntry.prototype.moveToTrash = function () {
    var self = this;
    if (self.selectedEntries().length > 0 && (self.superuser || !self.sharedWithMeSelected())) {
      self.entriesToDelete(self.selectedEntries());
      self.removeDocuments(false);
    }
  };

  HueFileEntry.prototype.showRestoreConfirmation = function () {
    var self = this;
    if (self.selectedEntries().length > 0 && (self.superuser || !self.sharedWithMeSelected())) {
      $('#restoreFromTrashModal').modal('show');
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
    if (self.entriesToDelete().indexOf(self) !== -1) {
      self.activeEntry(self.parent);
    }

    var deleteNext = function () {
      if (self.entriesToDelete().length > 0) {
        var nextUuid = self.entriesToDelete().shift().definition().uuid;
        self.apiHelper.deleteDocument({
          uuid: nextUuid,
          skipTrash: deleteForever,
          successCallback: function () {
            deleteNext();
          },
          errorCallback: function () {
            self.activeEntry().load();
            $('#deleteEntriesModal').modal('hide');
            $(".modal-backdrop").remove();
            self.deletingEntries(false);
          }
        });
      } else {
        self.deletingEntries(false);
        huePubSub.publish('assist.document.refresh');
        $('#deleteEntriesModal').modal('hide');
        $(".modal-backdrop").remove();
        self.activeEntry().load();
      }
    };
    self.deletingEntries(true);
    deleteNext();
  };


  HueFileEntry.prototype.closeUploadModal = function () {
    var self = this;
    if (self.app === 'documents') {
      $('#importDocumentsModal').modal('hide');
      $('#importDocumentData').modal('hide');
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
      self.importedDocSummary(null);
      self.showTable(false);
      self.apiHelper.uploadDocument({
        formData: new FormData($('#importDocumentsForm')[0]),
        successCallback: function (data) {
          self.uploading(false);
          self.uploadComplete(true);
          huePubSub.publish('assist.document.refresh');
          self.load();

          $('#importDocumentsModal').modal('hide');
          $('#importDocumentData').modal('show');

          self.importedDocSummary(data);
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

  HueFileEntry.prototype.importedDocumentCount = function () {
    var self = this;
    if (self.importedDocSummary()) {
      return self.importedDocSummary()['documents'].length;
    }
    return 0;
  };

  HueFileEntry.prototype.toggleShowTable = function () {
    var self = this;
    self.showTable(!self.showTable());
  };

  HueFileEntry.prototype.makeActive = function () {
    var self = this;
    if (!self.loaded()) {
      self.load();
    }
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
    window.location.href = window.HUE_BASE_URL + '/desktop/api2/doc/export?documents=' + ko.mapping.toJSON([ self.definition().id ]);
  };

  HueFileEntry.prototype.download = function () {
    var self = this;
    if (self.app = 'documents') {
      if (self.selectedEntries().length > 0) {
        var ids = self.selectedEntries().map(function (entry) {
          return entry.definition().id;
        });
        window.location.href = window.HUE_BASE_URL + '/desktop/api2/doc/export?documents=' + ko.mapping.toJSON([ self.definition().id ]);
      } else {
        self.downloadThis();
      }
    };
  };

  HueFileEntry.prototype.restoreFromTrash = function () {
    var self = this;
    if (self.app === 'documents') {
      if (self.selectedEntries().indexOf(self) !== -1) {
        self.activeEntry(self.parent);
      }

      if (self.selectedEntries().length > 0) {
        var uuids = self.selectedEntries().map(function(entry) {
          return entry.definition().uuid;
        }).join(',');
        self.apiHelper.restoreDocument({
          uuids: uuids,
          successCallback: function () {
            huePubSub.publish('assist.document.refresh');
            self.activeEntry().load();
          },
          errorCallback: function () {
            self.activeEntry().load();
          }
        });
      } else {
        self.activeEntry().load();
      }
      $('#restoreFromTrashModal').modal('hide');
    }
  };

  HueFileEntry.prototype.createDirectory = function (name) {
    var self = this;
    if (name && self.app === 'documents') {
      self.apiHelper.createDocumentsFolder({
        successCallback: function () {
          huePubSub.publish('assist.document.refresh');
          self.load()
        },
        parentUuid: self.definition().uuid,
        name: name
      });
      $('#newDirectoryName').val(null)
    }
  };

  HueFileEntry.prototype.renameDirectory = function (name) {
    var self = this;
    if (name && self.app === 'documents') {
      self.apiHelper.updateDocument({
        successCallback: function () {
          huePubSub.publish('assist.document.refresh');
          self.load();
        },
        uuid: self.definition().uuid,
        name: name
      });
      $('#renameDirectoryName').val(null)
    }
  };

  return HueFileEntry;
})();

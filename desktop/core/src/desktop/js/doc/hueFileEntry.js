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

import $ from 'jquery';
import ko from 'knockout';

import apiHelper from 'api/apiHelper';
import huePubSub from 'utils/huePubSub';
import HueDocument from 'doc/hueDocument';
import { DOCUMENT_TYPE_I18n, DOCUMENT_TYPES } from 'doc/docSupport';

const SORTS = {
  defaultAsc: (a, b) => {
    if (a.isDirectory() && !b.isDirectory()) {
      return -1;
    }
    if (!a.isDirectory() && b.isDirectory()) {
      return 1;
    }
    if (a.isDirectory() && b.isDirectory()) {
      return SORTS.nameAsc(a, b);
    }
    return SORTS.lastModifiedDesc(a, b);
  },
  nameAsc: (a, b) => a.definition().name.localeCompare(b.definition().name),
  nameDesc: (a, b) => SORTS.nameAsc(b, a),
  descriptionAsc: (a, b) => a.definition().description.localeCompare(b.definition().description),
  descriptionDesc: (a, b) => SORTS.descriptionAsc(b, a),
  typeAsc: (a, b) => a.definition().type.localeCompare(b.definition().type),
  typeDesc: (a, b) => SORTS.typeAsc(b, a),
  ownerAsc: (a, b) => a.definition().owner.localeCompare(b.definition().owner),
  ownerDesc: (a, b) => SORTS.ownerAsc(b, a),
  lastModifiedAsc: (a, b) => a.definition().last_modified_ts - b.definition().last_modified_ts,
  lastModifiedDesc: (a, b) => SORTS.lastModifiedAsc(b, a)
};

class HueFileEntry {
  /**
   *
   * @param {Object} options
   * @param {Object} options.definition
   * @param {Function} options.activeEntry - The observable keeping track of the current open directory
   * @param {Function} options.trashEntry - The observable keeping track of the trash directory
   * @param {HueFolder} options.parent
   * @param {string} options.app - Currently only 'documents' is supported
   * @param {string} options.user
   *
   * @constructor
   */
  constructor(options) {
    this.activeEntry = options.activeEntry;
    this.trashEntry = options.trashEntry;
    this.parent = options.parent;
    this.definition = ko.observable(options.definition);
    this.app = options.app;
    this.user = options.user;
    this.superuser = options.superuser;
    this.serverTypeFilter = options.serverTypeFilter || ko.observable({ type: 'all' });
    this.statsVisible = ko.observable(false);
    this.highlight = ko.observable(false);

    this.document = ko.observable();
    this.selectedDocsWithDependents = ko.observable([]);
    this.importedDocSummary = ko.observable();
    this.showTable = ko.observable();
    this.entries = ko.observableArray([]);

    // Filter is only used in the assist panel at the moment
    this.isFilterVisible = ko.observable(false);
    this.filter = ko.observable('').extend({ rateLimit: 400 });

    this.typeFilter = options.typeFilter || ko.observable(DOCUMENT_TYPES[0]); // First one is always 'all'

    this.isFilterVisible.subscribe(newValue => {
      if (!newValue && this.filter()) {
        this.filter('');
      }
    });

    this.filteredEntries = ko.pureComputed(() => {
      const filter = this.filter().toLowerCase();
      const typeFilter = this.typeFilter().type;
      if (filter || typeFilter !== 'all') {
        return this.entries().filter(entry => {
          const entryType = entry.definition().type;
          return (
            (typeFilter === 'all' || entryType === typeFilter || entryType === 'directory') &&
            (!filter ||
              entry
                .definition()
                .name.toLowerCase()
                .indexOf(filter) !== -1 ||
              (DOCUMENT_TYPE_I18n[entryType] &&
                DOCUMENT_TYPE_I18n[entryType].toLowerCase().indexOf(filter) !== -1) ||
              entry
                .definition()
                .description.toLowerCase()
                .indexOf(filter) !== -1)
          );
        });
      }
      return this.entries();
    });

    this.getSelectedDocsWithDependents = () => {
      this.selectedDocsWithDependents([]);
      const uuids = this.selectedEntries()
        .map(entry => entry.definition().uuid)
        .join(',');

      const data = {
        uuids: uuids,
        data: 'false',
        dependencies: 'true'
      };

      $.get('/desktop/api2/doc/', data, response => {
        const docsWithDependents = [];
        if (response && response.data_list) {
          for (let index = 0; index < response.data_list.length; index++) {
            docsWithDependents.push({
              name: response.data_list[index].document.name,
              dependents: response.data_list[index].dependents
            });
          }
        }
        this.selectedDocsWithDependents(docsWithDependents);
      }).fail(response => {
        $(document).trigger('error', 'Error getting document data: ' + response.responseText);
      });
    };

    this.isTrash = ko.pureComputed(() => this.definition().name === '.Trash');

    this.isTrashed = ko.pureComputed(() => {
      if (typeof this.parent !== 'undefined' && this.parent !== null) {
        return this.parent.isTrash() || this.parent.isTrashed();
      }
      return false;
    });

    this.isRoot = ko.pureComputed(() => this.definition().name === '');

    this.isDirectory = ko.pureComputed(() => this.definition().type === 'directory');

    this.isShared = ko.pureComputed(() => {
      const perms = this.definition().perms;
      return (
        perms &&
        (perms.read.users.length > 0 ||
          perms.read.groups.length > 0 ||
          perms.write.users.length > 0 ||
          perms.write.groups.length > 0)
      );
    });

    this.isSharedWithMe = ko.pureComputed(() => this.user !== this.definition().owner);

    this.canModify = ko.pureComputed(() => {
      const perms = this.definition().perms;
      return (
        !this.isSharedWithMe() ||
        this.superuser ||
        (perms &&
          (perms.write.users.some(user => user.username === this.user) ||
            perms.write.groups.some(
              writeGroup => LOGGED_USERGROUPS.indexOf(writeGroup.name) !== -1
            )))
      );
    });

    this.canReshare = ko.pureComputed(() => {
      if (!this.isSharedWithMe()) {
        return true;
      }
      let target = this;
      while (target.parent && !target.isShared()) {
        target = target.parent;
      }
      return target.canModify();
    });

    this.entriesToDelete = ko.observableArray();
    this.deletingEntries = ko.observable(false);

    this.selected = ko.observable(false);

    this.loaded = ko.observable(false);
    this.loading = ko.observable(false);
    this.hasErrors = ko.observable(false);

    this.uploading = ko.observable(false);
    this.uploadComplete = ko.observable(false);
    this.uploadFailed = ko.observable(false);
    this.selectedImportFile = ko.observable('');

    this.importEnabled = ko.pureComputed(() => this.selectedImportFile() !== '');

    this.activeSort = options.activeSort;

    this.selectedEntries = ko.pureComputed(() => this.entries().filter(entry => entry.selected()));

    this.sharedWithMeSelected = ko.pureComputed(() =>
      this.selectedEntries().some(entry => entry.isSharedWithMe())
    );

    this.directorySelected = ko.pureComputed(() =>
      this.selectedEntries().some(entry => entry.isDirectory())
    );

    this.selectedEntry = ko.pureComputed(() => {
      if (this.selectedEntries().length === 1) {
        return this.selectedEntries()[0];
      }
      return null;
    });

    this.breadcrumbs = ko.pureComputed(() => {
      const result = [];
      let lastParent = this.parent;
      while (lastParent) {
        result.unshift(lastParent);
        lastParent = lastParent.parent;
      }
      return result;
    });
  }

  getDirectory() {
    if (!this.definition() || this.isRoot()) {
      return null;
    } else {
      return this.definition().uuid;
    }
  }

  highlightInside(uuid) {
    const self = this;
    self.typeFilter(DOCUMENT_TYPES[0]);
    let foundEntry;
    self.entries().forEach(entry => {
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
        window.setTimeout(() => {
          huePubSub.subscribeOnce('assist.db.scrollToComplete', () => {
            foundEntry.highlight(true);
            // Timeout is for animation effect
            window.setTimeout(() => {
              foundEntry.highlight(false);
            }, 1800);
          });
          huePubSub.publish('assist.db.scrollTo', foundEntry);
        }, 0);
      }
    }
  }

  showContextPopover(entry, event, positionAdjustment) {
    const self = this;
    const $source = $(event.target);
    const offset = $source.offset();
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
    huePubSub.subscribeOnce('context.popover.hidden', () => {
      self.statsVisible(false);
    });
  }

  addDirectoryParamToUrl(url) {
    const self = this;
    const directoryId = self.getDirectory();

    if (!directoryId) {
      return url;
    } else if (url.indexOf('?') !== -1) {
      return url + '&directory_uuid=' + self.definition().uuid;
    } else {
      return url + '?directory_uuid=' + self.definition().uuid;
    }
  }

  beforeContextOpen() {
    if (!this.selected()) {
      this.parent.selectedEntries().forEach(entry => {
        entry.selected(false);
      });
      this.selected(true);
    }
  }

  showNewDirectoryModal() {
    if (!this.isTrash() && !this.isTrashed() && this.canModify()) {
      $('#createDirectoryModal').modal('show');
    }
  }

  showRenameDirectoryModal() {
    let selectedEntry = this;
    if (!selectedEntry.selected()) {
      selectedEntry = selectedEntry.selectedEntry();
    }
    if (!selectedEntry.isTrash() && !selectedEntry.isTrashed() && selectedEntry.canModify()) {
      $('#renameDirectoryName').val(selectedEntry.definition().name);
      $('#renameDirectoryModal').modal('show');
    }
  }

  setSort(name) {
    if (this.activeSort().indexOf(name) === -1) {
      if (name === 'lastModified') {
        this.activeSort('lastModifiedDesc');
      } else {
        this.activeSort(name + 'Asc');
      }
    } else if (name !== 'lastModified' && this.activeSort().indexOf('Asc') !== -1) {
      this.activeSort(name + 'Desc');
    } else if (name === 'lastModified' && this.activeSort().indexOf('Desc') !== -1) {
      this.activeSort('lastModifiedAsc');
    } else {
      this.activeSort('defaultAsc');
    }
    this.entries.sort(SORTS[this.activeSort()]);
  }

  showSharingModal(entry) {
    if (entry) {
      this.selectedEntries().forEach(otherEntry => {
        if (otherEntry !== entry) {
          otherEntry.selected(false);
        }
      });
      entry.selected(true);
    }
    if (this.selectedEntry()) {
      this.selectedEntry().loadDocument();
      $('#shareDocumentModal').modal('show');
    }
  }

  copy() {
    const self = this;
    if (self.selectedEntries().indexOf(self) !== -1) {
      self.activeEntry(self.parent);
    }
    const copyNext = () => {
      if (self.selectedEntries().length > 0) {
        const nextUuid = self
          .selectedEntries()
          .shift()
          .definition().uuid;
        apiHelper.copyDocument({
          uuid: nextUuid,
          successCallback: () => {
            copyNext();
          },
          errorCallback: () => {
            self.activeEntry().load();
          }
        });
      } else {
        huePubSub.publish('assist.document.refresh');
        self.activeEntry().load();
      }
    };
    copyNext();
  }

  loadDocument() {
    this.document(new HueDocument({ fileEntry: this }));
    this.document().load();
  }

  /**
   * @param {HueFileEntry[]} entries
   */
  moveHere(entries) {
    const self = this;
    if (self.app === 'documents') {
      const moveNext = () => {
        if (entries.length > 0) {
          const nextId = entries.shift().definition().uuid;
          apiHelper.moveDocument({
            successCallback: () => {
              moveNext();
            },
            errorCallback: () => {
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
      moveNext();
    }
  }

  createNewEntry(options) {
    return new HueFileEntry(
      $.extend(
        {
          activeEntry: this.activeEntry,
          activeSort: this.activeSort,
          trashEntry: this.trashEntry,
          serverTypeFilter: this.serverTypeFilter,
          typeFilter: this.typeFilter,
          app: this.app,
          user: this.user,
          superuser: this.superuser
        },
        options
      )
    );
  }

  search(query) {
    const self = this;

    const owner = self.definition().isSearchResult ? self.parent : self;

    if (!query) {
      if (self.definition().isSearchResult) {
        self.activeEntry(self.parent);
      }
      return;
    }

    const resultEntry = self.createNewEntry({
      definition: {
        isSearchResult: true,
        name: '"' + query + '"'
      },
      parent: owner
    });

    self.activeEntry(resultEntry);

    resultEntry.loading(true);

    apiHelper.searchDocuments({
      uuid: owner.uuid,
      query: query,
      type: self.serverTypeFilter().type,
      successCallback: function(data) {
        resultEntry.hasErrors(false);
        const newEntries = [];

        data.documents.forEach(definition => {
          const entry = self.createNewEntry({
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
      errorCallback: () => {
        resultEntry.hasErrors(true);
        resultEntry.loading(false);
        resultEntry.loaded(true);
      }
    });
  }

  toggleSelected() {
    this.selected(!this.selected());
  }

  openSelected() {
    if (this.selectedEntries().length === 1) {
      this.selectedEntry().open();
    }
  }

  open() {
    if (this.definition().type === 'directory') {
      this.makeActive();
      huePubSub.publish('file.browser.directory.opened');
      if (!this.loaded()) {
        this.load();
      }
    } else {
      huePubSub.publish('open.link', this.definition().absoluteUrl);
    }
  }

  load(successCallback, errorCallback, silenceErrors) {
    const self = this;
    if (self.loading()) {
      return;
    }
    self.loading(true);

    if (self.app === 'documents') {
      apiHelper.fetchDocuments({
        uuid: self.definition().uuid,
        type: self.serverTypeFilter().type,
        silenceErrors: !!silenceErrors,
        successCallback: data => {
          self.definition(data.document);
          self.hasErrors(false);
          const newEntries = [];

          data.children.forEach(definition => {
            const entry = self.createNewEntry({
              definition: definition,
              parent: self
            });
            if (entry.isTrash()) {
              self.trashEntry(entry);
            } else {
              newEntries.push(entry);
            }
          });

          newEntries.sort(SORTS[self.activeSort()]);
          self.entries(newEntries);
          if (!self.parent && data.parent) {
            self.parent = self.createNewEntry({
              definition:
                data.parent.path === '/' && self.isSharedWithMe() ? { name: '/' } : data.parent,
              parent: null
            });
          }
          self.loading(false);
          self.loaded(true);

          if (
            self.isRoot() &&
            self.entries().length === 1 &&
            self.entries()[0].definition().type === 'directory' &&
            self.entries()[0].isSharedWithMe()
          ) {
            self.activeEntry(self.entries()[0]);
            self.activeEntry().load(successCallback);
          } else if (successCallback && typeof successCallback === 'function') {
            successCallback();
          }
        },
        errorCallback: () => {
          self.hasErrors(true);
          self.loading(false);
          self.loaded(true);
          if (errorCallback) {
            errorCallback();
          }
        }
      });
    }
  }

  showTrash() {
    if (this.trashEntry()) {
      this.trashEntry().open();
    }
  }

  emptyTrash() {
    if (this.trashEntry()) {
      if (!this.trashEntry().loaded()) {
        this.trashEntry().load(function() {
          this.entriesToDelete(this.trashEntry().entries());
          $('#deleteEntriesModal').modal('show');
        });
      } else {
        this.entriesToDelete(this.trashEntry().entries());
        $('#deleteEntriesModal').modal('show');
      }
    }
  }

  moveToTrash() {
    if (this.selectedEntries().length > 0 && (this.superuser || !this.sharedWithMeSelected())) {
      this.entriesToDelete(this.selectedEntries());
      this.removeDocuments(false);
    }
  }

  showRestoreConfirmation() {
    if (this.selectedEntries().length > 0 && (this.superuser || !this.sharedWithMeSelected())) {
      $('#restoreFromTrashModal').modal('show');
    }
  }

  showDeleteConfirmation() {
    if (this.selectedEntries().length > 0 && (this.superuser || !this.sharedWithMeSelected())) {
      this.entriesToDelete(this.selectedEntries());
      $('#deleteEntriesModal').modal('show');
    }
  }

  removeDocuments(deleteForever) {
    const self = this;
    if (self.entriesToDelete().indexOf(self) !== -1) {
      self.activeEntry(self.parent);
    }

    const deleteNext = () => {
      if (self.entriesToDelete().length > 0) {
        const nextUuid = self
          .entriesToDelete()
          .shift()
          .definition().uuid;
        apiHelper.deleteDocument({
          uuid: nextUuid,
          skipTrash: deleteForever,
          successCallback: () => {
            deleteNext();
          },
          errorCallback: () => {
            self.activeEntry().load();
            $('#deleteEntriesModal').modal('hide');
            $('.modal-backdrop').remove();
            self.deletingEntries(false);
          }
        });
      } else {
        self.deletingEntries(false);
        huePubSub.publish('assist.document.refresh');
        $('#deleteEntriesModal').modal('hide');
        $('.modal-backdrop').remove();
        self.activeEntry().load();
      }
    };
    self.deletingEntries(true);
    deleteNext();
  }

  closeUploadModal() {
    if (this.app === 'documents') {
      $('#importDocumentsModal').modal('hide');
      $('#importDocumentData').modal('hide');
      $('#importDocumentInput').val('');
    }
    // Allow the modal to hide
    window.setTimeout(() => {
      this.uploading(false);
      this.uploadComplete(false);
      this.uploadFailed(false);
    }, 400);
  }

  upload() {
    const self = this;
    if (
      document.getElementById('importDocumentInput').files.length > 0 &&
      self.app === 'documents'
    ) {
      self.uploading(true);
      self.uploadComplete(false);
      self.uploadFailed(false);
      self.importedDocSummary(null);
      self.showTable(false);
      apiHelper.uploadDocument({
        formData: new FormData($('#importDocumentsForm')[0]),
        successCallback: data => {
          self.uploading(false);
          self.uploadComplete(true);
          huePubSub.publish('assist.document.refresh');
          self.load();

          $('#importDocumentsModal').modal('hide');
          $('#importDocumentData').modal('show');

          self.importedDocSummary(data);
        },
        progressHandler: event => {
          $('#importDocumentsProgress').val(Math.round((event.loaded / event.total) * 100));
        },
        errorCallback: () => {
          self.uploading(false);
          self.uploadComplete(true);
          self.uploadFailed(true);
        }
      });
    }
  }

  importedDocumentCount() {
    if (this.importedDocSummary()) {
      return this.importedDocSummary()['documents'].length;
    }
    return 0;
  }

  toggleShowTable() {
    this.showTable(!this.showTable());
  }

  makeActive() {
    if (!this.loaded()) {
      this.load();
    }
    this.activeEntry(this);
  }

  showUploadModal() {
    if (this.app === 'documents' && !this.isTrash() && !this.isTrashed()) {
      $('#importDocumentsModal').modal('show');
    }
  }

  contextMenuDownload() {
    if (this.selected()) {
      this.parent.download();
    } else {
      this.downloadThis();
    }
  }

  downloadThis() {
    window.location.href =
      window.HUE_BASE_URL +
      '/desktop/api2/doc/export?documents=' +
      ko.mapping.toJSON([this.definition().id]);
  }

  download() {
    if (this.app === 'documents') {
      if (this.selectedEntries().length > 0) {
        const ids = this.selectedEntries().map(entry => entry.definition().id);
        window.location.href =
          window.HUE_BASE_URL + '/desktop/api2/doc/export?documents=' + ko.mapping.toJSON(ids);
      } else {
        this.downloadThis();
      }
    }
  }

  restoreFromTrash() {
    const self = this;
    if (self.app === 'documents') {
      if (self.selectedEntries().indexOf(self) !== -1) {
        self.activeEntry(self.parent);
      }

      if (self.selectedEntries().length > 0) {
        const uuids = self
          .selectedEntries()
          .map(entry => entry.definition().uuid)
          .join(',');
        apiHelper.restoreDocument({
          uuids: uuids,
          successCallback: () => {
            huePubSub.publish('assist.document.refresh');
            self.activeEntry().load();
          },
          errorCallback: () => {
            self.activeEntry().load();
          }
        });
      } else {
        self.activeEntry().load();
      }
      $('#restoreFromTrashModal').modal('hide');
    }
  }

  createDirectory(name) {
    const self = this;
    if (name && self.app === 'documents') {
      apiHelper.createDocumentsFolder({
        successCallback: function() {
          huePubSub.publish('assist.document.refresh');
          self.load();
        },
        parentUuid: self.definition().uuid,
        name: name
      });
      $('#newDirectoryName').val(null);
    }
  }

  renameDirectory(name) {
    const self = this;
    if (name && self.app === 'documents') {
      apiHelper.updateDocument({
        successCallback: function() {
          huePubSub.publish('assist.document.refresh');
          self.load();
        },
        uuid: self.definition().uuid,
        name: name
      });
      $('#renameDirectoryName').val(null);
    }
  }
}

export default HueFileEntry;

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
import HueFileEntry from 'doc/hueFileEntry';
import { DOCUMENT_TYPES } from 'doc/docSupport';

class AssistDocumentsPanel {
  /**
   * @param {Object} options
   * @param {string} options.user
   * @constructor
   **/
  constructor(options) {
    const self = this;
    self.user = options.user;

    self.activeEntry = ko.observable();
    self.activeSort = ko.observable('defaultAsc');
    self.typeFilter = ko.observable(DOCUMENT_TYPES[0]); // all is first

    self.highlightTypeFilter = ko.observable(false);

    const lastOpenedUuid = apiHelper.getFromTotalStorage('assist', 'last.opened.assist.doc.uuid');

    if (lastOpenedUuid) {
      self.activeEntry(
        new HueFileEntry({
          activeEntry: self.activeEntry,
          trashEntry: ko.observable(),
          app: 'documents',
          user: self.user,
          activeSort: self.activeSort,
          typeFilter: self.typeFilter,
          definition: {
            uuid: lastOpenedUuid,
            type: 'directory'
          }
        })
      );
    } else {
      self.fallbackToRoot();
    }

    self.activeEntry.subscribe(newEntry => {
      if (!newEntry.loaded()) {
        const loadedSub = newEntry.loaded.subscribe(loaded => {
          if (
            loaded &&
            !newEntry.hasErrors() &&
            newEntry.definition() &&
            newEntry.definition().uuid
          ) {
            apiHelper.setInTotalStorage(
              'assist',
              'last.opened.assist.doc.uuid',
              newEntry.definition().uuid
            );
          }
          loadedSub.dispose();
        });
      } else if (!newEntry.hasErrors() && newEntry.definition() && newEntry.definition().uuid) {
        apiHelper.setInTotalStorage(
          'assist',
          'last.opened.assist.doc.uuid',
          newEntry.definition().uuid
        );
      }
    });

    self.reload = () => {
      self.activeEntry().load(
        () => {},
        () => {
          self.fallbackToRoot();
        }
      );
    };

    huePubSub.subscribe('assist.document.refresh', () => {
      huePubSub.publish('assist.clear.document.cache');
      self.reload();
    });

    huePubSub.subscribe('assist.doc.highlight', details => {
      huePubSub.publish('assist.show.documents');
      huePubSub.publish('context.popover.hide');
      const whenLoaded = $.Deferred().done(() => {
        self.activeEntry().highlightInside(details.docUuid);
      });
      if (
        self.activeEntry() &&
        self.activeEntry().definition() &&
        self.activeEntry().definition().uuid === details.parentUuid
      ) {
        if (self.activeEntry().loaded() && !self.activeEntry().hasErrors()) {
          whenLoaded.resolve();
        } else {
          const loadedSub = self.activeEntry().loaded.subscribe(newVal => {
            if (newVal) {
              if (!self.activeEntry().hasErrors()) {
                whenLoaded.resolve();
              }
              whenLoaded.reject();
              loadedSub.remove();
            }
          });
        }
        self.activeEntry().highlight(details.docUuid);
      } else {
        self.activeEntry(
          new HueFileEntry({
            activeEntry: self.activeEntry,
            trashEntry: ko.observable(),
            app: 'documents',
            user: self.user,
            activeSort: self.activeSort,
            typeFilter: self.typeFilter,
            definition: {
              uuid: details.parentUuid,
              type: 'directory'
            }
          })
        );
        self.activeEntry().load(
          () => {
            whenLoaded.resolve();
          },
          () => {
            whenLoaded.reject();
            self.fallbackToRoot();
          }
        );
      }
    });
  }

  setTypeFilter(newType) {
    const self = this;
    DOCUMENT_TYPES.some(docType => {
      if (docType.type === newType) {
        self.typeFilter(docType);
        return true;
      }
    });
    self.highlightTypeFilter(true);
    window.setTimeout(() => {
      self.highlightTypeFilter(false);
    }, 600);
  }

  fallbackToRoot() {
    const self = this;
    if (
      !self.activeEntry() ||
      (self.activeEntry().definition() &&
        (self.activeEntry().definition().path !== '/' || self.activeEntry().definition().uuid))
    ) {
      apiHelper.setInTotalStorage('assist', 'last.opened.assist.doc.uuid', null);
      self.activeEntry(
        new HueFileEntry({
          activeEntry: self.activeEntry,
          trashEntry: ko.observable(),
          app: 'documents',
          user: self.user,
          activeSort: self.activeSort,
          typeFilter: self.typeFilter,
          definition: {
            name: '/',
            type: 'directory'
          }
        })
      );
      self.activeEntry().load();
    }
  }

  init() {
    const self = this;
    if (!self.activeEntry().loaded()) {
      self.activeEntry().load(
        () => {},
        () => {
          self.fallbackToRoot();
        },
        true
      );
    }
  }
}

export default AssistDocumentsPanel;

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

import ko from 'knockout';

import 'ko/components/ko.catalogEntriesList';

import componentUtils from './componentUtils';
import dataCatalog from 'catalog/dataCatalog';

const TEMPLATE = `
  <div>
    <!-- ko hueSpinner: { spin: !catalogEntryExists(), inline: true } --><!-- /ko -->
    <!-- ko if: catalogEntryExists -->
      <!-- ko component: { name: 'catalog-entries-list', params: {
        catalogEntry: catalogEntry,
        selectedEntries: selectedEntries,
        editableDescriptions: editableDescriptions,
        contextPopoverEnabled: contextPopoverEnabled,
        onSampleClick: onSampleClick,
        refreshSampleInterval: refreshSampleInterval
      }} --><!-- /ko -->
    <!-- /ko -->
  </div>
`;

class PollingCatalogEntriesList {
  /**
   * This is the same as the 'catalog-entries-list' component with the difference that this
   * one waits until a catalog entry exists.
   *
   * Example usage:
   *
   * <div data-bind="component: { name: 'polling-catalog-entries-list', params: {
   *   sourceType: sourceType,
   *   namespace: ko.observable({ id: 'default' }),
   *   compute: ko.observable({ id: 'default' }),
   *   path: ko.observable('default.foo'),
   *   refreshSampleInterval: 3000
   * }}" />
   *
   * @param params
   * @constructor
   */

  constructor(params) {
    const self = this;
    self.selectedEntries = params.selectedEntries;
    self.editableDescriptions = params.editableDescriptions;
    self.contextPopoverEnabled = params.contextPopoverEnabled;
    self.onSampleClick = params.onSampleClick;
    self.sourceType = params.sourceType;
    self.namespace = params.namespace;
    self.compute = params.compute;
    self.path = params.path;
    self.refreshSampleInterval = params.refreshSampleInterval;

    self.pollTimeout = -1;
    self.pollCount = 0;

    self.disposals = [];

    self.lastPollSourceMetaPromise = undefined;

    self.catalogEntryExists = ko.observable(false);
    self.catalogEntry = ko.observable();

    self.intialize();

    if (ko.isObservable(self.path)) {
      const pathSub = self.path.subscribe(newValue => {
        if (newValue) {
          self.intialize();
        }
      });
      self.disposals.push(() => {
        pathSub.dispose();
      });
    }
  }

  pollForSourceMeta() {
    const self = this;
    window.clearTimeout(self.pollTimeout);

    const pollInternal = function() {
      self.pollCount++;
      if (self.catalogEntry()) {
        self.lastPollSourceMetaPromise = self
          .catalogEntry()
          .getSourceMeta({
            silenceErrors: true,
            refreshCache: self.pollCount > 0,
            cancellable: true
          })
          .done(sourceMeta => {
            if (sourceMeta.notFound) {
              self.pollForSourceMeta();
            } else {
              self.catalogEntryExists(true);
            }
          })
          .fail(() => {
            self.pollForSourceMeta();
          });
      }
    };

    if (self.pollCount === 0) {
      pollInternal();
    } else {
      self.pollTimeout = window.setTimeout(pollInternal, Math.min(1000 * self.pollCount, 3000));
    }
  }

  intialize() {
    const self = this;
    self.pollCount = 0;
    window.clearTimeout(self.pollTimeout);
    self.catalogEntryExists(false);

    if (self.lastPollSourceMetaPromise && self.lastPollSourceMetaPromise.cancel) {
      self.lastPollSourceMetaPromise.cancel();
    }

    dataCatalog
      .getEntry({
        sourceType: ko.unwrap(self.sourceType),
        namespace: ko.unwrap(self.namespace),
        compute: ko.unwrap(self.compute),
        path: ko.unwrap(self.path)
      })
      .done(catalogEntry => {
        self.catalogEntry(catalogEntry);
        self.pollForSourceMeta();
      });
  }

  dispose() {
    const self = this;
    window.clearTimeout(self.pollTimeout);
    if (self.lastPollSourceMetaPromise && self.lastPollSourceMetaPromise.cancel) {
      self.lastPollSourceMetaPromise.cancel();
    }
    while (self.disposals.length) {
      self.disposals.pop()();
    }
  }
}

componentUtils.registerComponent(
  'polling-catalog-entries-list',
  PollingCatalogEntriesList,
  TEMPLATE
);

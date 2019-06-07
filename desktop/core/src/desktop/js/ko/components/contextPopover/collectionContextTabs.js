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
import I18n from 'utils/i18n';

class CollectionContextTabs {
  constructor(data) {
    const self = this;

    self.disposals = [];

    self.catalogEntry = data.catalogEntry;

    self.data = ko.observable({
      details: data,
      loading: ko.observable(false),
      hasErrors: ko.observable(false),
      selectedPath: ko.observable(data.path),
      loadingTerms: ko.observable(false),
      loadingStats: ko.observable(false),
      statsSupported: ko.observable(true),
      terms: ko.mapping.fromJS({ prefix: '', data: [] }),
      stats: ko.mapping.fromJS({ facet: '', data: [] })
    });

    self.data().terms.prefix.subscribe(() => {
      self.loadTerms();
    });
    self
      .data()
      .terms.prefix.extend({ rateLimit: { timeout: 500, method: 'notifyWhenChangesStop' } });

    self.loadTerms();
    self.loadStats();

    self.tabs = [
      {
        id: 'terms',
        label: I18n('Terms'),
        template: 'context-popover-collection-terms-details',
        templateData: self.data
      },
      {
        id: 'stats',
        label: I18n('Stats'),
        template: 'context-popover-collection-stats-details',
        templateData: self.data
      }
    ];
    self.activeTab = ko.observable('terms');

    const showInAssistPubSub = huePubSub.subscribe('context.popover.show.in.assist', () => {
      huePubSub.publish('assist.db.highlight', self.catalogEntry);
    });
    self.disposals.push(() => {
      showInAssistPubSub.remove();
    });
  }

  loadTerms() {
    const self = this;
    self.data().terms.data.removeAll();
    self.data().loadingTerms(true);
    apiHelper.fetchDashboardTerms({
      collectionName: self.catalogEntry.path[1],
      fieldName: self.catalogEntry.path[2],
      prefix: self.data().terms.prefix(),
      engine: 'solr',
      successCallback: function(data) {
        if (data.terms != null) {
          $.each(data.terms, (key, val) => {
            self.data().terms.data.push({ key: key, val: val });
          });
        }
      },
      alwaysCallback: function() {
        self.data().loadingTerms(false);
      }
    });
  }

  loadStats() {
    const self = this;
    self.data().terms.data.removeAll();
    self.data().loadingStats(true);
    self.data().statsSupported(true);
    const fieldName = self.catalogEntry.path[2];
    apiHelper.fetchDashboardStats({
      collectionName: self.catalogEntry.path[1],
      fieldName: fieldName,
      engine: 'solr',
      successCallback: function(data) {
        if (data.stats.stats.stats_fields[fieldName] != null) {
          $.each(data.stats.stats.stats_fields[fieldName], (key, val) => {
            self.data().stats.data.push({ key: key, val: val });
          });
        }
      },
      notSupportedCallback: function() {
        self.data().statsSupported(false);
      },
      alwaysCallback: function() {
        self.data().loadingStats(false);
      }
    });
  }

  dispose() {
    const self = this;
    while (self.disposals.length) {
      self.disposals.pop()();
    }
  }
}

export default CollectionContextTabs;

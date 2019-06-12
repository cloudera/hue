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

class DataCatalogContext {
  constructor(options) {
    const self = this;
    self.popover = options.popover;
    self.catalogEntry = ko.observable(options.catalogEntry);

    self.loading = ko.observable(false);
    self.hasErrors = ko.observable(false);
    self.activePromises = [];
    self.errorText = ko.observable();

    self.onSampleClick = options.popover.onSampleClick;

    self.analysis = ko.observable();
    self.comment = ko.observable();
    self.commentExpanded = ko.observable(false);
    self.viewSql = ko.observable();
    self.viewSqlVisible = ko.observable(false);

    self.openActionsEnabled = ko.pureComputed(() => {
      return self.catalogEntry() && self.catalogEntry().path.length <= 2;
    });

    self.catalogEntry.subscribe(self.load.bind(self));

    self.breadCrumbs = ko.pureComputed(() => {
      const result = [];
      const catalogEntry = self.catalogEntry();
      if (catalogEntry) {
        for (let i = 0; i < catalogEntry.path.length; i++) {
          result.push({
            name: catalogEntry.path[i],
            isActive: i === catalogEntry.path.length - 1,
            path: catalogEntry.path.slice(0, i + 1),
            catalogEntry: self.catalogEntry,
            makeActive: function() {
              self
                .catalogEntry()
                .dataCatalog.getEntry({
                  namespace: self.catalogEntry().namespace,
                  compute: self.catalogEntry().compute,
                  path: this.path,
                  temporaryOnly: self.catalogEntry().isTemporary
                })
                .done(self.catalogEntry);
            }
          });
        }
      }
      return result;
    });
    self.originalCatalogEntry = options.catalogEntry;
    self.load();
  }

  refresh() {
    const self = this;
    self
      .catalogEntry()
      .clearCache({ invalidate: 'invalidate', cascade: true })
      .always(self.load.bind(self));
  }

  load() {
    const self = this;
    self.loading(true);
    self.hasErrors(false);
    self.cancelActivePromises();

    const viewSqlDeferred = $.Deferred().done(self.viewSql);
    self.activePromises.push(viewSqlDeferred.promise());

    self.activePromises.push(
      self
        .catalogEntry()
        .getSourceMeta({ cancellable: true })
        .fail(() => {
          self.hasErrors(true);
        })
        .always(() => {
          self.loading(false);
        })
    );

    if (
      self.catalogEntry().getSourceType() === 'impala' ||
      self.catalogEntry().getSourceType() === 'hive'
    ) {
      self.activePromises.push(
        self
          .catalogEntry()
          .getAnalysis({
            silenceErrors: true,
            cancellable: true
          })
          .done(analysis => {
            const found =
              analysis.properties &&
              analysis.properties.some(property => {
                if (property.col_name.toLowerCase() === 'view original text:') {
                  apiHelper
                    .formatSql({ statements: property.data_type })
                    .done(formatResponse => {
                      if (formatResponse.status === 0) {
                        viewSqlDeferred.resolve(formatResponse.formatted_statements);
                      } else {
                        viewSqlDeferred.resolve(property.data_type);
                      }
                    })
                    .fail(() => {
                      viewSqlDeferred.resolve(property.data_type);
                    });
                  return true;
                }
              });
            if (!found) {
              viewSqlDeferred.resolve();
            }
            self.analysis(analysis);
          })
          .fail(viewSqlDeferred.reject)
      );
    } else {
      viewSqlDeferred.reject();
    }

    self.activePromises.push(
      self
        .catalogEntry()
        .getComment({ silenceErrors: true, cancellable: true })
        .done(self.comment)
    );

    $.when.apply($, self.activePromises).always(() => {
      self.activePromises.length = 0;
    });
  }

  cancelActivePromises() {
    const self = this;
    while (self.activePromises.length) {
      const promise = self.activePromises.pop();
      if (promise.cancel) {
        promise.cancel();
      }
    }
  }

  dispose() {
    const self = this;
    self.cancelActivePromises();
  }

  showInAssist() {
    const self = this;
    huePubSub.publish('assist.db.highlight', self.catalogEntry());
    huePubSub.publish('global.search.close');
  }

  openInDashboard() {
    const self = this;
    huePubSub.publish(
      'open.link',
      '/hue/dashboard/browse/' +
        self.catalogEntry().path.join('.') +
        '?engine=' +
        self.catalogEntry().getSourceType()
    );
    huePubSub.publish('context.popover.hide');
    huePubSub.publish('global.search.close');
  }

  openInTableBrowser() {
    const self = this;
    huePubSub.publish(
      'open.link',
      '/metastore/table' +
        (self.catalogEntry().isTableOrView() ? '/' : 's/') +
        self.catalogEntry().path.join('/') +
        '?source_type=' +
        self.catalogEntry().getSourceType() +
        '&namespace=' +
        self.catalogEntry().namespace.id
    );
    huePubSub.publish('context.popover.hide');
    huePubSub.publish('global.search.close');
  }
}

export default DataCatalogContext;

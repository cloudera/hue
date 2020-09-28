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
import * as ko from 'knockout';

import apiHelper from 'api/apiHelper';
import dataCatalog from 'catalog/dataCatalog';
import huePubSub from 'utils/huePubSub';
import MetastoreDatabase from 'apps/tableBrowser/metastoreDatabase';

class MetastoreNamespace {
  constructor(options) {
    this.namespace = options.namespace;

    // TODO: Compute selection in the metastore?
    this.compute = options.namespace.computes[0];
    this.id = options.namespace.id;
    this.name = options.namespace.name;
    this.metastoreViewModel = options.metastoreViewModel;
    this.sourceType = options.sourceType;
    this.navigatorEnabled = options.navigatorEnabled;
    this.optimizerEnabled = options.optimizerEnabled;

    this.catalogEntry = ko.observable();

    this.database = ko.observable();
    this.databases = ko.observableArray();
    this.selectedDatabases = ko.observableArray();
    this.loading = ko.observable(false);
    this.lastLoadDatabasesPromise = undefined;
  }

  loadDatabases() {
    if (this.loading() && this.lastLoadDatabasesPromise) {
      return this.lastLoadDatabasesPromise;
    }

    this.loading(true);
    const deferred = $.Deferred();
    this.lastLoadDatabasesPromise = deferred.promise();

    deferred
      .fail(() => {
        this.databases([]);
      })
      .always(() => {
        this.loading(false);
      });

    // TODO: Use connectors in the table browser
    const connector = {
      type: this.sourceType,
      id: this.sourceType,
      dialect: this.sourceType
    };
    if (this.sourceType === 'hive' || this.sourceType === 'impala') {
      connector.optimizer = 'api';
    }
    dataCatalog
      .getEntry({
        namespace: this.namespace,
        compute: this.compute,
        connector: connector,
        path: [],
        definition: { type: 'source' }
      })
      .done(entry => {
        this.catalogEntry(entry);
        entry
          .getChildren()
          .done(databaseEntries => {
            this.databases(
              databaseEntries.map(
                databaseEntry =>
                  new MetastoreDatabase({
                    catalogEntry: databaseEntry,
                    optimizerEnabled: this.optimizerEnabled,
                    metastoreViewModel: this.metastoreViewModel
                  })
              )
            );
            deferred.resolve();
          })
          .fail(deferred.reject);
      });

    return this.lastLoadDatabasesPromise;
  }

  reload() {
    if (!this.loading() && this.catalogEntry()) {
      this.loading(true);
      // Clear will publish when done
      this.catalogEntry().clearCache();
    }
  }

  setDatabase(metastoreDatabase, callback) {
    huePubSub.publish('metastore.scroll.to.top');
    this.database(metastoreDatabase);

    if (!metastoreDatabase.loaded()) {
      metastoreDatabase.load(
        callback,
        this.optimizerEnabled(),
        this.navigatorEnabled(),
        this.sourceType
      );
    } else if (callback) {
      callback();
    }
  }

  onDatabaseClick(catalogEntry) {
    this.databases().some(database => {
      if (database.catalogEntry === catalogEntry) {
        this.setDatabase(database, () => {
          huePubSub.publish('metastore.url.change');
        });
        if (this.database()) {
          this.database().table(null);
        }
        return true;
      }
    });
  }

  setDatabaseByName(databaseName, callback) {
    const whenLoaded = clearCacheOnMissing => {
      if (!databaseName) {
        databaseName =
          apiHelper.getFromTotalStorage('editor', 'last.selected.database') ||
          apiHelper.getFromTotalStorage('metastore', 'last.selected.database') ||
          'default';
        clearCacheOnMissing = false;
      }
      if (this.database() && this.database().catalogEntry.name === databaseName) {
        if (callback) {
          callback();
        }
        return;
      }
      let foundDatabases = this.databases().filter(
        database => database.catalogEntry.name === databaseName
      );

      if (foundDatabases.length === 1) {
        this.setDatabase(foundDatabases[0], callback);
      } else if (clearCacheOnMissing) {
        this.catalogEntry()
          .clearCache({ silenceErrors: true })
          .then(() => {
            this.loadDatabases().done(() => {
              whenLoaded(false);
            });
          });
      } else {
        foundDatabases = this.databases().filter(
          database => database.catalogEntry.name === 'default'
        );

        if (foundDatabases.length === 1) {
          this.setDatabase(foundDatabases[0], callback);
        } else {
        }
      }
    };

    window.setTimeout(() => {
      if (this.loading() && this.lastLoadDatabasesPromise !== null) {
        this.lastLoadDatabasesPromise.done(() => {
          whenLoaded(true);
        });
      } else if (this.databases().length) {
        whenLoaded(true);
      } else {
        this.loadDatabases().done(() => {
          whenLoaded(true);
        });
      }
    }, 0);
  }
}

export default MetastoreNamespace;

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

import dataCatalog from 'catalog/dataCatalog';
import huePubSub from 'utils/huePubSub';
import sqlUtils from 'sql/sqlUtils';

const attachEntryResolver = function(location, sourceType, namespace, compute) {
  location.resolveCatalogEntry = function(options) {
    if (!options) {
      options = {};
    }
    if (location.resolvePathPromise && !location.resolvePathPromise.cancelled) {
      dataCatalog.applyCancellable(location.resolvePathPromise, options);
      return location.resolvePathPromise;
    }

    if (!location.identifierChain && !location.colRef && !location.colRef.identifierChain) {
      if (!location.resolvePathPromise) {
        location.resolvePathPromise = $.Deferred()
          .reject()
          .promise();
      }
      return location.resolvePathPromise;
    }

    const promise = sqlUtils.resolveCatalogEntry({
      sourceType: sourceType,
      namespace: namespace,
      compute: compute,
      temporaryOnly: options.temporaryOnly,
      cancellable: options.cancellable,
      cachedOnly: options.cachedOnly,
      identifierChain: location.identifierChain || location.colRef.identifierChain,
      tables: location.tables || (location.colRef && location.colRef.tables)
    });

    if (!options.cachedOnly) {
      location.resolvePathPromise = promise;
    }
    return promise;
  };
};

let registered = false;

export default {
  registerWorkers: function() {
    if (!window.IS_EMBEDDED && !registered && window.Worker) {
      // It can take a while before the worker is active
      const whenWorkerIsReady = function(worker, message) {
        if (!worker.isReady) {
          window.clearTimeout(worker.pingTimeout);
          worker.postMessage({ ping: true });
          worker.pingTimeout = window.setTimeout(() => {
            whenWorkerIsReady(worker, message);
          }, 500);
        } else {
          worker.postMessage(message);
        }
      };

      // For syntax checking
      const aceSqlSyntaxWorker = new Worker(
        window.HUE_BASE_URL + '/desktop/workers/aceSqlSyntaxWorker.js?v=' + window.HUE_VERSION
      );
      aceSqlSyntaxWorker.onmessage = function(e) {
        if (e.data.ping) {
          aceSqlSyntaxWorker.isReady = true;
        } else {
          huePubSub.publish('ace.sql.syntax.worker.message', e);
        }
      };

      huePubSub.subscribe('ace.sql.syntax.worker.post', message => {
        whenWorkerIsReady(aceSqlSyntaxWorker, message);
      });

      // For location marking
      const aceSqlLocationWorker = new Worker(
        window.HUE_BASE_URL + '/desktop/workers/aceSqlLocationWorker.js?v=' + window.HUE_VERSION
      );
      aceSqlLocationWorker.onmessage = function(e) {
        if (e.data.ping) {
          aceSqlLocationWorker.isReady = true;
        } else {
          if (e.data.locations) {
            e.data.locations.forEach(location => {
              attachEntryResolver(location, e.data.sourceType, e.data.namespace, e.data.compute);
            });
          }
          huePubSub.publish('ace.sql.location.worker.message', e);
        }
      };

      huePubSub.subscribe('ace.sql.location.worker.post', message => {
        whenWorkerIsReady(aceSqlLocationWorker, message);
      });

      registered = true;
    }
  }
};

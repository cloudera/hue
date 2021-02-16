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

import huePubSub from 'utils/huePubSub';
import { resolveCatalogEntry } from 'sql/sqlUtils';
import { applyCancellable } from '../catalog/catalogUtils';

export const POST_TO_LOCATION_WORKER_EVENT = 'ace.sql.location.worker.post';
export const POST_FROM_LOCATION_WORKER_EVENT = 'ace.sql.location.worker.message';
export const POST_TO_SYNTAX_WORKER_EVENT = 'ace.sql.syntax.worker.post';
export const POST_FROM_SYNTAX_WORKER_EVENT = 'ace.sql.syntax.worker.message';

const attachEntryResolver = function (location, connector, namespace, compute) {
  location.resolveCatalogEntry = function (options) {
    if (!options) {
      options = {};
    }
    if (location.resolvePathPromise && !location.resolvePathPromise.cancelled) {
      applyCancellable(location.resolvePathPromise, options);
      return location.resolvePathPromise;
    }

    if (!location.identifierChain && !location.colRef && !location.colRef.identifierChain) {
      if (!location.resolvePathPromise) {
        location.resolvePathPromise = $.Deferred().reject().promise();
      }
      return location.resolvePathPromise;
    }

    const promise = resolveCatalogEntry({
      connector: connector,
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
  registerWorkers: function () {
    if (!registered && window.Worker) {
      // It can take a while before the worker is active
      const whenWorkerIsReady = function (worker, message) {
        message.hueBaseUrl = window.HUE_BASE_URL;
        if (!worker.isReady) {
          window.clearTimeout(worker.pingTimeout);
          worker.postMessage({ ping: true, hueBaseUrl: message.hueBaseUrl });
          worker.pingTimeout = window.setTimeout(() => {
            whenWorkerIsReady(worker, message);
          }, 500);
        } else {
          // To JSON and back as Vue creates proxy objects with methods which are not serializable
          worker.postMessage(JSON.parse(JSON.stringify(message)));
        }
      };

      // For syntax checking
      const aceSqlSyntaxWorker = new Worker(
        window.HUE_BASE_URL +
          '/desktop/workers/aceSqlSyntaxWorker.js?v=' +
          window.HUE_VERSION +
          '.1'
      );
      aceSqlSyntaxWorker.onmessage = function (e) {
        if (e.data.ping) {
          aceSqlSyntaxWorker.isReady = true;
        } else {
          huePubSub.publish(POST_FROM_SYNTAX_WORKER_EVENT, e);
        }
      };

      huePubSub.subscribe(POST_TO_SYNTAX_WORKER_EVENT, message => {
        whenWorkerIsReady(aceSqlSyntaxWorker, message);
      });

      // For location marking
      const aceSqlLocationWorker = new Worker(
        window.HUE_BASE_URL +
          '/desktop/workers/aceSqlLocationWorker.js?v=' +
          window.HUE_VERSION +
          '.1'
      );
      aceSqlLocationWorker.onmessage = function (e) {
        if (e.data.ping) {
          aceSqlLocationWorker.isReady = true;
        } else {
          if (e.data.locations) {
            e.data.locations.forEach(location => {
              attachEntryResolver(location, e.data.connector, e.data.namespace, e.data.compute);
            });
          }
          huePubSub.publish(POST_FROM_LOCATION_WORKER_EVENT, e);
        }
      };

      huePubSub.subscribe(POST_TO_LOCATION_WORKER_EVENT, message => {
        whenWorkerIsReady(aceSqlLocationWorker, message);
      });

      registered = true;
    }
  }
};

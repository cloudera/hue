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

import {
  POST_FROM_LOCATION_WORKER_EVENT,
  POST_FROM_SYNTAX_WORKER_EVENT,
  POST_TO_LOCATION_WORKER_EVENT,
  POST_TO_SYNTAX_WORKER_EVENT
} from './events';
import { resolveCatalogEntry } from '../sqlUtils';
import { CancellablePromise } from 'api/cancellablePromise';
import { applyCancellable } from 'catalog/catalogUtils';
import DataCatalogEntry from 'catalog/DataCatalogEntry';
import { Compute, Connector, Namespace } from 'config/types';
import { IdentifierChainEntry, IdentifierLocation, ParsedTable } from 'parse/types';
import { hueWindow } from 'types/types';
import huePubSub from 'utils/huePubSub';

const whenWorkerIsReady = (
  worker: Worker & { isReady?: boolean; pingTimeout?: number },
  message: unknown & { hueBaseUrl?: string }
): void => {
  if (window) {
    message.hueBaseUrl = (<hueWindow>window).HUE_BASE_URL;
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
  }
};

const attachEntryResolver = (
  location: IdentifierLocation & {
    resolvePathPromise?: CancellablePromise<DataCatalogEntry>;
  },
  connector: Connector,
  namespace: Namespace,
  compute: Compute
): void => {
  location.resolveCatalogEntry = (options): CancellablePromise<DataCatalogEntry> => {
    if (!options) {
      options = {};
    }
    if (location.resolvePathPromise && !location.resolvePathPromise.cancelled) {
      applyCancellable(location.resolvePathPromise, options);
      return location.resolvePathPromise;
    }

    if (!location.identifierChain && !location.colRef) {
      if (!location.resolvePathPromise) {
        location.resolvePathPromise = CancellablePromise.reject();
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
      identifierChain:
        location.identifierChain ||
        (<{ identifierChain: IdentifierChainEntry[] }>location.colRef).identifierChain,
      tables:
        location.tables ||
        (location.colRef && (<{ tables: ParsedTable[] }>location.colRef).tables) ||
        undefined
    });

    if (!options.cachedOnly) {
      location.resolvePathPromise = promise;
    }
    return promise;
  };
};

export const attachSyntaxWorkerEvents = (syntaxWorker?: Worker & { isReady?: boolean }): void => {
  if (!syntaxWorker) {
    return;
  }
  syntaxWorker.onmessage = function (e) {
    if (e.data.ping) {
      syntaxWorker.isReady = true;
    } else {
      huePubSub.publish(POST_FROM_SYNTAX_WORKER_EVENT, e);
    }
  };

  huePubSub.subscribe(POST_TO_SYNTAX_WORKER_EVENT, message => {
    whenWorkerIsReady(syntaxWorker, message);
  });
};

export const attachLocationWorkerEvents = (
  locationWorker?: Worker & { isReady?: boolean }
): void => {
  if (!locationWorker) {
    return;
  }
  locationWorker.onmessage = function (e) {
    if (e.data.ping) {
      locationWorker.isReady = true;
    } else {
      if (e.data.locations) {
        (e.data.locations as IdentifierLocation[]).forEach(location => {
          attachEntryResolver(location, e.data.connector, e.data.namespace, e.data.compute);
        });
      }
      huePubSub.publish(POST_FROM_LOCATION_WORKER_EVENT, e);
    }
  };

  huePubSub.subscribe(POST_TO_LOCATION_WORKER_EVENT, message => {
    whenWorkerIsReady(locationWorker, message);
  });
};

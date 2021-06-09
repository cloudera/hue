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

import localforage from 'localforage';

import { fetchClusters, fetchComputes, fetchNamespaces } from './api';
import { Cluster, Compute, IdentifiableInterpreter, Namespace } from 'config/types';
import huePubSub from 'utils/huePubSub';
import { hueWindow } from 'types/types';
import noop from 'utils/timing/noop';
import {
  CONTEXT_CATALOG_REFRESHED_TOPIC,
  NAMESPACES_REFRESHED_TOPIC,
  NamespacesRefreshedEvent,
  REFRESH_CONTEXT_CATALOG_TOPIC
} from './events';

export interface GetOptions {
  connector: IdentifiableInterpreter;
  clearCache?: boolean;
  silenceErrors?: boolean;
}

export interface ConnectorNamespaces {
  dynamic?: boolean;
  hueTimestamp: number;
  namespaces: Namespace[];
}

enum ContextTypes {
  Namespace = 'namespace',
  Compute = 'compute',
  Cluster = 'cluster'
}

interface ContextMapping {
  [ContextTypes.Cluster]: Cluster[];
  [ContextTypes.Compute]: Compute[];
  [ContextTypes.Namespace]: ConnectorNamespaces;
}

const STORAGE_POSTFIX = (<hueWindow>window).LOGGED_USERNAME;
const CONTEXT_CATALOG_VERSION = 4;
const DISABLE_CACHE = true;

const store = localforage.createInstance({
  name: `HueContextCatalog_${STORAGE_POSTFIX}`
});

const namespacePromises = new Map<string, Promise<ConnectorNamespaces>>();
const computePromises = new Map<string, Promise<Compute[]>>();
const clusterPromises = new Map<string, Promise<Cluster[]>>();

huePubSub.subscribe(REFRESH_CONTEXT_CATALOG_TOPIC, async () => {
  const namespacesToRefresh = [...namespacePromises.keys()];
  namespacePromises.clear();
  computePromises.clear();
  clusterPromises.clear();
  try {
    await store.clear();
  } catch {}
  huePubSub.publish(CONTEXT_CATALOG_REFRESHED_TOPIC);
  namespacesToRefresh.forEach(connectorId => {
    huePubSub.publish<NamespacesRefreshedEvent>(NAMESPACES_REFRESHED_TOPIC, connectorId);
  });
});

const saveLaterToCache = <T extends keyof ContextMapping>(
  type: T,
  connector: IdentifiableInterpreter,
  entry: ContextMapping[T]
) => {
  if (entry) {
    window.setTimeout(async () => {
      try {
        await store.setItem<{ version: number; entry: ContextMapping[T] }>(
          `${type}_${connector.id}`,
          {
            version: CONTEXT_CATALOG_VERSION,
            entry
          }
        );
      } catch {}
    }, 1000);
  }
};

const deleteFromCache = async (type: keyof ContextMapping, connector: IdentifiableInterpreter) => {
  await store.removeItem(`${type}_${connector.id}`);
};

const getCached = async <T extends keyof ContextMapping>(
  type: T,
  connector: IdentifiableInterpreter
): Promise<ContextMapping[T] | undefined> => {
  if (!DISABLE_CACHE) {
    try {
      const storedItem = await store.getItem<
        { version: number; entry: ContextMapping[T] } | undefined
      >(`${type}_${connector.id}`);

      if (storedItem && storedItem.version === CONTEXT_CATALOG_VERSION) {
        return storedItem.entry;
      }
    } catch (err) {
      console.warn(err);
    }
  }
  return undefined;
};

export const getNamespaces = async ({
  connector,
  clearCache,
  silenceErrors
}: GetOptions): Promise<ConnectorNamespaces> => {
  const notifyForRefresh = namespacePromises.has(connector.id) && clearCache;
  if (clearCache) {
    namespacePromises.delete(connector.id);
    await deleteFromCache(ContextTypes.Namespace, connector);
  }

  if (!namespacePromises.has(connector.id)) {
    namespacePromises.set(
      connector.id,
      new Promise<ConnectorNamespaces>(async (resolve, reject) => {
        try {
          const cached = await getCached(ContextTypes.Namespace, connector);
          if (cached) {
            resolve(cached);
            return;
          }
        } catch {}

        const fetchedNamespaces = await fetchNamespaces(connector, silenceErrors);
        const namespaces = fetchedNamespaces[connector.id];
        if (namespaces) {
          const dynamic = fetchedNamespaces.dynamicClusters;
          namespaces.forEach(namespace => {
            // Adapt computes, TODO: Still needed?
            namespace.computes.forEach(
              (compute: Compute & { crn?: string; clusterName?: string }) => {
                if (!compute.id && compute.crn) {
                  compute.id = compute.crn;
                }
                if (!compute.name && compute.clusterName) {
                  compute.name = compute.clusterName;
                }
              }
            );
          });

          const connectorNamespaces: ConnectorNamespaces = {
            namespaces: namespaces.filter(namespace => namespace.name),
            dynamic,
            hueTimestamp: Date.now()
          };

          resolve(connectorNamespaces);

          if (notifyForRefresh) {
            huePubSub.publish<NamespacesRefreshedEvent>(NAMESPACES_REFRESHED_TOPIC, connector.id);
          }

          if (connectorNamespaces.namespaces.length) {
            saveLaterToCache(ContextTypes.Namespace, connector, connectorNamespaces);
          } else {
            deleteFromCache(ContextTypes.Namespace, connector).catch(noop);
          }
        } else {
          reject();
        }
      })
    );
  }

  return namespacePromises.get(connector.id)!;
};

export const getComputes = async ({
  connector,
  clearCache,
  silenceErrors
}: GetOptions): Promise<Compute[]> => {
  if (clearCache) {
    computePromises.delete(connector.id);
    await deleteFromCache(ContextTypes.Compute, connector);
  }

  if (!computePromises.has(connector.id)) {
    computePromises.set(
      connector.id,
      new Promise<Compute[]>(async (resolve, reject) => {
        try {
          const cached = await getCached(ContextTypes.Compute, connector);
          if (cached) {
            resolve(cached);
            return;
          }
        } catch {}

        const fetchedComputes = await fetchComputes(connector, silenceErrors);
        const computes = fetchedComputes[connector.id];
        if (computes) {
          resolve(computes);

          if (computes.length) {
            saveLaterToCache(ContextTypes.Compute, connector, computes);
          } else {
            deleteFromCache(ContextTypes.Compute, connector).catch(noop);
          }
        } else {
          reject();
        }
      })
    );
  }

  return computePromises.get(connector.id)!;
};

export const getClusters = async ({
  connector,
  clearCache,
  silenceErrors
}: GetOptions): Promise<Cluster[]> => {
  if (clearCache) {
    clusterPromises.delete(connector.id);
    await deleteFromCache(ContextTypes.Cluster, connector);
  }

  if (!clusterPromises.has(connector.id)) {
    clusterPromises.set(
      connector.id,
      new Promise<Cluster[]>(async (resolve, reject) => {
        try {
          const cached = await getCached(ContextTypes.Cluster, connector);
          if (cached) {
            resolve(cached);
            return;
          }
        } catch {}

        const fetchedClusters = await fetchClusters(connector, silenceErrors);
        const clusters = fetchedClusters[connector.id];
        if (clusters) {
          resolve(clusters);

          if (clusters.length) {
            saveLaterToCache(ContextTypes.Cluster, connector, clusters);
          } else {
            deleteFromCache(ContextTypes.Cluster, connector).catch(noop);
          }
        } else {
          reject();
        }
      })
    );
  }

  return clusterPromises.get(connector.id)!;
};

export default {
  getNamespaces,
  getComputes,
  getClusters
};

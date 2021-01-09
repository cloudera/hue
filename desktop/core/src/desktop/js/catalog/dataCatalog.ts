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

import { Cancellable, CancellablePromise } from 'api/cancellablePromise';
import { applyCancellable } from 'catalog/catalogUtils';
import DataCatalogEntry, {
  Analysis,
  Definition,
  ExtendedColumn,
  FieldSample,
  NavigatorMeta,
  OptimizerMeta,
  Partitions,
  Sample,
  SourceMeta,
  TableSourceMeta
} from 'catalog/DataCatalogEntry';
import GeneralDataCatalog from 'catalog/GeneralDataCatalog';
import MultiTableEntry, {
  TopAggs,
  TopColumns,
  TopFilters,
  TopJoins
} from 'catalog/MultiTableEntry';
import { getOptimizer, LOCAL_STRATEGY } from 'catalog/optimizer/optimizer';
import { Compute, Connector, Namespace } from 'types/config';
import { hueWindow } from 'types/types';

export interface TimestampedData {
  hueTimestamp?: number;
}

export interface CatalogGetOptions {
  silenceErrors?: boolean;
  cachedOnly?: boolean;
  refreshCache?: boolean;
  cancellable?: boolean;
}

export interface GetEntryOptions {
  path: string | string[];
  namespace: Namespace;
  compute: Compute;
  definition?: Definition;
  cachedOnly?: boolean;
  temporaryOnly?: boolean;
}

interface GetMultiTableEntryOptions {
  namespace: Namespace;
  compute: Compute;
  paths: string[][];
}

interface AddTemporaryTableOptions {
  name: string;
  namespace: Namespace;
  compute: Compute;
  database?: string;
  columns: { name: string; type: string }[];
  sample: FieldSample[][];
}

interface StoreEntry {
  version: number;
  definition?: Definition;
  sourceMeta?: SourceMeta;
  analysis?: Analysis;
  partitions?: Partitions;
  sample?: Sample;
  navigatorMeta?: NavigatorMeta;
  optimizerMeta?: OptimizerMeta;
  optimizerPopularity?: OptimizerPopularity;
}

interface StoreMultiTableEntry {
  version: number;
  topAggs?: TopAggs;
  topJoins?: TopJoins;
  topColumns?: TopColumns;
  topFilters?: TopFilters;
}

export interface OptimizerResponsePopularity {
  name?: string;
  columnCount: number;
  dbName?: string;
  tableName?: string;
  columnName?: string;
}

export interface OptimizerResponseValues {
  filterColumns?: OptimizerResponsePopularity[];
  groupbyColumns?: OptimizerResponsePopularity[];
  joinColumns?: OptimizerResponsePopularity[];
  orderbyColumns?: OptimizerResponsePopularity[];
  selectColumns?: OptimizerResponsePopularity[];
}

export interface OptimizerResponse extends TimestampedData {
  top_tables?: OptimizerResponsePopularity[];
  values?: OptimizerResponseValues;
}

export interface OptimizerPopularitySubType {
  filterColumn?: OptimizerResponsePopularity;
  groupByColumn?: OptimizerResponsePopularity;
  joinColumn?: OptimizerResponsePopularity;
  orderByColumn?: OptimizerResponsePopularity;
  selectColumn?: OptimizerResponsePopularity;
}

export interface OptimizerPopularity
  extends TimestampedData,
    OptimizerResponsePopularity,
    OptimizerPopularitySubType {
  column_count?: number;
  popularity?: number;
  relativePopularity?: number;
}

const STORAGE_POSTFIX = (<hueWindow>window).LOGGED_USERNAME || '';
const DATA_CATALOG_VERSION = 5;

let cacheEnabled = true;

/**
 * Creates a cache identifier given a namespace and path(s)
 */
const generateEntryCacheId = (options: {
  path?: string | string[];
  paths?: string[][];
  namespace: Namespace;
}): string => {
  let id = options.namespace.id;
  if (options.path) {
    if (typeof options.path === 'string') {
      id += '_' + options.path;
    } else if (options.path.length) {
      id += '_' + options.path.join('.');
    }
  } else if (options.paths && options.paths.length) {
    const pathSet: { [path: string]: boolean } = {};
    options.paths.forEach(path => {
      pathSet[path.join('.')] = true;
    });
    const uniquePaths = Object.keys(pathSet);
    uniquePaths.sort();
    id += '_' + uniquePaths.join(',');
  }
  return id;
};

const isFresh = (storeEntryValue: TimestampedData, ttl?: number) => {
  const confTtl = (<hueWindow>window).CACHEABLE_TTL || {};
  const ttlToCheck = typeof ttl !== 'undefined' ? ttl : confTtl.default;
  if (!storeEntryValue.hueTimestamp || typeof ttlToCheck === 'undefined') {
    return true;
  }
  return Date.now() - storeEntryValue.hueTimestamp < ttlToCheck;
};

/**
 * Helper function to fill a catalog entry with cached metadata.
 */
const mergeEntry = (dataCatalogEntry: DataCatalogEntry, storeEntry: StoreEntry): void => {
  if (storeEntry.version !== DATA_CATALOG_VERSION) {
    return;
  }

  if (storeEntry.definition && isFresh(storeEntry.definition)) {
    dataCatalogEntry.definition = storeEntry.definition;
  }
  if (storeEntry.sourceMeta && isFresh(storeEntry.sourceMeta)) {
    dataCatalogEntry.sourceMeta = storeEntry.sourceMeta;
    dataCatalogEntry.sourceMetaPromise = CancellablePromise.resolve(dataCatalogEntry.sourceMeta);
  }
  if (storeEntry.analysis && isFresh(storeEntry.analysis)) {
    dataCatalogEntry.analysis = storeEntry.analysis;
    dataCatalogEntry.analysisPromise = CancellablePromise.resolve(dataCatalogEntry.analysis);
  }
  if (storeEntry.partitions && isFresh(storeEntry.partitions)) {
    dataCatalogEntry.partitions = storeEntry.partitions;
    dataCatalogEntry.partitionsPromise = CancellablePromise.resolve(dataCatalogEntry.partitions);
  }
  if (storeEntry.sample && isFresh(storeEntry.sample)) {
    dataCatalogEntry.sample = storeEntry.sample;
    dataCatalogEntry.samplePromise = CancellablePromise.resolve(dataCatalogEntry.sample);
  }
  if (storeEntry.navigatorMeta && isFresh(storeEntry.navigatorMeta)) {
    dataCatalogEntry.navigatorMeta = storeEntry.navigatorMeta;
    dataCatalogEntry.navigatorMetaPromise = CancellablePromise.resolve(
      dataCatalogEntry.navigatorMeta
    );
  }
  if (dataCatalogEntry.getConnector().optimizer !== LOCAL_STRATEGY) {
    const confTtl = (<hueWindow>window).CACHEABLE_TTL || {};
    if (storeEntry.optimizerMeta && isFresh(storeEntry.optimizerMeta, confTtl.optimizer)) {
      dataCatalogEntry.optimizerMeta = storeEntry.optimizerMeta;
      dataCatalogEntry.optimizerMetaPromise = CancellablePromise.resolve(
        dataCatalogEntry.optimizerMeta
      );
    }
    if (
      storeEntry.optimizerPopularity &&
      isFresh(storeEntry.optimizerPopularity, confTtl.optimizer)
    ) {
      dataCatalogEntry.optimizerPopularity = storeEntry.optimizerPopularity;
    }
  }
};

/**
 * Helper function to fill a multi table catalog entry with cached metadata.
 */
const mergeMultiTableEntry = (
  multiTableEntry: MultiTableEntry,
  storeEntry: StoreMultiTableEntry
): void => {
  if (
    multiTableEntry.getConnector().optimizer === LOCAL_STRATEGY ||
    storeEntry.version !== DATA_CATALOG_VERSION
  ) {
    return;
  }
  const confTtl = (<hueWindow>window).CACHEABLE_TTL || {};
  if (storeEntry.topAggs && isFresh(storeEntry.topAggs, confTtl.optimizer)) {
    multiTableEntry.topAggs = storeEntry.topAggs;
    multiTableEntry.topAggsPromise = CancellablePromise.resolve(multiTableEntry.topAggs);
  }
  if (storeEntry.topColumns && isFresh(storeEntry.topColumns, confTtl.optimizer)) {
    multiTableEntry.topColumns = storeEntry.topColumns;
    multiTableEntry.topColumnsPromise = CancellablePromise.resolve(multiTableEntry.topColumns);
  }
  if (storeEntry.topFilters && isFresh(storeEntry.topFilters, confTtl.optimizer)) {
    multiTableEntry.topFilters = storeEntry.topFilters;
    multiTableEntry.topFiltersPromise = CancellablePromise.resolve(multiTableEntry.topFilters);
  }
  if (storeEntry.topJoins && isFresh(storeEntry.topJoins, confTtl.optimizer)) {
    multiTableEntry.topJoins = storeEntry.topJoins;
    multiTableEntry.topJoinsPromise = CancellablePromise.resolve(multiTableEntry.topJoins);
  }
};

export class DataCatalog {
  connector: Connector;
  entries: { [key: string]: Promise<DataCatalogEntry> } = {};
  temporaryEntries: { [key: string]: Promise<DataCatalogEntry> } = {};
  multiTableEntries: { [key: string]: Promise<MultiTableEntry> } = {};
  store: LocalForage;
  multiTableStore: LocalForage;

  invalidatePromise?: Promise<void>;

  constructor(connector: Connector) {
    if (!connector || !connector.id) {
      throw new Error('DataCatalog created without connector or id');
    }
    this.connector = connector;

    this.store = localforage.createInstance({
      name: 'HueDataCatalog_' + this.connector.id + '_' + STORAGE_POSTFIX
    });
    this.multiTableStore = localforage.createInstance({
      name: 'HueDataCatalog_' + this.connector.id + '_multiTable_' + STORAGE_POSTFIX
    });
  }

  /**
   * Disables the caching for subsequent operations, mainly used for test purposes
   */
  static disableCache(): void {
    cacheEnabled = false;
  }

  /**
   * Enables the cache for subsequent operations, mainly used for test purposes
   */
  static enableCache(): void {
    cacheEnabled = true;
  }

  static cacheEnabled(): boolean {
    return cacheEnabled;
  }

  /**
   * Returns true if the catalog can have Optimizer metadata
   */
  canHaveOptimizerMeta(): boolean {
    return !!(
      (<hueWindow>window).HAS_OPTIMIZER &&
      this.connector &&
      this.connector.optimizer &&
      this.connector.optimizer !== 'off'
    );
  }

  /**
   * Clears the data catalog and cache for the given path and any children thereof.
   */
  async clearStorageCascade(
    namespace?: Namespace,
    compute?: Compute,
    pathToClear?: string[]
  ): Promise<void> {
    if (!namespace || !compute) {
      if (!pathToClear || pathToClear.length === 0) {
        this.entries = {};
        return this.store.clear();
      }
      return;
    }

    const keyPrefix = generateEntryCacheId({ namespace: namespace, path: pathToClear });
    Object.keys(this.entries).forEach(key => {
      if (key.indexOf(keyPrefix) === 0) {
        delete this.entries[key];
      }
    });

    const deletePromises: Promise<void>[] = [];
    try {
      const keys = await this.store.keys();
      keys.forEach(key => {
        if (key.indexOf(keyPrefix) === 0) {
          deletePromises.push(this.store.removeItem(key));
        }
      });
      await Promise.all(deletePromises);
    } catch (err) {}
  }

  /**
   * Updates the cache for the given entry
   */
  async persistCatalogEntry(dataCatalogEntry: DataCatalogEntry): Promise<void> {
    const confTtl = (<hueWindow>window).CACHEABLE_TTL || {};
    if (!cacheEnabled || !confTtl.default || confTtl.default <= 0) {
      return;
    }
    const identifier = generateEntryCacheId(dataCatalogEntry);

    await this.store.setItem<StoreEntry>(identifier, {
      version: DATA_CATALOG_VERSION,
      definition: dataCatalogEntry.definition,
      sourceMeta: dataCatalogEntry.sourceMeta,
      analysis: dataCatalogEntry.analysis,
      partitions: dataCatalogEntry.partitions,
      sample: dataCatalogEntry.sample,
      navigatorMeta: dataCatalogEntry.navigatorMeta,
      optimizerMeta:
        this.connector.optimizer !== LOCAL_STRATEGY ? dataCatalogEntry.optimizerMeta : undefined,
      optimizerPopularity:
        this.connector.optimizer !== LOCAL_STRATEGY
          ? dataCatalogEntry.optimizerPopularity
          : undefined
    });
  }

  /**
   * Loads Navigator Optimizer popularity for multiple tables in one go.
   */
  loadOptimizerPopularityForTables(options: {
    namespace: Namespace;
    compute: Compute;
    paths: string[][];
    silenceErrors?: boolean;
    cancellable?: boolean;
  }): CancellablePromise<DataCatalogEntry[]> {
    const cancellablePromises: Cancellable[] = [];
    const popularEntries: DataCatalogEntry[] = [];
    const pathsToLoad: string[][] = [];

    const existingPromises: Promise<void>[] = [];
    options.paths.forEach(path => {
      const existingPromise = new Promise<void>(async (resolve, reject) => {
        try {
          const tableEntry = await this.getEntry({
            namespace: options.namespace,
            compute: options.compute,
            path: path
          });
          if (tableEntry.optimizerPopularityForChildrenPromise) {
            const existingPopularEntries = await tableEntry.optimizerPopularityForChildrenPromise;
            popularEntries.push(...existingPopularEntries);
          } else if (tableEntry.definition && tableEntry.definition.optimizerLoaded) {
            const childPromise = tableEntry.getChildren({ ...options, silenceErrors: true });
            cancellablePromises.push(childPromise);
            const childEntries = await childPromise;
            childEntries.forEach(childEntry => {
              if (childEntry.optimizerPopularity) {
                popularEntries.push(childEntry);
              }
            });
          } else {
            pathsToLoad.push(path);
          }
        } catch (err) {
          reject(err);
        }
        resolve();
      });
      existingPromises.push(existingPromise);
    });

    const popularityPromise = new CancellablePromise<DataCatalogEntry[]>(
      async (resolve, reject, onCancel) => {
        onCancel(() => {
          cancellablePromises.forEach(cancellable => {
            cancellable.cancel();
          });
        });
        try {
          await Promise.all(existingPromises);
        } catch (err) {}

        if (!pathsToLoad.length) {
          resolve(popularEntries);
          return;
        }

        const optimizer = getOptimizer(this.connector);

        const fetchPromise = optimizer.fetchPopularity({
          silenceErrors: true,
          paths: pathsToLoad
        });
        cancellablePromises.push(fetchPromise);

        try {
          const data = await fetchPromise;
          const perTable: { [path: string]: OptimizerResponse } = {};

          const splitOptimizerValuesPerTable = (listName: keyof OptimizerResponseValues): void => {
            const values = data.values && data.values[listName];
            if (values) {
              values.forEach(column => {
                let tableMeta = perTable[column.dbName + '.' + column.tableName];
                if (!tableMeta) {
                  tableMeta = { values: {} };
                  perTable[column.dbName + '.' + column.tableName] = tableMeta;
                }
                if (tableMeta.values) {
                  let valuesList = tableMeta.values[listName];
                  if (!valuesList) {
                    valuesList = [];
                    tableMeta.values[listName] = valuesList;
                  }
                  valuesList.push(column);
                }
              });
            }
          };

          if (data.values) {
            splitOptimizerValuesPerTable('filterColumns');
            splitOptimizerValuesPerTable('groupbyColumns');
            splitOptimizerValuesPerTable('joinColumns');
            splitOptimizerValuesPerTable('orderbyColumns');
            splitOptimizerValuesPerTable('selectColumns');
          }

          const tablePromises: Promise<void>[] = Object.keys(perTable).map(
            path =>
              new Promise<void>(async resolve => {
                try {
                  const entry = await this.getEntry({
                    namespace: options.namespace,
                    compute: options.compute,
                    path: path
                  });
                  const applyPromise = entry.applyOptimizerResponseToChildren(perTable[path], {
                    ...options,
                    silenceErrors: true
                  });
                  cancellablePromises.push(applyPromise);
                  popularEntries.push(...(await applyPromise));
                } catch (err) {}
                resolve();
              })
          );

          Promise.all(tablePromises).finally(() => {
            resolve(popularEntries);
          });
        } catch (err) {
          resolve(popularEntries);
        }
      }
    );
    return applyCancellable(popularityPromise);
  }

  async getKnownEntry(options: {
    namespace: Namespace;
    compute: Compute;
    path: string | string[];
  }): Promise<DataCatalogEntry> {
    return this.entries[generateEntryCacheId(options)];
  }

  /**
   * Adds a temporary table to the data catalog. This would allow autocomplete etc. of tables that haven't
   * been created yet.
   *
   * Calling this returns a handle that allows deletion of any created entries by calling delete() on the handle.
   */
  addTemporaryTable(options: AddTemporaryTableOptions): { delete: () => void } {
    const database = options.database || 'default';
    const path = [database, options.name];

    const identifiersToClean: string[] = [];

    const addEntryMeta = (entry: DataCatalogEntry, sourceMeta?: SourceMeta) => {
      entry.sourceMeta = sourceMeta || <SourceMeta>entry.definition;
      entry.sourceMetaPromise = CancellablePromise.resolve(entry.sourceMeta);
    };

    const sourceIdentifier = generateEntryCacheId({
      namespace: options.namespace,
      path: []
    });

    // Create the source entry if not already present
    if (!this.temporaryEntries[sourceIdentifier]) {
      const sourceEntry = new DataCatalogEntry({
        isTemporary: true,
        dataCatalog: this,
        namespace: options.namespace,
        compute: options.compute,
        path: [],
        definition: {
          index: 0,
          optimizerLoaded: true,
          type: 'source'
        }
      });
      addEntryMeta(sourceEntry);
      identifiersToClean.push(sourceIdentifier);
      sourceEntry.childrenPromise = CancellablePromise.resolve([]);
      this.temporaryEntries[sourceIdentifier] = Promise.resolve(sourceEntry);
    }

    this.temporaryEntries[sourceIdentifier].then(async sourceEntry => {
      const existingTemporaryDatabases = await sourceEntry.getChildren();
      const databaseIdentifier = generateEntryCacheId({
        namespace: options.namespace,
        path: [database]
      });

      // Create the database entry if not already present
      if (!this.temporaryEntries[databaseIdentifier]) {
        const databaseEntry = new DataCatalogEntry({
          isTemporary: true,
          dataCatalog: this,
          namespace: options.namespace,
          compute: options.compute,
          path: [database],
          definition: {
            index: 0,
            optimizerLoaded: true,
            type: 'database'
          }
        });
        addEntryMeta(databaseEntry);
        databaseEntry.childrenPromise = CancellablePromise.resolve([]);
        identifiersToClean.push(databaseIdentifier);
        existingTemporaryDatabases.push(databaseEntry);
        this.temporaryEntries[databaseIdentifier] = Promise.resolve(databaseEntry);
      }

      const databaseEntry = await this.temporaryEntries[databaseIdentifier];
      const existingTemporaryTables = await databaseEntry.getChildren();

      const tableIdentifier = generateEntryCacheId({
        namespace: options.namespace,
        path: path
      });

      // Unlink any existing table with the same identifier
      if (this.temporaryEntries[tableIdentifier]) {
        const tableEntry = await this.temporaryEntries[tableIdentifier];
        const index = existingTemporaryTables.indexOf(tableEntry);
        if (index !== -1) {
          existingTemporaryTables.splice(index, 1);
        }
      }

      const tableEntry = new DataCatalogEntry({
        isTemporary: true,
        dataCatalog: this,
        namespace: options.namespace,
        compute: options.compute,
        path: path,
        definition: {
          comment: '',
          index: existingTemporaryTables.length,
          name: options.name,
          optimizerLoaded: true,
          type: 'table'
        }
      });

      existingTemporaryTables.push(tableEntry);

      const tableSourceMeta: TableSourceMeta = {
        columns: (options.columns || []).map(col => col.name),
        extended_columns: options.columns || [],
        comment: '',
        notFound: false,
        is_view: false
      };

      addEntryMeta(tableEntry, tableSourceMeta);

      tableEntry.sample = { data: options.sample, meta: options.columns, type: 'table' };
      tableEntry.samplePromise = CancellablePromise.resolve(tableEntry.sample);

      identifiersToClean.push(tableIdentifier);
      this.temporaryEntries[tableIdentifier] = Promise.resolve(tableEntry);

      const columnEntries: DataCatalogEntry[] = [];
      tableEntry.childrenPromise = CancellablePromise.resolve(columnEntries);

      options.columns.forEach((column, index) => {
        const columnPath = [...path, column.name];
        const columnEntry = new DataCatalogEntry({
          isTemporary: true,
          dataCatalog: this,
          namespace: options.namespace,
          compute: options.compute,
          path: columnPath,
          definition: {
            comment: '',
            index: index,
            name: column.name,
            partitionKey: false,
            type: column.type
          }
        });

        columnEntry.sample = {
          data: options.sample.map(sampleRow => [sampleRow[index]]),
          meta: [column],
          type: 'table'
        };
        columnEntry.samplePromise = CancellablePromise.resolve(columnEntry.sample);

        tableSourceMeta.columns.push(column.name);
        tableSourceMeta.extended_columns.push(<ExtendedColumn>columnEntry.definition);
        addEntryMeta(columnEntry, {
          comment: '',
          name: column.name,
          notFound: false,
          sample: columnEntry.sample.data,
          type: column.type
        });

        const columnIdentifier = generateEntryCacheId({
          namespace: options.namespace,
          path: columnPath
        });
        identifiersToClean.push(columnIdentifier);
        this.temporaryEntries[columnIdentifier] = CancellablePromise.resolve(columnEntry);
      });
    });

    return {
      delete: () => {
        while (identifiersToClean.length) {
          const nextToDelete = identifiersToClean.pop();
          if (nextToDelete) {
            delete this.temporaryEntries[nextToDelete];
          }
        }
      }
    };
  }

  async getEntry(options: GetEntryOptions): Promise<DataCatalogEntry> {
    const identifier = generateEntryCacheId(options);
    if (options.temporaryOnly) {
      return this.temporaryEntries[identifier] || $.Deferred().reject().promise();
    }
    if (this.entries[identifier]) {
      return this.entries[identifier];
    }

    this.entries[identifier] = new Promise<DataCatalogEntry>(resolve => {
      if (!cacheEnabled) {
        resolve(
          new DataCatalogEntry({
            dataCatalog: this,
            namespace: options.namespace,
            compute: options.compute,
            path: options.path,
            definition: options.definition
          })
        );
      } else {
        this.store
          .getItem<StoreEntry>(identifier)
          .then(storeEntry => {
            const definition = storeEntry ? storeEntry.definition : options.definition;
            const entry = new DataCatalogEntry({
              dataCatalog: this,
              namespace: options.namespace,
              compute: options.compute,
              path: options.path,
              definition: definition
            });
            if (storeEntry) {
              mergeEntry(entry, storeEntry);
            } else if (!options.cachedOnly && options.definition) {
              entry.saveLater();
            }
            resolve(entry);
          })
          .catch(error => {
            console.warn(error);
            const entry = new DataCatalogEntry({
              dataCatalog: this,
              namespace: options.namespace,
              compute: options.compute,
              path: options.path,
              definition: options.definition
            });
            if (!options.cachedOnly && options.definition) {
              entry.saveLater();
            }
            resolve(entry);
          });
      }
    });

    return this.entries[identifier];
  }

  async getMultiTableEntry(options: GetMultiTableEntryOptions): Promise<MultiTableEntry> {
    const identifier = generateEntryCacheId(options);
    if (this.multiTableEntries[identifier]) {
      return this.multiTableEntries[identifier];
    }

    const newEntry = new MultiTableEntry({
      identifier: identifier,
      dataCatalog: this,
      paths: options.paths
    });

    this.multiTableEntries[identifier] = new Promise<MultiTableEntry>(async resolve => {
      if (!cacheEnabled) {
        resolve(newEntry);
        return;
      }
      try {
        const storeEntry = await this.multiTableStore.getItem<StoreMultiTableEntry>(identifier);
        if (storeEntry) {
          mergeMultiTableEntry(newEntry, storeEntry);
        }
      } catch (err) {
        console.warn(err);
      }
      resolve(newEntry);
    });

    return this.multiTableEntries[identifier];
  }

  /**
   * Updates the cache for the given multi table entry
   */
  async persistMultiTableEntry(multiTableEntry: MultiTableEntry): Promise<void> {
    const confTtl = (<hueWindow>window).CACHEABLE_TTL || {};
    if (
      !cacheEnabled ||
      (confTtl.default && confTtl.default <= 0) ||
      (confTtl.optimizer && confTtl.optimizer <= 0) ||
      multiTableEntry.getConnector().optimizer === LOCAL_STRATEGY
    ) {
      return;
    }
    await this.multiTableStore.setItem<StoreMultiTableEntry>(multiTableEntry.identifier, {
      version: DATA_CATALOG_VERSION,
      topAggs: multiTableEntry.topAggs,
      topColumns: multiTableEntry.topColumns,
      topFilters: multiTableEntry.topFilters,
      topJoins: multiTableEntry.topJoins
    });
  }
}

const generalDataCatalog = new GeneralDataCatalog();
const sourceBoundCatalogs: { [connectorId: string]: DataCatalog } = {};

/**
 * Helper function to get the DataCatalog instance for a given data source.
 */
const getCatalog = (connector: Connector): DataCatalog => {
  if (!connector || !connector.id) {
    throw new Error('getCatalog called without connector with id');
  }
  return (
    sourceBoundCatalogs[connector.id] ||
    (sourceBoundCatalogs[connector.id] = new DataCatalog(connector))
  );
};

export default {
  /**
   * Adds a detached (temporary) entry to the data catalog. This would allow autocomplete etc. of tables that haven't
   * been created yet.
   *
   * Calling this returns a handle that allows deletion of any created entries by calling delete() on the handle.
   */
  addTemporaryTable: (
    options: { connector: Connector } & AddTemporaryTableOptions
  ): { delete: () => void } => getCatalog(options.connector).addTemporaryTable(options),

  getEntry: (options: { connector: Connector } & GetEntryOptions): Promise<DataCatalogEntry> =>
    getCatalog(options.connector).getEntry(options),

  getMultiTableEntry: (
    options: { connector: Connector } & GetMultiTableEntryOptions
  ): Promise<MultiTableEntry> => getCatalog(options.connector).getMultiTableEntry(options),

  /**
   * This can be used as a shorthand function to get the child entries of the given path. Same as first calling
   * getEntry then getChildren.
   */
  getChildren: (
    options: {
      connector: Connector;
      namespace: Namespace;
      compute: Compute;
      path: string | string[];
      temporaryOnly?: boolean;
    } & CatalogGetOptions
  ): CancellablePromise<DataCatalogEntry[]> =>
    new CancellablePromise<DataCatalogEntry[]>(async (resolve, reject, onCancel) => {
      try {
        const entry = await getCatalog(options.connector).getEntry(options);
        const childPromise = entry.getChildren(options);
        onCancel(() => {
          childPromise.cancel();
        });

        resolve(applyCancellable(childPromise, options));
      } catch (err) {
        reject(err);
      }
    }),

  getCatalog,

  getAllNavigatorTags: generalDataCatalog.getAllNavigatorTags.bind(generalDataCatalog),

  updateAllNavigatorTags: generalDataCatalog.updateAllNavigatorTags.bind(generalDataCatalog),

  enableCache(): void {
    cacheEnabled = true;
  },

  disableCache(): void {
    cacheEnabled = false;
  }
};

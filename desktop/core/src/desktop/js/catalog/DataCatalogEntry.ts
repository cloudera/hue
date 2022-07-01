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

import * as ko from 'knockout';
import KnockoutObservable from '@types/knockout';

import { Cancellable, CancellablePromise } from 'api/cancellablePromise';
import {
  addNavTags,
  deleteNavTags,
  fetchDescribe,
  fetchNavigatorMetadata,
  fetchPartitions,
  fetchSample,
  fetchSourceMetadata,
  searchEntities,
  updateNavigatorProperties,
  updateSourceMetadata
} from 'catalog/api';
import MultiTableEntry, { TopAggs, TopFilters, TopJoins } from 'catalog/MultiTableEntry';

import { applyCancellable, forceSilencedErrors } from 'catalog/catalogUtils';
import { Compute, Connector, Namespace } from 'config/types';
import { hueWindow } from 'types/types';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';
import { executeSingleStatement } from 'apps/editor/execution/api';
import { SqlAnalyzer } from './analyzer/types';
import {
  CatalogGetOptions,
  DataCatalog,
  SqlAnalyzerPopularity,
  SqlAnalyzerResponse,
  SqlAnalyzerResponsePopularity,
  TimestampedData
} from './dataCatalog';

export interface BaseDefinition extends TimestampedData {
  name?: string;
  comment?: string;
  index?: number;
  type?: string;
  isMapValue?: boolean;
  sqlAnalyzerLoaded?: boolean;
  partitionKey?: boolean;
  primaryKey?: boolean;
  foreignKey?: KeySpecification;
}

export type Definition = ExtendedColumn | BaseDefinition;

export interface KeySpecification {
  name: string;
}

export interface ForeignKeySpecification extends KeySpecification {
  to: string;
}

export interface ExtendedColumn extends BaseDefinition, TimestampedData {
  name: string;
  type: string;
}

export interface RootSourceMeta extends TimestampedData {
  comment?: string | null;
  databases: string[];
  notFound?: boolean;
}

export interface TablesMeta extends TimestampedData {
  comment?: string | null;
  index: number;
  name: string;
  type: string;
}

export interface DatabaseSourceMeta extends TimestampedData {
  comment?: string | null;
  notFound?: boolean;
  tables_meta: TablesMeta[];
}

export interface TableSourceMeta extends TimestampedData {
  columns: string[];
  comment?: string | null;
  extended_columns: ExtendedColumn[];
  foreign_keys?: ForeignKeySpecification[];
  fields?: string[]; // TODO: On FieldSourceMeta?
  hdfs_link?: string;
  is_view?: boolean;
  notFound?: boolean;
  partition_keys?: KeySpecification[];
  primary_keys?: KeySpecification[];
  support_updates?: boolean;
}

export interface ComplexDetails {
  index?: number;
  isMapValue: boolean;
  type: string;
  fields?: {
    index?: number;
    type: string;
    name: string;
  }[];
}

export interface FieldSourceMeta extends TimestampedData {
  comment?: string | null;
  name: string;
  notFound?: boolean;
  sample: FieldSample[][];
  type: string;
  key?: ComplexDetails;
  value?: ComplexDetails;
  item?: ComplexDetails;
  fields?: {
    index?: number;
    type: string;
    name: string;
  }[];
}

export type SourceMeta = RootSourceMeta | DatabaseSourceMeta | TableSourceMeta | FieldSourceMeta;
export type FieldSample = string | number | null | undefined;
type ReloadOptions = Omit<CatalogGetOptions, 'cachedOnly' | 'refreshCache'>;

export interface NavigatorMeta extends TimestampedData {
  clusteredByColNames: unknown;
  compressed: boolean;
  created: string;
  customProperties: unknown;
  deleteTime: unknown;
  deleted: boolean;
  description: string | null;
  extractorRunId: string;
  fileSystemPath: string;
  firstClassParentId: unknown;
  identity: string;
  inputFormat: string;
  internalType: string;
  lastAccessed: string | null;
  lastModified: string | null;
  lastModifiedBy: string | null;
  metaClassName: string;
  name: string | null;
  originalDescription: string | null;
  originalName: string;
  original_name?: string;
  outputFormat: string;
  owner: string;
  packageName: string;
  parentPath: string;
  partColNames: unknown;
  properties: { [key: string]: string };
  serdeLibName: string;
  serdeName: string | null;
  serdeProps: string | null;
  sortByColNames: string | null;
  sourceId: string;
  sourceType: string;
  tags: unknown;
  technicalProperties: { [key: string]: string };
  type: string;
  userEntity: boolean;
}

export interface TableAnalysis extends TimestampedData {
  cols: { comment?: string | null; type: string; name: string }[];
  comment?: string | null;
  details: {
    properties: { [propertyKey: string]: string };
    stats: { [statKey: string]: string };
  };
  hdfs_link: string;
  is_view: boolean;
  message: string;
  name: string;
  partition_keys: KeySpecification[];
  path_location?: string;
  primary_keys: KeySpecification[];
  properties: { col_name: string; comment?: string | null; data_type?: string | null }[];
  stats: { col_name: string; comment?: string | null; data_type?: string | null }[];
}

export type Analysis = TableAnalysis;

export interface Partitions extends TimestampedData {
  partition_keys_json: string[];
  partition_values_json: {
    browseUrl: string;
    columns: string[];
    notebookUrl: string;
    partitionSpec: string;
    readUrl: string;
  }[];
}

export interface SampleMeta {
  comment?: string | null;
  name: string;
  type: string;
}

export interface Sample {
  data: FieldSample[][];
  has_more?: boolean;
  hueTimestamp?: number;
  isEscaped?: boolean;
  meta: SampleMeta[];
  type: string;
}

export interface SqlAnalyzerMeta extends TimestampedData {
  hueTimestamp?: number;
}

const cachedOnly = (options?: CatalogGetOptions): boolean => !!(options && options.cachedOnly);

const shouldReload = (options?: CatalogGetOptions & { refreshAnalysis?: boolean }): boolean =>
  !!(!DataCatalog.cacheEnabled() || (options && (options.refreshCache || options.refreshAnalysis)));

/**
 * Helper function to get the multi table catalog version of a catalog entry
 */
const getMultiTableEntry = async (catalogEntry: DataCatalogEntry): Promise<MultiTableEntry> => {
  if (!catalogEntry.isTableOrView()) {
    return Promise.reject();
  }
  return catalogEntry.dataCatalog.getMultiTableEntry({
    namespace: catalogEntry.namespace,
    compute: catalogEntry.compute,
    paths: [catalogEntry.path]
  });
};

export default class DataCatalogEntry {
  compute: Compute;
  dataCatalog: DataCatalog;
  definition?: Definition;
  isTemporary?: boolean;
  name: string;
  namespace: Namespace;
  path: string[];
  saveTimeout = -1;
  commentObservable?: KnockoutObservable<string | undefined>;

  analysis?: Analysis;
  analysisPromise?: CancellablePromise<Analysis>;
  childrenPromise?: CancellablePromise<DataCatalogEntry[]>;
  navigatorMeta?: NavigatorMeta;
  navigatorMetaForChildrenPromise?: CancellablePromise<DataCatalogEntry[]>;
  navigatorMetaPromise?: CancellablePromise<NavigatorMeta>;
  sqlAnalyzerMeta?: SqlAnalyzerMeta;
  sqlAnalyzerMetaPromise?: CancellablePromise<SqlAnalyzerMeta>;
  sqlAnalyzerPopularity?: SqlAnalyzerPopularity;
  sqlAnalyzerPopularityForChildrenPromise?: CancellablePromise<DataCatalogEntry[]>;
  partitions?: Partitions;
  partitionsPromise?: CancellablePromise<Partitions>;
  sample?: Sample;
  samplePromise?: CancellablePromise<Sample>;
  sourceMeta?: SourceMeta;
  sourceMetaPromise?: CancellablePromise<SourceMeta>;

  constructor(options: {
    compute: Compute;
    dataCatalog: DataCatalog;
    definition?: Definition;
    isTemporary?: boolean;
    namespace: Namespace;
    path?: string | string[];
  }) {
    if (!options.dataCatalog.connector) {
      throw new Error('DataCatalogEntry created without connector');
    }

    this.namespace = options.namespace;
    this.compute = options.compute;
    this.dataCatalog = options.dataCatalog;

    this.path = typeof options.path === 'string' ? options.path.split('.') : options.path || [];
    this.name = this.path.length ? this.path[this.path.length - 1] : this.getConnector().id;
    this.isTemporary = options.isTemporary;

    if (options.definition) {
      this.definition = options.definition;
    } else if (this.path.length === 0) {
      this.definition = { type: 'source' };
    } else if (this.path.length === 1) {
      this.definition = { type: 'database' };
    } else if (this.path.length === 2) {
      this.definition = { type: 'table' };
    }

    this.reset();
  }

  /**
   * Resets the entry to an empty state, it might still have some details cached
   */
  reset(): void {
    this.saveTimeout = -1;
    this.analysis = undefined;
    this.analysisPromise = undefined;
    this.childrenPromise = undefined;
    this.navigatorMeta = undefined;
    this.navigatorMetaForChildrenPromise = undefined;
    this.navigatorMetaPromise = undefined;
    this.sqlAnalyzerMeta = undefined;
    this.sqlAnalyzerMetaPromise = undefined;
    this.sqlAnalyzerPopularity = undefined;
    this.sqlAnalyzerPopularityForChildrenPromise = undefined;
    this.partitions = undefined;
    this.partitionsPromise = undefined;
    this.sample = undefined;
    this.samplePromise = undefined;
    this.sourceMeta = undefined;
    this.sourceMetaPromise = undefined;

    if (this.path.length) {
      this.dataCatalog
        .getKnownEntry({
          namespace: this.namespace,
          compute: this.compute,
          path: this.path.slice(0, this.path.length - 1)
        })
        .then(parent => {
          if (parent) {
            parent.navigatorMetaForChildrenPromise = undefined;
            parent.sqlAnalyzerPopularityForChildrenPromise = undefined;
          }
        })
        .catch(err => {
          console.warn(err);
        });
    }
  }

  /**
   * Resets the entry and clears the cache
   */
  async clearCache(options?: {
    cascade?: boolean;
    silenceErrors?: boolean;
    targetChild?: string;
  }): Promise<void> {
    if (!options) {
      options = {};
    }

    if (this.definition && this.definition.sqlAnalyzerLoaded) {
      delete this.definition.sqlAnalyzerLoaded;
    }

    this.reset();

    try {
      if (options.cascade) {
        await this.dataCatalog.clearStorageCascade(this.namespace, this.compute, this.path);
      } else {
        await this.save();
      }
    } catch (err) {}

    huePubSub.publish('data.catalog.entry.refreshed', {
      entry: this,
      cascade: !!options.cascade
    });
  }

  private reloadAnalysis(
    options?: ReloadOptions & { refreshAnalysis?: boolean }
  ): CancellablePromise<Analysis> {
    this.analysisPromise = new CancellablePromise<Analysis>(async (resolve, reject, onCancel) => {
      const fetchPromise = fetchDescribe({
        entry: this,
        ...options
      });

      onCancel(() => {
        fetchPromise.cancel();
      });

      try {
        this.analysis = await fetchPromise;
        resolve(this.analysis);
      } catch (err) {
        reject(err || 'Fetch failed');
        return;
      }
      this.saveLater();
    });
    return applyCancellable(this.analysisPromise, options);
  }

  private reloadNavigatorMeta(options?: ReloadOptions): CancellablePromise<NavigatorMeta> {
    if (this.canHaveNavigatorMetadata()) {
      this.navigatorMetaPromise = new CancellablePromise<NavigatorMeta>(async (resolve, reject) => {
        try {
          this.navigatorMeta = await fetchNavigatorMetadata({ ...options, entry: this });
          resolve(this.navigatorMeta);
        } catch (err) {
          reject(err || 'Fetch failed');
          return;
        }
        this.saveLater();
        if (this.commentObservable) {
          this.commentObservable(this.getResolvedComment());
        }
      });
    } else {
      this.navigatorMetaPromise = CancellablePromise.reject();
    }
    return applyCancellable(this.navigatorMetaPromise);
  }

  /**
   * Helper function to reload the nav opt metadata for the given entry
   */
  private reloadSqlAnalyzerMeta({
    cancellable,
    silenceErrors,
    sqlAnalyzer
  }: ReloadOptions & { sqlAnalyzer: SqlAnalyzer }): CancellablePromise<SqlAnalyzerMeta> {
    if (this.dataCatalog.canHaveSqlAnalyzerMeta()) {
      this.sqlAnalyzerMetaPromise = new CancellablePromise<SqlAnalyzerMeta>(
        async (resolve, reject, onCancel) => {
          const fetchPromise = sqlAnalyzer.fetchSqlAnalyzerMeta({
            path: this.path,
            silenceErrors
          });
          onCancel(() => {
            fetchPromise.cancel();
          });

          try {
            this.sqlAnalyzerMeta = await fetchPromise;
            resolve(this.sqlAnalyzerMeta);
          } catch (err) {
            reject(err || 'Fetch failed');
            return;
          }
          this.saveLater();
        }
      );
    } else {
      this.sqlAnalyzerMetaPromise = CancellablePromise.reject();
    }
    return applyCancellable(this.sqlAnalyzerMetaPromise, { cancellable });
  }

  private reloadPartitions(options?: ReloadOptions): CancellablePromise<Partitions> {
    this.partitionsPromise = new CancellablePromise<Partitions>(async (resolve, reject) => {
      try {
        this.partitions = await fetchPartitions({ ...options, entry: this });
        resolve(this.partitions);
      } catch (err) {
        reject(err || 'Fetch failed');
        return;
      }
      this.saveLater();
    });
    return applyCancellable(this.partitionsPromise, options);
  }

  private reloadSample(
    options?: ReloadOptions & { operation?: string }
  ): CancellablePromise<Sample> {
    this.samplePromise = new CancellablePromise<Sample>(async (resolve, reject) => {
      try {
        this.sample = await fetchSample({ ...options, entry: this });
        resolve(this.sample);
      } catch (err) {
        reject(err || 'Fetch failed');
        return;
      }
      this.saveLater();
    });
    return applyCancellable(this.samplePromise, options);
  }

  private reloadSourceMeta(options?: ReloadOptions): CancellablePromise<SourceMeta> {
    this.sourceMetaPromise = new CancellablePromise<SourceMeta>(async (resolve, reject) => {
      if (this.dataCatalog.invalidatePromise) {
        try {
          await this.dataCatalog.invalidatePromise;
        } catch (err) {}
      }

      try {
        this.sourceMeta = await fetchSourceMetadata({
          ...options,
          entry: this
        });
        resolve(this.sourceMeta);
      } catch (err) {
        reject(err || 'Fetch failed');
        return;
      }
      this.saveLater();
    });
    return applyCancellable(this.sourceMetaPromise, options);
  }

  drop(cascade?: boolean): CancellablePromise<void> {
    if (!this.isDatabase() && !this.isTableOrView()) {
      return CancellablePromise.reject('Drop is only possible for a database, table or view.');
    }
    const statement = `DROP ${
      this.isDatabase() ? 'DATABASE' : this.isView() ? 'VIEW' : 'TABLE'
    } IF EXISTS \`${this.path.join('`.`')}\`${this.isDatabase() && cascade ? ' CASCADE;' : ';'}`;

    return new CancellablePromise<void>((resolve, reject, onCancel) => {
      const executePromise = executeSingleStatement({
        connector: this.getConnector(),
        namespace: this.namespace,
        compute: this.compute,
        statement
      });
      onCancel(() => {
        executePromise.cancel();
      });

      executePromise
        .then(() => {
          this.clearCache({ cascade: true }).catch();
          resolve();
        })
        .catch(reject);
    });
  }

  /**
   * Save the entry to cache
   */
  async save(): Promise<void> {
    window.clearTimeout(this.saveTimeout);
    try {
      await this.dataCatalog.persistCatalogEntry(this);
    } catch (err) {}
  }

  /**
   * Save the entry at a later point of time
   */
  saveLater(): void {
    if (((<hueWindow>window).CACHEABLE_TTL?.default || 0) > 0) {
      window.clearTimeout(this.saveTimeout);
      this.saveTimeout = window.setTimeout(async () => {
        await this.save();
      }, 1000);
    }
  }

  /**
   * Gets the parent entry, rejected if there's no parent.
   */
  getParent(): Promise<DataCatalogEntry> {
    if (!this.path.length) {
      return Promise.reject();
    }

    return this.dataCatalog.getEntry({
      namespace: this.namespace,
      compute: this.compute,
      path: this.path.slice(0, this.path.length - 1)
    });
  }

  /**
   * Get the children of the catalog entry, columns for a table entry etc.
   */
  getChildren(options?: CatalogGetOptions): CancellablePromise<DataCatalogEntry[]> {
    if (this.childrenPromise && this.childrenPromise.cancelled) {
      this.childrenPromise = undefined;
    }
    if (!this.childrenPromise && cachedOnly(options)) {
      return CancellablePromise.reject();
    }

    if (this.childrenPromise && !shouldReload(options)) {
      return applyCancellable(this.childrenPromise, options);
    }

    this.childrenPromise = new CancellablePromise<DataCatalogEntry[]>(
      async (resolve, reject, onCancel) => {
        let sourceMeta: SourceMeta | undefined;
        let cancelled = false;
        onCancel(() => {
          cancelled = true;
        });
        try {
          sourceMeta = await this.getSourceMeta(options);
        } catch (err) {}

        if (cancelled) {
          reject('Cancelled');
          return;
        }

        if (!sourceMeta) {
          reject('No source meta found');
          return;
        }

        if (sourceMeta.notFound) {
          resolve([]);
          return;
        }

        const partitionKeys: { [key: string]: boolean } = {};
        const tableSourceMeta = <TableSourceMeta>sourceMeta;
        if (tableSourceMeta.partition_keys) {
          tableSourceMeta.partition_keys.forEach(partitionKey => {
            partitionKeys[partitionKey.name] = true;
          });
        }
        const primaryKeys: { [key: string]: boolean } = {};
        if (tableSourceMeta.primary_keys) {
          tableSourceMeta.primary_keys.forEach(primaryKey => {
            primaryKeys[primaryKey.name] = true;
          });
        }
        const foreignKeys: { [key: string]: KeySpecification } = {};
        if (tableSourceMeta.foreign_keys) {
          tableSourceMeta.foreign_keys.forEach(foreignKey => {
            foreignKeys[foreignKey.name] = foreignKey;
          });
        }

        const entities: string[] | ExtendedColumn[] =
          (<RootSourceMeta>sourceMeta).databases ||
          (<DatabaseSourceMeta>sourceMeta).tables_meta ||
          (<TableSourceMeta>sourceMeta).extended_columns ||
          (<FieldSourceMeta>sourceMeta).fields ||
          (<TableSourceMeta>sourceMeta).columns ||
          [];

        const promises: Promise<DataCatalogEntry>[] = [];
        let index = 0;
        entities.forEach((entity: string | ExtendedColumn) => {
          if (!(<RootSourceMeta>sourceMeta).databases || entity !== '_impala_builtins') {
            const name = (<ExtendedColumn>entity).name || <string>entity;
            const promise = this.dataCatalog.getEntry({
              namespace: this.namespace,
              compute: this.compute,
              path: [...this.path, name]
            });

            promise
              .then(catalogEntry => {
                if (
                  !catalogEntry.definition ||
                  typeof catalogEntry.definition.index === 'undefined'
                ) {
                  const definition: BaseDefinition =
                    typeof entity === 'object' ? entity : { name: entity };
                  if (!definition.type) {
                    if (this.path.length === 0) {
                      definition.type = 'database';
                    } else if (this.path.length === 1) {
                      definition.type = 'table';
                    } else if (this.path.length === 2) {
                      definition.type = 'column';
                    }
                  }

                  if ((<TableSourceMeta>sourceMeta).partition_keys) {
                    definition.partitionKey = partitionKeys[name];
                  }
                  if ((<TableSourceMeta>sourceMeta).primary_keys) {
                    definition.primaryKey = primaryKeys[name];
                  }
                  if ((<TableSourceMeta>sourceMeta).foreign_keys) {
                    definition.foreignKey = foreignKeys[name];
                  }
                  definition.index = index++;
                  catalogEntry.definition = definition;
                  catalogEntry.saveLater();
                }
              })
              .catch(err => {
                console.warn(err);
              });
            promises.push(promise);
          }
        });

        // TODO: Move to connector attributes
        if (
          sourceMeta &&
          (this.getDialect() === 'impala' || this.getDialect() === 'hive') &&
          this.isComplex()
        ) {
          const fieldSourceMeta = <FieldSourceMeta>sourceMeta;
          const complexAttributes: (keyof Pick<FieldSourceMeta, 'key' | 'value' | 'item'>)[] =
            fieldSourceMeta.type === 'map' ? ['key', 'value'] : ['item'];
          complexAttributes.forEach(path => {
            const definition = fieldSourceMeta[path];
            if (definition) {
              const promise = this.dataCatalog.getEntry({
                namespace: this.namespace,
                compute: this.compute,
                path: [...this.path, path]
              });
              promise
                .then(catalogEntry => {
                  if (
                    !catalogEntry.definition ||
                    typeof catalogEntry.definition.index === 'undefined'
                  ) {
                    definition.index = index++;
                    definition.isMapValue = path === 'value';
                    catalogEntry.definition = definition;
                    catalogEntry.saveLater();
                  }
                })
                .catch(err => {
                  console.warn(err);
                });
              promises.push(promise);
            }
          });
        }

        Promise.all(promises).then(resolve).catch(reject);
      }
    );

    return applyCancellable(this.childrenPromise, options);
  }

  /**
   * Loads navigator metadata for children, only applicable to databases and tables
   */
  loadNavigatorMetaForChildren(
    options?: Omit<CatalogGetOptions, 'cachedOnly'>
  ): CancellablePromise<DataCatalogEntry[]> {
    if (this.navigatorMetaForChildrenPromise && this.navigatorMetaForChildrenPromise.cancelled) {
      this.navigatorMetaPromise = undefined;
    }
    options = forceSilencedErrors(options);

    if (!this.canHaveNavigatorMetadata() || this.isField()) {
      return CancellablePromise.resolve([]);
    }

    if (this.navigatorMetaForChildrenPromise && !shouldReload(options)) {
      return applyCancellable(this.navigatorMetaForChildrenPromise, options);
    }

    this.navigatorMetaForChildrenPromise = new CancellablePromise<DataCatalogEntry[]>(
      async (resolve, reject, onCancel) => {
        const cancellablePromises: Cancellable[] = [];
        onCancel(() => {
          cancellablePromises.forEach(cancellable => {
            cancellable.cancel();
          });
        });

        try {
          const childPromise = this.getChildren(options);
          cancellablePromises.push(childPromise);

          const children = await childPromise;

          const someHaveNavMeta = children.some(childEntry => childEntry.navigatorMeta);

          if (someHaveNavMeta && !shouldReload(options)) {
            resolve(children);
            return;
          }

          // TODO: Add sourceType to nav search query
          const query = this.path.length
            ? `parentPath:"/${this.path.join('/')}" AND type:(table view field)`
            : 'type:database';

          const rejectUnknown = () => {
            children.forEach(childEntry => {
              if (!childEntry.navigatorMeta) {
                childEntry.navigatorMeta = undefined;
                childEntry.navigatorMetaPromise = undefined;
              }
            });
          };

          const searchPromise = searchEntities({
            query,
            rawQuery: true,
            limit: children.length,
            silenceErrors: options?.silenceErrors
          });

          cancellablePromises.push(searchPromise);

          searchPromise
            .then(result => {
              if (result && result.entities) {
                const childEntryIndex: { [name: string]: DataCatalogEntry } = {};
                children.forEach(childEntry => {
                  childEntryIndex[childEntry.name.toLowerCase()] = childEntry;
                });

                result.entities.forEach(entity => {
                  const matchingChildEntry =
                    childEntryIndex[(entity.original_name || entity.originalName).toLowerCase()];
                  if (matchingChildEntry) {
                    matchingChildEntry.navigatorMeta = entity;
                    entity.hueTimestamp = Date.now();
                    matchingChildEntry.navigatorMetaPromise = CancellablePromise.resolve(
                      matchingChildEntry.navigatorMeta
                    );
                    if (entity && matchingChildEntry.commentObservable) {
                      matchingChildEntry.commentObservable(matchingChildEntry.getResolvedComment());
                    }
                    matchingChildEntry.saveLater();
                  }
                });
              }
            })
            .catch(() => resolve([]))
            .finally(() => {
              rejectUnknown();
              resolve(children);
            });
        } catch (err) {
          resolve([]);
          return;
        }
      }
    );

    return applyCancellable(this.navigatorMetaForChildrenPromise, options);
  }

  /**
   * Helper function used when loading navopt metdata for children
   */
  applySqlAnalyzerResponseToChildren(
    response: SqlAnalyzerResponse,
    options?: { silenceErrors?: boolean }
  ): CancellablePromise<DataCatalogEntry[]> {
    if (!this.definition) {
      this.definition = {};
    }
    this.definition.sqlAnalyzerLoaded = true;
    this.saveLater();

    return new CancellablePromise<DataCatalogEntry[]>(async (resolve, reject, onCancel) => {
      const childPromise = this.getChildren(options);
      onCancel(() => {
        childPromise.cancel();
      });

      try {
        const childEntries = await childPromise;

        const entriesByName: { [name: string]: DataCatalogEntry } = {};
        childEntries.forEach(childEntry => {
          entriesByName[childEntry.name.toLowerCase()] = childEntry;
        });
        const updatedIndex: { [path: string]: DataCatalogEntry } = {};
        if (this.isDatabase() && response.top_tables) {
          response.top_tables.forEach(topTable => {
            if (!topTable.name) {
              return;
            }
            const matchingChild = entriesByName[topTable.name.toLowerCase()];
            if (matchingChild) {
              matchingChild.sqlAnalyzerPopularity = topTable;
              matchingChild.saveLater();
              updatedIndex[matchingChild.getQualifiedPath()] = matchingChild;
            }
          });
        } else if (this.isTableOrView() && response.values) {
          const addSqlAnalyzerPopularity = (
            columns: SqlAnalyzerResponsePopularity[] | undefined,
            type: keyof Pick<
              SqlAnalyzerPopularity,
              'filterColumn' | 'groupByColumn' | 'joinColumn' | 'orderByColumn' | 'selectColumn'
            >
          ) => {
            if (columns) {
              columns.forEach(column => {
                if (!column.columnName) {
                  return;
                }
                const matchingChild = entriesByName[column.columnName.toLowerCase()];
                if (matchingChild) {
                  if (!matchingChild.sqlAnalyzerPopularity) {
                    matchingChild.sqlAnalyzerPopularity = { column_count: 0, columnCount: 0 };
                  }
                  matchingChild.sqlAnalyzerPopularity[type] = column;
                  matchingChild.saveLater();
                  updatedIndex[matchingChild.getQualifiedPath()] = matchingChild;
                }
              });
            }
          };

          addSqlAnalyzerPopularity(response.values.filterColumns, 'filterColumn');
          addSqlAnalyzerPopularity(response.values.groupbyColumns, 'groupByColumn');
          addSqlAnalyzerPopularity(response.values.joinColumns, 'joinColumn');
          addSqlAnalyzerPopularity(response.values.orderbyColumns, 'orderByColumn');
          addSqlAnalyzerPopularity(response.values.selectColumns, 'selectColumn');
        }
        const popularEntries: DataCatalogEntry[] = [];
        Object.keys(updatedIndex).forEach(path => {
          popularEntries.push(updatedIndex[path]);
        });
        resolve(popularEntries);
      } catch (err) {
        reject(err);
      }
    });
  }

  /**
   * Loads SQL Analyzer popularity for the children of this entry.
   */
  loadSqlAnalyzerPopularityForChildren(
    options: CatalogGetOptions & { sqlAnalyzer: SqlAnalyzer }
  ): CancellablePromise<DataCatalogEntry[]> {
    if (
      this.sqlAnalyzerPopularityForChildrenPromise &&
      this.sqlAnalyzerPopularityForChildrenPromise.cancelled
    ) {
      this.sqlAnalyzerPopularityForChildrenPromise = undefined;
    }
    options.silenceErrors = true;

    if (!this.dataCatalog.canHaveSqlAnalyzerMeta()) {
      return CancellablePromise.reject();
    }

    if (this.sqlAnalyzerPopularityForChildrenPromise && !shouldReload(options)) {
      return applyCancellable(this.sqlAnalyzerPopularityForChildrenPromise, options);
    }

    if (this.definition && this.definition.sqlAnalyzerLoaded && !shouldReload(options)) {
      this.sqlAnalyzerPopularityForChildrenPromise = new CancellablePromise<DataCatalogEntry[]>(
        async (resolve, reject, onCancel) => {
          const childPromise = this.getChildren(options);
          onCancel(() => {
            childPromise.cancel();
          });
          try {
            const children = await childPromise;
            resolve(children.filter(child => child.sqlAnalyzerPopularity));
          } catch (err) {
            reject(err);
          }
        }
      );
    } else if (this.isDatabase() || this.isTableOrView()) {
      this.sqlAnalyzerPopularityForChildrenPromise = new CancellablePromise<DataCatalogEntry[]>(
        async (resolve, reject, onCancel) => {
          const cancellablePromises: Cancellable[] = [];
          onCancel(() => {
            cancellablePromises.forEach(cancellable => cancellable.cancel());
          });

          const popularityPromise = options.sqlAnalyzer.fetchPopularity({
            ...options,
            paths: [this.path]
          });
          cancellablePromises.push(popularityPromise);

          try {
            const analyzerResponse = await popularityPromise;
            const applyPromise = this.applySqlAnalyzerResponseToChildren(analyzerResponse, options);
            cancellablePromises.push(applyPromise);
            const entries = await applyPromise;
            resolve(entries);
          } catch (err) {
            resolve([]);
          }
        }
      );
    } else {
      this.sqlAnalyzerPopularityForChildrenPromise = CancellablePromise.resolve([]);
    }

    return applyCancellable(this.sqlAnalyzerPopularityForChildrenPromise);
  }

  /**
   * Returns true if the catalog entry can have navigator metadata
   */
  canHaveNavigatorMetadata(): boolean {
    if (!(<hueWindow>window).HAS_CATALOG) {
      return false;
    }
    // TODO: Move to connector attributes
    return (
      (this.getDialect() === 'hive' || this.getDialect() === 'impala') &&
      (this.isDatabase() || this.isTableOrView() || this.isColumn())
    );
  }

  /**
   * Returns the currently known comment without loading any additional metadata
   */
  getResolvedComment(): string {
    // TODO: Move to connector attributes
    if (this.navigatorMeta && (this.getDialect() === 'hive' || this.getDialect() === 'impala')) {
      if (this.navigatorMeta.description) {
        return this.navigatorMeta.description;
      }
      if (this.navigatorMeta.originalDescription) {
        return this.navigatorMeta.originalDescription;
      }
    }
    if (this.definition && this.definition.comment) {
      return this.definition.comment;
    }
    return (this.sourceMeta && this.sourceMeta.comment) || '';
  }

  /**
   * This can be used to get an observable for the comment which will be updated once a comment has been
   * resolved.
   */
  getCommentObservable(): KnockoutObservable<string | undefined> {
    if (!this.commentObservable) {
      this.commentObservable = ko.observable(this.getResolvedComment());
    }
    return this.commentObservable;
  }

  /**
   * Checks whether the comment is known and has been loaded from the proper source
   */
  hasResolvedComment(): boolean {
    if (this.canHaveNavigatorMetadata()) {
      return typeof this.navigatorMeta !== 'undefined';
    }
    return typeof this.sourceMeta !== 'undefined';
  }

  /**
   * Gets the comment for this entry, fetching it if necessary from the proper source.
   */
  getComment(options?: CatalogGetOptions): CancellablePromise<string> {
    const promise = new CancellablePromise<string>(async (resolve, reject, onCancel) => {
      const cancellablePromises: Cancellable[] = [];
      onCancel(() => {
        cancellablePromises.forEach(cancellable => cancellable.cancel());
      });

      if (this.canHaveNavigatorMetadata()) {
        const navigatorMetaPromise = this.getNavigatorMeta(options);
        cancellablePromises.push(navigatorMetaPromise);
        try {
          const navigatorMeta = await navigatorMetaPromise;
          if (navigatorMeta) {
            resolve(navigatorMeta.description || navigatorMeta.originalDescription || '');
            return;
          }
        } catch (err) {}
      }

      if (this.sourceMeta) {
        resolve(this.sourceMeta.comment || '');
      } else if (this.definition && this.definition.comment) {
        resolve(this.definition.comment);
      } else {
        const sourceMetaPromise = this.getSourceMeta(options);
        try {
          const sourceMeta = await sourceMetaPromise;
          resolve((sourceMeta && sourceMeta.comment) || '');
        } catch (err) {
          reject(err);
        }
      }
    });

    return applyCancellable(promise);
  }

  /**
   * Updates custom navigator metadata for the catalog entry
   */
  async updateNavigatorCustomMetadata(
    modifiedCustomMetadata?: { [key: string]: string },
    deletedCustomMetadataKeys?: string[],
    apiOptions?: Omit<CatalogGetOptions, 'cachedOnly' | 'cancellable'>
  ): Promise<NavigatorMeta> {
    if (!this.canHaveNavigatorMetadata()) {
      return Promise.reject();
    }

    const navigatorMeta = await this.getNavigatorMeta(apiOptions);

    if (!navigatorMeta) {
      throw new Error('Could not load navigator metadata.');
    }

    return new Promise<NavigatorMeta>((resolve, reject) => {
      updateNavigatorProperties({
        identity: navigatorMeta.identity,
        modifiedCustomMetadata,
        deletedCustomMetadataKeys
      })
        .then(entity => {
          if (entity) {
            this.navigatorMeta = entity;
            this.navigatorMetaPromise = CancellablePromise.resolve(entity);
            this.saveLater();
            resolve(entity);
          } else {
            reject();
          }
        })
        .catch(reject);
    });
  }

  /**
   * Sets the comment in the proper source
   */
  async setComment(
    comment: string,
    options?: Omit<CatalogGetOptions, 'cachedOnly' | 'cancellable'>
  ): Promise<string> {
    if (this.canHaveNavigatorMetadata()) {
      const navigatorMeta = await this.getNavigatorMeta(options);
      if (!navigatorMeta) {
        throw new Error('Could not load navigator metadata.');
      }

      return new Promise<string>((resolve, reject) => {
        updateNavigatorProperties({
          identity: navigatorMeta.identity,
          properties: {
            description: comment
          }
        })
          .then(async entity => {
            if (entity) {
              this.navigatorMeta = entity;
              this.navigatorMetaPromise = CancellablePromise.resolve(entity);
              this.saveLater();
            }
            this.getComment(options)
              .then(comment => {
                if (this.commentObservable) {
                  this.commentObservable(comment);
                }
                resolve(comment);
              })
              .catch(reject);
          })
          .catch(reject);
      });
    }

    return new Promise((resolve, reject) => {
      updateSourceMetadata({
        entry: this,
        properties: {
          comment: comment
        },
        silenceErrors: options?.silenceErrors
      })
        .then(async () => {
          try {
            await this.reloadSourceMeta(options);
            const comment = await this.getComment(options);
            if (this.commentObservable) {
              this.commentObservable(comment);
            }
            resolve(comment);
          } catch (err) {
            reject(err);
          }
        })
        .catch(reject);
    });
  }

  /**
   * Adds a list of tags and updates the navigator metadata of the entry
   */
  async addNavigatorTags(
    tags: string[],
    apiOptions?: Omit<CatalogGetOptions, 'cachedOnly' | 'cancellable'>
  ): Promise<NavigatorMeta> {
    if (!this.canHaveNavigatorMetadata()) {
      return Promise.reject();
    }

    const navigatorMeta = await this.getNavigatorMeta(apiOptions);

    return new Promise((resolve, reject) => {
      addNavTags(navigatorMeta.identity, tags)
        .then(entity => {
          if (entity) {
            this.navigatorMeta = entity;
            this.navigatorMetaPromise = CancellablePromise.resolve(entity);
            this.saveLater();
            resolve(entity);
          } else {
            reject();
          }
        })
        .catch(reject);
    });
  }

  /**
   * Removes a list of tags and updates the navigator metadata of the entry
   */
  async deleteNavigatorTags(
    tags: string[],
    apiOptions?: Omit<CatalogGetOptions, 'cachedOnly' | 'cancellable'>
  ): Promise<NavigatorMeta> {
    if (!this.canHaveNavigatorMetadata()) {
      return Promise.reject();
    }

    const navigatorMeta = await this.getNavigatorMeta(apiOptions);

    return new Promise((resolve, reject) => {
      deleteNavTags(navigatorMeta.identity, tags)
        .then(entity => {
          if (entity) {
            this.navigatorMeta = entity;
            this.navigatorMetaPromise = CancellablePromise.resolve(entity);
            this.saveLater();
            resolve(entity);
          } else {
            reject();
          }
        })
        .catch(reject);
    });
  }

  /**
   * Checks if the entry can have children or not without fetching additional metadata.
   */
  hasPossibleChildren(): boolean {
    return (
      this.path.length < 3 ||
      (!this.definition && !this.sourceMeta) ||
      (!!this.sourceMeta &&
        /^(?:struct|array|map)/i.test((<FieldSourceMeta>this.sourceMeta).type)) ||
      (!!this.definition &&
        !!this.definition.type &&
        /^(?:struct|array|map)/i.test(this.definition.type))
    );
  }

  /**
   * Returns the index representing the order in which the backend returned this entry.
   */
  getIndex(): number {
    return (this.definition && this.definition.index) || 0;
  }

  /**
   * Returns the dialect of this entry.
   */
  getDialect(): string {
    return this.getConnector().dialect || this.getConnector().id; // .id for editor v1
  }

  /**
   * Returns the connector for this entry
   */
  getConnector(): Connector {
    return this.dataCatalog.connector;
  }

  /**
   * Returns true if the entry represents a data source.
   *
   * @return {boolean}
   */
  isSource(): boolean {
    return this.path.length === 0;
  }

  /**
   * Returns true if the entry is a database.
   */
  isDatabase(): boolean {
    return this.path.length === 1;
  }

  /**
   * Returns true if the entry is a table or a view.
   *
   * @return {boolean}
   */
  isTableOrView(): boolean {
    return this.path.length === 2;
  }

  /**
   * Returns the default title used for the entry, the qualified path with type for fields. Optionally include
   * the comment after, if already resolved.
   */
  getTitle(includeComment?: boolean): string {
    let title = this.getQualifiedPath();
    if (this.isField()) {
      const type = this.getType();
      if (type) {
        title += ' (' + type + ')';
      }
    } else if (
      this.definition &&
      this.definition.type &&
      this.definition.type.toLowerCase() === 'materialized_view'
    ) {
      title += ' (' + I18n('Materialized') + ')';
    }
    if (includeComment && this.hasResolvedComment() && this.getResolvedComment()) {
      title += ' - ' + this.getResolvedComment();
    }
    return title;
  }

  /**
   * Returns the fully qualified path for this entry.
   */
  getQualifiedPath(): string {
    return this.path.join('.');
  }

  /**
   * Returns the display name for the entry, name or qualified path plus type for fields
   */
  getDisplayName(qualified?: boolean): string {
    const displayName = qualified ? this.getQualifiedPath() : this.name;
    if (this.isField()) {
      const type = this.getType();
      if (type) {
        return `${displayName} (${type})`;
      }
    }
    return displayName;
  }

  /**
   * Returns true for columns that are a primary key. Note that the definition has to come from a parent entry, i.e.
   * getChildren().
   */
  isPrimaryKey(): boolean {
    return !!(this.isColumn() && this.definition && (<ExtendedColumn>this.definition).primaryKey);
  }

  /**
   * Returns true if the entry is a partition key. Note that the definition has to come from a parent entry, i.e.
   * getChildren().
   */
  isPartitionKey(): boolean {
    return !!(this.definition && (<ExtendedColumn>this.definition).partitionKey);
  }

  /**
   * Returns true if the entry is a foreign key. Note that the definition has to come from a parent entry, i.e.
   * getChildren().
   */
  isForeignKey(): boolean {
    return !!this.definition && !!(<ExtendedColumn>this.definition).foreignKey;
  }

  /**
   * Returns true if the entry is either a partition or primary key. Note that the definition has to come from a parent entry, i.e.
   * getChildren().
   */
  isKey(): boolean {
    return this.isPartitionKey() || this.isPrimaryKey() || this.isForeignKey();
  }

  /**
   * Returns true if the entry is a table. It will be accurate once the source meta has been loaded.
   */
  isTable(): boolean {
    if (this.path.length === 2) {
      if (
        this.analysis &&
        this.analysis.details &&
        this.analysis.details.properties &&
        this.analysis.details.properties.table_type === 'VIRTUAL_VIEW'
      ) {
        return false;
      }
      if (this.sourceMeta) {
        return !(<TableSourceMeta>this.sourceMeta).is_view;
      }
      if (this.definition && this.definition.type) {
        return this.definition.type.toLowerCase() === 'table';
      }
      return true;
    }
    return false;
  }

  getHdfsFilePath(): string {
    const hdfs_link = this.analysis?.hdfs_link || '';
    return hdfs_link.replace('/filebrowser/view=', '');
  }

  /**
   * Returns true if the entry is an Iceberg table
   */
  isIcebergTable(): boolean {
    return this.analysis?.details?.stats?.table_type === 'ICEBERG';
  }

  isTransactionalTable(): boolean {
    return this.analysis?.details?.stats?.transactional === 'true';
  }

  /**
   * Returns true if the entry is a view. It will be accurate once the source meta has been loaded.
   */
  isView(): boolean {
    if (this.path.length === 2) {
      if (this.sourceMeta && (<TableSourceMeta>this.sourceMeta).is_view) {
        return true;
      }
      if (
        this.definition &&
        this.definition.type &&
        (this.definition.type.toLowerCase() === 'view' ||
          this.definition.type.toLowerCase() === 'materialized_view')
      ) {
        return true;
      }

      if (
        this.analysis &&
        this.analysis.details &&
        this.analysis.details.properties &&
        this.analysis.details.properties.table_type === 'VIRTUAL_VIEW'
      ) {
        return true;
      }
    }
    return false;
  }

  /**
   * Returns true if the entry is a ML Model. It will be accurate once the source meta has been loaded.
   */
  isModel(): boolean {
    return (
      this.path.length === 2 &&
      !!this.definition &&
      !!this.definition.type &&
      this.definition.type.toLowerCase() === 'model'
    );
  }

  /**
   * Returns true if the entry is a column.
   */
  isColumn(): boolean {
    return this.path.length === 3;
  }

  /**
   * Returns true if the entry is a column. It will be accurate once the source meta has been loaded or if loaded from
   * a parent entry via getChildren().
   */
  isComplex(): boolean {
    const sourceMeta = <FieldSourceMeta>this.sourceMeta;
    return !!(
      this.path.length > 2 &&
      ((sourceMeta && /^(?:struct|array|map)/i.test(sourceMeta.type)) ||
        (this.definition &&
          this.definition.type &&
          /^(?:struct|array|map)/i.test(this.definition.type)))
    );
  }

  /**
   * Returns true if the entry is a field, i.e. column or child of a complex type.
   */
  isField(): boolean {
    return this.path.length > 2;
  }

  /**
   * Returns true if the entry is an array. It will be accurate once the source meta has been loaded or if loaded from
   * a parent entry via getChildren().
   */
  isArray(): boolean {
    return (
      (!!this.sourceMeta && /^array/i.test((<FieldSourceMeta>this.sourceMeta).type)) ||
      (!!this.definition && !!this.definition.type && /^array/i.test(this.definition.type))
    );
  }

  /**
   * Returns true if the entry is a map. It will be accurate once the source meta has been loaded or if loaded from
   * a parent entry via getChildren().
   */
  isMap(): boolean {
    return (
      (!!this.sourceMeta && /^map/i.test((<FieldSourceMeta>this.sourceMeta).type)) ||
      (!!this.definition && !!this.definition.type && /^map/i.test(this.definition.type))
    );
  }

  /**
   * Returns true if the entry is a map value. It will be accurate once the source meta has been loaded or if loaded
   * from a parent entry via getChildren().
   */
  isMapValue(): boolean {
    return !!this.definition && !!this.definition.isMapValue;
  }

  /**
   * Returns the type of the entry. It will be accurate once the source meta has been loaded or if loaded from
   * a parent entry via getChildren().
   *
   * The returned string is always lower case and for complex entries the type definition is stripped to
   * either 'array', 'map' or 'struct'.
   */
  getType(): string {
    let type = this.getRawType();
    if (type.indexOf('<') !== -1) {
      type = type.substring(0, type.indexOf('<'));
    }
    return type.toLowerCase();
  }

  /**
   * Returns the raw type of the entry. It will be accurate once the source meta has been loaded or if loaded from
   * a parent entry via getChildren().
   *
   * For complex entries the type definition is the full version.
   */
  getRawType(): string {
    return (
      (this.sourceMeta && (<FieldSourceMeta>this.sourceMeta).type) ||
      (this.definition && this.definition.type) ||
      ''
    );
  }

  /**
   * Gets the source metadata for the entry. It will fetch it if not cached or if the refresh option is set.
   */
  getSourceMeta(options?: CatalogGetOptions): CancellablePromise<SourceMeta> {
    if (this.sourceMetaPromise && this.sourceMetaPromise.cancelled) {
      this.sourceMetaPromise = undefined;
    }
    if (!this.sourceMetaPromise && cachedOnly(options)) {
      return CancellablePromise.reject();
    }
    if (!this.sourceMetaPromise || shouldReload(options)) {
      return this.reloadSourceMeta(options);
    }
    return applyCancellable(this.sourceMetaPromise, options);
  }

  /**
   * Gets the analysis for the entry. It will fetch it if not cached or if the refresh option is set.
   */
  getAnalysis(
    options?: CatalogGetOptions & {
      refreshAnalysis?: boolean;
    }
  ): CancellablePromise<Analysis> {
    if (this.analysisPromise && this.analysisPromise.cancelled) {
      this.analysisPromise = undefined;
    }
    if (!this.analysisPromise && cachedOnly(options)) {
      return CancellablePromise.reject();
    }
    if (!this.analysisPromise || shouldReload(options)) {
      return this.reloadAnalysis(options);
    }
    return applyCancellable(this.analysisPromise, options);
  }

  /**
   * Gets the partitions for the entry. It will fetch it if not cached or if the refresh option is set.
   */
  getPartitions(options?: CatalogGetOptions): CancellablePromise<Partitions> {
    if (this.partitionsPromise && this.partitionsPromise.cancelled) {
      this.partitionsPromise = undefined;
    }
    if (!this.isTableOrView() || (!this.partitionsPromise && cachedOnly(options))) {
      return CancellablePromise.reject();
    }
    if (!this.partitionsPromise || shouldReload(options)) {
      return this.reloadPartitions(options);
    }
    return applyCancellable(this.partitionsPromise, options);
  }

  /**
   * Gets the Navigator metadata for the entry. It will fetch it if not cached or if the refresh option is set.
   */
  getNavigatorMeta(options?: CatalogGetOptions): CancellablePromise<NavigatorMeta> {
    if (this.navigatorMetaPromise && this.navigatorMetaPromise.cancelled) {
      this.navigatorMetaPromise = undefined;
    }
    options = forceSilencedErrors(options);
    if (!this.canHaveNavigatorMetadata() || (!this.navigatorMetaPromise && cachedOnly(options))) {
      return CancellablePromise.reject();
    }
    if (!this.navigatorMetaPromise || shouldReload(options)) {
      return this.reloadNavigatorMeta(options);
    }
    return applyCancellable(this.navigatorMetaPromise, options);
  }

  /**
   * Gets the SQL Analyzer metadata for the entry. It will fetch it if not cached or if the refresh option is set.
   */
  getSqlAnalyzerMeta(
    options: CatalogGetOptions & { sqlAnalyzer: SqlAnalyzer }
  ): CancellablePromise<SqlAnalyzerMeta> {
    if (this.sqlAnalyzerMetaPromise && this.sqlAnalyzerMetaPromise.cancelled) {
      this.sqlAnalyzerMetaPromise = undefined;
    }
    options.silenceErrors = true;

    if (!this.dataCatalog.canHaveSqlAnalyzerMeta() || !this.isTableOrView()) {
      return CancellablePromise.reject();
    }
    if (!this.sqlAnalyzerMetaPromise && cachedOnly(options)) {
      return CancellablePromise.reject();
    }
    if (!this.sqlAnalyzerMetaPromise || shouldReload(options)) {
      return this.reloadSqlAnalyzerMeta(options);
    }
    return applyCancellable(this.sqlAnalyzerMetaPromise, options);
  }

  /**
   * Gets the sample for the entry, if unknown it will first check if any parent table already has the sample. It
   * will fetch it if not cached or if the refresh option is set.
   */
  getSample(
    options?: CatalogGetOptions & {
      operation?: string;
    }
  ): CancellablePromise<Sample> {
    if (this.samplePromise && this.samplePromise.cancelled) {
      this.samplePromise = undefined;
    }
    // This prevents caching of any non-standard sample queries, i.e. DISTINCT etc.
    if (options && options.operation && options.operation !== 'default') {
      const operation = options.operation;
      const samplePromise = fetchSample({
        entry: this,
        operation,
        silenceErrors: options.silenceErrors
      });
      return applyCancellable(samplePromise, options);
    }

    // Check if parent has a sample that we can reuse
    if (!this.samplePromise && this.isColumn() && !shouldReload(options)) {
      this.samplePromise = new CancellablePromise<Sample>(async (resolve, reject, onCancel) => {
        const cancellablePromises: Cancellable[] = [];

        onCancel(() => {
          cancellablePromises.forEach(promise => promise.cancel());
        });

        try {
          const tableEntry = await this.dataCatalog.getEntry({
            namespace: this.namespace,
            compute: this.compute,
            path: this.path.slice(0, 2),
            definition: { type: 'table' }
          });

          if (tableEntry && tableEntry.samplePromise) {
            cancellablePromises.push(applyCancellable(tableEntry.samplePromise, options));

            const parentSample = await tableEntry.samplePromise;

            const colSample = {
              hueTimestamp: parentSample.hueTimestamp,
              has_more: parentSample.has_more,
              type: parentSample.type,
              data: <FieldSample[][]>[],
              meta: <SampleMeta[]>[]
            };
            if (parentSample.meta) {
              for (let i = 0; i < parentSample.meta.length; i++) {
                if (parentSample.meta[i].name.toLowerCase() === this.name.toLowerCase()) {
                  colSample.meta[0] = parentSample.meta[i];
                  parentSample.data.forEach(parentRow => {
                    colSample.data.push([parentRow[i]]);
                  });
                  break;
                }
              }
            }
            if (colSample.meta.length) {
              this.sample = colSample;
              resolve(this.sample);
              return;
            }
          }
        } catch (err) {}

        if (cachedOnly(options)) {
          reject();
        } else {
          const reloadPromise = this.reloadSample(options);
          try {
            resolve(await reloadPromise);
          } catch (err) {
            reject();
          }
        }
      });
      return applyCancellable(this.samplePromise, options);
    }

    if (!this.samplePromise && cachedOnly(options)) {
      return CancellablePromise.reject();
    }
    if (!this.samplePromise || shouldReload(options)) {
      return this.reloadSample(options);
    }
    return applyCancellable(this.samplePromise, options);
  }

  /**
   * Gets the top aggregate UDFs for the entry if it's a table or view. It will fetch it if not cached or if the refresh option is set.
   */
  getTopAggs(
    options: CatalogGetOptions & { sqlAnalyzer: SqlAnalyzer }
  ): CancellablePromise<TopAggs> {
    const promise = new CancellablePromise<TopAggs>(async (resolve, reject, onCancel) => {
      const multiTableEntry = await getMultiTableEntry(this);
      const topAggsPromise = multiTableEntry.getTopAggs(options);
      onCancel(() => {
        topAggsPromise.cancel();
      });
      topAggsPromise.then(resolve).catch(reject);
    });
    return applyCancellable(promise);
  }

  /**
   * Gets the top filters for the entry if it's a table or view. It will fetch it if not cached or if the refresh option is set.
   *
   * @return {CancellableJqPromise}
   */
  getTopFilters(
    options: CatalogGetOptions & { sqlAnalyzer: SqlAnalyzer }
  ): CancellablePromise<TopFilters> {
    const promise = new CancellablePromise<TopFilters>(async (resolve, reject, onCancel) => {
      const multiTableEntry = await getMultiTableEntry(this);
      const topFiltersPromise = multiTableEntry.getTopFilters(options);
      onCancel(() => {
        topFiltersPromise.cancel();
      });
      topFiltersPromise.then(resolve).catch(reject);
    });
    return applyCancellable(promise);
  }

  /**
   * Gets the top joins for the entry if it's a table or view. It will fetch it if not cached or if the refresh option is set.
   */
  getTopJoins(
    options: CatalogGetOptions & { sqlAnalyzer: SqlAnalyzer }
  ): CancellablePromise<TopJoins> {
    const promise = new CancellablePromise<TopJoins>(async (resolve, reject, onCancel) => {
      const multiTableEntry = await getMultiTableEntry(this);
      const topJoinsPromise = multiTableEntry.getTopJoins(options);
      onCancel(() => {
        topJoinsPromise.cancel();
      });
      topJoinsPromise.then(resolve).catch(reject);
    });
    return applyCancellable(promise);
  }
}

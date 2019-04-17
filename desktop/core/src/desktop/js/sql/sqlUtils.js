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

import CancellablePromise from 'api/cancellablePromise';
import dataCatalog from 'catalog/dataCatalog';

const hiveReservedKeywords = {
  ALL: true,
  ALTER: true,
  AND: true,
  ARRAY: true,
  AS: true,
  AUTHORIZATION: true,
  BETWEEN: true,
  BIGINT: true,
  BINARY: true,
  BOOLEAN: true,
  BOTH: true,
  BY: true,
  CACHE: true,
  CASE: true,
  CAST: true,
  CHAR: true,
  COLUMN: true,
  COMMIT: true,
  CONF: true,
  CONSTRAINT: true,
  CREATE: true,
  CROSS: true,
  CUBE: true,
  CURRENT: true,
  CURRENT_DATE: true,
  CURRENT_TIMESTAMP: true,
  CURSOR: true,
  DATABASE: true,
  DATE: true,
  DAYOFWEEK: true,
  DECIMAL: true,
  DELETE: true,
  DESCRIBE: true,
  DISTINCT: true,
  DIV: true,
  DOUBLE: true,
  DROP: true,
  ELSE: true,
  END: true,
  EXCHANGE: true,
  EXISTS: true,
  EXTENDED: true,
  EXTERNAL: true,
  EXTRACT: true,
  FALSE: true,
  FETCH: true,
  FLOAT: true,
  FLOOR: true,
  FOLLOWING: true,
  FOR: true,
  FOREIGN: true,
  FROM: true,
  FULL: true,
  FUNCTION: true,
  GRANT: true,
  GROUP: true,
  GROUPING: true,
  HAVING: true,
  IF: true,
  IMPORT: true,
  IN: true,
  INNER: true,
  INSERT: true,
  INT: true,
  INTEGER: true,
  INTERSECT: true,
  INTERVAL: true,
  INTO: true,
  IS: true,
  JOIN: true,
  LATERAL: true,
  LEFT: true,
  LESS: true,
  LIKE: true,
  LOCAL: true,
  MACRO: true,
  MAP: true,
  MORE: true,
  NONE: true,
  NOT: true,
  NULL: true,
  NUMERIC: true,
  OF: true,
  ON: true,
  ONLY: true,
  OR: true,
  ORDER: true,
  OUT: true,
  OUTER: true,
  OVER: true,
  PARTIALSCAN: true,
  PARTITION: true,
  PERCENT: true,
  PRECEDING: true,
  PRECISION: true,
  PRESERVE: true,
  PRIMARY: true,
  PROCEDURE: true,
  RANGE: true,
  READS: true,
  REDUCE: true,
  REFERENCES: true,
  REGEXP: true,
  REVOKE: true,
  RIGHT: true,
  RLIKE: true,
  ROLLBACK: true,
  ROLLUP: true,
  ROW: true,
  ROWS: true,
  SELECT: true,
  SET: true,
  SMALLINT: true,
  START: true,
  SYNC: true,
  TABLE: true,
  TABLESAMPLE: true,
  THEN: true,
  TIME: true,
  TIMESTAMP: true,
  TO: true,
  TRANSFORM: true,
  TRIGGER: true,
  TRUE: true,
  TRUNCATE: true,
  UNBOUNDED: true,
  UNION: true,
  UNIQUEJOIN: true,
  UPDATE: true,
  USER: true,
  USING: true,
  UTC_TIMESTAMP: true,
  VALUES: true,
  VARCHAR: true,
  VIEWS: true,
  WHEN: true,
  WHERE: true,
  WINDOW: true,
  WITH: true
};

const extraHiveReservedKeywords = {
  ASC: true,
  CLUSTER: true,
  DESC: true,
  DISTRIBUTE: true,
  FORMATTED: true,
  FUNCTION: true,
  INDEX: true,
  INDEXES: true,
  LIMIT: true,
  LOCK: true,
  SCHEMA: true,
  SORT: true
};

const impalaReservedKeywords = {
  ADD: true,
  AGGREGATE: true,
  ALL: true,
  ALLOCATE: true,
  ALTER: true,
  ANALYTIC: true,
  AND: true,
  ANTI: true,
  ANY: true,
  API_VERSION: true,
  ARE: true,
  ARRAY: true,
  ARRAY_AGG: true,
  ARRAY_MAX_CARDINALITY: true,
  AS: true,
  ASC: true,
  ASENSITIVE: true,
  ASYMMETRIC: true,
  AT: true,
  ATOMIC: true,
  AUTHORIZATION: true,
  AVRO: true,
  BEGIN_FRAME: true,
  BEGIN_PARTITION: true,
  BETWEEN: true,
  BIGINT: true,
  BINARY: true,
  BLOB: true,
  BLOCK_SIZE: true,
  BOOLEAN: true,
  BOTH: true,
  BY: true,
  CACHED: true,
  CALLED: true,
  CARDINALITY: true,
  CASCADE: true,
  CASCADED: true,
  CASE: true,
  CAST: true,
  CHANGE: true,
  CHAR: true,
  CHARACTER: true,
  CLASS: true,
  CLOB: true,
  CLOSE_FN: true,
  COLLATE: true,
  COLLECT: true,
  COLUMN: true,
  COLUMNS: true,
  COMMENT: true,
  COMMIT: true,
  COMPRESSION: true,
  COMPUTE: true,
  CONDITION: true,
  CONNECT: true,
  CONSTRAINT: true,
  CONTAINS: true,
  CONVERT: true,
  COPY: true,
  CORR: true,
  CORRESPONDING: true,
  COVAR_POP: true,
  COVAR_SAMP: true,
  CREATE: true,
  CROSS: true,
  CUBE: true,
  CURRENT: true,
  CURRENT_DATE: true,
  CURRENT_DEFAULT_TRANSFORM_GROUP: true,
  CURRENT_PATH: true,
  CURRENT_ROLE: true,
  CURRENT_ROW: true,
  CURRENT_SCHEMA: true,
  CURRENT_TIME: true,
  CURRENT_TRANSFORM_GROUP_FOR_TYPE: true,
  CURSOR: true,
  CYCLE: true,
  DATA: true,
  DATABASE: true,
  DATABASES: true,
  DATE: true,
  DATETIME: true,
  DEALLOCATE: true,
  DEC: true,
  DECFLOAT: true,
  DECIMAL: true,
  DECLARE: true,
  DEFINE: true,
  DELETE: true,
  DELIMITED: true,
  DEREF: true,
  DESC: true,
  DESCRIBE: true,
  DETERMINISTIC: true,
  DISCONNECT: true,
  DISTINCT: true,
  DIV: true,
  DOUBLE: true,
  DROP: true,
  DYNAMIC: true,
  EACH: true,
  ELEMENT: true,
  ELSE: true,
  EMPTY: true,
  ENCODING: true,
  END: true,
  END_FRAME: true,
  END_PARTITION: true,
  EQUALS: true,
  ESCAPE: true,
  ESCAPED: true,
  EVERY: true,
  EXCEPT: true,
  EXEC: true,
  EXECUTE: true,
  EXISTS: true,
  EXPLAIN: true,
  EXTENDED: true,
  EXTERNAL: true,
  FALSE: true,
  FETCH: true,
  FIELDS: true,
  FILEFORMAT: true,
  FILES: true,
  FILTER: true,
  FINALIZE_FN: true,
  FIRST: true,
  FLOAT: true,
  FOLLOWING: true,
  FOR: true,
  FOREIGN: true,
  FORMAT: true,
  FORMATTED: true,
  FRAME_ROW: true,
  FREE: true,
  FROM: true,
  FULL: true,
  FUNCTION: true,
  FUNCTIONS: true,
  FUSION: true,
  GET: true,
  GLOBAL: true,
  GRANT: true,
  GROUP: true,
  GROUPING: true,
  GROUPS: true,
  HASH: true,
  HAVING: true,
  HOLD: true,
  IF: true,
  IGNORE: true,
  ILIKE: true,
  IN: true,
  INCREMENTAL: true,
  INDICATOR: true,
  INIT_FN: true,
  INITIAL: true,
  INNER: true,
  INOUT: true,
  INPATH: true,
  INSENSITIVE: true,
  INSERT: true,
  INT: true,
  INTEGER: true,
  INTERMEDIATE: true,
  INTERSECT: true,
  INTERSECTION: true,
  INTERVAL: true,
  INTO: true,
  INVALIDATE: true,
  IREGEXP: true,
  IS: true,
  JOIN: true,
  JSON_ARRAY: true,
  JSON_ARRAYAGG: true,
  JSON_EXISTS: true,
  JSON_OBJECT: true,
  JSON_OBJECTAGG: true,
  JSON_QUERY: true,
  JSON_TABLE: true,
  JSON_TABLE_PRIMITIVE: true,
  JSON_VALUE: true,
  KEY: true,
  KUDU: true,
  LARGE: true,
  LAST: true,
  LATERAL: true,
  LEADING: true,
  LEFT: true,
  LIKE: true,
  LIKE_REGEX: true,
  LIMIT: true,
  LINES: true,
  LISTAGG: true,
  LOAD: true,
  LOCAL: true,
  LOCALTIMESTAMP: true,
  LOCATION: true,
  MAP: true,
  MATCH: true,
  MATCH_NUMBER: true,
  MATCH_RECOGNIZE: true,
  MATCHES: true,
  MERGE: true,
  MERGE_FN: true,
  METADATA: true,
  METHOD: true,
  MODIFIES: true,
  MULTISET: true,
  NATIONAL: true,
  NATURAL: true,
  NCHAR: true,
  NCLOB: true,
  NO: true,
  NONE: true,
  NORMALIZE: true,
  NOT: true,
  NTH_VALUE: true,
  NULL: true,
  NULLS: true,
  NUMERIC: true,
  OCCURRENCES_REGEX: true,
  OCTET_LENGTH: true,
  OF: true,
  OFFSET: true,
  OMIT: true,
  ON: true,
  ONE: true,
  ONLY: true,
  OR: true,
  ORDER: true,
  OUT: true,
  OUTER: true,
  OVER: true,
  OVERLAPS: true,
  OVERLAY: true,
  OVERWRITE: true,
  PARQUET: true,
  PARQUETFILE: true,
  PARTITION: true,
  PARTITIONED: true,
  PARTITIONS: true,
  PATTERN: true,
  PER: true,
  PERCENT: true,
  PERCENTILE_CONT: true,
  PERCENTILE_DISC: true,
  PORTION: true,
  POSITION: true,
  POSITION_REGEX: true,
  PRECEDES: true,
  PRECEDING: true,
  PREPARE: true,
  PREPARE_FN: true,
  PRIMARY: true,
  PROCEDURE: true,
  PRODUCED: true,
  PTF: true,
  PURGE: true,
  RANGE: true,
  RCFILE: true,
  READS: true,
  REAL: true,
  RECOVER: true,
  RECURSIVE: true,
  REF: true,
  REFERENCES: true,
  REFERENCING: true,
  REFRESH: true,
  REGEXP: true,
  REGR_AVGX: true,
  REGR_AVGY: true,
  REGR_COUNT: true,
  REGR_INTERCEPT: true,
  REGR_R2: true,
  REGR_SLOPE: true,
  REGR_SXX: true,
  REGR_SXY: true,
  REGR_SYY: true,
  RELEASE: true,
  RENAME: true,
  REPEATABLE: true,
  REPLACE: true,
  REPLICATION: true,
  RESTRICT: true,
  RETURNS: true,
  REVOKE: true,
  RIGHT: true,
  RLIKE: true,
  ROLE: true,
  ROLES: true,
  ROLLBACK: true,
  ROLLUP: true,
  ROW: true,
  ROWS: true,
  RUNNING: true,
  SAVEPOINT: true,
  SCHEMA: true,
  SCHEMAS: true,
  SCOPE: true,
  SCROLL: true,
  SEARCH: true,
  SEEK: true,
  SELECT: true,
  SEMI: true,
  SENSITIVE: true,
  SEQUENCEFILE: true,
  SERDEPROPERTIES: true,
  SERIALIZE_FN: true,
  SET: true,
  SHOW: true,
  SIMILAR: true,
  SKIP: true,
  SMALLINT: true,
  SOME: true,
  SORT: true,
  SPECIFIC: true,
  SPECIFICTYPE: true,
  SQLEXCEPTION: true,
  SQLSTATE: true,
  SQLWARNING: true,
  STATIC: true,
  STATS: true,
  STORED: true,
  STRAIGHT_JOIN: true,
  STRING: true,
  STRUCT: true,
  SUBMULTISET: true,
  SUBSET: true,
  SUBSTRING_REGEX: true,
  SUCCEEDS: true,
  SYMBOL: true,
  SYMMETRIC: true,
  SYSTEM_TIME: true,
  SYSTEM_USER: true,
  TABLE: true,
  TABLES: true,
  TABLESAMPLE: true,
  TBLPROPERTIES: true,
  TERMINATED: true,
  TEXTFILE: true,
  THEN: true,
  TIMESTAMP: true,
  TIMEZONE_HOUR: true,
  TIMEZONE_MINUTE: true,
  TINYINT: true,
  TO: true,
  TRAILING: true,
  TRANSLATE_REGEX: true,
  TRANSLATION: true,
  TREAT: true,
  TRIGGER: true,
  TRIM_ARRAY: true,
  TRUE: true,
  TRUNCATE: true,
  UESCAPE: true,
  UNBOUNDED: true,
  UNCACHED: true,
  UNION: true,
  UNIQUE: true,
  UNKNOWN: true,
  UNNEST: true,
  UPDATE: true,
  UPDATE_FN: true,
  UPSERT: true,
  USE: true,
  USER: true,
  USING: true,
  VALUE_OF: true,
  VALUES: true,
  VARBINARY: true,
  VARCHAR: true,
  VARYING: true,
  VERSIONING: true,
  VIEW: true,
  WHEN: true,
  WHENEVER: true,
  WHERE: true,
  WIDTH_BUCKET: true,
  WINDOW: true,
  WITH: true,
  WITHIN: true,
  WITHOUT: true
};

const identifierEquals = (a, b) =>
  a &&
  b &&
  a
    .replace(/^\s*`/, '')
    .replace(/`\s*$/, '')
    .toLowerCase() ===
    b
      .replace(/^\s*`/, '')
      .replace(/`\s*$/, '')
      .toLowerCase();

const autocompleteFilter = (filter, entries) => {
  const lowerCaseFilter = filter.toLowerCase();
  return entries.filter(suggestion => {
    // TODO: Extend with fuzzy matches
    let foundIndex = suggestion.value.toLowerCase().indexOf(lowerCaseFilter);
    if (foundIndex !== -1) {
      if (
        foundIndex === 0 ||
        (suggestion.filterValue &&
          suggestion.filterValue.toLowerCase().indexOf(lowerCaseFilter) === 0)
      ) {
        suggestion.filterWeight = 3;
      } else {
        suggestion.filterWeight = 2;
      }
    } else if (
      suggestion.details &&
      suggestion.details.comment &&
      lowerCaseFilter.indexOf(' ') === -1
    ) {
      foundIndex = suggestion.details.comment.toLowerCase().indexOf(lowerCaseFilter);
      if (foundIndex !== -1) {
        suggestion.filterWeight = 1;
        suggestion.matchComment = true;
      }
    }
    if (foundIndex !== -1) {
      suggestion.matchIndex = foundIndex;
      suggestion.matchLength = filter.length;
      return true;
    }
    return false;
  });
};

const sortSuggestions = (suggestions, filter, sortOverride) => {
  suggestions.sort((a, b) => {
    if (filter) {
      if (
        typeof a.filterWeight !== 'undefined' &&
        typeof b.filterWeight !== 'undefined' &&
        b.filterWeight !== a.filterWeight
      ) {
        return b.filterWeight - a.filterWeight;
      }
      if (typeof a.filterWeight !== 'undefined' && typeof b.filterWeight === 'undefined') {
        return -1;
      }
      if (typeof a.filterWeight === 'undefined' && typeof b.filterWeight !== 'undefined') {
        return 1;
      }
    }
    if (sortOverride && sortOverride.partitionColumnsFirst) {
      if (a.partitionKey && !b.partitionKey) {
        return -1;
      }
      if (b.partitionKey && !a.partitionKey) {
        return 1;
      }
    }
    const aWeight = a.category.weight + (a.weightAdjust || 0);
    const bWeight = b.category.weight + (b.weightAdjust || 0);
    if (typeof aWeight !== 'undefined' && typeof bWeight !== 'undefined' && bWeight !== aWeight) {
      return bWeight - aWeight;
    }
    if (typeof aWeight !== 'undefined' && typeof bWeight === 'undefined') {
      return -1;
    }
    if (typeof aWeight === 'undefined' && typeof bWeight !== 'undefined') {
      return 1;
    }
    return a.value.localeCompare(b.value);
  });
};

const identifierChainToPath = identifierChain => identifierChain.map(identifier => identifier.name);

/**
 *
 * @param {Object} options
 * @param {String} options.sourceType
 * @param {ContextNamespace} options.namespace
 * @param {ContextCompute} options.compute
 * @param {boolean} [options.temporaryOnly] - Default: false
 * @param {Object[]} [options.identifierChain]
 * @param {Object[]} [options.tables]
 * @param {Object} [options.cancellable]
 * @param {Object} [options.cachedOnly]
 *
 * @return {CancellablePromise}
 */
const resolveCatalogEntry = options => {
  const cancellablePromises = [];
  const deferred = $.Deferred();
  const promise = new CancellablePromise(deferred, undefined, cancellablePromises);
  dataCatalog.applyCancellable(promise, options);

  if (!options.identifierChain) {
    deferred.reject();
    return promise;
  }

  const findInTree = (currentEntry, fieldsToGo) => {
    if (fieldsToGo.length === 0) {
      deferred.reject();
      return;
    }

    let nextField;
    if (currentEntry.getType() === 'map') {
      nextField = 'value';
    } else if (currentEntry.getType() === 'array') {
      nextField = 'item';
    } else {
      nextField = fieldsToGo.shift();
    }

    cancellablePromises.push(
      currentEntry
        .getChildren({
          cancellable: options.cancellable,
          cachedOnly: options.cachedOnly,
          silenceErrors: true
        })
        .done(childEntries => {
          let foundEntry = undefined;
          childEntries.some(childEntry => {
            if (identifierEquals(childEntry.name, nextField)) {
              foundEntry = childEntry;
              return true;
            }
          });
          if (foundEntry && fieldsToGo.length) {
            findInTree(foundEntry, fieldsToGo);
          } else if (foundEntry) {
            deferred.resolve(foundEntry);
          } else {
            deferred.reject();
          }
        })
        .fail(deferred.reject)
    );
  };

  const findTable = tablesToGo => {
    if (tablesToGo.length === 0) {
      deferred.reject();
      return;
    }

    const nextTable = tablesToGo.pop();
    if (typeof nextTable.subQuery !== 'undefined') {
      findTable(tablesToGo);
      return;
    }

    cancellablePromises.push(
      dataCatalog
        .getChildren({
          sourceType: options.sourceType,
          namespace: options.namespace,
          compute: options.compute,
          path: identifierChainToPath(nextTable.identifierChain),
          cachedOnly: options && options.cachedOnly,
          cancellable: options && options.cancellable,
          temporaryOnly: options && options.temporaryOnly,
          silenceErrors: true
        })
        .done(childEntries => {
          let foundEntry = undefined;
          childEntries.some(childEntry => {
            if (identifierEquals(childEntry.name, options.identifierChain[0].name)) {
              foundEntry = childEntry;
              return true;
            }
          });

          if (foundEntry && options.identifierChain.length > 1) {
            findInTree(foundEntry, identifierChainToPath(options.identifierChain.slice(1)));
          } else if (foundEntry) {
            deferred.resolve(foundEntry);
          } else {
            findTable(tablesToGo);
          }
        })
        .fail(deferred.reject)
    );
  };

  if (options.tables) {
    findTable(options.tables.concat());
  } else {
    dataCatalog
      .getEntry({
        sourceType: options.sourceType,
        namespace: options.namespace,
        compute: options.compute,
        path: [],
        cachedOnly: options && options.cachedOnly,
        cancellable: options && options.cancellable,
        temporaryOnly: options && options.temporaryOnly,
        silenceErrors: true
      })
      .done(entry => {
        findInTree(entry, identifierChainToPath(options.identifierChain));
      });
  }

  return promise;
};

export default {
  autocompleteFilter: autocompleteFilter,
  backTickIfNeeded: (sourceType, identifier) => {
    if (identifier.indexOf('`') === 0) {
      return identifier;
    }
    const upperIdentifier = identifier.toUpperCase();
    if (
      sourceType === 'hive' &&
      (hiveReservedKeywords[upperIdentifier] || extraHiveReservedKeywords[upperIdentifier])
    ) {
      return '`' + identifier + '`';
    }
    if (sourceType === 'impala' && impalaReservedKeywords[upperIdentifier]) {
      return '`' + identifier + '`';
    }
    if (
      sourceType !== 'impala' &&
      sourceType !== 'hive' &&
      (impalaReservedKeywords[upperIdentifier] ||
        hiveReservedKeywords[upperIdentifier] ||
        extraHiveReservedKeywords[upperIdentifier])
    ) {
      return '`' + identifier + '`';
    }
    if (!/^[A-Za-z][A-Za-z0-9_]*$/.test(identifier)) {
      return '`' + identifier + '`';
    }
    return identifier;
  },
  locationEquals: (a, b) =>
    a &&
    b &&
    a.first_line === b.first_line &&
    a.first_column === b.first_column &&
    a.last_line === b.last_line &&
    a.last_column === b.last_column,
  identifierEquals: identifierEquals,
  sortSuggestions: sortSuggestions,
  resolveCatalogEntry: resolveCatalogEntry,
  identifierChainToPath: identifierChainToPath
};

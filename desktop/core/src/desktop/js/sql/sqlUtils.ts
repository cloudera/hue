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

import { Cancellable, CancellablePromise } from 'api/cancellablePromise';
import { applyCancellable } from 'catalog/catalogUtils';
import DataCatalogEntry from 'catalog/DataCatalogEntry';

import dataCatalog from 'catalog/dataCatalog';
import { IdentifierChainEntry, ParsedLocation, ParsedTable } from 'parse/types';
import sqlReferenceRepository from 'sql/reference/sqlReferenceRepository';
import {
  CommentDetails,
  Suggestion
} from 'apps/editor/components/aceEditor/autocomplete/AutocompleteResults';
import { Compute, Connector, Namespace } from 'config/types';
import { SqlReferenceProvider } from './reference/types';

const identifierEquals = (a?: string, b?: string): boolean =>
  !!a &&
  !!b &&
  a.replace(/^\s*`/, '').replace(/`\s*$/, '').toLowerCase() ===
    b.replace(/^\s*`/, '').replace(/`\s*$/, '').toLowerCase();

const autocompleteFilter = (filter: string, entries: Suggestion[]): Suggestion[] => {
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
      (<CommentDetails>suggestion.details).comment &&
      lowerCaseFilter.indexOf(' ') === -1
    ) {
      foundIndex = (<CommentDetails>suggestion.details).comment
        .toLowerCase()
        .indexOf(lowerCaseFilter);
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

export interface SortOverride {
  partitionColumnsFirst?: boolean;
}

const sortSuggestions = (
  suggestions: Suggestion[],
  filter: string,
  sortOverride?: SortOverride | null
): void => {
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
    const aWeight = (a.category.weight || 0) + (a.weightAdjust || 0);
    const bWeight = (b.category.weight || 0) + (b.weightAdjust || 0);
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

const identifierChainToPath = (identifierChain: IdentifierChainEntry[]): string[] =>
  identifierChain.map(identifier => identifier.name);

export const resolveCatalogEntry = (options: {
  connector: Connector;
  namespace: Namespace;
  compute: Compute;
  temporaryOnly?: boolean;
  cachedOnly?: boolean;
  cancellable?: boolean;
  identifierChain?: IdentifierChainEntry[];
  tables?: ParsedTable[];
}): CancellablePromise<DataCatalogEntry> => {
  const promise = new CancellablePromise<DataCatalogEntry>((resolve, reject, onCancel) => {
    const cancellablePromises: Cancellable[] = [];

    onCancel(() => {
      cancellablePromises.forEach(cancellable => cancellable.cancel());
    });
    if (!options.identifierChain) {
      reject();
      return;
    }

    const findInTree = (currentEntry: DataCatalogEntry, fieldsToGo: string[]): void => {
      if (fieldsToGo.length === 0) {
        reject();
        return;
      }

      let nextField: string;
      if (currentEntry.getType() === 'map') {
        nextField = 'value';
      } else if (currentEntry.getType() === 'array') {
        nextField = 'item';
      } else {
        nextField = fieldsToGo.shift() || '';
      }

      const childPromise = currentEntry.getChildren({
        cancellable: !!options.cancellable,
        cachedOnly: !!options.cachedOnly,
        silenceErrors: true
      });

      cancellablePromises.push(childPromise);

      childPromise
        .then(childEntries => {
          let foundEntry = undefined;
          childEntries.some((childEntry: { name: string }) => {
            if (identifierEquals(childEntry.name, nextField)) {
              foundEntry = childEntry;
              return true;
            }
          });
          if (foundEntry && fieldsToGo.length) {
            findInTree(foundEntry, fieldsToGo);
          } else if (foundEntry) {
            resolve(foundEntry);
          } else {
            reject();
          }
        })
        .catch(reject);
    };

    const findTable = (tablesToGo: ParsedTable[]): void => {
      if (tablesToGo.length === 0) {
        reject();
        return;
      }

      const nextTable = tablesToGo.pop();
      if (nextTable && typeof nextTable.subQuery !== 'undefined') {
        findTable(tablesToGo);
        return;
      }

      const childPromise = dataCatalog.getChildren({
        connector: options.connector,
        namespace: options.namespace,
        compute: options.compute,
        path: identifierChainToPath((nextTable && nextTable.identifierChain) || []),
        cachedOnly: !!options.cachedOnly,
        cancellable: !!options.cancellable,
        temporaryOnly: !!options.temporaryOnly,
        silenceErrors: true
      });

      cancellablePromises.push(childPromise);

      childPromise
        .then(childEntries => {
          let foundEntry = undefined;
          childEntries.some((childEntry: { name: string }) => {
            if (
              options.identifierChain &&
              options.identifierChain.length &&
              identifierEquals(childEntry.name, options.identifierChain[0].name)
            ) {
              foundEntry = childEntry;
              return true;
            }
          });

          if (foundEntry && options.identifierChain && options.identifierChain.length > 1) {
            findInTree(foundEntry, identifierChainToPath(options.identifierChain.slice(1)));
          } else if (foundEntry) {
            resolve(foundEntry);
          } else {
            findTable(tablesToGo);
          }
        })
        .catch(reject);
    };

    if (options.tables) {
      findTable(options.tables.concat());
    } else {
      dataCatalog
        .getEntry({
          namespace: options.namespace,
          compute: options.compute,
          connector: options.connector,
          path: [],
          cachedOnly: !!options.cachedOnly,
          temporaryOnly: !!options.temporaryOnly
        })
        .then(entry => {
          if (options.identifierChain) {
            findInTree(entry, identifierChainToPath(options.identifierChain));
          }
        });
    }
  });

  return applyCancellable(promise, options);
};

export default {
  autocompleteFilter: autocompleteFilter,
  backTickIfNeeded: async (
    connector: Connector,
    identifier: string,
    sqlReferenceProvider?: SqlReferenceProvider,
    forceAppendBacktick?: boolean
  ): Promise<string> => {
    if (forceAppendBacktick) {
      return identifier + '`';
    }
    const quoteChar =
      (connector.dialect_properties && connector.dialect_properties.sql_identifier_quote) || '`';
    if (identifier.indexOf(quoteChar) === 0) {
      return identifier;
    }
    const reservedKeywords = await (
      sqlReferenceProvider || sqlReferenceRepository
    ).getReservedKeywords(connector.dialect || 'generic');
    if (reservedKeywords.has(identifier.toUpperCase())) {
      return quoteChar + identifier + quoteChar;
    }

    if (!/^[A-Za-z][A-Za-z0-9_]*$/.test(identifier)) {
      return quoteChar + identifier + quoteChar;
    }
    return identifier;
  },
  locationEquals: (a?: ParsedLocation, b?: ParsedLocation): boolean =>
    !!a &&
    !!b &&
    a.first_line === b.first_line &&
    a.first_column === b.first_column &&
    a.last_line === b.last_line &&
    a.last_column === b.last_column,
  identifierEquals: identifierEquals,
  sortSuggestions: sortSuggestions,
  identifierChainToPath: identifierChainToPath
};

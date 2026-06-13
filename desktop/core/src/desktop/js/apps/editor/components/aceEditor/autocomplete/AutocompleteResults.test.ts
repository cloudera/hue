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

import * as Vue from 'vue';
import * as CatalogApi from 'catalog/api';
import { CancellablePromise } from 'api/cancellablePromise';
import AutocompleteResults, { Suggestion } from './AutocompleteResults';
import dataCatalog from 'catalog/dataCatalog';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';
import * as sqlUdfRepository from 'sql/reference/sqlUdfRepository';
import sqlReferenceRepository from 'sql/reference/sqlReferenceRepository';
import sleep from 'utils/timing/sleep';
import * as hueConfig from 'config/hueConfig';
import { Ace } from 'ext/ace';
import Executor from '../../../execution/executor';
import sqlAnalyzerRepository from 'catalog/analyzer/sqlAnalyzerRepository';
import { AutocompleteParseResult } from 'parse/types';
import { SetDetails, UdfDetails } from 'sql/reference/types';
import { HueConfig } from 'config/types';

describe('AutocompleteResults.ts', () => {
  jest.spyOn(Vue, 'onBeforeUnmount').mockImplementation(() => undefined);

  const sourceMetaSpy = jest
    .spyOn(CatalogApi, 'fetchSourceMetadata')
    .mockImplementation(options => {
      if (options.entry.path.length === 0) {
        return CancellablePromise.resolve(JSON.parse('{"status": 0, "databases": ["default"]}'));
      }
      if (options.entry.path.length === 1) {
        return CancellablePromise.resolve(
          JSON.parse(
            '{"status": 0, "tables_meta": [{"comment": "comment", "type": "Table", "name": "foo"}, {"comment": null, "type": "View", "name": "bar_view"}, {"comment": null, "type": "Table", "name": "bar"}]}'
          )
        );
      }
      if (options.entry.path.length === 2) {
        return CancellablePromise.resolve(
          JSON.parse(
            '{"status": 0, "support_updates": false, "hdfs_link": "/filebrowser/view=/user/hive/warehouse/customers", "extended_columns": [{"comment": "", "type": "int", "name": "id"}, {"comment": "", "type": "string", "name": "name"}, {"comment": "", "type": "struct<email_format:string,frequency:string,categories:struct<promos:boolean,surveys:boolean>>", "name": "email_preferences"}, {"comment": "", "type": "map<string,struct<street_1:string,street_2:string,city:string,state:string,zip_code:string>>", "name": "addresses"}, {"comment": "", "type": "array<struct<order_id:string,order_date:string,items:array<struct<product_id:int,sku:string,name:string,price:double,qty:int>>>>", "name": "orders"}], "columns": ["id", "name", "email_preferences", "addresses", "orders"], "partition_keys": []}'
          )
        );
      }
      if (options.entry.path.length === 3) {
        return CancellablePromise.resolve(
          JSON.parse(
            '{"status": 0, "comment": "", "type": "struct", "name": "email_preferences", "fields": [{"type": "string", "name": "email_format"}, {"type": "string", "name": "frequency"}, {"fields": [{"type": "boolean", "name": "promos"}, {"type": "boolean", "name": "surveys"}], "type": "struct", "name": "categories"}]}'
          )
        );
      }
      if (options.entry.path.length > 3) {
        return CancellablePromise.resolve(
          JSON.parse(
            '{"status": 0, "fields": [{"type": "boolean", "name": "promos"}, {"type": "boolean", "name": "surveys"}], "type": "struct", "name": "categories"}'
          )
        );
      }
      return CancellablePromise.reject();
    });

  const createSubject = (): AutocompleteResults => {
    const mockEditor = {
      getTextBeforeCursor: () => 'foo',
      getTextAfterCursor: () => 'bar'
    };

    const mockExecutor = {
      connector: () => ({ id: 'hive', dialect: 'hive' }),
      database: () => 'default',
      namespace: () => ({ id: 'defaultNamespace' }),
      compute: () => ({ id: 'defaultCompute' })
    } as Executor;

    return new AutocompleteResults({
      temporaryOnly: false,
      executor: mockExecutor,
      sqlAnalyzerProvider: sqlAnalyzerRepository,
      sqlReferenceProvider: sqlReferenceRepository,
      editor: mockEditor as unknown as Ace.Editor
    });
  };

  const mockSourceMetadata = (columnsByTable: Record<string, { type: string; name: string }[]>) => {
    jest.spyOn(hueConfig, 'getLastKnownConfig').mockImplementation(
      () =>
        ({
          app_config: {
            editor: {
              source_autocomplete_disabled: false
            }
          }
        }) as HueConfig
    );
    sourceMetaSpy.mockImplementation(
      (options: Parameters<typeof CatalogApi.fetchSourceMetadata>[0]) => {
        const path = options.entry.path;
        if (path.length === 0) {
          return CancellablePromise.resolve({ databases: ['default'] });
        }
        if (path.length === 1) {
          return CancellablePromise.resolve({
            tables_meta: Object.keys(columnsByTable).map((tableName, index) => ({
              comment: null,
              index,
              type: 'Table',
              name: tableName
            }))
          });
        }
        if (path.length === 2) {
          const tableName = path[1].toLowerCase();
          const extendedColumns = columnsByTable[tableName] || [];
          return CancellablePromise.resolve({
            extended_columns: extendedColumns.map(column => ({
              type: column.type,
              name: column.name
            })),
            columns: extendedColumns.map(column => column.name),
            partition_keys: []
          });
        }
        if (path.length === 3) {
          const tableName = path[1].toLowerCase();
          const columnName = path[2].toLowerCase();
          const foundColumn = (columnsByTable[tableName] || []).find(
            column => column.name.toLowerCase() === columnName
          );
          if (foundColumn) {
            return CancellablePromise.resolve({
              comment: '',
              type: foundColumn.type,
              name: foundColumn.name
            });
          }
        }
        return CancellablePromise.reject();
      }
    );
  };

  beforeEach(() => {
    huePubSub.publish('assist.clear.all.caches');
    dataCatalog.disableCache();
  });

  afterEach(() => {
    dataCatalog.enableCache();
    jest.resetAllMocks();
  });

  it('should handle parse results with keywords', async () => {
    const subject = createSubject();
    const suggestions: Suggestion[] = [];

    await subject.update(
      {
        lowerCase: true,
        suggestKeywords: [
          { value: 'BAR', weight: 1 },
          { value: 'FOO', weight: 2 }
        ]
      } as AutocompleteParseResult,
      suggestions
    );

    expect(suggestions.length).toBe(2);
    expect(suggestions[0].meta).toBe(I18n('keyword'));
    expect(suggestions[0].value).toBe('bar');
    expect(suggestions[0].weightAdjust).toBe(1);
    expect(suggestions[1].meta).toBe(I18n('keyword'));
    expect(suggestions[1].value).toBe('foo');
    expect(suggestions[1].weightAdjust).toBe(2);
  });

  it('should handle parse results with identifiers', async () => {
    const subject = createSubject();
    const suggestions: Suggestion[] = [];

    await subject.update(
      {
        lowerCase: false,
        suggestIdentifiers: [
          { name: 'foo', type: 'alias' },
          { name: 'bar', type: 'table' }
        ]
      } as AutocompleteParseResult,
      suggestions
    );

    expect(suggestions.length).toBe(2);
    expect(suggestions[1].meta).toBe('table');
    expect(suggestions[1].value).toBe('bar');
    expect(suggestions[0].meta).toBe('alias');
    expect(suggestions[0].value).toBe('foo');
  });

  it('should handle parse results with functions', async () => {
    const spy = jest
      .spyOn(sqlUdfRepository, 'getUdfsWithReturnTypes')
      .mockImplementation(async () =>
        Promise.resolve([
          {
            name: 'count',
            returnTypes: ['BIGINT'],
            arguments: [[{ type: 'T' }]],
            signature: 'count(col)',
            draggable: 'count()',
            description: 'some desc'
          }
        ])
      );
    const subject = createSubject();
    const suggestions: Suggestion[] = [];

    await subject.update(
      {
        lowerCase: false,
        suggestFunctions: {}
      } as AutocompleteParseResult,
      suggestions
    );

    await sleep(0);

    expect(spy).toHaveBeenCalled();

    expect(suggestions.length).toEqual(1);
    const udfDetails = suggestions[0].details as UdfDetails;
    expect(udfDetails.arguments).toBeDefined();
    expect(udfDetails.signature).toBeDefined();
    expect(udfDetails.description).toBeDefined();
  });

  it('should handle parse results with udf argument keywords', async () => {
    const spy = jest
      .spyOn(sqlUdfRepository, 'getArgumentDetailsForUdf')
      .mockImplementation(async () => Promise.resolve([{ type: 'T', keywords: ['a', 'b'] }]));
    const subject = createSubject();
    const suggestions: Suggestion[] = [];

    await subject.update(
      {
        lowerCase: false,
        udfArgument: {
          name: 'someudf',
          position: 1
        }
      } as AutocompleteParseResult,
      suggestions
    );

    await sleep(0);

    expect(spy).toHaveBeenCalled();

    expect(suggestions.length).toEqual(2);
    expect(suggestions[0].value).toEqual('a');
    expect(suggestions[1].value).toEqual('b');
  });

  it('should handle parse results set options', async () => {
    const spy = jest.spyOn(sqlReferenceRepository, 'getSetOptions').mockImplementation(
      async dialect =>
        new Promise(resolve => {
          expect(dialect).toEqual(subject.executor.connector().dialect);
          resolve({
            OPTION_1: {
              description: 'Desc 1',
              type: 'Integer',
              default: 'Some default'
            },
            OPTION_2: {
              description: 'Desc 2',
              type: 'Integer',
              default: 'Some default'
            }
          });
        })
    );
    const subject = createSubject();
    const suggestions: Suggestion[] = [];

    await subject.update(
      {
        lowerCase: false,
        suggestSetOptions: {}
      } as AutocompleteParseResult,
      suggestions
    );

    await sleep(0);

    expect(spy).toHaveBeenCalled();

    expect(suggestions.length).toEqual(2);
    expect((suggestions[0].details as SetDetails).description).toBeDefined();
    expect((suggestions[1].details as SetDetails).type).toBeDefined();
  });

  it('should fetch from source when disable_source_autocomplete is set to false', async () => {
    jest.spyOn(hueConfig, 'getLastKnownConfig').mockImplementation(
      () =>
        ({
          app_config: {
            editor: {
              source_autocomplete_disabled: false
            }
          }
        }) as HueConfig
    );

    const subject = createSubject();
    const suggestions: Suggestion[] = [];

    await subject.update(
      {
        lowerCase: false,
        suggestDatabases: {}
      } as AutocompleteParseResult,
      suggestions
    );

    expect(sourceMetaSpy).toHaveBeenCalled();
  });

  it('should not fetch from source when disable_source_autocomplete is set to true', async () => {
    jest.spyOn(hueConfig, 'getLastKnownConfig').mockImplementation(
      () =>
        ({
          app_config: {
            editor: {
              source_autocomplete_disabled: true
            }
          }
        }) as HueConfig
    );
    const subject = createSubject();
    const suggestions: Suggestion[] = [];

    await subject.update(
      {
        lowerCase: false,
        suggestDatabases: {}
      } as AutocompleteParseResult,
      suggestions
    );

    expect(sourceMetaSpy).not.toHaveBeenCalled();
  });

  it('should suggest columns for CTEs selecting all columns from a source table', async () => {
    mockSourceMetadata({
      foo: [
        { type: 'int', name: 'id' },
        { type: 'string', name: 'name' }
      ]
    });
    const subject = createSubject();
    const suggestions: Suggestion[] = [];

    await subject.update(
      {
        lowerCase: false,
        suggestColumns: {
          source: 'select',
          tables: [{ identifierChain: [{ cte: 't1' }] }]
        },
        commonTableExpressions: [
          {
            alias: 't1',
            columns: [{ tables: [{ identifierChain: [{ name: 'foo' }] }] }]
          }
        ]
      } as AutocompleteParseResult,
      suggestions
    );

    const values = suggestions.map(suggestion => suggestion.value);
    expect(values).toEqual(expect.arrayContaining(['id', 'name']));
  });

  it('should resolve CTEs that select all columns from another CTE', async () => {
    mockSourceMetadata({
      foo: [
        { type: 'int', name: 'id' },
        { type: 'string', name: 'name' }
      ]
    });
    const subject = createSubject();
    const suggestions: Suggestion[] = [];

    await subject.update(
      {
        lowerCase: false,
        suggestColumns: {
          source: 'select',
          tables: [{ identifierChain: [{ cte: 't2' }] }]
        },
        commonTableExpressions: [
          {
            alias: 't1',
            columns: [{ tables: [{ identifierChain: [{ name: 'foo' }] }] }]
          },
          {
            alias: 't2',
            columns: [{ tables: [{ identifierChain: [{ name: 't1' }] }] }]
          }
        ]
      } as AutocompleteParseResult,
      suggestions
    );

    const cteColumnSuggestions = suggestions.filter(suggestion =>
      ['id', 'name'].includes(suggestion.value)
    );
    expect(cteColumnSuggestions.map(suggestion => suggestion.value)).toEqual(
      expect.arrayContaining(['id', 'name'])
    );
    cteColumnSuggestions.forEach(suggestion => {
      expect(suggestion.table?.identifierChain).toEqual([{ cte: 't2' }]);
    });
  });

  it('should not resolve later CTEs from earlier CTE definitions', async () => {
    mockSourceMetadata({
      foo: [
        { type: 'int', name: 'id' },
        { type: 'string', name: 'name' }
      ],
      bar: [{ type: 'boolean', name: 'active' }]
    });
    const subject = createSubject();
    const suggestions: Suggestion[] = [];

    await subject.update(
      {
        lowerCase: false,
        suggestColumns: {
          source: 'select',
          tables: [{ identifierChain: [{ cte: 't1' }] }]
        },
        commonTableExpressions: [
          {
            alias: 't1',
            columns: [{ tables: [{ identifierChain: [{ name: 'foo' }] }] }]
          },
          {
            alias: 'foo',
            columns: [{ tables: [{ identifierChain: [{ name: 'bar' }] }] }]
          }
        ]
      } as AutocompleteParseResult,
      suggestions
    );

    const values = suggestions.map(suggestion => suggestion.value);
    expect(values).toEqual(expect.arrayContaining(['id', 'name']));
    expect(values).not.toEqual(expect.arrayContaining(['active']));
  });

  it('should prefer explicit CTE column aliases over expanded source columns', async () => {
    mockSourceMetadata({
      foo: [
        { type: 'int', name: 'id' },
        { type: 'string', name: 'name' }
      ]
    });
    const subject = createSubject();
    const suggestions: Suggestion[] = [];

    await subject.update(
      {
        lowerCase: false,
        suggestColumns: {
          source: 'select',
          tables: [{ identifierChain: [{ cte: 'renamed_cte' }] }]
        },
        commonTableExpressions: [
          {
            alias: 'renamed_cte',
            columnAliases: ['cte_id', 'cte_name'],
            columns: [{ tables: [{ identifierChain: [{ name: 'foo' }] }] }]
          }
        ]
      } as AutocompleteParseResult,
      suggestions
    );

    const values = suggestions.map(suggestion => suggestion.value);
    expect(values).toEqual(expect.arrayContaining(['cte_id', 'cte_name']));
    expect(values).not.toEqual(expect.arrayContaining(['id', 'name']));
  });

  it('should quote explicit CTE column aliases that require quoting', async () => {
    mockSourceMetadata({
      foo: [
        { type: 'int', name: 'id' },
        { type: 'string', name: 'name' }
      ]
    });
    const subject = createSubject();
    const suggestions: Suggestion[] = [];

    await subject.update(
      {
        lowerCase: false,
        suggestColumns: {
          source: 'select',
          tables: [{ identifierChain: [{ cte: 'renamed_cte' }] }]
        },
        commonTableExpressions: [
          {
            alias: 'renamed_cte',
            columnAliases: ['select', 'order-id'],
            columns: [{ tables: [{ identifierChain: [{ name: 'foo' }] }] }]
          }
        ]
      } as AutocompleteParseResult,
      suggestions
    );

    const values = suggestions.map(suggestion => suggestion.value);
    expect(values).toEqual(expect.arrayContaining(['`select`', '`order-id`']));
    expect(values).not.toEqual(expect.arrayContaining(['select', 'order-id', 'id', 'name']));
  });

  it('should suggest columns for CTEs backed only by explicit column aliases', async () => {
    const subject = createSubject();
    const suggestions: Suggestion[] = [];

    await subject.update(
      {
        lowerCase: false,
        suggestColumns: {
          source: 'select',
          tables: [{ identifierChain: [{ cte: 'values_cte' }] }]
        },
        commonTableExpressions: [
          {
            alias: 'values_cte',
            columnAliases: ['cte_id', 'cte_name']
          }
        ]
      } as AutocompleteParseResult,
      suggestions
    );

    const values = suggestions.map(suggestion => suggestion.value);
    expect(values).toEqual(expect.arrayContaining(['cte_id', 'cte_name']));
    const sourceTableColumnFetches = sourceMetaSpy.mock.calls.filter(
      ([options]) => options.entry.path.length > 1
    );
    expect(sourceTableColumnFetches).toHaveLength(0);
  });

  it('should apply type filtering to explicit CTE column aliases backed by source columns', async () => {
    mockSourceMetadata({
      foo: [
        { type: 'int', name: 'id' },
        { type: 'boolean', name: 'active' }
      ]
    });
    const subject = createSubject();
    const suggestions: Suggestion[] = [];

    await subject.update(
      {
        lowerCase: false,
        suggestColumns: {
          source: 'select',
          types: ['BOOLEAN'],
          tables: [{ identifierChain: [{ cte: 'renamed_cte' }] }]
        },
        commonTableExpressions: [
          {
            alias: 'renamed_cte',
            columnAliases: ['cte_id', 'cte_active'],
            columns: [{ tables: [{ identifierChain: [{ name: 'foo' }] }] }]
          }
        ]
      } as AutocompleteParseResult,
      suggestions
    );

    const values = suggestions.map(suggestion => suggestion.value);
    expect(values).toEqual(expect.arrayContaining(['cte_active']));
    expect(values).not.toEqual(expect.arrayContaining(['cte_id', 'id', 'active']));
  });

  it('should apply type filtering to physical table column suggestions', async () => {
    mockSourceMetadata({
      foo: [
        { type: 'int', name: 'id' },
        { type: 'boolean', name: 'active' }
      ]
    });
    const subject = createSubject();
    const suggestions: Suggestion[] = [];

    await subject.update(
      {
        lowerCase: false,
        suggestColumns: {
          source: 'select',
          types: ['BOOLEAN'],
          tables: [{ identifierChain: [{ name: 'foo' }] }]
        }
      } as AutocompleteParseResult,
      suggestions
    );

    const values = suggestions.map(suggestion => suggestion.value);
    expect(values).toEqual(expect.arrayContaining(['active']));
    expect(values).not.toEqual(expect.arrayContaining(['id']));
  });
});

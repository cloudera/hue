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

import ApiHelper from 'api/apiHelper';
import * as CatalogApi from 'catalog/api';
import * as apiUtils from 'sql/reference/apiUtils';
import { CancellablePromise } from 'api/cancellablePromise';
import AutocompleteResults from './autocompleteResults';
import dataCatalog from 'catalog/dataCatalog';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';
import LOTS_OF_PARSE_RESULTS from './test/lotsOfParseResults';
import * as sqlUdfRepository from 'sql/reference/sqlUdfRepository';
import sqlReferenceRepository from 'sql/reference/sqlReferenceRepository';
import sleep from 'utils/timing/sleep';
import * as hueConfig from 'config/hueConfig';

describe('AutocompleteResults.js', () => {
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

  const createSubject = () =>
    new AutocompleteResults({
      snippet: {
        autocompleteSettings: {
          temporaryOnly: false
        },
        type: () => 'hive',
        connector: () => ({ id: 'hive', dialect: 'hive' }),
        database: () => 'default',
        namespace: () => ({ id: 'defaultNamespace' }),
        compute: () => ({ id: 'defaultCompute' }),
        whenContextSet: () => Promise.resolve()
      },
      editor: () => ({
        getTextBeforeCursor: () => 'foo',
        getTextAfterCursor: () => 'bar'
      })
    });

  const mockSourceMetadata = columnsByTable => {
    sourceMetaSpy.mockImplementation(options => {
      const path = options.entry.path;
      if (path.length === 0) {
        return CancellablePromise.resolve({ status: 0, databases: ['default'] });
      }
      if (path.length === 1) {
        return CancellablePromise.resolve({
          status: 0,
          tables_meta: Object.keys(columnsByTable).map(tableName => ({
            type: 'Table',
            name: tableName
          }))
        });
      }
      if (path.length === 2) {
        const tableName = path[1].toLowerCase();
        const extendedColumns = columnsByTable[tableName] || [];
        return CancellablePromise.resolve({
          status: 0,
          extended_columns: extendedColumns.map(column => ({
            comment: '',
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
        const foundColumn = (columnsByTable[tableName] || []).find(column =>
          column.name.toLowerCase() === columnName
        );
        if (foundColumn) {
          return CancellablePromise.resolve({
            status: 0,
            comment: '',
            type: foundColumn.type,
            name: foundColumn.name
          });
        }
      }
      return CancellablePromise.reject();
    });
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

    expect(subject.filtered().length).toBe(0);

    await subject.update({
      lowerCase: true,
      suggestKeywords: [
        { value: 'BAR', weight: 1 },
        { value: 'FOO', weight: 2 }
      ]
    });

    expect(subject.filtered().length).toBe(2);
    // Sorted by weight, case adjusted
    expect(subject.filtered()[0].meta).toBe(I18n('keyword'));
    expect(subject.filtered()[0].value).toBe('foo');
    expect(subject.filtered()[1].meta).toBe(I18n('keyword'));
    expect(subject.filtered()[1].value).toBe('bar');
  });

  it('should handle parse results with identifiers', async () => {
    const subject = createSubject();

    expect(subject.filtered().length).toBe(0);
    await subject.update({
      lowerCase: false,
      suggestIdentifiers: [
        { name: 'foo', type: 'alias' },
        { name: 'bar', type: 'table' }
      ]
    });

    expect(subject.filtered().length).toBe(2);
    // Sorted by name, no case adjust
    expect(subject.filtered()[0].meta).toBe('table');
    expect(subject.filtered()[0].value).toBe('bar');
    expect(subject.filtered()[1].meta).toBe('alias');
    expect(subject.filtered()[1].value).toBe('foo');
  });

  it('should handle parse results with functions', async () => {
    const subject = createSubject();

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

    expect(subject.filtered().length).toBe(0);

    await subject.update({
      lowerCase: false,
      suggestFunctions: {}
    });

    await sleep(0);

    expect(spy).toHaveBeenCalled();

    expect(subject.filtered().length).toEqual(1);
    expect(subject.filtered()[0].details.arguments).toBeDefined();
    expect(subject.filtered()[0].details.signature).toBeDefined();
    expect(subject.filtered()[0].details.description).toBeDefined();
  });

  it('should handle parse results with udf argument keywords', async () => {
    const subject = createSubject();

    const spy = jest
      .spyOn(sqlUdfRepository, 'getArgumentDetailsForUdf')
      .mockImplementation(async () => Promise.resolve([{ type: 'T', keywords: ['a', 'b'] }]));

    expect(subject.filtered().length).toBe(0);

    await subject.update({
      lowerCase: false,
      udfArgument: {
        name: 'someudf',
        position: 1
      }
    });

    await sleep(0);

    expect(spy).toHaveBeenCalled();

    expect(subject.filtered().length).toEqual(2);
    expect(subject.filtered()[0].value).toEqual('a');
    expect(subject.filtered()[1].value).toEqual('b');
  });

  it('should handle parse results set options', async () => {
    const subject = createSubject();

    const spy = jest.spyOn(sqlReferenceRepository, 'getSetOptions').mockImplementation(
      async dialect =>
        new Promise(resolve => {
          expect(dialect).toEqual(subject.snippet.connector().dialect);
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

    expect(subject.filtered().length).toBe(0);

    await subject.update({
      lowerCase: false,
      suggestSetOptions: {}
    });

    await sleep(0);

    expect(spy).toHaveBeenCalled();

    expect(subject.filtered().length).toEqual(2);
    expect(subject.filtered()[0].details.description).toBeDefined();
    expect(subject.filtered()[1].details.type).toBeDefined();
  });

  it('should fetch from source when disable_source_autocomplete is set to false', async () => {
    jest.spyOn(hueConfig, 'getLastKnownConfig').mockImplementation(() => ({
      app_config: {
        editor: {
          source_autocomplete_disabled: false
        }
      }
    }));

    const subject = createSubject();

    await subject.update({
      lowerCase: false,
      suggestDatabases: {}
    });

    expect(sourceMetaSpy).toHaveBeenCalled();
  });

  it('should not fetch from source when disable_source_autocomplete is set to true', async () => {
    jest.spyOn(hueConfig, 'getLastKnownConfig').mockImplementation(() => ({
      app_config: {
        editor: {
          source_autocomplete_disabled: true
        }
      }
    }));
    const subject = createSubject();

    await subject.update({
      lowerCase: false,
      suggestDatabases: {}
    });

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

    await subject.update({
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
    });

    const values = subject.filtered().map(suggestion => suggestion.value);
    expect(values).toEqual(expect.arrayContaining(['id', 'name']));
  });

  it('should suggest columns for CTEs selecting all columns from joined source tables', async () => {
    mockSourceMetadata({
      foo: [
        { type: 'int', name: 'id' },
        { type: 'string', name: 'foo_name' }
      ],
      bar: [
        { type: 'int', name: 'id' },
        { type: 'string', name: 'bar_name' }
      ]
    });

    const subject = createSubject();

    await subject.update({
      lowerCase: false,
      suggestColumns: {
        source: 'select',
        tables: [{ identifierChain: [{ cte: 'joined_cte' }] }]
      },
      commonTableExpressions: [
        {
          alias: 'joined_cte',
          columns: [
            {
              tables: [
                { identifierChain: [{ name: 'foo' }] },
                { identifierChain: [{ name: 'bar' }] }
              ]
            }
          ]
        }
      ]
    });

    const values = subject.filtered().map(suggestion => suggestion.value);
    expect(values).toEqual(expect.arrayContaining(['id', 'foo_name', 'bar_name']));
    expect(values).not.toEqual(expect.arrayContaining(['foo.id', 'bar.id']));
  });

  it('should resolve CTEs that select all columns from another CTE', async () => {
    mockSourceMetadata({
      foo: [
        { type: 'int', name: 'id' },
        { type: 'string', name: 'name' }
      ]
    });

    const subject = createSubject();

    await subject.update({
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
    });

    const cteColumnSuggestions = subject
      .filtered()
      .filter(suggestion => ['id', 'name'].includes(suggestion.value));

    expect(cteColumnSuggestions.map(suggestion => suggestion.value)).toEqual(
      expect.arrayContaining(['id', 'name'])
    );
    cteColumnSuggestions.forEach(suggestion => {
      expect(suggestion.table.identifierChain).toEqual([{ cte: 't2' }]);
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

    await subject.update({
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
    });

    const values = subject.filtered().map(suggestion => suggestion.value);
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

    await subject.update({
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
    });

    const values = subject.filtered().map(suggestion => suggestion.value);
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

    await subject.update({
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
    });

    const values = subject.filtered().map(suggestion => suggestion.value);
    expect(values).toEqual(expect.arrayContaining(['`select`', '`order-id`']));
    expect(values).not.toEqual(expect.arrayContaining(['select', 'order-id', 'id', 'name']));
  });

  it('should suggest columns for CTEs backed only by explicit column aliases', async () => {
    const subject = createSubject();

    await subject.update({
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
    });

    const values = subject.filtered().map(suggestion => suggestion.value);
    expect(values).toEqual(expect.arrayContaining(['cte_id', 'cte_name']));
    const sourceTableColumnFetches = sourceMetaSpy.mock.calls.filter(
      ([options]) => options.entry.path.length > 1
    );
    expect(sourceTableColumnFetches).toHaveLength(0);
  });

  it('should not fetch source metadata for untyped explicit CTE column aliases', async () => {
    mockSourceMetadata({
      foo: [
        { type: 'int', name: 'id' },
        { type: 'string', name: 'name' }
      ]
    });

    const subject = createSubject();

    await subject.update({
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
    });

    const values = subject.filtered().map(suggestion => suggestion.value);
    expect(values).toEqual(expect.arrayContaining(['cte_id', 'cte_name']));
    const sourceTableColumnFetches = sourceMetaSpy.mock.calls.filter(
      ([options]) => options.entry.path.length === 2 && options.entry.path[1] === 'foo'
    );
    expect(sourceTableColumnFetches).toHaveLength(0);
  });

  it('should not fetch source metadata for untyped CTE column references', async () => {
    mockSourceMetadata({
      foo: [
        { type: 'int', name: 'id' },
        { type: 'boolean', name: 'active' }
      ]
    });

    const subject = createSubject();

    await subject.update({
      lowerCase: false,
      suggestColumns: {
        source: 'select',
        tables: [{ identifierChain: [{ cte: 't1' }] }]
      },
      commonTableExpressions: [
        {
          alias: 't1',
          columns: [
            { identifierChain: [{ name: 'foo' }, { name: 'id' }], type: 'COLREF' },
            { identifierChain: [{ name: 'foo' }, { name: 'active' }], type: 'COLREF' }
          ]
        }
      ]
    });

    const values = subject.filtered().map(suggestion => suggestion.value);
    expect(values).toEqual(expect.arrayContaining(['id', 'active']));
    const sourceTableColumnFetches = sourceMetaSpy.mock.calls.filter(
      ([options]) =>
        options.entry.path.length >= 2 &&
        options.entry.path[1] === 'foo' &&
        ['foo', 'id', 'active'].includes(options.entry.path[options.entry.path.length - 1])
    );
    expect(sourceTableColumnFetches).toHaveLength(0);
  });

  it('should suggest columns for qualified CTE references emitted as table names', async () => {
    mockSourceMetadata({
      foo: [
        { type: 'int', name: 'id' },
        { type: 'string', name: 'name' }
      ]
    });

    const subject = createSubject();

    await subject.update({
      lowerCase: false,
      suggestColumns: {
        source: 'select',
        tables: [{ identifierChain: [{ name: 't1' }] }]
      },
      commonTableExpressions: [
        {
          alias: 't1',
          columns: [{ tables: [{ identifierChain: [{ name: 'foo' }] }] }]
        }
      ]
    });

    const cteColumnSuggestions = subject
      .filtered()
      .filter(suggestion => ['id', 'name'].includes(suggestion.value));

    expect(cteColumnSuggestions.map(suggestion => suggestion.value)).toEqual(
      expect.arrayContaining(['id', 'name'])
    );
    cteColumnSuggestions.forEach(suggestion => {
      expect(suggestion.table.identifierChain).toEqual([{ cte: 't1' }]);
    });
  });

  it('should apply type filtering to explicit CTE column aliases backed by source columns', async () => {
    mockSourceMetadata({
      foo: [
        { type: 'int', name: 'id' },
        { type: 'boolean', name: 'active' }
      ]
    });

    const subject = createSubject();

    await subject.update({
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
    });

    const values = subject.filtered().map(suggestion => suggestion.value);
    expect(values).toEqual(expect.arrayContaining(['cte_active']));
    expect(values).not.toEqual(expect.arrayContaining(['cte_id', 'id', 'active']));
  });

  it('should apply type filtering to explicit CTE column aliases backed by column references', async () => {
    mockSourceMetadata({
      foo: [
        { type: 'int', name: 'id' },
        { type: 'boolean', name: 'active' }
      ]
    });

    const subject = createSubject();

    await subject.update({
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
          columns: [
            { identifierChain: [{ name: 'foo' }, { name: 'id' }], type: 'COLREF' },
            { identifierChain: [{ name: 'foo' }, { name: 'active' }], type: 'COLREF' }
          ]
        }
      ]
    });

    const values = subject.filtered().map(suggestion => suggestion.value);
    expect(values).toEqual(expect.arrayContaining(['cte_active']));
    expect(values).not.toEqual(expect.arrayContaining(['cte_id']));
  });

  it('should apply type filtering to CTE column suggestions', async () => {
    mockSourceMetadata({
      foo: [
        { type: 'int', name: 'id' },
        { type: 'string', name: 'name' },
        { type: 'boolean', name: 'active' },
        { type: 'double', name: 'score' }
      ]
    });

    const subject = createSubject();

    await subject.update({
      lowerCase: false,
      suggestColumns: {
        source: 'select',
        types: ['BOOLEAN'],
        tables: [{ identifierChain: [{ cte: 'typed_cte' }] }]
      },
      commonTableExpressions: [
        {
          alias: 'typed_cte',
          columns: [
            { alias: 'display_active', type: 'BOOLEAN' },
            { alias: 'customer_id', type: 'INT' },
            { tables: [{ identifierChain: [{ name: 'foo' }] }] }
          ]
        }
      ]
    });

    const values = subject.filtered().map(suggestion => suggestion.value);
    expect(values).toEqual(expect.arrayContaining(['display_active', 'active']));
    expect(values).not.toEqual(expect.arrayContaining(['customer_id', 'id', 'name', 'score']));
  });

  it('should apply type filtering to physical table column suggestions', async () => {
    mockSourceMetadata({
      foo: [
        { type: 'int', name: 'id' },
        { type: 'boolean', name: 'active' }
      ]
    });

    const subject = createSubject();

    await subject.update({
      lowerCase: false,
      suggestColumns: {
        source: 'select',
        types: ['BOOLEAN'],
        tables: [{ identifierChain: [{ name: 'foo' }] }]
      }
    });

    const values = subject.filtered().map(suggestion => suggestion.value);
    expect(values).toEqual(expect.arrayContaining(['active']));
    expect(values).not.toEqual(expect.arrayContaining(['id']));
  });

  describe('Test a whole lot of different parse results', () => {
    const LOADING_OBSERVABLES = [
      'loadingKeywords',
      'loadingFunctions',
      'loadingDatabases',
      'loadingTables',
      'loadingColumns',
      'loadingValues',
      'loadingPaths',
      'loadingJoins',
      'loadingJoinConditions',
      'loadingAggregateFunctions',
      'loadingGroupBys',
      'loadingOrderBys',
      'loadingFilters',
      'loadingPopularTables',
      'loadingPopularColumns'
    ];

    for (const parseResult of LOTS_OF_PARSE_RESULTS) {
      it('should handle parse result no. ' + parseResult.index, async () => {
        jest.spyOn(apiUtils, 'fetchUdfs').mockImplementation(() => Promise.resolve([]));
        jest.spyOn(ApiHelper, 'fetchHdfsPath').mockImplementation(options => {
          const deferred = $.Deferred();

          deferred.done(options.successCallback);

          deferred.resolve({
            superuser: 'hdfs',
            current_request_path: '/filebrowser/view=///var',
            current_dir_path: '///var',
            show_download_button: true,
            cwd_set: true,
            breadcrumbs: [
              {
                url: '/',
                label: '/'
              },
              {
                url: '/var',
                label: 'var'
              }
            ],
            apps: [
              'help',
              'sqoop',
              'pig',
              'hbase',
              'rdbms',
              'indexer',
              'metastore',
              'beeswax',
              'jobsub',
              'metadata',
              'zookeeper',
              'search',
              'useradmin',
              'notebook',
              'proxy',
              'oozie',
              'spark',
              'filebrowser',
              'about',
              'jobbrowser',
              'dashboard',
              'security',
              'impala'
            ],
            show_upload_button: true,
            files: [
              {
                humansize: '0\u00a0bytes',
                url: '/filebrowser/view=/',
                stats: {
                  size: 0,
                  group: 'supergroup',
                  blockSize: 0,
                  replication: 0,
                  user: 'hdfs',
                  mtime: 1476970119,
                  path: '///var/..',
                  atime: 0,
                  mode: 16877
                },
                name: '..',
                mtime: 'October 20, 2016 06:28 AM',
                rwx: 'drwxr-xr-x',
                path: '/',
                is_sentry_managed: false,
                type: 'dir',
                mode: '40755'
              },
              {
                humansize: '0\u00a0bytes',
                url: '/filebrowser/view=/var',
                stats: {
                  size: 0,
                  group: 'supergroup',
                  blockSize: 0,
                  replication: 0,
                  user: 'hdfs',
                  mtime: 1470887321,
                  path: '///var',
                  atime: 0,
                  mode: 16877
                },
                name: '.',
                mtime: 'August 10, 2016 08:48 PM',
                rwx: 'drwxr-xr-x',
                path: '/var',
                is_sentry_managed: false,
                type: 'dir',
                mode: '40755'
              },
              {
                humansize: '0\u00a0bytes',
                url: '/filebrowser/view=/var/lib',
                stats: {
                  size: 0,
                  group: 'supergroup',
                  blockSize: 0,
                  replication: 0,
                  user: 'hdfs',
                  mtime: 1470887321,
                  path: '/var/lib',
                  atime: 0,
                  mode: 16877
                },
                name: 'lib',
                mtime: 'August 10, 2016 08:48 PM',
                rwx: 'drwxr-xr-x',
                path: '/var/lib',
                is_sentry_managed: false,
                type: 'dir',
                mode: '40755'
              },
              {
                humansize: '0\u00a0bytes',
                url: '/filebrowser/view=/var/log',
                stats: {
                  size: 0,
                  group: 'mapred',
                  blockSize: 0,
                  replication: 0,
                  user: 'yarn',
                  mtime: 1470887196,
                  path: '/var/log',
                  atime: 0,
                  mode: 17405
                },
                name: 'log',
                mtime: 'August 10, 2016 08:46 PM',
                rwx: 'drwxrwxr-xt',
                path: '/var/log',
                is_sentry_managed: false,
                type: 'dir',
                mode: '41775'
              }
            ],
            users: [],
            is_embeddable: false,
            supergroup: 'supergroup',
            descending: 'false',
            groups: [],
            is_trash_enabled: true,
            pagesize: 50,
            file_filter: 'any',
            is_fs_superuser: false,
            is_sentry_managed: false,
            home_directory: '/user/admin',
            path: '///var',
            page: {
              num_pages: 1,
              total_count: 2,
              next_page_number: 1,
              end_index: 2,
              number: 1,
              previous_page_number: 1,
              start_index: 1
            }
          });

          return deferred.promise();
        });

        const subject = createSubject();
        if (parseResult.suggestKeywords) {
          const cleanedKeywords = [];
          parseResult.suggestKeywords.forEach(keyword => {
            if (!keyword.value) {
              cleanedKeywords.push({ value: keyword });
            } else {
              cleanedKeywords.push(keyword);
            }
          });
          parseResult.suggestKeywords = cleanedKeywords;
        }
        try {
          await subject.update(parseResult);
        } catch (e) {
          fail('Got exception');
          console.error(e);
        }
        if (subject.loading()) {
          LOADING_OBSERVABLES.forEach(observable => {
            if (subject[observable]()) {
              fail('Still loading (' + observable + '() == true), missing ajax spec?');
            }
          });
        }

        expect(subject.loading()).toBeFalsy();
      });
    }
  });
});

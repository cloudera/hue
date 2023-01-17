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

import { merge } from 'lodash';

import { default as MetastoreTable, DIALECT_HIVE, DIALECT_SPARK } from './metastoreTable';

describe('metastoreTable.js', () => {
  const generateOptions = customOptions => {
    const defaultOptions = {
      catalogEntry: {
        hasResolvedComment: () => false,
        isModel: () => false,
        isTransactionalTable: () => false,
        isView: () => false,
        getDialect: () => DIALECT_HIVE,
        getAnalysis: () =>
          Promise.resolve({
            details: {
              stats: {}
            },
            partition_keys: []
          }),
        getComment: () => Promise.resolve(''),
        getConnector: () => ({
          buttonName: '',
          displayName: '',
          id: 'connectorA',
          page: '',
          tooltip: '',
          type: ''
        }),
        getSample: () =>
          Promise.resolve({
            data: [],
            meta: []
          }),
        getTopJoins: () => Promise.resolve({})
      },
      database: {
        catalogEntry: {
          loadNavigatorMetaForChildren: () => Promise.resolve({})
        }
      },
      navigatorEnabled: false,
      sqlAnalyzerEnabled: false
    };

    return merge({}, defaultOptions, customOptions);
  };

  it('should enable import when analysis is loaded', async () => {
    const metastoreTable = new MetastoreTable(generateOptions({}));
    await metastoreTable.fetchDetails();
    expect(metastoreTable.enableImport()).toEqual(true);
  });

  it('should not enable import before there is an analysis loaded', async () => {
    const resolve = () => ({
      details: {
        stats: {}
      },
      partition_keys: []
    });
    const unresolvedPromise = new Promise(resolve, () => {});
    const metastoreTable = new MetastoreTable(
      generateOptions({ catalogEntry: { getAnalysis: () => unresolvedPromise } })
    );

    await metastoreTable.fetchDetails();
    expect(metastoreTable.enableImport()).toEqual(false);
  });

  it('should not enable import when the table is a view', async () => {
    const metastoreTable = new MetastoreTable(
      generateOptions({ catalogEntry: { isView: () => true } })
    );
    await metastoreTable.fetchDetails();
    expect(metastoreTable.enableImport()).toEqual(false);
  });

  it('should not enable import when the table is transactional and dialect is Hive', async () => {
    const metastoreTransactionalHiveTable = new MetastoreTable(
      generateOptions({ catalogEntry: { isTransactionalTable: () => true } })
    );
    await metastoreTransactionalHiveTable.fetchDetails();
    expect(metastoreTransactionalHiveTable.enableImport()).toEqual(false);

    const metastoreTransactionalTable = new MetastoreTable(
      generateOptions({
        catalogEntry: { isTransactionalTable: () => true, getDialect: () => 'sql' }
      })
    );
    await metastoreTransactionalTable.fetchDetails();
    expect(metastoreTransactionalTable.enableImport()).toEqual(true);

    const metastoreHiveTable = new MetastoreTable(generateOptions());
    await metastoreHiveTable.fetchDetails();
    expect(metastoreHiveTable.enableImport()).toEqual(true);
  });

  it('should not enable import when the dialect is sparksql', async () => {
    const metastoreTable = new MetastoreTable(
      generateOptions({ catalogEntry: { getDialect: () => DIALECT_SPARK } })
    );
    await metastoreTable.fetchDetails();
    expect(metastoreTable.enableImport()).toEqual(false);
  });
});

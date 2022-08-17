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

import { CancellablePromise } from 'api/cancellablePromise';
import dataCatalog from 'catalog/dataCatalog';
import DataCatalogEntry, { Sample, TableAnalysis } from 'catalog/DataCatalogEntry';
import { Compute, Connector, Namespace } from 'config/types';
import * as CatalogApi from './api';

const connectorOne: Connector = {
  buttonName: '',
  displayName: '',
  id: 'connectorA',
  page: '',
  tooltip: '',
  type: ''
};

const connectorTwo: Connector = {
  buttonName: '',
  displayName: '',
  id: 'connectorB',
  page: '',
  tooltip: '',
  type: ''
};

const compute: Compute = { id: 'computeId', name: '', type: '' };

const namespaceOne: Namespace = { computes: [compute], id: 'namespaceOne', name: '', status: '' };

const getEntry = (path: string | string[], connector?: Connector, namespace?: Namespace) =>
  dataCatalog.getEntry({
    connector: connector || connectorOne,
    compute,
    path: path,
    namespace: namespace || namespaceOne
  });

const clearStorage = async (): Promise<void> => {
  await dataCatalog.getCatalog(connectorOne).clearStorageCascade();
  await dataCatalog.getCatalog(connectorTwo).clearStorageCascade();
};

describe('dataCatalogEntry.ts', () => {
  beforeEach(clearStorage);

  afterAll(clearStorage);

  describe('getAnalysis', () => {
    const getAnalysisObj = () => ({
      message: '',
      name: 'iceberg-table-test',
      partition_keys: [],
      cols: [{ name: 'i', type: 'int', comment: '' }],
      path_location: 'test',
      hdfs_link: '/filebrowser/view=/warehouse/tablespace/managed/hive/sample_07',
      is_view: false,
      properties: [],
      details: {
        stats: {
          table_type: 'ICEBERG'
        },
        properties: {}
      },
      stats: [],
      primary_keys: []
    });

    const emptyAnalysisApiSpy = (additionalAnalysis: Record<string, unknown> = {}) => {
      const customAnalysis = merge({}, getAnalysisObj(), additionalAnalysis);
      jest
        .spyOn(CatalogApi, 'fetchDescribe')
        .mockReturnValue(CancellablePromise.resolve<TableAnalysis>(customAnalysis));
    };

    it('should return true for isIcebergTable after the analysis has has been loaded', async () => {
      emptyAnalysisApiSpy();
      const entry = await getEntry('someDb.someIcebergTable');

      expect(entry.isIcebergTable()).toBeFalsy();

      await entry.getAnalysis();
      expect(entry.isIcebergTable()).toBeTruthy();
    });

    it('returns true for isTransactionalTable when details.stats.transactional="true"', async () => {
      emptyAnalysisApiSpy({ details: { stats: { transactional: 'true' } } });
      const entry = await getEntry('someDb.someTransactionalTable');

      expect(entry.isTransactionalTable()).toBeFalsy();

      await entry.getAnalysis();
      expect(entry.isTransactionalTable()).toBeTruthy();
    });

    it('returns false for isTransactionalTable when there is no details.stats.transactional defined', async () => {
      emptyAnalysisApiSpy();
      const entry = await getEntry('someDb.someTransactionalTable');

      expect(entry.isTransactionalTable()).toBeFalsy();

      await entry.getAnalysis();
      expect(entry.isTransactionalTable()).toBeFalsy();
    });

    it('should return the hdfs path based on the hdfs_link', async () => {
      emptyAnalysisApiSpy();
      const entry = await getEntry('someDb.someTable');
      await entry.getAnalysis();
      expect(entry.getHdfsFilePath()).toEqual('/warehouse/tablespace/managed/hive/sample_07');
    });

    it('rejects a cachedOnly request if there is no previous promise', async () => {
      emptyAnalysisApiSpy();
      const entryA = await getEntry('someDb.someTable');
      let rejected = false;
      await entryA.getAnalysis({ cachedOnly: true }).catch(() => {
        rejected = true;
      });

      expect(rejected).toBeTruthy();
    });

    it('should return the same analysis promise for the same entry', async () => {
      emptyAnalysisApiSpy();
      const entryA = await getEntry('someDb.someTable');
      const entryB = await getEntry('someDb.someTable');
      expect(entryA.getAnalysis()).toEqual(entryB.getAnalysis());
    });

    it('should not return the same analysis promise for different entries', async () => {
      emptyAnalysisApiSpy();
      const entryA = await getEntry('someDb.someTableOne');
      const entryB = await getEntry('someDb.someTableTwo');
      expect(entryA.getAnalysis()).not.toEqual(entryB.getAnalysis());
    });

    it('should keep the analysis promise for future session use', async () => {
      emptyAnalysisApiSpy();
      const entryA = await getEntry('someDb.someTable');
      await entryA.clearCache();
      const analysisPromise = entryA.getAnalysis();
      expect(entryA.analysisPromise).toEqual(analysisPromise);
      const entryB = await getEntry('someDb.someTable');
      expect(entryB.analysisPromise).toEqual(analysisPromise);
    });

    it('should not cancel when cancellable option is not set to true', async () => {
      emptyAnalysisApiSpy();
      const entryA = await getEntry('someDb.someTable');
      const analysisPromise = entryA.getAnalysis({ cancellable: false });
      await analysisPromise.cancel();
      expect(analysisPromise.cancelled).toBeFalsy();
      expect(entryA.analysisPromise).toEqual(analysisPromise);
    });

    it('should not return a cancelled analysis promise', async () => {
      emptyAnalysisApiSpy();
      const entryA = await getEntry('someDb.someTable');
      const cancelledPromise = entryA.getAnalysis({ cancellable: true });
      await cancelledPromise.cancel();
      const newPromise = entryA.getAnalysis();
      expect(cancelledPromise.cancelled).toBeTruthy();
      expect(newPromise).not.toEqual(cancelledPromise);
    });
  });

  describe('getSample', () => {
    const emptySampleApiSpy = () => {
      jest.spyOn(CatalogApi, 'fetchSample').mockReturnValue(
        CancellablePromise.resolve<Sample>({
          data: [],
          meta: [],
          type: ''
        })
      );
    };

    it('should return the same sample promise for the same entry', async () => {
      emptySampleApiSpy();
      const entryA = await getEntry('someDb.someTable');
      const entryB = await getEntry('someDb.someTable');
      expect(entryA.getSample()).toEqual(entryB.getSample());
    });

    it('should not return the same sample promise for different entries', async () => {
      emptySampleApiSpy();
      const entryA = await getEntry('someDb.someTableOne');
      const entryB = await getEntry('someDb.someTableTwo');
      expect(entryA.getSample()).not.toEqual(entryB.getSample());
    });

    it('should not return the same sample promise if the operation is different', async () => {
      emptySampleApiSpy();
      const entryA = await getEntry('someDb.someTable');
      const entryB = await getEntry('someDb.someTable');
      expect(entryA.getSample({ operation: 'distinct' })).not.toEqual(entryB.getSample());
    });

    it('should keep the sample promise for future session use', async () => {
      emptySampleApiSpy();
      const entryA = await getEntry('someDb.someTable');
      await entryA.clearCache();
      const samplePromise = entryA.getSample();
      expect(entryA.samplePromise).toEqual(samplePromise);
      const entryB = await getEntry('someDb.someTable');
      expect(entryB.samplePromise).toEqual(samplePromise);
    });

    it('should not keep the sample promise if the operation is non-default', async () => {
      emptySampleApiSpy();
      const entryA = await getEntry('someDb.someTable');
      entryA.getSample({ operation: 'distinct' });
      expect(entryA.samplePromise).toBeUndefined();
    });

    it('should bubble up exceptions', async () => {
      jest.spyOn(CatalogApi, 'fetchSample').mockReturnValue(CancellablePromise.reject('failed!'));
      const entryA = await getEntry('someDb.someTable');
      let caught = false;
      try {
        await entryA.getSample();
      } catch (err) {
        expect(err).toEqual('failed!');
        caught = true;
      }
      expect(caught).toBeTruthy();
    });

    it('should not cancel when cancellable option is not set to true', async () => {
      emptySampleApiSpy();
      const entryA = await getEntry('someDb.someTable');
      const samplePromise = entryA.getSample({ cancellable: false });
      await samplePromise.cancel();
      expect(samplePromise.cancelled).toBeFalsy();
      expect(entryA.samplePromise).toEqual(samplePromise);
    });

    it('should not return a cancelled sample promise', async () => {
      emptySampleApiSpy();
      const entryA = await getEntry('someDb.someTable');
      const cancelledPromise = entryA.getSample({ cancellable: true });
      await cancelledPromise.cancel();
      const newPromise = entryA.getSample();
      expect(cancelledPromise.cancelled).toBeTruthy();
      expect(newPromise).not.toEqual(cancelledPromise);
    });

    it('should check the parent table samples for a column and re-use if set', async () => {
      const tableEntry = await getEntry('someDb.someTable');
      const tableSample: Sample = {
        data: [
          [1, 2],
          [3, 4]
        ],
        meta: [
          { name: 'someOtherCol', type: 'int' },
          { name: 'someCol', type: 'int' }
        ],
        type: 'table'
      };
      tableEntry.samplePromise = CancellablePromise.resolve<Sample>(tableSample);
      const colEntry = await getEntry('someDb.someTable.someCol');
      const colSample = await colEntry.getSample();
      expect(colSample.data[0][0]).toEqual(2);
      expect(colSample.data[1][0]).toEqual(4);
    });

    it('should check the parent table samples for a column and if not set reload the sample', async () => {
      let fetchCalledOnEntry: DataCatalogEntry | undefined;
      jest.spyOn(CatalogApi, 'fetchSample').mockImplementation(options => {
        fetchCalledOnEntry = options.entry;
        return CancellablePromise.resolve<Sample>({
          data: [],
          meta: [],
          type: ''
        });
      });
      const entryA = await getEntry('someDb.someTable.someCol');
      await entryA.getSample();
      expect(fetchCalledOnEntry).toBeDefined();
      expect(entryA).toEqual(fetchCalledOnEntry);
    });
  });
});

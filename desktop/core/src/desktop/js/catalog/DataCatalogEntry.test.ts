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
import DataCatalogEntry, {
  FieldSourceMeta,
  NavigatorMeta,
  Sample,
  TableAnalysis,
  TableSourceMeta
} from 'catalog/DataCatalogEntry';
import { Compute, Connector, Namespace } from 'config/types';
import * as CatalogApi from './api';
import { hueWindow } from '../types/types';

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

describe('DataCatalogEntry.ts', () => {
  beforeEach(() => {
    clearStorage();
    jest.clearAllMocks();
  });

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

  describe('getComment', () => {
    /* To better understand these test it helps to know that for a column the
       comment can come from multiple sources:
    
       1. If Hue is configured to use a service such as Navigator or Atlas it
          will use the comment from such a service for Hive and Impala (or
          fallback to below).
       3. When the table metadata is present it will use that data if it
          contains a defined comment for that column (from the extended_columns
          attribute in the table metadata).
       2. When a column is created directly with the complete path used in
          dataCatalog.getEntry() and not via tableEntry.getChildren() and
          there is no parent table metadata or if column comment is undefined
          in the table metadata we'll fall back to fetching the source
          metadata for the column (describe on the individual column).
    */

    it('should use the comment from Navigator/Atlas when defined', async () => {
      const initialCatalogFlag = (<hueWindow>window).HAS_CATALOG;
      (<hueWindow>window).HAS_CATALOG = true;
      const mockNavData = { name: 'colA', description: 'foo' } as NavigatorMeta;
      const navSpy = jest
        .spyOn(CatalogApi, 'fetchNavigatorMetadata')
        .mockReturnValue(CancellablePromise.resolve<NavigatorMeta>(mockNavData));
      const columnEntry = await getEntry('someDb.someTable.colA', {
        id: 'hive',
        dialect: 'hive'
      } as Connector);

      const comment = await columnEntry.getComment();

      expect(navSpy).toHaveBeenCalled();
      expect(comment).toEqual(mockNavData.description);
      (<hueWindow>window).HAS_CATALOG = initialCatalogFlag;
    });

    it('should only fetch source metadata for an individual column when the comment is undefined in the table metadata', async () => {
      const sourceMetaSpy = jest
        .spyOn(CatalogApi, 'fetchSourceMetadata')
        .mockImplementation(({ entry }) => {
          if (entry.isTable()) {
            return CancellablePromise.resolve<TableSourceMeta>({
              columns: ['colA'],
              extended_columns: [{ name: 'colA', type: 'int' }] // Comment undefined in table meta
            });
          }
          if (entry.isColumn()) {
            return CancellablePromise.resolve<FieldSourceMeta>({
              name: 'colA',
              comment: 'banana', // Comment is defined in column meta
              type: 'int'
            });
          }
          return CancellablePromise.reject();
        });
      const tableEntry = await getEntry('someDb.someTable');
      const columns = await tableEntry.getChildren();
      expect(columns.length).toEqual(1);
      const columnEntry = columns[0];

      expect(columnEntry.hasResolvedComment()).toBeFalsy();
      const comment = await columnEntry.getComment();

      expect(comment).toEqual('banana');
      expect(sourceMetaSpy).toHaveBeenCalledTimes(2);
    });

    it('should not fetch source metadata for an individual column when the comment is an empty string in the table metadata', async () => {
      const sourceMetaSpy = jest
        .spyOn(CatalogApi, 'fetchSourceMetadata')
        .mockImplementation(({ entry }) => {
          if (entry.isTable()) {
            return CancellablePromise.resolve<TableSourceMeta>({
              columns: ['colA'],
              extended_columns: [{ name: 'colA', type: 'int', comment: '' }] // Empty column comment in table meta
            });
          }
          return CancellablePromise.reject();
        });
      const tableEntry = await getEntry('someDb.someTable');
      const columns = await tableEntry.getChildren();
      expect(sourceMetaSpy).toHaveBeenCalledTimes(1);
      expect(columns.length).toEqual(1);
      const columnEntry = columns[0];

      expect(columnEntry.hasResolvedComment()).toBeTruthy();
      const comment = await columnEntry.getComment();

      expect(comment).toEqual('');
      expect(sourceMetaSpy).toHaveBeenCalledTimes(1);
    });

    it('should fetch column source metadata for the comment when there is no table metadata', async () => {
      const sourceMetaSpy = jest
        .spyOn(CatalogApi, 'fetchSourceMetadata')
        .mockImplementation(({ entry }) => {
          if (entry.isColumn()) {
            return CancellablePromise.resolve<FieldSourceMeta>({
              name: 'colA',
              comment: 'banana', // Comment is defined in column meta
              type: 'int'
            });
          }
          return CancellablePromise.reject();
        });
      const columnEntry = await getEntry('someDb.someTable.someColumn');

      expect(columnEntry.hasResolvedComment()).toBeFalsy();
      const comment = await columnEntry.getComment();

      expect(comment).toEqual('banana');
      expect(sourceMetaSpy).toHaveBeenCalled();
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

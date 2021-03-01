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

import { Compute, Connector, Namespace } from 'config/types';
import dataCatalog from './dataCatalog';

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
const namespaceTwo: Namespace = { computes: [compute], id: 'namespaceTwo', name: '', status: '' };

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

describe('dataCatalog.ts', () => {
  beforeEach(clearStorage);

  afterAll(clearStorage);

  describe('getEntry', () => {
    it('Should always return the same entry for the same path, connector and namespace', async () => {
      const promiseA = getEntry('someDb.someTable');
      const promiseB = getEntry('someDb.someTable');
      const [entryA, entryB] = await Promise.all([promiseA, promiseB]);
      expect(entryA).toBeDefined();
      expect(entryB).toBeDefined();
      expect(entryA).toEqual(entryB);
    });

    it('Should not return the same entry for the same path with different connectors', async () => {
      const promiseA = getEntry('someDb.someTable', connectorOne);
      const promiseB = getEntry('someDb.someTable', connectorTwo);
      const [entryA, entryB] = await Promise.all([promiseA, promiseB]);
      expect(entryA).toBeDefined();
      expect(entryB).toBeDefined();
      expect(entryA).not.toEqual(entryB);
    });

    it('Should not return the same entry for the same path with different namespaces', async () => {
      const promiseA = getEntry('someDb.someTable', connectorOne, namespaceOne);
      const promiseB = getEntry('someDb.someTable', connectorOne, namespaceTwo);
      const [entryA, entryB] = await Promise.all([promiseA, promiseB]);
      expect(entryA).toBeDefined();
      expect(entryB).toBeDefined();
      expect(entryA).not.toEqual(entryB);
    });
  });

  describe('getChildren', () => {
    it('should handle getChildren of non-existing path with cachedOnly set to true', async () => {
      let caught = false;
      try {
        const childPromise = dataCatalog.getChildren({
          connector: connectorOne,
          namespace: namespaceOne,
          compute: compute,
          path: 'bad.path',
          cachedOnly: true
        });

        await childPromise;
      } catch (err) {
        caught = true;
      }

      expect(caught).toBeTruthy();
    });
  });
});

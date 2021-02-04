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

import Connector from '../types/config';
import SqlAnalyzer from './SqlAnalyzer';

const connectorA: Connector = {
  buttonName: '',
  displayName: '',
  id: 'connectorA',
  page: '',
  tooltip: '',
  type: ''
};

describe('SqlAnalyzer.ts', () => {
  describe('checkMissingLimit', () => {
    it('Should detect a missing LIMIT', async () => {
      const isMissingLimit = await new SqlAnalyzer(connectorA).checkMissingLimit(
        'SELECT * FROM employee',
        'hive'
      );

      expect(isMissingLimit).toBeTruthy();
    });

    it('Should avoid warning from a missing LIMIT in SELECT without a table', async () => {
      const isMissingLimit = await new SqlAnalyzer(connectorA).checkMissingLimit(
        'SELECT 1',
        'hive'
      );

      expect(isMissingLimit).toBeFalsy();
    });

    it('Should not warning from a missing LIMIT in CREATE', async () => {
      const isMissingLimit = await new SqlAnalyzer(connectorA).checkMissingLimit(
        'CREATE TABLE a (a int)',
        'hive'
      );

      expect(isMissingLimit).toBeFalsy();
    });
  });

  describe('checkSelectStar', () => {
    it('Should detect a SELECT *', async () => {
      const isSelectStar = await new SqlAnalyzer(connectorA).checkSelectStar(
        'SELECT * FROM employee',
        'hive'
      );

      expect(isSelectStar).toBeTruthy();
    });
    it('Should not warning from a non SELECT *', async () => {
      const isSelectStar = await new SqlAnalyzer(connectorA).checkSelectStar(
        'SELECT name FROM employee',
        'hive'
      );

      expect(isSelectStar).toBeFalsy();
    });
  });
});

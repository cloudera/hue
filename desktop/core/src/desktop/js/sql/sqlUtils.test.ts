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

import type { Connector } from 'config/types';
import type { SqlReferenceProvider } from './reference/types';
import sqlUtils from './sqlUtils';

describe('sqlUtils.ts', () => {
  describe('backTickIfNeeded', () => {
    const trinoConnector = { dialect: 'trino', dialect_properties: {} } as unknown as Connector;
    const sqlReferenceProvider = {
      getReservedKeywords: jest.fn().mockResolvedValue(new Set(['SELECT', 'TABLE']))
    } as unknown as SqlReferenceProvider;

    const quote = (identifier: string, forceAppendBacktick?: boolean) =>
      sqlUtils.backTickIfNeeded(
        trinoConnector,
        identifier,
        sqlReferenceProvider,
        forceAppendBacktick
      );

    it('should use double quotes for Trino when no identifier quote is configured', async () => {
      expect(await quote('my-table')).toEqual('"my-table"');
    });

    it('should quote each part of a catalog.schema identifier', async () => {
      expect(await quote('hive.default')).toEqual('"hive"."default"');
    });

    it('should not quote an identifier that is already quoted', async () => {
      expect(await quote('"hive"')).toEqual('"hive"');
      expect(await quote('"hive"."default"')).toEqual('"hive"."default"');
    });

    it('should quote reserved keywords and identifiers that start with a digit', async () => {
      expect(await quote('table')).toEqual('"table"');
      expect(await quote('1table')).toEqual('"1table"');
    });

    it('should not quote a plain identifier', async () => {
      expect(await quote('orders')).toEqual('orders');
    });

    it('should only append the closing quote when forced', async () => {
      expect(await quote('hive', true)).toEqual('hive"');
    });
  });
});

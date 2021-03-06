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

import { UdfArgument } from 'sql/reference/types';
import { Connector } from 'config/types';
import { getArgumentDetailsForUdf } from './sqlUdfRepository';
import sqlReferenceRepository from './sqlReferenceRepository';
import * as apiUtils from 'sql/reference/apiUtils';

describe('sqlUdfRepository.ts', () => {
  const createTestConnector = (dialect: string, id: string): Connector => ({
    dialect: dialect,
    id: id,
    buttonName: '',
    displayName: '',
    page: '',
    tooltip: '',
    type: ''
  });

  const hiveConn: Connector = createTestConnector('hive', 'hive');
  const impalaConn = createTestConnector('impala', 'impala');

  jest.mock('sql/reference/impala/udfReference', () => ({
    UDF_CATEGORIES: [
      {
        functions: {
          cos: {
            returnTypes: ['DOUBLE'],
            arguments: [[{ type: 'DOUBLE' }]],
            signature: 'cos(DOUBLE a)',
            draggable: 'cos()',
            description: ''
          },
          concat: {
            returnTypes: ['STRING'],
            arguments: [[{ type: 'STRING' }], [{ type: 'STRING', multiple: true }]],
            signature: 'concat(STRING a, STRING b...)',
            draggable: 'concat()',
            description: ''
          },
          strleft: {
            returnTypes: ['STRING'],
            arguments: [[{ type: 'STRING' }], [{ type: 'INT' }]],
            signature: 'strleft(STRING a, INT num_chars)',
            draggable: 'strleft()',
            description: ''
          }
        }
      }
    ]
  }));

  jest.mock('sql/reference/hive/udfReference', () => ({
    UDF_CATEGORIES: [
      {
        functions: {
          cos: {
            returnTypes: ['DOUBLE'],
            arguments: [[{ type: 'DECIMAL' }, { type: 'DOUBLE' }]],
            signature: 'cos(DECIMAL|DOUBLE a)',
            draggable: 'cos()',
            description: ''
          },
          concat: {
            returnTypes: ['STRING'],
            arguments: [
              [
                { type: 'STRING', multiple: true },
                { type: 'BINARY', multiple: true }
              ]
            ],
            signature: 'concat(STRING|BINARY a, STRING|BINARY b...)',
            draggable: 'concat()',
            description: ''
          },
          reflect: {
            returnTypes: ['T'],
            arguments: [
              [{ type: 'STRING' }],
              [{ type: 'STRING' }],
              [{ type: 'T', multiple: true, optional: true }]
            ],
            signature: 'reflect(class, method[, arg1[, arg2..]])',
            draggable: 'reflect()',
            description: ''
          }
        }
      }
    ]
  }));

  jest.spyOn(apiUtils, 'fetchUdfs').mockImplementation(() => Promise.resolve([]));

  const extractType = (details: UdfArgument): string => details.type;

  it('should give the expected argument types at a specific position', async () => {
    expect(
      (await getArgumentDetailsForUdf(sqlReferenceRepository, hiveConn, 'cos', 1)).map(extractType)
    ).toEqual(['DECIMAL', 'DOUBLE']);
    expect(
      (await getArgumentDetailsForUdf(sqlReferenceRepository, hiveConn, 'cos', 2)).map(extractType)
    ).toEqual([]);
    expect(
      (await getArgumentDetailsForUdf(sqlReferenceRepository, impalaConn, 'cos', 1)).map(
        extractType
      )
    ).toEqual(['DOUBLE']);
    expect(
      (await getArgumentDetailsForUdf(sqlReferenceRepository, impalaConn, 'cos', 2)).map(
        extractType
      )
    ).toEqual([]);

    expect(
      (await getArgumentDetailsForUdf(sqlReferenceRepository, hiveConn, 'concat', 10)).map(
        extractType
      )
    ).toEqual(['STRING', 'BINARY']);
    expect(
      (await getArgumentDetailsForUdf(sqlReferenceRepository, impalaConn, 'concat', 10)).map(
        extractType
      )
    ).toEqual(['STRING']);
  });

  it('should handle functions with different type of arguments', async () => {
    expect(
      (await getArgumentDetailsForUdf(sqlReferenceRepository, hiveConn, 'reflect', 1)).map(
        extractType
      )
    ).toEqual(['STRING']);
    expect(
      (await getArgumentDetailsForUdf(sqlReferenceRepository, hiveConn, 'reflect', 2)).map(
        extractType
      )
    ).toEqual(['STRING']);
    expect(
      (await getArgumentDetailsForUdf(sqlReferenceRepository, hiveConn, 'reflect', 3)).map(
        extractType
      )
    ).toEqual(['T']);
    expect(
      (await getArgumentDetailsForUdf(sqlReferenceRepository, hiveConn, 'reflect', 200)).map(
        extractType
      )
    ).toEqual(['T']);
  });

  it('should handle functions with an infinite amount of arguments', async () => {
    expect(
      (await getArgumentDetailsForUdf(sqlReferenceRepository, impalaConn, 'greatest', 1)).map(
        extractType
      )
    ).toEqual(['T']);
    expect(
      (await getArgumentDetailsForUdf(sqlReferenceRepository, impalaConn, 'greatest', 200)).map(
        extractType
      )
    ).toEqual(['T']);

    expect(
      (await getArgumentDetailsForUdf(sqlReferenceRepository, hiveConn, 'strleft', 1)).map(
        extractType
      )
    ).toEqual(['T']);
    expect(
      (await getArgumentDetailsForUdf(sqlReferenceRepository, hiveConn, 'strleft', 2)).map(
        extractType
      )
    ).toEqual(['T']);
    expect(
      (await getArgumentDetailsForUdf(sqlReferenceRepository, hiveConn, 'strleft', 3)).map(
        extractType
      )
    ).toEqual(['T']);
    expect(
      (await getArgumentDetailsForUdf(sqlReferenceRepository, hiveConn, 'strleft', 200)).map(
        extractType
      )
    ).toEqual(['T']);
  });

  it('should not return types for arguments out of bounds', async () => {
    expect(
      (await getArgumentDetailsForUdf(sqlReferenceRepository, impalaConn, 'strleft', 1)).map(
        extractType
      )
    ).toEqual(['STRING']);
    expect(
      (await getArgumentDetailsForUdf(sqlReferenceRepository, impalaConn, 'strleft', 2)).map(
        extractType
      )
    ).toEqual(['INT']);
    expect(
      (await getArgumentDetailsForUdf(sqlReferenceRepository, impalaConn, 'strleft', 3)).map(
        extractType
      )
    ).toEqual([]);
    expect(
      (await getArgumentDetailsForUdf(sqlReferenceRepository, impalaConn, 'strleft', 200)).map(
        extractType
      )
    ).toEqual([]);
  });

  it("should return T for any argument if the udf isn't found", async () => {
    expect(
      (await getArgumentDetailsForUdf(sqlReferenceRepository, hiveConn, 'blabla', 2)).map(
        extractType
      )
    ).toEqual(['T']);
    expect(
      (await getArgumentDetailsForUdf(sqlReferenceRepository, hiveConn, 'blabla', 200)).map(
        extractType
      )
    ).toEqual(['T']);
    expect(
      (await getArgumentDetailsForUdf(sqlReferenceRepository, impalaConn, 'blabla', 2)).map(
        extractType
      )
    ).toEqual(['T']);
    expect(
      (await getArgumentDetailsForUdf(sqlReferenceRepository, impalaConn, 'blabla', 200)).map(
        extractType
      )
    ).toEqual(['T']);
  });
});

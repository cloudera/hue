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

import { getArgumentTypesForUdf } from './sqlReferenceRepository';
import * as apiUtils from 'sql/reference/apiUtils';

describe('sqlReferenceRepository.js', () => {
  const hiveConn = { dialect: 'hive', id: 'hive' };
  const impalaConn = { dialect: 'impala', id: 'impala' };

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
            arguments: [[{ type: 'STRING', multiple: true }, { type: 'BINARY', multiple: true }]],
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

  it('should give the expected argument types at a specific position', async () => {
    expect(await getArgumentTypesForUdf(hiveConn, 'cos', 1)).toEqual(['DECIMAL', 'DOUBLE']);
    expect(await getArgumentTypesForUdf(hiveConn, 'cos', 2)).toEqual([]);
    expect(await getArgumentTypesForUdf(impalaConn, 'cos', 1)).toEqual(['DOUBLE']);
    expect(await getArgumentTypesForUdf(impalaConn, 'cos', 2)).toEqual([]);

    expect(await getArgumentTypesForUdf(hiveConn, 'concat', 10)).toEqual(['BINARY', 'STRING']);
    expect(await getArgumentTypesForUdf(impalaConn, 'concat', 10)).toEqual(['STRING']);
  });

  it('should handle functions with different type of arguments', async () => {
    expect(await getArgumentTypesForUdf(hiveConn, 'reflect', 1)).toEqual(['STRING']);
    expect(await getArgumentTypesForUdf(hiveConn, 'reflect', 2)).toEqual(['STRING']);
    expect(await getArgumentTypesForUdf(hiveConn, 'reflect', 3)).toEqual(['T']);
    expect(await getArgumentTypesForUdf(hiveConn, 'reflect', 200)).toEqual(['T']);
  });

  it('should handle functions with an infinite amount of arguments', async () => {
    expect(await getArgumentTypesForUdf(impalaConn, 'greatest', 1)).toEqual(['T']);
    expect(await getArgumentTypesForUdf(impalaConn, 'greatest', 200)).toEqual(['T']);

    expect(await getArgumentTypesForUdf(hiveConn, 'strleft', 1)).toEqual(['T']);
    expect(await getArgumentTypesForUdf(hiveConn, 'strleft', 2)).toEqual(['T']);
    expect(await getArgumentTypesForUdf(hiveConn, 'strleft', 3)).toEqual(['T']);
    expect(await getArgumentTypesForUdf(hiveConn, 'strleft', 200)).toEqual(['T']);
  });

  it('should not return types for arguments out of bounds', async () => {
    expect(await getArgumentTypesForUdf(impalaConn, 'strleft', 1)).toEqual(['STRING']);
    expect(await getArgumentTypesForUdf(impalaConn, 'strleft', 2)).toEqual(['INT']);
    expect(await getArgumentTypesForUdf(impalaConn, 'strleft', 3)).toEqual([]);
    expect(await getArgumentTypesForUdf(impalaConn, 'strleft', 200)).toEqual([]);
  });

  it("should return T for any argument if the udf isn't found", async () => {
    expect(await getArgumentTypesForUdf(hiveConn, 'blabla', 2)).toEqual(['T']);
    expect(await getArgumentTypesForUdf(hiveConn, 'blabla', 200)).toEqual(['T']);
    expect(await getArgumentTypesForUdf(impalaConn, 'blabla', 2)).toEqual(['T']);
    expect(await getArgumentTypesForUdf(impalaConn, 'blabla', 200)).toEqual(['T']);
  });
});

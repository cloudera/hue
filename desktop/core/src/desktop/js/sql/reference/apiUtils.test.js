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

import { adaptApiFunctions, extractArgumentTypes, mergeArgumentTypes } from './apiUtils';

describe('apiUtils.js', () => {
  it('should return the default signature when not defined', () => {
    const result = extractArgumentTypes({});
    expect(JSON.stringify(result)).toEqual(JSON.stringify([[{ type: 'T', multiple: true }]]));
  });

  it('should extract empty argument types from empty signature', () => {
    const result = extractArgumentTypes({ signature: '()' });
    expect(result.length).toEqual(0);
  });

  it('should extract single argument type from signature', () => {
    const result = extractArgumentTypes({ signature: '(INT)' });
    expect(JSON.stringify(result)).toEqual(JSON.stringify([[{ type: 'INT' }]]));
  });

  it('should extract multiple argument types from signature', () => {
    const result = extractArgumentTypes({ signature: '(INT, BIGINT, TINYINT)' });
    expect(JSON.stringify(result)).toEqual(
      JSON.stringify([[{ type: 'INT' }], [{ type: 'BIGINT' }], [{ type: 'TINYINT' }]])
    );
  });

  it('should ignore precision in the signature', () => {
    const result = extractArgumentTypes({ signature: '(DECIMAL(*,*))' });
    expect(JSON.stringify(result)).toEqual(JSON.stringify([[{ type: 'DECIMAL' }]]));
  });

  it('should support repetitive argument types from signature', () => {
    const result = extractArgumentTypes({ signature: '(INT, BIGINT...)' });
    expect(JSON.stringify(result)).toEqual(
      JSON.stringify([[{ type: 'INT' }], [{ type: 'BIGINT', multiple: true }]])
    );
  });

  it('should support repetitive argument types with precision from signature', () => {
    const result = extractArgumentTypes({ signature: '(INT, CHAR(*)...)' });
    expect(JSON.stringify(result)).toEqual(
      JSON.stringify([[{ type: 'INT' }], [{ type: 'CHAR', multiple: true }]])
    );
  });

  it('should merge types', () => {
    const target = [[{ type: 'INT' }]];
    const additional = [[{ type: 'DOUBLE' }]];

    mergeArgumentTypes(target, additional);

    expect(JSON.stringify(target)).toEqual(JSON.stringify([[{ type: 'INT' }, { type: 'DOUBLE' }]]));
  });

  it('should add arguments where missing', () => {
    const apiFunctions = [
      {
        name: 'cos'
      },
      {
        name: 'sin'
      }
    ];

    const result = adaptApiFunctions(apiFunctions);

    expect(result.length).toEqual(2);
    expect(result[0].arguments.length).toEqual(1);
    expect(result[0].arguments[0].length).toEqual(1);
    expect(result[0].arguments[0][0].type).toEqual('T');
    expect(result[1].arguments.length).toEqual(1);
    expect(result[1].arguments[0].length).toEqual(1);
    expect(result[1].arguments[0][0].type).toEqual('T');
  });

  it('should add returnTypes where missing', () => {
    const apiFunctions = [
      {
        name: 'cos'
      },
      {
        name: 'sin'
      }
    ];

    const result = adaptApiFunctions(apiFunctions);

    expect(result.length).toEqual(2);
    expect(result[0].returnTypes.length).toEqual(1);
    expect(result[0].returnTypes[0]).toEqual('T');
    expect(result[1].returnTypes.length).toEqual(1);
    expect(result[1].returnTypes[0]).toEqual('T');
  });

  it('should merge same udf with multiple argument types', () => {
    const apiFunctions = [
      {
        is_builtin: 'BUILTIN',
        is_persistent: 'true',
        name: 'casttochar',
        return_type: 'CHAR(*)',
        signature: '(CHAR(*))'
      },
      {
        is_builtin: 'BUILTIN',
        is_persistent: 'true',
        name: 'casttochar',
        return_type: 'CHAR(*)',
        signature: '(INT)'
      }
    ];

    const result = adaptApiFunctions(apiFunctions);

    expect(result.length).toEqual(1);
    expect(result[0].arguments.length).toEqual(1);
    expect(result[0].arguments[0].length).toEqual(2);
    expect(result[0].arguments[0][0].type).toEqual('CHAR');
    expect(result[0].arguments[0][1].type).toEqual('INT');
  });

  it('should merge same udf with multiple return types', () => {
    const apiFunctions = [
      {
        is_builtin: 'BUILTIN',
        is_persistent: 'true',
        name: 'casttochar',
        return_type: 'CHAR(*)',
        signature: '(CHAR(*))'
      },
      {
        is_builtin: 'BUILTIN',
        is_persistent: 'true',
        name: 'casttochar',
        return_type: 'VARCHAR(*)',
        signature: '(INT)'
      }
    ];

    const result = adaptApiFunctions(apiFunctions);

    expect(result.length).toEqual(1);
    expect(result[0].returnTypes.length).toEqual(2);
    expect(result[0].returnTypes[0]).toEqual('CHAR');
    expect(result[0].returnTypes[1]).toEqual('VARCHAR');
  });
});

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

import { matchesType } from './typeUtils';

describe('typeUtils.ts', () => {
  it('should matchTypes for NUMBER', () => {
    expect(matchesType('hive', ['NUMBER'], ['INT'])).toBeTruthy();
    expect(matchesType('hive', ['NUMBER'], ['BIGINT'])).toBeTruthy();
    expect(matchesType('hive', ['NUMBER'], ['DOUBLE'])).toBeTruthy();
    expect(matchesType('hive', ['NUMBER'], ['DECIMAL'])).toBeTruthy();
    expect(matchesType('hive', ['NUMBER'], ['T'])).toBeTruthy();
    expect(matchesType('hive', ['NUMBER'], ['STRING'])).toBeTruthy();
    expect(matchesType('hive', ['INT'], ['NUMBER'])).toBeTruthy();
    expect(matchesType('hive', ['BIGINT'], ['NUMBER'])).toBeTruthy();
    expect(matchesType('hive', ['DOUBLE'], ['NUMBER'])).toBeTruthy();
    expect(matchesType('hive', ['DECIMAL'], ['NUMBER'])).toBeTruthy();

    expect(matchesType('hive', ['STRING'], ['NUMBER'])).toBeTruthy();
    expect(matchesType('hive', ['T'], ['NUMBER'])).toBeTruthy();
    expect(matchesType('hive', ['NUMBER'], ['BOOLEAN'])).toBeFalsy();
    expect(matchesType('hive', ['BOOLEAN'], ['NUMBER'])).toBeFalsy();
  });

  it('should strip precision', () => {
    expect(matchesType('hive', ['STRING'], ['VARCHAR(10)'])).toBeTruthy();
    expect(matchesType('hive', ['NUMBER'], ['DECIMAL(10,1)'])).toBeTruthy();
    expect(matchesType('hive', ['T'], ['CHAR(1)'])).toBeTruthy();
  });

  it('should matchTypes for BIGINT', () => {
    expect(matchesType('hive', ['BIGINT'], ['BIGINT'])).toBeTruthy();
    expect(matchesType('hive', ['BIGINT'], ['INT'])).toBeTruthy();
    expect(matchesType('hive', ['BIGINT'], ['SMALLINT'])).toBeTruthy();
    expect(matchesType('hive', ['BIGINT'], ['TINYINT'])).toBeTruthy();
    expect(matchesType('hive', ['BIGINT'], ['T'])).toBeTruthy();
    expect(matchesType('hive', ['BIGINT'], ['BOOLEAN'])).toBeFalsy();
    expect(matchesType('hive', ['BIGINT'], ['STRING'])).toBeFalsy();
    expect(matchesType('hive', ['INT'], ['BIGINT'])).toBeFalsy();
    expect(matchesType('hive', ['SMALLINT'], ['BIGINT'])).toBeFalsy();
    expect(matchesType('hive', ['TINYINT'], ['BIGINT'])).toBeFalsy();
    expect(matchesType('hive', ['DECIMAL'], ['BIGINT'])).toBeTruthy();
    expect(matchesType('hive', ['T'], ['BIGINT'])).toBeTruthy();
    expect(matchesType('hive', ['BOOLEAN'], ['BIGINT'])).toBeFalsy();
    expect(matchesType('hive', ['STRING'], ['BIGINT'])).toBeTruthy();
  });
});

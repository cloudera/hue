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

import { TypeConversion } from 'sql/reference/types';
import { TYPE_CONVERSION as GENERIC_TYPE_CONVERSION } from './generic/typeConversion';
import { TYPE_CONVERSION as HIVE_TYPE_CONVERSION } from './hive/typeConversion';
import { TYPE_CONVERSION as IMPALA_TYPE_CONVERSION } from './impala/typeConversion';
import { TYPE_CONVERSION as SPARKSQL_TYPE_CONVERSION } from './sparksql/typeConversion';

const stripPrecision = (types: string[]): string[] => {
  const result: string[] = [];
  types.forEach(type => {
    if (type.indexOf('(') > -1) {
      result.push(type.substring(0, type.indexOf('(')));
    } else {
      result.push(type);
    }
  });
  return result;
};

const getTypeConversion = (dialect: string): TypeConversion => {
  switch (dialect) {
    case 'hive':
      return HIVE_TYPE_CONVERSION;
    case 'impala':
      return IMPALA_TYPE_CONVERSION;
    case 'sparksql':
      return SPARKSQL_TYPE_CONVERSION;
    default:
      return GENERIC_TYPE_CONVERSION;
  }
};

/**
 * Matches types based on implicit conversion i.e. if you expect a BIGINT then INT is ok but not BOOLEAN etc.
 */
export const matchesType = (
  dialect: string,
  expectedTypes: string[],
  actualRawTypes: string[]
): boolean => {
  if (expectedTypes.length === 1 && expectedTypes[0] === 'T') {
    return true;
  }
  const actualTypes = stripPrecision(actualRawTypes);
  if (
    actualTypes.indexOf('ARRAY') !== -1 ||
    actualTypes.indexOf('MAP') !== -1 ||
    actualTypes.indexOf('STRUCT') !== -1
  ) {
    return true;
  }
  const conversionTable = getTypeConversion(dialect);
  for (let i = 0; i < expectedTypes.length; i++) {
    for (let j = 0; j < actualTypes.length; j++) {
      // To support future unknown types
      if (
        typeof conversionTable[expectedTypes[i]] === 'undefined' ||
        typeof conversionTable[expectedTypes[i]][actualTypes[j]] == 'undefined'
      ) {
        return true;
      }
      if (conversionTable[expectedTypes[i]] && conversionTable[expectedTypes[i]][actualTypes[j]]) {
        return true;
      }
    }
  }
  return false;
};

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

import isComplexDBTypeDefinition from './isComplexDBTypeDefinition';

describe('hue.utils.js', () => {
  describe('isComplexDBTypeDefinition', () => {
    beforeEach(() => {});

    it('returns true for complex DB type definitions', () => {
      expect(isComplexDBTypeDefinition('map<string,array<string>>')).toEqual(true);
      expect(isComplexDBTypeDefinition('MAP<string,array<string>>')).toEqual(true);
      expect(isComplexDBTypeDefinition('array<string>')).toEqual(true);
      expect(isComplexDBTypeDefinition('ARRAY<string>')).toEqual(true);
      expect(isComplexDBTypeDefinition('struct<f1:bigint,f2:bigint>')).toEqual(true);
      expect(isComplexDBTypeDefinition('STRUCT<f1:bigint,f2:bigint>')).toEqual(true);
      expect(
        isComplexDBTypeDefinition('uniontype<int, double, array<string>, struct<a:int,b:string>>')
      ).toEqual(true);
      expect(
        isComplexDBTypeDefinition('UNIONTYPE<int, double, array<string>, struct<a:int,b:string>>')
      ).toEqual(true);
    });

    it('returns false for other strings', () => {
      expect(isComplexDBTypeDefinition('<string,array<string>>')).toEqual(false);
      expect(isComplexDBTypeDefinition('<b>test</b>')).toEqual(false);
      expect(isComplexDBTypeDefinition('<string>')).toEqual(false);
      expect(isComplexDBTypeDefinition('xxx<f1:bigint,f2:bigint>')).toEqual(false);
      expect(isComplexDBTypeDefinition('map')).toEqual(false);
      expect(isComplexDBTypeDefinition('MAP')).toEqual(false);
      expect(isComplexDBTypeDefinition('ARRAY')).toEqual(false);
      expect(isComplexDBTypeDefinition('array')).toEqual(false);
      expect(isComplexDBTypeDefinition('struc')).toEqual(false);
      expect(isComplexDBTypeDefinition('STRUCT')).toEqual(false);
      expect(isComplexDBTypeDefinition('uniontype')).toEqual(false);
      expect(isComplexDBTypeDefinition('UNIONTYPE')).toEqual(false);
    });

    it('returns false for all non string based input', () => {
      expect(isComplexDBTypeDefinition(12)).toEqual(false);
      expect(isComplexDBTypeDefinition(-12)).toEqual(false);
      expect(isComplexDBTypeDefinition({})).toEqual(false);
      expect(isComplexDBTypeDefinition(undefined)).toEqual(false);
      expect(isComplexDBTypeDefinition(new Date())).toEqual(false);
      expect(isComplexDBTypeDefinition(null)).toEqual(false);
      expect(isComplexDBTypeDefinition([])).toEqual(false);
    });
  });
});

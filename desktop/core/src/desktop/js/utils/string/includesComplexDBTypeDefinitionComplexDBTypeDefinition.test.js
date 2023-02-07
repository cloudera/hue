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

import includesComplexDBTypeDefinition from './includesComplexDBTypeDefinition';

describe('hue.utils.js', () => {
  describe('includesComplexDBTypeDefinition', () => {
    beforeEach(() => {});

    it('returns true for strings including complex DB type definitions', () => {
      expect(includesComplexDBTypeDefinition('map<string,array<string>>')).toEqual(true);
      expect(includesComplexDBTypeDefinition('MAP<string,array<string>>')).toEqual(true);
      expect(includesComplexDBTypeDefinition('array<string>')).toEqual(true);
      expect(includesComplexDBTypeDefinition('ARRAY<string>')).toEqual(true);
      expect(includesComplexDBTypeDefinition('struct<f1:bigint,f2:bigint>')).toEqual(true);
      expect(includesComplexDBTypeDefinition('STRUCT<f1:bigint,f2:bigint>')).toEqual(true);
      expect(
        includesComplexDBTypeDefinition(
          'uniontype<int, double, array<string>, struct<a:int,b:string>>'
        )
      ).toEqual(true);
      expect(
        includesComplexDBTypeDefinition(
          'UNIONTYPE<int, double, array<string>, struct<a:int,b:string>>'
        )
      ).toEqual(true);

      expect(includesComplexDBTypeDefinition('"blabla" map<string,array<string>>')).toEqual(true);
      expect(includesComplexDBTypeDefinition('MAP<string,array<string>> "blabla"')).toEqual(true);
      expect(includesComplexDBTypeDefinition('test array<string>')).toEqual(true);
      expect(includesComplexDBTypeDefinition('ARRAY<string> test')).toEqual(true);
      expect(includesComplexDBTypeDefinition('xx struct<f1:bigint,f2:bigint>')).toEqual(true);
      expect(includesComplexDBTypeDefinition('STRUCT<f1:bigint,f2:bigint> x')).toEqual(true);
      expect(
        includesComplexDBTypeDefinition(
          'test uniontype<int, double, array<string>, struct<a:int,b:string>>'
        )
      ).toEqual(true);
      expect(
        includesComplexDBTypeDefinition(
          'UNIONTYPE<int, double, array<string>, struct<a:int,b:string>> test'
        )
      ).toEqual(true);

      expect(includesComplexDBTypeDefinition('<string,array<string>>')).toEqual(true);
    });

    it('returns false for strings not including complex DB type definitions', () => {
      expect(includesComplexDBTypeDefinition('<b>test</b>')).toEqual(false);
      expect(includesComplexDBTypeDefinition('<string>')).toEqual(false);
      expect(includesComplexDBTypeDefinition('xxx<f1:bigint,f2:bigint>')).toEqual(false);
      expect(includesComplexDBTypeDefinition('map')).toEqual(false);
      expect(includesComplexDBTypeDefinition('MAP')).toEqual(false);
      expect(includesComplexDBTypeDefinition('ARRAY')).toEqual(false);
      expect(includesComplexDBTypeDefinition('array')).toEqual(false);
      expect(includesComplexDBTypeDefinition('struc')).toEqual(false);
      expect(includesComplexDBTypeDefinition('STRUCT')).toEqual(false);
      expect(includesComplexDBTypeDefinition('uniontype')).toEqual(false);
      expect(includesComplexDBTypeDefinition('UNIONTYPE')).toEqual(false);
    });

    it('returns false for all non string based input', () => {
      expect(includesComplexDBTypeDefinition(12)).toEqual(false);
      expect(includesComplexDBTypeDefinition(-12)).toEqual(false);
      expect(includesComplexDBTypeDefinition({})).toEqual(false);
      expect(includesComplexDBTypeDefinition(undefined)).toEqual(false);
      expect(includesComplexDBTypeDefinition(new Date())).toEqual(false);
      expect(includesComplexDBTypeDefinition(null)).toEqual(false);
      expect(includesComplexDBTypeDefinition([])).toEqual(false);
    });
  });
});

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
(function () {
  describe('sqlAutocompleter2.js', function () {

    var hiveSubject = new SqlAutocompleter2({
      snippet: {
        type:function () { return 'hive' }
      }
    });

    var impalaSubject = new SqlAutocompleter2({
      snippet: {
        type:function () { return 'impala' }
      }
    });

    it('should backtick reserved keywords', function () {
      expect(hiveSubject.backTickIfNeeded('alter')).toEqual('`alter`');
      expect(hiveSubject.backTickIfNeeded('date')).toEqual('`date`');
      expect(hiveSubject.backTickIfNeeded('lateral')).toEqual('`lateral`');
      expect(hiveSubject.backTickIfNeeded('extended')).toEqual('`extended`');

      expect(impalaSubject.backTickIfNeeded('alter')).toEqual('`alter`');
      expect(impalaSubject.backTickIfNeeded('aggregate')).toEqual('`aggregate`');
      expect(impalaSubject.backTickIfNeeded('asc')).toEqual('`asc`');
      expect(impalaSubject.backTickIfNeeded('desc')).toEqual('`desc`');
    });

    it('should backtick non-reserved keywords that breaks the autocompleter', function () {
      // For now the autocompleter goes bananas on the following non-reserved words
      expect(hiveSubject.backTickIfNeeded('asc')).toEqual('`asc`');
      expect(hiveSubject.backTickIfNeeded('desc')).toEqual('`desc`');
      expect(hiveSubject.backTickIfNeeded('formatted')).toEqual('`formatted`');
      expect(hiveSubject.backTickIfNeeded('index')).toEqual('`index`');
      expect(hiveSubject.backTickIfNeeded('indexes')).toEqual('`indexes`');
      expect(hiveSubject.backTickIfNeeded('limit')).toEqual('`limit`');
      expect(hiveSubject.backTickIfNeeded('schema')).toEqual('`schema`');
      expect(hiveSubject.backTickIfNeeded('show')).toEqual('`show`');
    });
    
    it('should not backtick non-reserved keywords', function () {
      expect(hiveSubject.backTickIfNeeded('transactions')).toEqual('transactions');
      expect(impalaSubject.backTickIfNeeded('role')).toEqual('role');
    });

    it('should backtick identifiers that doesn\'t match the identifier pattern', function () {
      // [A-Za-z][A-Za-z0-9_]*
      expect(hiveSubject.backTickIfNeeded('bla bla')).toEqual('`bla bla`');
      expect(hiveSubject.backTickIfNeeded('1bla')).toEqual('`1bla`');
      expect(hiveSubject.backTickIfNeeded('_asdf')).toEqual('`_asdf`');
      expect(hiveSubject.backTickIfNeeded('*bla*')).toEqual('`*bla*`');
      expect(hiveSubject.backTickIfNeeded('Kåda')).toEqual('`Kåda`');
    });

    it('should not backtick identifiers that matches the identifier pattern', function () {
      // [A-Za-z][A-Za-z0-9_]*
      expect(hiveSubject.backTickIfNeeded('bla_bla')).toEqual('bla_bla');
      expect(hiveSubject.backTickIfNeeded('E1bla')).toEqual('E1bla');
      expect(hiveSubject.backTickIfNeeded('asdf_')).toEqual('asdf_');
      expect(hiveSubject.backTickIfNeeded('Kada')).toEqual('Kada');
    });

    it('should not backtick identifiers that are backticked', function () {
      // [A-Za-z][A-Za-z0-9_]*
      expect(hiveSubject.backTickIfNeeded('`bla bla`')).toEqual('`bla bla`');
    });

  });
})();
// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// 'License'); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an 'AS IS' BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

(function () {
  describe('sqlSyntaxParser.js', function() {

    it('should not find errors for ""', function () {
      var result = sqlSyntaxParser.parseSyntax('', '');
      expect(result).toBeFalsy();
    });

    it('should not find errors for "SEL"', function () {
      var result = sqlSyntaxParser.parseSyntax('SEL', '');
      expect(result).toBeFalsy();
    });

    it('should not find errors for "SELECT"', function () {
      var result = sqlSyntaxParser.parseSyntax('SELECT', '');
      expect(result).toBeFalsy();
    });

    it('should not find errors for "SELECT "', function () {
      var result = sqlSyntaxParser.parseSyntax('SELECT ', '');
      expect(result).toBeFalsy();
    });

    it('should not find errors for "SELECT *"', function () {
      var result = sqlSyntaxParser.parseSyntax('SELECT *', '');
      expect(result).toBeFalsy();
    });

    it('should not find errors for "SELECT * FR"', function () {
      var result = sqlSyntaxParser.parseSyntax('SELECT * FR', '');
      expect(result).toBeFalsy();
    });

    it('should find errors for "SLELECT "', function() {
      var result = sqlSyntaxParser.parseSyntax('SLELECT ', '');
      expect(result).toBeTruthy();
      expect(result.text).toEqual('SLELECT');
      expect(result.expected.length).toBeGreaterThan(0);
    });
  });
})();
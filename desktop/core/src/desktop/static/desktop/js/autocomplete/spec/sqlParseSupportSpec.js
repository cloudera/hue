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
  describe('sqlParseSupport.js', function () {

    var expectDistance = function (strA, strB, distance, ignoreCase) {
      var lr = SqlParseSupport.stringDistance(strA, strB, ignoreCase);
      var rl = SqlParseSupport.stringDistance(strB, strA, ignoreCase);
      expect(lr).toEqual(rl);
      expect(lr).toEqual(distance);
    };

    it('should calculate the distance between "" and "" correctly', function () {
      expectDistance('', '', 0, true);
    });

    it('should calculate the distance between "abc" and "" correctly', function () {
      expectDistance('abc', '', 3, true);
    });

    it('should calculate the distance between "a" and "b" correctly', function () {
      expectDistance('a', 'b', 1, true);
    });

    it('should calculate the distance between "abc" and "abc" correctly', function () {
      expectDistance('abc', 'abc', 0, true);
    });

    it('should calculate the distance between "abcd" and "abc" correctly', function () {
      expectDistance('abcd', 'abc', 1, true);
    });

    it('should calculate the distance between "abd" and "abc" correctly', function () {
      expectDistance('abd', 'abc', 1, true);
    });

    it('should calculate the distance between "ca" and "abc" correctly', function () {
      expectDistance('ca', 'abc', 3, true);
    });

    it('should calculate the distance between "abC" and "abc" whe not ignoring case correctly', function () {
      expectDistance('abC', 'abc', 1, false);
    });

    it('should calculate the distance between "abC" and "abc" when ignoring case correctly', function () {
      expectDistance('abC', 'abc', 0, true);
    });

    it('should calculate the distance between "abe" and "abc" correctly', function () {
      expectDistance('abe', 'abc', 1, true);
    });

    it('should calculate the distance between "ace" and "abc" correctly', function () {
      expectDistance('ace', 'abc', 2, true);
    });

    it('should calculate the distance between "12345" and "23451" correctly', function () {
      expectDistance('12345', '23451', 2, true);
    });

    it('should calculate the distance between "abcde" and "12345" correctly', function () {
      expectDistance('abcde', '12345', 5, true);
    });

    it('should calculate the distance between "12345" and "abcdefgh" correctly', function () {
      expectDistance('12345', 'abcdefgh', 8, true);
    });

    it('should calculate the distance between "abc1def" and "abcdef" correctly', function () {
      expectDistance('abc1def', 'abcdef', 1, true);
    });

    it('should calculate the distance between "bacdef" and "abcdef" correctly', function () {
      expectDistance('bacdef', 'abcdef', 2, true);
    });

    xit ('should be quick', function () {
      var strA = 'abcdefgh012345678ijklmnop012345678';
      var strB = 'ijklmnop012345678abcdefgh012345678';
      var start, end;
      var durations = new Array(10000 - 1000);
      for (var i = 0; i < 10000; i++) {
        if (i > 1000) {
          start = performance.now();
        }
        SqlParseSupport.stringDistance(strA, strB, true);
        if (i > 1000) {
          end = performance.now();
          durations.push(end-start);
        }
      }
      var sum = 0;
      durations.forEach(function (duration) {
        sum += duration;
      });
      console.log('it took ' + sum / durations.length + ' ms on average.');
      // ~ 0.037 ms on average
      expect(true).toBeTruthy();
    })
  });
})();
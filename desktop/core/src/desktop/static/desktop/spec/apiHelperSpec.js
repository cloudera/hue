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
(function() {

  describe('apiHelper.js', function() {
    var subject = ApiHelper.getInstance({
      i18n: {},
      user: 'testUser'
    });

    it('should be singleton', function() {
      var otherHelper = ApiHelper.getInstance();
      expect(subject === otherHelper).toBeTruthy();
    });

    describe('success response that is actually an error', function () {
      it('should not determine that a success response is an error response if status is 0', function () {
        expect(subject.successResponseIsError({ status: 0 })).toBeFalsy();
      });

      it('should determine that a success response is an error response if status is 1', function () {
        expect(subject.successResponseIsError({ status: 1 })).toBeTruthy();
      });

      it('should determine that a success response is an error response if status is -1', function () {
        expect(subject.successResponseIsError({ status: -1 })).toBeTruthy();
      });

      it('should determine that a success response is an error response if status is -3', function () {
        expect(subject.successResponseIsError({ status: -3 })).toBeTruthy();
      });

      it('should determine that a success response is an error response if status is 500', function () {
        expect(subject.successResponseIsError({ status: 500 })).toBeTruthy();
      });

      it('should determine that a success response is an error response if code is 500', function () {
        expect(subject.successResponseIsError({ code: 500 })).toBeTruthy();
      });

      it('should determine that a success response is an error response if code is 503', function () {
        expect(subject.successResponseIsError({ code: 503 })).toBeTruthy();
      });

      it('should determine that a success response is an error response if it contains traceback', function () {
        expect(subject.successResponseIsError({ traceback: {} })).toBeTruthy();
      });
    });
  });
})();
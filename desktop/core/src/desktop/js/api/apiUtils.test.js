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

import { successResponseIsError } from './apiUtils';

describe('apiUtils.js', () => {
  describe('success response that is actually an error', () => {
    it('should not determine that a success response is an error response if status is 0', () => {
      expect(successResponseIsError({ status: 0 })).toBeFalsy();
    });

    it('should determine that a success response is an error response if status is 1', () => {
      expect(successResponseIsError({ status: 1 })).toBeTruthy();
    });

    it('should determine that a success response is an error response if status is -1', () => {
      expect(successResponseIsError({ status: -1 })).toBeTruthy();
    });

    it('should determine that a success response is an error response if status is -3', () => {
      expect(successResponseIsError({ status: -3 })).toBeTruthy();
    });

    it('determine that a success response is an error response if status is 500', () => {
      expect(successResponseIsError({ status: 500 })).toBeTruthy();
    });

    it('should determine that a success response is an error response if code is 500', () => {
      expect(successResponseIsError({ code: 500 })).toBeTruthy();
    });

    it('should determine that a success response is an error response if code is 503', () => {
      expect(successResponseIsError({ code: 503 })).toBeTruthy();
    });

    it('should determine that a success response is an error response if it contains traceback', () => {
      expect(successResponseIsError({ traceback: {} })).toBeTruthy();
    });
  });
});

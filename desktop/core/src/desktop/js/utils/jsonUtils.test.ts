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

import { isJSON } from './jsonUtils';

describe('isJSON function', () => {
  it('should return false if data is null', () => {
    expect(isJSON(null)).toBe(false);
  });

  it('should return false if data is undefined', () => {
    expect(isJSON(undefined)).toBe(false);
  });

  it('should return true if data is a plain object', () => {
    const obj = { key: 'value' };
    expect(isJSON(obj)).toBe(true);
  });

  it('should return false if data is an instance of FormData', () => {
    const formData = new FormData();
    expect(isJSON(formData)).toBe(false);
  });

  it('should return false if data is an instance of Blob', () => {
    const blob = new Blob(['test'], { type: 'text/plain' });
    expect(isJSON(blob)).toBe(false);
  });

  it('should return false if data is an instance of ArrayBuffer', () => {
    const arrayBuffer = new ArrayBuffer(8);
    expect(isJSON(arrayBuffer)).toBe(false);
  });

  it('should return false if data is an array', () => {
    const arr = [1, 2, 3];
    expect(isJSON(arr)).toBe(false);
  });

  it('should return false if data is a number', () => {
    expect(isJSON(123)).toBe(false);
  });

  it('should return false if data is a string', () => {
    expect(isJSON('string')).toBe(false);
  });

  it('should return false if data is a boolean', () => {
    expect(isJSON(true)).toBe(false);
  });
});

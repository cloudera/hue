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
import formatBytes from './formatBytes';

describe('formatBytes function', () => {
  test('returns "Not available" when bytes is -1', () => {
    expect(formatBytes(-1)).toBe('Not available');
  });

  test('returns "0 Byte" when bytes is 0', () => {
    expect(formatBytes(0)).toBe('0 Byte');
  });

  test('returns "17 Byte" when bytes is 17', () => {
    expect(formatBytes(17)).toBe('17 Bytes');
  });

  test('returns "18 Byte" when bytes is 17.98', () => {
    expect(formatBytes(17.98)).toBe('18 Bytes');
  });

  test('correctly formats bytes to KB', () => {
    expect(formatBytes(1024)).toBe('1.00 KB');
    expect(formatBytes(2048)).toBe('2.00 KB');
  });

  test('correctly formats bytes to MB', () => {
    expect(formatBytes(1024 * 1024)).toBe('1.00 MB');
    expect(formatBytes(2 * 1024 * 1024)).toBe('2.00 MB');
  });

  test('correctly formats bytes to GB', () => {
    expect(formatBytes(1024 * 1024 * 1024)).toBe('1.00 GB');
    expect(formatBytes(2 * 1024 * 1024 * 1024)).toBe('2.00 GB');
  });

  test('correctly formats bytes to TB', () => {
    expect(formatBytes(1024 * 1024 * 1024 * 1024)).toBe('1.00 TB');
    expect(formatBytes(2 * 1024 * 1024 * 1024 * 1024)).toBe('2.00 TB');
  });

  test('correctly formats bytes to specified decimal points', () => {
    expect(formatBytes(2000, 3)).toBe('1.953 KB');
    expect(formatBytes(20000, 1)).toBe('19.5 KB');
  });

  test('correctly formats bytes to default 2 decimal points', () => {
    expect(formatBytes(2000)).toBe('1.95 KB');
  });
});

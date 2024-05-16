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
import { isHDFS, isOFS } from './storageBrowserUtils';

describe('isHDFS function', () => {
  test('returns true for paths starting with "/"', () => {
    expect(isHDFS('/path/to/file')).toBe(true);
    expect(isHDFS('/')).toBe(true);
  });

  test('returns true for paths starting with "hdfs"', () => {
    expect(isHDFS('hdfs://path/to/file')).toBe(true);
    expect(isHDFS('hdfs://')).toBe(true);
  });

  test('returns false for other paths', () => {
    expect(isHDFS('s3://path/to/file')).toBe(false);
    expect(isHDFS('file://path/to/file')).toBe(false);
    expect(isHDFS('')).toBe(false);
  });
});

describe('isOFS function', () => {
  test('returns true for paths starting with "ofs://"', () => {
    expect(isOFS('ofs://path/to/file')).toBe(true);
    expect(isOFS('ofs://')).toBe(true);
  });

  test('returns false for other paths', () => {
    expect(isOFS('/path/to/file')).toBe(false);
    expect(isOFS('hdfs://path/to/file')).toBe(false);
    expect(isOFS('s3://path/to/file')).toBe(false);
    expect(isOFS('')).toBe(false);
  });
});

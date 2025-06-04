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

import {
  getBreadcrumbs,
  getLastDirOrFileNameFromPath,
  getFileSystemAndPath
} from './PathBrowser.util';

describe('PathBrowser utils', () => {
  describe('getFileSystemAndPath', () => {
    it('should return an empty filesystem and the full path if no filesystem is specified', () => {
      const path = '/test/folder';
      const result = getFileSystemAndPath(path);

      expect(result).toEqual({
        fileSystem: 'hdfs',
        path: '/test/folder'
      });
    });

    it('should correctly handle a path with a non-HDFS filesystem identifier', () => {
      const path = 'abfs://my/storage/path';
      const result = getFileSystemAndPath(path);

      expect(result).toEqual({
        fileSystem: 'abfs',
        path: '/my/storage/path'
      });
    });

    it('should correctly handle a path with special characters in the filesystem', () => {
      const path = 's3://bucket-name/folder';
      const result = getFileSystemAndPath(path);

      expect(result).toEqual({
        fileSystem: 's3',
        path: '/bucket-name/folder'
      });
    });

    it('should return an empty filesystem and path when the input is an empty string', () => {
      const path = '';
      const result = getFileSystemAndPath(path);

      expect(result).toEqual({
        fileSystem: '',
        path: ''
      });
    });
  });

  describe('getBreadcrumbs', () => {
    it('should construct breadcrumbs for an HDFS path', () => {
      const hdfsPath = '/test/folder';
      const result = getBreadcrumbs('hdfs', hdfsPath);

      expect(result).toEqual([
        { url: '/', label: 'hdfs' },
        { url: '/test', label: 'test' },
        { url: '/test/folder', label: 'folder' }
      ]);
    });

    it('should construct breadcrumbs for a non-HDFS path', () => {
      const nonHdfsPath = '/test/folder';
      const result = getBreadcrumbs('abfs', nonHdfsPath);

      expect(result).toEqual([
        { url: 'abfs://', label: 'abfs' },
        { url: 'abfs://test', label: 'test' },
        { url: 'abfs://test/folder', label: 'folder' }
      ]);
    });

    it('should handle paths with a trailing slash correctly', () => {
      const pathWithTrailingSlash = '/folder/with/trailing/slash/';
      const result = getBreadcrumbs('hdfs', pathWithTrailingSlash);

      expect(result).toEqual([
        { url: '/', label: 'hdfs' },
        { url: '/folder', label: 'folder' },
        { url: '/folder/with', label: 'with' },
        { url: '/folder/with/trailing', label: 'trailing' },
        { url: '/folder/with/trailing/slash', label: 'slash' }
      ]);
    });

    it('should handle paths that start with a leading slash with HDFS file system', () => {
      const pathWithLeadingSlash = '/path/to/file';
      const result = getBreadcrumbs('hdfs', pathWithLeadingSlash);

      expect(result).toEqual([
        { url: '/', label: 'hdfs' },
        { url: '/path', label: 'path' },
        { url: '/path/to', label: 'to' },
        { url: '/path/to/file', label: 'file' }
      ]);
    });

    it('should handle paths with numbers and mixed case labels', () => {
      const mixedCasePath = '/folder/PathWith123/anotherOne';
      const result = getBreadcrumbs('abfs', mixedCasePath);

      expect(result).toEqual([
        { url: 'abfs://', label: 'abfs' },
        { url: 'abfs://folder', label: 'folder' },
        { url: 'abfs://folder/PathWith123', label: 'PathWith123' },
        { url: 'abfs://folder/PathWith123/anotherOne', label: 'anotherOne' }
      ]);
    });

    it('should construct breadcrumbs for a file without subfolders', () => {
      const filePath = '/file.txt';
      const result = getBreadcrumbs('abfs', filePath);

      expect(result).toEqual([
        { url: 'abfs://', label: 'abfs' },
        { url: 'abfs://file.txt', label: 'file.txt' }
      ]);
    });
  });

  describe('getLastDirOrFileNameFromPath', () => {
    it('should return the correct fileName for a valid path', () => {
      const path = '/user/documents/file.txt';
      const result = getLastDirOrFileNameFromPath(path);
      expect(result).toBe('file.txt');
    });

    it('should return the correct fileName for a valid path with double file extension', () => {
      const path = '/user/documents/file.tar.gz';
      const result = getLastDirOrFileNameFromPath(path);
      expect(result).toBe('file.tar.gz');
    });

    it('should return an correct fileName for a path ending with a slash', () => {
      const path = '/user/documents/file.txt/';
      const result = getLastDirOrFileNameFromPath(path);
      expect(result).toBe('file.txt');
    });

    it('should return correct directoryName for S3A path', () => {
      const path = 's3a://example/hue/';
      const result = getLastDirOrFileNameFromPath(path);
      expect(result).toBe('hue');
    });

    it('should return correct directoryName when path is root S3A', () => {
      const path = 's3a://';
      const result = getLastDirOrFileNameFromPath(path);
      expect(result).toBe('s3a');
    });

    it('should return correct directoryName when path is root HDFS', () => {
      const path = '/';
      const result = getLastDirOrFileNameFromPath(path);
      expect(result).toBe('hdfs');
    });

    it('should return empty string when path is empty string', () => {
      const path = '';
      const result = getLastDirOrFileNameFromPath(path);
      expect(result).toBe('');
    });
  });
});

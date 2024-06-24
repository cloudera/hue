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

export const isHDFS = (path: string): boolean => {
  const currentPath = path.toLowerCase();
  return currentPath.indexOf('/') === 0 || currentPath.indexOf('hdfs') === 0;
};

export const isOFS = (path: string): boolean => {
  return path.toLowerCase().indexOf('ofs://') === 0;
};

export const isS3 = (path: string): boolean => {
  return path.toLowerCase().indexOf('s3a://') === 0;
};

export const isGS = (path: string): boolean => {
  return path.toLowerCase().indexOf('gs://') === 0;
};

export const isABFS = (path: string): boolean => {
  return path.toLowerCase().indexOf('abfs://') === 0;
};

export const isS3Root = (path: string): boolean => {
  return isS3(path) && path.toLowerCase() === 's3a://';
};

export const isGSRoot = (path: string): boolean => {
  return isGS(path) && path.toLowerCase() === 'gs://';
};

export const isABFSRoot = (path: string): boolean => {
  return isABFS(path) && path.toLowerCase() === 'abfs://';
};

export const isOFSRoot = (path: string): boolean => {
  return isOFS(path) && path.toLowerCase() === 'ofs://';
};

export const isOFSServiceID = (path: string): boolean => {
  return isOFS(path) && path.split('/').length === 3 && path.split('/')[2] !== '';
};

export const isOFSVol = (path: string): boolean => {
  return isOFS(path) && path.split('/').length === 4 && path.split('/')[3] !== '';
};

export const inTrash = (path: string): boolean => {
  return path.match(/^\/user\/.+?\/\.Trash/) !== null;
};

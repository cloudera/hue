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

const fileSysteRoot = {
  hdfs: ['/', 'hdfs'],
  ofs: ['ofs://'],
  s3a: ['s3a://'],
  gs: ['gs://'],
  abfs: ['abfs://']
};

const checkFileSystem = (path: string, allowedRoots: string[]): boolean => {
  const formattedPath = path.toLowerCase();
  return allowedRoots.some(root => formattedPath.startsWith(root));
};

const checkFileSystemRoot = (path: string, allowedRoots: string[]): boolean => {
  const formattedPath = path.toLowerCase();
  return allowedRoots.some(root => formattedPath === root);
};

export const isHDFS = (path: string): boolean => {
  return checkFileSystem(path, fileSysteRoot.hdfs);
};

export const isOFS = (path: string): boolean => {
  return checkFileSystem(path, fileSysteRoot.ofs);
};

export const isS3 = (path: string): boolean => {
  return checkFileSystem(path, fileSysteRoot.s3a);
};

export const isGS = (path: string): boolean => {
  return checkFileSystem(path, fileSysteRoot.gs);
};

export const isABFS = (path: string): boolean => {
  return checkFileSystem(path, fileSysteRoot.abfs);
};

export const isS3Root = (path: string): boolean => {
  return checkFileSystemRoot(path, fileSysteRoot.s3a);
};

export const isGSRoot = (path: string): boolean => {
  return checkFileSystemRoot(path, fileSysteRoot.gs);
};

export const isABFSRoot = (path: string): boolean => {
  return checkFileSystemRoot(path, fileSysteRoot.abfs);
};

export const isOFSRoot = (path: string): boolean => {
  return checkFileSystemRoot(path, fileSysteRoot.ofs);
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

export const inRestorableTrash = (path: string): boolean => {
  return path.match(/^\/user\/.+?\/\.Trash\/.+?/) !== null;
};

export const isFileSystemNonRoot = (path: string): boolean => {
  if (isS3(path)) {
    return !isS3Root(path);
  }
  if (isGS(path)) {
    return !isGSRoot(path);
  }
  if (isABFS(path)) {
    return !isABFSRoot(path);
  }
  if (isOFS(path)) {
    return !isOFSServiceID(path) && !isOFSVol(path);
  }
  //in case of HDFS root and non root have same level of access. hence no check
  return true;
};

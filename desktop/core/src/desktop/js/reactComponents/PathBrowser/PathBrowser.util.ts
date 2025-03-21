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

export interface BreadcrumbData {
  label: string;
  url: string;
}

export const getFileSystemAndPath = (
  filePath: string
): {
  fileSystem: string;
  path: string;
} => {
  if (filePath === '') {
    return {
      fileSystem: '',
      path: ''
    };
  }
  if (filePath.includes('://')) {
    const [fileSystem, path] = filePath.split('://');
    return {
      fileSystem,
      path: `/${path}`
    };
  }
  return {
    fileSystem: 'hdfs',
    path: filePath
  };
};

export const getBreadcrumbs = (fileSystem: string, path: string): BreadcrumbData[] => {
  const pathParts = path.split('/').filter(Boolean);
  const rootUrl = fileSystem === 'hdfs' ? '/' : `${fileSystem}://`;
  const rootlabel = fileSystem === 'hdfs' ? 'hdfs' : fileSystem;
  const rootNode = {
    url: rootUrl,
    label: rootlabel
  };

  return pathParts.reduce(
    (acc, part, index) => {
      const currentUrl = `${acc[index].url}${index === 0 ? '' : '/'}${part}`;
      acc.push({ url: currentUrl, label: part });
      return acc;
    },
    [rootNode]
  );
};

export const getLastDirOrFileNameFromPath = (inputPath: string): string => {
  if (inputPath === '') {
    return inputPath;
  }
  const { fileSystem, path } = getFileSystemAndPath(inputPath);
  const sanitizedPath = path.endsWith('/') ? path.slice(0, -1) : path;
  return sanitizedPath.split('/').pop() || fileSystem;
};

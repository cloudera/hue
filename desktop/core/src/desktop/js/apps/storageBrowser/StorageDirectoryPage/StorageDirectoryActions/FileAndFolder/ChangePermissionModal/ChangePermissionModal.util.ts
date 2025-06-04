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

import { StorageDirectoryTableData } from '../../../../types';

interface entityPermission {
  read: boolean;
  write: boolean;
  execute: boolean;
}

interface RWXPermissions {
  user: entityPermission;
  group: entityPermission;
  other: entityPermission;
  sticky: boolean;
  recursive: boolean;
}

export interface Permission {
  key: string;
  user?: boolean;
  group?: boolean;
  other?: boolean;
  common?: boolean;
}

// Helper function to parse the rwx string into boolean values
const parseRWX = (rwx: string): RWXPermissions => ({
  user: {
    read: rwx[1] === 'r',
    write: rwx[2] === 'w',
    execute: rwx[3] === 'x'
  },
  group: {
    read: rwx[4] === 'r',
    write: rwx[5] === 'w',
    execute: rwx[6] === 'x'
  },
  other: {
    read: rwx[7] === 'r',
    write: rwx[8] === 'w',
    execute: rwx[9] === 'x'
  },
  sticky: rwx[10] === 't',
  recursive: false
});

export const getInitialPermissions = (files: StorageDirectoryTableData[]): Permission[] => {
  if (files.length === 0) {
    return [];
  }

  const defaultPermissions: Permission[] = [
    { key: 'read' },
    { key: 'write' },
    { key: 'execute' },
    { key: 'sticky' },
    { key: 'recursive' }
  ];

  const filesPermissions = files.map(({ permission }) => parseRWX(permission));

  return defaultPermissions.reduce((acc: Permission[], permission) => {
    const { key } = permission;

    filesPermissions.forEach(parsedPermission => {
      if (['read', 'write', 'execute'].includes(key)) {
        permission.user = permission.user || parsedPermission.user[key];
        permission.group = permission.group || parsedPermission.group[key];
        permission.other = permission.other || parsedPermission.other[key];
      }
      if (['sticky', 'recursive'].includes(key)) {
        permission.common = permission.common || parsedPermission[key];
      }
    });

    acc.push(permission);

    return acc;
  }, []);
};

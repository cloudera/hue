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

import I18n from 'utils/i18n';

const SKIP_TABLE_NAMES = new Set([
  'select',
  'where',
  'join',
  'inner',
  'left',
  'right',
  'full',
  'cross',
  'outer',
  'on',
  'as',
  'values'
]);

const TABLE_REF_RE =
  /\b(?:FROM|JOIN)\s+(?:(?:`([^`]+)`|([A-Za-z_][\w$]*))\s*\.\s*)?(?:`([^`]+)`|([A-Za-z_][\w$]*))/gi;

const trimToUndefined = value => {
  if (value === undefined || value === null) {
    return undefined;
  }
  const trimmed = String(value).trim();
  return trimmed ? trimmed : undefined;
};

export const formatRowDetailsTitle = sourceName => {
  const trimmed = trimToUndefined(sourceName);
  if (!trimmed) {
    return I18n('Row details');
  }
  return I18n('Row details - %s', trimmed);
};

export const resolveRowDetailsSourceName = value => {
  try {
    if (typeof value === 'function') {
      return trimToUndefined(value());
    }
    return trimToUndefined(value);
  } catch (e) {
    return undefined;
  }
};

export const inferRowDetailsSourceName = ({ database, statement } = {}) => {
  const tables = [];
  const seen = new Set();
  const db = trimToUndefined(database);

  if (statement) {
    TABLE_REF_RE.lastIndex = 0;
    let match;
    while ((match = TABLE_REF_RE.exec(statement)) !== null) {
      const qualifier = trimToUndefined(match[1] || match[2]);
      const name = trimToUndefined(match[3] || match[4]);
      if (!name || SKIP_TABLE_NAMES.has(name.toLowerCase())) {
        continue;
      }
      const qualified = qualifier ? `${qualifier}.${name}` : db ? `${db}.${name}` : name;
      const key = qualified.toLowerCase();
      if (!seen.has(key)) {
        seen.add(key);
        tables.push(qualified);
      }
    }
  }

  if (tables.length === 0) {
    return db;
  }
  if (tables.length <= 3) {
    return tables.join(', ');
  }
  return `${tables.slice(0, 3).join(', ')}...`;
};

export const inferRowDetailsSourceNameFromExecutable = executable => {
  if (!executable) {
    return undefined;
  }
  const statement =
    (typeof executable.getRawStatement === 'function' && executable.getRawStatement()) ||
    (executable.parsedStatement && executable.parsedStatement.statement);
  const database =
    typeof executable.database === 'function' ? executable.database() : executable.database;
  return inferRowDetailsSourceName({ database, statement });
};

/**
 * Licensed to Cloudera, Inc. under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  Cloudera, Inc. licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import { Table, Column } from '../lib/entities';

export const dbName = 'db-name';
export const tableNamePrefix = 'table-name';
export const columnNamePrefix = 'column-name';

export function createTables(tableCount: number, columnCount: number): Table[] {
  const entities: Table[] = [];
  for (let t = 0; t < tableCount; t++) {
    const tableName = `${tableNamePrefix}-${t}`;
    const tableId: string = Table.buildId(dbName, tableName);

    const columns: Column[] = [];

    for (let c = 0; c < columnCount; c++) {
      columns.push(new Column(tableId, `${columnNamePrefix}-${c}`));
    }
    entities.push(new Table(dbName, tableName, columns));
  }
  return entities;
}

export function sleep(duration: number): Promise<unknown> {
  return new Promise(r => setTimeout(r, duration));
}

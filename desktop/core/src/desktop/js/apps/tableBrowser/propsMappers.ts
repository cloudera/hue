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

import { Table, Column } from '../../components/er-diagram/lib/entities';

function createTable(database: string, name: string, columns: Array<string>) {
  return new Table(database, name, columns);
}

function getTables(
  fromDB: string,
  fromTableName: string,
  columns: Array<string>,
  foreignKeys: Array<unknown>
) {
  const fromTable = createTable(fromDB, fromTableName, columns);
  const tables = [fromTable];
  const createdTableIdSet = new Set([fromTable.id]);

  foreignKeys.forEach((key: unknown) => {
    const toPath = key.to.split('.');
    const tableId = Table.buildId(toPath[0], toPath[1]);
    if (!createdTableIdSet.has(tableId)) {
      createdTableIdSet.add(tableId);
      tables.push(createTable(toPath[0], toPath[1], [toPath[2]]));
    }
  });

  return tables;
}

function getForeignKeyRelations(
  fromDB: string,
  fromTableName: string,
  foreignKeys: Array<unknown>
) {
  const fromTableId = Table.buildId(fromDB, fromTableName);
  return foreignKeys.map(key => {
    const toPath = key.to.split('.');
    return {
      desc: 'Foreign Key',
      left: new Column(fromTableId, key.name),
      right: new Column(Table.buildId(toPath[0], toPath[1]), toPath[2])
    };
  });
}

export function tableERD(catalogEntry: unknown): unknown {
  const fromDB: string = catalogEntry.path[0];
  const fromTable: string = catalogEntry.path[1];

  return {
    entities: getTables(
      fromDB,
      fromTable,
      catalogEntry.sourceMeta.columns,
      catalogEntry.sourceMeta.foreign_keys
    ),
    relations: getForeignKeyRelations(fromDB, fromTable, catalogEntry.sourceMeta.foreign_keys)
  };
}

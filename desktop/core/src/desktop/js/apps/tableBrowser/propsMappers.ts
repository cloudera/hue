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

import { Dictionary } from 'lodash';
import { Table, Column } from '../../components/er-diagram/lib/entities';
import { IEntity, IRelation } from '../../components/er-diagram/lib/interfaces';

interface IPrimaryKey {
  name: string;
}

interface IForeignKey {
  name: string;
  to: string;
}

interface ISourceMeta {
  columns: string[];
  primary_keys: IPrimaryKey[];
  foreign_keys: IForeignKey[];
}

interface ICatalogEntity {
  path: string[];
  sourceMeta: ISourceMeta;
}

interface IProps {
  entities: IEntity[];
  relations: IRelation[];
}

const createTable = (database: string, fromDB: string, name: string, columnNames: string[]) => {
  const tableId: string = Table.buildId(database, name);
  const columns: Column[] = columnNames.map((columnName: string) => {
    return new Column(tableId, columnName);
  });
  const table = new Table(database, name, columns);
  if (database === fromDB) {
    table.cssClassName = 'hide-db';
  }
  return table;
};

const reorderBasedOnKeys = (
  columnNames: string[],
  primaryKeys: IPrimaryKey[],
  foreignKeys: IForeignKey[]
): string[] => {
  const keyWeight: Dictionary<number> = {};

  columnNames.forEach((key: string) => (keyWeight[key] = 0));
  foreignKeys.forEach((key: IForeignKey) => (keyWeight[key.name] = 1));
  primaryKeys.forEach((key: IPrimaryKey) => (keyWeight[key.name] = 2));

  columnNames.sort((a, b) => keyWeight[b] - keyWeight[a]);

  return columnNames;
};

const getTables = (
  fromDB: string,
  fromTableName: string,
  columnNames: string[],
  primaryKeys: IPrimaryKey[],
  foreignKeys: IForeignKey[]
): IEntity[] => {
  columnNames = reorderBasedOnKeys(columnNames, primaryKeys, foreignKeys);
  const fromTable = createTable(fromDB, fromDB, fromTableName, columnNames);
  const tables = [fromTable];
  const createdTableIdSet = new Set([fromTable.id]);

  foreignKeys.forEach((key: IForeignKey) => {
    const toPath = key.to.split('.');
    const tableId = Table.buildId(toPath[0], toPath[1]);
    if (!createdTableIdSet.has(tableId)) {
      createdTableIdSet.add(tableId);
      tables.push(createTable(toPath[0], fromDB, toPath[1], [toPath[2]]));
    }
  });

  return tables;
};

const getForeignKeyRelations = (
  fromDB: string,
  fromTableName: string,
  foreignKeys: IForeignKey[]
): IRelation[] => {
  const fromTableId = Table.buildId(fromDB, fromTableName);
  return foreignKeys.map((key: IForeignKey) => {
    const toPath = key.to.split('.');
    return {
      desc: 'Foreign Key',
      left: new Column(fromTableId, key.name),
      right: new Column(Table.buildId(toPath[0], toPath[1]), toPath[2])
    };
  });
};

export const tableERD = (catalogEntry: ICatalogEntity): IProps => {
  const fromDB: string = catalogEntry.path[0];
  const fromTable: string = catalogEntry.path[1];

  return {
    entities: getTables(
      fromDB,
      fromTable,
      catalogEntry.sourceMeta.columns,
      catalogEntry.sourceMeta.primary_keys,
      catalogEntry.sourceMeta.foreign_keys
    ),
    relations: getForeignKeyRelations(fromDB, fromTable, catalogEntry.sourceMeta.foreign_keys)
  };
};

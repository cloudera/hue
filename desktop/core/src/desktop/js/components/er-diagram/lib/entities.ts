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

import { EntityTypes } from './enums';
import { IEntity } from './interfaces';

export class Table implements IEntity {
  readonly id: string;
  readonly type: EntityTypes = EntityTypes.Table;

  database: string;
  name: string;
  columns: Column[];

  className: string;

  constructor(database: string, name: string, columns: Array<Column>) {
    this.id = Table.buildId(database, name);
    this.database = database;
    this.name = name;
    this.columns = columns;
  }

  static buildId(db: string, name: string): string {
    return `${db}.${name}`;
  }
}

export class Column implements IEntity {
  readonly id: string;
  readonly type: EntityTypes = EntityTypes.Column;

  tableId: string;
  name: string;

  className: string;

  constructor(tableId: string, name: string) {
    this.id = Column.buildId(tableId, name);
    this.tableId = tableId;
    this.name = name;
  }

  static buildId(tableId: string, name: string): string {
    return `${tableId}.${name}`;
  }
}

export class Literal implements IEntity {
  readonly id: string;
  readonly type: EntityTypes = EntityTypes.Literal;

  value: string;

  className: string;

  constructor(value: string) {
    this.id = value;
    this.value = value;
  }
}

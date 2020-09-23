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

import CancellableJqPromise from 'api/cancellableJqPromise';
import DataCatalogEntry from 'catalog/dataCatalogEntry';
import { ParsedSqlStatement } from './sqlStatementsParser';

export interface IdentifierChainEntry {
  name: string;
}

export interface ParsedTable {
  identifierChain: IdentifierChainEntry[];
  subQuery?: unknown; // TODO: Define
}

export interface ParsedLocation {
  first_line: number;
  first_column: number;
  last_line: number;
  last_column: number;
}

export interface IdentifierLocation {
  type: string;
  alias?: string;
  source?: string;
  location: ParsedLocation;
  function?: string;
  missing?: boolean;
  value?: string;
  colRef: boolean;
  argumentPosition?: number;
  identifierChain?: IdentifierChainEntry[];
  expression?: { types: string[]; text: string };
  parentLocation?: ParsedLocation;
  resolveCatalogEntry?: (options?: {
    cancellable?: boolean;
  }) => CancellableJqPromise<DataCatalogEntry>;
}

export interface StatementDetails {
  selectedStatements: ParsedSqlStatement[];
  precedingStatements: ParsedSqlStatement[];
  activeStatement: ParsedSqlStatement;
  followingStatements: ParsedSqlStatement[];
}

export interface SqlStatementsParser {
  parse(text: string): ParsedSqlStatement;
}

declare const sqlStatementsParser: SqlStatementsParser;

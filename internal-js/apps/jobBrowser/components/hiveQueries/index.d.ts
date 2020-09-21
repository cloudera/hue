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

export interface Dag {
  dagInfo: {
    dagId: string;
  };
}

export interface NormalizedQueryPerf {
  compile: number;
  groupTotal: {
    pre: number;
    submit: number;
    running: number;
    post: number;
  };
  parse: number;
  PostHiveProtoLoggingHook: number;
  RemoveTempOrDuplicateFiles: number;
  RenameOrMoveFiles: number;
  TezBuildDag: number;
  TezRunDag: number;
  TezSubmitDag: number;
  TezSubmitToRunningDag: number;
  total: number;
}

export interface QueryPerf {
  compile?: number;
  parse?: number;
  PostHiveProtoLoggingHook?: number;
  RemoveTempOrDuplicateFiles?: number;
  RenameOrMoveFiles?: number;
  TezBuildDag?: number;
  TezRunDag?: number;
  TezSubmitDag?: number;
  TezSubmitToRunningDag?: number;
}

export interface Query {
  appIds?: string[]; // TODO: From API or adaption? Type?
  clientIpAddress?: unknown; // TODO: string?
  cpuTime?: unknown; // TODO: number?
  createdAt: number[];
  dagIds?: string[]; // TODO: From API or adaption? Type[]?
  dags: Dag[];
  dataRead?: unknown; // TODO: type?
  dataWritten?: unknown; // TODO: type?
  databasesUsed: { [name: string]: number }[];
  details?: {
    diagnostics?: string;
    perf?: QueryPerf;
    configuration?: { [key: string]: string }; // TODO: value always string?
  };
  domainId?: unknown; // TODO: type?
  duration?: number; // TODO: From API or adaption? number?
  elapsedTime: number;
  endTime: number; // TODO: can be undefined?
  executionMode: string;
  highlightedQuery?: unknown; // TODO: type?
  hiveInstanceAddress: string; // TODO: can be undefined?
  hiveInstanceType?: unknown; // TODO: type?
  id: number;
  isComplete?: boolean; // TODO: From API or adaption?
  llapAppId?: string;
  logId?: unknown; // TODO: type?
  operationId: string; // TODO: can be undefined?
  physicalMemory?: unknown; // TODO: type?
  processed: boolean; // TODO: can be undefined?
  query: string;
  queryId: string;
  queueName?: string;
  requestUser: string;
  sessionId: string;
  startTime: number;
  status: string;
  tablesRead: { table: string, database: string }[];
  tablesWritten: { table: string, database: string }[];
  tablesReadWithDatabase?: string; // TODO: From API or adaption? type?
  tablesWrittenWithDatabase?: string; // TODO: From API or adaption? type?
  threadId: string;
  usedCBO: string; // TODO: can be undefined?
  userId: string;
  virtualMemory?: unknown; // TODO: type?
}

export interface Facet {
  facetField: string;
  values: { key: string; value: number; }[]
}

export interface SearchFacet {
  [key: string]: { in: string[] };
}

export interface SearchSort {
  sortColumnId: string;
  sortOrder: string;
}

export interface Search {
  category: string;
  clause: string;
  columns: unknown; // TODO: Type? Was null in test
  entity: string;
  facet: SearchFacet;
  id: number;
  name: string;
  owner: string;
  range: unknown; // TODO: Type? Was null in test
  sort: SearchSort | null; // TODO: undefined?
  type: string;
}

export interface FieldInfo {
  displayName: string;
  facetable: boolean;
  fieldName: string;
  rangeFacetable: boolean;
  searchable: boolean;
  sortable: boolean;
}

export interface SearchRequest {
  endTime: number;
  limit: number;
  offset: number;
  text?: string;
  sortText: string;
  startTime: number;
  type: string;
}

export interface SearchMeta {
  limit: number;
  offset: number;
  size: number;
}

interface TableDefinition {
  rangeData: {
    title: string;
  },
  columnPreferences: { id: string }[]
}

interface DataProcessor {
  facets: {
    fieldCount?: number;
  }
}

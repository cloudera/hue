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

// Todo: Move upstream
export type KeyHash<T> = { [key: string]: T };

export interface CounterDetails {
  counterName: string;
  counterValue: string;
}

export interface CounterGroup {
  counterGroupName: string;
  counters: CounterDetails[];
}

export interface VertexEvent {
  eventtype: string;
  timestamp: number;
  eventinfo: KeyHash<unknown>;
}

export interface Vertex {
  id: number;
  name: string;
  vertexId: string;
  dagId: number;
  taskCount: number;

  events?: VertexEvent[];

  succeededTaskCount: number;
  completedTaskCount: number;
  failedTaskCount: number;
  killedTaskCount: number;
  failedTaskAttemptCount: number;
  killedTaskAttemptCount: number;

  className: string;

  startTime: number;
  endTime: number;
  initRequestedTime: number;
  startRequestedTime: number;
  status: string;
  finalStatus?: string;

  counters: CounterGroup[];
  stats: {
    firstTaskStartTime: number;
    lastTaskFinishTime: number;
    minTaskDuration: number;
    maxTaskDuration: number;
    avgTaskDuration: number;
  };
}

export interface DagPlanVertex {
  vertexName: string;

  outEdgeIds: unknown[];

  data: Vertex;
}

export interface DagPlan {
  vertices: DagPlanVertex[];
  edges: KeyHash<string>[];
  vertexGroups: unknown[];
}

// TODO: Flatten and cleanup DAG object
export interface Dag {
  dagInfo: {
    dagId: string;
    dagName: string;
    applicationId: string;
    status: string;
    startTime: number;
    endTime: number;
  };
  dagDetails: {
    counters: CounterGroup[];
    dagPlan: DagPlan;
    diagnostics: string;
    hiveQueryId: number;
    id: number;
    vertexNameIdMapping: { [key: string]: string };
  };
  config?: { [key: string]: string }; // TODO: value always string?
  vertices: Vertex[];
}

export interface Table {
  table: string;
  database: string;
}

export enum QueryStatus {
  STARTED = 'STARTED',
  RUNNING = 'RUNNING',
  SUCCESS = 'SUCCESS',
  ERROR = 'ERROR'
}

export type Perf = { [key: string]: number };

export interface Query {
  appIds?: string[]; // TODO: From API or adaption? Type?
  clientIpAddress?: unknown; // TODO: string?
  cpuTime?: unknown; // TODO: number?
  createdAt: number[];
  dagIds?: string[]; // TODO: From API or adaption? Type[]?
  dags: Dag[];
  dataRead?: number; // TODO: type?
  dataWritten?: number; // TODO: type?
  databasesUsed: { [name: string]: number }[];
  details: {
    diagnostics?: string;
    perf?: Perf;
    configuration?: { [key: string]: unknown }; // TODO: value type string?
    explainPlan?: unknown; // TODO: type?
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
  physicalMemory?: number; // TODO: type?
  processed: boolean; // TODO: can be undefined?
  query: string;
  queryId: string;
  queueName?: string;
  requestUser: string;
  sessionId: string;
  startTime: number;
  status: QueryStatus;
  tablesRead: Table[];
  tablesWritten: Table[];
  tablesReadWithDatabase?: string; // TODO: From API or adaption? type?
  tablesWrittenWithDatabase?: string; // TODO: From API or adaption? type?
  threadId: string;
  usedCBO: string; // TODO: can be undefined?
  userId: string;
  virtualMemory?: number; // TODO: type?
}

export interface SearchResultFacet {
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
  facet: SearchResultFacet;
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

export interface SearchMeta {
  limit: number;
  offset: number;
  size: number;
  updateTime: number;
}

interface TableDefinition {
  rangeData: {
    title: string;
  };
  columnPreferences: { id: string }[];
}

interface DataProcessor {
  facets: {
    fieldCount?: number;
  };
}

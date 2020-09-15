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
  }
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

export interface DiffQueryModel {
  queryOne: QueryModel;
  queryTwo: QueryModel;
}

export interface QueryModel {
  appIds: string[]; // TODO: string[]?
  dagIds: string[]; // TODO: string[]?
  dags: Dag[];
  details: {
    diagnostics?: string;
    perf?: QueryPerf;
  };
  duration: number; // TODO: number?
  endTime: number; // TODO: number?
  llapAppId?: string;
  query: string;
  queryId: string;
  queueName?: string;
  requestUser: string;
  sessionId: string;
  startTime: number; // TODO: number?
  status: string;
  tablesReadWithDatabase?: string; // TODO: Or number?
  tablesWrittenWithDatabase?: string; // TODO: Or number?
  threadId: string;
}

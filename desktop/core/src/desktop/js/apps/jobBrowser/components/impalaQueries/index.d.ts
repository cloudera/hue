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

export enum ImpalaQueryStatus {
  SUCCESS = 'FINISHED',
  ERROR = 'ERROR'
}

export enum ImpalaQueryTypes {
  QUERY = 'QUERY',
  DDL = 'DDL'
}

type Map = { [key: string]: string };
export interface ImpalaQueryProfile {
  summaryMap: Map;

  cpuMetrics: Map;
  hdfsMetrics: Map;
  insertMetrics: Map;
  memoryMetrics: Map;
  threadTimeMetrics: Map;
}

export interface ImpalaQuery {
  queryId: string;
  queryText: string;
  status: ImpalaQueryStatus;
  queryType: ImpalaQueryTypes;

  startTime: number;
  endTime: number;
  duration: number;

  userName: string;
  coordinator: string;

  cpuTime: number;
  rowsProduced: number;
  peakMemory: number;
  hdfsBytesRead: number;

  profile: ImpalaQueryProfile;
}

// TODO: Remove if not used
interface TableDefinition {
  rangeData: {
    title: string;
  };
  columnPreferences: { id: string }[];
}

// TODO: Remove if not used
interface DataProcessor {
  facets: {
    fieldCount?: number;
  };
}

export interface CounterGroup {
  counterGroupName: string;
  counters: CounterDetails[];
}

export interface CounterDetails {
  counterName: string;
  counterValue: string;
}

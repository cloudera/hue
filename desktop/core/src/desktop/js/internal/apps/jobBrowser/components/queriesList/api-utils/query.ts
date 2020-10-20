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

import axios, { AxiosResponse } from 'axios';
import { Query, Vertex } from '../index';

const QUERY_URL = '/jobbrowser/query-proxy/api/hive/query';
const VERTICES_URL = '/jobbrowser/query-proxy/api/hive/vertices';

export interface ExtendedQueryRequest {
  queryId: string;
  extended: boolean;
}

interface VerticesRequest {
  dagId: string;
}

const fetchDagVertices = async (dagId: string): Promise<Vertex[]> => {
  const response = await axios.get<VerticesRequest, AxiosResponse<{ vertices: Vertex[] }>>(
    VERTICES_URL,
    { params: { dagId: dagId } }
  );
  return response.data.vertices;
};

export const fetchExtendedQuery = async (queryId: string): Promise<Query> => {
  const response = await axios.get<ExtendedQueryRequest, AxiosResponse<{ query: Query }>>(
    QUERY_URL,
    { params: { queryId: queryId, extended: true } }
  );
  const query: Query = response.data.query;

  for (const dag of query.dags) {
    dag.vertices = await fetchDagVertices(dag.dagInfo.dagId);
  }

  return query;
};

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export const kill = async (queries: Query[]): Promise<void> => {
  // const queryIds = queries.map(query => query.queryId );
  // TODO: Implement POST ...
};

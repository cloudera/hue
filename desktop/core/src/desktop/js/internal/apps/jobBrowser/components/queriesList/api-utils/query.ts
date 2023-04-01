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

import { Query, QueryStatus, Vertex } from '../index.d';
import { ApiError } from './api';

import { get, post } from 'api/utils';

const sleep = ms => new Promise(r => setTimeout(r, ms));

const QUERY_URL = '/jobbrowser/query-store/api/hive/query';
const QUERY_KILL_URL = '/jobbrowser/api/job/action/queries-hive/kill';
const VERTICES_URL = '/jobbrowser/query-store/api/hive/vertices';

const POLL_DELAY = 3000;
const POLL_COUNT = 10;

export const isRunning = (query: Query): boolean =>
  query.status === QueryStatus.STARTED || query.status === QueryStatus.RUNNING;

export interface ExtendedQueryRequest {
  queryId: string;
  extended: boolean;
}

interface VerticesRequest {
  dagId: string;
}

const fetchDagVertices = async (dagId: string): Promise<Vertex[]> => {
  const params: VerticesRequest = { dagId: dagId };
  try {
    const response = await get<{ vertices: Vertex[] }>(VERTICES_URL, params);
    return response.vertices;
  } catch (err) {
    throw new ApiError(err);
  }
};

export const fetchQuery = async (queryId: string): Promise<Query> => {
  const params = { queryId: queryId };
  try {
    const response = await get<{ query: Query }>(QUERY_URL, params);
    return response.query;
  } catch (err) {
    throw new ApiError(err);
  }
};

export const fetchExtendedQuery = async (queryId: string): Promise<Query> => {
  const params = { queryId: queryId, extended: true };
  try {
    const response = await get<{ query: Query }>(QUERY_URL, params);
    const query: Query = response.query;

    for (const dag of query.dags) {
      dag.vertices = await fetchDagVertices(dag.dagInfo.dagId);
    }

    return query;
  } catch (err) {
    throw new ApiError(err);
  }
};

export const kill = async (queries: Query[]): Promise<void> => {
  const queryIds = queries.map((query: Query) => query.queryId);

  const params = new URLSearchParams();
  params.append('operation', JSON.stringify({ action: 'kill' }));
  params.append('interface', JSON.stringify('queries-hive'));
  params.append('app_ids', JSON.stringify(queryIds));

  try {
    await post(QUERY_KILL_URL, params, {
      qsEncodeData: false
    });
  } catch (err) {
    throw new ApiError(err);
  }
};

/**
 * Waits for a max POLL_COUNT * POLL_DELAY milliseconds if checkFunction is true.
 * Returns false if checkFunction becomes false while waiting, else returns true after max waiting time.
 * @param query Query
 * @param checkFunction (query: Query) => boolean
 */
export const waitIf = async (
  query: Query,
  checkFunction: (query: Query) => boolean
): Promise<boolean> => {
  const queryId = query.queryId;
  for (let i = 0; i < POLL_COUNT; i++) {
    const query: Query = await fetchQuery(queryId);
    if (checkFunction(query)) {
      await sleep(POLL_DELAY);
    } else {
      return false;
    }
  }
  return true;
};

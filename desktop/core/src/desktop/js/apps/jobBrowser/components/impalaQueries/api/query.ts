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

import { ImpalaQuery, ImpalaQueryProfile } from '../index.d';
import { SearchRequest, SearchResponse } from '../../../commons/api-utils/search';
import { get, post } from 'api/utils';

const QUERIES_URL = '/jobbrowser/query-store/api/impala/queries';

export const searchQueries = async <Q>(data: SearchRequest): Promise<SearchResponse<Q>> => {
  const response = await post<SearchResponse<Q>>(QUERIES_URL, data, {
    qsEncodeData: false
  });
  return response;
};

type QueryData = { query: ImpalaQuery; profile: ImpalaQueryProfile };
export const loadQuery = async (queryId: string): Promise<ImpalaQuery> => {
  const url = `${QUERIES_URL}/${encodeURIComponent(queryId)}`;
  const response = await get<QueryData>(url);
  return {
    ...response.query,
    profile: response.profile
  };
};

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
import searchMockResponse from './test/api/query_search_post_response.json';
import queryMockResponse from './test/api/hive_query_get_response_3.json';
import { Facet, FieldInfo, Query, Search, SearchMeta } from './index';

const QUERY_URL = 'proxy/api/hive/query';
const SEARCH_URL = 'proxy/api/query/search';

const JSON_RESPONSE = {
  status: 200,
  statusText: 'OK',
  headers: { 'content-type': 'application/json' },
  request: {}
};

const defaultAdapter = axios.defaults.adapter;
axios.defaults.adapter = config =>
  new Promise((resolve, reject) => {
    if (config.url && config.url.indexOf(SEARCH_URL) !== -1) {
      const request = JSON.parse(config.data);
      searchMockResponse.meta.offset = request.offset;
      searchMockResponse.meta.limit = request.limit;
      resolve(<AxiosResponse>{
        ...JSON_RESPONSE,
        data: JSON.stringify(searchMockResponse)
      });
    } else if (config.url && config.url.indexOf(QUERY_URL) !== -1) {
      resolve(<AxiosResponse>{
        ...JSON_RESPONSE,
        data: JSON.stringify(queryMockResponse)
      });
    } else {
      axios
        .create({ ...config, adapter: defaultAdapter })
        .request(config)
        .then(resolve)
        .catch(reject);
    }
  });

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export const fetchSuggestedSearches = async (options: {
  entityType: string;
}): Promise<Search[]> => {
  // TODO: Implement GET 'api/suggested-searches?entityType=x'
  const response = { searches: [] };
  return response.searches;
};

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export const fetchFacets = async (options: {
  startTime: number;
  endTime: number;
  facetFields: string;
}): Promise<{ facets: Facet[]; rangeFacets: unknown[] }> => {
  // TODO: Implement GET '/api/query/facets?startTime=x&endTime=y&facetFields=z'
  return { facets: [], rangeFacets: [] };
};

export const fetchFieldsInfo = async (): Promise<FieldInfo[]> => {
  // TODO: Implement GET '/api/query/fields-information'
  const response = { fieldsInfo: [] };
  return response.fieldsInfo;
};

export interface SearchRequest {
  endTime: number;
  limit: number;
  offset: number;
  text?: string;
  sortText: string;
  startTime: number;
  type: string;
}

export interface SearchResponse {
  meta: SearchMeta;
  queries: Query[];
}

export const search = async (options: SearchRequest): Promise<SearchResponse> => {
  const response = await axios.post<SearchRequest, AxiosResponse<SearchResponse>>(
    SEARCH_URL,
    options
  );
  return response.data;
};

export const fetchExtendedQuery = async (options: { queryId: string }): Promise<Query> => {
  const response = await axios.post<
    { queryId: string; extended: boolean },
    AxiosResponse<{ query: Query }>
  >(QUERY_URL, { ...options, extended: true });
  return response.data.query;
};

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export const deleteSearch = async (search: Search): Promise<void> => {
  // TODO: Implement POST ...
};

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export const saveSearch = async (options: {
  name: string;
  category: string;
  type: string;
  entity: string;
  clause: string;
}): Promise<void> => {
  // TODO: Implement POST ...
};

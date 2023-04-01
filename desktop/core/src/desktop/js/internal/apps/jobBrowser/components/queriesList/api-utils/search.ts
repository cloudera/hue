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

import { get, post } from 'api/utils';
import { ApiError } from './api';

import { Facet } from '../../../../../../components/FacetSelector';
import { FieldInfo, Query, Search, SearchMeta } from '../index';
// Uncomment to serve mock response instead of calling the API endpoints
// import '../test/mockSearchHelper';

const SEARCH_URL = '/jobbrowser/query-store/api/query/search';
const FACETS_URL = '/jobbrowser/query-store/api/query/facets';

export interface SearchFacet {
  field: string;
  values: string[];
}

export interface SearchRequest {
  endTime: number;
  limit: number;
  offset: number;
  text?: string;
  facets?: SearchFacet[];
  sortText: string;
  startTime: number;
}

export interface SearchResponse {
  meta: SearchMeta;
  queries: Query[];
}

export const searchQueries = async (options: SearchRequest): Promise<SearchResponse> => {
  try {
    return await post<SearchResponse>(
      SEARCH_URL,
      {
        search: { ...options, type: 'BASIC' }
      },
      {
        qsEncodeData: false
      }
    );
  } catch (err) {
    throw new ApiError(err);
  }
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

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export const fetchSuggestedSearches = async (options: {
  entityType: string;
}): Promise<Search[]> => {
  // TODO: Implement GET 'api/suggested-searches?entityType=x'
  const response = { searches: [] };
  return response.searches;
};

export interface FacetsParams {
  startTime: number;
  endTime: number;
  facetFields: string | string[];
}

export interface FacetsResponse {
  facets: Facet[];
  rangeFacets: unknown[];
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export const fetchFacets = async (params: FacetsParams): Promise<FacetsResponse> => {
  if (Array.isArray(params.facetFields)) {
    params.facetFields = params.facetFields.join(',');
  }
  try {
    // TODO: Implement GET '/api/query/facets?startTime=x&endTime=y&facetFields=z'
    return await get<FacetsResponse>(FACETS_URL, params);
  } catch (err) {
    throw new ApiError(err);
  }
};

export const fetchFieldsInfo = async (): Promise<FieldInfo[]> => {
  // TODO: Implement GET '/api/query/fields-information'
  const response = { fieldsInfo: [] };
  return response.fieldsInfo;
};

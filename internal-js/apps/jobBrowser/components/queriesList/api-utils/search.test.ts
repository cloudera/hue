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
import { Query } from '..';

import { searchQueries, SearchRequest, SearchResponse } from './search';

import queryMockResponse2 from '../test/api/hive_query_get_response_2.json';
import queryMockResponse3 from '../test/api/hive_query_get_response_3.json';

describe('search.ts', () => {
  it('Should load queries data', async () => {
    jest.spyOn(axios, 'post').mockImplementation(
      async (): Promise<AxiosResponse<{ queries: Query[] }>> =>
        Promise.resolve(<AxiosResponse>{
          data: { queries: [queryMockResponse2.query, queryMockResponse3.query] }
        })
    );

    const response: SearchResponse = await searchQueries(<SearchRequest>{});

    expect(response.queries.length).toBe(2);
    expect(response.queries[0].queryId).toBe(queryMockResponse2.query.queryId);
    expect(response.queries[1].queryId).toBe(queryMockResponse3.query.queryId);
  });
});

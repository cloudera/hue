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

import api from './api';
import { AxiosResponse } from 'axios';
import { fetchExtendedQuery } from './query';
import { Query, Vertex } from '..';

import queryMockResponse from '../test/api/hive_query_get_response_2.json';

const TEST_QUERY_ID = 'hive_1234';

describe('query.ts', () => {
  it('Should load query data', async () => {
    jest
      .spyOn(api, 'get')
      .mockImplementation(
        async (): Promise<AxiosResponse<{ query: Query }>> =>
          Promise.resolve(<AxiosResponse>{ data: queryMockResponse })
      );

    const query = await fetchExtendedQuery(TEST_QUERY_ID);

    expect(query.query).toBe(queryMockResponse.query.query);
    expect(query.dags.length).toBe(1);
    expect(query.dags[0].vertices).toBeUndefined();
  });

  it('Should load query & vertices data', async () => {
    const TEST_VERTEX_DATA = {};

    jest.spyOn(api, 'get').mockImplementation(
      async (): Promise<AxiosResponse<{ query: Query; vertices: Vertex[] }>> =>
        Promise.resolve(<AxiosResponse>{
          data: { query: queryMockResponse.query, vertices: [TEST_VERTEX_DATA] }
        })
    );

    const query = await fetchExtendedQuery(TEST_QUERY_ID);

    expect(query.query).toBe(queryMockResponse.query.query);
    expect(query.dags.length).toBe(1);
    expect(query.dags[0].vertices[0]).toBe(TEST_VERTEX_DATA);
  });
});

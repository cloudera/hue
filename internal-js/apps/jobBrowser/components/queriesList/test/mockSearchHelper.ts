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
import searchMockResponse from '../test/api/query_search_post_response.json';
import facetsMockResponse from '../test/api/query_facets_get_response_1.json';

const SEARCH_URL = '/jobbrowser/query-proxy/api/query/search';
const FACETS_URL = '/jobbrowser/query-proxy/api/query/facets';

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
      resolve(<AxiosResponse>{
        ...JSON_RESPONSE,
        data: JSON.stringify(searchMockResponse)
      });
    } else if (config.url && config.url.indexOf(FACETS_URL) !== -1) {
      resolve(<AxiosResponse>{
        ...JSON_RESPONSE,
        data: JSON.stringify(facetsMockResponse)
      });
    } else {
      axios
        .create({ ...config, adapter: defaultAdapter })
        .request(config)
        .then(resolve)
        .catch(reject);
    }
  });

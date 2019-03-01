// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

const globalVars = {
  LOGGED_USERNAME: 'foo',
  CACHEABLE_TTL: 1,
  HAS_OPTIMIZER: false,
  AUTOCOMPLETE_TIMEOUT: 1,
  HUE_I18n: {
    autocomplete: {
      category: {
        all: 'all',
        column: 'columns',
        cte: 'cte',
        database: 'database',
        field: 'field',
        function: 'function',
        identifier: 'identifier',
        keyword: 'keyword',
        popular: 'popular',
        sample: 'sample',
        table: 'table',
        udf: 'udf',
        option: 'option',
        variable: 'variable'
      },
      meta: {
        aggregateFunction: 'aggregateFunction',
        alias: 'alias',
        commonTableExpression: 'commonTableExpression',
        database: 'database',
        filter: 'filter',
        groupBy: 'groupBy',
        join: 'join',
        joinCondition: 'joinCondition',
        keyword: 'keyword',
        orderBy: 'orderBy',
        table: 'table',
        sample: 'sample',
        variable: 'variable',
        view: 'view',
        virtual: 'virtual'
      }
    }
  }
};

Object.keys(globalVars).forEach(key => {
  global[key] = globalVars[key];
  global.window[key] = globalVars[key];
});

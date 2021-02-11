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

import { SetOptions, SqlReferenceProvider, UdfCategory } from 'sql/reference/types';

const GENERIC = 'generic';
const EMPTY_KEYWORDS = new Set<string>();

const KEYWORD_REFS: { [attr: string]: () => Promise<{ RESERVED_WORDS?: Set<string> }> } = {
  calcite: async () => import(/* webpackChunkName: "calcite-ref" */ './calcite/reservedKeywords'),
  generic: async () => import(/* webpackChunkName: "generic-ref" */ './generic/reservedKeywords'),
  hive: async () => import(/* webpackChunkName: "hive-ref" */ './hive/reservedKeywords'),
  impala: async () => import(/* webpackChunkName: "impala-ref" */ './impala/reservedKeywords'),
  postgresql: async () =>
    import(/* webpackChunkName: "generic-ref" */ './postgresql/reservedKeywords'),
  presto: async () => import(/* webpackChunkName: "generic-ref" */ './presto/reservedKeywords'),
  flink: async () => import(/* webpackChunkName: "flink-ref" */ './flink/reservedKeywords')
};

const SET_REFS: { [attr: string]: () => Promise<{ SET_OPTIONS?: SetOptions }> } = {
  impala: async () => import(/* webpackChunkName: "impala-ref" */ './impala/setReference')
};

const UDF_REFS: { [attr: string]: () => Promise<{ UDF_CATEGORIES?: UdfCategory[] }> } = {
  generic: async () => import(/* webpackChunkName: "generic-ref" */ './generic/udfReference'),
  hive: async () => import(/* webpackChunkName: "hive-ref" */ './hive/udfReference'),
  impala: async () => import(/* webpackChunkName: "impala-ref" */ './impala/udfReference'),
  pig: async () => import(/* webpackChunkName: "pig-ref" */ './pig/udfReference'),
  flink: async () => import(/* webpackChunkName: "flink-ref" */ './flink/udfReference')
};

export class SqlReferenceRepository implements SqlReferenceProvider {
  async getReservedKeywords(dialect: string): Promise<Set<string>> {
    const refImport = KEYWORD_REFS[dialect] || KEYWORD_REFS[GENERIC];
    const module = await refImport();
    return module.RESERVED_WORDS || EMPTY_KEYWORDS;
  }

  async getSetOptions(dialect: string): Promise<SetOptions> {
    if (SET_REFS[dialect]) {
      const module = await SET_REFS[dialect]();
      return module.SET_OPTIONS || {};
    }
    return {};
  }

  async getUdfCategories(dialect: string): Promise<UdfCategory[]> {
    const refImport = UDF_REFS[dialect] || UDF_REFS[GENERIC];
    const module = await refImport();
    return module.UDF_CATEGORIES || [];
  }

  hasUdfCategories(dialect: string): boolean {
    return !!UDF_REFS[dialect];
  }
}

const sqlReferenceRepository = new SqlReferenceRepository();

export default sqlReferenceRepository;

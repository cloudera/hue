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

import 'core-js/stable';
import 'regenerator-runtime/runtime';

import { attachSyntaxListener } from './workerUtils';
import sqlParserRepository from 'parse/sql/sqlParserRepository';

declare let __webpack_public_path__: string;

const ctx = self as DedicatedWorkerGlobalScope;
let baseUrlSet = false;

attachSyntaxListener(ctx, sqlParserRepository, msg => {
  if (!baseUrlSet) {
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    __webpack_public_path__ = (msg.data.hueBaseUrl || '') + '/dynamic_bundle/workers/';
    baseUrlSet = true;
  }
});

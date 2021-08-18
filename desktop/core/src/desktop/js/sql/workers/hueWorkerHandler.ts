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

import {
  attachLocationWorkerEvents,
  attachSyntaxWorkerEvents
} from 'sql/workers/registrationUtils';
import { hueWindow } from 'types/types';

const registerSyntaxWorker = (): Worker | undefined =>
  new Worker(
    `${(<hueWindow>window).HUE_BASE_URL}/desktop/workers/aceSqlSyntaxWorker.js?v=${
      (<hueWindow>window).HUE_VERSION
    }.1`
  );

const registerLocationWorker = (): Worker | undefined =>
  new Worker(
    `${(<hueWindow>window).HUE_BASE_URL}/desktop/workers/aceSqlLocationWorker.js?v=${
      (<hueWindow>window).HUE_VERSION
    }.1`
  );

let registered = false;

export const registerHueWorkers = (): void => {
  if (!window.Worker || registered) {
    return;
  }
  // It can take a while before the worker is active

  // For syntax checking
  const aceSqlSyntaxWorker = registerSyntaxWorker();
  attachSyntaxWorkerEvents(aceSqlSyntaxWorker);

  // For location marking
  const aceSqlLocationWorker = registerLocationWorker();
  attachLocationWorkerEvents(aceSqlLocationWorker);
  registered = true;
};

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

import { GenericApiResponse } from 'types/types';

export interface Compute {
  id: string;
  name: string;
  type: string;
  namespace?: string;
}

export interface Namespace {
  id: string;
  name: string;
  status: string;
  computes: Compute[];
}

export interface Cluster {
  credentials: Record<string, unknown>;
  id: string;
  name: string;
  type: string;
}

export interface AppConfig<T extends Interpreter> {
  buttonName: string;
  displayName: string;
  interpreter_names?: string[];
  interpreters: T[];
  name: string;
  page?: string;
}

export interface EditorConfig extends AppConfig<EditorInterpreter> {
  default_limit: number | null;
  default_sql_interpreter: string;
}

export enum AppType {
  browser = 'browser',
  editor = 'editor',
  dashboard = 'dashboard',
  scheduler = 'scheduler'
}

export interface HueConfig extends GenericApiResponse {
  app_config: {
    [AppType.browser]?: AppConfig<BrowserInterpreter>;
    catalogs?: CatalogInterpreter[];
    [AppType.dashboard]?: AppConfig<DashboardInterpreter>;
    [AppType.editor]?: EditorConfig;
    home?: AppConfig<Interpreter>;
    [AppType.scheduler]?: AppConfig<SchedulerInterpreter>;
  };
  button_action: AppConfig<Interpreter>[];
  cluster_type: string;
  clusters: Cluster[];
  default_sql_interpreter: string;
  documents: {
    types: string[];
  };
  has_computes: boolean;
  main_button_action: AppConfig<Interpreter>;
  status: number;
  hue_config: {
    enable_sharing: boolean;
  };
}

export interface Interpreter {
  buttonName: string;
  displayName: string;
  page: string;
  tooltip: string;
  type: string;
}

export interface IdentifiableInterpreter extends Interpreter {
  dialect?: string;
  id: string;
}

/* eslint-disable @typescript-eslint/no-empty-interface */
export interface Connector extends IdentifiableInterpreter {
  dialect_properties?: {
    sql_identifier_quote?: string;
  };
}

export interface EditorInterpreter extends IdentifiableInterpreter {
  dialect_properties: Record<string, unknown> | null;
  is_batchable: boolean;
  is_sql: boolean;
  name: string;
  optimizer: string;
  dialect: string;
}

/* eslint-disable @typescript-eslint/no-empty-interface */
export interface BrowserInterpreter extends Interpreter {}

export interface CatalogInterpreter extends IdentifiableInterpreter {
  is_catalog: boolean;
  is_sql: boolean;
  name: string;
}

export interface DashboardInterpreter extends IdentifiableInterpreter {
  is_sql: string;
}

/* eslint-disable @typescript-eslint/no-empty-interface */
export interface SchedulerInterpreter extends Interpreter {}

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
  AppType,
  BrowserInterpreter,
  DashboardInterpreter,
  EditorInterpreter,
  HueConfig,
  Interpreter
} from './types';

export declare const REFRESH_CONFIG_EVENT = 'cluster.config.refresh.config';
export declare const CONFIG_REFRESHED_EVENT = 'cluster.config.set.config';
export declare const GET_KNOWN_CONFIG_EVENT = 'cluster.config.get.config';

export declare const refreshConfig: () => Promise<HueConfig>;
export declare const getLastKnownConfig: () => HueConfig | undefined;
export declare const findDashboardConnector: (
  connectorTest: (connector: Interpreter) => boolean
) => DashboardInterpreter | undefined;
export declare const findBrowserConnector: (
  connectorTest: (connector: Interpreter) => boolean
) => BrowserInterpreter | undefined;
export declare const findEditorConnector: (
  connectorTest: (connector: Interpreter) => boolean
) => EditorInterpreter | undefined;
export declare const filterEditorConnectors: (
  connectorTest: (connector: Interpreter) => boolean
) => EditorInterpreter[] | undefined;

/**
 * This takes the initial path from the "browser" config, used in cases where the users can't access '/'
 * for abfs etc.
 */
export declare const getRootFilePath: (connector: BrowserInterpreter) => string;

declare const _default: {
  refreshConfig: (hueBaseUrl?: string) => Promise<HueConfig>;
  getInterpreters: (appType: AppType) => Interpreter[];
  getLastKnownConfig: () => HueConfig;
  getRootFilePath: (connector: BrowserInterpreter) => string;
  findBrowserConnector: (connectorTest: (connector: Interpreter) => boolean) => BrowserInterpreter;
  findDashboardConnector: (
    connectorTest: (connector: Interpreter) => boolean
  ) => DashboardInterpreter;
  findEditorConnector: (connectorTest: (connector: Interpreter) => boolean) => EditorInterpreter;
};

export default _default;

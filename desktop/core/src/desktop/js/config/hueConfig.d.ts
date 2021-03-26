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
  Interpreter,
  SchedulerInterpreter
} from './types';

interface InterpreterMap {
  [AppType.browser]: BrowserInterpreter;
  [AppType.editor]: EditorInterpreter;
  [AppType.dashboard]: DashboardInterpreter;
  [AppType.scheduler]: SchedulerInterpreter;
  [AppType.sdkapps]: Interpreter;
}

declare type ConnectorTest<T extends keyof InterpreterMap> = (
  connector: InterpreterMap[T]
) => boolean;

export declare const refreshConfig: () => Promise<HueConfig>;
export declare const getLastKnownConfig: () => HueConfig | undefined;
export declare const getConfig: () => Promise<HueConfig>;

export declare const findDashboardConnector: (
  connectorTest: ConnectorTest<AppType.dashboard>
) => DashboardInterpreter | undefined;
export declare const findBrowserConnector: (
  connectorTest: ConnectorTest<AppType.browser>
) => BrowserInterpreter | undefined;
export declare const findEditorConnector: (
  connectorTest: ConnectorTest<AppType.editor>
) => EditorInterpreter | undefined;
export declare const filterBrowserConnectors: (
  connectorTest: ConnectorTest<AppType.browser>
) => BrowserInterpreter[];
export declare const filterEditorConnectors: (
  connectorTest: ConnectorTest<AppType.editor>
) => EditorInterpreter[];

/**
 * This takes the initial path from the "browser" config, used in cases where the users can't access '/'
 * for abfs etc.
 */
export declare const getRootFilePath: (connector: BrowserInterpreter) => string;

declare const _default: {
  refreshConfig: () => Promise<HueConfig>;
  getInterpreters: <T extends keyof InterpreterMap>(appType: T) => InterpreterMap[T][];
  getLastKnownConfig: () => HueConfig;
  getRootFilePath: (connector: BrowserInterpreter) => string;
  findBrowserConnector: (connectorTest: ConnectorTest<AppType.browser>) => BrowserInterpreter;
  findDashboardConnector: (connectorTest: ConnectorTest<AppType.dashboard>) => DashboardInterpreter;
  findEditorConnector: (connectorTest: ConnectorTest<AppType.editor>) => EditorInterpreter;
};
export default _default;

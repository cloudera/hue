// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// 'License'); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an 'AS IS' BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import { ConnectorNamespaces, GetOptions } from 'catalog/contextCatalog';
import { Connector, EditorInterpreter, HueConfig } from 'config/types';
import Executor, { ExecutorOptions } from 'apps/editor/execution/executor';
import { DataCatalog } from 'catalog/dataCatalog';

export interface HueComponentConfig {
  baseUrl?: string;
}

declare const _default: {
  clearContextCatalogCache(connector: Connector): Promise<void>;
  configure(config: HueComponentConfig): void;
  createExecutor(options: ExecutorOptions): Executor;
  dataCatalog: DataCatalog;
  findEditorConnector(
    connectorTest: (connector: EditorInterpreter) => boolean
  ): EditorInterpreter | undefined;
  getNamespaces(options: GetOptions): Promise<ConnectorNamespaces>;
  isQueryEditorComponentsDefined(): Promise<void>;
  refreshConfig(hueBaseUrl?: string): Promise<HueConfig>;
  setBaseUrl(baseUrl: string): void;
  setBearerToken(bearerToken: string): void;
};

export default _default;

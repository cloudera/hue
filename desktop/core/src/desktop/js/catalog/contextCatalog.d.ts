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

import { Cluster, Compute, IdentifiableInterpreter, Namespace } from 'config/types';

interface GetOptions {
  connector: IdentifiableInterpreter;
  clearCache?: boolean;
  silenceErrors?: boolean;
}

interface ConnectorNamespaces {
  dynamic?: boolean;
  hueTimestamp: number;
  namespaces: Namespace[];
}

export declare const getNamespaces: ({
  connector,
  clearCache,
  silenceErrors
}: GetOptions) => Promise<ConnectorNamespaces>;
export declare const getComputes: ({
  connector,
  clearCache,
  silenceErrors
}: GetOptions) => Promise<Compute[]>;
export declare const getClusters: ({
  connector,
  clearCache,
  silenceErrors
}: GetOptions) => Promise<Cluster[]>;

declare const _default: {
  getNamespaces: ({
    connector,
    clearCache,
    silenceErrors
  }: GetOptions) => Promise<ConnectorNamespaces>;
  getComputes: ({ connector, clearCache, silenceErrors }: GetOptions) => Promise<Compute[]>;
  getClusters: ({ connector, clearCache, silenceErrors }: GetOptions) => Promise<Cluster[]>;
};
export default _default;

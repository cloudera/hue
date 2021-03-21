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

import localForage from 'localforage';
import { UdfCategory } from 'sql/reference/types';
import { Connector } from 'config/types';

const GLOBAL_UDF_CACHE_KEY = 'HUE_GLOBAL_UDF_KEY';
const VERSION = '0';

const getStore = (connector: Connector) =>
  localForage.createInstance({
    name: `HueUdfCatalog_${VERSION}_${connector.id}`
  });

export const clearUdfCache = async (connector: Connector): Promise<void> =>
  await getStore(connector).clear();

export const getCachedUdfCategories = async (
  connector: Connector,
  database: string | undefined
): Promise<UdfCategory[]> => await getStore(connector).getItem(database || GLOBAL_UDF_CACHE_KEY);

export const setCachedUdfCategories = async (
  connector: Connector,
  database: string | undefined,
  categories: UdfCategory[]
): Promise<UdfCategory[]> =>
  await getStore(connector).setItem(database || GLOBAL_UDF_CACHE_KEY, categories);

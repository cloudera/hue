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

import { simplePostAsync } from 'api/apiUtils';
import { FETCH_CONFIG_API } from 'api/urls';
import {
  AppType,
  BrowserInterpreter,
  DashboardInterpreter,
  EditorInterpreter,
  HueConfig,
  Interpreter
} from 'types/config';
import huePubSub from 'utils/huePubSub';

export const REFRESH_CONFIG_EVENT = 'cluster.config.refresh.config';
export const CONFIG_REFRESHED_EVENT = 'cluster.config.set.config';
export const GET_KNOWN_CONFIG_EVENT = 'cluster.config.get.config';

let lastConfigPromise: Promise<HueConfig> | undefined;
let lastKnownConfig: HueConfig | undefined;

const fetchConfig = async (): Promise<HueConfig> =>
  await simplePostAsync(FETCH_CONFIG_API, {}, { silenceErrors: true });

export const refreshConfig = async (): Promise<HueConfig> => {
  lastConfigPromise = new Promise<HueConfig>(async (resolve, reject) => {
    try {
      const apiResponse = await fetchConfig();
      if (apiResponse.status == 0) {
        lastKnownConfig = apiResponse;
        resolve(lastKnownConfig);
      } else {
        huePubSub.publish('hue.error', apiResponse.message);
        reject();
      }
    } catch (err) {
      reject(err);
    }
  });

  lastConfigPromise
    .then(config => {
      huePubSub.publish(CONFIG_REFRESHED_EVENT, config);
    })
    .catch(() => {
      huePubSub.publish(CONFIG_REFRESHED_EVENT);
    });

  return lastConfigPromise;
};

export const getLastKnownConfig = (): HueConfig | undefined => lastKnownConfig;

const getInterpreters = (appType: AppType): Interpreter[] => {
  if (!lastKnownConfig || !lastKnownConfig.app_config) {
    return [];
  }
  const appConfig = lastKnownConfig.app_config[appType];
  if (!appConfig) {
    console.warn(`No app config for type ${appType}`);
    return [];
  }
  if (!appConfig.interpreters) {
    console.warn(`No interpreters configured for type ${appType}`);
    return [];
  }
  return appConfig.interpreters;
};

export const findDashboardConnector = (
  connectorTest: (connector: Interpreter) => boolean
): DashboardInterpreter | undefined =>
  (getInterpreters(AppType.dashboard) as DashboardInterpreter[]).find(connectorTest);

export const findBrowserConnector = (
  connectorTest: (connector: Interpreter) => boolean
): BrowserInterpreter | undefined =>
  (getInterpreters(AppType.browser) as BrowserInterpreter[]).find(connectorTest);

export const findEditorConnector = (
  connectorTest: (connector: Interpreter) => boolean
): EditorInterpreter | undefined =>
  (getInterpreters(AppType.editor) as EditorInterpreter[]).find(connectorTest);

export const filterEditorConnectors = (
  connectorTest: (connector: Interpreter) => boolean
): EditorInterpreter[] | undefined =>
  (getInterpreters(AppType.editor) as EditorInterpreter[]).filter(connectorTest);

const rootPathRegex = /.*%3A%2F%2F(.+)$/;

/**
 * This takes the initial path from the "browser" config, used in cases where the users can't access '/'
 * for abfs etc.
 */
export const getRootFilePath = (connector: BrowserInterpreter): string => {
  if (!connector || connector.type === 'hdfs') {
    return '';
  }
  const match = connector.page.match(rootPathRegex);
  if (match) {
    return match[1] + '/';
  }

  return '';
};

huePubSub.subscribe(REFRESH_CONFIG_EVENT, refreshConfig);

// TODO: Replace GET_KNOWN_CONFIG_EVENT pubSub with sync getKnownConfig const
huePubSub.subscribe(GET_KNOWN_CONFIG_EVENT, (callback?: (appConfig: HueConfig) => void) => {
  if (lastConfigPromise && callback) {
    lastConfigPromise.then(callback).catch(callback);
  }
});

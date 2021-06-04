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

import { post } from 'api/utils';
import * as URLS from 'api/urls';
import {
  CONFIG_REFRESHED_TOPIC,
  ConfigRefreshedEvent,
  GET_KNOWN_CONFIG_TOPIC,
  GetKnownConfigEvent,
  REFRESH_CONFIG_TOPIC
} from './events';
import {
  AppType,
  BrowserInterpreter,
  DashboardInterpreter,
  EditorInterpreter,
  HueConfig,
  Interpreter,
  SchedulerInterpreter
} from './types';
import huePubSub from 'utils/huePubSub';

interface InterpreterMap {
  [AppType.browser]: BrowserInterpreter;
  [AppType.editor]: EditorInterpreter;
  [AppType.dashboard]: DashboardInterpreter;
  [AppType.scheduler]: SchedulerInterpreter;
  [AppType.sdkapps]: Interpreter;
}

type ConnectorTest<T extends keyof InterpreterMap> = (connector: InterpreterMap[T]) => boolean;

let lastConfigPromise: Promise<HueConfig> | undefined;
let lastKnownConfig: HueConfig | undefined;

export const refreshConfig = async (): Promise<HueConfig> => {
  lastConfigPromise = new Promise<HueConfig>(async (resolve, reject) => {
    try {
      const apiResponse = await post<HueConfig>(URLS.FETCH_CONFIG_API, {}, { silenceErrors: true });
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
      huePubSub.publish<ConfigRefreshedEvent>(CONFIG_REFRESHED_TOPIC, config);
    })
    .catch(() => {
      huePubSub.publish<ConfigRefreshedEvent>(CONFIG_REFRESHED_TOPIC);
    });

  return lastConfigPromise;
};

export const getLastKnownConfig = (): HueConfig | undefined => lastKnownConfig;

export const getConfig = async (): Promise<HueConfig> => getLastKnownConfig() || refreshConfig();

const getInterpreters = <T extends keyof InterpreterMap>(appType: T): InterpreterMap[T][] => {
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
  return appConfig.interpreters as InterpreterMap[T][];
};

const findConnector = <T extends keyof InterpreterMap>(
  appType: T,
  connectorTest: ConnectorTest<T>
): InterpreterMap[T] | undefined => getInterpreters(appType).find(connectorTest);

const filterConnector = <T extends keyof InterpreterMap>(
  appType: T,
  connectorTest: ConnectorTest<T>
): InterpreterMap[T][] => getInterpreters(appType).filter(connectorTest);

export const findDashboardConnector = (
  connectorTest: ConnectorTest<AppType.dashboard>
): DashboardInterpreter | undefined => findConnector(AppType.dashboard, connectorTest);

export const findBrowserConnector = (
  connectorTest: ConnectorTest<AppType.browser>
): BrowserInterpreter | undefined => findConnector(AppType.browser, connectorTest);

export const findEditorConnector = (
  connectorTest: ConnectorTest<AppType.editor>
): EditorInterpreter | undefined => findConnector(AppType.editor, connectorTest);

export const filterBrowserConnectors = (
  connectorTest: ConnectorTest<AppType.browser>
): BrowserInterpreter[] => filterConnector(AppType.browser, connectorTest);

export const filterEditorConnectors = (
  connectorTest: ConnectorTest<AppType.editor>
): EditorInterpreter[] => filterConnector(AppType.editor, connectorTest);

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

huePubSub.subscribe(REFRESH_CONFIG_TOPIC, refreshConfig);

// TODO: Replace GET_KNOWN_CONFIG_TOPIC pubSub with sync getKnownConfig const
huePubSub.subscribe<GetKnownConfigEvent>(GET_KNOWN_CONFIG_TOPIC, (callback?) => {
  if (lastConfigPromise && callback) {
    lastConfigPromise.then(callback).catch(callback);
  }
});

export default {
  refreshConfig,
  getInterpreters,
  getLastKnownConfig,
  getRootFilePath,
  findBrowserConnector,
  findDashboardConnector,
  findEditorConnector
};

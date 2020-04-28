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
import $ from 'jquery';

import apiHelper from 'api/apiHelper';
import huePubSub from 'utils/huePubSub';

export const REFRESH_CONFIG_EVENT = 'cluster.config.refresh.config';
export const CONFIG_REFRESHED_EVENT = 'cluster.config.set.config';
export const GET_KNOWN_CONFIG_EVENT = 'cluster.config.get.config';

let lastConfigPromise = undefined;
let lastKnownConfig = undefined;

export const refreshConfig = async () => {
  lastConfigPromise = new Promise((resolve, reject) => {
    apiHelper
      .getClusterConfig()
      .done(data => {
        if (data.status === 0) {
          lastKnownConfig = data;
          resolve(data);
        } else {
          $(document).trigger('error', data.message);
          reject();
        }
      })
      .fail(reject);
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

const validConnectorConfig = config => {
  if (
    !config ||
    !config.app_config ||
    !config.app_config.editor ||
    !config.app_config.editor.interpreters
  ) {
    console.error('No "interpreters" attribute present in the config.');
    return false;
  }
  return true;
};

export const findConnector = connectorTest => {
  if (validConnectorConfig(lastKnownConfig)) {
    const connectors = lastKnownConfig.app_config.editor.interpreters;
    return connectors.find(connectorTest);
  }
};

export const filterConnectors = connectorTest => {
  if (validConnectorConfig(lastKnownConfig)) {
    const connectors = lastKnownConfig.app_config.editor.interpreters;
    return connectors.filter(connectorTest);
  }
  return [];
};

huePubSub.subscribe(REFRESH_CONFIG_EVENT, refreshConfig);

// TODO: Replace GET_KNOWN_CONFIG_EVENT pubSub with sync getKnownConfig const
huePubSub.subscribe(GET_KNOWN_CONFIG_EVENT, callback => {
  if (lastConfigPromise && callback) {
    lastConfigPromise.then(callback).catch(callback);
  }
});

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

const refreshConfig = () => {
  lastConfigPromise = new Promise((resolve, reject) => {
    apiHelper
      .getClusterConfig()
      .done(data => {
        if (data.status === 0) {
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
};

huePubSub.subscribe(REFRESH_CONFIG_EVENT, refreshConfig);

huePubSub.subscribe(GET_KNOWN_CONFIG_EVENT, callback => {
  if (lastConfigPromise && callback) {
    lastConfigPromise.then(callback).catch(callback);
  }
});

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

// Based on original pub/sub implementation from http://davidwalsh.name/pubsub-javascript

/* eslint-disable @typescript-eslint/no-explicit-any */

type listener = (data: any) => void;

enum PubSubState {
  RUNNING,
  PAUSED
}

const topics: {
  [topic: string]: {
    listener: listener;
    app?: string;
    state: PubSubState;
  }[];
} = {};

const hOP = topics.hasOwnProperty;

export interface HueSubscription {
  remove: () => void;
}

const subscribe = (topic: string, listener: listener, app?: string): HueSubscription => {
  if (!hOP.call(topics, topic)) {
    topics[topic] = [];
  }

  const index =
    topics[topic].push({
      listener: listener,
      app: app,
      state: PubSubState.RUNNING
    }) - 1;

  return {
    remove: () => {
      delete topics[topic][index];
    }
  };
};

const removeAll = (topic: string): void => {
  topics[topic] = [];
};

// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
const publish = (topic: string, info?: any): void => {
  if (!hOP.call(topics, topic)) {
    return;
  }

  topics[topic].forEach(item => {
    if (item.state === PubSubState.RUNNING) {
      item.listener(info);
    }
  });
};

const subscribeOnce = (topic: string, listener: listener, app: string): HueSubscription => {
  const ephemeral = subscribe(
    topic,
    arg => {
      listener(arg);
      ephemeral.remove();
    },
    app
  );
  return ephemeral;
};

const getTopics = (): typeof topics => topics;

const setStatusForApp = (state: PubSubState, app?: string): void => {
  if (app) {
    Object.keys(topics).forEach(topicName => {
      topics[topicName].forEach(topic => {
        if (topic.app && (topic.app === app || topic.app.split('-')[0] === app)) {
          topic.state = state;
        }
      });
    });
  }
};

const pauseAppSubscribers = (app?: string): void => {
  setStatusForApp(PubSubState.PAUSED, app);
};

const resumeAppSubscribers = (app?: string): void => {
  setStatusForApp(PubSubState.RUNNING, app);
};

const clearAppSubscribers = (app?: string): void => {
  if (app) {
    Object.keys(topics).forEach(topicName => {
      topics[topicName] = topics[topicName].filter(obj => {
        return obj.app !== app;
      });
    });
  }
};

export default {
  clearAppSubscribers,
  getTopics,
  pauseAppSubscribers,
  publish,
  removeAll,
  resumeAppSubscribers,
  subscribe,
  subscribeOnce
};

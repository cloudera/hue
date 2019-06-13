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

const topics = {};
const hOP = topics.hasOwnProperty;

const huePubSub = {
  subscribe: function(topic, listener, app) {
    if (!hOP.call(topics, topic)) {
      topics[topic] = [];
    }

    const index =
      topics[topic].push({
        listener: listener,
        app: app,
        status: 'running'
      }) - 1;

    return {
      remove: function() {
        delete topics[topic][index];
      }
    };
  },
  removeAll: function(topic) {
    topics[topic] = [];
  },
  subscribeOnce: function(topic, listener, app) {
    const ephemeral = this.subscribe(
      topic,
      function() {
        listener.apply(listener, arguments);
        ephemeral.remove();
      },
      app
    );
  },
  publish: function(topic, info) {
    if (!hOP.call(topics, topic)) {
      return;
    }

    topics[topic].forEach(item => {
      if (item.status === 'running') {
        item.listener(info);
      }
    });
  },
  getTopics: function() {
    return topics;
  },
  pauseAppSubscribers: function(app) {
    if (app) {
      Object.keys(topics).forEach(topicName => {
        topics[topicName].forEach(topic => {
          if (
            typeof topic.app !== 'undefined' &&
            topic.app !== null &&
            (topic.app === app || topic.app.split('-')[0] === app)
          ) {
            topic.status = 'paused';
          }
        });
      });
    }
  },
  resumeAppSubscribers: function(app) {
    if (app) {
      Object.keys(topics).forEach(topicName => {
        topics[topicName].forEach(topic => {
          if (
            typeof topic.app !== 'undefined' &&
            topic.app !== null &&
            (topic.app === app || topic.app.split('-')[0] === app)
          ) {
            topic.status = 'running';
          }
        });
      });
    }
  },
  clearAppSubscribers: function(app) {
    if (app) {
      Object.keys(topics).forEach(topicName => {
        topics[topicName] = topics[topicName].filter(obj => {
          return obj.app !== app;
        });
      });
    }
  }
};

export default huePubSub;

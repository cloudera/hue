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


function ClusterConfig(params) {
  var self = this;

  self.clusterConfig = undefined;
  self.loading = true;

  var refreshConfig = function () {
    window.apiHelper.getClusterConfig(params).done(function (data) {
      if (data.status === 0) {
        self.loading = false;
        self.clusterConfig = data;
        huePubSub.publish('cluster.config.set.config', self.clusterConfig);
      } else {
        $(document).trigger("error", data.message);
        huePubSub.publish('cluster.config.set.config');
      }
    }).fail(function () {
      huePubSub.publish('clustser.config.set.config');
    }).always(function () {
      self.loading = false;
    });
  };

  huePubSub.subscribe('cluster.config.refresh.config', refreshConfig);

  if (window.location.pathname.indexOf('/accounts/login') === -1) {
    refreshConfig();
  }

  huePubSub.subscribe('cluster.config.get.config', function (callback) {
    if (!self.loading) {
      if (callback) {
        callback(self.clusterConfig)
      } else {
        huePubSub.publish('cluster.config.set.config', self.clusterConfig);
      }
    } else if (callback) {
      huePubSub.subscribeOnce('cluster.config.set.config', function () {
        callback(self.clusterConfig)
      })
    }
  });
}

new ClusterConfig();

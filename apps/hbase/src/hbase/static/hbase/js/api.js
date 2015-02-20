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

var API = {
  //base querying function
  //query(functionName, ClusterName, arg0, arg1).done(callback)
  query: function() {
    // all url building should be in this function
    var url = "/hbase/api";
    var $_POST = {};
    for(var i=0;i<arguments.length;i++) {
      if (arguments[i] == null)
        arguments[i] = "";
      arguments[i] = arguments[i] + "";
      var key = arguments[i].slice(0, 15);
      if (key == "hbase-post-key-") {
        key += Object.keys($_POST).length;
        $_POST[key] = arguments[i].slice(15);
        arguments[i] = key;
      }
      url += '/' + encodeURIComponent(arguments[i]);
    }
    var queryObject = {url:url, method:'POST', startTime: new Date().getTime(), status:'running...'};
    var handler = $.post(url, $_POST).error(function(response) {
      $(document).trigger("error", JSON.parse(response.responseText).message);
    });
    var doneHandle = handler.done;
    handler.done = function() {
      var cb = arguments[0];
      return doneHandle.apply(handler, [function(data)
      {
        app.views.tabledata.truncateLimit(data.limit);
        data = data.data;
        return cb(data);
      }].concat(Array.prototype.slice.call(arguments).slice(1)));
    };
    return handler;
  },
  queryArray: function(action, args) {
    return API.query.apply(this, [action].concat(args));
  },
  //function,arg0,arg1, queries the current cluster
  queryCluster: function() {
    var args = Array.prototype.slice.call(arguments);
    args.splice(1, 0, app.cluster());
    return API.query.apply(this, args);
  },
  queryTable: function() {
    var args = Array.prototype.slice.call(arguments);
    args.splice(1, 0, app.views.tabledata.name());
    return API.queryCluster.apply(this, args);
  },
  //functions to abstract away API structure, in case API changes:
  //only have function name, data, and callbacks. no URL or api-facing.
  createTable: function(cluster, tableName, columns, callback) {
     return API.query('createTable', cluster, tableName, columns).done(callback);
  },
  getTableNames: function(cluster, callback) {
    return API.query('getTableNames', cluster).done(callback);
  },
  getTableList: function(cluster, callback) {
    return API.query('getTableList', cluster).done(callback);
  }
}
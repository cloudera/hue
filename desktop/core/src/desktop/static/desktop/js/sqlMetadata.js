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

var SqlMetadata = (function () {

  function SqlMetadata (options) {
    var self = this;
    self.loaded = false;
    self.hasErrors = false;

    self.sourceType = options.sourceType;
    self.path = options.path;

    self.meta;
  }

  SqlMetadata.prototype.isMap = function () {
    var self = this;
    return self.meta && self.meta.type === 'map';
  };

  SqlMetadata.prototype.isStruct = function () {
    var self = this;
    return self.meta && self.meta.type === 'struct';
  };

  SqlMetadata.prototype.isArray = function () {
    var self = this;
    return self.meta && self.meta.type === 'array';
  };

  SqlMetadata.prototype.load = function (silenceErrors, cachedOnly) {
    var self = this;
    var promise = $.Deferred();
    ApiHelper.getInstance().fetchSqlMetadata({
      sourceType: self.sourceType,
      path: self.path,
      silenceErrors: silenceErrors,
      cachedOnly: cachedOnly
    })
    .done(function (data) {
      self.meta = data;
      self.loaded = true;
      promise.resolve(self);
    }).fail(function (message) {
      self.hasErrors = true;
      promise.reject(message);
    });

    return promise;
  };

  return SqlMetadata;
})();
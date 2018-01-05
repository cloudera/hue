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

    self.sourceMeta = undefined;
    self.navigatorMeta = undefined;
    self.commentObservable = undefined;

    self.lastNavigatorPromise = undefined;
    self.lastSourcePromise = undefined;

    self.silenceErrors = options.silenceErrors;
    self.cachedOnly = options.cachedOnly;
  }

  var refreshCommentObservable = function (sqlMeta) {
    if (sqlMeta.commentObservable) {
      if (HAS_NAVIGATOR) {
        sqlMeta.getNavigatorMeta().done(function () {
          if (sqlMeta.navigatorMeta && sqlMeta.navigatorMeta.entity) {
            sqlMeta.commentObservable(sqlMeta.navigatorMeta.entity.description || sqlMeta.navigatorMeta.entity.originalDescription);
          } else {
            sqlMeta.getSourceMeta().done(function () {
              sqlMeta.commentObservable(sqlMeta.sourceMeta ? (sqlMeta.sourceMeta.comment || '') : '');
            });
          }
        })
      } else {
        sqlMeta.getSourceMeta().done(function () {
          sqlMeta.commentObservable(sqlMeta.sourceMeta ? (sqlMeta.sourceMeta.comment || '') : '');
        });
      }
    }
  };

  SqlMetadata.prototype.getCommentObservable = function () {
    var self = this;
    if (!self.commentObservable) {
      self.commentObservable = ko.observable();
      refreshCommentObservable(self);
    }
    return self.commentObservable;
  };

  SqlMetadata.prototype.getSourceMeta = function () {
    var self = this;
    return self.lastSourcePromise || self.loadSourceMeta()
  };

  SqlMetadata.prototype.getNavigatorMeta = function () {
    var self = this;
    return self.lastNavigatorPromise || self.loadNavigatorMeta()
  };

  SqlMetadata.prototype.isDatabase = function () {
    var self = this;
    return self.path.length === 1;
  };

  SqlMetadata.prototype.isTable = function () {
    var self = this;
    return self.sourceMeta && typeof self.sourceMeta.columns !== 'undefined' && !self.sourceMeta.is_view;
  };

  SqlMetadata.prototype.isView = function () {
    var self = this;
    return self.sourceMeta && typeof self.sourceMeta.columns !== 'undefined' && self.sourceMeta.is_view;
  };

  SqlMetadata.prototype.isField = function () {
    var self = this;
    return self.path.length > 2
  };

  SqlMetadata.prototype.isMap = function () {
    var self = this;
    return self.sourceMeta && self.sourceMeta.type === 'map';
  };

  SqlMetadata.prototype.isStruct = function () {
    var self = this;
    return self.sourceMeta && self.sourceMeta.type === 'struct';
  };

  SqlMetadata.prototype.isArray = function () {
    var self = this;
    return self.sourceMeta && self.sourceMeta.type === 'array';
  };

  SqlMetadata.prototype.loadSourceMeta = function () {
    var self = this;
    self.lastSourcePromise = $.Deferred();
    ApiHelper.getInstance().fetchSourceMetadata({
      sourceType: self.sourceType,
      path: self.path,
      silenceErrors: self.silenceErrors,
      cachedOnly: self.cachedOnly
    }).done(function (data) {
      self.sourceMeta = data;
      self.loaded = true;
      self.lastSourcePromise.resolve(self);
    }).fail(function (message) {
      self.hasErrors = true;
      self.lastSourcePromise.reject(message);
    });

    return self.lastSourcePromise.promise();
  };
  
  SqlMetadata.prototype.loadNavigatorMeta = function () {
    var self = this;
    self.lastNavigatorPromise = $.Deferred();
    if (HAS_NAVIGATOR) {
      ApiHelper.getInstance().fetchNavigatorMetadata({
        path: self.path,
        silenceErrors: self.silenceErrors,
      }).done(function (data) {
        self.navigatorMeta = data;
        self.lastNavigatorPromise.resolve(self);
      }).fail(self.lastNavigatorPromise.reject);
    } else {
      self.lastNavigatorPromise.resolve();
    }
    return self.lastNavigatorPromise.promise();
  };

  return SqlMetadata;
})();
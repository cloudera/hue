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

var SourceContext = (function () {
  function SourceContext(name) {
    var self = this;
    self.name = name;
  }

  return SourceContext;
})();

var contextHelper = (function () {

  function ContextHelper () {
    var self = this;
    self.sourceContexts = [];

    if (window.IS_EMBEDDED && window.embeddedSourceContext) {
      self.sourceContexts.push(new SourceContext(window.embeddedSourceContext))
    } else {
      self.sourceContexts.push(new SourceContext('defaultNamespace')) // TODO: Drop when we fetch from backend
    }
  }

  ContextHelper.prototype.getSourceContexts = function () {
    var self = this;
    var deferred = $.Deferred();

    deferred.resolve(self.sourceContexts);

    return deferred.promise();
  };

  return new ContextHelper(); // Singleton
})();
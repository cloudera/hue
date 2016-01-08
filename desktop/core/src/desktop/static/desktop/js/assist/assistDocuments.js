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

(function (root, factory) {
  if(typeof define === "function" && define.amd) {
    define(['knockout'], factory);
  } else {
    root.AssistDocuments = factory(ko);
  }
}(this, function (ko) {

  /**
   * @param {object} definition
   * @constructor
   */
  function AssistDocument(definition) {
    var self = this;
    self.definition = definition;
  }

  /**
   * @param {AssistDocument[]} documents
   * @constructor
   */
  function AssistDocumentType(name, type, documents) {
    var self = this;
    self.name = name || type;
    self.type = type;
    self.documents = documents;
    self.open = ko.observable(false);
  }

  /**
   * @param {AssistHelper} assistHelper
   * @param {object} i18n
   * @constructor
   */
  function AssistDocuments (assistHelper, i18n) {
    var self = this;
    self.assistHelper = assistHelper;
    self.i18n = i18n;
    self.loading = ko.observable(false);
    self.availableTypes = ko.observableArray();
  }

  AssistDocuments.prototype.load = function() {
    var self = this;
    if (self.loading()) {
      return;
    }
    self.loading(true);

    var successCallback = function(data) {
      var documentsByType = {};
      $.each(data.documents, function (idx, document) {
        if (!documentsByType[document.type]) {
          documentsByType[document.type] = [];
        }
        documentsByType[document.type].push(new AssistDocument(document));
      });

      var types = [];
      $.each(documentsByType, function (key, value) {
        types.push(new AssistDocumentType(self.i18n.documentTypes[key], key, value))
      });

      self.availableTypes(types);
      self.loading(false);
    };

    var errorCallback = function () {
      self.loading(false);
    };

    self.assistHelper.fetchDocuments({
      successCallback: successCallback,
      errorCallback: errorCallback
    });
  };

  return AssistDocuments;
}));

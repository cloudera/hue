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

var DocumentChooser = (function () {

  function DocumentChooser (options) {
    var self = this;

    self.documentStore = {};
    self.documentsAutocompleteSource = function (request, callback) {
      var TYPE_MAP = {
        'hive': 'query-hive',
        'impala': 'query-impala',
        'java': 'query-java',
        'spark': 'query-spark2',
        'pig': 'query-pig',
        'sqoop': 'query-sqoop1',
        'distcp-doc': 'query-distcp',
        'mapreduce-doc': 'query-mapreduce'
      }
      var type = 'query-hive';
      if (this.options && typeof this.options.type === 'function') {
        type = TYPE_MAP[this.options.type()] ? TYPE_MAP[this.options.type()] : this.options.type();
      }

      $.get('/desktop/api2/docs/', {
        type: type,
        text: request.term,
        include_trashed: false,
        limit: 100
      }, function (data) {
        if (data && data.documents) {
          var docs = [];
          if (data.documents.length > 0) {
            $.each(data.documents, function (index, doc) {
              docs.push({
                data: {name: doc.name, type: doc.type, description: doc.description},
                value: doc.uuid,
                label: doc.name
              });
              self.documentStore[doc.uuid] = ko.mapping.fromJS(doc);
            });
          } else {
            docs.push({
              data: {name: 'No matches found', description: ''},
              label: 'No matches found',
              value: ''
            });
          }
          callback(docs);
        }
      });
    };
    
    self.getDocumentById = function (type, uuid) {
      return self.documentStore[uuid];
    };
    
    self.setAssociatedDocument = function (uuid, associatedDocument) {
      if (self.documentStore[uuid]){
        associatedDocument(self.documentStore[uuid]);
      }

      $.get('/desktop/api2/doc/', {
        uuid: uuid
      }, function(data){
        if (data && data.document){
          associatedDocument(ko.mapping.fromJS(data.document));
          self.documentStore[uuid] = associatedDocument();
        }
      });
    }
  }

  return DocumentChooser;
})();

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
import ko from 'knockout';

import apiHelper from 'api/apiHelper';

const TYPE_MAP = {
  hive: 'query-hive',
  impala: 'query-impala',
  java: 'query-java',
  spark: 'query-spark2',
  pig: 'query-pig',
  sqoop: 'query-sqoop1',
  'distcp-doc': 'query-distcp',
  'shell-doc': 'query-shell',
  'mapreduce-doc': 'query-mapreduce',
  'hive-document-widget': 'query-hive',
  'impala-document-widget': 'query-impala',
  'java-document-widget': 'query-java',
  'spark-document-widget': 'query-spark2',
  'pig-document-widget': 'query-pig',
  'sqoop-document-widget': 'query-sqoop1',
  'distcp-document-widget': 'query-distcp',
  'shell-document-widget': 'query-shell',
  'mapreduce-document-widget': 'query-mapreduce'
};

ko.bindingHandlers.documentChooser = {
  init: function(element, valueAccessor) {
    const options = valueAccessor();
    let type = 'query-hive';

    if (options.type) {
      let tempType = ko.unwrap(options.type);
      if (tempType === 'function') {
        tempType = tempType();
      }
      type = TYPE_MAP[tempType] ? TYPE_MAP[tempType] : tempType;
    }
    let firstLoad = false;

    $(element).selectize({
      valueField: 'uuid',
      labelField: 'name',
      searchField: 'name',
      options: [],
      create: false,
      preload: true,
      dropdownParent: 'body',
      render: {
        option: function(item, escape) {
          return (
            '<div>' +
            '<strong>' +
            escape(item.name) +
            '</strong><br>' +
            '<span class="muted">' +
            escape(item.description) +
            '</span>' +
            '</div>'
          );
        }
      },
      load: function(query, callback) {
        if (query === '' && options.value && !firstLoad) {
          firstLoad = true;
        }
        apiHelper.searchDocuments({
          type: type,
          text: query,
          include_trashed: false,
          limit: 100,
          successCallback: function(data) {
            callback(data.documents);
          }
        });
      },
      onChange: function(val) {
        if (options.value) {
          options.value(val);
        }
        if (options.document) {
          options.document(this.options[val]);
        }
        if (options.mappedDocument) {
          options.mappedDocument(ko.mapping.fromJS(this.options[val]));
        }
      },
      onLoad: function() {
        if (options.value) {
          this.setValue(options.value());
        }
        if (options.loading) {
          options.loading(false);
        }
      }
    });
  },

  update: function(element, valueAccessor) {
    const options = valueAccessor();
    if (options.value) {
      element.selectize.setValue(options.value());
    }
    if (options.dependentValue && options.dependentValue() !== '') {
      element.selectize.setValue(options.dependentValue());
      options.dependentValue('');
    }
  }
};

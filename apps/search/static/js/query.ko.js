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


function QueryViewModel(json_tags, json_docs) {
  var self = this;

  var MOCK_TAGS = {
    'history': {'name': 'History', 'id': 1, 'docs': [1], 'type': 'history'},
    'trash': {'name': 'Trash', 'id': 3, 'docs': [2]},
    'mine': [
      {'name': 'default', 'id': 2, 'docs': [3]},
      {'name': 'web', 'id': 3, 'docs': [3]}
    ],
    'notmine': [
      {'name': 'romain', 'projects': [
        {'name': 'example', 'id': 20, 'docs': [10]},
        {'name': 'ex2', 'id': 30, 'docs': [10, 11]}
      ]},
      {'name': 'pai', 'projects': [
        {'name': 'example2', 'id': 20, 'docs': [10]}
      ]}
    ]
  };

  var ALL_DOCUMENTS = json_docs;
  self.tags = ko.mapping.fromJS(json_tags);
  self.documents = ko.observableArray([]);

  self.editTagsToCreate = ko.observableArray([]);
  self.editTagsToDelete = ko.observableArray([]);

  self.selectedTag = ko.observable("");

  self.trash = ko.computed(function () {
    return self.tags.trash;
  });

  self.history = ko.computed(function () {
    return self.tags.history;
  });
}

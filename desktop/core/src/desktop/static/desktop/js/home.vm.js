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


function HomeViewModel(json_tags, json_docs) {
  var self = this;

  var ALL_DOCUMENTS = json_docs;
  self.tags = ko.mapping.fromJS(json_tags);
  self.documents = ko.observableArray([]);
  self.page = ko.observable(1);
  self.documentsPerPage = ko.observable(50);

  self.selectedTag = ko.observable({});
  self.selectedTagForDelete = ko.observable({
    name: ''
  });

  self.trash = ko.computed(function () {
    return self.tags.trash;
  });

  self.history = ko.computed(function () {
    return self.tags.history;
  });

  self.myTags = ko.computed(function () {
    return self.tags.mine();
  });

  self.sharedTags = ko.computed(function () {
    return self.tags.notmine();
  });

  self.allTags = ko.computed(function () {
    var _all = [];
    _all.push(self.tags.history);
    _all.push(self.tags.trash);
    _all = _all.concat(self.tags.mine());
    _all = _all.concat(self.tags.notmine());
    return _all;
  });

  self.renderableDocuments = ko.computed(function () {
    return self.documents().slice((self.page() * 1 - 1) * self.documentsPerPage(), (self.page() * self.documentsPerPage()) - 1);
  });

  self.totalPages = ko.computed(function () {
    return Math.ceil(self.documents().length / self.documentsPerPage());
  });

  self.hasPrevious = ko.computed(function () {
    return self.page() > 1;
  });

  self.hasNext = ko.computed(function () {
    return self.page() < self.totalPages();
  });

  self.page.subscribe(function (value) {
    if (isNaN(value * 1)) {
      self.page(1);
    }
    if (value > self.totalPages()) {
      self.page(self.totalPages());
    }
    if (value < 1) {
      self.page(1);
    }
  });

  self.nextPage = function () {
    if (self.hasNext()) {
      self.page(self.page() + 1);
    }
  }

  self.previousPage = function () {
    if (self.hasPrevious()) {
      self.page(self.page() - 1);
    }
  }

  self.documents.subscribe(function () {
    self.page(1);
  });

  self.getTagById = function (tagId) {
    var _tag = null;
    $.each(self.allTags(), function (id, tag) {
      if (tag.hasOwnProperty("id") && tag.id() == tagId) {
        _tag = tag;
      }
      if (tag.hasOwnProperty("projects")) {
        $.each(tag.projects(), function (iid, itag) {
          if (itag.hasOwnProperty("id") && itag.id() == tagId) {
            _tag = itag;
          }
        });
      }
    });
    return _tag;
  }

  self.getDocById = function (docId) {
    var _doc = null;
    $.each(ALL_DOCUMENTS, function (id, doc) {
      if (doc.id == docId) {
        _doc = doc;
      }
    });
    return _doc;
  }

  self.updateDoc = function (doc) {
    $.each(ALL_DOCUMENTS, function (id, iDoc) {
      if (iDoc.id == doc.id) {
        ALL_DOCUMENTS[id] = doc;

        $(self.tags.mine()).each(function (iCnt, tag) {
          var _removeDocFromTag = true;
          $(doc.tags).each(function (cnt, item) {
            if (tag.id() == item.id && tag.docs().indexOf(doc.id) == -1) {
              tag.docs().push(doc.id);
              tag.docs.valueHasMutated();
            }
            if (tag.docs().indexOf(doc.id) > -1 && tag.id() == item.id) {
              _removeDocFromTag = false;
            }
          });
          if (_removeDocFromTag) {
            if (tag.docs().indexOf(doc.id) != -1) {
              tag.docs().splice(tag.docs().indexOf(doc.id), 1);
              tag.docs.valueHasMutated();
            }
          }
        });
      }
    });
    self.filterDocs(self.selectedTag());
  }

  self.filterDocs = function (tag) {
    self.documents.removeAll();
    self.selectedTag(tag);
    var _docs = [];
    $.each(ALL_DOCUMENTS, function (id, doc) {
      if (tag.docs().indexOf(parseInt(id)) != -1) { // Beware, keys are strings in js
        _docs.push(doc);
      }
    });
    self.documents(_docs);
  }

  self.searchDocs = function (query) {
    self.documents.removeAll();
    var _docs = [];
    $.each(ALL_DOCUMENTS, function (id, doc) {
      if (self.selectedTag().docs().indexOf(parseInt(id)) != -1) { // Beware, keys are strings in js
        var _bigString = doc.name + doc.description + doc.owner + doc.lastModified;
        $.each(doc.tags, function (cnt, tag) {
          _bigString += tag.name;
        })
        if (_bigString.toLowerCase().indexOf($.trim(query.toLowerCase())) > -1) {
          _docs.push(doc);
        }
      }
    });
    self.documents(_docs);
  }

  self.createTag = function (tag_json) {
    var mapped_tag = ko.mapping.fromJS(tag_json);
    self.tags.mine.push(mapped_tag);
  }

  self.deleteTag = function (tag) {
    self.tags.mine.remove(tag);
  }
}

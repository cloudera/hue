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
    define([
      'knockout',
      'desktop/js/assist/assistHelper',
      'knockout-mapping'
    ], factory);
  } else {
    root.HomeViewModel = factory(ko, assistHelper);
  }
}(this, function (ko, AssistHelper) {

  function HomeViewModel(options) {
    var self = this;

    self.assistHelper = AssistHelper.getInstance(options);
    self.isLeftPanelVisible = ko.observable();
    self.assistHelper.withTotalStorage('assist', 'assist_panel_visible', self.isLeftPanelVisible, true);

    self.documents = ko.observableArray([]);
    self.path = ko.mapping.fromJS('/');
    self.mkdirFormPath = ko.observable('');
    self.deleteFormPath = ko.observable('');
    self.shareFormDocId = ko.observable('');
    self.exportFormDocIds = ko.observable('');

    self.page = ko.observable(1);
    self.documentsPerPage = ko.observable(50);

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
    };

    self.previousPage = function () {
      if (self.hasPrevious()) {
        self.page(self.page() - 1);
      }
    };

    self.documents.subscribe(function () {
      self.page(1);
    });


    self.loadDocuments = function(path) {
      $.get("/desktop/api2/docs2/", {
       path: path
      }, function(data) {
        self.path(path);
        self.documents(data.documents);
      }).fail(function (xhr) {
        $(document).trigger("error", xhr.responseText);
      });
    };

    self.mkdir = function() {
      $.post("/desktop/api2/doc/mkdir", {
        parent_path: ko.mapping.toJSON(self.path),
        name: ko.mapping.toJSON(self.mkdirFormPath)
      }, function (data) {
        if (data.status == 0) {
          self.loadDocuments(self.path()); // TODO proper refresh
          self.mkdirFormPath('');
        }
        else {
          $(document).trigger("error", data.message);
        }
      }).fail(function (xhr) {
        $(document).trigger("error", xhr.responseText);
      });
    };

    self.deleteDocument = function() {
      $.post("/desktop/api2/doc/delete", {
        doc_id: ko.mapping.toJSON(self.deleteFormPath),
        skip_trash: ko.mapping.toJSON(false)
      }, function (data) {
        if (data.status == 0) {
          self.loadDocuments(self.path()); // TODO proper refresh
          self.mkdirFormPath('');
        }
        else {
          $(document).trigger("error", data.message);
        }
      }).fail(function (xhr) {
        $(document).trigger("error", xhr.responseText);
      });
    };

    self.exportDocuments = function() {
      $('#export-documents').find('input[name=\'documents\']').val(ko.mapping.toJSON(self.exportFormDocIds().split(",")));
      $('#export-documents').find('form').submit();
    };
  }

  return HomeViewModel;
}));

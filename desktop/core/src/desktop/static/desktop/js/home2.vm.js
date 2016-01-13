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
      'desktop/js/documents/hueDirectory',
      'knockout-mapping'
    ], factory);
  } else {
    root.HomeViewModel = factory(ko, assistHelper, HueDirectory);
  }
}(this, function (ko, AssistHelper, HueDirectory) {

  function HomeViewModel(options) {
    var self = this;

    self.assistHelper = AssistHelper.getInstance(options);
    self.isLeftPanelVisible = ko.observable();
    self.assistHelper.withTotalStorage('assist', 'assist_panel_visible', self.isLeftPanelVisible, true);

    self.documents = ko.observableArray([]);

    self.currentDirectory = ko.observable(new HueDirectory({
      assistHelper: self.assistHelper,
      app: 'documents',
      definition: {
        name: '/'
      }
    }));

    self.currentDirectory().open();

    self.deleteFormPath = ko.observable('');
    self.shareFormDocId = ko.observable('');
    self.exportFormDocIds = ko.observable('');

    self.deleteDocument = function() {
      $.post("/desktop/api2/doc/delete", {
        doc_id: ko.mapping.toJSON(self.deleteFormPath),
        skip_trash: ko.mapping.toJSON(false)
      }, function (data) {
        if (data.status == 0) {
          self.currentDirectory().load();
        } else {
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

  HomeViewModel.prototype.openPath = function (path) {
    console.log(path);
  };

  return HomeViewModel;
}));

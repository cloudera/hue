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


var wizard = (function($) {
  var Wizard = koify.KOClass(function(options) {
    var self = this;
    var options = options || {};

    self.page_lookup = {};
    self.pages = ko.observableArray();
    self.index = ko.observable(0);
    self.page = ko.computed(function() {
      if (self.pages().length > 0 && self.index() < self.pages().length && self.index() >= 0) {
        return self.pages()[self.index()];
      } else {
        return null;
      }
    });
    self.hasNext = ko.computed(function() {
      var next_index = self.index() + 1;
      return self.pages().length > 0 && next_index < self.pages().length;
    });
    self.hasPrevious = ko.computed(function() {
      var previous_index = self.index() - 1;
      return self.pages().length > 0 && previous_index >= 0;
    });
    self.nextIndex = ko.computed(function() {
      if (self.hasNext()) {
        return self.index() + 1;
      } else {
        return -1;
      }
    });
    self.previousIndex = ko.computed(function() {
      if (self.hasPrevious()) {
        return self.index() - 1;
      } else {
        return -1;
      }
    });

    self.initialize(options);
  }, {
    initialize: function(options) {
      var self = this;
      self.options = options || {};
      if (self.options.pages) {
        self.pages(options.pages);
      }
      if (self.options.index) {
        self.index(self.options.index);
      }
    },
    addPage: function(page) {
      var self = this;
      self.page_lookup[page.identifier()] = self.pages().length;
      self.pages.push(page);
    },
    getIndex: function(identifier) {
      var self = this;
      return self.page_lookup[identifier];
    },
    clearPages: function() {
      var self = this;
      self.pages([]);
      self.index(0);
    }
  });

  var Page = koify.KOClass(function(options) {
    var self = this;
    var options = options || {};

    self.identifier = ko.observable();
    self.caption = ko.observable();
    self.description= ko.observable();
    self.template = ko.observable();
    self.node = ko.observable();

    self.initialize(options);
  }, {
    initialize: function(options) {
      var self = this;
      self.options = options || {};
      self.identifier(self.options.identifier);
      self.caption(self.options.caption);
      self.description(self.options.description);
      self.node(self.options.node);
      self.template(self.options.template);
    }
  });

  return {
    'Wizard': Wizard,
    'Page': Page
  };
})($);
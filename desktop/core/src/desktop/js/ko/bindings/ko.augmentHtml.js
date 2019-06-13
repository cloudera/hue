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

// TODO: less from bootstrap?

ko.bindingHandlers.augmentHtml = {
  render: function(element, valueAccessor) {
    const _val = ko.unwrap(valueAccessor());
    const _enc = $('<span>').html(_val);
    if (_enc.find('style').length > 0) {
      const parser = new less.Parser();
      $(_enc.find('style')).each((cnt, item) => {
        const _less = '.result-container {' + $(item).text() + '}';
        try {
          parser.parse(_less, (err, tree) => {
            $(item).text(tree.toCSS());
          });
        } catch (e) {}
      });
      $(element).html(_enc.html());
    } else {
      $(element).html(_val);
    }
  },
  init: function(element, valueAccessor, allBindingsAccessor, viewModel) {
    ko.bindingHandlers.augmentHtml.render(element, valueAccessor, allBindingsAccessor, viewModel);
  },
  update: function(element, valueAccessor, allBindingsAccessor, viewModel) {
    ko.bindingHandlers.augmentHtml.render(element, valueAccessor, allBindingsAccessor, viewModel);
  }
};

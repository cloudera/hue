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

// TODO: Depends on Ace

ko.bindingHandlers.readOnlyAce = {
  init: function(element) {
    $(element).css({
      'min-height': '250px'
    });
    const editor = ace.edit(element);
    editor.setOptions({
      readOnly: true,
      maxLines: Infinity
    });
    editor.setTheme($.totalStorage('hue.ace.theme') || 'ace/theme/hue');
    $(element).data('aceEditor', editor);
  },
  update: function(element, valueAccessor, allBindingsAccessor) {
    let value = ko.unwrap(valueAccessor());
    const options = ko.unwrap(allBindingsAccessor());
    $(element)
      .data('aceEditor')
      .getSession()
      .setMode('ace/mode/' + options.type || 'xml'); // e.g. xml, json...
    if (typeof value !== 'undefined' && value !== '') {
      // allows highlighting static code
      if (options.path) {
        value = value[options.path];
      }
      $(element)
        .data('aceEditor')
        .setValue(value, -1);
    }
  }
};

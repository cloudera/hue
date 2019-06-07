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

ko.bindingHandlers.solrChooser = {
  init: function(element, valueAccessor) {
    const self = $(element);
    self.val(valueAccessor()());

    function setPathFromAutocomplete(path) {
      self.val(path);
      valueAccessor()(path);
      self.blur();
    }

    self.on('blur', () => {
      valueAccessor()(self.val());
    });

    self.jHueGenericAutocomplete({
      showOnFocus: true,
      home: '/',
      serverType: 'SOLR',
      skipTables: true, // No notion of DB actually
      onPathChange: function(path) {
        setPathFromAutocomplete(path);
      },
      onEnter: function(el) {
        setPathFromAutocomplete(el.val());
      },
      onBlur: function() {
        if (self.val().lastIndexOf('.') === self.val().length - 1) {
          self.val(self.val().substr(0, self.val().length - 1));
        }
        valueAccessor()(self.val());
      }
    });
  }
};

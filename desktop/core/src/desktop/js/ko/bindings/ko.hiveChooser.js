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

ko.bindingHandlers.hiveChooser = {
  init: function(element, valueAccessor, allBindingsAccessor) {
    const self = $(element);
    let options = ko.unwrap(valueAccessor());
    let complexConfiguration = false;
    if (typeof options === 'function') {
      self.val(options());
    } else if (options && options.data) {
      self.val(options.data);
      complexConfiguration = true;
    } else {
      self.val(options);
    }

    if (complexConfiguration) {
      self.jHueGenericAutocomplete({
        showOnFocus: true,
        skipColumns: ko.unwrap(options.skipColumns),
        skipTables: ko.unwrap(options.skipTables),
        startingPath: options.database + '.',
        rewriteVal: true,
        onPathChange: options.onChange,
        namespace: ko.unwrap(options.namespace),
        compute: ko.unwrap(options.compute),
        searchEverywhere: ko.unwrap(options.searchEverywhere) || false,
        apiHelperUser: ko.unwrap(options.apiHelperUser) || '',
        apiHelperType: ko.unwrap(options.apiHelperType) || '',
        mainScrollable: ko.unwrap(options.mainScrollable) || $(window)
      });
    } else {
      options = allBindingsAccessor();

      const setPathFromAutocomplete = path => {
        self.val(path);
        valueAccessor()(path);
        self.blur();
      };

      self.on('blur', () => {
        if (!options.skipInvalids) {
          valueAccessor()(self.val());
        }
      });
      if (
        allBindingsAccessor().valueUpdate != null &&
        allBindingsAccessor().valueUpdate === 'afterkeydown'
      ) {
        self.on('keyup', () => {
          valueAccessor()(self.val());
        });
      }
      self.jHueGenericAutocomplete({
        showOnFocus: true,
        home: '/',
        skipColumns: ko.unwrap(options.skipColumns) || false,
        skipTables: ko.unwrap(options.skipTables) || false,
        namespace: ko.unwrap(options.namespace),
        compute: ko.unwrap(options.compute),
        pathChangeLevel: ko.unwrap(options.pathChangeLevel) || '',
        apiHelperUser: ko.unwrap(options.apiHelperUser) || '',
        apiHelperType: ko.unwrap(options.apiHelperType) || '',
        mainScrollable: ko.unwrap(options.mainScrollable) || $(window),
        onPathChange: function(path) {
          setPathFromAutocomplete(path);
        },
        onEnter: function(el) {
          if (!options.skipInvalids) {
            setPathFromAutocomplete(el.val());
          }
        },
        onBlur: function() {
          if (self.val().lastIndexOf('.') === self.val().length - 1) {
            self.val(self.val().substr(0, self.val().length - 1));
          }
          if (!options.skipInvalids) {
            valueAccessor()(self.val());
          }
        }
      });
    }
  }
};

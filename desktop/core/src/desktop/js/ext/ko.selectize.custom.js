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

// Based on https://gist.githubusercontent.com/xtranophilist/8001624/raw/ko_selectize.js

import $ from 'jquery';
import ko from 'knockout';

import I18n from 'utils/i18n';

var inject_binding = function (allBindings, key, value) {
  //https://github.com/knockout/knockout/pull/932#issuecomment-26547528
  return {
    has: function (bindingKey) {
      return (bindingKey == key) || allBindings.has(bindingKey);
    },
    get: function (bindingKey) {
      var binding = allBindings.get(bindingKey);
      if (bindingKey == key) {
        binding = binding ? [].concat(binding, value) : value;
      }
      return binding;
    }
  };
}

ko.bindingHandlers.browserAwareSelectize = {
  init: function (element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
    (window.isIE11 ? ko.bindingHandlers.options : ko.bindingHandlers.selectize).init.apply(null, arguments);
  },
  update: function (element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
    (window.isIE11 ? ko.bindingHandlers.options : ko.bindingHandlers.selectize).update.apply(null, arguments);
  }
}

ko.bindingHandlers.selectize = {
  init: function (element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
    if (typeof allBindingsAccessor.get('optionsCaption') == 'undefined')
      allBindingsAccessor = inject_binding(allBindingsAccessor, 'optionsCaption', I18n('Choose...'));

    ko.bindingHandlers.options.update(element, valueAccessor, allBindingsAccessor, viewModel, bindingContext);

    var options = {};

    if (allBindingsAccessor.get('optionsValue')) {
      options.valueField = allBindingsAccessor.get('optionsValue');
    }

    if (allBindingsAccessor.get('optionsText')) {
      options.labelField = allBindingsAccessor.get('optionsText'),
        options.searchField = allBindingsAccessor.get('optionsText')
    }

    if (allBindingsAccessor.has('selectizeOptions')) {
      var passed_options = allBindingsAccessor.get('selectizeOptions')
      for (var attr_name in passed_options) {
        if (attr_name === 'maxLength') {
          options.createFilter = function (input) {
            return input.length <= passed_options[attr_name]
          }
        }
        else if (attr_name === 'clearable' && passed_options[attr_name]) {
          options.plugins = ['clear_button'];
        }
        else {
          options[attr_name] = passed_options[attr_name];
        }
      }
    }

    if (!options.hasOwnProperty('dropdownParent')) {
      options.dropdownParent = 'body';
    }

    var $select = $(element).selectize(options)[0].selectize;


    if (typeof allBindingsAccessor.get('value') == 'function') {
      $select.addItem(allBindingsAccessor.get('value')());
      allBindingsAccessor.get('value').subscribe(function (new_val) {
        $select.addItem(new_val);
      })
    }

    if (allBindingsAccessor.get('innerSubscriber')) {
      valueAccessor()().forEach(function (item) {
        var previousValue;
        item[allBindingsAccessor.get('innerSubscriber')].subscribe(function (oldValue) {
          previousValue = oldValue;
        }, null, 'beforeChange');
        item[allBindingsAccessor.get('innerSubscriber')].subscribe(function (newValue) {
          var newOption = {};
          newOption[options.valueField] = newValue;
          newOption[options.labelField] = newValue;
          $select.updateOption(previousValue, newOption);
          $select.refreshOptions(false);
        });
      });
    }

    if (typeof allBindingsAccessor.get('selectedOptions') == 'function') {
      allBindingsAccessor.get('selectedOptions').subscribe(function (new_val) {
        // Removing items which are not in new value
        var values = $select.getValue();
        var items_to_remove = [];
        for (var k in values) {
          if (new_val.indexOf(values[k]) == -1) {
            items_to_remove.push(values[k]);
          }
        }

        for (var k in items_to_remove) {
          $select.removeItem(items_to_remove[k]);
        }

        for (var k in new_val) {
          $select.addItem(new_val[k]);
        }

      });
      var selected = allBindingsAccessor.get('selectedOptions')();
      for (var k in selected) {
        $select.addItem(selected[k]);
      }
    }


    if (typeof init_selectize == 'function') {
      init_selectize($select);
    }

    if (typeof valueAccessor().subscribe == 'function') {
      valueAccessor().subscribe(function (changes) {
        // To avoid having duplicate keys, all delete operations will go first
        var addedItems = new Array();
        changes.forEach(function (change) {
          switch (change.status) {
            case 'added':
              addedItems.push(change.value);
              break;
            case 'deleted':
              var itemId = change.value[options.valueField];
              if (typeof itemId === 'function') {
                itemId = itemId();
              }
              if (itemId != null) {
                $select.removeOption(itemId);
              }
          }
        });
        addedItems.forEach(function (item) {
          var optionValue = item[options.valueField];
          if (typeof optionValue === 'function') {
            optionValue = optionValue();
          }

          var optionLabel = item[options.labelField];
          if (typeof optionLabel === 'function') {
            optionLabel = optionLabel();
          }

          var newOption = {};
          newOption[options.valueField] = optionValue;
          newOption[options.labelField] = optionLabel;

          $select.addOption(newOption);

          if (allBindingsAccessor.get('innerSubscriber')) {
            var previousValue;
            item[allBindingsAccessor.get('innerSubscriber')].subscribe(function (oldValue) {
              previousValue = oldValue;
            }, null, 'beforeChange');
            item[allBindingsAccessor.get('innerSubscriber')].subscribe(function (newValue) {
              var newOption = {};
              newOption[options.valueField] = newValue;
              newOption[options.labelField] = newValue;
              $select.updateOption(previousValue, newOption);
              $select.refreshOptions(false);
            });
          }
        });

      }, null, "arrayChange");
    }

  },
  update: function (element, valueAccessor, allBindingsAccessor) {
    var optionsValue = allBindingsAccessor.get('optionsValue') || 'value';
    var value_accessor = valueAccessor();

    if (allBindingsAccessor.has('selectedObjects')) {
      allBindingsAccessor.get('selectedObjects')($.grep(value_accessor(), function (i) {
        var id = i[optionsValue];
        if (typeof i[optionsValue] == 'function') {
          id = i[optionsValue]()
        }
        return allBindingsAccessor.get('selectedOptions')().indexOf(id) > -1;
      }));
    }

    if (allBindingsAccessor.has('object')) {
      allBindingsAccessor.get('object')($.grep(value_accessor(), function (i) {
        var id = i[optionsValue];
        if (typeof i[optionsValue] == 'function') {
          id = i[optionsValue]()
        }
        return id == allBindingsAccessor.get('value')();
      })[0]);
    }
  }
}
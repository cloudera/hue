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

// TODO: Depends on Role

ko.bindingHandlers.select2 = {
  init: function(element, valueAccessor, allBindingsAccessor, viewModel) {
    const options = ko.toJS(valueAccessor()) || {};
    const $element = $(element);

    // When the options are in the binding value accessor the data attribute will be used instead of any <select>
    // tag it's attached to.
    if (ko.isObservable(valueAccessor().options) && ko.isObservable(valueAccessor().value)) {
      const optionsObservable = valueAccessor().options;
      const valueObservable = valueAccessor().value;
      options.data = $.map(optionsObservable(), value => {
        return { id: value, text: value };
      });
      options.val = valueObservable();

      const refreshSelect2Data = function() {
        $element.select2(
          'data',
          $.map(optionsObservable(), value => {
            return { id: value, text: value };
          })
        );
        $element.select2('val', valueObservable());
      };

      valueObservable.subscribe(newValue => {
        if (newValue !== $element.select2('val')) {
          refreshSelect2Data();
        }
      });

      optionsObservable.subscribe(refreshSelect2Data);

      window.setTimeout(() => {
        refreshSelect2Data();
      }, 10);
    }

    if (typeof valueAccessor().vm != 'undefined') {
      viewModel = valueAccessor().vm;
    }

    if (typeof valueAccessor().update != 'undefined') {
      if (
        options.type === 'user' &&
        viewModel.selectableHadoopUsers().indexOf(options.update) === -1
      ) {
        viewModel.availableHadoopUsers.push({
          username: options.update
        });
      }
      if (options.type === 'group') {
        if (options.update instanceof Array) {
          options.update.forEach(opt => {
            if (viewModel.selectableHadoopGroups().indexOf(opt) === -1) {
              viewModel.availableHadoopGroups.push({
                name: opt
              });
            }
          });
        } else if (viewModel.selectableHadoopGroups().indexOf(options.update) === -1) {
          viewModel.availableHadoopGroups.push({
            name: options.update
          });
        }
      }
      if (
        options.type === 'action' &&
        viewModel.availableActions().indexOf(options.update) === -1
      ) {
        viewModel.availableActions.push(options.update);
      }
      if (
        options.type === 'scope' &&
        viewModel.availablePrivileges().indexOf(options.update) === -1
      ) {
        viewModel.availablePrivileges.push(options.update);
      }
      if (options.type === 'parameter' && options.update !== '') {
        let _found = false;
        allBindingsAccessor()
          .options()
          .forEach(opt => {
            let _option = opt[allBindingsAccessor().optionsValue];
            if (ko.isObservable(_option)) {
              _option = _option();
            }
            if (_option === options.update) {
              _found = true;
            }
          });
        if (!_found) {
          allBindingsAccessor().options.push({
            name: ko.observable(options.update),
            value: ko.observable(options.update)
          });
        }
      }
    }
    $element
      .select2(options)
      .on('change', e => {
        if (typeof e.val != 'undefined') {
          if (typeof valueAccessor().update != 'undefined') {
            valueAccessor().update(e.val);
          }
          if (typeof valueAccessor().value != 'undefined') {
            valueAccessor().value(e.val);
          }
        }
      })
      .on('select2-focus', () => {
        if (typeof options.onFocus != 'undefined') {
          options.onFocus();
        }
      })
      .on('select2-blur', () => {
        if (typeof options.onBlur != 'undefined') {
          options.onBlur();
        }
      })
      .on('select2-open', () => {
        $('.select2-input')
          .off('keyup')
          .data('type', options.type)
          .on('keyup', function(e) {
            if (e.keyCode === 13) {
              const _isArray = options.update instanceof Array;
              const _newVal = $(this).val();
              const _type = $(this).data('type');
              if ($.trim(_newVal) !== '') {
                if (_type === 'user') {
                  viewModel.availableHadoopUsers.push({
                    username: _newVal
                  });
                }
                if (_type === 'group') {
                  viewModel.availableHadoopGroups.push({
                    name: _newVal
                  });
                }
                if (_type === 'action') {
                  viewModel.availableActions.push(_newVal);
                }
                if (_type === 'scope') {
                  viewModel.availablePrivileges.push(_newVal);
                }
                if (_type === 'role' && window.Role) {
                  const _r = new Role(viewModel, { name: _newVal });
                  viewModel.tempRoles.push(_r);
                  viewModel.roles.push(_r);
                }
                if (_type === 'parameter') {
                  let _found = false;
                  allBindingsAccessor()
                    .options()
                    .forEach(opt => {
                      if (opt[allBindingsAccessor().optionsValue]() === _newVal) {
                        _found = true;
                      }
                    });
                  if (!_found) {
                    allBindingsAccessor().options.push({
                      name: ko.observable(_newVal),
                      value: ko.observable(_newVal)
                    });
                  }
                }
                if (_isArray) {
                  const _vals = $(element).select2('val');
                  _vals.push(_newVal);
                  $(element).select2('val', _vals, true);
                } else {
                  $(element).select2('val', _newVal, true);
                }
                $(element).select2('close');
              }
            }
          });
      });
  },
  update: function(element, valueAccessor, allBindingsAccessor) {
    if (typeof allBindingsAccessor().visible != 'undefined') {
      if (
        (typeof allBindingsAccessor().visible == 'boolean' && allBindingsAccessor().visible) ||
        (typeof allBindingsAccessor().visible == 'function' && allBindingsAccessor().visible())
      ) {
        $(element)
          .select2('container')
          .show();
      } else {
        $(element)
          .select2('container')
          .hide();
      }
    }
    if (typeof valueAccessor().update != 'undefined') {
      $(element).select2('val', valueAccessor().update());
    }
    if (typeof valueAccessor().readonly != 'undefined') {
      $(element).select2('readonly', valueAccessor().readonly);
      if (typeof valueAccessor().readonlySetTo != 'undefined') {
        valueAccessor().readonlySetTo();
      }
    }
  }
};

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

ko.bindingHandlers.clearable = {
  after: ['textInput', 'value', 'valueUpdate'],
  init: function(element, valueAccessor, allBindingsAccessor) {
    const $element = $(element);

    const params = valueAccessor();
    const valueObservable = ko.isObservable(params) ? params : params.value;

    function tog(v) {
      return v ? 'addClass' : 'removeClass';
    }

    $element.addClass('clearable');
    $element[tog(valueObservable())]('x');

    $element
      .on('input', function() {
        $element[tog(this.value)]('x');
      })
      .on('mousemove', function(e) {
        $element[tog(this.offsetWidth - 18 < e.clientX - this.getBoundingClientRect().left)]('onX');
      })
      .on('click', function(e) {
        if (this.offsetWidth - 18 < e.clientX - this.getBoundingClientRect().left) {
          $element.removeClass('x onX').val('');
          valueObservable('');
          if (typeof params.onClear === 'function') {
            params.onClear();
          }
        }
      });

    if (!allBindingsAccessor()['textInput'] || !allBindingsAccessor()['value']) {
      $element
        .on('change', () => {
          valueObservable($element.val());
        })
        .on('blur', () => {
          valueObservable($element.val());
        });

      if (
        allBindingsAccessor()['valueUpdate'] != null &&
        allBindingsAccessor()['valueUpdate'] === 'afterkeydown'
      ) {
        $element.on('keyup', () => {
          valueObservable($element.val());
        });
      }

      if (allBindingsAccessor()['valueUpdateDelay'] != null) {
        let _timeout = -1;
        $element.on('keyup', e => {
          if (!([13, 37, 38, 39, 40].indexOf(e.keyCode) > -1)) {
            window.clearTimeout(_timeout);
            _timeout = window.setTimeout(() => {
              valueObservable($element.val());
            }, allBindingsAccessor()['valueUpdateDelay']);
          }
        });
      }
    }
  },
  update: function(element, valueAccessor) {
    const $element = $(element);
    const params = valueAccessor();
    const valueObservable = ko.isObservable(params) ? params : params.value;

    if (!$element.is(':focus') || valueObservable() !== $element.val()) {
      $element.val(valueObservable());
    }
    if ($element.val() === '') {
      $element.removeClass('x');
    }
  }
};

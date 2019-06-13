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

import hueUtils from 'utils/hueUtils';

ko.bindingHandlers.filechooser = {
  init: function(element, valueAccessor, allBindingsAccessor) {
    const $element = $(element);
    const options = ko.unwrap(allBindingsAccessor());
    $element.attr('autocomplete', 'off');
    if (typeof valueAccessor() == 'function' || typeof valueAccessor().value == 'function') {
      $element.val(valueAccessor().value ? valueAccessor().value() : valueAccessor()());
      $element.data('fullPath', $element.val());
      $element.attr('data-original-title', $element.val());
      if (valueAccessor().displayJustLastBit) {
        const _val = $element.val();
        $element.val(_val.split('/')[_val.split('/').length - 1]);
      }
      $element.on('blur', () => {
        if (valueAccessor().value) {
          if (valueAccessor().displayJustLastBit) {
            const _val = $element.data('fullPath');
            valueAccessor().value(_val.substr(0, _val.lastIndexOf('/')) + '/' + $element.val());
          } else {
            valueAccessor().value($element.val());
          }
          $element.data('fullPath', valueAccessor().value());
        } else {
          valueAccessor()($element.val());
          $element.data('fullPath', valueAccessor()());
        }
        $element.attr('data-original-title', $element.data('fullPath'));
      });

      if (options.valueUpdate && options.valueUpdate === 'afterkeydown') {
        $element.on('keyup', () => {
          if (valueAccessor().value) {
            valueAccessor().value($element.val());
          } else {
            valueAccessor()($element.val());
          }
        });
      }
    } else {
      $element.val(valueAccessor());
      $element.on('blur', () => {
        valueAccessor($element.val());
      });
      if (options.valueUpdate && options.valueUpdate === 'afterkeydown') {
        $element.on('keyup', () => {
          valueAccessor($element.val());
        });
      }
    }

    $element.after(
      hueUtils.getFileBrowseButton(
        $element,
        true,
        valueAccessor,
        true,
        allBindingsAccessor,
        valueAccessor().isAddon,
        valueAccessor().isNestedModal,
        allBindingsAccessor &&
          allBindingsAccessor().filechooserOptions &&
          allBindingsAccessor().filechooserOptions.linkMarkup
      )
    );

    if (
      allBindingsAccessor &&
      allBindingsAccessor().filechooserOptions &&
      allBindingsAccessor().filechooserOptions.openOnFocus
    ) {
      $element.on('focus', () => {
        if ($element.val() === '') {
          $element.siblings('.filechooser-clickable').click();
        }
      });
    }
  }
};

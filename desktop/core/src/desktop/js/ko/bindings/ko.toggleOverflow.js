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

ko.bindingHandlers.toggleOverflow = {
  render: function($element, options) {
    if (hueUtils.isOverflowing($element.find('.toggle-overflow'))) {
      $('<div>')
        .addClass('toggle-overflow-toggle')
        .html('<i class="fa fa-caret-down muted"></i>')
        .appendTo($element);
      $element.on('click', () => {
        if ($element.find('.toggle-overflow-toggle i').hasClass('fa-caret-down')) {
          $element.find('.toggle-overflow').css('height', '');
          $element.css('cursor', 'n-resize');
          $element
            .find('.toggle-overflow-toggle')
            .removeClass('toggle-hidden')
            .css('cursor', 'n-resize');
          $element
            .find('.toggle-overflow-toggle i')
            .removeClass('fa-caret-down')
            .addClass('fa-caret-up');
        } else {
          if (options.height) {
            $element.find('.toggle-overflow').height(options.height);
          }
          $element.css('cursor', 's-resize');
          $element
            .find('.toggle-overflow-toggle')
            .addClass('toggle-hidden')
            .css('cursor', 's-resize');
          $element
            .find('.toggle-overflow-toggle i')
            .removeClass('fa-caret-up')
            .addClass('fa-caret-down');
        }
      });
    }
  },

  init: function(element, valueAccessor) {
    const $element = $(element);
    const options = valueAccessor() || {};
    $element.wrapInner('<div class="toggle-overflow"></div>');
    if (options.height) {
      $element.find('.toggle-overflow').height(options.height);
    }
    if (options.width) {
      $element.find('.toggle-overflow').width(options.width);
    }
  },

  update: function(element, valueAccessor) {
    const $element = $(element);
    const options = valueAccessor() || {};
    window.setTimeout(() => {
      ko.bindingHandlers.toggleOverflow.render($element, options);
    }, 100);
  }
};

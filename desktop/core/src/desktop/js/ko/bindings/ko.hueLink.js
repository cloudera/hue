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

import huePubSub from 'utils/huePubSub';

ko.bindingHandlers.hueLink = {
  init: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
    ko.bindingHandlers.click.init(
      element,
      () => {
        return function(data, event) {
          const url = ko.unwrap(valueAccessor());
          if (url) {
            const prefix = window.HUE_BASE_URL + '/hue' + (url.indexOf('/') === 0 ? '' : '/');
            if ($(element).attr('target')) {
              window.open(prefix + url, $(element).attr('target'));
            } else if (event.ctrlKey || event.metaKey || event.which === 2) {
              window.open(prefix + url, '_blank');
            } else {
              huePubSub.publish('open.link', url);
            }
          }
        };
      },
      allBindings,
      viewModel,
      bindingContext
    );

    ko.bindingHandlers.hueLink.update(element, valueAccessor);
  },
  update: function(element, valueAccessor) {
    const url = ko.unwrap(valueAccessor());
    if (url) {
      $(element).attr('href', '/hue' + (url.indexOf('/') === 0 ? url : '/' + url));
    } else {
      $(element).attr('href', 'javascript: void(0);');
    }
  }
};

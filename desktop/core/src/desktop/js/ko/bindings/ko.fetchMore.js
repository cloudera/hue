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

ko.bindingHandlers.fetchMore = {
  init: function(element, valueAccessor) {
    const options = valueAccessor();
    const $element = $(element);

    let throttle = -1;
    $element.on('scroll.fetchMore', () => {
      window.clearTimeout(throttle);
      throttle = window.setTimeout(() => {
        if (
          element.scrollTop + $element.innerHeight() >= element.scrollHeight - 10 &&
          ko.unwrap(options.hasMore) &&
          !ko.unwrap(options.loadingMore)
        ) {
          options.fetchMore();
        }
      }, 100);
    });

    ko.utils.domNodeDisposal.addDisposeCallback(element, () => {
      $element.off('scroll.fetchMore');
    });
  }
};

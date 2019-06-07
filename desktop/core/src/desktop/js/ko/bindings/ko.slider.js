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

ko.bindingHandlers.slider = {
  init: function(element, valueAccessor) {
    const _el = $(element);
    const _options = $.extend(valueAccessor(), {});
    _el.slider({
      min: !isNaN(parseFloat(_options.start())) ? parseFloat(_options.start()) : 0,
      max: !isNaN(parseFloat(_options.end())) ? parseFloat(_options.end()) : 10,
      step: !isNaN(parseFloat(_options.gap())) ? parseFloat(_options.gap()) : 1,
      handle: _options.handle ? _options.handle : 'triangle',
      start: parseFloat(_options.min()),
      end: parseFloat(_options.max()),
      tooltip_split: true,
      tooltip: 'always',
      labels: _options.labels
    });
    _el.on('slide', e => {
      _options.start(e.min);
      _options.end(e.max);
      _options.min(e.start);
      _options.max(e.end);
      if (_options.min() < _options.start()) {
        _options.start(_options.min());
      }
      if (_options.max() > _options.end()) {
        _options.end(_options.max());
      }
      _options.gap(e.step);
      if (typeof _options.properties.initial_start == 'function') {
        _options.properties.start(_options.properties.initial_start());
        _options.properties.end(_options.properties.initial_end());
        _options.properties.gap(_options.properties.initial_gap());
      }
    });
    _el.on('slideStop', () => {
      if (window.searchViewModel) {
        window.searchViewModel.search();
      }
    });
  },
  update: function(element, valueAccessor) {
    $.extend(valueAccessor(), {});
  }
};

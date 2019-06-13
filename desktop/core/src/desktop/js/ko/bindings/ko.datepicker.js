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

ko.bindingHandlers.datepicker = {
  init: function(element, valueAccessor, allBindings) {
    const _el = $(element);
    const _options = ko.unwrap(valueAccessor());
    _el
      .datepicker({
        format: 'yyyy-mm-dd'
      })
      .on('show', e => {
        if (_options.momentFormat) {
          const m = moment.utc(_el.val());
          _el.datepicker('setValue', m.format('YYYY-MM-DD'));
          _el.val(m.format(_options.momentFormat)); // Set value again as datepicker clears the time component
        }
      })
      .on('changeDate', e => {
        setDate(e.date);
      })
      .on('hide', e => {
        setDate(e.date);
      });

    function setDate(d) {
      if (_options.momentFormat) {
        const m = moment(d);
        // Keep time intact
        const previous = moment.utc(allBindings().value());
        previous.date(m.date());
        previous.month(m.month());
        previous.year(m.year());

        _el.val(previous.format(_options.momentFormat));
      }
      allBindings().value(_el.val());
    }
  }
};

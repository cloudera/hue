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

// Not in coordinator_properties as also used in create coordinator.

function initCoordinator(coordinator_json, i18n) {

  var coordCron =
    $('#coord-frequency')
      .jqCron({
        texts: {
          i18n: i18n
        },
        enabled_minute: false,
        multiple_dom: true,
        multiple_month: true,
        multiple_mins: true,
        multiple_dow: true,
        multiple_time_hours: true,
        multiple_time_minutes: false,
        default_period: 'day',
        default_value: coordinator_json.frequency,
        no_reset_button: true,
        lang: 'i18n'
      })
      .jqCronGetInstance();

  var coordViewModel = function(coordinator_json) {
    var self = this;

    self.cronFrequency = ko.observable(typeof coordinator_json.frequency != "undefined" && coordinator_json.frequency != null ? coordinator_json.frequency : '');
    self.isSaveVisible = ko.observable(false);
    self.isAdvancedCron = ko.observable(typeof coordinator_json.isAdvancedCron != "undefined" && coordinator_json.isAdvancedCron != null ? coordinator_json.isAdvancedCron : false);
    self.isAdvancedCron.subscribe(function(value) {
      if (value) {
        coordCron.disable();
      } else {
        coordCron.enable();
      }
    });
  };

  window.coordViewModel = new coordViewModel(coordinator_json);

  ko.applyBindings(window.coordViewModel, document.getElementById('step2'));
}

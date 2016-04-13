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



var driver = (function($) {
  var DriverModel = koify.Model.extend({
    'id': 1,
    'job_config': [],
    'config_resources': {},
    'initialize': function(attrs) {
      var self = this;
      var _attrs = $.extend(true, {}, attrs);
      _attrs = transform_keys(_attrs, {
        'job_config': 'job_config'
      });
      _attrs = transform_values(_attrs, {
        'job_config': to_configs
      });
      return _attrs;
    }
  });

  var Driver = koify.Node.extend({
    'identifier': 'driver',
    'persists': false,
    'model_class': DriverModel,
    'base_url': '/sqoop/api/driver/',
    'initialize': function() {
      var self = this;
      self.parent.initialize.apply(self, arguments);
      self.selected = ko.observable();
    },
    'map': function() {
      var self = this;
      var mapping_options = $.extend(true, {
        'ignore': ['parent', 'initialize']
      }, configs.MapProperties);
      if ('__ko_mapping__' in self) {
        ko.mapping.fromJS(self.model, mapping_options, self);
      } else {
        var mapped = ko.mapping.fromJS(self.model, mapping_options);
        $.extend(self, mapped);
      }
    }
  });

  return {
    'DriverModel': DriverModel,
    'Driver': Driver
  }
})($);

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



var framework = (function($) {
  var FrameworkModel = koify.Model.extend({
    'id': 1,
    'job_forms': {
      'IMPORT': [],
      'EXPORT': []
    },
    'con_forms': [],
    'resources': {},
    'initialize': function(attrs) {
      var self = this;
      var attrs = $.extend(true, attrs, {});
      attrs = transform_keys(attrs, {
        'job-forms': 'job_forms',
        'con-forms': 'con_forms'
      });
      attrs = transform_values(attrs, {
        'con_forms': to_forms,
        'job_forms': function(key, value) {
          transform_values(value, {
            'IMPORT': to_forms,
            'EXPORT': to_forms
          });
          return value;
        }
      });
      return attrs;
    }
  });

  var Framework = koify.Node.extend({
    'identifier': 'framework',
    'persists': false,
    'modelClass': FrameworkModel,
    'base_url': '/sqoop/api/framework/',
    'initialize': function() {
      var self = this;
      self.parent.initialize.apply(self, arguments);
    }
  });

  return {
    'FrameworkModel': FrameworkModel,
    'Framework': Framework
  }
})($);

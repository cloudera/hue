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


var connectors = (function($) {
  var ConnectorModel = koify.Model.extend({
    'id': -1,
    'name': null,
    'class': null,
    'job_forms': {
      'IMPORT': [],
      'EXPORT': []
    },
    'con_forms': [],
    'version': null,
    'resources': {},
    'initialize': function(attrs) {
      var self = this;
      var _attrs = $.extend(true, {}, attrs);
      _attrs = transform_keys(_attrs, {
        'job-forms': 'job_forms',
        'con-forms': 'con_forms'
      });
      _attrs = transform_values(_attrs, {
        'con_forms': to_forms,
        'job_forms': function(key, value) {
          transform_values(value, {
            'IMPORT': to_forms,
            'EXPORT': to_forms
          });
          return value;
        }
      });
      return _attrs;
    }
  });

  var Connector = koify.Node.extend({
    'identifier': 'connector',
    'persist': false,
    'model_class': ConnectorModel,
    'base_url': '/sqoop/api/connectors/',
    'initialize': function() {
      var self = this;
      self.parent.initialize.apply(self, arguments);
      self.selected = ko.observable();
    },
    map: function() {
      var self = this;
      var mapping_options = $.extend(true, {
        'ignore': ['parent', 'initialize']
      }, forms.MapProperties);
      if ('__ko_mapping__' in self) {
        ko.mapping.fromJS(self.model, mapping_options, self);
      } else {
        var mapped = ko.mapping.fromJS(self.model, mapping_options);
        $.extend(self, mapped);
      }
    }
  });

  function fetch_connectors(options) {
    $(document).trigger('load.connectors', [options]);
    var request = $.extend({
      url: '/sqoop/api/connectors/',
      dataType: 'json',
      type: 'GET',
      success: fetcher_success('connectors', Connector, options)
    }, options || {});
    $.ajax(request);
  }

  return {
    'ConnectorModel': ConnectorModel,
    'Connector': Connector,
    'fetchConnectors': fetch_connectors
  };
})($);

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
  var CONNECTOR_NAMES = ["hdfs-connector", "generic-jdbc-connector"];

  var ConnectorModel = koify.Model.extend({
    'id': -1,
    'name': null,
    'class': null,
    'job_config': {
      'FROM': [],
      'TO': []
    },
    'link_config': [],
    'version': null,
    'config_resources': {},
    'initialize': function(attrs) {
      var self = this;
      var _attrs = $.extend(true, {}, attrs);
      _attrs = transform_keys(_attrs, {
        'link_config': 'link_config',
        'job_config': 'job_config'
      });
      _attrs = transform_values(_attrs, {
        'link_config': to_configs,
        'job_config': function(key, value) {
          transform_values(value, {
            'FROM': to_configs,
            'TO': to_configs
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
      }, configs.MapProperties);
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
      success: fetcher_success('connectors', Connector, options),
      error: fetcher_error('connectors', Connector, options)
    }, options || {});
    $.ajax(request);
  }

  return {
    'ConnectorModel': ConnectorModel,
    'Connector': Connector,
    'fetchConnectors': fetch_connectors,
    'CONNECTOR_NAMES': CONNECTOR_NAMES
  };
})($);

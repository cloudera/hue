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


var connections = (function($) {
  var ConnectionModel = koify.Model.extend({
    'id': -1,
    'name': null,
    'connector': [],
    'connector_id': 0,
    'creation_date': null,
    'creation_user': null,
    'update_date': null,
    'update_user': null,
    'framework': [],
    'initialize': function(attrs) {
      var self = this;
      var _attrs = $.extend(true, {}, attrs);
      _attrs = transform_keys(_attrs, {
        'connector-id': 'connector_id'
      });
      _attrs = transform_values(_attrs, {
        'connector': to_forms,
        'framework': to_forms
      });
      return _attrs;
    }
  });

  var Connection = koify.Node.extend({
    'identifier': 'connection',
    'persists': true,
    'model_class': ConnectionModel,
    'base_url': '/sqoop/api/connections/',
    'initialize': function(options) {
      var self = this;
      self.parent.initialize.apply(self, arguments);
      self.selected = ko.observable();
      self.persisted = ko.computed(function() {
        return self.id() > -1;
      });
      self.connectionString = ko.computed(function() {
        var connection_string = null;
        $.each(self.connector(), function(index, form) {
          if (form.name() == 'connection') {
            $.each(form.inputs(), function(index, input) {
              if (input.name() == 'connection.connectionString') {
                connection_string = input.value();
              }
            });
          }
        });
        return connection_string;
      });
    },
    'map': function() {
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
    },
  });

  function fetch_connections(options) {
    $(document).trigger('load.connections', [options]);
    var request = $.extend({
      url: '/sqoop/api/connections/',
      dataType: 'json',
      type: 'GET',
      success: fetcher_success('connections', Connection, options)
    }, options || {});
    $.ajax(request);
  }

  return {
    'ConnectionModel': ConnectionModel,
    'Connection': Connection,
    'fetchConnections': fetch_connections
  }
})($);

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


var links = (function($) {
  var LinkModel = koify.Model.extend({
    'id': -1,
    'name': null,
    'link_config_values': [],
    'connector_id': 0,
    'creation_date': null,
    'creation_user': null,
    'update_date': null,
    'update_user': null,
    'initialize': function(attrs) {
      var self = this;
      var _attrs = $.extend(true, {}, attrs);
      _attrs = transform_keys(_attrs, {
        'connector-id': 'connector_id'
      });
      _attrs = transform_values(_attrs, {
        'link_config_values': to_configs
      });
      return _attrs;
    }
  });

  var Link = koify.Node.extend({
    'identifier': 'linkConfig',
    'persists': true,
    'model_class': LinkModel,
    'base_url': '/sqoop/api/links/',
    'initialize': function(options) {
      var self = this;
      self.parent.initialize.apply(self, arguments);
      self.selected = ko.observable();
      self.persisted = ko.computed(function() {
        return self.id() > -1;
      });
      self.connectionString = ko.computed(function() {
        var link_string = null;
        $.each(self.link_config_values(), function(index, config) {
          if (config.name() == 'linkConfig') {
            $.each(config.inputs(), function(index, input) {
              if (input.name() == 'linkConfig.connectionString') {
                link_string = input.value();
              }
            });
          }
        });
        return link_string;
      });
      self.jdbcDriver = ko.computed(function() {
        var jdbc_driver = null;
        $.each(self.link_config_values(), function(index, config) {
          if (config.name() == 'linkConfig') {
            $.each(config.inputs(), function(index, input) {
              if (input.name() == 'linkConfig.jdbcDriver') {
                jdbc_driver = input.value();
              }
            });
          }
        });
        return jdbc_driver;
      });
      self.host = ko.computed(function() {
        var pattern = null;
        switch (self.jdbcDriver()) {
          case 'com.mysql.jdbc.Driver':
          pattern = /jdbc:mysql:\/\/([^\:\/]+).*/;
          break;
          case 'org.postgresql.Driver':
          pattern = /jdbc:postgresql:\/\/([^\:\/]+).*/;
          break;
          case 'oracle.jdbc.OracleDriver':
          pattern = /jdbc:oracle:thin:@([^\:\/]+).*/;
          break;
        }
        if (pattern) {
          var res = self.connectionString().match(pattern);
          if (res) {
            return res[1];
          } else {
            return null;
          }
        }
      });
      self.port = ko.computed(function() {
        var pattern = null;
        switch (self.jdbcDriver()) {
          case 'com.mysql.jdbc.Driver':
          pattern = /jdbc:mysql:\/\/[^\:\/]+:(\d+)\/.*/;
          break;
          case 'org.postgresql.Driver':
          pattern = /jdbc:postgresql:\/\/[^\:\/]+:(\d+)\/.*/;
          break;
          case 'oracle.jdbc.OracleDriver':
          pattern = /jdbc:oracle:thin:@[^\:\/]+:(\d+):.*/;
          break;
        }
        if (pattern) {
          var res = self.connectionString().match(pattern);
          if (res) {
            return res[1];
          } else {
            return null;
          }
        }
      });
      self.hostAndPort = ko.computed(function() {
        if (self.host()) {
          if (self.port()) {
            return self.host() + ":" + self.port();
          } else {
            return self.host();
          }
        } else {
          return null;
        }
      });
      self.database = ko.computed(function() {
        var pattern = null;
        switch (self.jdbcDriver()) {
          case 'com.mysql.jdbc.Driver':
          pattern = /jdbc:mysql:\/\/.*?\/(.*)/;
          break;
          case 'org.postgresql.Driver':
          pattern = /jdbc:postgresql:\/\/.*?\/(.*)/;
          break;
          case 'oracle.jdbc.OracleDriver':
          pattern = /jdbc:oracle:thin:@.*?:.*?:(.*)/;
          break;
        }
        if (pattern) {
          var res = self.connectionString().match(pattern);
          if (res) {
            return res[1];
          } else {
            return null;
          }
        }
      });
      self.username = ko.computed(function() {
        var username = null;
        $.each(self.link_config_values(), function(index, config) {
          if (config.name() == 'linkConfig') {
            $.each(config.inputs(), function(index, input) {
              if (input.name() == 'linkConfig.username') {
                username = input.value();
              }
            });
          }
        });
        return username;
      });
      self.password = ko.computed(function() {
        var password = null;
        $.each(self.link_config_values(), function(index, config) {
          if (config.name() == 'linkConfig') {
            $.each(config.inputs(), function(index, input) {
              if (input.name() == 'linkConfig.password') {
                password = input.value();
              }
            });
          }
        });
        return password;
      });
      self.type = ko.computed(function() {
        var conn_string = self.connectionString();
        if (!conn_string) {
          return "unknown";
        }

        var parts = conn_string.split(':');
        if (parts.length < 2) {
          return "unknown";
        }

        return parts[1];
      });
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

  function fetch_links(options) {
    $(document).trigger('load.links', [options]);
    var request = $.extend({
      url: '/sqoop/api/links/',
      dataType: 'json',
      type: 'GET',
      success: fetcher_success('links', Link, options),
      error: fetcher_error('links', Link, options)
    }, options || {});
    $.ajax(request);
  }

  return {
    'LinkModel': LinkModel,
    'Link': Link,
    'fetchLinks': fetch_links
  }
})($);

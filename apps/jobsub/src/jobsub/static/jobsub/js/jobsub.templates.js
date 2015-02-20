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


//// Load templates
// Load partial templates (for widgets)
// Load action templates
var Templates = (function($, ko) {
  var module = function(options) {
    var self = this;

    var options = $.extend({
      actions: {
        mapreduce: 'static/templates/actions/mapreduce.html',
        java: 'static/templates/actions/java.html',
        streaming: 'static/templates/actions/streaming.html',
        hive: 'static/templates/actions/hive.html',
        pig: 'static/templates/actions/pig.html',
        sqoop: 'static/templates/actions/sqoop.html',
        fs: 'static/templates/actions/fs.html',
        ssh: 'static/templates/actions/ssh.html',
        shell: 'static/templates/actions/shell.html',
        email: 'static/templates/actions/email.html',
        distcp: 'static/templates/actions/distcp.html'
      },
      partials: {
        name: 'static/templates/widgets/text.html',
        description: 'static/templates/widgets/text.html',
        is_shared: 'static/templates/widgets/checkbox.html',
        // Oozie parameters
        parameters: 'static/templates/widgets/parameters.html',
        archives: 'static/templates/widgets/filechooser.html',
        files: 'static/templates/widgets/filechooser.html',
        mkdirs: 'static/templates/widgets/folderchooser.html',
        deletes: 'static/templates/widgets/pathchooser.html',
        touchzs: 'static/templates/widgets/filechooser.html',
        chmods: 'static/templates/widgets/chmods.html',
        moves: 'static/templates/widgets/moves.html',
        job_properties: 'static/templates/widgets/properties.html',
        prepares: 'static/templates/widgets/prepares.html',
        arguments: 'static/templates/widgets/params.html',
        args: 'static/templates/widgets/params.html',
        params: 'static/templates/widgets/params.html',
        arguments_envvars: 'static/templates/widgets/params.html',
        params_arguments: 'static/templates/widgets/params.html',
        capture_output: 'static/templates/widgets/checkbox.html'
      }
    }, options);

    self.initialize(options);
  };

  function invertDictionary(dict) {
    var inverse = {};
    $.each(dict, function(key, value) {
      if (value in inverse) {
        inverse[value].push(key);
      } else {
        inverse[value] = [key];
      }
    });
    return inverse;
  }

  $.extend(module.prototype, {
    initialize: function(options) {
      var self = this;

      var reverse_partials = invertDictionary(options.partials);
      var reverse_actions = invertDictionary(options.actions);

      self.partials = {};
      $.each(reverse_partials, function(url, widget_ids) {
        $.get(url, function(data) {
          $.each(widget_ids, function(index, widget_id) {
            self.partials[widget_id] = data;
          });
        });
      });

      self.actions = {};
      $.each(reverse_actions, function(url, widget_ids) {
        $.get(url, function(data) {
          $.each(widget_ids, function(index, widget_id) {
            self.actions[widget_id] = data;
          });
        });
      });
    },
    getActionTemplate: function(id, context) {
      var self = this;
      var el = $('#' + id);
      if (el.length > 0 && el.html().length > 0) {
        return el;
      } else {
        var html = Mustache.to_html(self.actions[id], context, self.partials);
        // no jQuery here, IE8 doesn't like it.
        var scriptTag = document.createElement('script');
        scriptTag.setAttribute('id', id);
        scriptTag.setAttribute('type', 'text/html');
        scriptTag.text = html;
        document.body.appendChild(scriptTag);
        return $('#' + id);
      }
    }
  });

  return module;
})($, ko);
var templates = new Templates();
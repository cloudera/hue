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

/**
 * Import workflow action module
 * Enables selection of workflows.
 * Enables selection of actions within workflows.
 */
var ImportNodeModule = function($, managed) {
  var module = function(options) {
    var self = this;

    self.nodes = ko.observableArray();
    self.workflows = ko.observableArray();
    self.selected_workflow = ko.observable();
    self.nodes_url = ko.computed(function() {
      return '/oozie/workflows/' + ((self.selected_workflow()) ? self.selected_workflow().id : 0) + '/actions';
    });
    self.workflows_url = ko.computed(function() {
      if (managed) {
        return '/oozie/workflows?managed=true';
      } else {
        return '/oozie/workflows?managed=false';
      }
    });

    module.prototype.initialize.apply(self, arguments);

    return self;
  };

  $.extend(module.prototype, {
    initialize: function(options) {
      var self = this;

      var options = options || {};

      if (options.workflows) {
        self.workflows.removeAll();
        $.each(options.workflows, function(index, workflow) {
          self.workflows.push(new WorkflowModel(workflow));
        });
      }

      if (options.nodes) {
        self.nodes.removeAll();
        $.each(options.nodes, function(index, node) {
          self.nodes.push(new NodeModel(node));
        });
      }
    },

    getAvailableNodes: function() {
      var self = this;

      return self.available_nodes;
    },

    fetchWorkflows: function(options) {
      var self = this;

      var request = $.extend({
        url: self.workflows_url(),
        dataType: 'json',
        type: 'GET',
        success: $.noop,
        error: $.noop
      }, options || {});

      $.ajax(request);
    },

    fetchNodes: function(options) {
      var self = this;

      var request = $.extend({
        url: self.nodes_url(),
        dataType: 'json',
        type: 'GET',
        success: $.noop,
        error: $.noop
      }, options || {});

      $.ajax(request);
    }
  });

  return module;
};

var ImportWorkflowAction = ImportNodeModule($, true);
var ImportJobsubAction = ImportNodeModule($, false);

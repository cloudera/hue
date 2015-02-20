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
 * Registry of models
 *  - Each model should have an ID attribute.
 */
var RegistryModule = function($) {
  var module = function() {
    var self = this;

    self.nodes = {};

    module.prototype.initialize.apply(self, arguments);

    return self;
  };

  $.extend(module.prototype, {
    // Normal stuff
    initialize: function() {},

    toString: function() {
      var self = this;

      var s = $.map(self.nodes, function(node) {
        return node.id();
      }).join();
      return s;
    },

    add: function(id, node) {
      var self = this;
      $(self).trigger('registry.add');
      self.nodes[String(id)] = node;
    },

    remove: function(id) {
      var self = this;
      $(self).trigger('registry.remove');
      delete self.nodes[String(id)];
    },

    get: function(id) {
      var self = this;
      return self.nodes[id];
    },

    clear: function() {
      var self = this;

      delete self.nodes;
      self.nodes = {};
    },

    allNodes: function() {
      var self = this;
      var nodes = [];
      $.each(self.nodes, function(key, node) {
        nodes.push(node);
      });
      return nodes;
    }
  });

  return module;
};
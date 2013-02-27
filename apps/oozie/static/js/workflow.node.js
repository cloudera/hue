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
 * Node
 * Displays node in a graph and handles graph manipulation.
 * The majority of nodes require similar logic.
 * This modules takes advantage of that fact.
 */
var NodeModule = function($, IdGeneratorTable, NodeFields) {
  var META_LINKS = ['related', 'default', 'error'];

  var linkTypeChooser = function(parent, child) {
    if (child.node_type() == 'kill') {
      return 'error';
    }
    switch(parent.node_type()) {
      case 'start':
        return (child.node_type() == 'end') ? 'related' : 'to';
      case 'fork':
        return (child.node_type() == 'join') ? 'related' : 'start';
      case 'decision':
        return (child.node_type() == 'decisionend') ? 'related' : 'start';
      case 'join':
      case 'decisionend':
        return 'to';
      default:
        return 'ok';
    };
  };

  var module = function(workflow, model, registry) {
    var self = this;

    self.map(model);

    self.links = ko.computed(function() {
      var links = self.child_links().filter(function(element, index, arr) {
        return $.inArray(element.name(), META_LINKS) == -1;
      });
      return links;
    });

    self.meta_links = ko.computed(function() {
      var links = self.child_links().filter(function(element, index, arr) {
        return $.inArray(element.name(), META_LINKS) != -1;
      });
      return links;
    });

    self._workflow = workflow;

    self.registry = registry;
    self.children = ko.observableArray([]);
    self.model = model;

    var errors = {};
    for(var key in model) {
      switch(key) {
        case 'child_links':
        case 'node_ptr':
        case 'initialize':
        case 'toString':
        break;
        default:
          errors[key] = [];
        break;
      }
    }
    self.errors = ko.mapping.fromJS(errors);

    self.edit_template = model.node_type + 'EditTemplate';
    switch(model.node_type) {
    case 'start':
    case 'end':
      self.view_template = ko.observable('disabledNodeTemplate');
    break;

    case 'kill':
      self.view_template = ko.observable('emptyTemplate');
    break;

    case 'fork':
      self.view_template = ko.observable('forkTemplate');
    break;

    case 'join':
      self.view_template = ko.observable('joinTemplate');
    break;

    case 'decision':
      self.view_template = ko.observable('decisionTemplate');
    break;

    case 'decisionend':
      self.view_template = ko.observable('decisionEndTemplate');
    break;

    default:
      self.view_template = ko.observable('nodeTemplate');
    break;
    }

    // Data manipulation
    if ('files' in model) {
      //// WARNING: The following order should be preserved!

      // Need to represent files as some thing else for knockout mappings.
      // The KO idiom "value" requires a named parameter.
      self._files = self.files;
      self.files = ko.observableArray([]);

      // ['file', ...] => [{'name': 'file', 'dummy': ''}, ...].
      $.each(self._files(), function(index, filename) {
        var prop = { name: ko.observable(filename), dummy: ko.observable("") };
        prop.name.subscribe(function(value) {
          self.files.valueHasMutated();
        });
        prop.dummy.subscribe(function(value) {
          self.files.valueHasMutated();
        });
        self.files.push(prop);
      });

      // [{'name': 'file', 'dummy': ''}, ...] => ['file', ...].
      self.files.subscribe(function(value) {
        self._files.removeAll();
        $.each(self.files(), function(index, file) {
          self._files.push(file.name);
        });
      });

      self.addFile = function() {
        var prop = { name: ko.observable(""), dummy: ko.observable("") };
        prop.name.subscribe(function(value) {
          self.files.valueHasMutated();
        });
        prop.dummy.subscribe(function(value) {
          self.files.valueHasMutated();
        });
        self.files.push(prop);
      };

      self.removeFile = function(val) {
        self.files.remove(val);
      };
    }

    self.initialize.apply(self, arguments);

    return self;
  };

  $.extend(true, module.prototype, NodeFields, {
    // Data.
    children: null,
    model: null,

    // Normal stuff
    /**
     * Called when creating a new node
     */
    initialize: function(workflow, model, registry) {},

    toString: function() {
      return '';
    },

    /**
     * Fetches registry
     */
    getRegistry: function() {
      return registry;
    },

    /**
     * Maps a model to self
     * Called when creating a new node before any thing else
     */
    map: function(model) {
      var self = this;

      // @see http://knockoutjs.com/documentation/plugins-mapping.html
      // MAPPING_OPTIONS comes from /oozie/static/js/models.js
      var mapping = ko.mapping.fromJS(model, MAPPING_OPTIONS);

      $.extend(self, mapping);
      $.each(mapping, function(key, value) {
        var key = key;
        if (ko.isObservable(self[key])) {
          self[key].subscribe(function(value) {
            model[key] = ko.mapping.toJS(value);
          });
        }
      });

      $.each(self.child_links(), function(index, link) {
        var $index = index;
        link.comment.subscribe(function(value) {
          self.model.child_links[$index].comment = value;
        });

        link.child.subscribe(function(value) {
          self.model.child_links[$index].child = value;
        });
      });

    },

    validate: function( ) {
      var self = this;

      var options = {};

      data = $.extend(true, {}, self.model);

      var success = false;
      var request = $.extend({
        url: '/oozie/workflows/' + self._workflow.id() + '/nodes/' + self.node_type() + '/validate',
        type: 'POST',
        data: { node: JSON.stringify(data) },
        success: function(data) {
          ko.mapping.fromJS(data.data, self.errors);
          success = data.status == 0;
        },
        async: false
      }, options);

      $.ajax(request);

      return success;
    },

    // Hierarchy manipulation.
    /**
     * Append node to self
     * Does not support multiple children.
     * Ensures single child.
     * Ensures no cycles.
     * 1. Finds all children and attaches them to node (cleans node first).
     * 2. Remove all children from self.
     * 3. Attach node to self.
     */
    append: function(node) {
      var self = this;

      // Not fork nor decision nor self
      if ($.inArray(self.node_type(), ['fork', 'decision']) == -1 && node.id() != self.id() && !self.isChild(node)) {
        node.removeAllChildren();
        $.each(self.links(), function(index, link) {
          node.addChild(self.registry.get(link.child()));
        });
        self.removeAllChildren();
        self.addChild(node);
      }
    },

    /**
     * Find all parents of current node
     */
    findParents: function() {
      var self = this;

      var parents = [];
      $.each(self.registry.nodes, function(id, node) {
        $.each(node.links(), function(index, link) {
          if (link.child() == self.id()) {
            parents.push(node);
          }
        });
      });
      return parents;
    },

    /**
     * Find all children of current node
     */
    findChildren: function() {
      var self = this;

      var children = [];
      $.each(self.links(), function(index, link) {
        children.push(self.registry.get(link.child()));
      });

      return children;
    },

    /**
     * Detach current node from the graph
     * 1. Takes children of self node, removes them from self node, and adds them to each parent of self node.
     * 2. The self node is then removed from every parent.
     * 3. Does not support multiple children since we do not automatically fork.
     */
    detach: function() {
      var self = this;

      $.each(self.findParents(), function(index, parent) {
        $.each(self.links(), function(index, link) {
          var node = self.registry.get(link.child());
          parent.replaceChild(self, node);
        });
      });

      $(self).trigger('detached');

      self.removeAllChildren();
    },

    /**
     * Add child
     * Update child links for this node.
     */
    addChild: function(node) {
      var self = this;
      var link = {
        parent: ko.observable(self.id()),
        child: ko.observable(node.id()),
        name: ko.observable(linkTypeChooser(self, node)),
        comment: ko.observable('')
      };
      self.child_links.unshift(link);
    },

    /**
     * Remove child node
     * 1. Find child node link
     * 2. Remove child node link
     */
    removeChild: function(node) {
      var self = this;
      var spliceIndex = -1;

      $.each(self.child_links(), function(index, link) {
        if (link.child() == node.id()) {
          spliceIndex = index;
        }
      });

      if (spliceIndex > -1) {
        self.child_links.splice(spliceIndex, 1);
      }

      return spliceIndex != -1;
    },

    /**
     * Remove all children
     * Removes all children except for related, default, and error links
     * Note: we hold on to related, default, and error links because
     *  we have to.
     */
    removeAllChildren: function() {
      var self = this;
      var keep_links = [];

      $.each(self.child_links(), function(index, link) {
        if ($.inArray(link.name(), META_LINKS) > -1) {
          keep_links.push(link);
        }
      });

      self.child_links.removeAll();
      $.each(keep_links, function(index, link) {
        self.child_links.push(link);
      });
    },

    /**
     * Replace child node with another node in the following way:
     * 1. Find child index
     * 2. Remove child index
     * 3. Remove and remember every element after child
     * 4. Add replacement node
     * 5. Add every child that was remembered
     */
    replaceChild: function(child, replacement) {
      var self = this;
      var index = -1;

      $.each(self.child_links(), function(i, link) {
        if (link.child() == child.id()) {
          index = i;
        }
      });

      if (index > -1) {
        self.child_links.splice(index, 1);
        var links = self.child_links.splice(index);
        var link = {
          parent: ko.observable(self.id()),
          child: ko.observable(replacement.id()),
          name: ko.observable(linkTypeChooser(self, replacement)),
          comment: ko.observable('')
        };
        self.child_links.push(link);

        $.each(links, function(index, link) {
          self.child_links.push(link);
        });
      }

      return index != -1;
    },

    isChild: function(node) {
      var self = this;
      var res = false;
      $.each(self.links(), function(index, link) {
        if (link.child() == node.id()) {
          res = true;
        }
      });
      return res;
    },

    erase: function() {
      var self = this;
      self.registry.remove(self.id());
    }

  });

  return module;
};
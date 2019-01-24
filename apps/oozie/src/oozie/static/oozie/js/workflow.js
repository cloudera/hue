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

var Registry = RegistryModule($);

var Modal = ModalModule($, ko);

var Node = NodeModule($, IdGeneratorTable, NodeFields);

var SubworkflowNode = NodeModule($, IdGeneratorTable, NodeFields);
$.extend(SubworkflowNode.prototype, Node.prototype, {
  'initialize': function(workflow, model, registry) {
    var self = this;

    if (self.sub_workflow()) {
      self.sub_workflow(self.sub_workflow().toString());
    }
  }
});

var StartNode = NodeModule($, IdGeneratorTable, NodeFields);
$.extend(StartNode.prototype, Node.prototype, {
  /**
   * Same as addChild for nodes, except if we reach the end,
   * we add the end node to our child_links in the form of a
   * 'related' link and 'start' link.
   * We should always have a start link in an empty workflow!
   */
  replaceChild: function(child, replacement) {
    var self = this;
    var index = -1;

    $.each(self.non_error_links(), function(i, link) {
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
        name: ko.observable('to'),
        comment: ko.observable('')
      };
      self.child_links.push(link);

      $.each(links, function(index, link) {
        self.child_links.push(link);
      });
    }

    return index != -1;
  }
});

var ForkNode = NodeModule($, IdGeneratorTable, NodeFields);
$.extend(ForkNode.prototype, Node.prototype, {
  // Join nodes are connected through 'related' links
  join: function() {
    var self = this;

    var join = null;
    $.each(self.child_links(), function(index, link) {
      if (link.name() == 'related') {
        join = self.registry.get(link.child());
      }
    });
    return join;
  },

  /**
   * Append a node to the current fork
   * Also adds join node to node.
   * When adding the join node, append will remove all the children from the join!
   * We need to make sure the join remembers its children since append will replace them.
   * NOTE: Cannot append a fork or decision! Use addChild or replaceChild instead!
   */
  append: function(node) {
    var self = this;

    if (node.node_type() != 'decision' && node.node_type() != 'fork') {
      var join = self.join();
      if (join.id() != node.id()) {
        var children = join.findChildren();

        self.addChild(node);
        node.append(join);

        // remember children
        $.each(children, function(index, child) {
          join.addChild(child);
        });
      }
    }
  },

  /**
   * Replace child node with another node
   * 1. Remove child if the replacement is related join
   * 2. Apply Node.replaceChild for all other causes
   * NOTE: can assume the only join this fork will ever see is the related join!
   * This is because the related will always be the closest join for children.
   * Also, the operations allowed that would make this all possible: detach, append;
   * are inherently going to remove any other joins if they exist.
   * This is also easier given nodes are contained within Forks!
   */
  replaceChild: function(child, replacement) {
    var self = this;

    var ret = true;
    if (self.join().id() == replacement.id()) {
      ret = self.removeChild(child);
    } else {
      ret = Node.prototype.replaceChild.apply(self, arguments);
    }

    var links = self.links().filter(function(element, index, arr) {
      var node = self.registry.get(element.child());
      // If no node is found, it means that it's a temporary node that may be added to the graph.
      // This will not be a join. It will most likely be a decision node.
      return !node || node.node_type() != 'join';
    });

    if (links.length < 2) {
      self.detach();
      self.join().detach();

      self.erase();
      self.join().erase();
    }

    return ret;
  },

  /**
   * Converts fork node into decision node in the following way:
   * 1. Copies contents of current fork node into a new decision node
   * 2. Detach fork node
   * 3. Erase fork node
   * 4. Append decision node to parent
   */
  convertToDecision: function() {
    var self = this;

    var join = self.join();
    var end = null;
    var child = join.findChildren()[0];

    // Replace join with decision end
    var decision_end_model = new NodeModel({
      id: IdGeneratorTable['decisionend'].nextId(),
      node_type: 'decisionend',
      workflow: self.workflow(),
      child_links: ko.mapping.toJS(join.child_links())
    });
    $.each(decision_end_model.child_links, function(index, link) {
      link.parent = decision_end_model.id;
    });
    var decision_end_node = new Node(self._workflow, decision_end_model, self.registry);
    var parents = join.findParents();
    $.each(parents, function(index, parent) {
      parent.replaceChild(join, decision_end_node);
    });

    // Replace fork with decision node
    var decision_model = new DecisionModel({
      id: IdGeneratorTable['decision'].nextId(),
      name: self.name(),
      description: self.description(),
      node_type: 'decision',
      workflow: self.workflow(),
      child_links: ko.mapping.toJS(self.child_links())
    });
    var default_link = {
      parent: decision_model.id,
      child: self._workflow.end(),
      name: 'default',
      comment: ''
    };

    decision_model.child_links.push(default_link);

    $.each(decision_model.child_links, function(index, link) {
      link.parent = decision_model.id;
    });

    var parents = self.findParents();
    var decision_node = new DecisionNode(self._workflow, decision_model, self.registry);
    decision_node.removeChild(join);
    decision_node.addChild(decision_end_node);

    $.each(parents, function(index, parent) {
      parent.replaceChild(self, decision_node);
    });

    // Get rid of fork and join in registry
    join.erase();
    self.erase();

    // Add decision and decision end to registry
    self.registry.add(decision_node.id(), decision_node);
    self.registry.add(decision_end_node.id(), decision_end_node);
  }
});

var DecisionNode = NodeModule($, IdGeneratorTable, NodeFields);
$.extend(DecisionNode.prototype, ForkNode.prototype, {
  initialize: function(workflow, model, registry) {
    var self = this;
    var registry = registry;

    var end = null;
  },

  end: function() {
    var self = this;

    var end = null;

    $.each(self.child_links(), function(index, link) {
      if (link.name() == 'related') {
        end = self.registry.get(link.child());
      }
    });

    return end;
  },

  /**
   * Append a node to the current decision
   * Also appends end node to node.
   * NOTE: Cannot append a decision or fork! Use addChild or replaceChild instead!
   */
  append: function(node) {
    var self = this;

    if (node.node_type() != 'decision' && node.node_type() != 'fork') {
      var end = self.end();
      if (end.id() != node.id()) {
        var children = end.findChildren();

        self.addChild(node);
        node.append(end);

        // remember children
        $.each(children, function(index, child) {
          end.addChild(child);
        });
      }
    }
  },

  /**
   * Replace child node with another node
   * 1. Remove child if the replacement is end
   * 2. Apply Node.replaceChild for all other causes
   */
  replaceChild: function(child, replacement) {
    var self = this;

    var ret = true;
    var end = self.end();

    if (end && end.id() == replacement.id()) {
      ret = self.removeChild(child);
    } else {
      ret = Node.prototype.replaceChild.apply(self, arguments);
    }

    if (self.links().length < 2) {
      self.detach();
      end.detach();
      self.erase();
      end.erase();
    }

    return ret;
  }
});

/**
 * Workflow module
 */
var WorkflowModule = function($, NodeModelChooser, Node, ForkNode, DecisionNode, IdGeneratorTable) {

  function addHooks(workflow, mapping, model, key) {
    mapping.subscribe(function(value) {
      workflow.is_dirty(true);
    });
  }

  function updateData(mapping, model) {
    // Unstructured data section.
    // Assumes ko.mapping was used to create children.
    // Assumes one of three structures:
    //   - members are literals
    //   - members are arrays of literals
    //   - members are arrays of objects with literal members
    // The point is to keep any parent containers and replace child observables.
    // Templates will likely be tied to parent containers... so if we bubble changes
    // to the parent container... the UI will reflect that.
    $.each(mapping, function(member, value) {
      if (member in model) {
        if ($.isArray(value()) && $.isArray(model[member])) {
          mapping[member].removeAll();
          $.each(model[member], function(key, object_or_literal) {
            if ($.isPlainObject(object_or_literal)) {
              var obj = {};
              $.each(object_or_literal, function(key, literal) {
                obj[key] = ko.mapping.fromJS(literal);
                obj[key].subscribe(function() {
                  mapping[member].valueHasMutated();
                });
              });
              mapping[member].push(obj);
            } else {
              var literal = ko.mapping.fromJS(object_or_literal);
              mapping[member].push(literal);
              literal.subscribe(function() {
                mapping[member].valueHasMutated();
              });
            }
          });
        } else {
          mapping[member](model[member]);
        }
      }
    });
  }

  var module = function(options) {
    var self = this;

    // @see http://knockoutjs.com/documentation/plugins-mapping.html
    var mapping = ko.mapping.fromJS(options.model, {
      ignore: ['initialize', 'toString', 'copy', 'nodes'],
      job_properties: {
        create: function(options) {
          var parent = options.parent;
          var subscribe = function(mapping) {
            mapping.name.subscribe(function(value) {
              parent.job_properties.valueHasMutated();
            });
            mapping.value.subscribe(function(value) {
              parent.job_properties.valueHasMutated();
            });
          };

          return map_params(options, subscribe);
        },
        update: function(options) {
          var parent = options.parent;
          var subscribe = function(mapping) {
            mapping.name.subscribe(function(value) {
              parent.job_properties.valueHasMutated();
            });
            mapping.value.subscribe(function(value) {
              parent.job_properties.valueHasMutated();
            });
          };

          return map_params(options, subscribe);
        }
      },
      parameters: {
        // Will receive individual objects to subscribe.
        // Containing array is mapped automagically
        create: function(options) {
          var parent = options.parent;
          var subscribe = function(mapping) {
            mapping.name.subscribe(function(value) {
              parent.parameters.valueHasMutated();
            });
            mapping.value.subscribe(function(value) {
              parent.parameters.valueHasMutated();
            });
          };

          return map_params(options, subscribe);
        },
        update: function(options) {
          var parent = options.parent;
          var subscribe = function(mapping) {
            mapping.name.subscribe(function(value) {
              parent.parameters.valueHasMutated();
            });
            mapping.value.subscribe(function(value) {
              parent.parameters.valueHasMutated();
            });
          };

          return map_params(options, subscribe);
        }
      },
      data: {
        create: function(options) {
          return map_data(options);
        },
        update: function(options) {
          return map_data(options);
        }
      }
    });

    $.extend(self, mapping);

    $.each(self['__ko_mapping__'].mappedProperties, function(key, value) {
      if (ko.isObservable(self[key])) {
        addHooks(self, self[key], options.model, key);
      } else {
        // Unstructured data object.
        $.each(self[key], function(_key, _value) {
          // @TODO: Don't assume all children are observable
          if (ko.isObservable(self[key][_key])) {
            addHooks(self, self[key][_key], options.model[key], _key);
          }
        });
      }
    });

    self.model = options.model;
    self.registry = options.registry;
    self.options = options;
    self.el = (options.el) ? $(options.el) : $('#workflow');
    self.nodes = ko.observableArray([]);
    self.kill = null;
    self.is_dirty = ko.observable(false);
    self.loading = ko.observable(false);
    self.read_only = ko.observable(options.read_only || false);
    self.new_node = ko.observable();

    // Create fields from the generic data field
    self.sla = ko.computed(function() {
      return self.data.sla();
    });


    self.url = ko.computed(function() {
      return '/oozie/workflows/' + self.id();
    });

    // Events
    self.el.on('workflow:rebuild', function() {
      self.rebuild();
    });
    self.el.on('workflow:events:load', function() {
      self.dragAndDropEvents( options );
    });
    self.el.on('workflow:droppables:load', function() {
      self.droppables();
    });
    self.el.on('workflow:draggables:load', function() {
      self.draggables();
    });

    self.dragAndDropEvents( options );
    self.el.trigger('workflow:events:loaded');

    module.prototype.initialize.apply(self, arguments);

    return self;
  };

  $.extend(module.prototype, {
    // Normal stuff
    initialize: function(options) {
      var self = this;

      $.extend(self.options, options);

      if ('model' in options) {
        self.model = options.model;

        // Initialize nodes
        if (self.model.nodes) {
          self.registry.clear();

          $.each(self.model.nodes, function(index, node) {
            var NodeModel = NodeModelChooser(node.node_type);
            var model = new NodeModel(node);
            var temp = null;
            switch(node.node_type) {
              case 'start':
                temp = new StartNode(self, model, self.registry);
              break;
              case 'fork':
                temp = new ForkNode(self, model, self.registry);
              break;
              case 'decision':
                temp = new DecisionNode(self, model, self.registry);
              break;
              case 'kill':
                temp = self.kill = new Node(self, model, self.registry);
              break;
              case 'subworkflow':
                temp = new SubworkflowNode(self, model, self.registry);
              break;
              default:
                temp = new Node(self, model, self.registry);
              break;
            }

            self.registry.add(temp.id(), temp);
          });
        }

        // Update data
        $.each(self.model, function (key, value) {
          if (key in self) {
            switch(key) {
              case 'job_properties':
              case 'parameters':
                // These may be serialized JSON data since that is how they are stored
                self[key].removeAll();
                var arr;
                try {
                  arr = JSON.parse(value);
                }
                catch (error){
                  arr = value;
                }

                $.each(arr, function(index, obj) {
                  var mapping = ko.mapping.fromJS(obj);
                  mapping.name.subscribe(function(value) {
                    self[key].valueHasMutated();
                  });
                  mapping.value.subscribe(function(value) {
                    self[key].valueHasMutated();
                  });
                  self[key].push(mapping);
                });
              break;

              case 'nodes':
              break;

              case 'data':
                var data = {};
                try {
                  data = JSON.parse(value);
                } catch (error){
                  data = value;
                }
                updateData(self[key], data);
              break;

              default:
                self[key](value);
              break;
            }
          }
        });
        self.is_dirty( false );
      }

      if (!self.kill) {
        var kill_json = {
          "description": "",
          "workflow": self.id(),
          "child_links": [],
          "node_type": "kill",
          "message": "Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]",
          "name": "kill",
          "id": IdGeneratorTable['kill'].nextId()
        };
        var NodeModel = NodeModelChooser(kill_json.node_type);
        var model = new NodeModel(kill_json);
        self.kill = new Node(self, model, self.registry);
        self.registry.add(self.kill.id(), self.kill);
      }

      if ('read_only' in options) {
        self.read_only(options['read_only']);
      }

      if (self.errors) {
        ko.mapping.fromJS(format_errors_mapping(self.model), self.errors);
      } else {
        self.errors = ko.mapping.fromJS(format_errors_mapping(self.model));
      }
    },

    toString: function() {
      return '';
      var s = '[';
      $.each(self.registry.nodes, function(key, node) {
        s += node.model.toString() + ",\n";
      });
      return s + ']';
    },

    // Data manipulation
    toJSON: function() {
      var self = this;

      data = $.extend(true, {}, ko.mapping.toJS(self));

      data['nodes'] = [];
      $.each(self.registry.nodes, function(key, node) {
        // Create object with members from the actual model to address JSON.stringify bug
        // JSON.stringify does not pick up members specified in prototype prior to object creation.
        data['nodes'].push(node.toJS());
      });

      return JSON.stringify(data);
    },

    save: function( options ) {
      var self = this;

      var request = $.extend({
        url: self.url() + '/save',
        type: 'POST',
        data: { workflow: self.toJSON() },
        success: $.noop,
        error: $.noop
      }, options || {});

      $.ajax(request);
    },

    load: function( options ) {
      var self = this;

      var request = $.extend({
        url: self.url(),
        dataType: 'json',
        type: 'GET',
        success: $.noop,
        error: $.noop
      }, options || {});

      $.ajax(request);
    },

    reload: function(model) {
      var self = this;

      // Clear all children
      $.each(self.registry.nodes, function(index, node) {
        node.children.removeAll();
      });
      self.nodes.removeAll();

      self.initialize({model: model});
      self.rebuild();
      self.el.trigger('workflow:loaded');
    },

    addParameter: function(data, event) {
      var self = this;
      var prop = { name: ko.observable(""), value: ko.observable("") };
      // force bubble up to containing observable array.
      prop.name.subscribe(function(){
        self.parameters.valueHasMutated();
      });
      prop.value.subscribe(function(){
        self.parameters.valueHasMutated();
      });
      self.parameters.push(prop);
    },

    removeParameter: function(data, event) {
      var self = this;
      self.parameters.remove(data);
    },

    addJobProperty: function(data, event) {
      var self = this;
      var prop = { name: ko.observable(""), value: ko.observable("") };
      // force bubble up to containing observable array.
      prop.name.subscribe(function(){
        self.job_properties.valueHasMutated();
      });
      prop.value.subscribe(function(){
        self.job_properties.valueHasMutated();
      });
      self.job_properties.push(prop);
    },

    removeJobProperty: function(data, event) {
      var self = this;
      self.job_properties.remove(data);
    },

    // Workflow UI
    // Function to build nodes... recursively.
    build: function() {
      var self = this;

      var maximum = 100;
      var count = 0;

      var methodChooser = function(node, collection, skip_parents_check) {
        if (count++ >= maximum) {
          console.error('Hit maximum number of node recursion: ' + maximum);
          return null;
        }

        if (!node) {
          return node;
        }

        var parents = node.findParents();

        // Found end of decision node or found join!
        if (parents.length > 1 && !skip_parents_check) {
          return node;
        }

        switch(node.node_type()) {
        case 'start':
        case 'end':
        case 'kill':
        case 'fork':
        case 'join':
        case 'decision':
        case 'decisionend':
          return control(node, collection);
        default:
          return normal(node, collection);
        }
      };

      var normal = function(node, collection) {
        collection.push(node);

        var retNode = null;
        $.each(node.links(), function(index, link) {
          var next_node = self.registry.get(link.child());
          retNode = methodChooser(next_node, collection, false, true);
        });
        return retNode;
      };

      var control = function(node, collection, skip_parents_check) {
        switch(node.node_type()) {
          case 'start':
          case 'end':
          case 'kill':
          case 'join':
          case 'decisionend':
            return normal(node, collection, false, true);

          case 'fork':
            collection.push(node);

            // Wait for join.
            // Iterate through all children and add them to child collection.
            var join = null;
            $.each(node.links(), function(index, link) {
              var next_node = self.registry.get(link.child());
              var collection = ko.observableArray([]);
              node.children.push(collection);
              join = methodChooser(next_node, collection, false, true);
            });

            // Add join to collection, then find its single child.
            return methodChooser(join, collection, true, true);

          case 'decision':
            collection.push(node);

            // Waits for end, then runs through children of end node
            var end = null;
            $.each(node.links(), function(index, link) {
              var next_node = self.registry.get(link.child());
              var collection = ko.observableArray([]);
              node.children.push(collection);
              end = methodChooser(next_node, collection, true, true);
            });

            // Add end
            return methodChooser(node.end(), collection, true, true);

          default:
            // Should never get here.
            return node;
        }
      };

      methodChooser(self.registry.get(self.start()), self.nodes, false, true);
      $(".tooltip").remove();
      $("[relz=tooltip]").tooltip({placement: "left", delay: 0});
      $("[relz=tooltip]").hover(function () {
        $(".tooltip").css("left", parseInt($(".tooltip").css("left")) - 10 + "px");
      }, function () {
        $(".tooltip").remove();
      });
    },

    rebuild: function() {
      var self = this;

      // Clear all children
      $.each(self.registry.nodes, function(index, node) {
        node.children.removeAll();
      });
      self.nodes.removeAll();

      // Rebuild
      self.build();
      self.draggables();
      self.droppables();

      self.el.trigger('workflow:rebuilt');
    },

    draggables: function() {
      var self = this;

      self.el.find('.node-action').each(function(index, el) {
        if (!$(el).hasClass('ui-draggable')) {
          $(el).find('ul li a').eq(0).css('cursor', 'move');
          $(el).find('.row-fluid').eq(0).css('cursor', 'move');
          $(el).draggable({
            containment: [ self.el.offset().left - 10, self.el.offset().top - 10,
                           self.el.offset().left + self.el.outerWidth(), self.el.offset().top + self.el.outerHeight() ],
            refreshPositions: true,
            revert: true,
            zIndex: 1000,
            opacity: 0.45,
            revertDuration: 0,
            cancel: '.edit-node-link'
          });
        }
      });
    },

    droppables: function() {
      var self = this;

      self.el.find('.node-link').each(function(index, el) {
        $(el).droppable({
          'hoverClass': 'node-link-hover',
          'greedy': true,
          'accept': '.node-action',
          'tolerance': 'pointer'
        });
      });

      self.el.find('.node-decision-end').each(function(index, el) {
        $(el).droppable({
          'hoverClass': 'node-link-hover',
          'greedy': true,
          'accept': '.node-action',
          'tolerance': 'pointer'
        });
      });

      self.el.find('.node-fork .action').each(function(index, el) {
        $(el).droppable({
          'hoverClass': 'node-fork-hover',
          'greedy': true,
          'accept': '.node-action',
          'tolerance': 'pointer'
        });
      });

      self.el.find('.node-decision .action').each(function(index, el) {
        $(el).droppable({
          'hoverClass': 'node-fork-hover',
          'greedy': true,
          'accept': '.node-action',
          'tolerance': 'pointer'
        });
      });

      self.el.find('.node-action .action').each(function(index, el) {
        $(el).droppable({
          'hoverClass': 'node-action-hover',
          'greedy': true,
          'accept': '.node-action',
          'tolerance': 'pointer'
        });
      });
    },

    dragAndDropEvents: function( options ) {
      var self = this;

      var read_only_error_handler = options.read_only_error_handler;

      // Build event delegations.
      // Drop on node link
      self.el.on('drop', '.node-link', function(e, ui) {
        if (self.read_only()) {
          read_only_error_handler();
          return false;
        }

        // draggable should be a node.
        // droppable should be a link.
        var draggable = ko.contextFor(ui.draggable[0]).$data;
        var droppable = ko.contextFor(this).$data;

        // If newParent is fork, prepend to child instead.
        // This will make it so that we can drop and drop to the top of a node list within a fork.
        var newParent = self.registry.get(droppable.parent());

        if (newParent.id() != draggable.id() && !newParent.isChild(draggable)) {
          switch(newParent.node_type()) {
          case 'fork':
          case 'decision':
            // Children that are forks or decisions may be removed when we detach.
            // Remember children in this case to find correct node.
            var child = self.registry.get(droppable.child());
            var children_of_child = [];
            if (child.node_type() == 'fork' || child.node_type() == 'decision') {
              children_of_child = child.findChildren();
            }

            draggable.detach();

            // Make sure fork and decision still exist
            // Otherwise find child that replaced it
            var child_to_replace = child;
            if (child.node_type() == 'fork' || child.node_type() == 'decision') {
              if (!self.registry.get(child.id())) {
                // Guaranteed one because the fork is being removed right now.
                child_to_replace = $.grep(children_of_child, function(child_of_child, index) {
                  return child_of_child.findParents().length > 0;
                })[0];
              }
            }
            newParent.replaceChild(child_to_replace, draggable);
            draggable.addChild(child_to_replace);
          break;

          case 'join':
          case 'decisionend':
            // Join and decisionend may disappear when we detach...
            // Remember its children and append to child.
            var parents = newParent.findParents();
            draggable.detach();

            if (newParent.findParents().length < 2) {
              $.each(parents, function(index, parent) {
                parent.append(draggable);
              });
            } else {
              newParent.append(draggable);
            }
          break;

          default:
            draggable.detach();
            newParent.append(draggable);
          break;
          }
          workflow.is_dirty( true );
          self.rebuild();
        }

        // Prevent bubbling events
        return false;
      });

      // Drop on fork
      self.el.on('drop', '.node-fork', function(e, ui) {
        if (self.read_only()) {
          read_only_error_handler();
          return false;
        }

        // draggable should be a node.
        // droppable should be a fork.
        var draggable = ko.contextFor(ui.draggable[0]).$data;
        var droppable = ko.contextFor(this).$data;

        if (!droppable.isChild(draggable) && droppable.id() != draggable.id()) {
          draggable.detach();
          droppable.append(draggable);

          self.rebuild();
        }

        // Prevent bubbling events
        return false;
      });

      // Drop on decision
      self.el.on('drop', '.node-decision', function(e, ui) {
        if (self.read_only()) {
          read_only_error_handler();
          return false;
        }

        // draggable should be a node.
        // droppable should be a fork.
        var draggable = ko.contextFor(ui.draggable[0]).$data;
        var droppable = ko.contextFor(this).$data;

        if (!droppable.isChild(draggable) && droppable.id() != draggable.id()) {
          draggable.detach();
          droppable.append(draggable);

          self.rebuild();
        }

        // Prevent bubbling events
        return false;
      });

      // Drop on action
      self.el.on('drop', '.node-action', function(e, ui) {
        if (self.read_only()) {
          read_only_error_handler();
          return false;
        }

        // draggable should be a node.
        // droppable should be a node.
        var draggable = ko.contextFor(ui.draggable[0]).$data;
        var droppable = ko.contextFor(this).$data;

        // Create a fork and join programatically.
        var newParents = droppable.findParents();

        // skip forking beneathe a decision node
        if (droppable.id() != draggable.id() && newParents.length == 1 && draggable.findParents().length <= 1) {
          var ForkModel = NodeModelChooser('fork');
          var JoinModel = NodeModelChooser('join');

          var fork = new ForkModel({
            id: IdGeneratorTable['fork'].nextId(),
            description: "",
            workflow: self.id,
            node_type: "fork",
            child_links: []
          });
          var forkNode = new ForkNode(self, fork, self.registry);

          var join = new JoinModel({
            id: IdGeneratorTable['join'].nextId(),
            description: "",
            workflow: self.id,
            node_type: "join",
            child_links: []
          });
          var joinNode = new Node(self, join, self.registry);

          self.registry.add(forkNode.id(), forkNode);
          self.registry.add(joinNode.id(), joinNode);

          forkNode.addChild(joinNode);

          // Handles fork creation.
          $.each(newParents, function(index, parent) {
            parent.replaceChild(droppable, forkNode);
          });
          draggable.detach();
          forkNode.append(draggable);
          forkNode.append(droppable);

          self.rebuild();
        }

        // Prevent bubbling events.
        return false;
      });
    }
  });

  return module;
};
var Workflow = WorkflowModule($, nodeModelChooser, Node, ForkNode, DecisionNode, IdGeneratorTable);

// Manage Kill Module
function ManageKillModule($, workflow, NodeModelChooser, Node, NodeModel) {
  var email_action = null;
  var parents = workflow.kill.findParents();
  var email_enabled = ko.observable();
  if (parents.length > 0) {
    email_action = parents[0];
    email_enabled(true);
  } else {
    var email_json = {
      "description": "",
      "workflow": workflow.id(),
      "child_links": [],
      "node_type": "email",
      "message": "Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]",
      "name": 'killemail',
      "id": IdGeneratorTable['email'].nextId()
    };
    var NodeModel = NodeModelChooser(email_json.node_type);
    var model = new NodeModel(email_json);
    email_action = new Node(workflow, model, workflow.registry);
    email_enabled(false);
  }

  var replace_email = function(email_action) {
    email_action.removeAllChildren();
    email_action.removeErrorChildren();

    $.each(workflow.registry.nodes, function(index, node) {
      if (node.getErrorChild() && node.id() != email_action.id()) {
        node.putErrorChild(workflow.kill);
      }
    });
  };

  var replace_kill = function(email_action) {
    if (email_action.findChildren().length == 0) {
      email_action.addChild(workflow.kill, 'ok');
    }

    if (!email_action.getErrorChild()) {
      email_action.putErrorChild(workflow.kill);
    }

    $.each(workflow.registry.nodes, function(index, node) {
      if (node.getErrorChild() && node.id() != email_action.id()) {
        node.putErrorChild(email_action);
      }
    });
  };

  // Add/Remove kill email action node from registry so that it is not sent to server.
  email_action.to.subscribe(function(value) {
    if (value && !email_enabled()) {
      workflow.registry.add(email_action.id(), email_action);
      replace_kill(email_action);
      email_enabled(true);
    } else if (!value && email_enabled()) {
      replace_email(email_action);
      email_enabled(false);
      workflow.registry.remove(email_action.id());
      email_action.id(IdGeneratorTable['email'].nextId());
    }

    return value;
  });

  // View model
  return {
    'enabled': email_enabled,
    'isValid': function() {
      return email_action.validate();
    },
    'context': ko.observable({
      'node': ko.observable(email_action),
      'read_only': ko.observable(workflow.read_only())
    })
  };
};
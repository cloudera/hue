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

// open a modal window for editing a node
function edit_node_modal(modal, workflow, node, save, cancel, template) {
  var backup = ko.mapping.toJS(node);
  normalize_model_fields(backup);

  modal.hide();
  modal.setTemplate(template || node.edit_template);
  // Provide node, readonly mode, and error link updater.
  // Kill node is manually added to list of nodes that users can select from.
  // Kill node is placed at the front of the list so that it is automatically selected.
  var context = {
    node: node,
    read_only: workflow.read_only(),
    nodes: ko.computed({
      read: function() {
        var arr = ko.utils.arrayFilter(workflow.registry.allNodes(), function(_node) {
          return _node.id() && _node.id() != node.id() && $.inArray(_node.node_type(), ['start']) == -1;
        });
        return arr;
      }
    }),
    error_node: ko.computed({
      read: function() {
        var error_child  = node.getErrorChild();
        return (error_child) ? error_child.id() : null;
      },
      write: function(node_id) {
        var error_child = workflow.registry.get(node_id);
        if (error_child) {
          node.putErrorChild(error_child);
        }
      }
    })
  };
  modal.show(context);
  modal.recenter(280, 0);
  modal.addDecorations();

  var cancel_edit = cancel || function() {
    ko.mapping.fromJS(backup, node);
    modal.hide();

    // Prevent event propagation
    return false;
  };

  var try_save = save || function() {
    if (node.validate()) {
      workflow.is_dirty( true );
      modal.hide();
    }
  };

  $('.modal-backdrop').on('click', cancel_edit);
  modal.el.on('click', '.close', cancel_edit);
  modal.el.on('click', '.cancelButton', cancel_edit);
  modal.el.on('click', '.doneButton', try_save);

  modal.el.on('click', '.edit-node-link', function() {
    var link = ko.contextFor(this).$data;
    var parent = ko.contextFor(this).$parent;
    var node = parent.registry.get(link.child());

    cancel_edit();

    edit_node_modal(node);
  });
}

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

ko.bindingHandlers.droppable = {
  init: function (element, valueAccessor) {
    var _dropElement = $(element);
    var _options = valueAccessor();

    if (_options.enabled) {
      var _dropOptions = {
        hoverClass: 'drop-target-highlight',
        drop: _options.onDrop
      };
      _dropElement.droppable(_dropOptions);
    }
  }
};


function magicWorkflowLayout(vm) {
  loadWorkflowLayout(vm, vm.initial.layout);
  $(document).trigger("magicWorkflowLayout");
}

function loadWorkflowColumns(viewModel, json_layout) {
  var _columns = [];

  $(json_layout).each(function (cnt, json_col) {
    var _rows = [];
    $(json_col.rows).each(function (rcnt, json_row) {
      var row = new ExtendedRow([], viewModel);
      $(json_row.widgets).each(function (wcnt, widget) {
        var _w = new ExtendedWidget({
          size: widget.size,
          id: widget.id,
          name: widget.name,
          widgetType: widget.widgetType,
          properties: widget.properties,
          offset: widget.offset,
          loading: true,
          vm: viewModel
        });
        row.addWidget(_w);
      });
      row.columns(loadWorkflowColumns(viewModel, json_row.columns));
      _rows.push(row);
    });
    var column = new ExtendedColumn(json_col.size, _rows, viewModel);
    _columns = _columns.concat(column);
  });
  return _columns;
}

function loadWorkflowLayout(viewModel, json_layout) {
  var _cols = loadWorkflowColumns(viewModel, json_layout);
  viewModel.oozieColumns(_cols);
}


// End dashboard lib

var Node = function (node, vm) {
  var self = this;

  var type = typeof node.widgetType != "undefined" ? node.widgetType : node.type;

  self.id = ko.observable(typeof node.id != "undefined" && node.id != null ? node.id : hueUtils.UUID());
  self.name = ko.observable(typeof node.name != "undefined" && node.name != null ? node.name : "");
  self.type = ko.observable(typeof type != "undefined" && type != null ? type : "");

  self.properties = ko.mapping.fromJS(typeof node.properties != "undefined" && node.properties != null ? node.properties : {});
  self.children = ko.mapping.fromJS(typeof node.children != "undefined" && node.children != null ? node.children : []);

  self.associatedDocumentLoading = ko.observable(true);
  self.associatedDocument = ko.observable();

  self.associatedDocumentUuid = ko.observable(typeof node.properties.uuid != "undefined" && node.properties.uuid != null ? node.properties.uuid : null);
  self.associatedDocumentUuid.subscribe(function(val){
    self.properties.uuid(val);
  });

  self.actionParameters = ko.observableArray([]);
  self.actionParametersUI = ko.computed(function () {
    if (typeof self.properties.parameters != "undefined") {
      var _vars = $.map(self.properties.parameters(), function (p, i) {
        return p.value().split('=', 1)[0];
      });
      if (typeof self.actionParameters() == "undefined") {
        return _vars;
      }
      return $.grep(self.actionParameters(), function (param) {
        return _vars.indexOf(param) == -1;
      });
    }
  });
  self.actionParametersFetched = ko.observable(false);

  self.get_link = function (name) {
    var _link = null;
    $.each(self.children(), function (index, link) {
      if (name in link) {
        _link = link;
        return false;
      }
    });
    return _link;
  };

  self.set_link = function (name, node_id) {
    var _link = self.get_link(name);

    if (_link == null) {
      _link = {}
      self.children.push(_link);
    }
    _link[name] = node_id;
    self.children.valueHasMutated();
  };

  self.remove_link = function (name, child) {
    var _link = null;
    $.each(self.children(), function (index, link) {
      var _l = ko.mapping.toJS(link);
      if (name in _l && _l[name] == child) {
        _link = link;
        return false;
      }
    });
    if (_link != null) {
      self.children.remove(_link);
    }
  };

  self.fetch_parameters = function () {
    if (typeof self.properties.parameters != "undefined" && ! self.actionParametersFetched()) { // Fetch once the possible variable when they exist
      $.post("/oozie/editor/workflow/action/parameters/", {
        "node": ko.mapping.toJSON(self),
      }, function (data) {
        self.actionParametersFetched(true);
        self.actionParameters(data.parameters);
        if (data.parameters && data.parameters.length > 0 && self.properties.parameters().length == 0) { // If new node with variables, give a hint by adding a parameter
          self.properties.parameters.push(ko.mapping.fromJS({'value': ''}));
        }
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
      });
    }
  };

  if (typeof self.properties.parameters != "undefined") {
    self.properties.parameters.subscribe(function (newVal) {
      if (newVal) {
        self.fetch_parameters();
      }
    });
  }

  if (typeof self.properties.script_path != "undefined") {
    self.properties.script_path.subscribe(function () {
      self.actionParametersFetched(false);
    });
  }

  if ((type == 'hive-document-widget' || type == 'impala-document-widget' || type == 'spark-document-widget') && typeof self.properties.uuid != "undefined") {
    self.properties.uuid.subscribe(function () {
      self.actionParametersFetched(false);
      self.fetch_parameters();
    });
  }
}


var Workflow = function (vm, workflow) {
  var self = this;

  self.id = ko.observable(typeof workflow.id != "undefined" && workflow.id != null ? workflow.id : null);
  self.uuid = ko.observable(typeof workflow.uuid != "undefined" && workflow.uuid != null ? workflow.uuid : hueUtils.UUID());
  self.name = ko.observable(typeof workflow.name != "undefined" && workflow.name != null ? workflow.name : "");

  self.tracker = new ChangeTracker(self, ko, {
    ignore: [
      "associatedDocument",
      "associatedDocumentUuid",
      "associatedDocumentLoading",
      "actionParameters",
      "actionParametersFetched",
      "actionParametersUI"
    ]
  }); // from ko.common-dashboard.js

  self.isDirty = ko.computed(function () {
    return self.tracker().somethingHasChanged();
  });

  self.properties = ko.mapping.fromJS(typeof workflow.properties != "undefined" && workflow.properties != null ? workflow.properties : {});
  self.nodes = ko.observableArray([]);

  self.versions = ko.mapping.fromJS(['uri:oozie:workflow:0.4', 'uri:oozie:workflow:0.4.5', 'uri:oozie:workflow:0.5']);
  self.movedNode = null;
  self.properties.show_arrows.subscribe(function (newVal) {
    if (newVal) {
      $(document).trigger("drawArrows");
    }
    else {
      $(document).trigger("removeArrows");
    }
  });

  self.nodeIds = ko.computed(function () {
    var mapping = [];

    $.each(self.nodes(), function (index, node) {
      mapping.push(node.id());
    });

    return mapping;
  });
  self.nodeNamesMapping = ko.computed(function () {
    var mapping = {};

    $.each(self.nodes(), function (index, node) {
      mapping[node.id()] = node.name();
    });

    return mapping;
  });
  self.linkMapping = ko.computed(function () {
    var mapping = {};

    $.each(self.nodes(), function (index, node) {
      var links = []
      $.each(node.children(), function (index, link) {
        if ('to' in link) {
          links.push(link['to']);
        }
      });
      mapping[node.id()] = links
    });

    return mapping;
  });

  self.linkMapping.subscribe(function (newVal) {
    $(document).trigger("drawArrows");
  });

  self.loadNodes = function (workflow) {
    var nodes = []
    $.each(workflow.nodes, function (index, node) {
      var _node = new Node(node, vm);
      nodes.push(_node);
    });
    self.nodes(nodes)
  }

  self.newNode = function (widget, callback, sourceNode) {
    $.ajax({
      type: "POST",
      url: "/oozie/editor/workflow/new_node/",
      data: {
        "node": ko.mapping.toJSON(widget)
      },
      success: function (data) {
        if (data.status == 0) {
          window.workflowEditorViewModel.addActionProperties.removeAll();
          $.each(data.properties, function (i, prop) {
            window.workflowEditorViewModel.addActionProperties.push(ko.mapping.fromJS(prop));
          });

          if (data.workflows.length > 0) {
            window.workflowEditorViewModel.subworkflows(getOtherSubworkflows(window.workflowEditorViewModel, data.workflows));
          }

          if (callback) {
            callback(widget, sourceNode);
          }
        }
      }
    });
    hueAnalytics.log('oozie/editor/workflow', 'new_node/' + widget.widgetType());
  };

  self.addNode = function (widget, copiedNode) {
    $.post("/oozie/editor/workflow/add_node/", {
      "node": ko.mapping.toJSON(widget),
      "properties": ko.mapping.toJSON(window.workflowEditorViewModel.addActionProperties()),
      "copiedProperties": copiedNode ? ko.mapping.toJSON(copiedNode.properties) : "{}"
    }, function (data) {
      if (data.status == 0) {
        var _node = ko.mapping.toJS(widget);
        _node.properties = data.properties;
        _node.name = data.name;

        if (self.movedNode) {
          var node = self.movedNode;
          self.movedNode = null;
        } else {
          var node = new Node(_node, vm);
          node.fetch_parameters();
        }

        self.nodes.push(node);

        // If added to the side
        if (vm.currentlyCreatingFork) {
          var parentWidget = vm.getWidgetPredecessor(node.id());
          var parent = self.getNodeById(parentWidget.id());

          if (self.getNodeById(parentWidget.id()) == null) { // New fork

            vm.currentlyCreatedJoin.properties['fork_id'] = vm.currentlyCreatedFork.id;
            vm.currentlyCreatedFork.properties['join_id'] = vm.currentlyCreatedJoin.id;

            var fork = new Node(vm.currentlyCreatedFork, vm);
            var join = new Node(vm.currentlyCreatedJoin, vm);

            self.nodes.push(fork);
            self.nodes.push(join);

            var forkParent = self.getNodeById(vm.getWidgetPredecessor(parentWidget.id()).id());

            // In case of Fork of Fork, we need to pick the link of the neighbor of new node instead of just the first forkParent.get_link('to')
            var newParentLink = $.grep(forkParent.children(), function (link) {
              var _link = ko.mapping.toJS(link)
              return 'to' in _link && vm.getWidgetPredecessor(_link['to']).id() == fork.id();
            })[0];

            var afterParentId = ko.mapping.toJS(newParentLink).to;
            var afterParent = self.getNodeById(afterParentId);
            fork.children.push({'to': afterParentId, 'condition': '${ 1 gt 0 }'});
            fork.children.push({'to': node.id(), 'condition': '${ 1 gt 0 }'});

            newParentLink['to'] = fork.id();

            var belowJoin = vm.getWidgetSuccessor(join.id());
            join.set_link('to', belowJoin.id());

            if (afterParent.type() == 'fork-widget') {
              self.getNodeById(afterParent.properties.join_id()).set_link('to', join.id());
            } else {
              afterParent.set_link('to', join.id());
            }

            node.set_link('to', join.id());
            node.set_link('error', '17c9c895-5a16-7443-bb81-f34b30b21548');
          } else {
            // Just add to existing fork
            var join = vm.getWidgetSuccessor(node.id());
            node.set_link('to', join.id());
            node.set_link('error', '17c9c895-5a16-7443-bb81-f34b30b21548');

            parent.children.push({'to': node.id(), 'condition': '${ 1 gt 0 }'});
          }
        } else {
          var parentWidget = vm.getWidgetPredecessor(node.id());
          var parent = self.getNodeById(parentWidget.id());

          if (widget.widgetType() == 'kill-widget') {
            parent.set_link('to', node.id());
          } else if (parentWidget.widgetType() == 'fork-widget') {
            var child = vm.getWidgetSuccessor(node.id());
            parent.remove_link('to', child.id());
            parent.children.push({'to': node.id(), 'condition': '${ 1 gt 0 }'});

            node.set_link('to', child.id());
            node.set_link('error', '17c9c895-5a16-7443-bb81-f34b30b21548');
          } else {
            // Parent is regular node
            node.set_link('to', parent.get_link('to')['to']);
            node.set_link('error', '17c9c895-5a16-7443-bb81-f34b30b21548');

            parent.set_link('to', node.id());
          }
        }

        vm.currentlyCreatingFork = false;
      } else {
        $(document).trigger("error", data.message);
      }
    }).fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });
    hueAnalytics.log('oozie/editor/workflow', 'add_node');
  };

  self.removeNode = function (node_id) {
    var node = self.getNodeById(node_id);

    var parents = self.getParents(node_id);
    var parent = null;
    var childLink = null;
    if (node) {
      childLink = node.get_link('to');
    }
    if (childLink) {
      var childId = ko.mapping.toJS(childLink)['to'];

      $.each(parents, function (index, _parent) {
        _parent.remove_link('to', node_id);
        _parent.children.unshift({'to': childId});
        parent = _parent;
      });

      self.nodes.remove(node);

      // If need to remove fork

      if (parent.type() == 'fork-widget') {
        var fork = parent;
        var join = self.getNodeById(childId);

        if (join.type() == 'join-widget') {
          if (fork.children().length == 2) {
            // Link top to above and delete fork
            fork.remove_link('to', childId);
            var forkParent = self.getParents(fork.id())[0];
            if (forkParent.type() == 'fork-widget') {
              forkParent.remove_link('to', fork.id());
              forkParent.children.push({'to': ko.mapping.toJS(fork.get_link('to'))['to'], 'condition': '${ 1 gt 0 }'});
            } else {
              forkParent.set_link('to', ko.mapping.toJS(fork.get_link('to'))['to']); // Only link
            }

            self.nodes.remove(fork);

            // Link bottom to child of join
            var beboreJoin = self.getParents(childId)[0];
            var joinChildId = ko.mapping.toJS(join.get_link('to'))['to'];
            beboreJoin.set_link('to', joinChildId);

            self.nodes.remove(join);
          } else {
            parent.remove_link('to', childId);
          }
        }
      }
    }
    else {
      self.nodes.remove(node);
    }
    hueAnalytics.log('oozie/editor/workflow', 'remove_node');
  };

  self.moveNode = function (widget) {
    var node = self.getNodeById(widget.id());
    self.movedNode = node;

    self.removeNode(node.id());
    self.addNode(widget);
  };

  self.getParents = function (node_id) { // Join nodes can have multiple parents
    var _nodes = [];
    $.each(self.nodes(), function (index, node) {
      $.each(node.children(), function (index, link) {
        var _link = ko.mapping.toJS(link);
        if ('to' in _link && _link.to == node_id) {
          _nodes.push(node);
        }
      })
    });
    return _nodes;
  };

  self.getNodeById = function (node_id) {
    var _node = null;
    $.each(self.nodes(), function (index, node) {
      if (node.id() == node_id) {
        _node = node;
        return false;
      }
    });
    return _node;
  };

  self.hasKillNode = ko.pureComputed(function() {
    return $.grep(self.nodes(), function(node) {
      return node.type() == 'kill-widget';
    }).length > 0;
  });
}

var WorkflowEditorViewModel = function (layout_json, workflow_json, credentials_json, workflow_properties_json, subworkflows_json, can_edit_json) {
  var self = this;

  self.isNested = ko.observable(true);

  self.currentDraggableSection = ko.observable();
  self.currentDraggableSection.subscribe(function (newVal) {
    huePubSub.publish('oozie.draggable.section.change', newVal);
  });

  self.sharingEnabled = ko.observable(false);

  var updateFromConfig = function (hueConfig) {
    self.sharingEnabled(
      hueConfig && (hueConfig.hue_config.is_admin || hueConfig.hue_config.enable_sharing)
    );
  };

  updateFromConfig(window.getLastKnownConfig());
  huePubSub.subscribe('cluster.config.set.config', updateFromConfig);

  self.canEdit = ko.mapping.fromJS(can_edit_json);
  self.isEditing = ko.observable(workflow_json.id == null);
  self.isEditing.subscribe(function (newVal) {
    $(document).trigger("editingToggled");
  });
  self.toggleEditing = function () {
    self.isEditing(!self.isEditing());
  };
  self.isToolbarVisible = ko.pureComputed(function(){
    return self.isEditing();
  })
  self.isSaving = ko.observable(false);

  self.isInvalid = ko.observable(false);
  self.isRunning = ko.observable(false);

  self.newAction = ko.observable();

  self.columns = ko.observableArray([]);
  self.oozieColumns = ko.observableArray([]);
  self.availableActions = ko.observableArray([]);

  self.availableNamespaces = ko.observableArray();
  self.namespace = ko.observable();
  self.availableComputes = ko.observableArray();
  self.compute = ko.observable();

  contextCatalog.getNamespaces({ connector: { id: 'oozie' } }).done(function (context) { self.availableNamespaces(context.namespaces) });
  contextCatalog.getComputes({ connector: { id: 'oozie' } }).done(self.availableComputes);


  self.previewColumns = ko.observable("");
  self.workflow = new Workflow(self, workflow_json);
  self.credentials = ko.mapping.fromJS(credentials_json);

  self.inited = ko.observable(self.oozieColumns().length > 0);
  self.init = function (callback) {
    self.workflow_properties = ko.mapping.fromJS(workflow_properties_json);
    loadWorkflowLayout(self, layout_json);
    self.workflow.loadNodes(workflow_json);
    self.workflow.tracker().markCurrentStateAsClean();
  };

  self.tempDocument = ko.observable();

  self.addActionProperties = ko.observableArray([]);
  self.addActionPropertiesFilledOut = ko.computed(function () {
    var _filledInternalValues = function (val) {
      var _iAllFilled = true;
      val.forEach(function (iVal) {
        if (iVal.value() == '') {
          _iAllFilled = false;
        }
      });
      return _iAllFilled;
    }
    var _allFilled = true;
    ko.utils.arrayForEach(self.addActionProperties(), function (property) {
      var _val = property.value();
      if (($.isArray(_val) && !_filledInternalValues(_val) ) || _val == '' || _val == null || typeof _val == 'undefined') {
        _allFilled = false;
      }
    });
    return _allFilled;
  });


  self.subworkflows = ko.observableArray(getOtherSubworkflows(self, subworkflows_json));

  self.getSubWorkflow = function (uuid) {
    var wf = $.grep(self.subworkflows(), function (wf, i) {
      return wf.value == uuid;
    });
    if (wf[0]) {
      return ko.mapping.fromJS(wf[0]);
    }
  };

  self.currentlyDraggedWidget = ko.observable(null);
  self.currentlyDraggedOp = ko.observable("move");
  self.currentlyDraggedWidget.subscribe(function (widget) {
    toggleSideDrop(widget, false);
  });

  self.setCurrentlyDraggedWidget = function (widget, op) {
    self.currentlyDraggedOp($(op).hasClass("fa-copy") ? "copy" : "move");
    self.currentlyDraggedWidget(widget);
  }

  self.enableSideDrop = function (widget) {
    toggleSideDrop(widget, true);
    sideDropsTouched.forEach(function (row) {
      row.enableOozieDropOnSide(true);
    });
    sideDropsTouched = [];
  }

  var sideDropsTouched = [];

  function toggleSideDrop(widget, enable) {
    if (widget != null && widget.id() != "" && self.currentlyDraggedOp() == "move") {
      var _row = self.getWidgetParentRow(widget.id());
      if (_row) {
        _row.enableOozieDropOnSide(enable);
        sideDropsTouched.push(_row);
        _row.enableOozieDropOnBefore(enable);

        var _parentRow = self.getRowParentRow(_row.id());
        if (_parentRow) {
          _parentRow.enableOozieDropOnSide(enable);
          sideDropsTouched.push(_parentRow);
          if (_parentRow.columns().length <= 2) {
            _parentRow.columns().forEach(function (col) {
              col.enableOozieDropOnBefore(enable);
              col.enableOozieDropOnAfter(enable);
              col.rows()[0].enableOozieDropOnSide(enable);
              sideDropsTouched.push(col.rows()[0]);
            });
            var _prevParentRow = self.getPrevRow(_parentRow);
            if (_prevParentRow && _prevParentRow.widgets().length > 0 && _prevParentRow.widgets()[0].widgetType() == "fork-widget") {
              _prevParentRow.enableOozieDropOnSide(enable);
              sideDropsTouched.push(_prevParentRow);
            }
          }
        }

        var _col = self.getRowParentColumn(_row.id());
        if (self.getColumnParentRow(_col.id()) != null) {
          _col.enableOozieDropOnBefore(enable);
          _col.enableOozieDropOnAfter(enable);
        }

        var _prevRow = self.getPrevRow(_row);
        if (_prevRow) {
          if (_prevRow.widgets().length > 0 && _prevRow.widgets()[0].widgetType() == "start-widget") {
            _prevRow.enableOozieDropOnSide(enable);
            sideDropsTouched.push(_prevRow);
            self.getRowParentColumn(_prevRow.id()).enableOozieDropOnBefore(enable);
          }
        }
        var _nextRow = self.getNextRow(_row);
        if (_nextRow) {
          _nextRow.enableOozieDropOnBefore(enable);
          if (_nextRow.widgets().length > 0 && _nextRow.widgets()[0].widgetType() == "end-widget") {
            _nextRow.enableOozieDropOnSide(enable);
            sideDropsTouched.push(_nextRow);
            self.getRowParentColumn(_nextRow.id()).enableOozieDropOnAfter(enable);
          }
        }
      }
    }
  }

  self.currentlyCreatingFork = false;
  self.currentlyCreatedFork = null;
  self.currentlyCreatedJoin = null;
  self.isDragging = ko.observable(false);

  self.addDraggedWidget = function (target, atBeginning) {
    if (self.currentlyDraggedWidget() != null) {
      var _parentCol = target instanceof Column ? target : self.getRowParentColumn(target.id());

      var _newRow = null;
      if (typeof atBeginning != "undefined") {
        if (_parentCol.rows().length > 0 && _parentCol.rows()[0].widgets() && _parentCol.rows()[0].widgets().length > 0 && _parentCol.rows()[0].widgets()[0].widgetType() == "start-widget") {
          if (atBeginning) {
            _newRow = _parentCol.addEmptyRow(false, 1);
          }
          else {
            _newRow = _parentCol.addEmptyRow(false, _parentCol.rows().length - 2);
          }
        }
        else {
          _newRow = _parentCol.addEmptyRow(atBeginning);
        }
      }
      else {
        var _rowIdx = 0;
        $.each(_parentCol.rows(), function (i, irow) {
          if (irow.id() == target.id()) {
            _rowIdx = i;
          }
        });

        _newRow = _parentCol.addEmptyRow(false, _rowIdx);
      }

      var _w = new ExtendedWidget({
        size: self.currentlyDraggedWidget().size(),
        id: hueUtils.UUID(),
        name: self.currentlyDraggedWidget().name(),
        widgetType: self.currentlyDraggedWidget().widgetType(),
        properties: self.currentlyDraggedWidget().properties(),
        offset: self.currentlyDraggedWidget().offset(),
        loading: true,
        vm: self
      });

      if (self.currentlyDraggedWidget().id() != "" && self.currentlyDraggedOp() == "move") {
        self.removeWidgetById(self.currentlyDraggedWidget().id());
        _w = self.currentlyDraggedWidget();
      }

      _newRow.widgets([_w]);

      return _w;
    }
  }

  self.addSideDraggedWidget = function (row, atBeginning) {
    if (self.currentlyDraggedWidget() != null) {
      var _parentCol = self.getRowParentColumn(row.id());
      var _rowIdx = 0;
      $.each(_parentCol.rows(), function (i, irow) {
        if (irow.id() == row.id()) {
          _rowIdx = i;
        }
      });

      var _addForkAndJoin = (row.columns().length == 0);

      if (_addForkAndJoin) {
        var _forkRow = _parentCol.addEmptyRow(false, _rowIdx);
        var _id = hueUtils.UUID();
        var _fork = new ExtendedWidget({
          size: 12,
          id: _id,
          name: 'fork' + '-' + _id.slice(0, 4),
          widgetType: "fork-widget",
          properties: {},
          offset: 0,
          loading: true,
          vm: self
        });

        _forkRow.widgets([_fork]);
      }

      var _w = new ExtendedWidget({
        size: self.currentlyDraggedWidget().size(),
        id: hueUtils.UUID(),
        name: self.currentlyDraggedWidget().name(),
        widgetType: self.currentlyDraggedWidget().widgetType(),
        properties: self.currentlyDraggedWidget().properties(),
        offset: self.currentlyDraggedWidget().offset(),
        loading: true,
        vm: self
      });

      if (self.currentlyDraggedWidget().id() != "" && self.currentlyDraggedOp() == "move") {
        self.removeWidgetById(self.currentlyDraggedWidget().id());
        _w = self.currentlyDraggedWidget();
      }

      if (row.columns().length == 0) {
        var _col = row.addColumn(null, atBeginning);
        if (row.widgets().length > 0) {
          var _row = _col.addEmptyRow();
          row.widgets().forEach(function (widget) {
            _row.addWidget(widget);
          });
          if (row.widgets()[0].widgetType() == "fork-widget") {
            var _widgetsRow = self.getNextRow(row);
            var _joinRow = self.getNextRow(_widgetsRow);
            _col.rows.push(_widgetsRow);
            _col.rows.push(_joinRow);
            self.getRowParentColumn(row.id()).rows.remove(_widgetsRow);
            self.getRowParentColumn(row.id()).rows.remove(_joinRow);
          }
          row.widgets([]);
        }
      }

      var _col = row.addColumn(null, atBeginning);
      var _row = new ExtendedRow([_w], self);
      _col.addRow(_row);

      if (_addForkAndJoin) {
        var _joinRow = _parentCol.addEmptyRow(false, _rowIdx + 2);
        var _id = hueUtils.UUID();
        var _join = new ExtendedWidget({
          size: 12,
          id: _id,
          name: "join" + '-' + _id.slice(0, 4),
          widgetType: "join-widget",
          properties: {},
          offset: 0,
          loading: true,
          vm: self
        });

        _joinRow.widgets([_join]);
        self.currentlyCreatedFork = ko.mapping.toJS(_fork);
        self.currentlyCreatedJoin = ko.mapping.toJS(_join);
      }

      self.currentlyCreatingFork = true;

      return _w;
    }
  }

  self.getAllWidgets = function () {
    var _widgets = [];

    for (var i = 0; i < self.oozieColumns().length; i++) {
      _widgets = _widgets.concat(self.deeplyGetAllWidgets(self.oozieColumns()[i]));
    }

    return _widgets;
  }

  self.deeplyGetAllWidgets = function (col) {
    var _widgets = [];
    if (col) {
      for (var j = 0; j < col.rows().length; j++) {
        var row = col.rows()[j];
        if (row && row.widgets()) {
          for (var z = 0; z < row.widgets().length; z++) {
            _widgets = _widgets.concat(row.widgets()[z]);
          }
        }
        if (row && row.columns()) {
          for (var i = 0; i < row.columns().length; i++) {
            _widgets = _widgets.concat(self.deeplyGetAllWidgets(row.columns()[i]));
          }
        }
      }
    }
    return _widgets;
  }

  self.getWidgetById = function (widget_id) {
    var _widget = null;

    for (var i = 0; i < self.oozieColumns().length; i++) {
      _widget = self.deeplyGetWidgetById(widget_id, self.oozieColumns()[i]);
      if (_widget != null) {
        break;
      }
    }

    return _widget;
  }

  self.deeplyGetWidgetById = function (widget_id, col) {
    var _widget = null;
    if (col) {
      for (var j = 0; j < col.rows().length; j++) {
        var row = col.rows()[j];
        if (row && row.widgets()) {
          for (var z = 0; z < row.widgets().length; z++) {
            var widget = row.widgets()[z];
            if (widget.id() == widget_id) {
              _widget = widget;
            }
            if (_widget != null) {
              break;
            }
          }
        }
        if (_widget != null) {
          break;
        }
        if (row && row.columns() && _widget == null) {
          for (var i = 0; i < row.columns().length; i++) {
            _widget = self.deeplyGetWidgetById(widget_id, row.columns()[i]);
            if (_widget != null) {
              break;
            }
          }
        }
      }
    }
    return _widget;
  }

  self.removeWidget = function (widget_json) {
    self.workflow.removeNode(widget_json.id());
    self.removeWidgetById(widget_json.id());
    self.cleanupDeadWidgets();
  }

  self.removeWidgetById = function (widget_id) {
    $.each(self.oozieColumns(), function (i, col) {
      self.deeplyRemoveWidgetById(widget_id, col, self)
    });
  }

  self.cleanupDeadWidgets = function () {
    var _modelWidgets = Object.keys(self.workflow.linkMapping());
    var _uiWidgets = self.getAllWidgets();
    _uiWidgets.forEach(function(widget){
      if (_modelWidgets.indexOf(widget.id()) == -1){
        self.removeWidgetById(widget.id());
      }
    });
  }

  self.deeplyRemoveWidgetById = function (widget_id, col, parent) {
    if (col) {
      $.each(col.rows(), function (j, row) {
        if (row && row.widgets()) {
          $.each(row.widgets(), function (z, widget) {
            if (widget.id() == widget_id) {
              row.widgets.remove(widget);
              col.rows.remove(row);
            }
          });
        }
        if (row && row.columns()) {
          $.each(row.columns(), function (i, icol) {
            self.deeplyRemoveWidgetById(widget_id, icol, row);
          });
        }
      });
      if (col.rows().length == 0) {
        parent.columns.remove(col);
        if (parent.columns().length > 1) {
          var _size = Math.max(1, Math.floor(12 / (parent.columns().length)));
          parent.columns().forEach(function (icol) {
            icol.size(_size);
          });
        }
        else {
          var _rows = parent.columns()[0].rows();
          var _parentRows = self.getRowParentColumn(parent.id()).rows;
          var _prevRowIdx = -1;
          for (var i = 0; i < _parentRows().length; i++) {
            if (_parentRows()[i].id() == parent.id()) {
              break;
            }
            _prevRowIdx = i;
          }

          if (_prevRowIdx > -1 && _parentRows()[_prevRowIdx].widgets().length > 0 && _parentRows()[_prevRowIdx].widgets()[0].widgetType() == "fork-widget") {
            _parentRows.remove(_parentRows()[_prevRowIdx]);
            _parentRows.remove(_parentRows()[_prevRowIdx + 1]);
          }

          for (var i = 0; i < _rows.length; i++) {
            if (i == 0) {
              parent.widgets(_rows[i].widgets());
            }
            else {
              _parentRows.push(_rows[i]);
            }
          }
          parent.columns([]);
        }
      }
    }
  }

  self.getWidgetRelative = function (widget_id, isPredecessor) {
    // fixes the order of the main column first
    if (self.oozieColumns()[0].rows().length > 3) {
      if (self.oozieColumns()[0].rows()[1].widgets()[0].id() == "33430f0f-ebfa-c3ec-f237-3e77efa03d0a") { // end widget
        self.oozieColumns()[0].rows().move(1, self.oozieColumns()[0].rows().length - 1);
      }
      if (self.oozieColumns()[0].rows()[1].widgets()[0].id() ==  "17c9c895-5a16-7443-bb81-f34b30b21548") { // kill widget
        self.oozieColumns()[0].rows().move(1, self.oozieColumns()[0].rows().length - 1);
      }
    }
    var _row = self.getWidgetParentRow(widget_id);
    var _col = self.getRowParentColumn(_row.id());
    var _nextRow = null;
    for (var i = 0; i < _col.rows().length; i++) {
      if (_col.rows()[i].id() == _row.id()) {
        if (!isPredecessor && _col.rows().length >= i + 1) {
          _nextRow = _col.rows()[i + 1];
        }
        break;
      }
      _nextRow = _col.rows()[i];
    }
    if (_nextRow != null) {
      return _nextRow.widgets()[0];
    }
    else {
      var _parentRow = self.getColumnParentRow(_col.id());
      if (_parentRow) {
        var _parentColumn = self.getRowParentColumn(_parentRow.id());
        var _nextParentRow = null;
        for (var i = 0; i < _parentColumn.rows().length; i++) {
          if (_parentColumn.rows()[i].id() == _parentRow.id()) {
            if (!isPredecessor && _parentColumn.rows().length >= i + 1) {
              _nextParentRow = _parentColumn.rows()[i + 1];
            }
            break;
          }
          _nextParentRow = _parentColumn.rows()[i];
        }
        if (_nextParentRow != null) {
          return _nextParentRow.widgets()[0];
        }
      }
    }
    return null;
  }

  self.getWidgetPredecessor = function (widget_id) {
    return self.getWidgetRelative(widget_id, true);
  }

  self.getWidgetSuccessor = function (widget_id) {
    return self.getWidgetRelative(widget_id, false);
  }

  self.isRowAfterFork = function (row) {
    var _parentColumn = self.getRowParentColumn(row.id());
    var _prevRow = null;
    if (_parentColumn != null) {
      for (var i = 0; i < _parentColumn.oozieRows().length; i++) {
        var _currentRow = _parentColumn.oozieRows()[i];
        if (_currentRow.id() == row.id()) {
          break;
        }
        _prevRow = _currentRow;
      }
      if (_prevRow != null) {
        return _prevRow.widgets().length > 0 && (_prevRow.widgets()[0].widgetType() == "fork-widget" || _prevRow.widgets()[0].widgetType() == "decision-widget");
      }
    }
    return false;
  }

  self.isRowBeforeJoin = function (row) {
    return row.widgets().length > 0 && row.widgets()[0].widgetType() == "join-widget";
  }

  self.getNextRow = function (row) {
    var _parentColumn = self.getRowParentColumn(row.id());
    var _nextParentRow = null;
    for (var i = 0; i < _parentColumn.rows().length; i++) {
      if (_parentColumn.rows()[i].id() == row.id()) {
        if (_parentColumn.rows().length >= i + 1) {
          _nextParentRow = _parentColumn.rows()[i + 1];
        }
        break;
      }
      _nextParentRow = _parentColumn.rows()[i];
    }
    return _nextParentRow;
  }

  self.getPrevRow = function (row) {
    var _parentColumn = self.getRowParentColumn(row.id());
    var _prevParentRow = null;
    for (var i = 0; i < _parentColumn.rows().length; i++) {
      if (_parentColumn.rows()[i].id() == row.id()) {
        if (i > 0) {
          _prevParentRow = _parentColumn.rows()[i - 1];
        }
        break;
      }
      _prevParentRow = _parentColumn.rows()[i];
    }
    return _prevParentRow;
  }

  self.getWidgetParentRow = function (widget_id) {
    var _row = null;
    for (var i = 0; i < self.oozieColumns().length; i++) {
      _row = self.traverseColumnForWidget(widget_id, self.oozieColumns()[i]);
      if (_row != null) {
        break;
      }
    }
    return _row;
  }

  self.getRowParentColumn = function (row_id) {
    return self.traverseColumnForColumn(row_id, self.oozieColumns()[0], 0);
  }

  self.getColumnParentRow = function (col_id) {
    return self.traverseColumnForRow(col_id, self.oozieColumns()[0], 0);
  }

  self.getRowParentRow = function (row_id) {
    var _col = self.getRowParentColumn(row_id);
    if (_col != null) {
      return self.getColumnParentRow(_col.id());
    }
  }

  self.traverseColumnForColumn = function (row_id, col) {
    var _column = null;
    if (col) {
      for (var j = 0; j < col.rows().length; j++) {
        var row = col.rows()[j];

        for (var z = 0; z < row.columns().length; z++) {
          _column = self.traverseColumnForColumn(row_id, row.columns()[z]);
          if (_column != null) {
            return _column;
          }
        }

        if (row.id() == row_id) {
          _column = col;
          return _column;
        }

      }
    }
    return _column;
  }

  self.traverseColumnForRow = function (col_id, col) {
    var _row = null;
    if (col) {
      for (var j = 0; j < col.rows().length; j++) {
        var row = col.rows()[j];
        for (var z = 0; z < row.columns().length; z++) {
          var _col = row.columns()[z];
          if (_col.id() == col_id) {
            _row = row;
          }
          else {
            _row = self.traverseColumnForRow(col_id, _col);
          }
          if (_row != null) {
            return _row;
          }
        }
      }
    }
    return _row;
  }

  self.traverseColumnForWidget = function (widget_id, col) {
    var _row = null;
    if (col) {
      for (var j = 0; j < col.rows().length; j++) {
        var row = col.rows()[j];
        for (var z = 0; z < row.widgets().length; z++) {
          var widget = row.widgets()[z];
          if (widget.id() == widget_id) {
            _row = row;
            break;
          }
        }
        if (_row != null) {
          break;
        }
        for (var z = 0; z < row.columns().length; z++) {
          _row = self.traverseColumnForWidget(widget_id, row.columns()[z]);
          if (_row != null) {
            break;
          }
        }
      }
    }
    return _row;
  }

  self.convertToDecision = function (widget, node) {
    if (widget.widgetType() == "fork-widget") {
      var _row = self.getWidgetParentRow(widget.id());
      var _next = self.getNextRow(_row);
      while (_next.widgets().length == 0) {
        _next = self.getNextRow(_next);
      }

      // Remove the join
      self.workflow.removeNode(_next.widgets()[0].id());
      self.removeWidgetById(_next.widgets()[0].id());

      node.children.push({'to': '33430f0f-ebfa-c3ec-f237-3e77efa03d0a', 'condition': 'default'});

      widget.widgetType("decision-widget");
      node.type("decision-widget");
      var _newName = "decision-" + node.id().slice(0, 4);
      node.name(_newName);
      widget.name(_newName);
      $(document).trigger("drawArrows");
    }
  };

  self.save = function () {
    if (! self.isSaving()) {
      self.isSaving(true);
      $(".jHueNotify").remove();
      $.post("/oozie/editor/workflow/save/", {
        "layout": ko.mapping.toJSON(self.oozieColumns),
        "workflow": ko.mapping.toJSON(self.workflow)
      }, function (data) {
        if (data.status == 0) {
          if (data.url) {
            window.location.replace(data.url);
          }
          if (self.workflow.id() == null) {
            shareViewModel.setDocUuid(data.doc_uuid);
          }
          self.workflow.id(data.id);
          $(document).trigger("info", data.message);
          self.workflow.tracker().markCurrentStateAsClean();
          huePubSub.publish('assist.document.refresh');
          hueUtils.changeURL('/hue/oozie/editor/workflow/edit/?workflow=' + data.id);
        } else {
          $(document).trigger("error", data.message);
        }
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
      }).always(function () {
        self.isSaving(false);
      });
    hueAnalytics.log('oozie/editor/workflow', 'save');
    }
  };

  self.gen_xml = function () {
    $.post("/oozie/editor/workflow/gen_xml/", {
      "layout": ko.mapping.toJSON(self.oozieColumns),
      "workflow": ko.mapping.toJSON(self.workflow)
    }, function (data) {
      if (data.status == 0) {
        console.log(data.xml);
      }
      else {
        $(document).trigger("error", data.message);
      }
    }).fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });
  };

  self.showSubmitPopup = function () {
    $(".jHueNotify").remove();
    $.get("/oozie/editor/workflow/submit/" + self.workflow.id(), {
      format: 'json',
      cluster: self.compute() ? ko.mapping.toJSON(self.compute()) : '{}'
    }, function (data) {
      $(document).trigger("showSubmitPopup", data);
    }).fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });
  };

  self.showSubmitActionPopup = function (w) {
    $(".jHueNotify").remove();
    $.get("/oozie/editor/workflow/submit_single_action/" + self.workflow.id() + "/" + self.workflow.getNodeById(w.id()).id(), {
      format: 'json'
    }, function (data) {
      $(document).trigger("showSubmitPopup", data);
    }).fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });
  };

  self.schedule = function () {
    hueAnalytics.log('oozie/editor/workflow', 'schedule');
    huePubSub.publish('open.link', '/oozie/editor/coordinator/new/?workflow=' + self.workflow.uuid());
  };


  self.drawArrows = function () {
    function linkWidgets(fromId, toId) {
      var _from = $("#wdg_" + (typeof fromId == "function" ? fromId() : fromId));
      var _to = $("#wdg_" + (typeof toId == "function" ? toId() : toId));
      if (_from.length > 0 && _to.length > 0) {
        var $painter = $(document.body);
        var heightCorrection = 0;
        var widthCorrection = 0;

        var $workflowWidgets = $('.workflow-widgets');
        if ($workflowWidgets.length > 0) {
          $painter = $workflowWidgets;
          heightCorrection = $workflowWidgets.scrollTop();
          widthCorrection = $workflowWidgets.scrollLeft();
        }
       var $jobBrowserGraphTab = $('#workflow-page-graph');
        if ($jobBrowserGraphTab.length > 0) {
          $painter = $jobBrowserGraphTab;
          heightCorrection = $jobBrowserGraphTab.scrollTop();
          widthCorrection = $jobBrowserGraphTab.scrollLeft();
        }

        var _fromCenter = {
          x: _from.position().left + widthCorrection + _from.outerWidth() / 2,
          y: _from.position().top + heightCorrection + _from.outerHeight() + 3
        };

        var _toCenter = {
          x: _to.position().left + widthCorrection + _to.outerWidth() / 2,
          y: _to.position().top + heightCorrection - 5
        };

        var _curveCoords = {};

        if (_fromCenter.x == _toCenter.x) {
          _curveCoords.x = _fromCenter.x;
          _curveCoords.y = _fromCenter.y + (_toCenter.y - _fromCenter.y) / 2;
        } else {
          if (_fromCenter.x > _toCenter.x) {
            _fromCenter.x = _fromCenter.x - 5;
            _toCenter.x = _toCenter.x + 5;
          } else {
            _fromCenter.x = _fromCenter.x + 5;
            _toCenter.x = _toCenter.x - 5;
          }
          _curveCoords.x = _fromCenter.x - (_fromCenter.x - _toCenter.x) / 4;
          _curveCoords.y = _fromCenter.y + (_toCenter.y - _fromCenter.y) / 2;
        }

        $painter.curvedArrow({
          p0x: _fromCenter.x,
          p0y: _fromCenter.y,
          p1x: _curveCoords.x,
          p1y: _curveCoords.y,
          p2x: _toCenter.x,
          p2y: _toCenter.y,
          lineWidth: 2,
          size: 10,
          strokeStyle: self.isEditing() ? '#e5e5e5' : '#dddddd'
        });
      }
    }

    $("canvas").remove();
    if (self.oozieColumns()[0].rows().length > 3) {
      var _links = self.workflow.linkMapping();
      Object.keys(_links).forEach(function (id) {
        if (_links[id].length > 0) {
          _links[id].forEach(function (nextId) {
            linkWidgets(id, nextId);
          });
        }
      });
    }
  }

  function bareWidgetBuilder(name, type) {
    return new ExtendedWidget({
      size: 12,
      id: "",
      name: name,
      widgetType: type
    });
  }

  self.draggableHiveAction = ko.observable(bareWidgetBuilder("Hive Script", "hive-widget"));
  self.draggableHive2Action = ko.observable(bareWidgetBuilder("HiveServer2 Script", "hive2-widget"));
  self.draggableImpalaAction = ko.observable(bareWidgetBuilder("Impala Script", "impala-widget"));
  self.draggableAltusAction = ko.observable(bareWidgetBuilder("Altus Command", "altus-widget"));
  self.draggablePigAction = ko.observable(bareWidgetBuilder("Pig Script", "pig-widget"));
  self.draggableJavaAction = ko.observable(bareWidgetBuilder("Java program", "java-widget"));
  self.draggableMapReduceAction = ko.observable(bareWidgetBuilder("MapReduce job", "mapreduce-widget"));
  self.draggableSubworkflowAction = ko.observable(bareWidgetBuilder("Sub workflow", "subworkflow-widget"));
  self.draggableSqoopAction = ko.observable(bareWidgetBuilder("Sqoop 1", "sqoop-widget"));
  self.draggableShellAction = ko.observable(bareWidgetBuilder("Shell", "shell-widget"));
  self.draggableSshAction = ko.observable(bareWidgetBuilder("Ssh", "ssh-widget"));
  self.draggableFsAction = ko.observable(bareWidgetBuilder("Fs", "fs-widget"));
  self.draggableEmailAction = ko.observable(bareWidgetBuilder("Email", "email-widget"));
  self.draggableStreamingAction = ko.observable(bareWidgetBuilder("Streaming", "streaming-widget"));
  self.draggableDistCpAction = ko.observable(bareWidgetBuilder("Distcp", "distcp-widget"));
  self.draggableSparkAction = ko.observable(bareWidgetBuilder("Spark", "spark-widget"));
  self.draggableGenericAction = ko.observable(bareWidgetBuilder("Generic", "generic-widget"));
  self.draggableHiveDocumentAction = ko.observable(bareWidgetBuilder("Hive", "hive-document-widget"));
  self.draggableImpalaDocumentAction = ko.observable(bareWidgetBuilder("Impala", "impala-document-widget"));
  self.draggableJavaDocumentAction = ko.observable(bareWidgetBuilder("Java", "java-document-widget"));
  self.draggableSparkDocumentAction = ko.observable(bareWidgetBuilder("Spark", "spark-document-widget"));
  self.draggablePigDocumentAction = ko.observable(bareWidgetBuilder("Pig", "pig-document-widget"));
  self.draggableSqoopDocumentAction = ko.observable(bareWidgetBuilder("Sqoop", "sqoop-document-widget"));
  self.draggableDistCpDocumentAction = ko.observable(bareWidgetBuilder("DistCp", "distcp-document-widget"));
  self.draggableShellDocumentAction = ko.observable(bareWidgetBuilder("Shell", "shell-document-widget"));
  self.draggableMapReduceDocumentAction = ko.observable(bareWidgetBuilder("MapReduce", "mapreduce-document-widget"));
  self.draggableKillNode = ko.observable(bareWidgetBuilder("Kill", "kill-widget"));
};


function getOtherSubworkflows(vm, workflows) {
  var _cleanedSubworkflows = [];
  workflows.forEach(function(sub){
    if (sub.id != vm.workflow.id()){
      _cleanedSubworkflows.push(sub);
    }
  });
  return _cleanedSubworkflows;
}

var ExtendedColumn = function (size, rows, viewModel) {
  var self = new Column(size, rows, viewModel);
  self.rowPrototype = ExtendedRow;
  self.oozieStartRow = ko.computed(function () {
    var _row = null;
    ko.utils.arrayForEach(self.rows(), function (row) {
      if ((row.widgets().length > 0 && row.widgets()[0].id() == "3f107997-04cc-8733-60a9-a4bb62cebffc")) {
        _row = row;
      }
    });
    return _row;
  }, self);

  self.oozieEndRow = ko.computed(function () {
    var _row = null;
    ko.utils.arrayForEach(self.rows(), function (row) {
      if ((row.widgets().length > 0 && row.widgets()[0].id() == "33430f0f-ebfa-c3ec-f237-3e77efa03d0a")) {
        _row = row;
      }
    });
    return _row;
  }, self);

  self.oozieKillRow = ko.computed(function () {
    var _row = null;
    ko.utils.arrayForEach(self.rows(), function (row) {
      if ((row.widgets().length > 0 && row.widgets()[0].id() == "17c9c895-5a16-7443-bb81-f34b30b21548")) {
        _row = row;
      }
    });
    return _row;
  }, self);


  self.oozieRows = ko.computed(function () {
    var _rows = [];
    ko.utils.arrayForEach(self.rows(), function (row) {
      if ((row.widgets().length > 0 && ["3f107997-04cc-8733-60a9-a4bb62cebffc", "33430f0f-ebfa-c3ec-f237-3e77efa03d0a", "17c9c895-5a16-7443-bb81-f34b30b21548"].indexOf(row.widgets()[0].id()) == -1) || row.widgets().length == 0) {
        _rows.push(row);
      }
    });
    return _rows;
  }, self);

  self.enableOozieDropOnBefore = ko.observable(true);
  self.enableOozieDropOnAfter = ko.observable(true);

  return self;
}

var ExtendedRow = function (widgets, vm, columns) {
  var self = new Row(widgets, vm, columns);
  self.columnPrototype = ExtendedColumn;
  self.enableOozieDrop = ko.computed(function () {
    return vm.isEditing && vm.isEditing() && self.widgets && self.widgets().length < 1
  });

  self.enableOozieDropOnBefore = ko.observable(true);
  self.enableOozieDropOnSide = ko.observable(true);

  return self;
}

var ExtendedWidget = function (params) {
  var self = new Widget(params);
  self.oozieMovable = ko.computed(function () {
    return ["end-widget", "start-widget", "fork-widget", "decision-widget", "join-widget"].indexOf(self.widgetType()) == -1
  });

  self.oozieExpanded = ko.observable(false);
  self.ooziePropertiesExpanded = ko.observable(false);
  self.status = ko.observable("");
  self.progress = ko.observable(0);
  self.actionURL = ko.observable("");
  self.logsURL = ko.observable("");
  self.externalId = ko.observable("");
  self.externalJobId = ko.observable("");
  self.externalIdUrl = ko.observable("");
  return self;
}

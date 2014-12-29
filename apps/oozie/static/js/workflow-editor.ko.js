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


function magicLayout(vm) {
  loadLayout(vm, vm.initial.layout);
  $(document).trigger("magicLayout");
}

function loadColumns(viewModel, json_layout) {
  var _columns = [];

  $(json_layout).each(function (cnt, json_col) {
    var _rows = [];
    $(json_col.rows).each(function (rcnt, json_row) {
      var row = new Row([], viewModel);
      $(json_row.widgets).each(function (wcnt, widget) {
        var _w = new Widget({
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
      row.columns(loadColumns(viewModel, json_row.columns));
      _rows.push(row);
    });
    var column = new Column(json_col.size, _rows);
    _columns = _columns.concat(column);
  });
  return _columns;
}

function loadLayout(viewModel, json_layout) {
  viewModel.columns(loadColumns(viewModel, json_layout));
}


// End dashboard lib

var Node = function (node) {
  var self = this;

  var type = typeof node.widgetType != "undefined" ? node.widgetType : node.type;

  self.id = ko.observable(typeof node.id != "undefined" && node.id != null ? node.id : UUID());
  self.name = ko.observable(typeof node.name != "undefined" && node.name != null ? node.name : "");
  self.type = ko.observable(typeof type != "undefined" && type != null ? type : "");

  self.properties = ko.mapping.fromJS(typeof node.properties != "undefined" && node.properties != null ? node.properties : {});
  self.children = ko.mapping.fromJS(typeof node.children != "undefined" && node.children != null ? node.children : []);

  self.actionParameters = ko.observableArray([]);
  self.actionParametersUI = ko.computed(function() { // TODO: remove truncation when autocomplete
    return $.map(self.actionParameters().slice(0, 3), function(param) {return param + '=...'}).join();
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
  }

  self.set_link = function (name, node_id) {
    var _link = self.get_link(name);

    if (_link == null) {
      _link = {}
      self.children.push(_link);
    }
    _link[name] = node_id;
    self.children.valueHasMutated();
  }

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
  }
  
  if (typeof self.properties.parameters != "undefined") { // Fetch once the possible variable when they exist 
    self.properties.parameters.subscribe(function(newVal) { // TODO: only fetch when first time focus on one of the parameters and showing the autocomplete.
      if (newVal && ! self.actionParametersFetched()) {
	    $.post("/oozie/editor/workflow/action/parameters/", {
		  "node": ko.mapping.toJSON(self),
	     }, function (data) {
	       self.actionParametersFetched(true);
  	       self.actionParameters(data.parameters);
	    }).fail(function (xhr, textStatus, errorThrown) {
	      $(document).trigger("error", xhr.responseText);
	    });
	  }
    });  
  }
  
  if (typeof self.properties.script_path != "undefined") {
    self.properties.script_path.subscribe(function() {
      self.actionParametersFetched(false);
    });
  }
}


var Workflow = function (vm, workflow) {
  var self = this;

  self.id = ko.observable(typeof workflow.id != "undefined" && workflow.id != null ? workflow.id : null);
  self.uuid = ko.observable(typeof workflow.uuid != "undefined" && workflow.uuid != null ? workflow.uuid : UUID());
  self.name = ko.observable(typeof workflow.name != "undefined" && workflow.name != null ? workflow.name : "");

  self.properties = ko.mapping.fromJS(typeof workflow.properties != "undefined" && workflow.properties != null ? workflow.properties : {});
  self.nodes = ko.observableArray([]);
  self.movedNode = null;

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
      var _node = new Node(node);
      nodes.push(_node);
    });
    self.nodes(nodes)
  }

  self.newNode = function (widget, callback) {
    $.ajax({
      type: "POST",
      url: "/oozie/editor/workflow/new_node/",
      data: {
        "workflow": ko.mapping.toJSON(workflow),
        "node": ko.mapping.toJSON(widget)
      },
      success: function (data) {
        if (data.status == 0) {
          viewModel.addActionProperties(data.properties);
          viewModel.addActionWorkflows(data.workflows);
          if (callback) {
            callback(widget);
          }
        }
      },
      async: false
    });
  };

  self.addNode = function (widget) {
    $.post("/oozie/editor/workflow/add_node/", {
      "workflow": ko.mapping.toJSON(workflow),
      "node": ko.mapping.toJSON(widget),
      "properties": ko.mapping.toJSON(viewModel.addActionProperties()),
      "subworkflow": viewModel.selectedSubWorkflow() ? ko.mapping.toJSON(viewModel.selectedSubWorkflow()) : '{}'
    }, function (data) {
      if (data.status == 0) {
        var _node = ko.mapping.toJS(widget);
        _node.properties = data.properties;
        _node.name = data.name;

        if (self.movedNode) {
          var node = self.movedNode;
        } else {
          var node = new Node(_node);
        }

        self.nodes.push(node);

        // If added to the side
        if (vm.currentlyCreatingFork) {
          var parentWidget = vm.getWidgetPredecessor(node.id());
          var parent = self.getNodeById(parentWidget.id());

          if (self.getNodeById(parentWidget.id()) == null) { // New fork

            vm.currentlyCreatedJoin.properties['fork_id'] = vm.currentlyCreatedFork.id;
            vm.currentlyCreatedFork.properties['join_id'] = vm.currentlyCreatedJoin.id;

            var fork = new Node(vm.currentlyCreatedFork);
            var join = new Node(vm.currentlyCreatedJoin);

            self.nodes.push(fork);
            self.nodes.push(join);

            var forkParent = self.getNodeById(vm.getWidgetPredecessor(parentWidget.id()).id());

            var afterParentId = ko.mapping.toJS(forkParent.get_link('to')).to;
            var afterParent = self.getNodeById(afterParentId);
            fork.children.push({'to': afterParentId, 'condition': ''});
            fork.children.push({'to': node.id(), 'condition': ''});

            forkParent.get_link('to')['to'] = fork.id();

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

            parent.children.push({'to': node.id(), 'condition': ''});
          }
        } else {
          var parentWidget = vm.getWidgetPredecessor(node.id());
          var parent = self.getNodeById(parentWidget.id());

          if (widget.widgetType() == 'kill-widget') {
            parent.set_link('to', node.id());
          } else if (parentWidget.widgetType() == 'fork-widget') {
            var child = vm.getWidgetSuccessor(node.id());
            parent.remove_link('to', child.id());
            parent.children.push({'to': node.id(), 'condition': ''});

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
            forkParent.set_link('to', ko.mapping.toJS(fork.get_link('to'))['to']); // Only link

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
      } else if (parent.type() == 'decision-widget') {
        parent.remove_link('to', childId);
      }
    }
    else {
      self.nodes.remove(node);
    }
  };

  self.moveNode = function (widget) {
    var node = self.getNodeById(widget.id());
    self.movedNode = node;

    self.removeNode(node.id());
    self.addNode(widget);

    self.movedNode = null;
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
}

var WorkflowEditorViewModel = function (layout_json, workflow_json, credentials_json, workflow_properties_json) {
  var self = this;

  self.isNested = ko.observable(true);

  self.isEditing = ko.observable(true);
  self.isEditing.subscribe(function (newVal) {
    $(document).trigger("editingToggled");
  });
  self.toggleEditing = function () {
    self.isEditing(!self.isEditing());
  };

  self.hasArrows = ko.observable(true);
  self.hasArrows.subscribe(function (newVal) {
    if (newVal){
      $(document).trigger("drawArrows");
    }
    else {
      $(document).trigger("removeArrows");
    }
  });
  self.toggleArrows = function () {
    self.hasArrows(!self.hasArrows());
  };

  self.newAction = ko.observable();

  self.columns = ko.observable([]);
  self.previewColumns = ko.observable("");
  self.workflow = new Workflow(self, workflow_json);
  self.credentials = ko.mapping.fromJSON(credentials_json);

  self.inited = ko.observable(self.columns().length > 0);
  self.init = function (callback) {
    self.workflow_properties = ko.mapping.fromJS(workflow_properties_json);
    loadLayout(self, layout_json);
    self.workflow.loadNodes(workflow_json);
  }

  self.depen = ko.observableArray(workflow_json.dependencies);

  self.addActionProperties = ko.observableArray([]);
  self.addActionWorkflows = ko.observableArray([]);
  self.selectedSubWorkflow = ko.observable();


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
  }

  function toggleSideDrop(widget, enable) {
    if (widget != null && widget.id() != "" && self.currentlyDraggedOp() == "move") {
      var _row = self.getWidgetParentRow(widget.id());
      if (_row) {
        _row.enableOozieDropOnSide(enable);
        _row.enableOozieDropOnBefore(enable);

        var _parentRow = self.getRowParentRow(_row.id());
        if (_parentRow) {
          _parentRow.enableOozieDropOnSide(enable);
          if (_parentRow.columns().length <= 2) {
            _parentRow.columns().forEach(function (col) {
              col.enableOozieDropOnBefore(enable);
              col.enableOozieDropOnAfter(enable);
              col.rows()[0].enableOozieDropOnSide(enable);
            });
            var _prevParentRow = self.getPrevRow(_parentRow);
            if (_prevParentRow && _prevParentRow.widgets().length > 0 && _prevParentRow.widgets()[0].widgetType() == "fork-widget") {
              _prevParentRow.enableOozieDropOnSide(enable);
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
            self.getRowParentColumn(_prevRow.id()).enableOozieDropOnBefore(enable);
          }
        }
        var _nextRow = self.getNextRow(_row);
        if (_nextRow) {
          _nextRow.enableOozieDropOnBefore(enable);
          if (_nextRow.widgets().length > 0 && _nextRow.widgets()[0].widgetType() == "end-widget") {
            _nextRow.enableOozieDropOnSide(enable);
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

      var _w = new Widget({
        size: self.currentlyDraggedWidget().size(),
        id: UUID(),
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
        var _id = UUID();
        var _fork = new Widget({
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

      var _w = new Widget({
        size: self.currentlyDraggedWidget().size(),
        id: UUID(),
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
      var _row = new Row([_w], self);
      _col.addRow(_row);

      if (_addForkAndJoin) {
        var _joinRow = _parentCol.addEmptyRow(false, _rowIdx + 2);
        var _id = UUID();
        var _join = new Widget({
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

  self.removeWidget = function (widget_json) {
    self.workflow.removeNode(widget_json.id());
    self.removeWidgetById(widget_json.id());
  }

  self.removeWidgetById = function (widget_id) {
    $.each(self.columns(), function (i, col) {
      self.deeplyRemoveWidgetById(widget_id, col, self)
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
    for (var i = 0; i < _parentColumn.rows().length; i++) {
      var _currentRow = _parentColumn.rows()[i];
      if (_currentRow.id() == row.id()) {
        break;
      }
      _prevRow = _currentRow;
    }
    if (_prevRow != null) {
      return _prevRow.widgets().length > 0 && (_prevRow.widgets()[0].widgetType() == "fork-widget" || _prevRow.widgets()[0].widgetType() == "decision-widget");
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
    for (var i = 0; i < self.columns().length; i++) {
      _row = self.traverseColumnForWidget(widget_id, self.columns()[i]);
      if (_row != null) {
        break;
      }
    }
    return _row;
  }

  self.getRowParentColumn = function (row_id) {
    return self.traverseColumnForColumn(row_id, self.columns()[0], 0);
  }

  self.getColumnParentRow = function (col_id) {
    return self.traverseColumnForRow(col_id, self.columns()[0], 0);
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
  }

  self.save = function () {
    $.post("/oozie/editor/workflow/save/", {
      "layout": ko.mapping.toJSON(self.columns),
      "workflow": ko.mapping.toJSON(self.workflow)
    }, function (data) {
      if (data.status == 0) {
    	if (self.workflow.id() == null) {
    	  shareViewModel.setDocId(data.doc1_id);
    	}
        self.workflow.id(data.id);
        $(document).trigger("info", data.message);
        if (window.location.search.indexOf("workflow") == -1) {
          window.location.hash = '#workflow=' + data.id;
        }
      }
      else {
        $(document).trigger("error", data.message);
      }
    }).fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });
  };

  self.gen_xml = function () {
    $.post("/oozie/editor/workflow/gen_xml/", {
      "layout": ko.mapping.toJSON(self.columns),
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

  self.import_workflows = function () {
    $.post("/oozie/editor/workflow/import_workflows/", {
    }, function (data) {
      if (data.status == 0) {
        console.log(data.json);
      }
      else {
        $(document).trigger("error", data.message);
      }
    }).fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });
  };

  self.showSubmitPopup = function () {
    // If self.workflow.id() == null, need to save wf for now

    $.get("/oozie/editor/workflow/submit/" + self.workflow.id(), {
    }, function (data) {
      $(document).trigger("showSubmitPopup", data);
    }).fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });
  };

  function bareWidgetBuilder(name, type) {
    return new Widget({
      size: 12,
      id: "",
      name: name,
      widgetType: type
    });
  }

  self.draggableHiveAction = ko.observable(bareWidgetBuilder("Hive Script", "hive-widget"));
  self.draggableHive2Action = ko.observable(bareWidgetBuilder("HiveServer2 Script", "hive2-widget"));
  self.draggablePigAction = ko.observable(bareWidgetBuilder("Pig Script", "pig-widget"));
  self.draggableJavaAction = ko.observable(bareWidgetBuilder("Java program", "java-widget"));
  self.draggableMapReduceAction = ko.observable(bareWidgetBuilder("MapReduce job", "mapreduce-widget"));
  self.draggableSubworkflowAction = ko.observable(bareWidgetBuilder("Sub workflow", "subworkflow-widget"));
  self.draggableSqoopAction = ko.observable(bareWidgetBuilder("Sqoop 1", "sqoop-widget"));
  self.draggableShellAction = ko.observable(bareWidgetBuilder("Shell", "shell-widget"));
  self.draggableSshAction = ko.observable(bareWidgetBuilder("Ssh", "ssh-widget"));
  self.draggableFsAction = ko.observable(bareWidgetBuilder("HDFS Fs", "fs-widget"));
  self.draggableEmailAction = ko.observable(bareWidgetBuilder("Email", "email-widget"));
  self.draggableStreamingAction = ko.observable(bareWidgetBuilder("Streaming", "streaming-widget"));
  self.draggableDistCpAction = ko.observable(bareWidgetBuilder("Distcp", "distcp-widget"));

  self.draggableKillNode = ko.observable(bareWidgetBuilder("Kill", "kill-widget"));
};


function logGA(page) {
  if (typeof trackOnGA == 'function') {
    trackOnGA('oozie/editor/workflow' + page);
  }
}
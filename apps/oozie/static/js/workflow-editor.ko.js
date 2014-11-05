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
  init: function(element, valueAccessor) {
    var _dropElement = $(element);
    var _options = valueAccessor();

    if (_options.enabled){
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

function loadLayout(viewModel, json_layout) {
  var _columns = [];

  $(json_layout).each(function (cnt, json_col) {
    var _rows = [];
    $(json_col.rows).each(function (rcnt, json_row) {
      var row = new Row([], viewModel);
      $(json_row.widgets).each(function (wcnt, widget) {
        row.addWidget(new Widget({
          size:widget.size,
          id: widget.id,
          name: widget.name,
          widgetType: widget.widgetType,
          properties: widget.properties,
          offset: widget.offset,
          loading: true,
          vm: viewModel
        }));
      });
      $(json_row.columns).each(function (ccnt, column) {
        var _irows = [];
        $(column.rows).each(function (ircnt, json_irow) {
          var _irow = new Row([], viewModel);
          $(json_irow.widgets).each(function (iwcnt, iwidget) {
            _irow.addWidget(new Widget({
              size:iwidget.size,
              id: iwidget.id,
              name: iwidget.name,
              widgetType: iwidget.widgetType,
              properties: iwidget.properties,
              offset: iwidget.offset,
              loading: true,
              vm: viewModel
            }));
          });
          _irows.push(_irow);
        });
        row.addColumn(new Column(column.size, _irows));
      });
      _rows.push(row);
    });
    var column = new Column(json_col.size, _rows);
    _columns = _columns.concat(column);
  });
  viewModel.columns(_columns);
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

  self.get_link = function(name) {
    var _link = null;
    $.each(self.children(), function(index, link) {
      if (name in link) {
        _link = link;
        return false;
      }
    });
    return _link;
  }

  self.set_link = function(name, node_id) {
	var _link = self.get_link(name);

    if (_link == null) {
      _link = {};
      self.children.push(_link);
    }

    _link[name] = node_id;
  }

  self.remove_link = function(name, child) {
    var _link = null;
    $.each(self.children(), function(index, link) {
      if (name in link && link[name] == child) {
        _link = link;
        return false;
      }
    });
    if (_link != null) {
      self.children.remove(_link);
    }
  }  
}


var Workflow = function (vm, workflow) {
  var self = this;

  self.id = ko.observable(typeof workflow.id != "undefined" && workflow.id != null ? workflow.id : null);
  self.uuid = ko.observable(typeof workflow.uuid != "undefined" && workflow.uuid != null ? workflow.uuid : UUID());
  self.name = ko.observable(typeof workflow.name != "undefined" && workflow.name != null ? workflow.name : "");

  self.properties = ko.mapping.fromJS(typeof workflow.properties != "undefined" && workflow.properties != null ? workflow.properties : {});
  self.nodes = ko.observableArray([]);

  self.loadNodes = function(workflow) {
    var nodes = []
    $.each(workflow.nodes, function(index, node) {
      var _node = new Node(node);
      nodes.push(_node);
    });
    self.nodes(nodes)
  }

  self.newNode = function(widget) {
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
        }
      },
      async: false
    });
  };

  self.addNode = function(widget) {
    // Todo get parent cell, link nodes... when we have the new layout
    $.post("/oozie/editor/workflow/add_node/", {
        "workflow": ko.mapping.toJSON(workflow),
        "node": ko.mapping.toJSON(widget),
        "properties": ko.mapping.toJSON(viewModel.addActionProperties()),
        "subworkflow": viewModel.selectedSubWorkflow() ? ko.mapping.toJSON(viewModel.selectedSubWorkflow()) : '{}',
      }, function (data) {
      if (data.status == 0) {
        var _node = ko.mapping.toJS(widget);
        _node.properties = data.properties;
        _node.name = data.name;

        var node = new Node(_node);    	

        // Add to list of nodes
        var end = self.nodes.pop();
        self.nodes.push(node);
        self.nodes.push(end);

       // if node != kill node

        // Added to the side ?
        if (vm.currentlyCreatingFork) {
          var parent = self.getNodeById('3f107997-04cc-8733-60a9-a4bb62cebffc');

          if (parent.type() != 'fork-widget') {          
            var fork = new Node(vm.currentlyCreatedFork);
            var join = new Node(vm.currentlyCreatedJoin);
            
            // Start node
            var afterStartId = ko.mapping.toJS(parent.get_link('to')).to;
            var afterStart = self.getNodeById(afterStartId);
            fork.children.push({'to': afterStartId});
            fork.children.push({'to': node.id()});
            
            parent.get_link('to')['to'] = fork.id();
            
            join.set_link('to', afterStart.get_link('to')['to']);

            afterStart.set_link('to', join.id());
	        node.set_link('to', join.id());
	        node.set_link('error', '17c9c895-5a16-7443-bb81-f34b30b21548');   
	        
	        var end = self.nodes.pop();
	        self.nodes.push(fork);
	        self.nodes.push(join);
	        self.nodes.push(end);	        
            // Regular node
          
            // Join node
          } else {
            // Just add to existing fork
          }
        } else {
          var parentWidget = vm.getWidgetPredecessor(node.id());
          var parent = self.getNodeById(parentWidget.id());

          if (parentWidget.widgetType() == 'start-widget') {
	        // Star node link to new node	
	        parent.set_link('to', node.id());
	
	        // Link to end
	        node.set_link('to', '33430f0f-ebfa-c3ec-f237-3e77efa03d0a');
	        node.set_link('error', '17c9c895-5a16-7443-bb81-f34b30b21548');
          } else if (parentWidget.widgetType() == 'pig-widget') {
            // Parent regular node        	
  	        node.set_link('to', parent.get_link('to')['to']);
  	        node.set_link('error', '17c9c895-5a16-7443-bb81-f34b30b21548');
  	
  	        parent.set_link('to', node.id());        	
          }
    	  // Parent fork/decision/join...
        }

        vm.currentlyCreatingFork = false;
        
      } else {
        $(document).trigger("error", data.message);
       }
     }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
     });
  };
  
  self.removeNode = function(node_id) {
	var node = self.getNodeById(node_id);
	
    var parentWidget = vm.getWidgetPredecessor(node_id); // Use smarter self.getParents if action node with multi parents
    var parent = self.getNodeById(parentWidget.id());

    var childLink = node.get_link('to');
    var childId = ko.mapping.toJS(childLink)['to'];
    
    parent.remove_link('to', node_id);
    parent.children.push({'to': childId});
    self.nodes.remove(node);
    
    // If need to remove fork
    if (parentWidget.widgetType() == 'fork-widget') {
      var fork = parent;
      var join = self.getNodeById(childId);
      if (join.type() == 'join-widget') {
    	if (join.children().length == 1) {
    		
          // Link top to above and delete fork
    	  var forkParent = self.getParents(fork.id());
    	  forkParent.set_link('to', ko.mapping.toJS(fork.get_link('to'))['to']);

    	  self.nodes.remove(fork);

    	  // Link bottom to child of join
    	  var beboreJoin = self.getParents(childId);
    	  var joinChildId = ko.mapping.toJS(join.get_link('to'))['to'];
    	  beboreJoin.set_link('to', joinChildId);

    	  self.nodes.remove(join); 
    	}
      }
    }
  };
  
  self.getParents = function(node_id) { // Only one for now
    var _node = null;
    $.each(self.nodes(), function (index, node) {
      $.each(node.children(), function(index, link) {
    	var _link = ko.mapping.toJS(link);
        if ('to' in _link && _link.to == node_id) {
          _node = node;
          return false;
        }  
      })
    });
    return _node;  
  }

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

var WorkflowEditorViewModel = function (layout_json, workflow_json, credentials_json) {
  var self = this;

  self.isNested = ko.observable(true);

  self.isEditing = ko.observable(true);
  self.toggleEditing = function () {
    self.isEditing(! self.isEditing());
  };

  self.columns = ko.observable([]);
  self.previewColumns = ko.observable("");
  self.workflow = new Workflow(self, workflow_json);
  self.credentials = ko.mapping.fromJSON(credentials_json);

  self.inited = ko.observable(self.columns().length > 0);
  self.init = function(callback) {
    loadLayout(self, layout_json);
    self.workflow.loadNodes(workflow_json);
  }

  self.depen = ko.observableArray(workflow_json.dependencies);

  self.addActionProperties = ko.observableArray([]);
  self.addActionWorkflows = ko.observableArray([]);
  self.selectedSubWorkflow = ko.observable();


  self.currentlyDraggedWidget = null;
  self.currentlyCreatingFork = false;
  self.currentlyCreatedFork = null;
  self.currentlyCreatedJoin = null;
  self.isDragging = ko.observable(false);

  self.setCurrentDraggedWidget = function (widget) {
    self.currentlyDraggedWidget = widget;
  }

  self.addDraggedWidget = function (row, atBeginning) {
    if (self.currentlyDraggedWidget != null) {
      var _parentCol = self.getRowParentColumn(row.id());
      var _rowIdx = 0;
      $.each(_parentCol.rows(), function (i, irow) {
        if (irow.id() == row.id()) {
          _rowIdx = i;
        }
      });

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

      var _w = new Widget({
        size: self.currentlyDraggedWidget.size(),
        id: UUID(),
        name: self.currentlyDraggedWidget.name(),
        widgetType: self.currentlyDraggedWidget.widgetType(),
        properties: self.currentlyDraggedWidget.properties(),
        offset: self.currentlyDraggedWidget.offset(),
        loading: true,
        vm: self
      });

      var _col = row.addEmptyColumn(atBeginning);
      var _row = new Row([_w], self);
      _col.addRow(_row);

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

      self.currentlyDraggedWidget = null;
      self.currentlyCreatingFork = true;
      self.currentlyCreatedFork = ko.mapping.toJS(_fork);
      self.currentlyCreatedJoin = ko.mapping.toJS(_join);

      linkWidgets(_fork.id(), _w.id());
      linkWidgets(_w.id(), _join.id());

      return _w;
    }
  }

  self.getWidgetById = function (widget_id) {
    var _widget = null;
    $.each(self.columns(), function (i, col) {
      $.each(col.rows(), function (j, row) {
        $.each(row.widgets(), function (z, widget) {
          if (widget.id() == widget_id){
            _widget = widget;
            return false;
          }
        });
      });
    });
    return _widget;
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
        if (row && row.widgets()){
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

          if (_prevRowIdx > -1 && _parentRows()[_prevRowIdx].widgets().length > 0 && _parentRows()[_prevRowIdx].widgets()[0].widgetType() == "fork-widget"){
            _parentRows.remove(_parentRows()[_prevRowIdx]);
            _parentRows.remove(_parentRows()[_prevRowIdx+1]);
          }

          for (var i=0;i<_rows.length;i++){
            if (i==0){
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

  self.getWidgetPredecessor = function (widget_id) {
    var _row = self.getWidgetParentRow(widget_id);
    var _col = self.getRowParentColumn(_row.id());
    var _prevRow = null;
    for (var i = 0; i < _col.rows().length; i++) {
      if (_col.rows()[i].id() == _row.id()) {
        break;
      }
      _prevRow = _col.rows()[i];
    }
    if (_prevRow != null) {
      return _prevRow.widgets()[0];
    }
    else {
      var _parentRow = self.getColumnParentRow(_col.id());
      var _parentColumn = self.getRowParentColumn(_parentRow.id());
      var _prevParentRow = null;
      for (var i = 0; i < _parentColumn.rows().length; i++) {
        if (_parentColumn.rows()[i].id() == _parentRow.id()) {
          break;
        }
        _prevParentRow = _parentColumn.rows()[i];
      }
      if (_prevParentRow != null) {
        return _prevParentRow.widgets()[0];
      }
    }
    return null;
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
    var _column = null;
    for (var i = 0; i < self.columns().length; i++) {
      _column = self.traverseColumnForColumn(row_id, self.columns()[i]);
    }
    return _column;
  }

  self.getColumnParentRow = function (col_id) {
    var _row = null;
    for (var i = 0; i < self.columns().length; i++) {
      _row = self.traverseColumnForRow(col_id, self.columns()[i]);
      if (_row != null) {
        break;
      }
    }
    return _row;
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

        if (row.id() == row_id) {
          _column = col;
          break;
        }

        for (var z = 0; z < row.columns().length; z++) {
          _column = self.traverseColumnForColumn(row_id, row.columns()[z]);
          if (_column != null) {
            break;
          }
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
            break;
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

  self.save = function () {
    $.post("/oozie/editor/workflow/save/", {
        "layout": ko.mapping.toJSON(self.columns),
        "workflow": ko.mapping.toJSON(self.workflow)
    }, function (data) {
      if (data.status == 0) {
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
        alert(data.xml);
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

  function bareWidgetBuilder(name, type){
    return new Widget({
      size: 12,
      id: UUID(),
      name: name,
      widgetType: type
    });
  }

  self.draggableHiveAction = ko.observable(bareWidgetBuilder("Hive Script", "hive-widget"));
  self.draggablePigAction = ko.observable(bareWidgetBuilder("Pig Script", "pig-widget"));
  self.draggableJavaAction = ko.observable(bareWidgetBuilder("Java program", "java-widget"));
  self.draggableMapReduceAction = ko.observable(bareWidgetBuilder("MapReduce job", "mapreduce-widget"));
  self.draggableSubworkflowAction = ko.observable(bareWidgetBuilder("Sub workflow", "subworkflow-widget"));

  self.draggableStopNode = ko.observable(bareWidgetBuilder("Kill", "kill-widget"));
};

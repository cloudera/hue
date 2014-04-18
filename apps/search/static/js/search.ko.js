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


// Start dashboard lib to move out

var Column = function (size, rows) {
  var self = this;
  self.size = ko.observable(size);
  self.rows = ko.observableArray(rows);
  self.klass = ko.computed(function () {
    return "card card-home card-column span" + self.size();
  });
  self.addEmptyRow = function () {
    self.addRow();
  };
  self.addRow = function (row) {
    if (typeof row == "undefined" || row == null) {
      row = new Row([]);
    }
    self.rows.push(row);
  };
}

var Row = function (widgets) {
  var self = this;
  self.widgets = ko.observableArray(widgets);

  self.addWidget = function (widget) {
    self.widgets.push(widget);
  };

  self.move = function (from, to) {
    try {
      viewModel.columns()[to].addRow(self);
      viewModel.columns()[from].rows.remove(self);
    }
    catch (exception) {
    }
  }

  self.moveDown = function (col, row) {
    var _i = col.rows().indexOf(row);
    if (_i < col.rows().length - 1) {
      var _arr = col.rows();
      col.rows.splice(_i, 2, _arr[_i + 1], _arr[_i]);
    }
  }

  self.moveUp = function (col, row) {
    var _i = col.rows().indexOf(row);
    if (_i >= 1) {
      var _arr = col.rows();
      col.rows.splice(_i - 1, 2, _arr[_i], _arr[_i - 1]);
    }
  }

  self.remove = function (col, row) {
    col.rows.remove(row);
  }
}

// A widget is generic. It has an id that refer to another object (e.g. facet) with the same id.
var Widget = function (size, id, name, widgetType, properties, offset) {
  var self = this;
  self.size = ko.observable(size).extend({ numeric: 0 });

  self.name = ko.observable(name);
  self.id = ko.observable(id);
  self.widgetType = ko.observable(typeof widgetType != "undefined" && widgetType != null ? widgetType : "empty-widget");
  self.properties = ko.observable(typeof properties != "undefined" && properties != null ? properties : {});
  self.offset = ko.observable(typeof offset != "undefined" && offset != null ? offset : 0).extend({ numeric: 0 });


  self.klass = ko.computed(function () {
    return "card card-widget span" + self.size() + (self.offset() * 1 > 0 ? " offset" + self.offset() : "");
  });

  self.expand = function () {
    self.size(self.size() + 1);
  }
  
  self.compress = function () {
    self.size(self.size() - 1);
  }

  self.moveLeft = function () {
    self.offset(self.offset() - 1);
  }
  
  self.moveRight = function () {
    self.offset(self.offset() + 1);
  }

  self.remove = function (row, widget) {
    viewModel.removeWidget(widget);
    row.widgets.remove(widget);
  }
};

Widget.prototype.clone = function () {
  return new Widget(this.size(), UUID(), this.name(), this.widgetType());
};

function fullLayout() {
  setLayout([12]);
}

function oneThirdLeftLayout() {
  setLayout([3, 9]);
}

function oneThirdRightLayout() { // instead --> full with 1 row = timeline, 2 = 3 pies, 3 = grid result
  setLayout([9, 3]);
}

function setLayout(colSizes) {
  // Save previous widgets
  var _allRows = [];
  $(viewModel.columns()).each(function (cnt, col) {
    var _tRows = [];
    $(col.rows()).each(function (icnt, row) {
      if (row.widgets().length > 0) {
        _tRows.push(row);
      }
    });
    _allRows = _allRows.concat(_tRows);
  });

  var _cols = [];
  var _highestCol = {
    idx: -1,
    size: -1
  };
  $(colSizes).each(function (cnt, size) {
    _cols.push(new Column(size, []));
    if (size > _highestCol.size) {
      _highestCol.idx = cnt;
      _highestCol.size = size;
    }
  });
  if (_allRows.length > 0 && _highestCol.idx > -1) {
    _cols[_highestCol.idx].rows(_allRows);
  }

  $(_cols).each(function (cnt, col) {
    if (col.rows().length == 0) {
      col.rows([new Row([])]);
    }
  });

  viewModel.columns(_cols);
}

function loadLayout(viewModel, json_layout) {
  var _columns = [];
  
  $(json_layout).each(function (cnt, json_col) { 
    var _rows = [];
    $(json_col.rows).each(function (rcnt, json_row) {
      var row = new Row();
      $(json_row.widgets).each(function (wcnt, widget) {
        row.addWidget(new Widget(widget.size, widget.id, widget.name, widget.widgetType, widget.properties, widget.offset));
      });
      _rows.push(row);
    });
    var column = new Column(json_col.size, _rows);
    _columns = _columns.concat(column);
  });

  viewModel.columns(_columns);
}

// End dashboard lib

var Query = function (vm, query) {
  var self = this;

  self.q = ko.observable(query.q);
  self.fq = query.fq

  self.selectFacet = function (facet_json) {
    self.fq[facet_json.cat] = facet_json.value; // need to add facet id too
    vm.search();
  }

  self.unselectFacet = function (facet_json) {
    delete self.fq[facet_json.cat];
    vm.search();
  }
};


var Collection = function (vm, collection) {
  var self = this;

  self.id = collection.id;
  self.name = collection.name;
  self.label = collection.label;
  self.idField = collection.idField;
  self.template = ko.mapping.fromJS(collection.template);
  self.template.fieldsSelected.subscribe(function () {
    vm.search();
  });
  self.template.template.subscribe(function () {
    vm.search();
  });
  self.template.isGridLayout.subscribe(function () {
    vm.search();
  });
  self.facets = ko.mapping.fromJS(collection.facets);
  $.each(self.facets(), function (index, facet) {
    facet.field.subscribe(function () {
      vm.search();
    });
  });


  self.fields = ko.mapping.fromJS(collection.fields);

  self.addFacet = function (facet_json) {
    $.post("/search/template/" + self.id + "/new_facet", {
        "id": facet_json.widget_id,
        "label": facet_json.name,
        "field": facet_json.name,
        "widget_type": facet_json.widgetType
      }, function (data) {
      if (data.status == 0) {
	    var facet = ko.mapping.fromJS(data.facet);
	    facet.field.subscribe(function () {
	      vm.search();
	    });
	    self.facets.push(facet);
	    vm.search();
      }
    }).fail(function (xhr, textStatus, errorThrown) {});
  };

  self.removeFacet = function (widget_id) {
    $.each(self.facets(), function (index, facet) {	
      if (facet.id() == widget_id()) {
        self.facets.remove(facet);
        return false;
      }
    });
  }  
  
  self.getFacetById = function (facet_id) {
    var _facet = null;
    $.each(self.facets(), function (index, facet) {//alert(ko.mapping.toJSON(category));
      if (facet.id() == facet_id) {
        _facet = facet;
        return false;
      }
    });
    return _facet;
  }  
  
  self.template.fields = ko.computed(function () {
    var _fields = [];
    $.each(self.template.fieldsAttributes(), function (index, field) {
      var position = self.template.fieldsSelected.indexOf(field.name());
      if (position != -1) {
    	_fields[position] = field;
      }      
    });
    return _fields;
  });    
  
  self.addDynamicFields = function () { // + Adding merge smartly if schema updated
    $.post("/search/index/" + self.id + "/fields/dynamic", {
      }, function (data) {
      if (data.status == 0) {
        $.each(data.dynamic_fields, function (index, field) {
          if (self.fields.indexOf(field) == -1) {
            self.fields.push(field);
          }
        });
      }
    }).fail(function (xhr, textStatus, errorThrown) {});
  }

  self.toggleSortColumnGridLayout = function (template_field) {
	 if (! template_field.sort.direction()) {
	   template_field.sort.direction('desc');
	 } else if (template_field.sort.direction() == 'desc') {
	   template_field.sort.direction('asc');
	 } else {
	   template_field.sort.direction(null); 
	 }

	 vm.search();
  };
};


var SearchViewModel = function (collection_json, query_json) {
  var self = this;

  // Models
  self.collection = new Collection(self, collection_json.collection);
  self.query = new Query(self, query_json);

  // UI
  self.response = ko.observable({});
  self.results = ko.observableArray([]);
  self.norm_facets = ko.computed(function () {
    return self.response().normalized_facets;
  });
  self.getFacetFromQuery = function (facet_id) {	
    var _facet = null;
    if (self.norm_facets() !== undefined) {
	  $.each(self.norm_facets(), function (index, norm_facet) {  
	    if (norm_facet.id == facet_id()) {
	      _facet = norm_facet;
	    }      
	  });
    }
    return _facet;	  
  };

  self.previewColumns = ko.observable("");
  self.columns = ko.observable({});
  loadLayout(self, collection_json.layout);

  self.isEditing = ko.observable(false);
  self.toggleEditing = function () {
    self.isEditing(!self.isEditing());
  };
  self.isRetrievingResults = ko.observable(false);
      
  self.draggableHit = ko.observable(new Widget(12, UUID(), "Hit Count", "hit-widget"));
  self.draggableFacet = ko.observable(new Widget(12, UUID(), "Facet", "facet-widget"));
  self.draggableResultset = ko.observable(new Widget(12, UUID(), "Results", "resultset-widget"));
  self.draggableHistogram = ko.observable(new Widget(12, UUID(), "Histogram", "histogram-widget"));
  self.draggableArea = ko.observable(new Widget(12, UUID(), "Area Chart", "area-widget"));
  self.draggableMap = ko.observable(new Widget(12, UUID(), "Map", "map-widget"));
  self.draggableLine = ko.observable(new Widget(12, UUID(), "Line Chart", "line-widget"));
  self.draggablePie = ko.observable(new Widget(12, UUID(), "Pie Chart", "pie-widget"));

  self.init = function () {
	//self.collection.addDynamicFields();

	self.isEditing(true);
	self.search();	
  }

  self.search = function () {
    self.isRetrievingResults(true);
    $(".jHueNotify").hide();
    $.post("/search/search", {
      collection: ko.mapping.toJSON(self.collection),
      query: ko.mapping.toJSON(self.query),
      layout: ko.mapping.toJSON(self.columns)
    }, function (data) {
      self.response(data); // Content not observable for performance
      self.results.removeAll();
      if (data.error) {
        $(document).trigger("error", data.error);
      }
      else {
        if (self.collection.template.isGridLayout()) {
          // Table view
          $.each(data.response.docs, function (index, item) {
            var row = [];
            var fields = self.collection.template.fieldsSelected();
            // Field selection or whole record
            if (fields.length != 0) {
              $.each(self.collection.template.fieldsSelected(), function (index, field) {  
                row.push(item[field]);
              });
            } else {
              row.push(ko.mapping.toJSON(item)); 
            }
            self.results.push(row);
          });
        }
        else {
          // Template view
          var _mustacheTmpl = fixTemplateDotsAndFunctionNames(self.collection.template.template());
          $.each(data.response.docs, function (index, item) {
            addTemplateFunctions(item);
            self.results.push(Mustache.render(_mustacheTmpl, item));
          });
        }
        self.isRetrievingResults(false);
      }
    }).fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });
  };
  
  self.removeWidget = function (widget_json) {
    self.collection.removeFacet(widget_json.id); 
    self.search();
  }  

  self.save = function () {
    $.post("/search/save", {
      collection: ko.mapping.toJSON(self.collection),
      layout: ko.mapping.toJSON(self.columns)
    },function (data) {
      if (data.status == 0) {
    	self.collection.id = data.id;
        $(document).trigger("info", data.message);
      }
      else {
        $(document).trigger("error", data.message);
      }
    }).fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });
  };
};

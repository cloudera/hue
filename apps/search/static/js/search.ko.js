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

  var Widget = function (size, name, widgetType, properties, offset) {
    var self = this;
    self.size = ko.observable(size).extend({ numeric: 0 });

    self.name = ko.observable(name);
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
      row.widgets.remove(widget);
    }
  };

  Widget.prototype.clone = function () {
    return new Widget(this.size(), this.name(), this.widgetType());
  };

  function fullLayout() {
    setLayout([12]);
  }

  function oneThirdLeftLayout() {
    setLayout([3, 9]);
  }

  function oneThirdRightLayout() {
    setLayout([9, 3]);
  }

  function setLayout(colSizes) {
    // save previous widgets
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

// End dashboard lib
  
var Query = function (vm, query) {
  var self = this;

  self.q = ko.observable(query.q);
  self.fq = query.fq
  
  self.selectFacet = function(facet_json) {
	self.fq[facet_json.cat] = facet_json.value;
	vm.search();
  }

  self.unselectFacet = function(facet_json) {
	delete self.fq[facet_json.cat];
    vm.search();
  }
};


var Collection = function (vm, collection) {
  var self = this;

  self.id = collection.id;
  self.name = collection.name;
  self.idField = collection.idField;
  self.template = ko.mapping.fromJS(collection.template);
  self.template.fields.subscribe(function() {
	vm.search();
  });
  self.template.template.subscribe(function() {
    vm.search();
  });
  self.facets = ko.mapping.fromJS(collection.facets);

  self.fields = ko.observableArray(collection.fields);

  self.addFacet = function(facet_json) {
    self.facets.push(ko.mapping.fromJS({
	   "uuid": "f6618a5c-bbba-2886-1886-bbcaf01409ca",
        "verbatim": "", "isVerbatim": false, "label": facet_json.name, 
	    "field": facet_json.name, "type": "field"
    }));
  }  
  
  self.addDynamicFields = function() {
	$.post("/search/index/" + self.id + "/fields/dynamic", {		
	  }, function (data){
		if (data.status == 0) {
		  $.each(data.dynamic_fields, function(index, field) {
            self.fields.push(field);
		  });
		}
	  }).fail(function(xhr, textStatus, errorThrown) {}
	);
  }
    
  // Init
  self.addDynamicFields();
};


var SearchViewModel = function (collection_json, query_json) {
  var self = this;

  // Models
  self.collection = new Collection(self, collection_json);
  self.query = new Query(self, query_json);
  
  // UI
  self.response = ko.observable({});
  self.results = ko.observableArray([]);
  self.norm_facets = ko.computed(function () {
    return self.response().normalized_facets;
  });
  
  self.selectedFacet = ko.observable();

  self.previewColumns = ko.observable("");
  self.columns = ko.observableArray([]); // load back? 
  self.isEditing = ko.observable(false);
  self.draggableFacet = ko.observable(new Widget(12, "Facet", "facet-widget"));
  self.draggableResultset = ko.observable(new Widget(12, "Results", "resultset-widget"));
  self.draggableBar = ko.observable(new Widget(12, "Bar Chart", "bar-widget"));
  self.draggableArea = ko.observable(new Widget(12, "Area Chart", "area-widget"));
  self.draggableMap = ko.observable(new Widget(12, "Map", "map-widget"));
  self.draggableLine = ko.observable(new Widget(12, "Line Chart", "line-widget"));
  self.draggablePie = ko.observable(new Widget(12, "Pie Chart", "pie-widget"));
  self.toggleEditing = function () {
    self.isEditing(!self.isEditing());
  };  
  
  
  self.search = function () {
	$(".jHueNotify").hide();
    $.post("/search/search", {
        collection: ko.mapping.toJSON(self.collection),
        query: ko.mapping.toJSON(self.query),
        layout: ko.mapping.toJSON(self.columns)
      }, function (data) {
       self.response(data); // If error we should probably update only the facets
   	   self.results.removeAll(); 
   	   if (data.error) {
   		 $(document).trigger("error", data.error);
   	   } else {
   	     if (self.collection.template.isGridLayout()) {
 	       // Table view
 	       $.each(data.response.docs, function (index, item) {
 	    	 var row = [];
 	    	 $.each(self.collection.template.fields(), function (index, column) {
 	    	   row.push(item[column]); // TODO: if null + some escaping
 	    	 });
 	    	 self.results.push(row);
 	       });
   	     } else {
   	   	   // Template view
   	       var _mustacheTmpl = fixTemplateDotsAndFunctionNames(self.collection.template.template());
           $.each(data.response.docs, function (index, item) {
             addTemplateFunctions(item);
             self.results.push(Mustache.render(_mustacheTmpl, item));
           });
         }
   	   }
     }).fail(function(xhr, textStatus, errorThrown) {    	
       $(document).trigger("error", xhr.responseText);
     });
  };
    
  self.selectSingleFacet = function(normalized_facet_json) {
	$.each(self.collection.facets(), function(index, facet) {
      if (facet.field() == normalized_facet_json.field) {
        self.selectedFacet(facet);
      }
	});	  
  }
  
  self.removeFacet = function(facet_json) {
	$.each(self.collection.facets(), function(index, item) {
	  if (item.field() == facet_json.field) {
		self.collection.facets.remove(item);
	   }
	});
	self.search();
  }
};

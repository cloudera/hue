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

  self.qs = ko.mapping.fromJS([{'q': ''}]);
  self.fqs = ko.mapping.fromJS([]);
  
  self.toggleFacet = function (data) {
    var fq = self.getFacetFilter(data.widget.id());

    if (fq == null) {
      self.fqs.push(ko.mapping.fromJS({
        'id': data.widget.id(),
        'field': data.widget.field(),
        'filter': [data.facet.value()],
        'type': 'field'
      }));
    } else {
      $.each(self.fqs(), function (index, fq) {
        if (fq.id() == data.widget.id()) {
          if (fq.filter.indexOf(data.facet.value()) > -1) {
            fq.filter.remove(data.facet.value());
            if (fq.filter().length == 0) {
              self.fqs.remove(fq);
            }
          } else {
            fq.filter.push(data.facet.value());
          }
        }
      });
    }

    vm.search();
  }  
  
  self.selectRangeFacet = function (data) {
    var fq = self.getFacetFilter(data.widget_id);

    if (fq == null) {
      self.fqs.push(ko.mapping.fromJS({
          'id': data.widget_id,
          'field': data.cat,
          'filter': [{'value': data.from, 'exclude': false}],
          'properties': [{'from': data.from, 'to': data.to}],
          'type': 'range'
      }));
    } else {
      var f = $.grep(fq.filter(), function(f) { return f.value() == data.from; });
      if (f.length > 0) { // Unselect
        fq.filter.remove(f[0]);
        $.each(fq.properties(), function (index, prop) {
          if (prop && prop.from() == data.from) {
            fq.properties.remove(prop);
          }
        });
        if (fq.filter().length == 0) {
          self.removeFilter(ko.mapping.fromJS({'id': data.widget_id}));
        }
      } else {
       fq.filter.push(ko.mapping.fromJS({'exclude': data.exclude ? true : false, 'value': data.from}));
       fq.properties.push(ko.mapping.fromJS({'from': data.from, 'to': data.to}));
      }
    }
  };  
  
  self.getFacetFilter = function (facet_id) {
    var _facet = null;
    $.each(self.fqs(), function (index, facet) {
      if (facet.id() == facet_id) {
        _facet = facet;
        return false;
      }
    });
    return _facet;	  
  }
}

var Dashboard = function (vm, dashboard) { 
  var self = this;

  self.id = ko.mapping.fromJS(dashboard.id);
  self.facets = ko.mapping.fromJS(dashboard.facets);
  self.properties = ko.mapping.fromJS(dashboard.properties);

  self.dropdownDbs = ko.observableArray([]);
  self.selectedDropdownDb = ko.observable("");
  self.selectedDropdownDb.subscribe(function(value) {
	self.properties()[0].database(self.selectedDropdownDb());
	if (self.selectedDropdownDb() && self.selectedDropdownTable()) {
	  self.updateFields(); 
	}
  });  

  self.dropdownTables = ko.observableArray(["customers", "sample_07", "sample_08", "web_logs"]);
  self.selectedDropdownTable = ko.observable("");
  self.selectedDropdownTable.subscribe(function(value) {
	self.properties()[0].table(self.selectedDropdownTable());
	if (self.selectedDropdownDb() && self.selectedDropdownTable()) {
	  self.updateFields(); 
	}
  });
  
  self.updateDropdownDatabases = function(databases) {
    if (databases) {
      var i = databases.indexOf("_impala_builtins"); // Blacklist of system databases
      if (i != -1) {
        databases.splice(i, 1);
      }
      self.dropdownDbs(databases);
    }
  };

  self.fields = ko.computed(function () {
    if (self.properties() != null && self.properties().length > 0 && self.properties()[0].fields != null){
	  return self.properties()[0].fields();
    }
    return [];
  });
  self.fieldNames = ko.computed(function () {
	return $.map(self.fields(), function (field) { return field.name() });
  });

  self.resultsetShowFieldList = ko.observable(true);
  self.resultsetFieldsFilter = ko.observable(""); // For UI

  self.resultsetSelectedFields = ko.observableArray(self.fieldNames());
  /**self.resultsetSelectedFields.subscribe(function(value) {
    vm.search();
  });*/

  self.resultsetFilteredFields = ko.computed(function() {
    var _fields = [];
    $.each(self.fields(), function (index, field) {
      if (self.resultsetFieldsFilter() == "" || field.name().toLowerCase().indexOf(self.resultsetFieldsFilter().toLowerCase()) > -1){
        _fields.push(field);
      }
    });
    return _fields;
  });

  self.selectedNewFacetField = ko.observable();
  
  self.addFacet = function(facet_json) {
   $.post("/impala/dashboard/new_facet", {
       "dashboard": ko.mapping.toJSON(self),
       "facet_json": ko.mapping.toJSON(facet_json),
       "field": self.selectedNewFacetField(),
     }, function (data) {
       if (data.status == 0) {
         var facet = ko.mapping.fromJS(data.facet);
         facet.properties.limit.subscribe(function () {
           vm.search();
         });
         self.facets.push(facet);
         vm.search();
       } else {
         $(document).trigger("error", data.message);
       }
    }).fail(function (xhr, textStatus, errorThrown) {});
  }
  
  self.getFacetById = function (facet_id) {
    var _facet = null;
    $.each(self.facets(), function (index, facet) {
      if (facet.id() == facet_id) {
        _facet = facet;
        return false;
      }
    });
    return _facet;
  }   
  
  self.updateFields = function(database, table) {
    $.post("/impala/dashboard/get_fields", {
    	"database": self.properties()[0].database(),
    	"table": self.properties()[0].table()
    }, function (data) {
      if (data.status == 0) {
        self.properties()[0].fields.removeAll();
        self.resultsetSelectedFields.removeAll();
    	$.each(data.fields, function (index, field) {
    	  self.properties()[0].fields.push(ko.mapping.fromJS(field));
    	  self.resultsetSelectedFields.push(field.name);
      	});        
      }
    }).fail(function (xhr, textStatus, errorThrown) {});
  }  
}

var ImpalaDashboardViewModel = function (query_json, dashboard_json, initial_json) {
    var self = this;

    self.isEditing = ko.observable(true);
    self.toggleEditing = function () {
      self.isEditing(! self.isEditing());
    };
    self.isRetrievingResults = ko.observable(false);
    self.previewColumns = ko.observable("");
    self.columns = ko.observable([]);
    
    loadLayout(self, dashboard_json.layout);

    self.query = new Query(self, query_json);
    self.dashboard = new Dashboard(self, dashboard_json.dashboard);
    self.initial = initial_json;

    self.results = ko.observableArray([]);
    self.results_facet = ko.observableArray([]);
    self.results_cols = ko.observableArray([]);

    self.inited = ko.observable(self.columns().length > 0);

    self.selectedQDefinition = ko.observable();
    self.isNested = ko.observable(false);

    self.init = function(callback) {
      if (self.inited()){
        self.search();
      }
      callback();
    }
    
    self.search = function (callback) {
      self.isRetrievingResults(true);
      self.results.removeAll();
    	
      var multiQs = $.map(self.dashboard.facets(), function(facet) {
        return $.post("/impala/dashboard/query", {
           "query": ko.mapping.toJSON(self.query),
           "dashboard": ko.mapping.toJSON(self.dashboard),
           "layout": ko.mapping.toJSON(self.columns),
           "facet": ko.mapping.toJSON(facet),
        }, function (data) {return data});
      });    	
    	
      $.when.apply($, [
          $.post("/impala/dashboard/query", {
            "query": ko.mapping.toJSON(self.query),
            "dashboard": ko.mapping.toJSON(self.dashboard),
            "layout": ko.mapping.toJSON(self.columns),
            }, function (data) {
              self.isRetrievingResults(false);
              if (data.status == 0) {
            	self.results_cols(data.cols)
            	$.each(data.data, function (index, row) {
            	  self.results.push(row);
            	});
              } else {
                $(document).trigger("error", data.message);
              }
            })
          ].concat(multiQs)
      )
      .done(function() {
          if (multiQs.length > 0) {
            for (var i = 1; i < arguments.length; i++) {
              var facet = arguments[i][0];
              removeFrom(self.results_facet, facet.id);
              self.results_facet.push(ko.mapping.fromJS(facet));
            }
          }          
        })
      .fail(function (xhr, textStatus, errorThrown) {
    	  $(document).trigger("error", errorThrown);
       });
    };

    function removeFrom(collection, item_id) {
      $.each(collection(), function (index, item) {
        if (item.id() == item_id) {
          collection.remove(item);
          return false;
        }
      });
    }
    
    self.getFacetFromResult = function (facet_id) {
      var _facet = null;
      $.each(self.results_facet(), function (index, facet) {
        if (facet.id() == facet_id) {
          _facet = facet;
          return false;
        }
      });
      return _facet;
    }

    self.getWidgetById = function (widget_id) {
      var _widget = null;
      $.each(self.columns(), function (i, col) {
        $.each(col.rows(), function (j, row) {
          $.each(row.widgets(), function (z, widget) {
            if (widget.id() == widget_id){
              _widget = widget;
            }
          });
        });
      });
      return _widget;
    }
    
    self.save = function () {
      $.post("/impala/dashboard/save", {
          "dashboard": ko.mapping.toJSON(self.dashboard),
          "layout": ko.mapping.toJSON(self.columns)
      }, function (data) {
        if (data.status == 0) {
          self.dashboard.id(data.id);
          $(document).trigger("info", data.message);
          if (window.location.search.indexOf("dashboard") == -1) {
            window.location.hash = '#dashboard=' + data.id;
          }
        }
        else {
          $(document).trigger("error", data.message);
        }
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

    self.draggableFacet = ko.observable(bareWidgetBuilder("Facet", "facet-widget"));
    self.draggableResultset = ko.observable(bareWidgetBuilder("Grid Results", "resultset-widget"));
    self.draggableHistogram = ko.observable(bareWidgetBuilder("Histogram", "histogram-widget"));
    self.draggableBar = ko.observable(bareWidgetBuilder("Bar Chart", "bar-widget"));
    self.draggableMap = ko.observable(bareWidgetBuilder("Map", "map-widget"));
    self.draggableLine = ko.observable(bareWidgetBuilder("Line Chart", "line-widget"));
    self.draggablePie = ko.observable(bareWidgetBuilder("Pie Chart", "pie-widget"));
    self.draggableFilter = ko.observable(bareWidgetBuilder("Filter Bar", "filter-widget"));
};

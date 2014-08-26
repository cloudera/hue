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
        'filter': [data.facet[0]],
        'type': 'field'
      }));
    } else {
      $.each(self.fqs(), function (index, fq) {
        if (fq.id() == data.widget.id()) {
          if (fq.filter.indexOf(data.facet[0]) > -1) {
            fq.filter.remove(data.facet[0]);
            if (fq.filter().length == 0) {
              self.fqs.remove(fq);
            }
          } else {
            fq.filter.push(data.facet[0]);
          }
        }
      });
    }

    vm.search();
  }  
  
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
  
  self.facets = ko.observable(dashboard.facets);
  
  self.addFacet = function(data) {
    
  }
  
  self.getFacetById = function (facet_id) {
    var _facet = null;
    $.each(self.facets(), function (index, facet) {
      if (facet.id == facet_id) {
        _facet = facet;
        return false;
      }
    });
    return _facet;
  }   
}

var TestViewModel = function (query_json, dashboard_json) {
    var self = this;
    self.isEditing = ko.observable(false);
    self.toggleEditing = function () {
      self.isEditing(! self.isEditing());
    };
    self.previewColumns = ko.observable("");
    self.columns = ko.observable([]);

    loadLayout(self, dashboard_json.layout);

    self.query = new Query(self, query_json);
    self.dashboard = new Dashboard(self, dashboard_json);
    self.results = ko.observableArray([]);
    self.results_facet = ko.observableArray([]);

    self.search = function (callback) {
      self.results.removeAll();
    	
      var multiQs = $.map(self.dashboard.facets(), function(facet) {
            return $.post("/impala/query", {
                "query": ko.mapping.toJSON(self.query),
                "dashboard": ko.mapping.toJSON(self.dashboard),
                "layout": ko.mapping.toJSON(self.columns),
                "facet": ko.mapping.toJSON(facet),
              }, function (data) {return data});
      });    	
    	
      $.when.apply($, [
          $.post("/impala/query", {
            "query": ko.mapping.toJSON(self.query),
            "dashboard": ko.mapping.toJSON(self.dashboard),
            "layout": ko.mapping.toJSON(self.columns),
            }, function (data) {
              if (data.status == 0) {
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
          if (arguments.length > 1) { // If multi queries
            for (var i = 1; i < arguments.length; i++) {
              var facet = arguments[i][0];
              removeFrom(self.results_facet, facet.id);
              self.results_facet.push(ko.mapping.fromJS(facet));
            }
          }
        })
      .fail(function (xhr, textStatus, errorThrown) {
    	  $(document).trigger("error", data.message);
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

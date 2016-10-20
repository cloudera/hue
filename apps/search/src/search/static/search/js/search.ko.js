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

  self.uuid = ko.observable(typeof query.uuid != "undefined" && query.uuid != null ? query.uuid : UUID());
  self.qs = ko.mapping.fromJS(query.qs);
  self.qs.subscribe(function(){
    if (vm.selectedQDefinition() != null){
      vm.selectedQDefinition().hasChanged(true);
    }
  });
  self.fqs = ko.mapping.fromJS(query.fqs);
  self.start = ko.mapping.fromJS(query.start);

  var defaultMultiqGroup = {'id': 'query', 'label': 'query'};
  self.multiqs = ko.computed(function () { // List of widgets supporting multiqs
    var histogram_ids = $.map(vm.collection.getHistogramFacets(), function (histo) { return histo.id(); });
    return [defaultMultiqGroup].concat(
        $.map($.grep(self.fqs(), function(fq, i) {
            return (fq.type() == 'field' || fq.type() == 'range') && (histogram_ids.indexOf(fq.id()) == -1);
        }), function(fq) { return {'id': fq.id(), 'label': fq.field()} })
      );
  });

  self.selectedMultiq = ko.observable('query');

  self.getFacetFilter = function(widget_id) {
    var _fq = null;
    $.each(self.fqs(), function (index, fq) {
      if (fq.id() == widget_id) {
        _fq = fq;
        return false;
      }
    });
    return _fq;
  };

  self.getMultiq = ko.computed(function () {
    if (self.selectedMultiq()) {
      if (self.selectedMultiq() == 'query') {
        if (self.qs().length >= 2) {
          return 'query';
        }
      } else {
        var facet = self.getFacetFilter(self.selectedMultiq());
        if (facet && facet.filter().length > 0) {
          return 'facet';
        }
      }
    }
    return null;
  });

  self.addQ = function (data) {
    self.qs.push(ko.mapping.fromJS({'q': ''}));
    if (vm.selectedQDefinition() != null) {
      vm.selectedQDefinition().hasChanged(true);
    }
  };

  self.removeQ = function (query) {
    self.qs.remove(query);
    if (vm.selectedQDefinition() != null){
      vm.selectedQDefinition().hasChanged(true);
    }
  };

  self.selectedMultiq.subscribe(function () { // To keep below the computed objects!
    vm.search();
  });

  self.toggleFacet = function (data) {
    var fq = self.getFacetFilter(data.widget_id);

    if (fq == null) {
      self.fqs.push(ko.mapping.fromJS({
        'id': data.widget_id,
        'field': data.facet.cat,
        'filter': [{'exclude': data.exclude ? true : false, 'value': data.facet.value}],
        'type': 'field'
      }));
    } else {
      $.each(self.fqs(), function (index, fq) {
        if (fq.id() == data.widget_id) {
          var f = $.grep(fq.filter(), function(f) { return ko.toJSON(f.value()) == ko.toJSON(data.facet.value); });
          if (f.length > 0) {
            fq.filter.remove(f[0]);
            if (fq.filter().length == 0) {
              self.fqs.remove(fq);
            }
          } else {
            fq.filter.push(ko.mapping.fromJS({'exclude': data.exclude ? true : false, 'value': data.facet.value}));
          }
        }
      });
    }

    if (vm.selectedQDefinition() != null){
      vm.selectedQDefinition().hasChanged(true);
    }

    self.start(0);
    vm.search();
  }

  self.togglePivotFacet = function (data) {
    data.facet.cat = data.facet.fq_fields;
    data.facet.value = data.facet.fq_values;
    self.toggleFacet(data);
  }

  function _toggleSingleTermFacet(data, exclude) {
    var fq = getFilterByField(data.val.cat);
    var id;
    if (fq) {
      id = fq.id();
    } else {
      id = UUID();
    }
    self.toggleFacet({'widget_id': id, 'facet': {'cat': data.val.cat, 'value': data.val.value}, 'exclude': exclude});
    vm.search();
  }

  self.addSingleTermFacet = function(data) {
    _toggleSingleTermFacet(data, false);
  }
  self.removeSingleTermFacet = function(data) {
    _toggleSingleTermFacet(data, true);
  }

  self.selectRangeFacet = function (data) {
    if (data.force != undefined) {
      self.removeFilter(ko.mapping.fromJS({'id': data.widget_id, 'dontZoomOut': true}));
    }

    var fq = self.getFacetFilter(data.widget_id);

    if (fq == null) {
      self.fqs.push(ko.mapping.fromJS({
          'id': data.widget_id,
          'field': data.cat,
          'filter': [{'exclude': data.exclude ? true : false, 'value': data.from}],
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

    if (vm.selectedQDefinition() != null) {
      vm.selectedQDefinition().hasChanged(true);
    }

    self.start(0);
    if (data.no_refresh == undefined) {
      vm.search();
    }
  };

  self.selectRangeUpFacet = function (data) {
    if (data.force != undefined) {
      self.removeFilter(ko.mapping.fromJS({'id': data.widget_id, 'dontZoomOut': true}));
    }

    var fq = self.getFacetFilter(data.widget_id);

    if (fq == null) {
      self.fqs.push(ko.mapping.fromJS({
          'id': data.widget_id,
          'field': data.cat,
          'filter': [{'exclude': data.exclude ? true : false, 'value': data.from}],
          'properties': [{'from': data.from, 'to': data.to}],
          'type': 'range-up',
          'is_up': data.is_up
      }));
    } else {
      var f = $.grep(fq.filter(), function(f) { return f.value() == data.from; });

      if (f.length > 0) { // Unselect
        var excludeToRemove = f[0].exclude();
        var select = false;
      } else {
        var excludeToRemove = data.exclude ? true : false;
        var select = true;
      }

      var toRemove = []
      $.each(fq.filter(), function(index, filter) {
        if (filter.exclude() == excludeToRemove) {
          toRemove.push(filter.value());
          fq.filter.remove(filter);
        }
      });

      $.each(fq.properties(), function(index, prop) {
        if (toRemove.indexOf(prop.from()) != -1) {
          fq.properties.remove(prop);
        }
      })

      if (select) {
        fq.filter.push(ko.mapping.fromJS({'exclude': data.exclude ? true : false, 'value': data.from}));
        fq.properties.push(ko.mapping.fromJS({'from': data.from, 'to': data.to}));
      }

      if (fq.filter().length == 0) {
        self.removeFilter(ko.mapping.fromJS({'id': data.widget_id}));
      }
    }

    if (vm.selectedQDefinition() != null){
      vm.selectedQDefinition().hasChanged(true);
    }

    self.start(0);
    if (data.no_refresh == undefined) {
      vm.search();
    }
  };

  self.selectMapRegionFacet = function (data) {
    self.removeFilter(ko.mapping.fromJS({'id': data.widget_id, 'dontZoomOut': true}));

    self.fqs.push(ko.mapping.fromJS({
      'id': data.widget_id,
      'field': data.lat,
      'lat': data.lat,
      'lon': data.lon,
      'filter': [
        {'exclude': false, 'value': ko.mapping.toJSON(data.bounds)} // Need common type
      ],
      'type': 'map',
      'properties': {
        'lat_sw': data.bounds._southWest.lat, 'lon_sw': data.bounds._southWest.lng,
        'lat_ne': data.bounds._northEast.lat, 'lon_ne': data.bounds._northEast.lng
      }
    }));

    if (vm.selectedQDefinition() != null) {
      vm.selectedQDefinition().hasChanged(true);
    }

    self.start(0);
    vm.search();
  };

  function getFilterByField(field) {
    var _fq = null;
    $.each(self.fqs(), function (index, fq) {
      if (fq.field() == field && fq.id().indexOf('***') == 0) {
        _fq= fq;
        return false;
      }
    });
    return _fq;
  };

  self.removeFilter = function (data) {
    var found = false;
    $.each(self.fqs(), function (index, fq) {
      if (fq.id() == data.id()) {
        self.fqs.remove(fq);
        // Also re-init range select widget
        var rangeWidget = vm.collection.getFacetById(fq.id());
        if (data.dontZoomOut == undefined && rangeWidget != null && RANGE_SELECTABLE_WIDGETS.indexOf(rangeWidget.widgetType()) != -1 && fq.type() == 'range') {
          vm.collection.rangeZoomOut({'id': rangeWidget.id()});
        }
        found = true;
        return false;
      }
    });
    return found;
  };

  self.paginate = function (direction) {
    if (direction == 'next') {
      self.start(self.start() + vm.collection.template.rows() * 1.0);
    } else {
      self.start(self.start() - vm.collection.template.rows() * 1.0);
    }
    vm.search();
  };
};


var FieldAnalysis = function (vm, field_name) {
  var self = this;

  self.name = ko.observable(field_name);

  self.isLoading = ko.observable(true);

  self.section = ko.observable('terms');
  self.section.subscribe(function () {
    self.update();
  });
  self.terms = ko.mapping.fromJS({'prefix': '', 'data': []});
  self.terms.prefix.subscribe(function () {
    self.getTerms();
  });
  self.terms.prefix.extend({rateLimit: {timeout: 2000, method: "notifyWhenChangesStop"}});
  self.stats = ko.mapping.fromJS({'facet': '', 'data': []});

  var _statsUpdateTimeout = -1;
  self.stats.facet.subscribe(function () {
    // this is to avoid false positives from typeahead blur
    window.clearTimeout(_statsUpdateTimeout);
    _statsUpdateTimeout = window.setTimeout(function(){self.getStats()}, 200);
  });

  self.update = function() {
    if (self.section() == 'stats') {
      if (self.stats.data().length == 0) {
        self.getStats();
      }
    } else {
      if (self.terms.data().length == 0) {
         self.getTerms();
      }
    }
  }

  self.getTerms = function () {
    self.isLoading(true);
    self.terms.data.removeAll();
    $.post("/search/get_terms", {
      collection: ko.mapping.toJSON(vm.collection),
      analysis: ko.mapping.toJSON(self)
    }, function (data) {
      data = JSON.bigdataParse(data);
      if (data.status == 0) {
        if (data.terms != null) {
          $.each(data.terms, function (key, val) {
            self.terms.data.push({'key': key, 'val': val});
          });
        }
      }
      else if (data.status == 1) {
        self.terms.data.push({'key': 'Error', 'val': data.message});
      }
      else {
        $(document).trigger("error", data.message);
      }
      self.isLoading(false);
    }, "text").fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });
  };

  self.getStats = function () {
    self.stats.data.removeAll();
    self.isLoading(true);
    $.post("/search/get_stats", {
      collection: ko.mapping.toJSON(vm.collection),
      query: ko.mapping.toJSON(vm.query),
      analysis: ko.mapping.toJSON(self)
    }, function (data) {
      data = JSON.bigdataParse(data);
      if (data.status == 0) {
        if (data.stats.stats.stats_fields[self.name()] != null) {
          $.each(data.stats.stats.stats_fields[self.name()], function (key, val) {
            self.stats.data.push({'key': key, 'val': val});
          });
        }
      }
      else if (data.status == 1) {
        self.stats.data.push({'key': 'Error', 'val': data.message});
      }
      else {
        $(document).trigger("error", data.message);
      }
      self.isLoading(false);
    }, "text").fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });
  };
}


var Collection = function (vm, collection) {
  var self = this;

  self.id = ko.mapping.fromJS(collection.id);
  self.uuid = ko.observable(typeof collection.uuid != "undefined" && collection.uuid != null ? collection.uuid : UUID());
  self.name = ko.mapping.fromJS(collection.name);
  self.label = ko.mapping.fromJS(collection.label);
  self.description = ko.observable(typeof collection.description != "undefined" && collection.description != null ? collection.description : "");
  self.suggest = ko.mapping.fromJS(collection.suggest);
  self.enabled = ko.mapping.fromJS(collection.enabled);
  self.autorefresh = ko.mapping.fromJS(collection.autorefresh);
  self.autorefreshSeconds = ko.mapping.fromJS(collection.autorefreshSeconds || 60);
  self.idField = ko.observable(collection.idField);
  self.timeFilter = ko.mapping.fromJS(collection.timeFilter);
  self.timeFilter.value.subscribe(function () {
    vm.search();
  });
  self.timeFilter.from.subscribe(function () {
    vm.search();
  });
  self.timeFilter.to.subscribe(function () {
    vm.search();
  });
  self.timeFilter.type.subscribe(function (val) {
    if (val == 'fixed' && self.timeFilter.from().length == 0) {
      $.ajax({
        type: "POST",
        url: "/search/get_range_facet",
        data: {
          collection: ko.mapping.toJSON(self),
          facet: ko.mapping.toJSON({widgetType: 'facet-widget', field: self.timeFilter.field()}),
          action: 'get_range'
        },
        success: function (data) {
          self.timeFilter.from(data.properties.start);
          self.timeFilter.to(data.properties.end);
        }
      });
    } else {
      vm.search();
    }
  });

  collection.template.chartSettings = $.extend({
    chartType: 'bars',
    chartSorting: 'none',
    chartScatterGroup: null,
    chartScatterSize: null,
    chartScope: 'world',
    chartX: null,
    chartYSingle: null,
    chartYMulti: [],
    chartData: [],
    chartMapLabel: null
  }, collection.template.chartSettings);

  self.template = ko.mapping.fromJS(collection.template);

  for (var setting in self.template.chartSettings) {
    self.template.chartSettings[setting].subscribe(function () {
      huePubSub.publish('gridChartForceUpdate');
    });
  }

  self.template.fieldsSelected.subscribe(function () {
    vm.search();
  });
  self.template.extracode($("<span>").html(self.template.extracode()).text()); // Unescape HTML
  self.template.extracode.extend({rateLimit: {timeout: 3000, method: "notifyWhenChangesStop"}});
  self.template.template.extend({rateLimit: {timeout: 3000, method: "notifyWhenChangesStop"}});
  self.template.template.subscribe(function () {
    vm.resultsHash = '';
    vm.search();
  });
  self.template.isGridLayout.subscribe(function () {
    vm.results.removeAll();
    vm.resultsHash = '';
    vm.search();
  });
  if (self.template.leafletmap.latitudeField == undefined) {
    self.template.leafletmap.latitudeField = ko.observable();
  }
  if (self.template.leafletmap.longitudeField == undefined) {
    self.template.leafletmap.longitudeField = ko.observable();
  }
  if (self.template.leafletmap.labelField == undefined) {
    self.template.leafletmap.labelField = ko.observable();
  }

  self.template.leafletmapOn = ko.computed(function() {
    return self.template.leafletmap.latitudeField() != null && self.template.leafletmap.longitudeField() != null;
  });
  self.template.leafletmap.latitudeField.subscribe(function (newValue) {
    if (self.template.leafletmap.longitudeField() != null && newValue != null) {
      vm.search();
    }
  });
  self.template.leafletmap.longitudeField.subscribe(function (newValue) {
    if (self.template.leafletmap.latitudeField() != null && newValue != null) {
      vm.search();
    }
  });
  self.template.leafletmap.labelField.subscribe(function (newValue) {
    if (self.template.leafletmapOn()) {
      vm.search();
    }
  });

  self.template.selectedVisualField = ko.observable();
  self.template.selectedVisualFunction = ko.observable();
  self.template.selectedVisualFunction.subscribe(function (newValue) {
    var _vf = $("#visualFunctions");
    _vf.siblings(".muted").text(_vf.find(":selected").attr("title"));
  });
  self.template.selectedSourceField = ko.observable();
  self.template.selectedSourceFunction = ko.observable();
  self.template.selectedSourceFunction.subscribe(function (newValue) {
    var _sf = $("#sourceFunctions");
    _sf.siblings(".muted").text(_sf.find(":selected").attr("title"));
  });

  self.template.addFieldToVisual = function () {
    $(document).trigger("addFieldToVisual", self.template.selectedVisualField());
  };
  self.template.addFunctionToVisual = function () {
    $(document).trigger("addFunctionToVisual", self.template.selectedVisualFunction());
  };

  self.template.addFieldToSource = function () {
    $(document).trigger("addFieldToSource", self.template.selectedSourceField());
  };
  self.template.addFunctionToSource = function () {
    $(document).trigger("addFunctionToSource", self.template.selectedSourceFunction());
  };

  if (collection.facets.length > 0) {
    collection.facets.forEach(function (f) {
      if (typeof f.properties.facets_form.field === 'undefined') {
        f.properties.facets_form.field = null;
      }
    });
  }

  self.facets = ko.mapping.fromJS(collection.facets);
  $.each(self.facets(), function (index, facet) {
    facet.properties.limit.subscribe(function () {
      vm.search();
    });
    if (facet.properties.gap) {
      facet.properties.gap.subscribe(function () {
        vm.search();
      });
    }
    if (facet.properties.aggregate) {
      facet.properties.aggregate.subscribe(function () {
        vm.search();
      });
    }
    if (typeof facet.properties.facets != 'undefined') {
      $.each(facet.properties.facets(), function (index, pivotFacet) {
        if (pivotFacet.aggregate) {
          pivotFacet.aggregate.subscribe(function () {
            vm.search();
          });
        }
      });
    }
  });

  self.template.rows.subscribe(function() {
    vm.search();
  });
  self.template.rows.extend({rateLimit: {timeout: 1500, method: "notifyWhenChangesStop"}});

  self.fields = ko.mapping.fromJS(collection.fields);
  self.qdefinitions = ko.mapping.fromJS(collection.qdefinitions);

  self.availableFacetFields = ko.computed(function() {
    return self.fields();
  });

  self.selectedDocument = ko.observable({});

  self.newQDefinitionName = ko.observable("");

  self.addQDefinition = function () {
    if ($.trim(self.newQDefinitionName()) != "") {
      var _def = ko.mapping.fromJS({
        'name': $.trim(self.newQDefinitionName()),
        'id': UUID(),
        'data': ko.mapping.toJSON(vm.query)
      });
      self.qdefinitions.push(_def);
      self.loadQDefinition(_def);
      self.newQDefinitionName("");
    }
  };

  self.removeQDefinition = function (qdef) {
    $.each(self.qdefinitions(), function (index, qdefinition) {
      if (qdefinition.id() == qdef.id()) {
        self.qdefinitions.remove(qdefinition);
        return false;
      }
    });
  }

  self.loadQDefinition = function (qdefinition) {
    var qdef = ko.mapping.fromJSON(qdefinition.data());
    vm.query.uuid(qdef.uuid());
    vm.query.qs(qdef.qs());
    vm.query.fqs(qdef.fqs());
    vm.query.start(qdef.start());
    vm.query.selectedMultiq(qdef.selectedMultiq());
    qdefinition.hasChanged = ko.observable(false);

    vm.selectedQDefinition(qdefinition);
    if (window.location.hash.indexOf("collection") == -1) {
      if (location.getParameter("collection") != "") {
        hueUtils.changeURL("?collection=" + location.getParameter("collection") + "&qd=" + qdef.uuid());
      }
      else {
        window.location.hash = "qd=" + qdef.uuid();
      }
    }
    vm.search();
    $(document).trigger("loadedQDefinition");
    window.setTimeout(function () {
      vm.selectedQDefinition().hasChanged(false);
    }, 50);
  }

  self.reloadQDefinition = function () {
    self.loadQDefinition(vm.selectedQDefinition());
    vm.selectedQDefinition().hasChanged(false);
  }

  self.updateQDefinition = function () {
    for (var i = 0; i < self.qdefinitions().length; i++) {
      if (self.qdefinitions()[i].id() == vm.selectedQDefinition().id()) {
        self.qdefinitions()[i].data(ko.mapping.toJSON(vm.query));
        break;
      }
    }
    vm.selectedQDefinition().hasChanged(false);
  }

  self.unloadQDefinition = function () {
    vm.selectedQDefinition(null);
    vm.query.uuid(null);
    vm.query.qs.removeAll();
    vm.query.qs.push(ko.mapping.fromJS({q:""}));
    vm.query.fqs.removeAll();
    vm.query.start(0);
    vm.query.selectedMultiq([]);
    if (window.location.hash.indexOf("collection") == -1) {
      if (location.getParameter("collection") != "") {
        hueUtils.changeURL("?collection=" + location.getParameter("collection"));
      }
      else {
        window.location.hash = "";
      }
    }
  }

  self.getQDefinition = function (qDefID) {
    for (var i = 0; i < self.qdefinitions().length; i++) {
      var qdef = ko.mapping.fromJSON(self.qdefinitions()[i].data());
      if (qdef.uuid() == qDefID) {
        return self.qdefinitions()[i];
      }
    }
    return null;
  }

  self.addFacet = function (facet_json) {
    self.removeFacet(function(){return facet_json.widget_id});
    logGA('add_facet/' + facet_json.widgetType);

    $.post("/search/template/new_facet", {
      "collection": ko.mapping.toJSON(self),
        "id": facet_json.widget_id,
        "label": facet_json.name,
        "field": facet_json.name,
        "widget_type": facet_json.widgetType
      }, function (data) {
        if (data.status == 0) {
          var facet = ko.mapping.fromJS(data.facet);
          facet.properties.limit.subscribe(function () {
            vm.search();
          });
          if (facet.properties.gap) {
            facet.properties.gap.subscribe(function () {
              vm.search();
            });
          }
          if (facet.properties.aggregate) {
            facet.properties.aggregate.subscribe(function () {
              vm.search();
            });
          }
          self.facets.push(facet);
          vm.search();
        } else {
          $(document).trigger("error", data.message);
        }
    }).fail(function (xhr, textStatus, errorThrown) {});
  };

  self.addPivotFacetValue = function(facet) {
    var pivot = null;

    if (typeof facet.properties.facets_form.field == 'string') { // Hackish but we load back properties as simple objects
      pivot = ko.mapping.fromJS({
        'field': facet.properties.facets_form.field,
        'limit': facet.properties.facets_form.limit,
        'mincount': facet.properties.facets_form.mincount,
        'aggregate': facet.properties.facets_form.aggregate,
      });
      facet.properties.facets_form.field = null;
      facet.properties.facets_form.limit = 5;
      facet.properties.facets_form.mincount = 1;
      facet.properties.facets_form.aggregate = 'count';
    } else {
      if (typeof facet.properties.facets_form.field != 'undefined') {
        pivot = ko.mapping.fromJS({
          'field': facet.properties.facets_form.field(),
          'limit': facet.properties.facets_form.limit(),
          'mincount': facet.properties.facets_form.mincount(),
          'aggregate': facet.properties.facets_form.aggregate ? facet.properties.facets_form.aggregate() : ''
        });
        facet.properties.facets_form.field(null);
        facet.properties.facets_form.limit(5);
        facet.properties.facets_form.mincount(1);
        facet.properties.facets_form.aggregate ? facet.properties.facets_form.aggregate('count') : '';
      }
    }

    if (pivot != null) {
      pivot.aggregate.subscribe(function() {
        vm.search();
      });
      facet.properties.facets.push(pivot);
      vm.search();
    }
  }

  self.removePivotFacetValue = function(facet) {
    facet['pivot_facet'].properties.facets.remove(facet['value']);

    vm.search();
  }

  self.removeFacet = function (widget_id) {
    $.each(self.facets(), function (index, facet) {
      if (facet.id() == widget_id()) {
        self.facets.remove(facet);
        return false;
      }
    });
  }

  self.removeLeaflet = function (widget_json) {
    if (widget_json.widgetType() == "leafletmap-widget") {
      self.template.leafletmap.latitudeField(null);
      self.template.leafletmap.longitudeField(null);
      self.template.leafletmap.labelField(null);
    }
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

  self.getHistogramFacets = function () {
    var _facets = [];
    $.each(self.facets(), function (index, facet) {
      if (facet.widgetType() == 'histogram-widget') {
        _facets.push(facet);
      }
    });
    return _facets;
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

  self.template.fieldsNames = ko.computed(function () {
    return $.map(self.template.fieldsAttributes(), function(field) {
      return field.name();
    }).sort(function (a, b) {
      return a.toLowerCase().localeCompare(b.toLowerCase());
    });
  });

  self.template.sortedGeogFieldsNames = ko.computed(function () {
    return $.map(
      $.grep(self.availableFacetFields(), function(field) {
        return FLOAT_TYPES.indexOf(field.type()) != -1 || GEO_TYPES.indexOf(field.type()) != -1 || field.type().match(/rpt$/);
      }),
      function (field) {
        return field.name();
    }).sort(function (a, b) {
      return a.toLowerCase().localeCompare(b.toLowerCase());
    });
  });

  self.template.getMeta = function (extraCheck) {
    var iterable = self.template.fieldsAttributes();
    if (self.template.fields().length > 0) {
      iterable = self.template.fields();
    }
    return $.map(iterable, function (field) {
      if (typeof field !== 'undefined' && field.name() != '' && extraCheck(field.type())) {
        return field;
      }
    }).sort(function (a, b) {
      return a.name().toLowerCase().localeCompare(b.name().toLowerCase());
    });
  }

  function alwaysTrue() {
    return true;
  }

  function isNumericColumn(type) {
    return $.inArray(type, NUMBER_TYPES.concat(FLOAT_TYPES)) > -1;
  }

  function isDateTimeColumn(type) {
    return $.inArray(type, DATE_TYPES) > -1;
  }

  function isStringColumn(type) {
    return !isNumericColumn(type) && !isDateTimeColumn(type);
  }

  self.template.cleanedMeta = ko.computed(function () {
    return self.template.getMeta(alwaysTrue);
  });

  self.template.cleanedNumericMeta = ko.computed(function () {
    return self.template.getMeta(isNumericColumn);
  });

  self.template.cleanedStringMeta = ko.computed(function () {
    return self.template.getMeta(isStringColumn);
  });

  self.template.cleanedDateTimeMeta = ko.computed(function () {
    return self.template.getMeta(isDateTimeColumn);
  });

  self.template.hasDataForChart = ko.computed(function () {
    var hasData = false;
    if (self.template.chartSettings.chartType() == ko.HUE_CHARTS.TYPES.BARCHART || self.template.chartSettings.chartType() == ko.HUE_CHARTS.TYPES.LINECHART) {
      hasData = typeof self.template.chartSettings.chartX() != "undefined" && self.template.chartSettings.chartX() != null && self.template.chartSettings.chartYMulti().length > 0;
    }
    else {
     hasData = typeof self.template.chartSettings.chartX() != "undefined" && self.template.chartSettings.chartX() != null && typeof self.template.chartSettings.chartYSingle() != "undefined" && self.template.chartSettings.chartYSingle() != null ;
    }
    if (!hasData && self.template.showChart()){
      self.template.showFieldList(true);
    }
    return hasData;
  });

  self.getTemplateField = function (name) {
    var _field = null;
    $.each(self.template.fields(), function (index, field) {
      if (field.name() == name) {
        _field = field;
        return false;
      }
    });
    return _field;
  };

  self.template.fieldsModalFilter = ko.observable(""); // For UI
  self.template.fieldsModalType = ko.observable(""); // For UI
  self.template.fieldsAttributesFilter = ko.observable(""); // For UI

  self.template.filteredAttributeFieldsAll = ko.observable(true);
  self.template.filteredAttributeFields = ko.computed(function() {
    var _fields = [];

    var _iterable = self.template.fieldsAttributes();
    if (! self.template.filteredAttributeFieldsAll()){
      _iterable = self.template.fields();
    }

    $.each(_iterable, function (index, field) {
      if (self.template.fieldsAttributesFilter() == "" || field.name().toLowerCase().indexOf(self.template.fieldsAttributesFilter().toLowerCase()) > -1){
        _fields.push(field);
      }
    });

    return _fields;
  });
  self.template.availableWidgetFields = ko.computed(function() {
    if (self.template.fieldsModalType() == 'histogram-widget' || self.template.fieldsModalType() == 'timeline-widget') {
      return vm.availableDateFields();
    }
    else if (self.template.fieldsModalType() == 'line-widget') {
      return vm.availableNumberFields();
    }
    else if (self.template.fieldsModalType() == 'map-widget') {
      return vm.availableStringFields();
    }
    else if (self.template.fieldsModalType() == 'tree-widget' || self.template.fieldsModalType() == 'heatmap-widget') {
      return vm.availablePivotFields();
    }
    else {
      return self.availableFacetFields();
    }
  });
  self.template.availableWidgetFieldsNames = ko.computed(function() {
    return $.map(self.template.availableWidgetFields(), function(field) {
      return field.name();
    });
  });

  self.template.filteredModalFields = ko.pureComputed(function () {
    var filter = self.template.fieldsModalFilter();
    if (!filter) {
      return self.template.availableWidgetFields();
    } else {
      return ko.utils.arrayFilter(self.template.availableWidgetFields(), function (field) {
        return field.name().toLowerCase().indexOf(filter.toLowerCase()) > -1;
      });
    }
  });

  self.switchCollection = function() { // Long term would be to reload the page
    $.post("/search/get_collection", {
        name: self.name()
    }, function (data) {
      if (data.status == 0) {
        self.idField(data.collection.collection.idField);
        self.template.template(data.collection.collection.template.template);
        self.template.fieldsAttributes.removeAll();
        $.each(data.collection.collection.template.fieldsAttributes, function(index, field) {
          self.template.fieldsAttributes.push(ko.mapping.fromJS(field));
        });
        self.fields.removeAll();
        $.each(data.collection.collection.fields, function(index, field) {
          self.fields.push(ko.mapping.fromJS(field));
        });

        self.syncDynamicFields();
      }
    }).fail(function (xhr, textStatus, errorThrown) {});
  };

  function diff(A, B) {
    return A.filter(function (a) {
      return B.indexOf(a) == -1;
    });
  }

  function syncArray(currentObservable, newJson, isDynamic) {
    // Get names of fields
    var _currentFieldsNames = $.map(
        $.grep(currentObservable(), function(field) {
          return field.isDynamic() == isDynamic;
        }), function(field) {
      return field.name() + '|' + field.type();
    });
    var _newFieldsNames = $.map(
      $.grep(newJson, function(field) {
          return field.isDynamic == isDynamic;
        }), function(field) {
      return field.name + '|' + field.type;
    });

    var _toDelete = diff(_currentFieldsNames, _newFieldsNames);
    var _toAdd = diff(_newFieldsNames, _currentFieldsNames);

    // Deleted fields
    self.template.fieldsSelected.removeAll(_toDelete);
    var bulk = $.grep(currentObservable(), function(field) {
      return (_toDelete.indexOf(field.name() + '|' + field.type()) != -1)
    });
    currentObservable.removeAll(bulk);

    // New fields
    $.each(newJson, function(index, field) {
      if (_toAdd.indexOf(field.name + '|' + field.type) != -1) {
        currentObservable.push(ko.mapping.fromJS(field));
      }
    });
  }

  self.syncFields = function() {
    $.post("/search/get_collection", {
        name: self.name()
      }, function (data) {
        if (data.status == 0) {
          self.idField(data.collection.collection.idField);
          syncArray(self.template.fieldsAttributes, data.collection.collection.template.fieldsAttributes, false);
          syncArray(self.fields, data.collection.collection.fields, false);
        }
        // After sync the dynamic fields
        self.syncDynamicFields();
    }).fail(function (xhr, textStatus, errorThrown) {});
  };

  self.syncDynamicFields = function () {
    $.post("/search/index/fields/dynamic", {
        name: self.name()
      }, function (data) {
        if (data.status == 0) {
          syncArray(self.template.fieldsAttributes, data.gridlayout_header_fields, true);
          syncArray(self.fields, data.fields, true);
        }
    }).fail(function (xhr, textStatus, errorThrown) {});
  };

  self.toggleSortColumnGridLayout = function (template_field) {
    if (! template_field.sort.direction()) {
      template_field.sort.direction('desc');
    } else if (template_field.sort.direction() == 'desc') {
      template_field.sort.direction('asc');
    } else {
      template_field.sort.direction(null);
    }

    $(document).trigger("setResultsHeight");
    vm.search();
  };

  self.toggleSortFacet = function (facet_field, event) {
    if (facet_field.properties.sort() == 'desc') {
      facet_field.properties.sort('asc');
    } else {
      facet_field.properties.sort('desc');
    }

    if (facet_field.type() == 'range-up') {
      vm.query.removeFilter(ko.mapping.fromJS({'id': facet_field.id})); // Reset filter query
    }

    vm.search();
  };

  self.toggleRangeFacet = function (facet_field, event) {
    vm.query.removeFilter(ko.mapping.fromJS({'id': facet_field.id})); // Reset filter query

    if (facet_field.type() == 'field') {
       facet_field.type('range');
     } else if (facet_field.type() == 'range') {
       facet_field.type('range-up')
     } else if (facet_field.type() == 'range-up') {
       facet_field.type('field')
     }

    vm.search();
  };

  self.selectTimelineFacet = function (data) {
    var facet = self.getFacetById(data.widget_id);

    if (facet.properties.isDate()) {
      facet.properties.start(moment(data.from).utc().format("YYYY-MM-DD[T]HH:mm:ss[Z]"));
      facet.properties.end(moment(data.to).utc().format("YYYY-MM-DD[T]HH:mm:ss[Z]"));
      facet.properties.min(moment(data.from).utc().format("YYYY-MM-DD[T]HH:mm:ss[Z]"));
      facet.properties.max(moment(data.to).utc().format("YYYY-MM-DD[T]HH:mm:ss[Z]"));
    }

    vm.query.selectRangeFacet({widget_id: data.widget_id, from: data.from, to: data.to, cat: data.cat, no_refresh: true, force: true});

    $.ajax({
      type: "POST",
      url: "/search/get_range_facet",
      data: {
        collection: ko.mapping.toJSON(self),
        facet: ko.mapping.toJSON(facet),
        action: 'select'
      },
      success: function (data) {
        if (data.status == 0) {
          facet.properties.gap(data.properties.gap);
        }
      },
      async: false
    });

    vm.search();
  }

  self.rangeZoomOut = function (facet_json) {
    var facet_id = ko.mapping.toJS(facet_json).id;
    var facet = self.getFacetById(facet_id);

    vm.query.removeFilter(ko.mapping.fromJS({'id': facet_id}));
    if (facet.properties.gap() != null) { // Bar, line charts don't have gap
      facet.properties.gap(facet.properties.initial_gap());
    }
    if (facet.properties.initial_start() != null) { // Bar and line charts
      facet.properties.start(facet.properties.initial_start());
      facet.properties.end(facet.properties.initial_end());
      facet.properties.min(facet.properties.initial_start());
      facet.properties.max(facet.properties.initial_end());
    }

    vm.search();
  }

  self.translateSelectedField = function (index, direction) {
    var array = self.template.fieldsSelected();
    vm.resultsHash = '';

    if (direction == 'left') {
      self.template.fieldsSelected.splice(index - 1, 2, array[index], array[index - 1]);
    } else {
      self.template.fieldsSelected.splice(index, 2, array[index + 1], array[index]);
    }
  };

  self.upDownFacetLimit = function (facet_id, direction) {
    var facet = self.getFacetById(facet_id);

    if (facet.properties.prevLimit == undefined) {
      facet.properties.prevLimit = facet.properties.limit();
    }

    if (direction == 'up') {
      facet.properties.limit(facet.properties.limit() + 10);
    } else {
      facet.properties.limit(facet.properties.limit() - 10);
    }

    vm.search();
  };
};

var NewTemplate = function (vm, initial) {
  var self = this;

  self.collections = ko.mapping.fromJS(initial.collections);
  self.layout = initial.layout;
  self.inited = ko.observable(self.collections().length > 0); // No collection if not a new dashboard

  self.init = function() {
    if (self.inited()) {
      // If new dashboard
      vm.collection.name.subscribe(function(newValue) {
        vm.collection.label(newValue);
        vm.collection.switchCollection();
        vm.search();
      });
    } else {
      self.syncCollections();
    }

    if (initial.autoLoad) {
      magicLayout(vm);
    }
  };

  self.syncCollections = function () {
    vm.isSyncingCollections(true);
    $.post("/search/get_collections", {
        collection: ko.mapping.toJSON(vm.collection),
        show_all: ko.mapping.toJSON(vm.showCores)
      }, function (data) {
        if (data.status == 0) {
          // Sync new and old names
          $.each(data.collection, function(index, name) {
            if (self.collections.indexOf(name) == -1) {
              self.collections.push(name);
            }
          });
          var _toDelete = [];
          $.each(self.collections(), function(index, collection) {
            if (data.collection.indexOf(collection) == -1) {
              _toDelete.push(collection);
            }
          });
          $.each(_toDelete, function(index, collection) {
            self.collections.remove(collection);
          });
        }
        else {
          $(document).trigger("error", data.message);
        }
    }).fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    }).done(function() {
      vm.isSyncingCollections(false);
      self.inited(true);
    });
  };
};


var DATE_TYPES = ['date', 'tdate'];
var NUMBER_TYPES = ['int', 'tint', 'long', 'tlong', 'float', 'tfloat', 'double', 'tdouble', 'currency'];
var FLOAT_TYPES = ['float', 'tfloat', 'double', 'tdouble'];
var GEO_TYPES = ['SpatialRecursivePrefixTreeFieldType'];

var RANGE_SELECTABLE_WIDGETS = ['histogram-widget', 'bar-widget', 'line-widget'];


var SearchViewModel = function (collection_json, query_json, initial_json) {
  var self = this;

  self.intervalOptions = ko.observableArray(ko.bindingHandlers.daterangepicker.INTERVAL_OPTIONS);
  self.isNested = ko.observable(false);
  self.isLatest = ko.mapping.fromJS(typeof initial_json.is_latest != "undefined" ? initial_json.is_latest : false);

  // Models
  self.collection = new Collection(self, collection_json.collection);
  self.query = new Query(self, query_json);
  self.initial = new NewTemplate(self, initial_json);

  // UI
  self.selectedQDefinition = ko.observable();
  self.response = ko.observable({});
  self.results = ko.observableArray([]);
  self.resultsHash = '';
  self.norm_facets = {};
  self.getFacetFromQuery = function (facet_id) {
    if (! (facet_id in self.norm_facets)) {
      self.norm_facets[facet_id] = ko.mapping.fromJS({
          id: facet_id,
          has_data: false,
          hash: '',
          counts: [],
          label: '',
          field: '',
          dimension: 1,
          extraSeries: []
      });
    }

    return self.norm_facets[facet_id];
  };
  self.toggledGridlayoutResultChevron = ko.observable(false);
  self.enableGridlayoutResultChevron = function() {
    self.toggledGridlayoutResultChevron(true);
  };
  self.disableGridlayoutResultChevron = function() {
    self.toggledGridlayoutResultChevron(false);
  };
  self.fieldAnalyses = ko.observableArray([]);
  self.fieldAnalysesName = ko.observableArray("");
  self.fieldsAnalysisAttributesNames = ko.computed(function () {
    var _fields = [];
    $.each(self.collection.template.fieldsAttributes(), function (index, field) {
      if (field.name() != self.fieldAnalysesName()){
        _fields.push(field.name())
      }
    });
    return _fields;
  });

  self.previewColumns = ko.observable("");
  self.columns = ko.observable([]);
  loadLayout(self, collection_json.layout);

  self.additionalMustache = null;

  self.isEditing = ko.observable(false);
  self.toggleEditing = function () {
    self.isEditing(! self.isEditing());
  };
  self.isRetrievingResults = ko.observable(false);
  self.hasRetrievedResults = ko.observable(true);

  self.showCores = ko.observable(false);
  self.showCores.subscribe(function(newValue) {
    self.initial.syncCollections();
  });
  self.isSyncingCollections = ko.observable(false);

  self.isPlayerMode = ko.observable(false);

  function bareWidgetBuilder(name, type){
    return new Widget({
      size: 12,
      id: UUID(),
      name: name,
      widgetType: type
    });
  }

  self.draggableHit = ko.observable(bareWidgetBuilder("Hit Count", "hit-widget"));
  self.draggableFacet = ko.observable(bareWidgetBuilder("Facet", "facet-widget"));
  self.draggableResultset = ko.observable(bareWidgetBuilder("Grid Results", "resultset-widget"));
  self.draggableHtmlResultset = ko.observable(bareWidgetBuilder("HTML Results", "html-resultset-widget"));
  self.draggableHistogram = ko.observable(bareWidgetBuilder("Histogram", "histogram-widget")); // Deprecated
  self.draggableBar = ko.observable(bareWidgetBuilder("Bar Chart", "bar-widget")); // Deprecated
  self.draggableMap = ko.observable(bareWidgetBuilder("Map", "map-widget")); // Deprecated
  self.draggableLeafletMap = ko.observable(bareWidgetBuilder("Marker Map", "leafletmap-widget"));
  self.draggableLine = ko.observable(bareWidgetBuilder("Line Chart", "line-widget")); // Deprecated
  self.draggablePie = ko.observable(bareWidgetBuilder("Pie Chart", "pie-widget")); // Deprecated
  self.draggablePie2 = ko.observable(bareWidgetBuilder("Pie Chart", "pie2-widget"));
  self.draggableFilter = ko.observable(bareWidgetBuilder("Filter Bar", "filter-widget"));
  self.draggableTree = ko.observable(bareWidgetBuilder("Tree", "tree-widget"));
  self.draggableHeatmap = ko.observable(bareWidgetBuilder("Heatmap", "heatmap-widget"));
  self.draggableCounter = ko.observable(bareWidgetBuilder("Counter", "hit-widget"));
  self.draggableBucket = ko.observable(bareWidgetBuilder("Chart", "bucket-widget"));
  self.draggableTimeline = ko.observable(bareWidgetBuilder("Timeline", "timeline-widget"));
  self.draggableGradienMap = ko.observable(bareWidgetBuilder("Gradient Map", "gradient-map-widget"));

  self.availableDateFields = ko.computed(function() {
    return $.grep(self.collection.availableFacetFields(), function(field) { return DATE_TYPES.indexOf(field.type()) != -1; });
  });
  self.availableNumberFields = ko.computed(function() {
    return $.grep(self.collection.availableFacetFields(), function(field) { return NUMBER_TYPES.indexOf(field.type()) != -1; });
  });
  self.availablePivotFields = ko.computed(function() {
    return self.collection.fields();
  });
  self.availableStringFields = ko.computed(function() {
    return $.grep(self.collection.availableFacetFields(), function(field) { return NUMBER_TYPES.indexOf(field.type()) == -1 && DATE_TYPES.indexOf(field.type()) == -1; });
  });

  function getWidgets(equalsTo) {
    return $.map(self.columns(), function (col){return $.map(col.rows(), function(row){ return $.grep(row.widgets(), function(widget){ return equalsTo(widget); });}) ;})
  };

  self.availableDraggableResultset = ko.computed(function() {
    return getWidgets(function(widget) { return ['resultset-widget', 'html-resultset-widget'].indexOf(widget.widgetType()) != -1; }).length == 0;
  });
  self.availableDraggableLeaflet = ko.computed(function() {
    return getWidgets(function(widget) { return ['leafletmap-widget'].indexOf(widget.widgetType()) != -1; }).length == 0;
  });
  self.availableDraggableFilter = ko.computed(function() {
    return getWidgets(function(widget) { return widget.widgetType() == 'filter-widget'; }).length == 0;
  });
  self.availableDraggableHistogram = ko.computed(function() {
    return self.availableDateFields().length > 0;
  });
  self.availableTimeline = ko.computed(function() {
    return self.availableDateFields().length > 0;
  });
  self.availableDraggableNumbers = ko.computed(function() {
    return self.availableNumberFields().length > 0;
  });
  self.availableDraggableChart = ko.computed(function() {
    return self.collection.availableFacetFields().length > 0;
  });
  self.availableDraggableMap = ko.computed(function() {
    return self.availableStringFields().length > 0;
  })


  self.init = function (callback) {
    self.isEditing(self.columns().length == 0);
    self.initial.init();
    self.collection.syncFields();
    self.search(callback);
  }

  self.searchBtn = function () {
    self.query.start(0);
    self.search();
  };

  self.search = function (callback) {
    $(".jHueNotify").hide();
    logGA('search');
    self.isRetrievingResults(true);

    if (self.selectedQDefinition() != null) {
      var _prop = ko.mapping.fromJSON(self.selectedQDefinition().data());
      if (ko.toJSON(_prop.qs()) != ko.mapping.toJSON(self.query.qs())
        || ko.toJSON(_prop.selectedMultiq()) != ko.mapping.toJSON(self.query.selectedMultiq())) {
        self.selectedQDefinition().hasChanged(true);
      }
    }
    else if (location.getParameter("collection") != "") {
      var firstQuery = self.query.qs()[0].q();
      hueUtils.changeURL("?collection=" + location.getParameter("collection") + (firstQuery ? "&q=" + firstQuery : ""));
    }

    // Multi queries
    var multiQs = [];
    var multiQ = self.query.getMultiq();

    if (multiQ != null) {
      var facet = {};
      var queries = [];

      if (multiQ == 'query') {
        queries = self.query.qs();
      } else {
        facet = self.query.getFacetFilter(self.query.selectedMultiq());
        queries = $.map(facet.filter(), function (f) {
          return f.value();
        });
      }

      multiQs = $.map(queries, function (qdata) {
        return $.post("/search/get_timeline", {
          collection: ko.mapping.toJSON(self.collection),
          query: ko.mapping.toJSON(self.query),
          facet: ko.mapping.toJSON(facet),
          qdata: ko.mapping.toJSON(qdata),
          multiQ: multiQ
        }, function (data) {
          return data
        });
      });
    }

    $.each(self.fieldAnalyses(), function (index, analyse) { // Invalidate stats analysis
      analyse.stats.data.removeAll();
    });

    if (self.getFieldAnalysis()) {
      self.getFieldAnalysis().update();
    }


    $.when.apply($, [
        $.post("/search/search", {
            collection: ko.mapping.toJSON(self.collection),
            query: ko.mapping.toJSON(self.query),
            layout: ko.mapping.toJSON(self.columns)
          }, function (data) {
            try {
              data = JSON.bigdataParse(data);

              if (typeof callback === "function") {
                callback(data);
              }

              $.each(data.normalized_facets, function (index, new_facet) {
                var facet = self.getFacetFromQuery(new_facet.id);
                var _hash = ko.mapping.toJSON(new_facet);

                if (!facet.has_data() || facet.hash() != _hash) {
                  facet.counts(new_facet.counts);
                  facet.label(new_facet.label);
                  facet.field(new_facet.field);
                  facet.dimension(new_facet.dimension);
                  facet.extraSeries(typeof new_facet.extraSeries != 'undefined' ? new_facet.extraSeries : []);
                  facet.hash(_hash);
                  facet.has_data(true);
                }
              });

              // Delete norm_facets that were deleted

              self.response(data);

              if (data.error) {
                $(document).trigger("error", data.error);
              }
              else {
                var _resultsHash = ko.mapping.toJSON(data.response.docs);

                if (self.resultsHash != _resultsHash) {

                  var _docs = [];
                  var leafletmap = {};
                  var _mustacheTmpl = self.collection.template.isGridLayout() ? "" : fixTemplateDotsAndFunctionNames(self.collection.template.template());
                  $.each(data.response.docs, function (index, item) {
                    var row = [];
                    var _externalLink = item.externalLink;
                    var _details = item.details;
                    var _id = item.hueId;
                    delete item["externalLink"];
                    delete item["details"];
                    delete item["hueId"];
                    var fields = self.collection.template.fieldsSelected();
                    // Display selected fields or whole json document
                    if (fields.length != 0) {
                      $.each(self.collection.template.fieldsSelected(), function (index, field) {
                        row.push(item[field]);
                      });
                    } else {
                      row.push(ko.mapping.toJSON(item));
                    }
                    if (self.collection.template.leafletmapOn()) {
                      leafletmap = {
                        'latitude': item[self.collection.template.leafletmap.latitudeField()],
                        'longitude': item[self.collection.template.leafletmap.longitudeField()],
                        'label': self.collection.template.leafletmap.labelField() ? item[self.collection.template.leafletmap.labelField()] : ""
                      }
                    }
                    var doc = {
                      'id': _id,
                      'row': row,
                      'item': ko.mapping.fromJS(item),
                      'showEdit': ko.observable(false),
                      'hasChanged': ko.observable(false),
                      'externalLink': ko.observable(_externalLink),
                      'details': ko.observableArray(_details),
                      'originalDetails': ko.observable(''),
                      'showDetails': ko.observable(false),
                      'leafletmap': leafletmap
                    };
                    if (!self.collection.template.isGridLayout()) {
                      // fix the fields that contain dots in the name
                      addTemplateFunctions(item);
                      if (self.additionalMustache != null && typeof self.additionalMustache == "function") {
                        self.additionalMustache(item);
                      }
                      doc.content = Mustache.render(_mustacheTmpl, item);
                    }
                    _docs.push(doc);
                  });
                  self.results(_docs);
                }
                self.resultsHash = _resultsHash;
              }
            }
            catch (e) {

            }
          },
          "text")
      ].concat(multiQs)
    )
      .done(function () {
        if (arguments[0] instanceof Array) { // If multi queries
          var histograms = self.collection.getHistogramFacets();
          for (var h = 0; h < histograms.length; h++) { // Do not use $.each here
            var histoFacetId = histograms[h].id();
            var histoFacet = self.getFacetFromQuery(histoFacetId);
            var _series = [];
            for (var i = 1; i < arguments.length; i++) {
              _series.push(arguments[i][0]['series']);
            }
            histoFacet.extraSeries(_series);
          }
          ;
          self.response.valueHasMutated();
        }
      })
      .fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
      })
      .always(function () {
        self.isRetrievingResults(false);
        self.hasRetrievedResults(true);
        $('.btn-loading').button('reset');
      });
  };

  self.suggest = function (query, callback) {
    $.post("/search/suggest/", {
      collection: ko.mapping.toJSON(self.collection),
      query: query
    }, function (data) {
      if (data.status == 0) {
        callback(data);
      }
      else {
        callback();
      }
    }).fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });
  };

  self.removeWidget = function (widget_json) {
    self.collection.removeFacet(widget_json.id);
    self.collection.removeLeaflet(widget_json);
    var refresh = self.query.removeFilter(widget_json);
    self.removeWidgetById(widget_json.id());

    if (refresh) {
      self.search();
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

  self.removeWidgetById = function (widget_id) {
    $.each(self.columns(), function (i, col) {
      $.each(col.rows(), function (j, row) {
        $.each(row.widgets(), function (z, widget) {
          if (widget && widget.id() == widget_id){
            row.widgets.remove(widget);
            row.autosizeWidgets();
            return false;
          }
        });
      });
    });
  }

  self.getDocument = function (doc, callback) {
    $.post("/search/get_document", {
      collection: ko.mapping.toJSON(self.collection),
      id: doc.id
    }, function (data) {
      data = JSON.bigdataParse(data);
      var details = [];
      doc.details.removeAll();
      if (data.status == 0) {

        $.each(data.doc.doc, function(key, val) {
          var _field = ko.mapping.fromJS({
              key: key,
              value: val,
              hasChanged: false
          });
          _field.value.subscribe(function() {
            doc.hasChanged(true);
            _field.hasChanged(true);
          });
          details.push(_field);
        });
      }
      else if (data.status == 1) {
        $(document).trigger("info", data.message);
        details.push(ko.mapping.fromJS({
            key: '',
            value: ''
        }));
      }
      else {
        $(document).trigger("error", data.message);
      }
      doc.details(details);
      doc.originalDetails(ko.toJSON(doc.details()));
      if (callback) {
        callback(details);
      }
    }, "text").fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });
  };

  self.updateDocument = function (doc) {
    $.post("/search/update_document", {
      collection: ko.mapping.toJSON(self.collection),
      document: ko.mapping.toJSON(doc),
      id: doc.id
    }, function (data) {
      data = JSON.bigdataParse(data);
      if (data.status == 0) {
        doc.showEdit(false);

        var versionField = $.grep(doc.details(), function(field) { return field.key() == '_version_'; });
        if (versionField.length > 0) {
          versionField[0].value( data.update.adds[1]);
          versionField[0].hasChanged(false);
        };

        doc.originalDetails(ko.toJSON(doc.details()));
      }
      else {
        $(document).trigger("error", data.message);
      }
    }, "text").fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });
  };

  self.showFieldAnalysis = function(vm, e) {
    if (self.fieldAnalysesName()) {
      var analyse = self.getFieldAnalysis();

      if (analyse == null) {
        analyse = new FieldAnalysis(self, self.fieldAnalysesName());
        self.fieldAnalyses.push(analyse);
      }

      analyse.update();
      $(document).trigger("shownAnalysis", e);
    }
  }

  self.getFieldAnalysis = function() {
    var field_name = self.fieldAnalysesName();
    var _analyse = null;

    $.each(self.fieldAnalyses(), function (index, analyse) {
      if (analyse.name() == field_name) {
        _analyse = analyse;
        return false;
      }
    });

    return _analyse;
  }

  self.save = function () {
    $.post("/search/save", {
      collection: ko.mapping.toJSON(self.collection),
      layout: ko.mapping.toJSON(self.columns)
    }, function (data) {
      if (data.status == 0) {
        self.collection.id(data.id);
        $(document).trigger("info", data.message);
        if (window.location.search.indexOf("collection") == -1) {
          window.location.hash = '#collection=' + data.id;
        }
      }
      else {
        $(document).trigger("error", data.message);
      }
    }).fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });
  };

};

function logGA(page) {
  if (typeof trackOnGA == 'function') {
    trackOnGA('search/' + page);
  }
}

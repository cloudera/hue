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

function magicSearchLayout(vm) {
  loadSearchLayout(vm, vm.initial.layout);
  $(document).trigger("magicSearchLayout");
}

function loadSearchLayout(viewModel, json_layout) {
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
    var column = new Column(json_col.size, _rows, viewModel);
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


var FieldAnalysis = function (vm, fieldName, fieldType) {
  var self = this;

  self.name = ko.observable(fieldName);
  self.type = ko.observable(fieldType);

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
    $.post("/dashboard/get_terms", {
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
    $.post("/dashboard/get_stats", {
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
  self.engine = ko.observable(typeof collection.engine != "undefined" && collection.engine != null ? collection.engine : "solr");
  self.engine.subscribe(function() {
    self.name(null);
  });
  self.async = ko.computed(function() {
    return ['impala', 'hive'].indexOf(self.engine()) != -1;
  });
  self.queryResult = ko.observable(new QueryResult(self, {
    type: self.engine(),
  }));
  self.supportAnalytics = ko.pureComputed(function() {
    var engine = vm.initial.getEngine(self.engine());
    return engine && engine.analytics();
  });
  self.supportNesting = ko.pureComputed(function() {
    var engine = vm.initial.getEngine(self.engine());
    return engine && engine.nesting();
  });
  self.nested = ko.mapping.fromJS(collection.nested);
  self.nestedNames = ko.computed(function() {
    function flatten(values) {
      var fields = [];
      $.each(values, function (index, facet) {
        fields.push(facet.filter());
        if (facet.values().length > 0) {
          fields.push.apply(fields, flatten(facet.values()));
        }
      });
      return fields;
    }
    return self.nested && self.nested.schema ? flatten(self.nested.schema()) : [];
  });
  self.nestedAddLeaf = function(leaf) {
    leaf.push(
      ko.mapping.fromJS(
        {'filter': '', 'name': '', 'selected': false, 'values': []} // limit 10
    ));
  };
  self.enabled = ko.mapping.fromJS(collection.enabled);
  self.autorefresh = ko.mapping.fromJS(collection.autorefresh);
  self.autorefreshSeconds = ko.mapping.fromJS(collection.autorefreshSeconds || 60).extend({ numeric: 0, throttle: 1000 });
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
    if (val == 'fixed'){
      self.autorefresh(false);
    }
    if (val == 'fixed' && self.timeFilter.from().length == 0) {
      $.ajax({
        type: "POST",
        url: "/dashboard/get_range_facet",
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
  if (typeof self.template.extracode == 'undefined') {
    self.template.extracode = ko.observable();
  }
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
  if (typeof self.template.leafletmap.latitudeField == 'undefined') {
    self.template.leafletmap.latitudeField = ko.observable();
  }
  if (typeof self.template.leafletmap.longitudeField == 'undefined') {
    self.template.leafletmap.longitudeField = ko.observable();
  }
  if (typeof self.template.leafletmap.labelField == 'undefined') {
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

  self.widgetType = ko.computed(function() {
     return self.template.isGridLayout() ? 'resultset-widget' : 'html-resultset-widget';
  });

  if (collection.facets.length > 0) {
    collection.facets.forEach(function (f) {
      if (f.properties.facets_form && typeof f.properties.facets_form.field === 'undefined') {
        f.properties.facets_form.field = null;
      }
    });
  }

  self._addObservablesToFacet = function(facet, vm) {
    facet.properties.limit.subscribe(function () {
      vm.search();
    });
    facet.properties.mincount.subscribe(function () {
      vm.search();
    });
    if (facet.properties.gap) {
      facet.properties.gap.subscribe(function () {
        vm.search();
      });
    }
    if (facet.properties.aggregate) {
      facet.properties.aggregate.function.subscribe(function () {
        vm.search();
      });
    }
    if (facet.properties.facets) {
      facet.properties.facets.subscribe(function(newValue) {
        vm.search();
      });
    }

    // For Hue 4 facets only
    if (typeof facet.template != 'undefined') {
      facet.template.filteredAttributeFields = ko.computed(function() { // Dup of template.filteredAttributeFields
        var _fields = [];

        var _iterable = facet.template.fieldsAttributes();
        if (! facet.template.filteredAttributeFieldsAll()){
          _iterable = facet.template.fields();
        }

        $.each(_iterable, function (index, field) {
          if (facet.template.fieldsAttributesFilter() == "" || field.name().toLowerCase().indexOf(facet.template.fieldsAttributesFilter().toLowerCase()) > -1){
            _fields.push(field);
          }
        });

        return _fields;
      });

      facet.fields = facet.template.fieldsAttributes;

      facet.template.fields = ko.computed(function () {  // Dup of template.fields
        var _fields = [];
        $.each(facet.template.fieldsAttributes(), function (index, field) {
          var position = facet.template.fieldsSelected.indexOf(field.name());
          if (position != -1) {
            _fields[position] = field;
          }
        });
        return _fields;
      });

      facet.template.fieldsSelected.subscribe(function(newValue) { // Could be more efficient as we don't need to research, just redraw
        vm.getFacetFromQuery(facet.id()).resultHash('');
        vm.search();
      });

      facet.template.chartSettings.chartType.subscribe(function(newValue) {
        facet.widgetType(
            newValue == ko.HUE_CHARTS.TYPES.PIECHART ? 'pie2-widget' :
            (newValue == ko.HUE_CHARTS.TYPES.TIMELINECHART ? 'timeline-widget' :
            (newValue == ko.HUE_CHARTS.TYPES.GRADIENTMAP ? 'gradient-map-widget' : 'bucket-widget'))
        );
      });

      // TODO Reload QueryResult
      facet.queryResult = ko.observable(new QueryResult(self, {
        type: self.engine(),
      }));
    }
  }

  self.facets = ko.mapping.fromJS(collection.facets);
  $.each(self.facets(), function (index, facet) {
    self._addObservablesToFacet(facet, vm);

    if (facet.properties.aggregate && facet.properties.aggregate.function) {
      facet.properties.aggregate.function.subscribe(function () {
        vm.search();
      });
    }

    if (typeof facet.properties.facets != 'undefined') {
      $.each(facet.properties.facets(), function (index, pivotFacet) {
        if (pivotFacet.aggregate && pivotFacet.aggregate.function) {
          pivotFacet.aggregate.function.subscribe(function () {
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


  self.template.showFieldList.subscribe(function() {
    $(window).trigger('resize');
  });

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
    hueAnalytics.log('dashboard', 'add_facet/' + facet_json.widgetType);

    $.post("/dashboard/template/new_facet", {
        "collection": ko.mapping.toJSON(self),
        "id": facet_json.widget_id,
        "label": facet_json.name,
        "field": facet_json.name,
        "widget_type": facet_json.widgetType
      }, function (data) {
        if (data.status == 0) {
          var facet = ko.mapping.fromJS(data.facet);

          self._addObservablesToFacet(facet, vm);

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
    }
  }

  self.addPivotFacetValue2 = function(facet) {
    var pivot = null;

    pivot = ko.mapping.fromJS({
      'field': ko.mapping.toJS(facet.properties.facets_form.field),
      'limit': ko.mapping.toJS(facet.properties.facets_form.limit),
      'mincount': ko.mapping.toJS(facet.properties.facets_form.mincount),
      'aggregate': ko.mapping.toJS(facet.properties.facets_form.aggregate),
    });

    facet.properties.facets_form.field(null);
    facet.properties.facets_form.limit(5);
    facet.properties.facets_form.mincount(1);

    facet.properties.facets_form.aggregate.function('count');
    facet.properties.facets_form.aggregate.ops.removeAll();
    facet.properties.facets_form.aggregate.percentiles.removeAll();
    facet.properties.facets_form.aggregate.percentiles.push({'value': 50});

    if (pivot != null) {
      pivot.aggregate.function.subscribe(function() {
        vm.search();
      });
      facet.properties.facets.push(pivot);
    }
  }

  self.removePivotFacetValue = function(facet) {
    facet['pivot_facet'].properties.facets.remove(facet['value']);
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

  self.getTemplateField = function (name, fields) {
    var _field = null;
    $.each(fields, function (index, field) {
      if (field && field.name() == name) {
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
    else if (self.template.fieldsModalType() == 'tree-widget' || self.template.fieldsModalType() == 'tree2-widget' || self.template.fieldsModalType() == 'heatmap-widget') {
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
    if (! filter) {
      return self.template.availableWidgetFields();
    } else {
      return ko.utils.arrayFilter(self.template.availableWidgetFields(), function (field) {
        return field.name().toLowerCase().indexOf(filter.toLowerCase()) > -1;
      });
    }
  });

  self.switchCollection = function() {
    $.post("/dashboard/get_collection", {
        name: self.name(),
        engine: self.engine()
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
    $.post("/dashboard/get_collection", {
        name: self.name(),
        engine: self.engine()
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
    $.post("/dashboard/index/fields/dynamic", {
        name: self.name(),
        engine: self.engine()
      }, function (data) {
        if (data.status == 0) {
          syncArray(self.template.fieldsAttributes, data.gridlayout_header_fields, true);
          syncArray(self.fields, data.fields, true);
        }
    }).fail(function (xhr, textStatus, errorThrown) {});

    if (self.supportNesting()) {
      self.getNestedDocuments();
    }
  };

  self.getNestedDocuments = function () {
    $.post("/dashboard/index/fields/nested_documents", {
        collection: ko.mapping.toJSON(self),
        engine: self.engine()
      }, function (data) {
        self.nested.enabled(data.status == 0 && data.has_nested_documents);
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

  self.toggleSortFacet2 = function (facet_field, event) {
    if (facet_field.properties.sort() == 'desc') {
      facet_field.properties.sort('asc');
    } else {
      facet_field.properties.sort('desc');
    }

    if (facet_field.properties.type && facet_field.properties.type() == 'range-up') {
      vm.query.removeFilter(ko.mapping.fromJS({'id': facet_field.id})); // Reset filter query
    }

    vm.search();
  };

  self.toggleRangeFacet = function (facet_field, event) { // Deprecated after Hue 4
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

  self.toggleRangeFacet2 = function (facet_field, event) {
    vm.query.removeFilter(ko.mapping.fromJS({'id': facet_field.id})); // Reset filter query

    if (facet_field.properties.type() == 'field') {
       facet_field.properties.type('range');
     } else if (facet_field.properties.type() == 'range') {
       facet_field.properties.type('range-up')
     } else if (facet_field.properties.type() == 'range-up') {
       facet_field.properties.type('field')
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
      url: "/dashboard/get_range_facet",
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

  self.translateSelectedField = function (index, direction, template) {
    var array = template.fieldsSelected();
    if (self.template == template) {
      vm.resultsHash = '';
    }

    if (direction == 'left') {
      template.fieldsSelected.splice(index - 1, 2, array[index], array[index - 1]);
    } else {
      template.fieldsSelected.splice(index, 2, array[index + 1], array[index]);
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
  self.engines = ko.mapping.fromJS(initial.engines);
  self.layout = initial.layout;
  self.inited = ko.observable(self.collections().length > 0); // No collection if not a new dashboard

  self.init = function() {
    if (self.inited()) {
      // If new dashboard
      vm.collection.name.subscribe(function(newValue) {
        if (newValue && (vm.collection.engine() == 'solr' || /^[^\.]+\.[^\.]+$/.test(newValue))) {
          vm.collection.label(newValue);
          vm.collection.switchCollection();
          vm.search();
        }
      });
    } else {
      self.syncCollections();
    }

    if (initial.autoLoad) {
      magicSearchLayout(vm);
    }
  };

  self.syncCollections = function () {
    vm.isSyncingCollections(true);
    $.post("/dashboard/get_collections", {
        collection: ko.mapping.toJSON(vm.collection),
        show_all: false
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

  self.getEngine = function(type) {
     var _engine = null;
     $.each(self.engines(), function (index, engine) {
      if (engine.type() == type) {
        _engine = engine;
        return false;
      }
    });
    return _engine;
  };
};


var QueryResult = function (vm, initial) { // Similar to to Notebook Snippet
  var self = this;

  self.id = ko.observable(UUID());
  self.type = ko.mapping.fromJS(initial.type);
  self.status = ko.observable(initial.status || 'running');
  self.progress = ko.mapping.fromJS(initial.progress || 0);

  self.hasResultset = ko.observable(true);

  // UI
  self.saveResultsModalVisible = ko.observable(false);

  self.result = ko.mapping.fromJS(initial.result);
  self.result.hasSomeResults = ko.computed(function () {
    return self.hasResultset(); // && self.data().length > 0; // status() == 'available'
  });
  self.result.type = ko.observable('table');

  self.getContext = function() {
    return self;
  }

  self.asyncResult = function() {
    return ko.mapping.toJS(self.result.result);
  }
};


var DATE_TYPES = ['date', 'tdate', 'timestamp'];
var NUMBER_TYPES = ['int', 'tint', 'long', 'tlong', 'float', 'tfloat', 'double', 'tdouble', 'currency'];
var FLOAT_TYPES = ['float', 'tfloat', 'double', 'tdouble'];
var GEO_TYPES = ['SpatialRecursivePrefixTreeFieldType'];

var RANGE_SELECTABLE_WIDGETS = ['histogram-widget', 'bar-widget', 'line-widget'];


var SearchViewModel = function (collection_json, query_json, initial_json) {
  var self = this;

  self.collectionJson = collection_json;
  self.queryJson = query_json;
  self.initialJson = initial_json;

  self.build = function () {
    self.intervalOptions = ko.observableArray(ko.bindingHandlers.daterangepicker.INTERVAL_OPTIONS);
    self.isNested = ko.observable(false);

    // Models
    self.initial = new NewTemplate(self, self.initialJson);
    self.collection = new Collection(self, self.collectionJson.collection);
    self.isSaved = ko.computed(function() {
      return !!self.collection.id();
    });
    self.query = new Query(self, self.queryJson);

    // UI
    self.selectedQDefinition = ko.observable();
    self.response = ko.observable({});
    self.results = ko.observableArray([]);
    self.resultsHash = '';
    self.norm_facets = {};
    self.getFacetFromQuery = function (facet_id) {
      if (!(facet_id in self.norm_facets)) {
        self.norm_facets[facet_id] = ko.mapping.fromJS({
          id: facet_id,
          has_data: false,
          resultHash: '',
          counts: [],
          label: '',
          field: '',
          dimension: 1,
          extraSeries: [],
          // Hue 4
          hasRetrievedResults: true, // Temp
          results: [],
          response: '',
          fieldAnalysesName: ''
        });
      }

      return self.norm_facets[facet_id];
    };
    self.toggledGridlayoutResultChevron = ko.observable(false);
    self.enableGridlayoutResultChevron = function () {
      self.toggledGridlayoutResultChevron(true);
    };
    self.disableGridlayoutResultChevron = function () {
      self.toggledGridlayoutResultChevron(false);
    };
    self.fieldAnalyses = ko.observableArray([]);
    self.fieldAnalysesName = ko.observable("");
    self.fieldsAnalysisAttributesNames = ko.computed(function () {
      var _fields = [];
      $.each(self.collection.template.fieldsAttributes(), function (index, field) {
        if (field.name() != self.fieldAnalysesName()) {
          _fields.push(field.name())
        }
      });
      return _fields;
    });

    self.previewColumns = ko.observable("");
    self.columns = ko.observableArray([]);
    self.columnsTotalSize = ko.pureComputed(function () {
      var totalSize = 0;
      self.columns().forEach(function (col) {
        totalSize += col.size();
      });
      return totalSize;
    });
    loadSearchLayout(self, self.collectionJson.layout);

    self.additionalMustache = null;

    self.isEditing = ko.observable(false);
    self.toggleEditing = function () {
      self.isEditing(!self.isEditing());
    };
    self.isRetrievingResults = ko.observable(false);
    self.hasRetrievedResults = ko.observable(true);
    self.asyncSearchesCounter = ko.observableArray([]);
    self.asyncSearchesCounter.subscribe(function (newVal) {
      if (newVal.length == 0) {
        self.isRetrievingResults(false);
        self.hasRetrievedResults(true);
        $('.btn-loading').button('reset');

        huePubSub.publish('check.autorefresh');
      }
    });

    self.isSyncingCollections = ko.observable(false);

    self.isPlayerMode = ko.observable(false);

    function bareWidgetBuilder(name, type) {
      return new Widget({
        size: 12,
        id: UUID(),
        name: name,
        widgetType: type
      });
    }

    self.draggableHit = ko.observable(bareWidgetBuilder("Hit Count", "hit-widget")); // Not used
    self.draggableFacet = ko.observable(bareWidgetBuilder("Facet", "facet-widget")); // Deprecated
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
    self.draggableTree = ko.observable(bareWidgetBuilder("Tree", "tree-widget")); // Deprecated
    self.draggableHeatmap = ko.observable(bareWidgetBuilder("Heatmap", "heatmap-widget"));
    self.draggableCounter = ko.observable(bareWidgetBuilder("Counter", "hit-widget"));
    self.draggableBucket = ko.observable(bareWidgetBuilder("Chart", "bucket-widget"));
    self.draggableTimeline = ko.observable(bareWidgetBuilder("Timeline", "timeline-widget"));
    self.draggableGradienMap = ko.observable(bareWidgetBuilder("Gradient Map", "gradient-map-widget"));
    self.draggableTree2 = ko.observable(bareWidgetBuilder("Tree", "tree2-widget"));
    self.draggableTextFacet = ko.observable(bareWidgetBuilder("Text Facet", "text-facet-widget"));


    self.availableDateFields = ko.computed(function () {
      return $.grep(self.collection.availableFacetFields(), function (field) {
        return DATE_TYPES.indexOf(field.type()) != -1 && field.name() != '_version_';
      });
    });
    self.availableNumberFields = ko.computed(function () {
      return $.grep(self.collection.availableFacetFields(), function (field) {
        return NUMBER_TYPES.indexOf(field.type()) != -1;
      });
    });
    self.availablePivotFields = ko.computed(function () {
      return self.collection.fields();
    });
    self.availableStringFields = ko.computed(function () {
      return $.grep(self.collection.availableFacetFields(), function (field) {
        return NUMBER_TYPES.indexOf(field.type()) == -1 && DATE_TYPES.indexOf(field.type()) == -1;
      });
    });

    function getWidgets(equalsTo) {
      return $.map(self.columns(), function (col) {
        return $.map(col.rows(), function (row) {
          return $.grep(row.widgets(), function (widget) {
            return equalsTo(widget);
          });
        });
      })
    };

    self.availableDraggableResultset = ko.computed(function () {
      return getWidgets(function (widget) {
          return ['resultset-widget', 'html-resultset-widget'].indexOf(widget.widgetType()) != -1;
        }).length == 0;
    });
    self.availableDraggableLeaflet = ko.computed(function () {
      return getWidgets(function (widget) {
          return ['leafletmap-widget'].indexOf(widget.widgetType()) != -1;
        }).length == 0;
    });
    self.availableDraggableFilter = ko.computed(function () {
      return getWidgets(function (widget) {
          return widget.widgetType() == 'filter-widget';
        }).length == 0;
    });
    self.availableDraggableHistogram = ko.computed(function () {
      return self.availableDateFields().length > 0;
    });
    self.availableTimeline = ko.computed(function () {
      return self.availableDateFields().length > 0;
    });
    self.availableDraggableNumbers = ko.computed(function () {
      return self.availableNumberFields().length > 0;
    });
    self.availableDraggableChart = ko.computed(function () {
      return self.collection.availableFacetFields().length > 0;
    });
    self.availableDraggableMap = ko.computed(function () {
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

    self.checkStatus = function (facet) { // TODO: have a common generic with Notebook
      $.post("/notebook/api/check_status", {
        notebook: ko.mapping.toJSON({type: facet.queryResult().type()}),
        snippet: ko.mapping.toJSON(facet.queryResult().getContext())
      }, function (data) {
        if (!self.collection.async()) {
          self.fetchResult(facet);
        }
        else if (facet.queryResult().status() == 'canceled') {
          // Query was canceled in the meantime, do nothing
        } else {

          if (data.status == 0) {
            facet.queryResult().status(data.query_status.status);

            if (facet.queryResult().status() == 'running' || facet.queryResult().status() == 'starting') {
              // if (! notebook.unloaded()) { self.checkStatusTimeout = setTimeout(self.checkStatus, 1000); };
              setTimeout(function () {
                self.checkStatus(facet);
              }, 1000);
            }
            else if (facet.queryResult().status() == 'available') {
              self.fetchResult(facet);
              facet.queryResult().progress(100);
            }
            else if (facet.queryResult().status() == 'success') {
              facet.queryResult().progress(99);
            }
          } else if (data.status == -3) {
            facet.queryResult().status('expired');
          } else {
            //self._ajaxError(data); // common?
            $(document).trigger("error", data.message);
          }
        }
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText || textStatus);
        facet.queryResult().status('failed');
      });
    };

    self.isCanceling = ko.observable(false);

    self.cancelAsync = function (facet) { // TODO: have a common generic with Notebook
      self.isCanceling(true);
      hueAnalytics.log('dashboard', 'cancel');

      multiQs = $.map(self.asyncSearchesCounter(), function (facet) {
        $.post("/notebook/api/cancel_statement", {
          notebook: ko.mapping.toJSON({type: facet.queryResult().type()}),
          snippet: ko.mapping.toJSON(facet.queryResult().getContext())
        }, function (data) {
          if (data.status == 0) {
            facet.queryResult().status('canceled');
            self.asyncSearchesCounter.remove(facet);
          } else {
            //self._ajaxError(data);
          }
        }).fail(function (xhr, textStatus, errorThrown) {
          $(document).trigger("error", xhr.responseText);
          self.queryResult().status('failed');
        }).always(function () {
          // self.isCanceling(false);
        });
      });
    };

    self.close = function (facet) {
      $.post("/notebook/api/close_statement", {
        notebook: ko.mapping.toJSON({type: facet.queryResult().type()}),
        snippet: ko.mapping.toJSON(facet.queryResult().getContext())
      }, function (data) {
        if (data.status == 0) {
          // self.status('closed'); // Keep as 'running' as currently it happens before running a new query
        } else {
          //self._ajaxError(data);
        }
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
        facet.queryResult().status('failed');
      });
    };

    self._loadResults = function (facet, data) {
      if (facet.type) {
        $.each(data.normalized_facets, function (index, facet) {
          self._make_result_facet(facet);
        });
      } else {
        self._make_grid_result(data);
      }
    }

    self.fetchResult = function (facet) {
      if (!self.collection.async()) {
        self._loadResults(facet, facet.queryResult().asyncResult());
      } else {
        $.post("/dashboard/search", {
          collection: ko.mapping.toJSON(self.collection),
          query: ko.mapping.toJSON(self.query),
          facet: ko.mapping.toJSON(facet),
          fetch_result: true
        }, function (data) {
          self._loadResults(facet, data);
          self.asyncSearchesCounter.remove(facet);

          //if (facet.queryResult().result['handle'].has_result_set()) {
          //  self.fetchResultSize(facet);
          //}
        });
      }
    };

    self.fetchResultSize = function (facet) {
      $.post("/notebook/api/fetch_result_size", {
        notebook: ko.mapping.toJSON({type: facet.queryResult().type()}),
        snippet: ko.mapping.toJSON(facet.queryResult)
      }, function (data) {
        if (data.status == 0) {
          if (data.result.rows != null) {
            facet.response().response.numFound(data.result.rows);
          }
        } else if (data.status == 5) {
          // No supported yet for this snippet
        } else {
          $(document).trigger("error", data.message);
        }
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
      });
    };


    self.search = function (callback) {
      $(".jHueNotify").remove();
      hueAnalytics.log('dashboard', 'search');
      self.isRetrievingResults(true);

      if (! self.collection.name()) {
        return;
      }

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
          return $.post("/dashboard/get_timeline", {
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

      if (self.collection.engine() != 'solr') {
        $.each([self.collection].concat(self.collection.facets()), function (index, facet) {
          if (facet.queryResult().result.handle) {
            self.close(facet);
          }
        });

        multiQs = $.map(self.collection.facets(), function (facet) {
          return $.post("/dashboard/search", {
            collection: ko.mapping.toJSON(self.collection),
            query: ko.mapping.toJSON(self.query),
            facet: ko.mapping.toJSON(facet),
          }, function (data) {
            facet.queryResult(new QueryResult(self, {
              type: self.collection.engine(),
              result: data,
              status: 'running',
              progress: 0,
            }));

            self.checkStatus(facet);
          });
        });

        if (self.collection.async()) {
          self.asyncSearchesCounter([self.collection].concat(self.collection.facets()));
        }
      }

      $.each(self.fieldAnalyses(), function (index, analyse) { // Invalidate stats analysis
        analyse.stats.data.removeAll();
      });

      if (self.getFieldAnalysis()) {
        self.getFieldAnalysis().update();
      }


      $.when.apply($, [
          $.post("/dashboard/search", {
              collection: ko.mapping.toJSON(self.collection),
              query: ko.mapping.toJSON(self.query),
              layout: ko.mapping.toJSON(self.columns)
            }, function (data) {
              data = JSON.bigdataParse(data);
              try {
                if (self.collection.engine() == 'solr') {
                  self._make_grid_result(data, callback);
                } else {
                  self.collection.queryResult(new QueryResult(self, {
                    type: self.collection.engine(),
                    result: data,
                    status: 'running',
                    progress: 0,
                  }));
                  self.checkStatus(self.collection);
                }
              }
              catch (e) {
                console.log(e);
              }
            },
            "text")
        ].concat(multiQs)
      )
        .done(function () {
          if (arguments[0] instanceof Array) {
            if (self.collection.engine() == 'solr') { // If multi queries
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
              self.response.valueHasMutated();
            }
          }
        })
        .fail(function (xhr, textStatus, errorThrown) {
          $(document).trigger("error", xhr.responseText);
        })
        .always(function () {
          if (!self.collection.async()) {
            self.isRetrievingResults(false);
            self.hasRetrievedResults(true);
            $('.btn-loading').button('reset');
          }
        });
    };

    self._make_grid_result = function (data, callback) {
      if (typeof callback === "function") { // For Solr Auto refresh
        callback(data);
      }

      $.each(data.normalized_facets, function (index, new_facet) {
        self._make_result_facet(new_facet);
      });

      // Delete norm_facets that were deleted
      //data.response.numFound = ko.observable(data.response.numFound);
      self.response(data);

      if (data.error) {
        $(document).trigger("error", data.error);
      }
      else {
        var _resultsHash = ko.mapping.toJSON(data.response.docs);

        if (self.resultsHash != _resultsHash) {
          var _docs = [];
          var _mustacheTmpl = self.collection.template.isGridLayout() ? "" : fixTemplateDotsAndFunctionNames(self.collection.template.template());
          $.each(data.response.docs, function (index, item) {
            _docs.push(self._make_result_doc(item, _mustacheTmpl, self.collection.template));
          });
          self.results(_docs);
        }
        self.resultsHash = _resultsHash;
      }
    };

    self._make_result_facet = function (new_facet) {
      var facet = self.getFacetFromQuery(new_facet.id);
      var _hash = ko.mapping.toJSON(new_facet);

      if (!facet.has_data() || facet.resultHash() != _hash) {
        facet.counts(new_facet.counts);

        if (typeof new_facet.docs != 'undefined') {
          var _docs = [];

          // Update template
          var _facet_model = self.collection.getFacetById(new_facet.id);
          var _fields = []
          $.each(new_facet.fieldsAttributes, function (index, item) {
            _fields.push(ko.mapping.fromJS(item));
          });
          _facet_model.template.fieldsAttributes(_fields);

          $.each(new_facet.docs, function (index, item) {
            _docs.push(self._make_result_doc(item, "", _facet_model.template));
          });
          facet.results(_docs);
          facet.response(new_facet.response);
        }
        facet.label(new_facet.label);
        facet.field(new_facet.field);
        facet.dimension(new_facet.dimension);
        facet.extraSeries(typeof new_facet.extraSeries != 'undefined' ? new_facet.extraSeries : []);
        facet.resultHash(_hash);
        facet.has_data(true);
      }
    }

    self._make_result_doc = function (item, _mustacheTmpl, template) {
      var row = [];
      var leafletmap = {};
      var _externalLink = item.externalLink;
      var _details = item.details;
      var _id = item.hueId;
      var _childDocuments = item._childDocuments_;
      delete item["externalLink"];
      delete item["details"];
      delete item["hueId"];
      delete item["_childDocuments_"];
      var fields = template.fieldsSelected();
      // Display selected fields or whole json document
      if (fields.length != 0) {
        $.each(template.fieldsSelected(), function (index, field) {
          row.push(item[field]);
        });
      } else {
        row.push(ko.mapping.toJSON(item));
      }
      if (template.leafletmapOn()) {
        leafletmap = {
          'latitude': item[template.leafletmap.latitudeField()],
          'longitude': item[template.leafletmap.longitudeField()],
          'label': template.leafletmap.labelField() ? item[template.leafletmap.labelField()] : ""
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

      if (_childDocuments) {
        var childRecords = [];
        $.each(_childDocuments, function (index, item) {
          var record = self._make_result_doc(item, _mustacheTmpl, self.collection.template);
          $.each(item, function (key, val) {
            var _field = ko.mapping.fromJS({
              key: key,
              value: val,
              hasChanged: false
            });
            record.details.push(_field);
          });
          childRecords.push(record);
        });
        doc['childDocuments'] = ko.observable(childRecords);
      }
      if (!template.isGridLayout()) {
        // fix the fields that contain dots in the name
        addTemplateFunctions(item);
        if (self.additionalMustache != null && typeof self.additionalMustache == "function") {
          self.additionalMustache(item);
        }
        doc.content = Mustache.render(_mustacheTmpl, item);
      }
      return doc;
    }

    self.suggest = function (query, callback) {
      $.post("/dashboard/suggest/", {
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
            if (widget.id() == widget_id) {
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
            if (widget && widget.id() == widget_id) {
              row.widgets.remove(widget);
              row.autosizeWidgets();
              return false;
            }
          });
        });
      });
    }

    self.getDocument = function (doc, callback) {
      $.post("/dashboard/get_document", {
        collection: ko.mapping.toJSON(self.collection),
        id: doc.id
      }, function (data) {
        data = JSON.bigdataParse(data);
        var details = [];
        doc.details.removeAll();
        if (data.status == 0) {

          $.each(data.doc.doc, function (key, val) {
            var _field = ko.mapping.fromJS({
              key: key,
              value: val,
              hasChanged: false
            });
            _field.value.subscribe(function () {
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
      $.post("/dashboard/update_document", {
        collection: ko.mapping.toJSON(self.collection),
        document: ko.mapping.toJSON(doc),
        id: doc.id
      }, function (data) {
        data = JSON.bigdataParse(data);
        if (data.status == 0) {
          doc.showEdit(false);

          var versionField = $.grep(doc.details(), function (field) {
            return field.key() == '_version_';
          });
          if (versionField.length > 0) {
            versionField[0].value(data.update.adds[1]);
            versionField[0].hasChanged(false);
          }
          ;

          doc.originalDetails(ko.toJSON(doc.details()));
        }
        else {
          $(document).trigger("error", data.message);
        }
      }, "text").fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
      });
    };

    self.showFieldAnalysis = function (data, e) {
      if (self.fieldAnalysesName()) {
        var analyse = self.getFieldAnalysis();

        if (analyse == null) {
          analyse = new FieldAnalysis(self, self.fieldAnalysesName(), data.type());
          self.fieldAnalyses.push(analyse);
        }

        analyse.update();
        $(document).trigger("shownAnalysis", e);
      }
    }

    self.getFieldAnalysis = function () {
      var fieldName = self.fieldAnalysesName();
      var _analyse = null;

      $.each(self.fieldAnalyses(), function (index, analyse) {
        if (analyse.name() == fieldName) {
          _analyse = analyse;
          return false;
        }
      });

      return _analyse;
    };

    self.save = function () {
      $.post("/dashboard/save", {
        collection: ko.mapping.toJSON(self.collection),
        layout: ko.mapping.toJSON(self.columns)
      }, function (data) {
        if (data.status == 0) {
          self.collection.id(data.id);
          $(document).trigger("info", data.message);
          if (window.location.search.indexOf("collection") == -1) {
            hueUtils.changeURL((IS_HUE_4 ? '/hue' : '') + '/dashboard/?collection=' + data.id);
          }
          huePubSub.publish('assist.document.refresh');
        }
        else {
          $(document).trigger("error", data.message);
        }
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
      });
    };
  };

  self.reset = function() {
    self.intervalOptions(ko.bindingHandlers.daterangepicker.INTERVAL_OPTIONS);
    self.isNested(false);

    // Models
    ko.mapping.fromJS(self.initialJson.collections, self.initial.collections)
    ko.mapping.fromJS(self.initialJson.engines, self.initial.engines);
    self.initial.layout = self.initialJson.layout;
    self.initial.inited(self.initial.collections().length > 0);

    var c = self.collectionJson.collection;
    ko.mapping.fromJS(c.id, self.collection.id);
    self.collection.uuid(typeof c.uuid != "undefined" && c.uuid != null ? c.uuid : UUID());
    ko.mapping.fromJS(c.name, self.collection.name);
    ko.mapping.fromJS(c.label, self.collection.label);
    self.collection.description(typeof c.description != "undefined" && c.description != null ? c.description : '');
    ko.mapping.fromJS(c.suggest, self.collection.suggest);
    self.collection.engine(typeof c.engine != "undefined" && c.engine != null ? c.engine : 'solr');
    self.collection.queryResult(new QueryResult(self.collection, {
      type: self.collection.engine(),
    }));
    ko.mapping.fromJS(c.nested, self.collection.nested);
    ko.mapping.fromJS(c.enabled, self.collection.enabled);
    ko.mapping.fromJS(c.autorefresh, self.collection.autorefresh);
    ko.mapping.fromJS(c.autorefreshSeconds || 60, self.collection.autorefreshSeconds);
    self.collection.idField(c.idField);
    ko.mapping.fromJS(c.timeFilter, self.collection.timeFilter);

    c.template.chartSettings = $.extend({
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
    }, c.template.chartSettings);

    ko.mapping.fromJS(c.template, self.collection.template);

    for (var setting in self.collection.template.chartSettings) {
      self.collection.template.chartSettings[setting].subscribe(function () {
        huePubSub.publish('gridChartForceUpdate');
      });
    }

    self.collection.template.extracode($("<span>").html(self.collection.template.extracode()).text()); // Unescape HTML
    if (self.collection.template.leafletmap.latitudeField == undefined) {
      self.collection.template.leafletmap.latitudeField = ko.observable();
    }
    if (self.collection.template.leafletmap.longitudeField == undefined) {
      self.collection.template.leafletmap.longitudeField = ko.observable();
    }
    if (self.collection.template.leafletmap.labelField == undefined) {
      self.collection.template.leafletmap.labelField = ko.observable();
    }

    self.collection.template.selectedVisualField(null);
    self.collection.template.selectedVisualFunction(null);
    self.collection.template.selectedSourceField(null);
    self.collection.template.selectedSourceFunction(null);


    if (c.facets.length > 0) {
      c.facets.forEach(function (f) {
        if (f.properties.facets_form && typeof f.properties.facets_form.field === 'undefined') {
          f.properties.facets_form.field = null;
        }
      });
    }

    ko.mapping.fromJS(c.facets, self.collection.facets);
    $.each(self.collection.facets(), function (index, facet) {
      self.collection._addObservablesToFacet(facet, vm);

      if (facet.properties.aggregate && facet.properties.aggregate.function) {
        facet.properties.aggregate.function.subscribe(function () {
          vm.search();
        });
      }
      if (typeof facet.properties.facets != 'undefined') {
        $.each(facet.properties.facets(), function (index, pivotFacet) {
          if (pivotFacet.aggregate && pivotFacet.aggregate.function) {
            pivotFacet.aggregate.function.subscribe(function () {
              vm.search();
            });
          }
        });
      }
    });

    ko.mapping.fromJS(c.fields, self.collection.fields);
    ko.mapping.fromJS(c.qdefinitions, self.collection.qdefinitions);

    self.collection.selectedDocument({});
    self.collection.newQDefinitionName("");
    self.collection.template.fieldsModalFilter(""); // For UI
    self.collection.template.fieldsModalType(""); // For UI
    self.collection.template.fieldsAttributesFilter(""); // For UI
    self.collection.template.filteredAttributeFieldsAll(true);

    var q = self.queryJson;
    self.query.uuid(typeof q.uuid != "undefined" && q.uuid != null ? q.uuid : UUID());
    ko.mapping.fromJS(q.qs, self.query.qs);
    ko.mapping.fromJS(q.fqs, self.query.fqs);
    ko.mapping.fromJS(q.start, self.query.start);
    self.query.selectedMultiq('query');



    // UI
    self.selectedQDefinition(null);
    self.response({});
    self.results([]);
    self.resultsHash = '';
    self.norm_facets = {};
    self.toggledGridlayoutResultChevron(false);
    self.fieldAnalyses([]);
    self.fieldAnalysesName("");
    self.previewColumns("");
    self.columns([]);
    loadSearchLayout(self, self.collectionJson.layout);
    self.isEditing(true);
    self.isRetrievingResults(false);
    self.hasRetrievedResults(true);
    self.asyncSearchesCounter([]);
    self.isSyncingCollections(false);
    self.isPlayerMode(false);

    if (window.location.search.indexOf("collection") > -1) {
      hueUtils.changeURL((IS_HUE_4 ? '/hue' : '') + '/dashboard/new_search');
    }
  }

  self.build();
};


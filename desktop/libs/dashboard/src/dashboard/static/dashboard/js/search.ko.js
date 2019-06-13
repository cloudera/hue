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
  huePubSub.publish('dashboard.set.layout');
}

function queryBuilderSearchLayout(vm, isQueryBuilder) {
  vm.isQueryBuilder(!!isQueryBuilder);
  loadSearchLayout(vm, vm.initial.qbLayout);
  $(document).trigger("magicSearchLayout");
  huePubSub.publish('dashboard.set.layout');
}

function textSearchLayout(vm, isQueryBuilder) {
  vm.isQueryBuilder(!!isQueryBuilder);
  loadSearchLayout(vm, vm.initial.textSearchLayout);
  vm.collection.template.isGridLayout(false);
  $(document).trigger("magicSearchLayout");
  huePubSub.publish('dashboard.set.layout');
}

function loadSearchLayout(viewModel, json_layout) {
  var _columns = [];

  $(json_layout).each(function (cnt, json_col) {
    var _rows = [];
    $(json_col.rows).each(function (rcnt, json_row) {
      var row = new Row([], viewModel);
      $(json_row.widgets).each(function (wcnt, widget) {
        row.addWidget(new Widget({
          size: widget.size,
          id: widget.id,
          name: widget.name,
          widgetType: widget.widgetType,
          properties: widget.properties,
          offset: widget.offset,
          loading: true,
          gridsterHeight: viewModel.draggableWidgets[widget.widgetType].gridsterHeight() || 6,
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

function loadDashboardLayout(vm, gridster_layout) {
  $.each(gridster_layout, function(index, item) {
    vm.gridItems.push(ko.mapping.fromJS({
      col: parseInt(item.col),
      row: parseInt(item.row),
      size_x: parseInt(item.size_x),
      size_y: parseInt(item.size_y),
      widget: item.widget ? vm.getWidgetById(item.widget.id) : null,
      emptyProperties: new EmptyGridsterWidget(vm),
    }));
  });
}

// End dashboard lib

function layoutToGridster(vm) {
  var emptyWidgetHeight = 4;
  var layout = [];
  var startingCol = 1;

  $.each(vm.columns(), function (indexY, column) {
    var startingRow = 1;
    $.each(column.rows(), function (indexX, row) {
      $.each(row.widgets(), function (indexW, widget) {
        var targetHeight = vm.draggableWidgets[widget.widgetType()].gridsterHeight() || 6;
        layout.push(ko.mapping.fromJS({
          col: parseInt(startingCol),
          row: parseInt(startingRow),
          size_x: parseInt(column.size()),
          size_y: parseInt(targetHeight),
          widget: vm.getWidgetById(widget.id())
        }));
        startingRow += targetHeight;
      });
      if (row.widgets().length === 0) {
        layout.push(ko.mapping.fromJS({
          col: parseInt(startingCol),
          row: parseInt(startingRow),
          size_x: parseInt(column.size()),
          size_y: parseInt(emptyWidgetHeight),
          widget: null,
          emptyProperties: new EmptyGridsterWidget(vm),
        }));
        startingRow += emptyWidgetHeight;
      }
    });
    startingCol += column.size();
  });

  return layout;
}

var EmptyGridsterWidget = function (vm) {
  var self = this;

  self.isAdding = ko.observable(true);
  self.fieldName = ko.observable();
  self.fieldViz = ko.observable(window.HUE_CHARTS.TYPES.BARCHART);
  self.fieldSort = ko.observable('desc');
  self.fieldOperation = ko.observable();
  self.fieldOperations = ko.pureComputed(function () {
    return HIT_OPTIONS;
  });

  self.availableSorts = ['desc', 'asc', 'default'];
  self.loopThroughSorts = function () {
    self.availableSorts.push(self.availableSorts.shift());
    self.fieldSort(self.availableSorts[0]);
  }
};

var Query = function (vm, query) {
  var self = this;

  self.uuid = ko.observable(typeof query.uuid != "undefined" && query.uuid != null ? query.uuid : hueUtils.UUID());
  self.qs = ko.mapping.fromJS(query.qs);
  self.qs.subscribe(function(){
    if (vm.selectedQDefinition() != null){
      vm.selectedQDefinition().hasChanged(true);
    }
  });
  self.fqs = ko.mapping.fromJS(query.fqs);
  self.start = ko.mapping.fromJS(query.start);
  self.timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

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

  self.toggleFacetClear = function (data) {
    var fqs = self.fqs();
    for (var i = fqs.length - 1; i >= 0; i--) { // Backward iteration to delete
      fq = fqs[i];
      if (fq.id() == data.widget_id) {
        self.fqs.remove(fq);
      }
    }
    self.start(0);
    vm.search();
  };

  self.toggleFacet = function (data, bSingle) {
    var fq = self.getFacetFilter(data.widget_id);

    if (!fq) {
      self.fqs.push(ko.mapping.fromJS({
        'id': data.widget_id,
        'field': data.facet.cat,
        'filter': [{'exclude': data.exclude ? true : false, 'value': data.facet.value}],
        'type': 'field'
      }));
    } else {
      var fqs = self.fqs();
      var fFilter = function(f) { return ko.toJSON(f.value()) == ko.toJSON(data.facet.value); };
      for (var i = fqs.length - 1; i >= 0; i--) { // Backward iteration to delete
        fq = fqs[i];
        if (fq.id() == data.widget_id) {
          var f = $.grep(fq.filter(), fFilter);
          if (f.length && !bSingle) {
            fq.filter.remove(f[0]);
            if (!fq.filter().length) {
              self.fqs.remove(fq);
            }
          } else {
            if (bSingle) {
              fq.filter.removeAll();
            }
            fq.filter.push(ko.mapping.fromJS({'exclude': data.exclude ? true : false, 'value': data.facet.value}));
          }
        }
      }
    }

    if (vm.selectedQDefinition()) {
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
      id = hueUtils.UUID();
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
  self.uuid = ko.observable(typeof collection.uuid != "undefined" && collection.uuid != null ? collection.uuid : hueUtils.UUID());
  self.name = ko.mapping.fromJS(collection.name);
  self.label = ko.mapping.fromJS(collection.label);
  self.description = ko.observable(typeof collection.description != "undefined" && collection.description != null ? collection.description : "");
  self.suggest = ko.mapping.fromJS(collection.suggest);
  self.activeNamespace = ko.observable();
  self.activeCompute = ko.observable();

  contextCatalog.getNamespaces({ sourceType: collection.engine || 'solr' }).done(function (context) {
    // TODO: Namespace selection
    self.activeNamespace(context.namespaces[0]);
    self.activeCompute(context.namespaces[0].computes[0]);
  });

  self.engine = ko.observable(typeof collection.engine != "undefined" && collection.engine != null ? collection.engine : "solr");
  self.engine.subscribe(function() {
    self.name(null);
  });
  self.source = ko.observable(typeof collection.source != "undefined" && collection.source != null ? collection.source : "data");
  self.async = ko.computed(function() {
    return ['impala', 'hive', 'report'].indexOf(self.engine()) != -1;
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

  collection.template.chartSettings = $.extend(collection.template.chartSettings, collection.template.chartSettings.chartType == 'lines' && { // Retire line chart
    chartType: 'bars',
    chartSelectorType: 'line'
  });
  collection.template.chartSettings = $.extend({
    chartType: 'bars',
    chartSelectorType: 'bar',
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

  self.template.chartSettings.hideStacked = ko.computed(function () {
    return self.template.chartSettings.chartYMulti().length <= 1;
  });

  for (var setting in self.template.chartSettings) {
    self.template.chartSettings[setting].subscribe(function () {
      huePubSub.publish('gridChartForceUpdate');
    });
  }

  self.template.fields = ko.pureComputed(function () {
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

  self.template.facetFieldsNames = ko.pureComputed(function () {
    return self.template.fieldsAttributes();
  });

 self.template.fieldsSelected.subscribe(function () {
    vm.search();
    if (self.template.moreLikeThis) {
      self.template.moreLikeThis(false);
    }
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
      if (f.properties.facets_form) {
        if (typeof f.properties.facets_form.field === 'undefined') {
          f.properties.facets_form.field = null;
        }
        f.properties.facets_form.isEditing = ko.observable(true);
      }
    });
  }

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

  self._get_field_operations = function(field, facet) {
    if (! field) {
      return HIT_OPTIONS;
    } else {
      return facet.widgetType() == 'hit-widget' ? (
         isNumericColumn(field.type()) ? NUMERIC_HIT_OPTIONS : ALPHA_HIT_COUNTER_OPTIONS
      ) : HIT_OPTIONS;
    }
  };

  // Very top facet
  self._addObservablesToFacet = function (facet, vm) {
    if (facet.properties && facet.properties.facets_form && facet.properties.facets_form.aggregate) { // Only Solr 5+
      facet.properties.facets_form.aggregate.metrics = ko.computed(function () {
        var _field = self.getTemplateField(facet.properties.facets_form.field(), self.template.fieldsAttributes());
        return self._get_field_operations(_field, facet);
      });

      // Here we could weight the fields
      facet.properties.facets_form.aggregate.facetFieldsNames = ko.computed(function () {
        return self._getCompatibleMetricFields(facet.properties.facets_form);
      }).extend({trackArrayChanges: true});

      facet.properties.facets_form.isEditing = ko.observable(true);

      if (facet.properties.facets) {
        facet.properties.facets.subscribe(function (newValue) {
          vm.search();
        });
      }
    } else {
      facet.properties.limit.subscribe(function () {
        vm.search();
      });
      if (facet.properties.gap) {
        facet.properties.gap.subscribe(function () {
          vm.search();
        });
      }
      if (facet.properties.aggregate && facet.properties.aggregate.function) {
        facet.properties.aggregate.function.subscribe(function () {
          vm.search();
        });
      }
    }

    if (facet.properties.compare) {
      facet.properties.compare.is_enabled.subscribe(function () {
        vm.search();
      });
      facet.properties.compare.use_percentage.subscribe(function () {
        vm.search();
      });
      facet.properties.compare.gap.subscribe(function () {
        vm.search();
      });
    }

    // For Solr 5+  only
    if (typeof facet.template != 'undefined') {
      facet.template.filteredAttributeFields = ko.computed(function () { // Dup of template.filteredAttributeFields
        var _fields = [];

        var _iterable = facet.template.fieldsAttributes();
        if (!facet.template.filteredAttributeFieldsAll()) {
          _iterable = facet.template.fields();
        }

        $.each(_iterable, function (index, field) {
          if (facet.template.fieldsAttributesFilter() == "" || field.name().toLowerCase().indexOf(facet.template.fieldsAttributesFilter().toLowerCase()) > -1) {
            _fields.push(field);
          }
        });

        return _fields;
      });

      facet.fields = facet.template.fieldsAttributes;

      facet.template.fields = ko.computed(function () { // Dup of template.fields
        var _fields = [];
        var fieldsSelected = facet.template.fieldsSelected();
        $.each(facet.template.fieldsAttributes(), function (index, field) {
          var position = facet.template.fieldsSelected.indexOf(field.name());
          if (!fieldsSelected.length || position != -1) {
            _fields.push(field);
          }
        });
        return _fields;
      });

      facet.template.getMeta = function (extraCheck) {
        return $.map(facet.template.fields(), function (field) {
          var fieldType = field.type().toLowerCase();
          if (fieldType.indexOf('_') > -1) {
            fieldType = fieldType.split('_')[0];
          }
          if (typeof field !== 'undefined' && field.name() != '' && extraCheck(fieldType)) {
            return field;
          }
        }).sort(function (a, b) {
          return a.name().toLowerCase().localeCompare(b.name().toLowerCase());
        });
      }

      facet.template.cleanedMeta = ko.computed(function () {
        return facet.template.getMeta(alwaysTrue);
      });

      facet.template.cleanedNumericMeta = ko.computed(function () {
        return facet.template.getMeta(isNumericColumn);
      });

      facet.template.cleanedStringMeta = ko.computed(function () {
        return facet.template.getMeta(isStringColumn);
      });

      facet.template.cleanedDateTimeMeta = ko.computed(function () {
        return facet.template.getMeta(isDateTimeColumn);
      });

      facet.template.fieldsSelected.subscribe(function (newValue) { // Could be more efficient as we don't need to research, just redraw
        if (newValue.length > 0) {
          vm.getFacetFromQuery(facet.id()).resultHash('');
          vm.search();
        }
      });
      facet.template.chartSettings.hideStacked = ko.computed(function () {
          return facet.template.chartSettings.chartYMulti().length <= 1;
      });

      /*facet.template.chartSettings.chartType.subscribe(function (newValue) {
      if (facet.widgetType() === 'document-widget') {
        var _fields = [];
        $.each(facet.fields(), function (index, field) {
          _fields.push(field.name());
        });
        facet.template.fieldsSelected(_fields);
      }
      });*/

      // TODO Reload QueryResult
      facet.queryResult = ko.observable(new QueryResult(self, {
        type: self.engine(),
      }));
    }

    facet.isEditing = ko.observable(false);
    facet.isAdding = ko.observable(false);

    if (facet.properties.facets) { // Sub facet
      $.each(facet.properties.facets(), function (index, nestedFacet) {
        self._addObservablesToNestedFacet(facet, nestedFacet, vm, index);
      });
    }

    function getFq() {
      var _fq, fqs = vm.query && vm.query.fqs();
      for (var i = 0; fqs && i < fqs.length; i++) {
        var fq = fqs[i];
        if (fq.id() == facet.id()) {
          _fq = fq;
          break;
        }
      }
      return _fq;
    }

    facet.canReset = ko.computed(function () {
      var _fq = getFq();

      function isNotInitial() {
        if (!facet.properties.canRange()) {
          return false;
        }
        if (facet.properties.facets) {
          return facet.properties.facets()[0].start() !== facet.properties.initial_start() || facet.properties.facets()[0].end() !== facet.properties.initial_end();
        } else {
          return facet.properties.start() !== facet.properties.initial_start() || facet.properties.end() !== facet.properties.initial_end();
        }
      }

      return _fq && _fq.filter().length || isNotInitial();
    });
    facet.canZoomIn = ko.computed(function () {
      var _fq = getFq();
      return facet.properties.canRange() && _fq && _fq.filter().length;
    });
  }

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

  self._addObservablesToNestedFacet = function (facet, nestedFacet, vm, index) {
    nestedFacet.limit.subscribe(function () {
      vm.search();
    });

    if (nestedFacet.gap) {
      nestedFacet.gap.subscribe(function () {
        vm.search();
      });
    }

    if (nestedFacet.aggregate) {
      if (nestedFacet.aggregate.function) {
        nestedFacet.aggregate.function.subscribe(function () {
          vm.search();
        });
      }

      nestedFacet.aggregate.metrics = ko.computed(function () {
        var _field = self.getTemplateField(nestedFacet.field(), self.template.fieldsAttributes());
        return self._get_field_operations(_field, facet);
      });

      nestedFacet.aggregate.facetFieldsNames = ko.computed(function () {
        if (index != 0) {
          return self._getCompatibleMetricFields(nestedFacet);
        }
        var template = self.template;
        if (facet.properties.canRange() && facet.properties.isDate()) {
          return template.cleanedDateTimeMeta();
        } else if (facet.properties.canRange()) {
          return template.cleanedNumericMeta();
        } else {
          return template.cleanedStringMeta();
        }
      }).extend({trackArrayChanges: true});
    }

    nestedFacet.isEditing = ko.observable(false);
  }

  self._getCompatibleMetricFields = function (nestedFacet) {
    var fields = null;

    if (['avg', 'sum', 'median', 'percentile', 'stddev', 'variance'].indexOf(nestedFacet.aggregate.function()) != -1) {
      fields = $.grep(self.template.fieldsAttributes(), function (field) {
        return isNumericColumn(field.type()) || isDateTimeColumn(field.type());
      })
    } else {
      fields = self.template.facetFieldsNames();
    }

    return fields.sort(function (a, b) {
      return a.name().toLowerCase().localeCompare(b.name().toLowerCase());
    });
  };

  self.facets = ko.mapping.fromJS(collection.facets);

  $.each(self.facets(), function (index, facet) {
    self._addObservablesToFacet(facet, vm);
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

  self.selectedDocument = ko.observable({uuid: window.location.getParameter('uuid'), statement_id: parseInt(window.location.getParameter('statement')) || 0});

  self.newQDefinitionName = ko.observable("");

  self.addQDefinition = function () {
    if ($.trim(self.newQDefinitionName()) != "") {
      var _def = ko.mapping.fromJS({
        'name': $.trim(self.newQDefinitionName()),
        'id': hueUtils.UUID(),
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

  self.addFacet = function (facet_json, callback) {
    self.removeFacet(function(){return facet_json.widget_id});
    hueAnalytics.log('dashboard', 'add_facet/' + facet_json.widgetType);

    $.post("/dashboard/template/new_facet", {
        "collection": ko.mapping.toJSON(self),
        "id": facet_json.widget_id,
        "label": facet_json.name,
        "field": facet_json.name,
        'window_size': $(window).width() - 600, // TODO: Find a better way to get facet width.
        "widget_type": facet_json.widgetType
      }, function (data) {
        if (data.status == 0) {
          var facet = ko.mapping.fromJS(data.facet);

          self._addObservablesToFacet(facet, vm); // Top widget
          self.facets.push(facet);
          huePubSub.publish('search.facet.added', facet);
          vm.search();
        } else {
          $(document).trigger("error", data.message);
        }
        if (callback) {
          callback();
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
      facet.properties.facets_form.mincount = 0;
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
        facet.properties.facets_form.mincount(0);
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
      'fieldLabel': ko.mapping.toJS(facet.properties.facets_form.field),
      'limit': ko.mapping.toJS(facet.properties.facets_form.limit),
      'mincount': ko.mapping.toJS(facet.properties.facets_form.mincount),
      'aggregate': ko.mapping.toJS(facet.properties.facets_form.aggregate),
      'sort': ko.mapping.toJS(facet.properties.facets_form.aggregate.function == 'count' ? 'desc' : 'default'),
      'canRange': ko.mapping.toJS(facet.properties.facets_form.canRange),
      'type': ko.mapping.toJS(facet.properties.facets_form.type),
      'isEditing': false
    });
    pivot.aggregate.metrics = ko.computed(function() {
      var _field = self.getTemplateField(pivot.field(), self.template.fieldsAttributes());
      return self._get_field_operations(_field, facet);
    });

    pivot.aggregate.facetFieldsNames = ko.computed(function() {
      return self._getCompatibleMetricFields(pivot);
    }).extend({ trackArrayChanges: true });

    facet.properties.facets_form.field(null);
    facet.properties.facets_form.limit(5);
    facet.properties.facets_form.mincount(0);
    facet.properties.facets_form.sort('desc');

    facet.properties.facets_form.aggregate.formula('');
    facet.properties.facets_form.aggregate.percentile = 50;

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

  self.dropOnWidget = function (id) {
    if (vm.isEditing() && vm.lastDraggedMeta() && vm.lastDraggedMeta().type === 'sql' && vm.lastDraggedMeta().column  && self.template.availableWidgetFieldsNames().indexOf(vm.lastDraggedMeta().column) > -1) {
      var facet = self.getFacetById(id);
      if (facet && facet.properties && facet.properties.facets_form) {
        facet.properties.facets_form.field(vm.lastDraggedMeta().column);
      }
      if (self.supportAnalytics()) {
        self.addPivotFacetValue2(facet);
      }
      else {
        self.addPivotFacetValue(facet);
      }
      vm.lastDraggedMeta(null);
    }
  }

  self.dropOnEmpty = function (column, atBeginning) {
    if (vm.isEditing() && vm.lastDraggedMeta() && vm.lastDraggedMeta().type === 'sql' && vm.lastDraggedMeta().column  && self.template.availableWidgetFieldsNames().indexOf(vm.lastDraggedMeta().column) > -1) {
      var row = column.addEmptyRow(atBeginning);
      if (self.supportAnalytics()) {
        row.addWidget(vm.draggableBucket());
      }
      else {
        row.addWidget(vm.draggableBar());
      }
      var widget = row.widgets()[0];
      self.addFacet({
        'name': vm.lastDraggedMeta().column,
        'widget_id': widget.id(),
        'widgetType': widget.widgetType()
      });
      vm.lastDraggedMeta(null);
    }
  }

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

  self.template.hasDataForChart = ko.computed(function () {
    var hasData = false;

    if ([window.HUE_CHARTS.TYPES.BARCHART, window.HUE_CHARTS.TYPES.LINECHART, window.HUE_CHARTS.TYPES.TIMELINECHART].indexOf(self.template.chartSettings.chartType()) >= 0) {
      hasData = typeof self.template.chartSettings.chartX() != "undefined" && self.template.chartSettings.chartX() != null && self.template.chartSettings.chartYMulti().length > 0;
    }
    else {
      hasData = typeof self.template.chartSettings.chartX() != "undefined" && self.template.chartSettings.chartX() != null && typeof self.template.chartSettings.chartYSingle() != "undefined" && self.template.chartSettings.chartYSingle() != null
        || self.template.chartSettings.chartType() == window.HUE_CHARTS.TYPES.COUNTER;
    }
    if (!hasData && self.template.showChart()){
      self.template.showFieldList(true);
    }
    return hasData;
  });

  self.template.fieldsModalFilter = ko.observable(""); // For UI
  self.template.autocompleteFromFieldsModalFilter = function (nonPartial, partial) {
    var result = [];
    var partialLower = partial.toLowerCase();
    self.template.availableWidgetFields().forEach(function (entry) {
      var value = typeof entry.name() == "string" ? entry.name() : entry.name().toString();
      if (value.toLowerCase().indexOf(partialLower) === 0) {
        result.push(nonPartial + partial + value.substring(partial.length));
      }
    });
    return result;
  };
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
    var bHasText = filter && filter.text && filter.text.length;
    var bHasFacet = filter && filter.facets && filter.facets['type'];
    if (!bHasText && !bHasFacet) {
      return self.template.availableWidgetFields();
    } else {
      var aType = bHasFacet ? Object.keys(filter.facets['type']).map(function (s) { return s && s.toLowerCase(); }) : [];
      var aText = filter.text.map(function (s) { return s && s.toLowerCase(); })
      return ko.utils.arrayFilter(self.template.availableWidgetFields(), function (field) {
        var bTextMatch = !bHasText || aText.some(function (text) {
          return field.name().toLowerCase().indexOf(text) > -1;
        });
        var bFacetMatch = !bHasFacet || aType.indexOf(field.type().toLowerCase()) > -1;
        return bTextMatch && bFacetMatch;
      });
    }
  });

  self.switchCollection = function() {
    $.post("/dashboard/get_collection", {
        name: self.name(),
        engine: self.engine(),
        source: self.source()
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
        huePubSub.publish('set.active.dashboard.collection', self);

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
        engine: self.engine(),
        source: self.source()
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
        engine: self.engine(),
        source: self.source()
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

  self.toggleSortFacet2 = function (widget, facet_field) {
    var sortField = facet_field.properties ? facet_field.properties.sort : facet_field.sort;

    if (sortField() == 'desc') {
      sortField('asc');
    } else if (sortField() == 'asc' && self.engine() != 'solr') {
      sortField('default');
    } else {
      sortField('desc');
    }

    // Update facets of same dimension to be consistent
    if (self.engine() == 'solr') {
      $.each(self.getDimensionFacets(widget, facet_field), function(index, facet) {
        if (facet != facet_field) {
          var sortField = facet.properties ? facet.properties.sort : facet.sort;
          sortField('default');
        }
      })
    }

    if (facet_field.properties && facet_field.properties.type && facet_field.properties.type() == 'range-up') {
      vm.query.removeFilter(ko.mapping.fromJS({'id': facet_field.id})); // Reset filter query
    }

    vm.search();
  };

  self.getDimensionFacets = function (widget, facet_field) {
    var facets = [widget];
    var facetFound = widget == facet_field;

    $.each(widget.properties.facets(), function(index, facet) {
      if (facet.aggregate.function() == 'count') {
        if (facetFound) {
          return false;
        } else {
          facets = [facet];
        }
      }
      if (facet == facet_field) {
        facetFound = true;
      } else {
        facets.push(facet);
      }
    });

    return facets;
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

  self.selectTimelineFacet2 = function (data) {
    var facet = self.getFacetById(data.widget_id);
    var nestedFacet = facet.properties.facets()[0];

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
          nestedFacet.gap(data.properties.gap);
        }
      },
      async: false
    });

    vm.search();
  }

  self.rangeZoomIn = function (facet_json) {
    var facet_id = ko.mapping.toJS(facet_json).id;
    var facet = self.getFacetById(facet_id);
    var fqs = vm.query.fqs();
    var fq;
    for (var i = 0; i < fqs.length; i++) {
      if (fqs[i].id() == facet_id) {
        fq = fqs[i];
      }
    }
    if (!fq || !fq.properties()[0].from) {
      return;
    }
    var properties;
    if (facet_json.type() == 'nested') {
      facet = facet.properties.facets()[0];
      properties = facet;
    } else {
      properties = facet.properties;
    }
    if (facet.isDate && facet.isDate()) {
      properties.start(moment(fq.properties()[0].from()).utc().format("YYYY-MM-DD[T]HH:mm:ss[Z]"));
      properties.end(moment(fq.properties()[0].to()).utc().format("YYYY-MM-DD[T]HH:mm:ss[Z]"));
    } else {
      properties.start(fq.properties()[0].from());
      properties.end(fq.properties()[0].to());
    }

    vm.search();
  };

  self.rangeZoomOut = function (facet_json) {
    var facet_id = ko.mapping.toJS(facet_json).id;
    var facet = self.getFacetById(facet_id);

    vm.query.removeFilter(ko.mapping.fromJS({'id': facet_id}));
    if (facet.properties.canRange()) {
      facet.properties.start(facet.properties.min());
      facet.properties.end(facet.properties.max());
      if (facet.properties.facets) {
        var nestedFacet = facet.properties.facets()[0];
        nestedFacet.start(facet.properties.min());
        nestedFacet.end(facet.properties.max());
      }
    }
    vm.search();
  }

  self.rangeZoomOut2 = function (facet_json) {
    var facet_id = ko.mapping.toJS(facet_json).id;
    var facet = self.getFacetById(facet_id).properties.facets()[0]; // 1 dimension only currently

    vm.query.removeFilter(ko.mapping.fromJS({'id': facet_id}));
    if (facet.gap() != null) { // Bar, line charts don't have gap
      facet.gap(facet.initial_gap());
    }
    if (facet.initial_start() != null) { // Bar and line charts
      facet.start(facet.initial_start());
      facet.end(facet.initial_end());
      facet.min(facet.initial_start());
      facet.max(facet.initial_end());
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

  self.name.subscribe(function(newValue) { // New Dashboard
    if (newValue && (self.engine() == 'solr' || /^[^\.]+\.[^\.]+$/.test(newValue))) {
      huePubSub.publish('dashboard.switch.collection');
      self.label(newValue);
      self.switchCollection();
      vm.search();
    }
  });

  self.showContextPopover = function (field, event) {
    var $source = $(event.target);
    var offset = $source.offset();
    var split = self.name().split('.');
    huePubSub.publish('context.popover.show', {
      data: {
        type: self.engine() === 'solr' ? 'collection' : 'column',
        identifierChain: [
          { name: split.length > 1 ? split[0] : 'default' },
          { name: split.length > 1 ? split[1] : split[0] },
          { name: field.name() }
        ]
      },
      showInAssistEnabled: true,
      sourceType: self.engine(),
      orientation: 'right',
      namespace: self.activeNamespace(),
      compute: self.activeCompute(),
      defaultDatabase: 'default',
      pinEnabled: false,
      source: {
        element: event.target,
        left: offset.left,
        top: offset.top - 3,
        right: offset.left + $source.width() + 1,
        bottom: offset.top + $source.height() - 3
      }
    });
  };

  huePubSub.publish('set.active.dashboard.collection', self);
};

var NewTemplate = function (vm, initial) {
  var self = this;

  self.collections = ko.mapping.fromJS(initial.collections);
  self.engines = ko.mapping.fromJS(initial.engines);
  self.layout = initial.layout;
  self.qbLayout = initial.qb_layout;
  self.textSearchLayout = initial.text_search_layout;
  self.inited = ko.observable(self.collections().length > 0); // No collection if not a new dashboard

  self.init = function() {
    if (!self.inited()) {
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
  var self = this; // TODO remove 'vm'

  self.id = ko.observable(hueUtils.UUID());
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


var DATE_TYPES = ['date', 'tdate', 'timestamp', 'pdate'];
var NUMBER_TYPES = [
    'int', 'tint', 'pint', 'long', 'tlong', 'plong', 'float', 'tfloat', 'pfloat', 'double', 'tdouble', 'pdouble', 'currency',
    'smallint', 'bigint', 'tinyint'
];
var FLOAT_TYPES = ['float', 'tfloat', 'pfloat', 'double', 'tdouble', 'pdouble'];
var GEO_TYPES = ['SpatialRecursivePrefixTreeFieldType'];

var RANGE_SELECTABLE_WIDGETS = ['histogram-widget', 'bar-widget', 'line-widget'];

var TempDocument = function () {
  var self = this;

  self.name = ko.observable('');
  self.uuid = ko.observable();
  self.uuid.subscribe(function (val) {
    if (val) {
      window.apiHelper.fetchDocument({ uuid: val, silenceErrors: false, fetchContents: true }).done(function (data) {
        if (data && data.data && data.data.snippets.length > 0) {
          self.name(data.document.name);
          var snippet = data.data.snippets[0];
          self.parsedStatements(sqlStatementsParser.parse(snippet.statement));
          self.selectedStatement(self.parsedStatements()[0].statement);
          self.selectedStatementId(0);
        }
      });
    }
  });

  self.parsedStatements = ko.observableArray([]);
  self.selectedStatement = ko.observable();
  self.selectedStatementId = ko.observable();

  self.reset = function () {
    self.name('');
    self.uuid('');
    self.parsedStatements([]);
    self.selectedStatement('');
    self.selectedStatementId('');
  }
}


var SearchViewModel = function (collection_json, query_json, initial_json, has_gridster_enabled, has_new_add_method) {

  var self = this;

  self.collectionJson = collection_json;
  self.queryJson = query_json;
  self.initialJson = initial_json;

  self.isGridster = ko.observable(!!has_gridster_enabled && (collection_json.layout.length === 0 || (collection_json.layout.length && collection_json.gridItems.length)));
  self.hasNewAdd = ko.observable(!!has_new_add_method);
  self.isQueryBuilder = ko.observable(false);

  if ($.totalStorage('hue.enable.gridster') === false) {
    self.isGridster(false);
  }

  self.showPlusButtonHint = ko.observable(false);
  self.showPlusButtonHint.subscribe(function(val){
    if (!val) {
      self.showPlusButtonHintShownOnce(true);
    }
  });
  self.showPlusButtonHintShownOnce = ko.observable(false);

  self.tempDocument = new TempDocument();


  self.build = function () {
    self.intervalOptions = ko.observableArray(ko.bindingHandlers.dateRangePicker.INTERVAL_OPTIONS);
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
          filterHash: '',
          counts: [],
          label: '',
          field: '',
          dimension: 1,
          extraSeries: [],
          // Hue 4
          hasRetrievedResults: true, // Temp
          results: [],
          response: '',
          fieldAnalysesName: '',
          querySpec: ''
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
    self.gridItems = ko.observableArray([]);
    self.additionalMustache = null;

    self.isEditing = ko.observable(false);
    self.toggleEditing = function () {
      self.isEditing(!self.isEditing());
      self.isToolbarVisible(self.isEditing());
    };

    self.isToolbarVisible = ko.observable(false);

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

    self.draggableWidgets = {};

    function bareWidgetBuilder(name, type, gridsterHeight) {
      var w = new Widget({
        size: 12,
        gridsterHeight: gridsterHeight,
        id: hueUtils.UUID(),
        name: name,
        widgetType: type,
        isEditing: false
      });

      self.draggableWidgets[type] = w;
      return w;
    }

    self.draggableHit = ko.observable(bareWidgetBuilder("Hit Count", "hit-widget", 6)); // Not used
    self.draggableFacet = ko.observable(bareWidgetBuilder("Facet", "facet-widget", 6)); // Deprecated
    self.draggableResultset = ko.observable(bareWidgetBuilder("Grid Results", "resultset-widget", 14));
    self.draggableHtmlResultset = ko.observable(bareWidgetBuilder("HTML Results", "html-resultset-widget", 16));
    self.draggableHistogram = ko.observable(bareWidgetBuilder("Histogram", "histogram-widget", 6)); // Deprecated
    self.draggableBar = ko.observable(bareWidgetBuilder("Bar Chart", "bar-widget", 6)); // Deprecated
    self.draggableMap = ko.observable(bareWidgetBuilder("Map", "map-widget", 6)); // Deprecated
    self.draggableLeafletMap = ko.observable(bareWidgetBuilder("Marker Map", "leafletmap-widget", 9));
    self.draggableLine = ko.observable(bareWidgetBuilder("Line Chart", "line-widget", 6)); // Deprecated
    self.draggablePie = ko.observable(bareWidgetBuilder("Pie Chart", "pie-widget", 6)); // Deprecated
    self.draggablePie2 = ko.observable(bareWidgetBuilder("Pie Chart", "pie2-widget", 6));
    self.draggableFilter = ko.observable(bareWidgetBuilder("Filter Bar", "filter-widget", 3));
    self.draggableTree = ko.observable(bareWidgetBuilder("Tree", "tree-widget", 6)); // Deprecated
    self.draggableHeatmap = ko.observable(bareWidgetBuilder("Heatmap", "heatmap-widget", 6));
    self.draggableCounter = ko.observable(bareWidgetBuilder("Counter", "hit-widget", 3));
    self.draggableBucket = ko.observable(bareWidgetBuilder("Chart", "bucket-widget", 6));
    self.draggableTimeline = ko.observable(bareWidgetBuilder("Timeline", "timeline-widget", 6));
    self.draggableGradienMap = ko.observable(bareWidgetBuilder("Gradient Map", "gradient-map-widget", 6));
    self.draggableTree2 = ko.observable(bareWidgetBuilder("Tree", "tree2-widget", 6));
    self.draggableTextFacet = ko.observable(bareWidgetBuilder("Text Facet", "text-facet-widget", 6));
    self.draggableDocument = ko.observable(bareWidgetBuilder("Document", "document-widget", 6));

    self.hasAvailableFields = ko.pureComputed(function () {
      return self.collection.availableFacetFields().length > 0;
    });
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
    });

    self.lastDraggedMeta = ko.observable();
    huePubSub.subscribe('draggable.text.meta', function (meta) {
      self.lastDraggedMeta(meta);
    }, 'dashboard');

    self.init = function (callback) {
      self.isEditing(self.columns().length == 0);
      self.isToolbarVisible(self.isEditing());
      self.initial.init();
      self.collection.syncFields();
      if (self.collection.engine() === 'solr') {
        self.search(callback);
      }
      else {
        callback();
      }
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
          self.isCanceling(false);
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

      if (!self.collection.name()) {
        return;
      }

      if (self.selectedQDefinition() != null) {
        var _prop = ko.mapping.fromJSON(self.selectedQDefinition().data());
        if (ko.toJSON(_prop.qs()) != ko.mapping.toJSON(self.query.qs())
          || ko.toJSON(_prop.selectedMultiq()) != ko.mapping.toJSON(self.query.selectedMultiq())) {
          self.selectedQDefinition().hasChanged(true);
        }
      } else if (location.getParameter("collection") != "") {
        var firstQuery = self.query.qs()[0].q();
        if (firstQuery != location.getParameter("q")) {
          hueUtils.changeURL("?collection=" + location.getParameter("collection") + (firstQuery ? "&q=" + firstQuery : ""));
        }
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
        var queryFragments = [].concat(self.collection.facets());
        if (self.collection.engine() != 'report') {
          queryFragments.concat([self.collection]);
        }

        $.each(queryFragments, function (index, facet) {
          if (facet.queryResult().result.handle) {
            self.close(facet);
          }
        });

        multiQs = $.map(self.collection.facets(), function (facet) {
          return $.post("/dashboard/search", {
            collection: ko.mapping.toJSON(self.collection),
            query: ko.mapping.toJSON(self.query),
            facet: ko.mapping.toJSON(facet)
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
          self.asyncSearchesCounter(queryFragments);
        }
      }

      $.each(self.fieldAnalyses(), function (index, analyse) { // Invalidate stats analysis
        analyse.stats.data.removeAll();
      });

      if (self.getFieldAnalysis()) {
        self.getFieldAnalysis().update();
      }

      if (self.collection.engine() != 'report') {
        multiQs.concat([
          $.post("/dashboard/search", {
            collection: ko.mapping.toJSON(self.collection),
            query: ko.mapping.toJSON(self.query),
            layout: ko.mapping.toJSON(self.columns)
          }, function (data) {
            huePubSub.publish('charts.state');
            data = JSON.bigdataParse(data);
            try {
              if (self.collection.engine() === 'solr') {
                self._make_grid_result(data, callback);
              } else {
                self.collection.queryResult(new QueryResult(self, {
                  type: self.collection.engine(),
                  result: data,
                  status: 'running',
                  progress: 0,
                }));
                self.checkStatus(self.collection);
                if (callback) {
                  callback();
                }
              }
            }
            catch (e) {
              console.log(e);
            }
          },
          "text")
        ]);
      }

      $.when.apply($, multiQs).done(function () {
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
        var _resultsHash = ko.mapping.toJSON(data.response.docs) + (data.response.moreLikeThis ? '/moreLikeThis' : '');

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
      var _fq = (function() {
        var _fq, fqs = self.query.fqs();
        for (var i = 0; i < fqs.length; i++) {
          var fq = fqs[i];
          if (fq.id() == new_facet.id) {
            _fq = fq;
            break;
          }
        }
        return _fq;
      })();
      var _filterHash = _fq ? ko.mapping.toJSON(_fq) : '';
      if (!facet.has_data() || facet.resultHash() != _hash || facet.filterHash() != _filterHash) {
        if (facet.countsSelectedSubscription) {
          facet.countsSelectedSubscription.dispose();
        }
        facet.counts(new_facet.counts);
        facet.autocompleteFromEntries = function (nonPartial, partial) {
          var result = [];
          var partialLower = partial.toLowerCase();
          facet.counts().forEach(function (entry) {
            var value = typeof entry.value == "string" ? entry.value : entry.value.toString();
            if (value.toLowerCase().indexOf(partialLower) === 0) {
              result.push(nonPartial + partial + value.substring(partial.length));
            }
          });
          return result;
        };
        $.each(facet.counts(), function (index, item) {
          item.text = item.value + ' (' + item.count + ')';
        });
        var countsSelected = _fq && _fq.filter()[0].value() || "";
        if (!facet.countsFiltered) {
          facet.countsSelected = ko.observable(countsSelected);
          facet.countsFiltered = ko.pureComputed(function() {
            var querySpec = facet.querySpec();
            if (!querySpec || !querySpec.query) return facet.counts();
            var text = querySpec.query.toLowerCase();
            return facet.counts().filter(function (entry) {
              var value = typeof entry.value == "string" ? entry.value : entry.value.toString();
              return value.toLowerCase().indexOf(text) >= 0;
            });
          });
        }
        setTimeout(function () { // Delay the execution, because setting facet.counts() above sets the value of countsSelected to ""
          facet.countsSelectedSubscription = facet.countsSelected.subscribe(function (value) {
            var bIsSingleSelect = self.collection.facets()
            .filter(function (facet) { return facet.id() == new_facet.id; })
            .reduce(function (isSingle, facet) {
              if (!facet.properties.facets) {
                return isSingle;
              }
              var dimension = facet.properties.facets()[0];
              return isSingle || (dimension.multiselect && !dimension.multiselect());
            }, false);
            if (!bIsSingleSelect) return;
            var counts = facet.counts();
            for (var i = 0; i < counts.length; i++) {
              if (counts[i].value == value && value !== '') {
                self.query.toggleFacet({ facet: counts[i], widget_id: new_facet.id }, true);
                return;
              }
            }
            self.query.toggleFacetClear({ widget_id: new_facet.id });
          });
          facet.countsSelected(countsSelected);
        },1);
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
        facet.hideStacked = ko.computed(function () {
          return facet.dimension() != 2 && !facet.extraSeries().length;
        });
        facet.displayValuesInLegend = ko.computed(function () {
          return !facet.hideStacked();
        });
        facet.selectedSerie = ko.observable({});
        facet.resultHash(_hash);
        facet.filterHash(_filterHash);
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
        doc['numFound'] = ko.observable(item.numFound);
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
              huePubSub.publish('gridster.remove.widget', widget_id);
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
        } else if (data.status == 1) {
          details.push(ko.mapping.fromJS({
            key: 'Warning',
            value: data.message
          }));
          $.each(doc.item, function (key, val) {
            if (key != '__ko_mapping__') {
              details.push(ko.mapping.fromJS({
                key: key,
                value: val,
                hasChanged: false
              }));
            }
          });
        } else {
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

    self.canSave = function () {
      return self.collection.id();
    };

    self.save = function () {
      var saveObj = {
        collection: ko.mapping.toJSON(self.collection),
        layout: ko.mapping.toJSON(self.columns)
      }
      if (self.isGridster()) {
        saveObj.gridItems = ko.mapping.toJSON(self.gridItems);
      }
      $.post("/dashboard/save", saveObj, function (data) {
        if (data.status == 0) {
          if (! self.collection.id()) {
            huePubSub.publish('assist.document.refresh');
          }
          var oldId  = self.collection.id();
          self.collection.id(data.id);
          $(document).trigger("info", data.message);
          if (oldId !== data.id) {
            hueUtils.changeURL('/hue/dashboard/?collection=' + data.id);
          }
        }
        else {
          $(document).trigger("error", data.message);
        }
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
      });
    };

    self.saveAs = function() {
      self.collection.id(null);
      self.collection.uuid(hueUtils.UUID());
      self.save();
    };

    loadSearchLayout(self, self.collectionJson.layout);
    if (self.collectionJson.gridItems && self.collectionJson.gridItems.length > 0) {
      loadDashboardLayout(self, self.collectionJson.gridItems);
    }
    else {
      self.gridItems(layoutToGridster(self));
    }

    huePubSub.subscribe('dashboard.set.layout', function() {
      self.gridItems(layoutToGridster(self));
    }, 'dashboard');

  };

  self.reset = function() {
    self.intervalOptions(ko.bindingHandlers.dateRangePicker.INTERVAL_OPTIONS);
    self.isNested(false);

    // Models
    ko.mapping.fromJS(self.initialJson.collections, self.initial.collections)
    ko.mapping.fromJS(self.initialJson.engines, self.initial.engines);
    self.initial.layout = self.initialJson.layout;
    self.initial.inited(self.initial.collections().length > 0);

    var c = self.collectionJson.collection;
    ko.mapping.fromJS(c.id, self.collection.id);
    self.collection.uuid(typeof c.uuid != "undefined" && c.uuid != null ? c.uuid : hueUtils.UUID());
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

    self.collection.template.chartSettings.hideStacked = ko.computed(function () {
      return self.collection.template.chartSettings.chartYMulti().length <= 1;
    });

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
    self.query.uuid(typeof q.uuid != "undefined" && q.uuid != null ? q.uuid : hueUtils.UUID());
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
    self.gridItems([]);
    loadSearchLayout(self, self.collectionJson.layout);
    self.isEditing(true);
    self.isToolbarVisible(true);
    self.isRetrievingResults(false);
    self.hasRetrievedResults(true);
    self.asyncSearchesCounter([]);
    self.isSyncingCollections(false);
    self.isPlayerMode(false);
    // loadDashboardLayout(self, self.collectionJson.gridItems); // TODO

    if (window.location.search.indexOf("collection") > -1) {
      hueUtils.changeURL('/hue/dashboard/new_search');
    }
  };


  self.build();
};

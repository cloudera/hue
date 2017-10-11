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

(function () {

  ko.HUE_CHARTS = {
    TYPES: {
      LINECHART: 'lines',
      BARCHART: 'bars',
      TIMELINECHART: 'timeline',
      POINTCHART: 'points',
      PIECHART: 'pie',
      MAP: 'map',
      GRADIENTMAP: 'gradientmap',
      SCATTERCHART: 'scatter'
    },
    PLOTLY_OPTIONS: {
      displaylogo: false,
      modeBarButtonsToRemove: ['sendDataToCloud', 'hoverCompareCartesian']
    }
  };

  ko.bindingHandlers.pieChart = {
    update: function (element, valueAccessor) {
      var _options = valueAccessor();
      var plotterTimeout = window.setTimeout(function () {
        window.clearTimeout(plotterTimeout);
        var _data = _options.transformer(_options.data);
        var chartData = {
          values: [],
          labels: [],
          type: 'pie'
        }
        _data.forEach(function (el) {
          chartData.values.push(el.value);
          chartData.labels.push(el.label);
        });
        var layout = {
          height: 400
        };
        Plotly.newPlot(element, [chartData], layout, ko.HUE_CHARTS.PLOTLY_OPTIONS);
      }, 10);
    }
  };

  ko.bindingHandlers.barChart = {
    init: function (element, valueAccessor) {
      $(element).html('To-do.');
    },
    update: function (element, valueAccessor) {
      $(element).html('To-do.');
    }
  };

  ko.bindingHandlers.timelineChart = {
    init: function (element, valueAccessor) {
      $(element).html('To-do.');
    },
    update: function (element, valueAccessor) {
      $(element).html('To-do.');
    }
  };

  ko.bindingHandlers.lineChart = {
    init: function (element, valueAccessor) {
      $(element).html('To-do.');
    },
    update: function (element, valueAccessor) {
      $(element).html('To-do.');
    }
  };

  ko.bindingHandlers.mapChart = {
    init: function (element, valueAccessor) {
      $(element).html('To-do.');
    },
    update: function (element, valueAccessor, allBindingsAccessor) {
      $(element).html('To-do.');
    }
  };

  ko.bindingHandlers.scatterChart = {
    update: function (element, valueAccessor) {
      $(element).html('To-do.');
    }
  };

  ko.bindingHandlers.partitionChart = {
    init: function (element, valueAccessor) {
      $(element).html('To-do.');
    },
    update: function (element, valueAccessor) {
      $(element).html('To-do.');
    }
  };

  window.chartsUpdatingState = function(){};
  window.chartsNormalState = function(){};

})();
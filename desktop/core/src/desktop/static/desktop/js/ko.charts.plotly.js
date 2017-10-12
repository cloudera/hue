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
    }
  };

  var PLOTLY_COMMON_LAYOUT = {
    height: 400
  };

  var PLOTLY_COMMON_OPTIONS = {
    displaylogo: false,
    modeBarButtonsToRemove: ['sendDataToCloud', 'hoverCompareCartesian']
  }

  function resizeHandlers(element) {
    var resizeSubscription = huePubSub.subscribe('resize.plotly.chart', function () {
      Plotly.Plots.resize(element);
    });
    var resizeEvent = function () {
      Plotly.Plots.resize(element);
    };

    $(window).on('resize', resizeEvent);
    ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
      resizeSubscription.remove();
      $(window).off('resize', resizeEvent);
    });
  }

  ko.bindingHandlers.pieChart = {
    init: function (element, valueAccessor) {
      resizeHandlers(element);
    },
    update: function (element, valueAccessor) {
      var options = valueAccessor();
      window.clearTimeout(element.plotterTimeout);
      element.plotterTimeout = window.setTimeout(function () {
        var data = options.transformer(options.data);
        var chartData = {
          values: [],
          labels: [],
          type: 'pie'
        }
        data.forEach(function (el) {
          chartData.values.push(el.value);
          chartData.labels.push(el.label);
        });
        Plotly.newPlot(element, [chartData], PLOTLY_COMMON_LAYOUT, PLOTLY_COMMON_OPTIONS);
      }, 200);
    }
  };

  ko.bindingHandlers.barChart = {
    init: function (element, valueAccessor) {
      resizeHandlers(element);
    },
    update: function (element, valueAccessor) {
      var options = valueAccessor();
      window.clearTimeout(element.plotterTimeout);
      element.plotterTimeout = window.setTimeout(function () {
        var data = options.transformer(options.datum);
        var chartData = {
          x: [],
          y: [],
          type: 'bar'
        }
        data.forEach(function (el) {
          el.values.forEach(function (serie) {
            chartData.x.push(serie.x);
            chartData.y.push(serie.y);
          });
        });
        Plotly.newPlot(element, [chartData], PLOTLY_COMMON_LAYOUT, PLOTLY_COMMON_OPTIONS);
      }, 200);
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
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

/*

  This is the Plotly replacement for the charts, currently not in use.

 */

import $ from 'jquery';
import ko from 'knockout';
import Plotly from 'plotly.js-dist';

import huePubSub from 'utils/huePubSub';

// TODO: Search and replace at source
window.HUE_CHARTS = {
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

const PLOTLY_COMMON_LAYOUT = {
  height: 400
};

const PLOTLY_COMMON_OPTIONS = {
  displaylogo: false,
  modeBarButtonsToRemove: ['sendDataToCloud', 'hoverCompareCartesian']
};

function resizeHandlers(element) {
  const resizeEvent = function() {
    try {
      if ($(element).is(':visible')) {
        Plotly.Plots.resize(element);
      }
    } catch (e) {}
  };
  const resizeSubscription = huePubSub.subscribe('resize.plotly.chart', resizeEvent);

  $(window).on('resize', resizeEvent);
  ko.utils.domNodeDisposal.addDisposeCallback(element, () => {
    resizeSubscription.remove();
    $(window).off('resize', resizeEvent);
  });
}

function eventEmitterSetup(element) {
  element.on('plotly_afterplot', () => {
    huePubSub.publish('plotly.afterplot', element);
  });
}

ko.bindingHandlers.pieChart = {
  init: function(element, valueAccessor) {
    resizeHandlers(element);
  },
  update: function(element, valueAccessor) {
    const options = valueAccessor();
    window.clearTimeout(element.plotterTimeout);
    element.plotterTimeout = window.setTimeout(() => {
      const data = options.transformer(options.data);
      const chartData = {
        values: [],
        labels: [],
        type: 'pie'
      };
      data.forEach(el => {
        chartData.values.push(el.value);
        chartData.labels.push(el.label);
      });
      Plotly.newPlot(element, [chartData], PLOTLY_COMMON_LAYOUT, PLOTLY_COMMON_OPTIONS);
      eventEmitterSetup(element);
    }, 200);
  }
};

function basicChartBuilder(element, valueAccessor, chartType) {
  const options = valueAccessor();
  window.clearTimeout(element.plotterTimeout);
  element.plotterTimeout = window.setTimeout(() => {
    const data = options.transformer(options.datum);
    const chartData = [];
    data.forEach(el => {
      const chartSerie = {
        x: [],
        y: [],
        name: el.key,
        type: options.chartType || chartType
      };
      el.values.forEach(serie => {
        chartSerie.x.push(serie.x);
        chartSerie.y.push(serie.y);
      });
      chartData.push(chartSerie);
    });
    Plotly.newPlot(element, chartData, PLOTLY_COMMON_LAYOUT, PLOTLY_COMMON_OPTIONS);
    eventEmitterSetup(element);
  }, 200);
}

ko.bindingHandlers.basicChart = {
  init: function(element, valueAccessor) {
    resizeHandlers(element);
  },
  update: function(element, valueAccessor) {
    basicChartBuilder(element, valueAccessor);
  }
};

ko.bindingHandlers.barChart = {
  init: function(element, valueAccessor) {
    resizeHandlers(element);
  },
  update: function(element, valueAccessor) {
    basicChartBuilder(element, valueAccessor, 'bar');
  }
};

ko.bindingHandlers.timelineChart = {
  init: function(element, valueAccessor) {
    resizeHandlers(element);
  },
  update: function(element, valueAccessor) {
    basicChartBuilder(element, valueAccessor, 'scatter');
  }
};

ko.bindingHandlers.lineChart = {
  init: function(element, valueAccessor) {
    resizeHandlers(element);
  },
  update: function(element, valueAccessor) {
    basicChartBuilder(element, valueAccessor, 'scatter');
  }
};

ko.bindingHandlers.mapChart = {
  init: function(element, valueAccessor) {
    $(element).html('To-do.');
  },
  update: function(element, valueAccessor, allBindingsAccessor) {
    $(element).html('To-do.');
  }
};

ko.bindingHandlers.scatterChart = {
  update: function(element, valueAccessor) {
    $(element).html('To-do.');
  }
};

ko.bindingHandlers.partitionChart = {
  init: function(element, valueAccessor) {
    $(element).html('To-do.');
  },
  update: function(element, valueAccessor) {
    $(element).html('To-do.');
  }
};

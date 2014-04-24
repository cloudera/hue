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


ko.bindingHandlers.pieChart = {
    init: function (element, valueAccessor) {
      var _options = valueAccessor();
      var _data = _options.transformer(_options.data);

      nv.addGraph(function () {
        var _chart = nv.models.pieChart()
                .x(function (d) {
                  return d.label
                })
                .y(function (d) {
                  return d.value
                })
                .height($(element).width())
                .showLabels(true).showLegend(false);

        var _d3 = ($(element).find('svg').length > 0) ? d3.select($(element).find('svg')[0]) : d3.select($(element)[0]).append('svg');

        _d3.datum(_data)
                .transition().duration(350)
                .call(_chart);
        nv.utils.windowResize(_chart.update);
        $(element).height($(element).width());
        return _chart;
      }, function () {
        d3.selectAll(".nv-slice").on('click',
                function (d, i) {
                  _options.onClick(d);
                });
      });
    },
    update: function (element, valueAccessor) {
      var value = valueAccessor();
      // do something with the updated value
    }
  };

ko.bindingHandlers.barChart = {
  init: function (element, valueAccessor) {
    barChart(element, valueAccessor(), false);
  },
  update: function (element, valueAccessor) {
    var value = valueAccessor();
    // do something with the updated value
  }
};

ko.bindingHandlers.timelineChart = {
  init: function (element, valueAccessor) {
    barChart(element, valueAccessor(), true);
  },
  update: function (element, valueAccessor) {
    var value = valueAccessor();
    // do something with the updated value
  }
};

function barChart(element, options, isTimeline) {

  var _data = options.transformer(options.data);
  $(element).height(300);

  nv.addGraph(function () {
    var _chart;
    if (isTimeline) {
      _chart = nv.models.multiBarWithFocusChart();
      _chart.enableSelection();
      _chart.onSelectRange(function(from, to){
        console.log("SELECT RANGE!")
        console.log(from);
        console.log(to);
      });
    }
    else {
      _chart = nv.models.multiBarChart();
    }

    _chart.margin({bottom: 100})
        .transitionDuration(300);

    _chart.multibar
        .hideable(true);
    if (isTimeline) {
      _chart.xAxis
          .showMaxMin(true)
          .tickFormat(d3.time.format("%Y-%m-%d %H:%M:%S"));
    }
    else {
      _chart.xAxis
          .showMaxMin(true)
          .tickFormat(d3.format(',0f'));
    }
    _chart.yAxis
        .tickFormat(d3.format(',0f'));

    var _d3 = ($(element).find('svg').length > 0) ? d3.select($(element).find('svg')[0]) : d3.select($(element)[0]).append('svg');
    _d3.datum([
          {
            key: options.label,
            values: _data
          }
        ])
        .call(_chart);

    nv.utils.windowResize(_chart.update);

    return _chart;
  }, function () {
    d3.selectAll(".nv-bar").on('click',
        function (d, i) {
          options.onClick(d);
        });
  });

}

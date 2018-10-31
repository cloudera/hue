## Licensed to Cloudera, Inc. under one
## or more contributor license agreements.  See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  Cloudera, Inc. licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.

<%!
from desktop.views import _ko
from django.utils.translation import ugettext as _
%>

<%def name="performanceGraph()">

  <script type="text/html" id="performance-graph-d3-template">
    <svg data-bind="style: { height: graphHeight + 'px', width: graphWidth + 'px' }"></svg>
  </script>

  <script type="text/html" id="performance-graph-template">
    <div class="performance-graph" style="position: relative">
      <h3 data-bind="text: header"></h3>
      <div style="position: absolute; right: 20px; top: 3px;">
        ${ _("Min") } <span style="font-weight: 300; margin-right: 10px" data-bind="text: min"></span> ${ _("Max") } <span style="font-weight: 300; margin-right: 10px" data-bind="text: max"></span> ${ _("Average") } <span style="font-weight: 300; margin-right: 10px" data-bind="text: average"></span>
      </div>
      <!-- ko template: { name: 'performance-graph-d3-template', afterRender: graphContainerRendered } --><!-- /ko -->
    </div>
  </script>

  <script type="text/javascript">


    (function () {
      var generateFakeData = function () {
        var entries = 100;
        var timeDiff = 300000; // 5 minutes
        var startTime = Date.now() - entries * timeDiff;
        var result = [];

        var lastVal = 0;
        for (var i = 0; i < 100; i++) {
          lastVal = Math.round(Math.max(Math.min(lastVal + (Math.random()-0.5) * 20, 100), 0));
          result.push({
            x: startTime + timeDiff * i,
            y: lastVal
          });
        }
        return result;
      };

      var AVAILABLE_TYPES = {
        'cpu': {
          header: '${ _("CPU") }'
        }
      };

      /**
       * @param {object} params
       *
       * @constructor
       */
      function PerformanceGraph(params) {
        var self = this;
        self.type = params.type;
        self.header = AVAILABLE_TYPES[self.type].header;
        self.graphHeight = 300;
        self.graphWidth = 750;
        self.graphMargin = { top: 15, right: 30, bottom: 20, left: 25 };

        self.average = ko.observable('-');
        self.max = ko.observable('-');
        self.min = ko.observable('-');
        self.datum = ko.observable();

        self.fetchData();

        self.graphContainerRendered = function (domTree) {
          var graphElement = domTree[1];

          var chart = nv.models.lineChart()
                  .margin(self.graphMargin)
                  .useInteractiveGuideline(true)
                  .transitionDuration(350)
                  .yDomain([0, 100])
                  .showLegend(false)
                  .showYAxis(true)
                  .showXAxis(true);

          chart.xAxis
                  .tickFormat(function(d){return moment(d).format('HH:mm:ss');})
                  .showMaxMin(false)
                  .tickPadding(10);

          chart.yAxis
                  .axisLabel('Percentage');

          d3.select(graphElement).datum(self.datum()).call(chart);
        }
      }

      PerformanceGraph.prototype.fetchData = function () {
        var self = this;
        var series = [];

        var values = generateFakeData();
        var max = 0, min = 0, average = 0;
        values.forEach(function (val) {
          if (val.y > max) {
            max = val.y;
          }
          if (val.y < min) {
            min = val.y
          }
          average += val.y;
        });
        average = average / values.length;

        series.push({
          values: values,
          key: AVAILABLE_TYPES[self.type].label,
          color: '#0B7FAD'
        });
        self.min(min + '%');
        self.max(max + '%');
        self.average(Math.round(average) + '%');
        self.datum(series);
      };

      ko.components.register('performance-graph', {
        viewModel: PerformanceGraph,
        template: { element: 'performance-graph-template' }
      });
    })();
  </script>
</%def>

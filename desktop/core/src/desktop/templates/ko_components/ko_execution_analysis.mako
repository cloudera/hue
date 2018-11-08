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
from django.utils.translation import ugettext as _

from notebook.conf import ENABLE_QUERY_SCHEDULING

from desktop.conf import IS_EMBEDDED, IS_MULTICLUSTER_ONLY
from desktop.lib.i18n import smart_unicode
from desktop.views import _ko
%>

<%def name="executionAnalysis()">
  <script src="${ static('desktop/ext/js/d3-tip.min.js') }"></script>
  <script src="${ static('desktop/ext/js/sprintf.min.js') }"></script>
  <script type="text/html" id="hue-execution-analysis-template">
    <div class="hue-execution-analysis">
      <!-- ko hueSpinner: { spin: loading, inline: true } --><!-- /ko -->
      <!-- ko ifnot: loading -->
        <!-- ko if: analysisPossible() && !analysis() -->
        <div class="no-analysis">${ _('Execute a query to get query execution analysis.') }</div>
        <!-- /ko -->
        <!-- ko ifnot: analysisPossible -->
        ## TODO: This should be removed once we have the proper analysis conditions,
        ##       it's better to not show the execution analysis tab in the first place.
        <div class="no-analysis">${ _('Analysis was not possible for the executed query.') }</div>
        <!-- /ko -->
        <!-- ko with: analysis -->
        <div>
          <h4>${_('Heatmap')}</h4>
          <div>
              <select data-bind="options: heatmapMetrics, event: { change: $parent.heatmapMetricChanged.bind($parent) }"></select>
              <svg class="heatmap"/>
          </div>
        </div>
        <div>
          <h4>${_('Summary')}</h4>
          <ul class="risk-list" data-bind="foreach: summary" style="margin-bottom: 10px">
            <li>
              <span data-bind="text: key"></span>: <strong><span data-bind="numberFormat: { value: value, unit: unit }"></strong></span>
            </li>
          </ul>
        </div>
        <div>
          <h4>${_('Top down analysis')}</h4>
          <ul class="risk-list" data-bind="foreach: healthChecks">
            <li>
              <div><span data-bind="text: contribution_factor_str"></span> - <strong><span data-bind="duration: wall_clock_time"></strong></div>
              <ul class="risk-list" data-bind="foreach: reason">
                <li>
                  <span data-bind="text: message"></span><strong> - <span data-bind="duration: impact"></span></strong>
                </li>
              </ul>
            </li>
          </ul>
        </div>
        <!-- /ko -->
      <!-- /ko -->
    </div>
  </script>

  <script type="text/javascript">
    (function () {
      var ExecutionAnalysis = function (params) {
        var self = this;
        self.disposals = [];

        self.loading = ko.observable(false);
        self.analysis = ko.observable();
        self.analysisPossible = ko.observable(true);
        self.analysisCount = ko.pureComputed(function () {
          if (!self.analysis()) {
            return '';
          }
          return '(' + self.analysis().healthChecks.reduce(function (count, check) {
            return count + check.reason.length;
          }, 0) + ')';
        });

        self.lastAnalysisPromise = undefined;

        var clearAnalysisSub = huePubSub.subscribe('editor.clear.execution.analysis', function() {
          if (!HAS_WORKLOAD_ANALYTICS) {
            return;
          }
          if (self.lastAnalysisPromise) {
            self.lastAnalysisPromise.cancel();
          }
          self.analysis(undefined);
          $('[href*=executionAnalysis] span:eq(1)').text(self.analysisCount());
          $(".d3-tip");
          d3.select(".heatmap").remove();
        });

        var executionAnalysisSub = huePubSub.subscribe('editor.update.execution.analysis', function (details) {
          if (!HAS_WORKLOAD_ANALYTICS) {
            return;
          }
          if (details.analysisPossible) {
            self.analysisPossible(true);
            self.loadAnalysis(details.compute, details.queryId);
          } else {
            self.analysisPossible(false);
          }
        });

        self.disposals.push(function () {
          clearAnalysisSub.remove();
          executionAnalysisSub.remove();
        });
      };
      ExecutionAnalysis.prototype.heatmapMetricChanged = function (model, el) {
        var self = this;
        self.updateHeatMap(self.analysis()['heatmap'][el.target.value], el.target.value);
      };
      ExecutionAnalysis.prototype.loadAnalysis = function (compute, queryId) {
        var self = this;
        self.loading(true);
        self.lastAnalysisPromise = ApiHelper.getInstance().fetchQueryExecutionAnalysis({
          silenceErrors: true,
          compute: compute,
          queryId: queryId
        }).done(function (response) {
          self.analysis(response.query);
          $('[href*=executionAnalysis] span:eq(1)').text(self.analysisCount());
          setTimeout(function () { // Wait for analysis to render
            self.updateHeatMap(response.query['heatmap'][response.query.heatmapMetrics[0]], response.query.heatmapMetrics[0]);
          }, 0);
        }).always(function () {
          self.loading(false);
        });
      };

      ExecutionAnalysis.prototype.updateHeatMap = function(data, counterName) {
        // Heatmap block and gap sizes
        var blockWidth = 40;
        var blockGap = 5;

        // Create tooltip
        var d3 = window.d3v3;
        $(".d3-tip").remove();
        var tip = d3.d3tip()
          .attr('class', 'd3-tip')
          .offset([-10, 0])
          .html(function(d) {
            var host = d[0];
            if (host.indexOf(":") >= 0) {
                host = host.substring(0, host.indexOf(":"));
            }
            var value = d[2];
            var formattedValue = String(value).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
            return "<strong style='color:cyan'>" + host + "</strong><br><strong>" + counterName + ":</strong> <span style='color:red'>" + formattedValue + "</span>";
          });
        d3.select(".heatmap").call(tip);

        // Color gradient
        var colors = ['#f6faaa', '#9E0142'];
        var colorScale = d3.scale.linear()
            .domain([0, 1])
            .interpolate(d3.interpolateHsl)
            .range(colors);

        // Define map dimensions
        var svgWidth = $(".heatmap").width();
        var cols = Math.trunc(svgWidth / (blockWidth + blockGap));
        $(".heatmap").height((Math.trunc((data.data.length - 1) / cols) + 1) * (blockWidth + blockGap));

        // Attribute functions
        var x = function(d, i) { return (i % cols) * (blockWidth + blockGap) + 1; };
        var y = function(d, i) { return Math.trunc(i / cols) * (blockWidth + blockGap) + 1; };
        var c = function(d, i) { return colorScale(d[3]); };

        d3.select(".heatmap").selectAll(".box")
            .data([])
          .exit()
            .remove();
        d3.select(".heatmap").selectAll(".box")
            .data(data.data)
          .enter()
            .append("rect")
            .attr("class", "box")
            .attr("x", x)
            .attr("y", y)
            .attr("height", blockWidth)
            .attr("width", blockWidth)
            .attr("fill", c)
            .on("mouseover", tip.show)
            .on("mouseout", tip.hide);
      }

      ExecutionAnalysis.prototype.dispose = function () {
        var self = this;
        while (self.disposals.length) {
          self.disposals.pop()();
        }
      };

      ko.components.register('hue-execution-analysis', {
        viewModel: ExecutionAnalysis,
        template: { element: 'hue-execution-analysis-template' }
      });
    })();
  </script>
</%def>

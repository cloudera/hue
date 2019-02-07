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
          <ul class="risk-list" data-bind="foreach: $parent.healthChecks">
            <li>
              <div><a href="javascript:void(0);" data-bind="click: $parents[1].handleNodePress.bind($parents[1], $data)"><span data-bind="text: contribution_factor_str"></span></a> - <strong><span data-bind="duration: wall_clock_time"></strong></div>
              <ol data-bind="foreach: reason">
                <li>
                  <span data-bind="text: message, css: { striked: fix.fixed }"></span><strong> - <span data-bind="numberFormat: { value: impact, unit: unit }"></span></strong><span data-bind="visible: fix.fixable && !fix.fixed"> - <a href="javascript:void(0);" data-bind="click: $parents[2].handleFix.bind($parents[2], $data.fix)">${_('Fix')}</a></span>
                </li>
              </ol>
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
        self.details = ko.observable();
        var analysisSub = self.analysis.subscribe(function (analysis) {
          $('[href*=executionAnalysis] span:eq(1)').text(self.analysisCount());
          setTimeout(function () { // Wait for analysis to render
            if (analysis.heatmap) {
              self.updateHeatMap(analysis.heatmap[analysis.heatmapMetrics[0]], analysis.heatmapMetrics[0]);
            } else {
              d3.select(".heatmap").remove();
            }
          }, 0);
        });
        self.healthChecks = ko.pureComputed(function () {
          var analysis = self.analysis()
          if (!analysis) {
            return [];
          }
          return analysis.healthChecks.filter(function (check) {
            return check.reason.length;
          });
        });
        self.analysisPossible = ko.observable(true);
        self.analysisCount = ko.pureComputed(function () {
          if (self.healthChecks().length) {
            return '(' + self.healthChecks().length + ')'
          }
          return '';
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
        });

        var executionAnalysisSub = huePubSub.subscribe('editor.update.execution.analysis', function (details) {
          if (!HAS_WORKLOAD_ANALYTICS) {
            return;
          }
          if (details.analysisPossible) {
            self.analysisPossible(true);
            self.details(details);
            self.loadAnalysis(details.compute, details.queryId);
          } else {
            self.analysisPossible(false);
          }
        });

        self.disposals.push(function () {
          analysisSub.dispose()
          clearAnalysisSub.remove();
          executionAnalysisSub.remove();
        });
      };
      ExecutionAnalysis.prototype.heatmapMetricChanged = function (model, el) {
        var self = this;
        var analysis = self.analysis();
        if (analysis.heatmap) {
          self.updateHeatMap(analysis.heatmap[analysis.heatmapMetrics[0]], analysis.heatmapMetrics[0]);
        }
      };
      ExecutionAnalysis.prototype.loadAnalysis = function (compute, queryId) {
        var self = this;
        self.loading(true);
        self.lastAnalysisPromise = window.apiHelper.fetchQueryExecutionAnalysis({
          silenceErrors: true,
          compute: compute,
          queryId: queryId
        }).done(function (response) {
          var analysis = response.query;
          self.analysis(analysis);
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
          .attr('class', 'risk d3-tip')
          .offset([-10, 0])
          .html(function(d) {
            var host = d[0];
            if (host.indexOf(":") >= 0) {
                host = host.substring(0, host.indexOf(":"));
            }
            var value = d[2];
            var unit = d[5];

            var formattedValue = ko.bindingHandlers.numberFormat.human(value, unit);
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

      ExecutionAnalysis.prototype.handleFix = function (fix) {
        var self = this;
        window.apiHelper.fixQueryExecutionAnalysis({ fix: fix, start_time: ko.mapping.toJSON((new Date()).getTime()), compute: self.details().compute })
        .done(function(resp) {
          huePubSub.publish('notebook.task.submitted', resp.task.history_uuid);
          fix.fixed = true;
          self.analysis.valueHasMutated();
        });
      };

      ExecutionAnalysis.prototype.handleNodePress = function (contributor) {
        var self = this;
        //TODO: Loading
        if (!$('[href*="' + self.details().name + '"]')[0]) {
          huePubSub.publish('show.jobs.panel', { id: self.details().name, interface: 'queries' });
          setTimeout(function() {
            huePubSub.publish('impala.node.moveto', contributor.result_id);
            huePubSub.publish('impala.node.select', contributor.result_id);
          }, 500);
        } else {
          if (!$('#jobsPanel').is(":visible")) {
            $('#jobsPanel').show();
          }
          huePubSub.publish('impala.node.moveto', contributor.result_id);
          huePubSub.publish('impala.node.select', contributor.result_id);
        }
      };

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

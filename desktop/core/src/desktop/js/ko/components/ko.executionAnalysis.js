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

import $ from 'jquery';
import d3v3 from 'd3v3';
import 'ext/d3-tip.min';
import ko from 'knockout';
import komapping from 'knockout.mapping';

import apiHelper from 'api/apiHelper';
import componentUtils from './componentUtils';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';

const TEMPLATE = `
  <div class="hue-execution-analysis">
    <!-- ko hueSpinner: { spin: loading, inline: true } --><!-- /ko -->
    <!-- ko ifnot: loading -->
      <!-- ko if: analysisPossible() && !analysis() -->
      <div class="no-analysis">${I18n('Execute a query to get query execution analysis.')}</div>
      <!-- /ko -->
      <!-- ko ifnot: analysisPossible -->
      <div class="no-analysis">${I18n('Analysis was not possible for the executed query.')}</div>
      <!-- /ko -->
      <!-- ko with: analysis -->
      <div>
        <h4>${I18n('Heatmap')}</h4>
        <div>
            <select data-bind="options: heatmapMetrics, event: { change: $parent.heatmapMetricChanged.bind($parent) }"></select>
            <svg class="heatmap"/>
        </div>
      </div>
      <div>
        <h4>${I18n('Summary')}</h4>
        <ul class="risk-list" data-bind="foreach: summary" style="margin-bottom: 10px">
          <li>
            <span data-bind="text: key"></span>: <strong><span data-bind="numberFormat: { value: value, unit: unit }"></strong></span>
          </li>
        </ul>
      </div>
      <div>
        <h4>${I18n('Top down analysis')}</h4>
        <ul class="risk-list" data-bind="foreach: $parent.healthChecks">
          <li>
            <div><a href="javascript:void(0);" data-bind="click: $parents[1].handleNodePress.bind($parents[1], $data)"><span data-bind="text: contribution_factor_str"></span></a> - <strong><span data-bind="duration: wall_clock_time"></strong></div>
            <ol data-bind="foreach: reason">
              <li>
                <span data-bind="text: message, css: { striked: fix.fixed }"></span><strong> - <span data-bind="numberFormat: { value: impact, unit: unit }"></span></strong><span data-bind="visible: fix.fixable && !fix.fixed"> - <a href="javascript:void(0);" data-bind="click: $parents[2].handleFix.bind($parents[2], $data.fix)">${I18n(
                  'Fix'
                )}</a></span>
              </li>
            </ol>
          </li>
        </ul>
      </div>
      <!-- /ko -->
    <!-- /ko -->
  </div>
`;

class ExecutionAnalysis {
  constructor() {
    const self = this;
    self.disposals = [];

    self.loading = ko.observable(false);
    self.analysis = ko.observable();
    self.details = ko.observable();
    const analysisSub = self.analysis.subscribe(analysis => {
      $('[href*=executionAnalysis] span:eq(1)').text(self.analysisCount());
      setTimeout(() => {
        // Wait for analysis to render
        if (analysis.heatmap) {
          self.updateHeatMap(
            analysis.heatmap[analysis.heatmapMetrics[0]],
            analysis.heatmapMetrics[0]
          );
        } else {
          d3v3.select('.heatmap').remove();
        }
      }, 0);
    });
    self.healthChecks = ko.pureComputed(() => {
      const analysis = self.analysis();
      if (!analysis) {
        return [];
      }
      return analysis.healthChecks.filter(check => {
        return check.reason.length;
      });
    });
    self.analysisPossible = ko.observable(true);
    self.analysisCount = ko.pureComputed(() => {
      if (self.healthChecks().length) {
        return '(' + self.healthChecks().length + ')';
      }
      return '';
    });
    self.lastAnalysisPromise = undefined;

    const clearAnalysisSub = huePubSub.subscribe('editor.clear.execution.analysis', () => {
      if (!window.HAS_WORKLOAD_ANALYTICS) {
        return;
      }
      if (self.lastAnalysisPromise) {
        self.lastAnalysisPromise.cancel();
      }
      self.analysis(undefined);
    });

    const executionAnalysisSub = huePubSub.subscribe(
      'editor.update.execution.analysis',
      details => {
        if (!window.HAS_WORKLOAD_ANALYTICS) {
          return;
        }
        if (details.analysisPossible) {
          self.analysisPossible(true);
          self.details(details);
          self.loadAnalysis(details.compute, details.queryId);
        } else {
          self.analysisPossible(false);
        }
      }
    );

    self.disposals.push(() => {
      analysisSub.dispose();
      clearAnalysisSub.remove();
      executionAnalysisSub.remove();
    });
  }

  heatmapMetricChanged(model, el) {
    const self = this;
    const analysis = self.analysis();
    if (analysis.heatmap) {
      self.updateHeatMap(analysis.heatmap[analysis.heatmapMetrics[0]], analysis.heatmapMetrics[0]);
    }
  }

  loadAnalysis(compute, queryId) {
    const self = this;
    self.loading(true);
    self.lastAnalysisPromise = apiHelper
      .fetchQueryExecutionAnalysis({
        silenceErrors: true,
        compute: compute,
        queryId: queryId
      })
      .done(response => {
        const analysis = response.query;
        self.analysis(analysis);
      })
      .always(() => {
        self.loading(false);
      });
  }

  updateHeatMap(data, counterName) {
    // Heatmap block and gap sizes
    const blockWidth = 40;
    const blockGap = 5;

    // Create tooltip
    const d3 = d3v3;
    $('.d3-tip').remove();
    const tip = d3
      .d3tip()
      .attr('class', 'risk d3-tip')
      .offset([-10, 0])
      .html(d => {
        let host = d[0];
        if (host.indexOf(':') >= 0) {
          host = host.substring(0, host.indexOf(':'));
        }
        const value = d[2];
        const unit = d[5];

        const formattedValue = ko.bindingHandlers.numberFormat.human(value, unit);
        return (
          "<strong style='color:cyan'>" +
          host +
          '</strong><br><strong>' +
          counterName +
          ":</strong> <span style='color:red'>" +
          formattedValue +
          '</span>'
        );
      });
    d3.select('.heatmap').call(tip);
    // Color gradient
    const colors = ['#f6faaa', '#9E0142'];
    const colorScale = d3.scale
      .linear()
      .domain([0, 1])
      .interpolate(d3.interpolateHsl)
      .range(colors);

    // Define map dimensions

    const $heatmap = $('.heatmap');
    const svgWidth = $heatmap.width();
    const cols = Math.trunc(svgWidth / (blockWidth + blockGap));
    $heatmap.height((Math.trunc((data.data.length - 1) / cols) + 1) * (blockWidth + blockGap));

    // Attribute functions
    const x = function(d, i) {
      return (i % cols) * (blockWidth + blockGap) + 1;
    };
    const y = function(d, i) {
      return Math.trunc(i / cols) * (blockWidth + blockGap) + 1;
    };
    const c = function(d) {
      return colorScale(d[3]);
    };

    d3.select('.heatmap')
      .selectAll('.box')
      .data([])
      .exit()
      .remove();
    d3.select('.heatmap')
      .selectAll('.box')
      .data(data.data)
      .enter()
      .append('rect')
      .attr('class', 'box')
      .attr('x', x)
      .attr('y', y)
      .attr('height', blockWidth)
      .attr('width', blockWidth)
      .attr('fill', c)
      .on('mouseover', tip.show)
      .on('mouseout', tip.hide);
  }

  handleFix(fix) {
    const self = this;
    apiHelper
      .fixQueryExecutionAnalysis({
        fix: fix,
        start_time: komapping.toJSON(new Date().getTime()),
        compute: self.details().compute
      })
      .done(resp => {
        huePubSub.publish('notebook.task.submitted', resp.task.history_uuid);
        fix.fixed = true;
        self.analysis.valueHasMutated();
      });
  }

  handleNodePress(contributor) {
    const self = this;
    //TODO: Loading
    if (!$('[href*="' + self.details().name + '"]')[0]) {
      huePubSub.publish('show.jobs.panel', { id: self.details().name, interface: 'queries' });
      setTimeout(() => {
        huePubSub.publish('impala.node.moveto', contributor.result_id);
        huePubSub.publish('impala.node.select', contributor.result_id);
      }, 500);
    } else {
      if (!$('#jobsPanel').is(':visible')) {
        $('#jobsPanel').show();
      }
      huePubSub.publish('impala.node.moveto', contributor.result_id);
      huePubSub.publish('impala.node.select', contributor.result_id);
    }
  }

  dispose() {
    const self = this;
    while (self.disposals.length) {
      self.disposals.pop()();
    }
  }
}

componentUtils.registerComponent('hue-execution-analysis', ExecutionAnalysis, TEMPLATE);

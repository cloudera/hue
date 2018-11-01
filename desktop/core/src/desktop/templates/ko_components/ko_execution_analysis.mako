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
  <script type="text/html" id="health-check-details-content">
    <div data-bind="text: description"></div>
  </script>

  <script type="text/html" id="health-check-details-title">
    <span data-bind="text: name"></span>
  </script>

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
        <ul class="risk-list" data-bind="foreach: healthChecks">
          <li data-bind="templatePopover : { placement: 'right', contentTemplate: 'health-check-details-content', titleTemplate: 'health-check-details-title', minWidth: '320px', trigger: 'hover' }">
            <div class="risk-list-title risk-list-normal"><span data-bind="text: name"></span></div>
          </li>
        </ul>
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

      ExecutionAnalysis.prototype.loadAnalysis = function (compute, queryId) {
        var self = this;
        self.loading(true);
        self.lastAnalysisPromise = ApiHelper.getInstance().fetchQueryExecutionAnalysis({
          silenceErrors: true,
          compute: compute,
          queryId: queryId
        }).done(function (response) {
          self.analysis(response.query)
        }).always(function () {
          self.loading(false);
        });
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

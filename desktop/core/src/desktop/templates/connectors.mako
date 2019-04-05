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

from desktop import conf
from desktop.views import commonheader, commonfooter
%>

<%
MAIN_SCROLLABLE = is_embeddable and "'.page-content'" or "window"
if conf.CUSTOM.BANNER_TOP_HTML.get():
  TOP_SNAP = is_embeddable and "78px" or "106px"
else:
  TOP_SNAP = is_embeddable and "50px" or "106px"
%>

<%namespace name="actionbar" file="actionbar.mako" />
<%namespace name="layout" file="about_layout.mako" />

%if not is_embeddable:
${ commonheader(_('Connectors'), "about", user, request) | n,unicode }
%endif


<script type="text/javascript">
  (function () {
    var ConnectorsViewModel = function () {
      var self = this;

      self.apiHelper = window.apiHelper;
      self.metrics = ko.observableArray();
      self.selectedMetric = ko.observable('All');
      self.metricsFilter = ko.observable();

      self.selectedMetrics = ko.pureComputed(function () {
        return self.metrics().filter(function (metric) {
          return self.selectedMetric() == 'All' || metric.category == self.selectedMetric();
        });
      });
      self.filteredMetrics = ko.pureComputed(function () {
        var metrics = self.selectedMetrics();

        if (self.metricsFilter()) {
          var lowerQuery = self.metricsFilter().toLowerCase();
          var filteredMetrics = []
          metrics.forEach(function (metric) {
            var _metric = {"category": metric.category, "values": []};
            _metric.values = metric.values.filter(function (subMetricKey) {
              return subMetricKey.name.toLowerCase().indexOf(lowerQuery) !== -1;
            });
            if (_metric.values.length > 0){
              filteredMetrics.push(_metric);
            }
          });
          metrics = filteredMetrics;
        }

        return metrics;
      });

      self.fetchConnectors = function () {
        self.apiHelper.simpleGet('/desktop/connectors/', {}, {successCallback: function (data) {
          self.metrics(data.metric);
        }});
      };
    }

    $(document).ready(function () {
      var viewModel = new ConnectorsViewModel();
      ko.applyBindings(viewModel, $('#connectorsComponents')[0]);
    });
  })();
</script>

${layout.menubar(section='connectors')}

<div id="connectorsComponents" class="container-fluid">
  <div class="card card-small margin-top-10">
    <div data-bind="dockable: { scrollable: ${ MAIN_SCROLLABLE }, jumpCorrection: 0,topSnap: '${ TOP_SNAP }', triggerAdjust: ${ is_embeddable and "0" or "106" }}">
      <ul class="nav nav-pills">
        <li data-bind="css: { 'active': $root.selectedMetric() === 'All' }">
          <a href="javascript:void(0)" data-bind="text: 'All', click: function(){ $root.selectedMetric('All') }"></a>
        </li>
        <!-- ko foreach: metrics() -->
        <li data-bind="css: { 'active': $root.selectedMetric() === $data.category }">
          <a href="javascript:void(0)" data-bind="text: $data.category, click: function(){ $root.selectedMetric($data.category) }"></a>
        </li>
        <!-- /ko -->
      </ul>
      <input type="text" data-bind="clearable: metricsFilter, valueUpdate: 'afterkeydown'"
          class="input-xlarge pull-right margin-bottom-10" placeholder="${ _('Filter metrics...') }">
    </div>

    <div class="margin-top-10">
      <div data-bind="foreach: filteredMetrics()">
        <h4 data-bind="text: category"></h4>
        <table class="table table-condensed">
          <thead>
            <tr>
              <th width="30%">${ _('Name') }</th>
              <th>${ _('Value') }</th>
            </tr>
          </thead>
          <!-- ko if: $data.values -->
          <tbody data-bind="foreach: values">
            <tr>
              <td data-bind="text: name"></td>
              <td data-bind="text: ''"></td>
            </tr>
          </tbody>
          <!-- /ko -->
          <!-- ko ifnot: $data.values -->
          <tfoot>
            <tr>
              <td colspan="2">${ _('There are no metrics matching your filter') }</td>
            </tr>
          </tfoot>
          <!-- /ko -->
          </table>
      </div>

      <!-- ko if: filteredMetrics().length == 0 -->
      <table class="table table-condensed">
        <thead>
          <tr>
            <th width="30%">${ _('Name') }</th>
            <th>${ _('Value') }</th>
          </tr>
        </thead>
        <tfoot>
          <tr>
            <td colspan="2">${ _('There are no metrics matching your filter') }</td>
          </tr>
        </tfoot>
      </table>
      <!-- /ko -->
  </div>
</div>


% if not is_embeddable:
 ${ commonfooter(request, messages) | n,unicode }
% endif

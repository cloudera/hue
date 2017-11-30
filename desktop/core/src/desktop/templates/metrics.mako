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
from desktop.views import commonheader, commonfooter
from django.utils.translation import ugettext as _
from desktop import conf
%>

<%
MAIN_SCROLLABLE = is_embeddable and ".page-content" or ".content-panel"
if conf.CUSTOM.BANNER_TOP_HTML.get():
  TOP_SNAP = is_embeddable and "78px" or "106px"
else:
  TOP_SNAP = is_embeddable and "50px" or "74px"
%>

<%namespace name="actionbar" file="actionbar.mako" />
<%namespace name="layout" file="about_layout.mako" />

%if not is_embeddable:
${ commonheader(_('Metrics'), "about", user, request) | n,unicode }
%endif


<script type="text/javascript">


  var MetricsViewModel = function () {
    var self = this;
    self.metricsFilter = ko.observable();
    self.metrics = ${metrics | n,unicode};
    self.selectedSubMetric = ko.observable(Object.keys(self.metrics)[0]);
    self.filteredMetrics = ko.pureComputed(function () {
      if (self.metricsFilter()) {
        var lowerQuery = self.metricsFilter().toLowerCase();
        var result = {};
        Object.keys(self.metrics).forEach(function (key) {
          var filteredSubMetric = {};
          var atleastOne = false;
          Object.keys(self.metrics[key]).forEach(function (subMetricKey) {
            if (subMetricKey.toLowerCase().indexOf(lowerQuery) !== -1) {
              filteredSubMetric[subMetricKey] = self.metrics[key][subMetricKey];
              atleastOne = true;
            }
          });
          if (atleastOne) {
            result[key] = filteredSubMetric;
          }
         });
        return result;
      }
      return self.metrics;
     });
  }

  $(document).ready(function () {
    var metricsViewModel = new MetricsViewModel();
    ko.cleanNode(document.getElementById("metricsComponent"));
    ko.applyBindings(metricsViewModel, document.getElementById('metricsComponent'));
  });

 </script>

${layout.menubar(section='metrics')}

<div id="metricsComponent" class="container-fluid">
 <span class="card card-small" style="padding-top: 10px">
  <br>
  <div data-bind="dockable: { scrollable: '${ MAIN_SCROLLABLE }', jumpCorrection: 0,topSnap: '${ TOP_SNAP }'}">
   <!-- ko if: $data.metrics -->
   <ol class="breadcrumb" data-bind="foreach: {'data': Object.keys($data.metrics)}">
     <li><a href="" data-bind="text: $data,click: function(){$root.selectedSubMetric(this)}"/></li>
   </ol><!-- /ko -->
    <br>
    <!-- ko hueSpinner: { spin: !$data.filteredMetrics(), center: true, size: 'xlarge' } --><!-- /ko -->
    <form class="form-search">
      <input type="text" data-bind="clearable: metricsFilter, valueUpdate: 'afterkeydown'"
             class="input-xlarge search-query float-right" placeholder="${_('Filter metrics...')}">
    </form>
  </div>
  <br>
  <div>
    <strong data-bind="text: $data.selectedSubMetric()"/>
    <table class="table table-condensed">
     <thead>
      <tr>
        <th>${ _('Name') }</th>
        <th>${ _('Value') }</th>
      </tr>
     </thead>
     <!-- ko if: $data.filteredMetrics()[$data.selectedSubMetric()] -->
     <tbody data-bind="foreach: {'data': Object.keys($data.filteredMetrics()[$data.selectedSubMetric()])}">
      <tr>
        <td data-bind="text: $data"></td>
        <td data-bind="text: $parent.filteredMetrics()[$parent.selectedSubMetric()][$data]"></td>
      </tr>
      </tbody>
     <!-- /ko -->
    </table>
  </div>

 </span>
</div>


%if not is_embeddable:
${ commonfooter(request, messages) | n,unicode }
%endif

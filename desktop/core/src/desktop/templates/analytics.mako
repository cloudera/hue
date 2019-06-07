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
MAIN_SCROLLABLE = "'.page-content'"
if conf.CUSTOM.BANNER_TOP_HTML.get():
  TOP_SNAP = "78px"
else:
  TOP_SNAP = "50px"
%>

<%namespace name="actionbar" file="actionbar.mako" />
<%namespace name="layout" file="about_layout.mako" />


<script type="text/javascript">
  (function () {
    var AnalyticsViewModel = function () {
      var self = this;

      self.apiHelper = window.apiHelper;

      self.stats = ko.observableArray();

      self.fetchAnalytics = function () {
        self.apiHelper.simpleGet('/desktop/analytics/api/admin_stats', {}, {successCallback: function (data) {
          self.stats(data.admin_stats);
        }});
      };
    }

    $(document).ready(function () {
      var viewModel = new AnalyticsViewModel();
      ko.applyBindings(viewModel, $('#analyticsComponents')[0]);
    });
  })();
</script>


${ layout.menubar(section='analytics') }


<div id="analyticsComponents" class="container-fluid">

  <a href="javascript:void(0)" data-bind="click: function() { selectedConnectorCategory('All'); section('installed-connectors-page'); }">
    ${ _('Analytics') }
  </a>

  <textarea data-bind="text: stats" readonly></textarea>
</script>

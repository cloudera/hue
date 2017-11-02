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
from desktop import conf
from desktop.lib.i18n import smart_unicode

from django.utils.translation import ugettext as _
from desktop.views import _ko
%>

<%def name="breadCrumbs()">

  <script type="text/html" id="breadcrumbs-template">
    <div class="hue-breadcrumb-container">
      <!-- ko if: hiddenBreadcrumbs().length > 0 -->
      ...
      <!-- ko component: { name: 'hue-drop-down', params: { entries: hiddenBreadcrumbs, noLabel: true, searchable: false, value: hiddenValue } } --><!-- /ko -->
      <div class="hue-breadcrumb-divider" data-bind="text: divider"></div>
      <!-- /ko -->
      <!-- ko foreach: lastTwoBreadcrumbs -->
      <!-- ko if: $index() < $parent.lastTwoBreadcrumbs().length - 1 -->
      <div class="hue-breadcrumb pointer" data-bind="text: $data.label || $data, click: $parent.onSelect"></div>
      <div class="hue-breadcrumb-divider" data-bind="text: $parent.divider"></div>
      <!-- /ko -->
      <!-- ko if: $index() === $parent.lastTwoBreadcrumbs().length - 1 -->
      <div class="hue-breadcrumb pointer" data-bind="text: $data.label || $data"></div>
      <!-- /ko -->
      <!-- /ko -->
    </div>
  </script>

  <script type="text/javascript">
    (function () {
      function BreadcrumbViewModel(params) {
        var self = this;
        self.hiddenValue = ko.observable();
        self.onSelect = params.onSelect || function () {};
        self.hiddenValue.subscribe(function (newValue) {
          if (newValue) {
            self.onSelect(newValue);
          }
        });
        self.hiddenBreadcrumbs = ko.pureComputed(function () {
          if (params.breadcrumbs().length > 2) {
            return params.breadcrumbs().slice(0, params.breadcrumbs().length - 2);
          }
          return [];
        });
        self.lastTwoBreadcrumbs = ko.pureComputed(function () {
          return params.breadcrumbs().slice(params.breadcrumbs().length - 2, params.breadcrumbs().length);
        });
        self.divider  = params.divider || '>';
      }

      ko.components.register('hue-breadcrumbs', {
        viewModel: BreadcrumbViewModel,
        template: { element: 'breadcrumbs-template' }
      });
    })();
  </script>

</%def>
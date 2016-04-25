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
from useradmin.models import group_permissions
from django.contrib.auth.models import Group
%>

<%namespace name="actionbar" file="actionbar.mako" />
<%namespace name="configKoComponents" file="/config_ko_components.mako" />
<%namespace name="layout" file="layout.mako" />
<%namespace name="require" file="/require.mako" />

${commonheader(_('Configurations'), "useradmin", user) | n,unicode}
${layout.menubar(section='configurations')}

<div class="container-fluid">
  <div class="card card-small">
    <h1 class="card-heading simple">${ _('Configurations') }</h1>
    <%actionbar:render>
      <%def name="search()">
        <input id="filterInput" type="text" class="input-xlarge search-query" placeholder="${_('Search for application, group, etc...')}" data-bind="visible: !loading() && !hasErrors(), textInput: searchQuery">
      </%def>
    </%actionbar:render>

    <!-- ko hueSpinner: { spin: loading, center: true, size: 'large' } --><!-- /ko -->
    <h4 style="width: 100%; text-align: center;" data-bind="visible: !loading() && hasErrors()">${ _('There was an error loading the configurations') }</h4>

    <table class="table table-striped table-condensed datatables" data-bind="visible: !loading() && !hasErrors()">
      <thead>
        <tr>
          <th>${ _('Application') }</th>
          <th>${ _('Default') }</th>
          <th>${ _('Groups') }</th>
        </tr>
      </thead>
      <tbody data-bind="foreach: appKeys">
        <tr class="tableRow">
          <td data-bind="text: $data"></td>
          <!-- ko with: $parent.filteredApps()[$data] -->
          <!-- ko if: $data.default -->
          <td>${ _('defined') }</td>
          <!-- /ko -->
          <!-- ko ifnot: $data.default -->
          <td>&nbsp;</td>
          <!-- /ko -->
          <!-- ko if: $data.groups -->
          <td data-bind="text: Object.keys(groups()).join(', ');"></td>
          <!-- /ko -->
          <!-- ko ifnot: $data.groups -->
          <td>&nbsp;</td>
          <!-- /ko -->
          <!-- /ko -->
        </tr>
      </tbody>
      <tfoot class="hide">
        <tr>
          <td colspan="3">
            <div class="alert">
              ${_('There are no configurations matching the search criteria.')}
            </div>
          </td>
        </tr>
      </tfoot>
    </table>
  </div>
</div>

${ require.config() }
${ configKoComponents.config() }

<script type="text/javascript" charset="utf-8">
  require([
    'knockout',
    'desktop/js/apiHelper',
    'knockout-mapping',
    'ko.hue-bindings'
  ], function (ko, apiHelper) {

    var ConfigurationsViewModel = function () {
      var self = this;
      self.apiHelper = apiHelper.getInstance({
        user: '${ user.username }'
      });
      self.hasErrors = ko.observable(false);
      self.loading = ko.observable(false);
      self.apps = ko.observableArray();
      self.searchQuery = ko.observable();
      self.filteredApps = ko.pureComputed(function () {
        return self.apps();
      });

      self.appKeys = ko.pureComputed(function () {
        return Object.keys(self.filteredApps()).filter(function (key) {
          return key.indexOf('__') !== 0;
        });
      });

      self.loadApps();
    };

    ConfigurationsViewModel.prototype.loadApps = function () {
      var self = this;
      if (self.loading()) {
        return;
      }
      self.loading(true);
      self.hasErrors(false);
      self.assistHelper.fetchConfigurations({
        successCallback: function (data) {
          self.apps(ko.mapping.fromJS(data.apps));
          self.loading(false);
        },
        errorCallback: function () {
          self.hasErrors(true);
          self.loading(false);
        }
      })
    };

    ko.applyBindings(new ConfigurationsViewModel());

  });
</script>

${layout.commons()}

${ commonfooter(request, messages) | n,unicode }

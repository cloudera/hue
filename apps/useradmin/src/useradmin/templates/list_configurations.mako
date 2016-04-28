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


<script id="app-list" type="text/html">
  <div class="card card-small">
    <h1 class="card-heading simple">${ _('Configurations') }</h1>
    <%actionbar:render>
      <%def name="search()">
        <input id="filterInput" type="text" class="input-xlarge search-query" placeholder="${_('Search for application, group, etc...')}" data-bind="textInput: searchQuery">
      </%def>
    </%actionbar:render>

    <table class="table table-striped table-condensed datatables">
      <thead>
      <tr>
        <th>${ _('Application') }</th>
        <th>${ _('Default') }</th>
        <th>${ _('Groups') }</th>
      </tr>
      </thead>
      <tbody data-bind="foreach: filteredApps">
      <tr class="tableRow pointer" data-bind="click: function () { $parent.edit($data); }">
        <td data-bind="text: name"></td>
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
</script>

<script id="edit-app" type="text/html">
  <!-- ko with: selectedApp -->
  <div class="card card-small" style="padding-bottom: 68px;">
    <h1 class="card-heading simple">${ _('Configuration') } - <!-- ko text: name --><!-- /ko --></h1>
    <h4 class="margin-left-20 simple">${ _('Global') }</h4>
    <div class="form-horizontal" style="width:100%;">
      <!-- ko foreach: properties -->
      <!-- ko template: { name: 'property', data: { type: type(), label: nice_name, helpText: help_text, value: value, visibleObservable: ko.observable() } } --><!-- /ko -->
      <!-- /ko -->
    </div>

    <h4 class="margin-left-20 simple">${ _('Group specific') }</h4>
    <!-- ko foreach: groupConfigurations -->
    <div class="form-horizontal" style="width:100%;">
      <div>
        <select data-bind="options: availableGroups, optionsText: 'name', optionsValue: 'id', value: group"></select>
      </div>
      <!-- ko foreach: properties -->
      <!-- ko template: { name: 'property', data: { type: type(), label: nice_name, helpText: help_text, value: value, visibleObservable: ko.observable() } } --><!-- /ko -->
      <!-- /ko -->
    </div>
    <!-- /ko -->
    <a class="pointer" data-bind="click: addGroup">
      <i class="fa fa-plus"></i>
    </a>
  </div>
  <!-- /ko -->
  <div class="form-actions">
    <button class="btn btn-primary" data-bind="click: save">${_('Update configuration')}</button>
    <button class="btn" data-bind="click: function () { selectedApp(null) }">${_('Cancel')}</button>
  </div>
</script>

<div class="container-fluid">
  <!-- ko hueSpinner: { spin: loading, center: true, size: 'large' } --><!-- /ko -->
  <h4 style="width: 100%; text-align: center;" data-bind="visible: !loading() && hasErrors()">${ _('There was an error loading the configurations') }</h4>
  <!-- ko template: { if: !loading() && !hasErrors() && !selectedApp(), name: 'app-list' } --><!-- /ko -->
  <!-- ko template: { if: !loading() && !hasErrors() && selectedApp(), name: 'edit-app' } --><!-- /ko -->
</div>

${ require.config() }
${ configKoComponents.config() }

<script type="text/javascript" charset="utf-8">
  require([
    'knockout',
    'desktop/js/apiHelper',
    'knockout-mapping',
    'ko.hue-bindings',
    'knockout-sortable'
  ], function (ko, apiHelper) {

    var GroupConfiguration = function (properties, availableGroups) {
      var self = this;
      self.properties = ko.mapping.fromJS(properties);
      self.availableGroups = availableGroups;
      self.group = ko.observable();
    };

    var AppConfiguration = function (app, availableGroups) {
      var self = this;
      self.name = app.name;
      self.availableProperties = app.properties;
      self.properties = ko.mapping.fromJS(app.properties);
      self.availableGroups = availableGroups;
      self.groupConfigurations = ko.observableArray();
    };

    AppConfiguration.prototype.addGroup = function () {
      var self = this;
      self.groupConfigurations.push(new GroupConfiguration(self.availableProperties, self.availableGroups));
    };

    var ConfigurationsViewModel = function () {
      var self = this;
      self.apiHelper = apiHelper.getInstance({
        user: '${ user.username }'
      });
      self.hasErrors = ko.observable(false);
      self.loading = ko.observable(false);
      self.apps = ko.observableArray();
      self.groups = {};
      self.searchQuery = ko.observable();
      self.selectedApp = ko.observable();
      self.filteredApps = ko.pureComputed(function () {
        return self.apps();
      });

      self.load();
    };

    ConfigurationsViewModel.prototype.edit = function (app) {
      var self = this;
      self.selectedApp(new AppConfiguration(app, self.groups));
    };

    ConfigurationsViewModel.prototype.save = function () {
      var self = this;
      var data = {};
      self.apps().forEach(function (app) {
        data[app.name] = app;
      });
      data[self.selectedApp().name] = {
        properties: ko.mapping.toJS(self.selectedApp().properties),
        groups: {}
      };
      self.selectedApp().groupConfigurations().forEach(function (groupConfig) {
        data[self.selectedApp().name].groups[groupConfig.group()] = ko.mapping.toJS(groupConfig.properties);
      });
      self.apiHelper.saveGlobalConfiguration({
        successCallback: function(data) {
          var apps = [];
          $.each(data.apps, function (appName, app) {
            app.name = appName;
            apps.push(app);
          });
          self.apps(apps);
          self.selectedApp(null);
        },
        configuration: data
      })
    };

    ConfigurationsViewModel.prototype.load = function () {
      var self = this;
      if (self.loading()) {
        return;
      }
      self.selectedApp(null);
      self.loading(true);
      self.hasErrors(false);

      var errorCallback = function () {
        self.hasErrors(true);
        self.loading(false);
      };

      self.apiHelper.fetchUsersAndGroups({
        successCallback: function (usersAndGroups) {
          self.groups = usersAndGroups.groups;
          self.apiHelper.fetchConfigurations({
            successCallback: function (data) {
              var apps = [];
              $.each(data.apps, function (appName, app) {
                app.name = appName;
                apps.push(app);
              });
              self.apps(apps);
              self.loading(false);
            },
            errorCallback: errorCallback
          })
        },
        errorCallback: errorCallback
      });
    };

    ko.applyBindings(new ConfigurationsViewModel());

  });
</script>

${layout.commons()}

${ commonfooter(request, messages) | n,unicode }

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
from desktop.views import _ko
from useradmin.models import group_permissions
from django.contrib.auth.models import Group
%>

<%namespace name="actionbar" file="actionbar.mako" />
<%namespace name="configKoComponents" file="/config_ko_components.mako" />
<%namespace name="layout" file="layout.mako" />
%if not is_embeddable:
${commonheader(_('Configurations'), "useradmin", user, request) | n,unicode}
%endif
${layout.menubar(section='configurations')}

<script src="${ static('metastore/js/metastore.ko.js') }"></script>

<script id="app-list" type="text/html">
  <div class="card card-small">
    <h1 class="card-heading simple">${ _('Configurations') }</h1>

    <table class="table table-condensed datatables margin-top-20">
      <thead>
      <tr>
        <th>${ _('Application') }</th>
        <th>${ _('Groups') }</th>
      </tr>
      </thead>
      <tbody data-bind="foreach: filteredApps">
      <tr class="tableRow pointer" data-bind="click: function () { $parent.edit($data); }">
        <td data-bind="text: name"></td>
        <!-- ko if: $data.groups -->
        <td data-bind="text: overriddenGroupNames"></td>
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
    <h1 class="card-heading simple"><!-- ko text: name --><!-- /ko --> ${ _('configuration') }</h1>

    <!-- ko foreach: groups -->
    <h4 class="margin-left-20" style="display: inline-block;">${ _('Role') }</h4>
    <div class="config-actions">
      <a class="inactive-action pointer margin-left-10" title="${ _('Remove') }" rel="tooltip" data-bind="click: function() { $parent.groups.remove($data) }"><i class="fa fa-times"></i> ${ _('Remove') }</a>
    </div>
    <div class="form-horizontal margin-top-20">
      <div class="control-group">
        <label class="control-label">${ _('Groups') }</label>
        <div class="controls">
          <!-- ko component: { name: 'multi-group-selector',
            params: {
              width: 500,
              height: 198,
              options: allGroups,
              optionsValue: 'id',
              optionsText: 'name',
              selectedOptions: group_ids,
            }
          } --><!-- /ko -->
        </div>
      </div>
      <div class="control-group">
        <label class="control-label">${ _('Properties') }</label>
        <div class="controls">
          <!-- ko component: { name: 'property-selector', params: { properties: properties } } --><!-- /ko -->
        </div>
      </div>
    </div>
    <!-- /ko -->
    <div class="margin-left-20 margin-top-20">
      <a class="inactive-action pointer" href="javascript:void(0)" data-bind="click: addGroupOverride">
        <i class="fa fa-plus"></i> ${ _('Add role') }
      </a>
    </div>
  </div>
  <!-- /ko -->
  <div class="form-actions">
    <button class="btn btn-primary" data-bind="click: save">${ _('Update configuration') }</button>
    <button class="btn" data-bind="click: function () { selectedApp(null) }">${ _('Cancel') }</button>
  </div>
</script>

<div id="configurationsComponents" class="container-fluid">
  <!-- ko hueSpinner: { spin: loading, center: true, size: 'large' } --><!-- /ko -->
  <h4 style="width: 100%; text-align: center; display: none;" data-bind="visible: !loading() && hasErrors()">${ _('There was an error loading the configurations') }</h4>
  <!-- ko template: { if: !loading() && !hasErrors() && !selectedApp(), name: 'app-list' } --><!-- /ko -->
  <!-- ko template: { if: !loading() && !hasErrors() && selectedApp(), name: 'edit-app' } --><!-- /ko -->
</div>

%if not is_embeddable:
${ configKoComponents.config() }
%endif

<script type="text/javascript">
  (function () {
    var GroupOverride = function (group, allGroups) {
      var self = this;
      self.allGroups = allGroups;
      ko.mapping.fromJS(group, {}, self);
    };

    var AppConfiguration = function (app, allGroups) {
      var self = this;
      self.rawProperties = app.properties;
      self.rawApp = app;
      self.allGroups = allGroups;
      ko.mapping.fromJS(app, {
        'groups': {
          create: function(options) {
            return new GroupOverride(options.data, self.allGroups);
          }
        }
      }, self);

      self.overriddenGroupNames = ko.pureComputed(function () {
        var groups = {};
        var groupIndex = {};
        self.allGroups().forEach(function (group) {
          groupIndex[group.id] = group.name;
        });

        self.groups().forEach(function (groupOverride) {
          groupOverride.group_ids().forEach(function (id) {
            groups[groupIndex[id]] = true;
          })
        });
        return Object.keys(groups).sort().join(', ');
      });
    };

    AppConfiguration.prototype.addGroupOverride = function () {
      var self = this;
      self.groups.push(new GroupOverride({
        group_ids: [],
        properties: self.rawProperties
      }, self.allGroups));
    };

    var ConfigurationsViewModel = function () {
      var self = this;
      self.apiHelper = window.apiHelper;
      self.hasErrors = ko.observable(false);
      self.loading = ko.observable(false);
      self.apps = ko.observableArray();
      self.allGroups = ko.observableArray();
      self.searchQuery = ko.observable();
      self.selectedApp = ko.observable();
      self.filteredApps = ko.pureComputed(function () {
        return self.apps();
      });
      self.load();
    };

    ConfigurationsViewModel.prototype.edit = function (app) {
      var self = this;
      self.selectedApp(new AppConfiguration(app.rawApp, self.allGroups));
    };

    ConfigurationsViewModel.prototype.save = function () {
      var self = this;
      var data = {};
      self.apps().forEach(function (app) {
        data[app.name()] = app;
      });

      data[self.selectedApp().name()] = self.selectedApp();

      $.each(data, function (app, appConfig) {
        var actualGroups = [];
        appConfig.groups().forEach(function (groupConfig) {
          var actualGroupOverrides = $.grep(groupConfig.properties(), function (property) {
            return property.defaultValue().toString() !== property.value().toString()
          });
          if (actualGroupOverrides.length > 0 && groupConfig.group_ids().length > 0) {
            actualGroups.push({
              group_ids: ko.mapping.toJS(groupConfig.group_ids),
              properties: actualGroupOverrides
            });
          }
        });
        data[app] = ko.mapping.toJS(appConfig);
        data[app].groups = actualGroups;
      });

      self.apiHelper.saveGlobalConfiguration({
        successCallback: function(data) {
          self.updateFromData(data);
          self.selectedApp(null);
        },
        configuration: data
      })
    };

    ConfigurationsViewModel.prototype.updateFromData = function (data) {
      var self = this;
      var apps = [];
      var groupIndex = {};
      self.allGroups().forEach(function (group) {
        groupIndex[group.id] = group;
      });

      $.each(data.configuration, function (appName, app) {
        app.name = appName;
        app.default = []; // Delete any existing default overrides

        if (typeof app.groups === 'undefined') {
          app.groups = [];
        } else {
          var groups = [];
          app.groups.forEach(function (group) {
            var groupPropertyIndex = {};
            group.properties.forEach(function (groupProperty) {
              groupPropertyIndex[groupProperty.name || groupProperty.nice_name] = groupProperty;
            })
            // Merge the base properties into any existing group config
            app.properties.forEach(function (property) {
              if (!groupPropertyIndex[property.name || property.nice_name]){
                group.properties.push(property);
              }
            });
          });
        }
        apps.push(new AppConfiguration(app, self.allGroups));
      });
      apps.sort(function (a, b) {
        return a.name().localeCompare(b.name());
      })
      self.apps(apps);
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
          self.allGroups(usersAndGroups.groups);
          self.apiHelper.fetchConfigurations({
            successCallback: function (data) {
              self.updateFromData(data);
              self.loading(false);
            },
            errorCallback: errorCallback
          })
        },
        errorCallback: errorCallback
      });
    };

    ko.applyBindings(new ConfigurationsViewModel(), $('#configurationsComponents')[0]);

  })();
</script>

${layout.commons()}
%if not is_embeddable:
${ commonfooter(request, messages) | n,unicode }
%endif

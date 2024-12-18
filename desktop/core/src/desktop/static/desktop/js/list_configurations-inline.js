
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
        create: function (options) {
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
      successCallback: function (data) {
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
            if (!groupPropertyIndex[property.name || property.nice_name]) {
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

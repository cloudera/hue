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


// groups, privileges


var Privilege = function (vm, privilege) {
  var self = this;

  self.privilegeScope = ko.observable(typeof privilege.privilegeScope != "undefined" && privilege.privilegeScope != null ? privilege.privilegeScope : "");
  self.serverName = ko.observable(typeof privilege.serverName != "undefined" && privilege.serverName != null ? privilege.serverName : "");
  self.dbName = ko.observable(typeof privilege.dbName != "undefined" && privilege.dbName != null ? privilege.dbName : "");
  self.tableName = ko.observable(typeof privilege.tableName != "undefined" && privilege.tableName != null ? privilege.tableName : "");
  self.URI = ko.observable(typeof privilege.URI != "undefined" && privilege.URI != null ? privilege.URI : "");
  self.action = ko.observable(typeof privilege.action != "undefined" && privilege.action != null ? privilege.action : "");

  self.availablePrivileges = ko.observableArray(['SERVER', 'DATABASE', 'TABLE']);
  self.availableActions = ko.observableArray(['SELECT', 'INSERT', 'ALL', '']);
}

var Role = function(vm, privilege) {
  var self = this;

  self.name = ko.observable('');
  self.groups = ko.observableArray();
  self.privileges = ko.observableArray();


  self.reset = function() {
	self.name('');
    self.groups.removeAll();
    self.privileges.removeAll();
  }

  self.addGroup = function() {
    self.groups.push('');
  }

  self.addPrivilege = function() {
	self.privileges.push(new Privilege(vm, {}));
  }

  self.create = function() {
	$(".jHueNotify").hide();
    $.post("/security/api/hive/create_role", {
        role: ko.mapping.toJSON(self)
      }, function (data) {
        if (data.status == 0) {
          $(document).trigger("info", data.message);
          data.role['privileges'] = ko.observableArray();
          data.role['newPrivileges'] = ko.observableArray();
          data.role['showPrivileges'] = ko.observable(false);
          vm.roles.unshift(data.role);
          self.reset();
          vm.showCreateRole(false);
        }
        else {
          $(document).trigger("error", data.message);
        }
    }).fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });
  }

  self.remove = function(role) {
	$(".jHueNotify").hide();
    $.post("/security/api/hive/drop_sentry_role", {
    	roleName: role.name
      }, function (data) {
        if (data.status == 0) {
          $(document).trigger("info", data.message);
          vm.removeRole(role.name);
        }
        else {
          $(document).trigger("error", data.message);
        }
    }).fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });
  }

  self.addNewPrivilege = function(role) {
    role['newPrivileges'].push(new Privilege(self, {}));
  }

  self.saveNewPrivileges = function(role) {
	$(".jHueNotify").hide();
    $.post("/security/api/hive/add_privileges", {
        role: ko.mapping.toJSON(role)
      }, function (data) {
        if (data.status == 0) {
          $.each(data.privileges, function(index, privileges) { // TODO: get back a set<TSentryPrivilege>
            //role['privileges'] = ko.observableArray();
            //vm.roles.unshift(data.role); privileges
          });
          // self.reset();
        }
        else {
          $(document).trigger("error", data.message);
        }
    }).fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });
  }
}


var Assist = function (vm) {
  var self = this;

  self.path = ko.observable('');
  self.path.subscribe(function () {
	self.fetchDatabases();
  });
  self.files = ko.observableArray();

  self.fetchDatabases = function() {
    var request = {
      url: '/beeswax/api/autocomplete', // impala too
      dataType: 'json',
      type: 'GET',
      success: function(data) {
        self.files(data.databases);
      },
      cache: false
    };
    $.ajax(request).fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });
  };
}


var HiveViewModel = function (initial) {
  var self = this;

  // Models
  self.roles = ko.observableArray();
  self.privileges = ko.observableArray();
  self.availableHadoopGroups = ko.mapping.fromJS(initial.hadoop_groups);
  self.assist = new Assist(self);

  // Edition
  self.showCreateRole = ko.observable(false);
  self.role = new Role(self);
  self.privilege = new Privilege(self, {});


  self.init = function() {
    self.list_sentry_roles_by_group();
    self.assist.fetchDatabases();
  };

  self.removeRole = function(roleName) {
    $.each(self.roles(), function (index, role) {
      if (role.name == roleName) {
        self.roles.remove(role);
        return false;
      }
    });
  };

  self.list_sentry_roles_by_group = function() {
    $.getJSON('/security/api/hive/list_sentry_roles_by_group', {    	
      }, function (data) {
        $.each(data.roles, function(index, item) {
          item['privileges'] = ko.observableArray();
          item['showPrivileges'] = ko.observable(false);
          item['newPrivileges'] = ko.observableArray();
    	  self.roles.push(item);
        });
    }).fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });
  };

  self.list_sentry_privileges_by_role = function(role) {
    $.ajax({
      type: "POST",
      url: "/security/api/hive/list_sentry_privileges_by_role",
      data: {    	
        'roleName': role.name
      },
      success: function (data) {
    	role.privileges.removeAll();
        $.each(data.sentry_privileges, function(index, item) {
          role.privileges.push(ko.mapping.fromJS(item));
        });
        role.showPrivileges(true);
      }
    }).fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });
  };

  self.list_sentry_privileges_for_provider = function(role) {
    $.ajax({
      type: "POST",
      url: "/security/api/hive/list_sentry_privileges_for_provider",
      data: {    	
    	groups: ko.mapping.toJSON(['sambashare']),
    	roleSet: ko.mapping.toJSON({all: true, roles: []}),
        authorizableHierarchy: ko.mapping.toJSON({'server': 'aa', 'db': 'default'}),
      },
      success: function (data) {
    	alert(ko.mapping.toJSON(data));
      }
    }).fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });
  };
};

function logGA(page) {
  if (typeof trackOnGA == 'function') {
    trackOnGA('security/' + page);
  }
}

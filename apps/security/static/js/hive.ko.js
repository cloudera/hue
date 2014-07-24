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


var Privilege = function (vm, privilege) {
  var self = this;

  self.privilegeScope = ko.observable(typeof privilege.privilegeScope != "undefined" && privilege.privilegeScope != null ? privilege.privilegeScope : "");
  self.serverName = ko.observable(typeof privilege.serverName != "undefined" && privilege.serverName != null ? privilege.serverName : "");
  self.dbName = ko.observable(typeof privilege.dbName != "undefined" && privilege.dbName != null ? privilege.dbName : "");
  self.tableName = ko.observable(typeof privilege.tableName != "undefined" && privilege.tableName != null ? privilege.tableName : "");
  self.URI = ko.observable(typeof privilege.URI != "undefined" && privilege.URI != null ? privilege.URI : "");
  self.action = ko.observable(typeof privilege.action != "undefined" && privilege.action != null ? privilege.action : "");

  self.status = ko.observable(typeof privilege.status != "undefined" && privilege.status != null ? privilege.status : "");
  self.edition = ko.observable(typeof privilege.edition != "undefined" && privilege.edition != null ? privilege.edition : false);

  self.availablePrivileges = ko.observableArray(['SERVER', 'DATABASE', 'TABLE']);
  self.availableActions = ko.observableArray(['SELECT', 'INSERT', 'ALL', '']);
  
  self.remove = function(privilege) {
	privilege.status('deleted');
  }
}

var Role = function(vm, role) {
  var self = this;

  self.name = ko.observable(typeof role.name != "undefined" && role.name != null ? role.name : "");
  self.grantorPrincipal = ko.observable(typeof role.grantorPrincipal != "undefined" && role.grantorPrincipal != null ? role.grantorPrincipal : "");
  self.groups = ko.observableArray();
  $.each(typeof role.groups != "undefined" && role.groups != null ? role.groups : [], function(index, group) {
	self.groups.push(group);
  });
  self.privileges = ko.observableArray(); // Not included in the API
  self.showPrivileges = ko.observable(false);

  self.privilegesChanged = ko.computed(function () {
    return $.grep(self.privileges(), function (privilege) {
      return ['new', 'deleted', 'modified'].indexOf(privilege.status()) != -1;
    });
  });  

  self.reset = function() {
	self.name('');
    self.groups.removeAll();
    self.privileges.removeAll();
  }

  self.addGroup = function() {
    self.groups.push('');
  }

  self.addPrivilege = function() {
	self.privileges.push(new Privilege(vm, {'serverName': vm.assist.server(), 'status': 'new', 'edition': true}));
  }

  self.create = function() {
	$(".jHueNotify").hide();
    $.post("/security/api/hive/create_role", {
        role: ko.mapping.toJSON(self)
      }, function (data) {
        if (data.status == 0) {
          $(document).trigger("info", data.message);
          vm.roles.unshift(new Role(vm, data.role));
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

  self.savePrivileges = function(role) {
	$(".jHueNotify").hide();
    $.post("/security/api/hive/save_privileges", {
        role: ko.mapping.toJSON(role)
      }, function (data) {
        if (data.status == 0) {
          vm.list_sentry_privileges_by_role(role); // Refresh all role privileges
        } else {
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
  self.path.subscribe(function() {
	self.fetchDatabases();
  });
  self.server = ko.observable('server1');
  self.db = ko.computed(function() {
    return self.path().split(/[.]/)[0];
  });
  self.table = ko.computed(function() {
    return self.path().split(/[.]/)[1];
  });
  self.files = ko.observableArray();
  self.privilege = ko.observable();

  self.fetchDatabases = function() {
	var path = self.path().replace('.', '/');

    var request = {
      url: '/beeswax/api/autocomplete/' + path,
      dataType: 'json',
      type: 'GET',
      success: function(data) {
    	if (data.databases) {
          self.files(data.databases);
    	} else if (data.tables && data.tables.length > 0) {
    	  var tables = $.map(data.tables, function(table, index) {return self.db() + '.' + table;});
    	  self.files(tables);
    	}
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
  self.role = new Role(self, {});
  self.privilege = new Privilege(self, {});

  self.doAs = ko.observable('');
  self.doAs.subscribe(function() {
	self.assist.fetchDatabases();
  });
  self.availableHadoopUsers = ko.observableArray();
  self.availableHadoopGroups = ko.observableArray();

  self.init = function() {
	self.fetchUsers();
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
    	  self.roles.push(new Role(self, item));
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
          role.privileges.push(_create_ko_privilege(item));
        });
        role.showPrivileges(true);
      }
    }).fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });
  };
  
  function _create_ko_privilege(privilege) {
	var _privilege = new Privilege(self, {
        'privilegeScope': privilege.scope,
        'serverName': privilege.server,
        'dbName': privilege.database,
        'tableName': privilege.table,
        'URI': privilege.URI,
        'action': privilege.action
    });
    _privilege.properties = ko.mapping.fromJS(privilege);
    return _privilege;
  }

  self.list_sentry_privileges_by_authorizable = function(path) {
	self.assist.path(path);
    $.ajax({
      type: "POST",
      url: "/security/api/hive/list_sentry_privileges_by_authorizable",
      data: {    	
    	groups: ko.mapping.toJSON(['sambashare', 'hadoop']),
    	roleSet: ko.mapping.toJSON({all: true, roles: []}),
        authorizableHierarchy: ko.mapping.toJSON({
            'server': self.assist.server(),
            'db': self.assist.db(),
            'table': self.assist.table(),
        }),
      },
      success: function (data) {
    	self.assist.privilege(ko.mapping.fromJS(data));
      }
    }).fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });
  };
  
  self.fetchUsers = function () {
    $.getJSON('/desktop/api/users/autocomplete', {
      
    }, function (data) {
      $.each(data.users, function (i, user) {
        self.availableHadoopUsers.push(user.username);
      });

      $.each(data.groups, function (i, group) {
        self.availableHadoopGroups.push(group.name);
      });      
    });
  }
};

function logGA(page) {
  if (typeof trackOnGA == 'function') {
    trackOnGA('security/' + page);
  }
}

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
  self.serverName.subscribe(function () {
    if (self.status() == '') {
      self.status('modified');
    }
  });
  self.dbName = ko.observable(typeof privilege.dbName != "undefined" && privilege.dbName != null ? privilege.dbName : "");
  self.dbName.subscribe(function () {
    if (self.status() == '') {
      self.status('modified');
    }
  });
  self.tableName = ko.observable(typeof privilege.tableName != "undefined" && privilege.tableName != null ? privilege.tableName : "");
  self.tableName.subscribe(function () {
    if (self.status() == '') {
      self.status('modified');
    }
  });
  self.URI = ko.observable(typeof privilege.URI != "undefined" && privilege.URI != null ? privilege.URI : "");
  self.URI.subscribe(function () {
    if (self.status() == '') {
      self.status('modified');
    }
  });
  self.action = ko.observable(typeof privilege.action != "undefined" && privilege.action != null ? privilege.action : "");
  self.action.subscribe(function () {
    if (self.status() == '') {
      self.status('modified');
    }
  });

  self.status = ko.observable(typeof privilege.status != "undefined" && privilege.status != null ? privilege.status : "");
  self.editing = ko.observable(typeof privilege.editing != "undefined" && privilege.editing != null ? privilege.editing : false);

  self.availablePrivileges = ko.observableArray(['SERVER', 'DATABASE', 'TABLE']);
  self.availableActions = ko.observableArray(['SELECT', 'INSERT', 'ALL', '']);

  self.remove = function (privilege) {
    privilege.status('deleted');
  }
}

var Role = function (vm, role) {
  var self = this;

  self.name = ko.observable(typeof role.name != "undefined" && role.name != null ? role.name : "");
  self.grantorPrincipal = ko.observable(typeof role.grantorPrincipal != "undefined" && role.grantorPrincipal != null ? role.grantorPrincipal : "");
  self.groups = ko.observableArray();
  $.each(typeof role.groups != "undefined" && role.groups != null ? role.groups : [], function (index, group) {
    self.groups.push(group);
  });
  self.privileges = ko.observableArray(); // Not included in the API
  self.originalPrivileges = ko.observableArray();
  self.showPrivileges = ko.observable(false);

  self.privilegesChanged = ko.computed(function () {
    return $.grep(self.privileges(), function (privilege) {
      return ['new', 'deleted', 'modified'].indexOf(privilege.status()) != -1;
    });
  });

  self.reset = function () {
    self.name('');
    self.groups.removeAll();
    self.privileges.removeAll();
    self.originalPrivileges.removeAll();
  }

  self.addGroup = function () {
    self.groups.push('');
  }

  self.addPrivilege = function () {
    self.privileges.push(new Privilege(vm, {'serverName': vm.assist.server(), 'status': 'new', 'editing': true}));
  }

  self.create = function () {
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

  self.remove = function (role) {
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

  self.savePrivileges = function (role) {
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

  self.compareNames = function (a, b) {
    if (a.name.toLowerCase() < b.name.toLowerCase())
      return -1;
    if (a.name.toLowerCase() > b.name.toLowerCase())
      return 1;
    return 0;
  }

  self.path = ko.observable('');
  self.path.subscribe(function () {
    self.fetchHivePath();
  });
  self.server = ko.observable('');
  self.db = ko.computed(function () {
    return self.path().split(/[.]/)[0];
  });
  self.table = ko.computed(function () {
    return self.path().split(/[.]/)[1];
  });
  self.privileges = ko.observableArray();
  self.isDiffMode = ko.observable(false);

  self.isDiffMode = ko.observable(false);
  self.isDiffMode.subscribe(function () {
    //self.refreshTree();
  });

  self.isLoadingTree = ko.observable(false);

  self.treeAdditionalData = {};
  self.treeData = ko.observable({nodes: []});
  self.loadData = function (data) {
    self.treeData(new TreeNodeModel(data));
  };

  self.initialGrowingTree = {
    path: "__HUEROOT__",
    name: "__HUEROOT__",
    selected: false,
    nodes: []
  };

  self.growingTree = ko.observable(jQuery.extend(true, {}, self.initialGrowingTree));

  self.addDatabases = function (databases) {
    var _tree = self.growingTree();
    databases.forEach(function (db) {
      var _mainFound = false;
      _tree.nodes.forEach(function (node) {
        if (node.path == db) {
          _mainFound = true;
        }
      });
      if (!_mainFound) {
        var _item = {
          path: db,
          name: db,
          isDb: true,
          isTable: false,
          isColumn: false,
          isExpanded: false,
          nodes: []
        };
        _tree.nodes.push(_item);
      }
    });
    self.loadData(self.growingTree());
  }

  self.addTables = function (tables) {
    var _branch = self.growingTree();
    _branch.nodes.forEach(function (node) {
      if (node.path == self.path()) {
        _branch = node;
      }
    });

    tables.forEach(function (table) {
      var _mainFound = false;
      var _path = self.path() + "." + table;
      _branch.nodes.forEach(function (node) {
        if (node.path == _path) {
          _mainFound = true;
        }
      });
      if (!_mainFound) {
        var _item = {
          path: _path,
          name: table,
          isDb: false,
          isTable: true,
          isColumn: false,
          isExpanded: false,
          nodes: []
        };
        _branch.nodes.push(_item);
      }
    });
    self.loadData(self.growingTree());
  }

  self.addColumns = function (columns) {
    var _branch = self.growingTree();
    _branch.nodes.forEach(function (node) {
      if (node.path == self.path().split(".")[0]) {

        node.nodes.forEach(function (inode) {
          if (inode.path == self.path()) {
            _branch = inode;
          }
        });

      }
    });

    columns.forEach(function (column) {
      var _mainFound = false;
      var _path = self.path() + "." + column;
      _branch.nodes.forEach(function (node) {
        if (node.path == _path) {
          _mainFound = true;
        }
      });
      if (!_mainFound) {
        var _item = {
          path: _path,
          name: column,
          isDb: false,
          isTable: false,
          isColumn: true,
          isExpanded: false,
          nodes: []
        };
        _branch.nodes.push(_item);
      }
    });
    self.loadData(self.growingTree());
  }

  self.setPath = function (obj, toggle) {
    if (self.getTreeAdditionalDataForPath(obj.path()).loaded || (!obj.isExpanded() && !self.getTreeAdditionalDataForPath(obj.path()).loaded)) {
      if (typeof toggle == "boolean" && toggle) {
        obj.isExpanded(!obj.isExpanded());
      }
      else {
        obj.isExpanded(true);
      }
      self.updatePathProperty(self.growingTree(), obj.path(), "isExpanded", obj.isExpanded());
    }
    self.path(obj.path());
  }

  self.togglePath = function (obj) {
    self.setPath(obj, true);
  }


  self.getTreeAdditionalDataForPath = function (path) {
    if (typeof self.treeAdditionalData[path] == "undefined") {
      var _add = {
        loaded: false
      }
      self.treeAdditionalData[path] = _add;
    }
    return self.treeAdditionalData[path];
  }

  self.updatePathProperty = function (leaf, path, property, value) {
    if (leaf.path == path) {
      leaf[property] = value;
    }
    if (leaf.nodes.length > 0) {
      leaf.nodes.forEach(function (node) {
        self.updatePathProperty(node, path, property, value);
      });
    }
    return leaf;
  }

  self.updateTreeProperty = function (leaf, property, value) {
    leaf[property] = value;
    if (leaf.nodes.length > 0) {
      leaf.nodes.forEach(function (node) {
        self.updateTreeProperty(node, property, value);
      });
    }
    return leaf;
  }

  self.collapseTree = function () {
    self.updateTreeProperty(self.growingTree(), "isExpanded", false);
    self.updatePathProperty(self.growingTree(), "/", "isExpanded", true);
    self.loadData(self.growingTree());
  }

  self.collapseOthers = function () {
    self.updateTreeProperty(self.growingTree(), "isExpanded", false);
    self.updatePathProperty(self.growingTree(), "/", "isExpanded", true);

    var _path = self.path();
    var _crumb = "";
    for (var i = 0; i < _path.length; i++) {
      if ((_path[i] === "/" && _crumb != "")) {
        self.updatePathProperty(self.growingTree(), _crumb, "isExpanded", true);
      }
      _crumb += _path[i];
    }

    self.updatePathProperty(self.growingTree(), _path, "isExpanded", true);

    self.loadData(self.growingTree());
  }


  self.fetchHivePath = function () {
    if (self.path().split(".").length < 3) {
      var _path = self.path().replace('.', '/');

      var request = {
        url: '/beeswax/api/autocomplete/' + _path,
        dataType: 'json',
        type: 'GET',
        success: function (data) {
          if (data.databases) {
            self.addDatabases(data.databases);
          }
          else if (data.tables && data.tables.length > 0) {
            self.addTables(data.tables);
            var tables = $.map(data.tables, function (table, index) {
              return self.db() + '.' + table;
            });
          }
          else if (data.columns && data.columns.length > 0) {
            self.addColumns(data.columns);
          }

          vm.list_sentry_privileges_by_authorizable();
        },
        cache: false
      };
      $.ajax(request).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
      });
    }
    else {
      vm.list_sentry_privileges_by_authorizable();
    }
  };

  self.afterRender = function () {
    $(document).trigger("rendered.tree");
  }
}


var HiveViewModel = function (initial) {
  var self = this;

  // Models
  self.roles = ko.observableArray();
  self.availableHadoopGroups = ko.mapping.fromJS(initial.hadoop_groups);
  self.assist = new Assist(self);

  // Editing
  self.showCreateRole = ko.observable(false);
  self.role = new Role(self, {});
  self.privilege = new Privilege(self, {});

  self.doAs = ko.observable(initial.user);
  self.doAs.subscribe(function () {
    self.assist.fetchHivePath();
  });
  self.availableHadoopUsers = ko.observableArray();
  self.availableHadoopGroups = ko.observableArray();

  self.selectableHadoopUsers = ko.computed(function () {
    var _users = ko.utils.arrayMap(self.availableHadoopUsers(), function (user) {
      return user.username;
    });
    return _users.sort();
  }, self);

  self.selectableHadoopGroups = ko.computed(function () {
    var _users = ko.utils.arrayMap(self.availableHadoopGroups(), function (group) {
      return group.name;
    });
    return _users.sort();
  }, self);

  self.init = function () {
    self.fetchUsers();
    self.list_sentry_roles_by_group();
    self.assist.fetchHivePath();
  };

  self.removeRole = function (roleName) {
    $.each(self.roles(), function (index, role) {
      if (role.name == roleName) {
        self.roles.remove(role);
        return false;
      }
    });
  };

  self.list_sentry_roles_by_group = function () {
    $.getJSON('/security/api/hive/list_sentry_roles_by_group', function (data) {
      if (typeof data.status !== "undefined" && data.status == -1) {
        $(document).trigger("error", data.message);
      }
      else {
        $.each(data.roles, function (index, item) {
          self.roles.push(new Role(self, item));
        });
      }
    }).fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });
  };

  self.list_sentry_privileges_by_role = function (role) {
    $.ajax({
      type: "POST",
      url: "/security/api/hive/list_sentry_privileges_by_role",
      data: {
        'roleName': role.name
      },
      success: function (data) {
        if (typeof data.status !== "undefined" && data.status == -1) {
          $(document).trigger("error", data.message);
        }
        else {
          role.privileges.removeAll();
          role.originalPrivileges.removeAll();
          $.each(data.sentry_privileges, function (index, item) {
              var privilege = _create_ko_privilege(item);
              role.privileges.push(privilege);
              role.originalPrivileges.push(privilege);
          });
          role.showPrivileges(true);
        }
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

  self.list_sentry_privileges_by_authorizable = function () {
    if (self.assist.path() != ""){
      $.ajax({
        type: "POST",
        url: "/security/api/hive/list_sentry_privileges_by_authorizable",
        data: {
          groups: ko.mapping.toJSON(['sambashare', 'hadoop']),
          roleSet: ko.mapping.toJSON({all: true, roles: []}),
          authorizableHierarchy: ko.mapping.toJSON({
            'server': self.assist.server(),
            'db': self.assist.db(),
            'table': self.assist.table()
          })
        },
        success: function (data) {
          self.assist.privileges.removeAll();
          $.each(data.privileges, function (index, item) {
        	self.assist.privileges.push(_create_ko_privilege(item));
          });
        }
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
      });
    }
  };

  self.fetchUsers = function () {
    $.getJSON('/desktop/api/users/autocomplete', {
      'include_myself': true,
      'extend_user': true
    }, function (data) {
      self.availableHadoopUsers(data.users);
      self.availableHadoopGroups(data.groups);
      $(document).trigger("loaded.users");
    });
  }
};

function logGA(page) {
  if (typeof trackOnGA == 'function') {
    trackOnGA('security/' + page);
  }
}

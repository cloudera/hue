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

  self.status = ko.observable(typeof privilege.status != "undefined" && privilege.status != null ? privilege.status : "");
  self.editing = ko.observable(typeof privilege.editing != "undefined" && privilege.editing != null ? privilege.editing : false);
  //self.privilegeScope = ko.observable(typeof privilege.privilegeScope != "undefined" && privilege.privilegeScope != null ? privilege.privilegeScope : "");
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

  // UI
  self.showAdvanced = ko.observable(false);
  self.path = ko.computed({
	read: function () {
	  if (self.tableName().length > 0) {
	    return self.dbName() + "." + self.tableName();
	  } else {
        return self.dbName();
	  }
	},
	write: function (value) {
	  var lastSpacePos = value.lastIndexOf(".");
	    if (lastSpacePos > 0) {
	      this.dbName(value.substring(0, lastSpacePos));
	      this.tableName(value.substring(lastSpacePos + 1));
	    } else {
	      this.dbName(value);
	      this.tableName('');
	    }
	  },
	owner: self
  });
  self.privilegeScope = ko.computed(function() {
      if (self.tableName().length > 0) {
        return 'TABLE';	
      } else if (self.dbName().length > 0) {
    	return 'DATABASE';
      } else {
    	return 'SERVER';
      }
  });  
  
  self.remove = function (privilege) {
    privilege.status('deleted');
  }
}

var Role = function (vm, role) {
  var self = this;

  self.name = ko.observable(typeof role.name != "undefined" && role.name != null ? role.name : "");
  self.selected = ko.observable(false);
  self.handleSelect = function (row, e) {
    self.selected(!self.selected());
  }
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
        $(document).trigger("created.role");
        vm.showCreateRole(false);
      } else {
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

  self.path = ko.observable("");
  self.path.subscribe(function (path) {
    //self.fetchHivePath();
    window.location.hash = path;
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

  self.addDatabases = function (path, databases, skipLoading) {
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
    if (typeof skipLoading == "undefined" || !skipLoading){
      self.loadData(self.growingTree());
    }
  }

  self.addTables = function (path, tables, skipLoading) {
    var _branch = self.growingTree();
    _branch.nodes.forEach(function (node) {
      if (node.path == path) {
        _branch = node;
      }
    });

    tables.forEach(function (table) {
      var _mainFound = false;
      var _path = path + "." + table;
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
    if (typeof skipLoading == "undefined" || !skipLoading){
      self.loadData(self.growingTree());
    }
  }

  self.addColumns = function (path, columns, skipLoading) {
    var _branch = self.growingTree();
    _branch.nodes.forEach(function (node) {
      if (node.path == path.split(".")[0]) {

        node.nodes.forEach(function (inode) {
          if (inode.path == path) {
            _branch = inode;
          }
        });

      }
    });

    columns.forEach(function (column) {
      var _mainFound = false;
      var _path = path + "." + column;
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
    if (typeof skipLoading == "undefined" || !skipLoading){
      self.loadData(self.growingTree());
    }
  }

  self.collapseTree = function () {
    self.updateTreeProperty(self.growingTree(), "isExpanded", false);
    self.updatePathProperty(self.growingTree(), "__HUEROOT__", "isExpanded", true);
    self.loadData(self.growingTree());
  }

  self.collapseOthers = function () {
    self.updateTreeProperty(self.growingTree(), "isExpanded", false);
    self.updatePathProperty(self.growingTree(), "__HUEROOT__", "isExpanded", true);

    var _path = self.path();
    var _crumb = "";
    for (var i = 0; i < _path.length; i++) {
      if ((_path[i] === "." && _crumb != "")) {
        self.updatePathProperty(self.growingTree(), _crumb, "isExpanded", true);
      }
      _crumb += _path[i];
    }

    self.updatePathProperty(self.growingTree(), _path, "isExpanded", true);

    self.loadData(self.growingTree());
  }

  self.expandTree = function () {
    self.updateTreeProperty(self.growingTree(), "isExpanded", true);
    self.loadData(self.growingTree());
  }

  self.refreshTree = function (force) {
    self.growingTree(jQuery.extend(true, {}, self.initialGrowingTree));
    // load root first
    self.fetchHivePath("", function(){
      Object.keys(self.treeAdditionalData).forEach(function (path) {
        if (path.indexOf(".") == -1 && path != ""){
          if (typeof force == "boolean" && force) {
            self.fetchHivePath(path);
          }
          else {
            if (self.treeAdditionalData[path].loaded) {
              self.fetchHivePath(path, function(){
                Object.keys(self.treeAdditionalData).forEach(function (ipath) {
                  if (ipath.split(".").length == 2 && ipath.split(".")[0] == path){
                    self.fetchHivePath(ipath, function(){
                      self.updateTreeProperty(self.growingTree(), "isExpanded", true);
                    });
                  }
                });
              });
            }
          }
        }
      });
    });

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
    self.fetchHivePath();
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

  self.loadParents = function (callback) {
    self.fetchHivePath("", function(){
      self.updatePathProperty(self.growingTree(), "", "isExpanded", true);
      var _crumbs = self.path().split(".");
      self.fetchHivePath(_crumbs[0], function(){
        self.updatePathProperty(self.growingTree(), _crumbs[0], "isExpanded", true);
        if (_crumbs.length > 1){
          self.fetchHivePath(_crumbs[0] + "." + _crumbs[1], function(){
            self.updatePathProperty(self.growingTree(), _crumbs[0] + "." + _crumbs[1], "isExpanded", true);
            self.loadData(self.growingTree());
            if (typeof callback != "undefined"){
              callback();
            }
            else {
              self.collapseOthers();
              vm.list_sentry_privileges_by_authorizable();
            }
          });
        }
        else {
          self.loadData(self.growingTree());
          if (typeof callback != "undefined"){
            callback();
          }
          else {
            self.collapseOthers();
            vm.list_sentry_privileges_by_authorizable();
          }
        }
      });
    });
  }

  self.fetchHivePath = function (optionalPath, loadCallback) {
    var _originalPath = typeof optionalPath != "undefined" ? optionalPath : self.path();
    if (_originalPath.split(".").length < 3) {
      var _path = _originalPath.replace('.', '/');

      var request = {
        url: '/beeswax/api/autocomplete/' + _path,
        dataType: 'json',
        type: 'GET',
        success: function (data) {
          var _hasCallback = typeof loadCallback != "undefined";

          //self.getTreeAdditionalDataForPath(self.path()).loaded = true;
          self.getTreeAdditionalDataForPath(_originalPath).loaded = true;

          if (data.databases) {
            self.addDatabases(_originalPath, data.databases, _hasCallback);
          }
          else if (data.tables && data.tables.length > 0) {
            self.addTables(_originalPath, data.tables, _hasCallback);
          }
          else if (data.columns && data.columns.length > 0) {
            self.addColumns(_originalPath, data.columns, _hasCallback);
          }


          if (_hasCallback){
            loadCallback(data);
          }
          else {
            vm.list_sentry_privileges_by_authorizable();
          }
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

  self.availablePrivileges = ko.observableArray(['SERVER', 'DATABASE', 'TABLE']);
  self.availableActions = ko.observableArray(['SELECT', 'INSERT', 'ALL', '']);

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


  self.selectAllRoles = function () {
    self.allRolesSelected(!self.allRolesSelected());
    ko.utils.arrayForEach(self.roles(), function (role) {
      role.selected(self.allRolesSelected());
    });
    return true;
  };

  self.allRolesSelected = ko.observable(false);

  self.selectedRoles = ko.computed(function () {
    return ko.utils.arrayFilter(self.roles(), function (role) {
      return role.selected();
    });
  }, self);

  self.selectedRole = ko.computed(function () {
    return self.selectedRoles()[0];
  }, self);

  self.deleteSelectedRoles = function () {
    ko.utils.arrayForEach(self.selectedRoles(), function (role) {
      role.remove(role);
    });
  };

  self.expandSelectedRoles = function () {
    if (self.selectedRoles().length == 0){
      self.selectAllRoles();
    }
    ko.utils.arrayForEach(self.selectedRoles(), function (role) {
      self.list_sentry_privileges_by_role(role)
    });
  };

  self.init = function (path) {
    self.fetchUsers();
    self.assist.path(path);
    self.list_sentry_roles_by_group();

    if (path != ""){
      self.assist.loadParents();
    }
    else {
      self.assist.fetchHivePath();
    }

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

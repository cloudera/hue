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


function s4() {
  return Math.floor((1 + Math.random()) * 0x10000)
      .toString(16)
      .substring(1);
}

function UUID() {
  return s4() + s4() + '-' + s4() + '-' + s4() + '-' + s4() + '-' + s4() + s4() + s4();
}


var Privilege = function (vm, privilege) {
  var self = this;

  self.id = ko.observable(typeof privilege.id != "undefined" && privilege.id != null ? privilege.id : "");
  self.roleName = ko.observable(typeof privilege.roleName != "undefined" && privilege.roleName != null ? privilege.roleName : "");
  self.status = ko.observable(typeof privilege.status != "undefined" && privilege.status != null ? privilege.status : "");
  self.editing = ko.observable(typeof privilege.editing != "undefined" && privilege.editing != null ? privilege.editing : false);
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
  self.action = ko.observable(typeof privilege.action != "undefined" && privilege.action != null ? privilege.action : 'SELECT');
  self.action.subscribe(function () {
    if (self.status() == '') {
      self.status('modified');
    }
  });
  self.timestamp = ko.observable(typeof privilege.timestamp != "undefined" && privilege.timestamp != null ? privilege.timestamp : 0);
  self.grantor = ko.observable(typeof privilege.grantor != "undefined" && privilege.grantor != null ? privilege.grantor : "");

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
	if (privilege.status() == 'new') {
	  privilege.status('alreadydeleted');
	} else {
      privilege.status('deleted');
	}
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
  self.originalGroups = ko.observableArray();
  $.each(typeof role.groups != "undefined" && role.groups != null ? role.groups : [], function (index, group) {
    self.groups.push(group);
    self.originalGroups.push(group);
  });
  self.privileges = ko.observableArray(); // Not included in the API
  self.originalPrivileges = ko.observableArray();
  self.showPrivileges = ko.observable(false);
  self.showEditGroups = ko.observable(false);

  self.privilegesChanged = ko.computed(function () {
    return $.grep(self.privileges(), function (privilege) {
      return ['new', 'deleted', 'modified'].indexOf(privilege.status()) != -1;
    });
  });

  self.groupsChanged = ko.computed(function () {
	return ! ($(self.groups()).not(self.originalGroups()).length == 0 && $(self.originalGroups()).not(self.groups()).length == 0);
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
	if (vm.getSectionHash() == 'edit') {
      self.privileges.push(new Privilege(vm, {'serverName': vm.assist.server(), 'status': 'new', 'editing': true, 'dbName': vm.assist.db(), 'tableName': vm.assist.table()}));
	} else {
      self.privileges.push(new Privilege(vm, {'serverName': vm.assist.server(), 'status': 'new', 'editing': true}));
	}
  }
  
  self.resetGroups = function () {
	self.groups.removeAll();
	$.each(self.originalGroups(), function (index, group) {
	  self.groups.push(group);
	});
  }
  
  self.saveGroups = function() {
    $(".jHueNotify").hide();
    $.post("/security/api/hive/update_role_groups", {
    	role: ko.mapping.toJSON(self)
    }, function (data) {
      if (data.status == 0) {
        self.showEditGroups(false);
    	self.originalGroups.removeAll();
    	$.each(self.groups(), function (index, group) {
    	  self.originalGroups.push(group);
    	});        
      } else {
        $(document).trigger("error", data.message);
      }
    }).fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
	});
  }

  self.create = function () {
    $(".jHueNotify").hide();
    $.post("/security/api/hive/create_role", {
      role: ko.mapping.toJSON(self)
    }, function (data) {
      if (data.status == 0) {
        $(document).trigger("info", data.message);
        vm.showCreateRole(false);
        self.reset();
        $(document).trigger("created.role");
        var role = new Role(vm, data.role);
        vm.roles.unshift(role);
        vm.list_sentry_privileges_by_role(role); // Show privileges        
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
        vm.removeRole(role.name);
      } else {
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
    	vm.list_sentry_privileges_by_authorizable();
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
    vm.updatePathHash(path);
  });
  self.server = ko.observable('server1');
  self.db = ko.computed(function () {
    return self.path().split(/[.]/)[0];
  });
  self.table = ko.computed(function () {
    return self.path().split(/[.]/)[1];
  });
  self.privileges = ko.observableArray();
  self.roles = ko.observableArray();
  self.isDiffMode = ko.observable(false);

  self.isDiffMode = ko.observable(false);
  self.isDiffMode.subscribe(function () {
    self.refreshTree();
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
      if (! _mainFound) {
        var _item = {
          path: db,
          name: db,
          isDb: true,
          isTable: false,
          isColumn: false,
          isExpanded: false,
          isChecked: false,
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
          isChecked: false,
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
          isChecked: false,
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
        if (path.indexOf(".") == -1 && path != "") {
          if (typeof force == "boolean" && force) {
            self.fetchHivePath(path);
          }
          else {
            if (self.treeAdditionalData[path].loaded) {
              self.fetchHivePath(path, function(){
                Object.keys(self.treeAdditionalData).forEach(function (ipath) {
                  if (ipath.split(".").length == 2 && ipath.split(".")[0] == path){
                    self.fetchHivePath(ipath, function() {
                      self.updateTreeProperty(self.growingTree(), "isExpanded", true);
                      self.loadData(self.growingTree());
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
      self.updatePathProperty(self.growingTree(), obj.path(), "isExpanded", obj.isExpanded());
    }
    else {
      if (typeof toggle == "boolean" && toggle){
        obj.isExpanded(!obj.isExpanded());
      } else {
        obj.isExpanded(false);
      }
      self.updatePathProperty(self.growingTree(), obj.path(), "isExpanded", obj.isExpanded());
    }
    self.path(obj.path());
    $(document).trigger("changed.path");
    self.fetchHivePath();
  }

  self.togglePath = function (obj) {
    self.setPath(obj, true);
  }

  self.checkPath = function (obj) {
    obj.isChecked(!obj.isChecked());
    self.updatePathProperty(self.growingTree(), obj.path(), "isChecked", obj.isChecked());
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

  self.getCheckedItems = function (leaf, checked) {
    if (leaf == null){
      leaf = self.growingTree();
    }
    if (checked == null){
      checked = []
    }
    if (leaf.isChecked){
      checked.push(leaf);
    }
    if (leaf.nodes.length > 0) {
      leaf.nodes.forEach(function (node) {
        self.getCheckedItems(node, checked);
      });
    }
    return checked;
  }

  self.loadParents = function (callback) {
    self.fetchHivePath("", function(){
      self.updatePathProperty(self.growingTree(), "", "isExpanded", true);
      var _crumbs = self.path().split(".");
      self.fetchHivePath(_crumbs[0], function() {
        self.updatePathProperty(self.growingTree(), _crumbs[0], "isExpanded", true);
        if (_crumbs.length > 1){
          self.fetchHivePath(_crumbs[0] + "." + _crumbs[1], function(){
            self.updatePathProperty(self.growingTree(), _crumbs[0] + "." + _crumbs[1], "isExpanded", true);
            self.loadData(self.growingTree());
            if (typeof callback != "undefined") {
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
          if (typeof callback != "undefined") {
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

          self.getTreeAdditionalDataForPath(_originalPath).loaded = true;

          if (data.databases) {
            self.addDatabases(_originalPath, data.databases, _hasCallback);
          } else if (data.tables && data.tables.length > 0) {
            self.addTables(_originalPath, data.tables, _hasCallback);
          } else if (data.columns && data.columns.length > 0) {
            self.addColumns(_originalPath, data.columns, _hasCallback);
          }

          if (_hasCallback) {
            loadCallback(data);
          } else {
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
  self.availableActions = ko.observableArray(['SELECT', 'INSERT', 'ALL']);

  // Models
  self.roles = ko.observableArray();
  self.roleFilter = ko.observable("");
  self.filteredRoles = ko.computed(function () {
    var _filter = self.roleFilter().toLowerCase();
    if (! _filter) {
      return self.roles();
    } else {
      return ko.utils.arrayFilter(self.roles(), function (role) {
        var _inGroups = false;
        role.groups().forEach(function (group) {
          if (group.toLowerCase().indexOf(_filter) > -1) {
            _inGroups = true;
          }
        });
        var _inPrivileges = false;
        role.privileges().forEach(function (priv) {
          if (priv.dbName().toLowerCase().indexOf(_filter) > -1 || priv.tableName().toLowerCase().indexOf(_filter) > -1) {
            _inPrivileges = true;
          }
        });
        return role.name().toLowerCase().indexOf(_filter) > -1 || role.grantorPrincipal().toLowerCase().indexOf(_filter) > -1 || _inGroups || _inPrivileges;
      });
    }
  }, self);

  self.availableHadoopGroups = ko.observableArray();
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
    var _groups = ko.utils.arrayMap(self.availableHadoopGroups(), function (group) {
      return group.name;
    });
    _groups.push("");
    return _groups.sort();
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
    $(document).trigger("deleted.role");
  };

  self.expandSelectedRoles = function () {
    ko.utils.arrayForEach(self.selectedRoles(), function (role) {
      if (! role.showPrivileges()) { 
        self.list_sentry_privileges_by_role(role);
      }
    });
  };

  self.init = function (path) {
    self.fetchUsers();
    self.assist.path(path);
    self.list_sentry_roles_by_group();

    if (path != "") {
      self.assist.loadParents();
    } else {
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
    $.ajax({
      type: "POST",
      url: "/security/api/hive/list_sentry_roles_by_group",
      data: {
        'groupName': $('#selectedGroup').val()
      },
      success: function (data) {
        if (typeof data.status !== "undefined" && data.status == -1) {
          $(document).trigger("error", data.message);
        } 
        else {
          self.roles.removeAll();
          $.each(data.roles, function (index, item) {
            self.roles.push(new Role(self, item));
          });
        }
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
            var privilegeCopy = _create_ko_privilege(item);
            privilegeCopy.id(privilege.id());
            role.privileges.push(privilege);
            role.originalPrivileges.push(privilegeCopy);
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
      'action': privilege.action,
      'timestamp': privilege.timestamp,
      'roleName': privilege.roleName,
      'id': UUID()
    });
    return _privilege;
  }

  function _create_authorizable_from_ko(privilege) {
    return {
      'server': self.assist.server(),
      'db': self.assist.db(),
      'table': self.assist.table()
    }
  }
  
  self.list_sentry_privileges_by_authorizable = function () {
    if (self.assist.path() != "") {
      $.ajax({
        type: "POST",
        url: "/security/api/hive/list_sentry_privileges_by_authorizable",
        data: {
          groupName: $('#selectedGroup').val(),
          roleSet: ko.mapping.toJSON({all: true, roles: []}),
          authorizableHierarchy: ko.mapping.toJSON(_create_authorizable_from_ko())
        },
        success: function (data) {
          self.assist.roles.removeAll();
          self.assist.privileges.removeAll();
          $.each(data.privileges, function (index, item) {
            var _role = null;
            self.assist.roles().forEach(function(role){
              if (role.name() == item.roleName){
                _role = role;
              }
            });
            if (_role == null){
              var _idx = self.assist.roles.push(new Role(self, { name: item.roleName }));
              _role = self.assist.roles()[_idx - 1];
            }
            _role.privileges.push(_create_ko_privilege(item));
        	self.assist.privileges.push(_create_ko_privilege(item));
          });
        }
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
      });
    }
  };

  self.bulk_delete_privileges = function (role) {
    $(".jHueNotify").hide();
    var checkedPaths = self.assist.getCheckedItems();
    $.post("/security/api/hive/bulk_delete_privileges", {
      'authorizableHierarchy': ko.mapping.toJSON(_create_authorizable_from_ko()),
      'checkedPaths': ko.mapping.toJSON(checkedPaths),
    }, function (data) {
      if (data.status == 0) {
        self.list_sentry_privileges_by_authorizable(); // Refresh
      } else {
        $(document).trigger("error", data.message);
      }
    }).fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });
  }  

  self.bulk_add_privileges = function (role) {
    $(".jHueNotify").hide();
    var checkedPaths = self.assist.getCheckedItems();
    $.post("/security/api/hive/bulk_add_privileges", {
      'privileges': ko.mapping.toJSON(self.assist.privileges),
      'authorizableHierarchy': ko.mapping.toJSON(_create_authorizable_from_ko()),
      'checkedPaths': ko.mapping.toJSON(checkedPaths),
    }, function (data) {
      if (data.status == 0) {
        self.list_sentry_privileges_by_authorizable(); // Refresh
      } else {
        $(document).trigger("error", data.message);
      }
    }).fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });
  } 
  
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

  self.updatePathHash = function (path) {
    var _hash = window.location.hash;
    if (_hash.indexOf("@") == -1){
      window.location.hash = path;
    }
    else {
      window.location.hash = path + "@" + _hash.split("@")[1];
    }
  }

  self.updateSectionHash = function (section) {
    var _hash = window.location.hash;
    if (_hash == ""){
      window.location.hash = "@" + section;
    }
    if (_hash.indexOf("@") == -1){
      window.location.hash = _hash + "@" + section;
    }
    else {
      window.location.hash = _hash.split("@")[0] + "@" + section;
    }
  }

  self.getPathHash = function () {
    if (window.location.hash != "") {
      var _hash = window.location.hash.substr(1);
      if (_hash.indexOf("@") > -1){
        return _hash.split("@")[0];
      }
      else {
        return _hash;
      }
    }
    return "";
  }

  self.getSectionHash = function () {
    if (window.location.hash != "") {
      var _hash = window.location.hash.substr(1);
      if (_hash.indexOf("@") > -1){
        return _hash.split("@")[1];
      }
    }
    return "edit";
  }
};

function logGA(page) {
  if (typeof trackOnGA == 'function') {
    trackOnGA('security/' + page);
  }
}

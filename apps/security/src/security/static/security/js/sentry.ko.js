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

var SentryViewModel = (function () {

  var Authorizable = function (vm, privilege, authorizable) {
    var self = this;

    self.type = ko.observable(typeof authorizable.type != "undefined" && authorizable.type != null ? authorizable.type : "");
    self.type.subscribe(function () {
      if (privilege.status() == '') {
        privilege.status('modified');
      }
    });
    self.name_ = ko.observable(typeof authorizable.name != "undefined" && authorizable.name != null ? authorizable.name : "");
    self.name_.subscribe(function () {
      if (privilege.status() == '') {
        privilege.status('modified');
      }
    });
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
    self.component = ko.observable(typeof privilege.component != "undefined" && privilege.component != null ? privilege.component : vm.component());
    self.authorizables = ko.observableArray();
    if (typeof privilege.authorizables != "undefined" && privilege.authorizables != null) {
      self.authorizables(
        $.map(privilege.authorizables, function(authorizable) {
          return new Authorizable(vm, privilege, authorizable);
        })
      )
    };
    self.authorizables.subscribe(function () {
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
    self.grantorPrincipal = ko.observable(typeof privilege.grantorPrincipal != "undefined" && privilege.grantorPrincipal != null ? privilege.grantorPrincipal : vm.user());
    self.grantOption = ko.observable(typeof privilege.grantOption != "undefined" && privilege.grantOption != null ? privilege.grantOption : false);
    self.grantOption.subscribe(function () {
      if (self.status() == '') {
        self.status('modified');
      }
    });

    // UI
    self.privilegeType = ko.computed(function() {
      var last = self.authorizables().slice(-1)[0];
      return last ? last.type().toUpperCase() : 'SERVER';
    });
    self.showAdvanced = ko.observable(false);
    self.path = ko.computed({
      read: function () {
        if (vm.component() == 'solr') {
          return $.map(self.authorizables(), function (authorizable) {
            if (authorizable.name_() !== '') {
              if (authorizable.type() === 'COLLECTION') {
                return 'collections.' + authorizable.name_();
              }
              else {
                return 'configs.' + authorizable.name_();
              }
            }
          }).join("");
        }
        else {
          return $.map(self.authorizables(), function (authorizable) {
            if (authorizable.name_() !== '') {
              return authorizable.name_();
            }
          }).join(".");
        }
      },
      write: function (value) {
        var _parts = value.split(".");

        self.authorizables.removeAll();

        if (vm.component() == 'solr') {
          if (_parts[0] == 'collections') {
            self.authorizables.push(new Authorizable(vm, self, {type: 'COLLECTION', name: _parts[1]}))
          }
          else if (_parts[0] == 'configs') {
            self.authorizables.push(new Authorizable(vm, self, {type: 'CONFIG', name: _parts[1]}))
          }
          else if (_parts[0] == 'admin') {
            self.authorizables.push(new Authorizable(vm, self, {type: 'ADMIN', name: _parts[1]}))
          }
        } else {
          self.authorizables.push(new Authorizable(vm, self, {type: 'DATABASE', name: _parts[0]}))
          if (_parts.length > 1) {
            self.authorizables.push(new Authorizable(vm, self, {type: 'TABLE', name: _parts[1]}))
          }
          if (_parts.length > 2) {
            self.authorizables.push(new Authorizable(vm, self, {type: 'COLUMN', name: _parts[2]}))
          }
        }
      },
      owner: self
    });

    self.indexerPath = ko.computed(function () {
      if (self.authorizables().length > 0 && self.authorizables()[0].type() == 'COLLECTION') {
        return '/indexer/#edit/' + self.authorizables()[0].name_();
      }
      else {
        return '/indexer/#manage';
      }
    });

    self.metastorePath = ko.computed(function() {
      var path = '';

      if (self.authorizables()[0] && self.authorizables()[0]['type'] == 'DATABASE') {
        path = '/metastore/tables/' + self.authorizables()[0];
      }
      if (self.authorizables()[1] && self.authorizables()[1]['type'] == 'TABLE') {
        path +=  "/" + self.authorizables()[1];
      }
      if (self.authorizables()[2] && self.authorizables()[2]['type'] == 'COLUMN') {
        path +=  "#col=" + self.authorizables()[2];
      }

      return path;
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
    self.name.subscribe(function (value){
      var _found = false;
      vm.role().isEditing(false);
      ko.utils.arrayForEach(vm.roles(), function (role) {
        if (role.name() == value){
          vm.role(role);
          _found = true;
        }
      });
      if (_found) {
        vm.role().isEditing(true);
        vm.list_sentry_privileges_by_role(vm.role());
        $(document).trigger("destroyTypeahead");
      }
    });
    self.selected = ko.observable(false);
    self.handleSelect = function (row, e) {
      self.selected(!self.selected());
    }

    self.groups = ko.observableArray();
    self.originalGroups = ko.observableArray();
    self.groups.extend({ rateLimit: 300 });
    self.originalGroups.extend({ rateLimit: 300 });
    $.each(typeof role.groups != "undefined" && role.groups != null ? role.groups : [], function (index, group) {
      self.groups.push(group);
      self.originalGroups.push(group);
    });
    self.privileges = ko.observableArray(); // Not included in the API
    self.privilegesForViewTo = ko.observable(49);
    self.originalPrivileges = ko.observableArray();
    self.showPrivileges = ko.observable(false);
    self.showPrivileges.subscribe(function (value) {
      var _expanded = vm.expandedRoles();
      if (value) {
        if (_expanded.indexOf(self.name()) == -1) {
          _expanded.push(self.name());
        }
      }
      else {
        if (_expanded.indexOf(self.name()) > -1) {
          _expanded.splice(_expanded.indexOf(self.name()), 1);
        }
      }
      vm.expandedRoles(_expanded);
    });

    self.showEditGroups = ko.observable(false);
    self.isEditing = ko.observable(false);
    self.isValid = ko.computed(function () {
      return self.name().length > 0 && $.grep(self.privileges(), function (privilege) {
        return privilege.path() === '';
      }).length === 0;
    });

    self.privilegesChanged = ko.computed(function () {
      return $.grep(self.privileges(), function (privilege) {
        return ['new', 'deleted', 'modified'].indexOf(privilege.status()) != -1;
      });
    });

    self.groupsChanged = ko.computed(function () {
      return !($(self.groups()).not(self.originalGroups()).length == 0 && $(self.originalGroups()).not(self.groups()).length == 0);
    });
    self.groupsChanged.extend({ rateLimit: 300 });

    self.privilegesForView = ko.computed(function() {
      var _filter = vm.privilegeFilter().toLowerCase();
      if (_filter == "") {
        return self.privileges().slice(0, self.privilegesForViewTo());
      }
      else {
        var _filtered = ko.utils.arrayFilter(self.privileges(), function (priv) {
          return $.grep(priv.authorizables(), function(auth) {
              return auth.name_().toLowerCase().indexOf(_filter) > -1;
          }).length > 0 ||
          priv.action().toLowerCase().indexOf(_filter) > -1;
        });
        return _filtered.slice(0, self.privilegesForViewTo());
      }
    });

    self.reset = function () {
      self.name('');
      self.groups.removeAll();
      self.privileges.removeAll();
      self.originalPrivileges.removeAll();
      self.isEditing(false);
    }

    self.addGroup = function () {
      self.groups.push('');
    }

    self.addPrivilege = function () {
      var privilege = new Privilege(vm, {'serverName': vm.assist.server(), 'status': 'new', 'editing': true});
      if (vm.assist.path() && vm.getSectionHash() == 'edit') {
        privilege.path(vm.assist.path());
      }
      self.privileges.push(privilege);
    }

    self.resetGroups = function () {
      self.groups.removeAll();
      $.each(self.originalGroups(), function (index, group) {
        self.groups.push(group);
      });
    }

    self.saveGroups = function () {
      $(".jHueNotify").remove();
      $.post("/security/api/sentry/update_role_groups", {
        role: ko.mapping.toJSON(self),
        component: vm.component()
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
      $(".jHueNotify").remove();
      if (self.isValid()) {
        $.post("/security/api/sentry/create_role", {
          role: ko.mapping.toJSON(self),
          component: vm.component()
        }, function (data) {
          if (data.status == 0) {
            $(document).trigger("info", data.message);
            vm.showCreateRole(false);
            self.reset();
            var role = new Role(vm, data.role);
            role.showPrivileges(true);
            vm.originalRoles.unshift(role);
            vm.list_sentry_privileges_by_authorizable();
            $(document).trigger("createdRole");
          } else {
            $(document).trigger("error", data.message);
          }
        }).fail(function (xhr, textStatus, errorThrown) {
          $(document).trigger("error", xhr.responseText);
        });
      }
    }

    self.update = function () {
      $(".jHueNotify").remove();
      if (self.isValid()) {
        $.post("/security/api/sentry/save_privileges", {
          role: ko.mapping.toJSON(self),
          component: vm.component()
        }, function (data) {
          if (data.status == 0) {
            $(document).trigger("info", data.message);
            vm.showCreateRole(false);
            vm.list_sentry_privileges_by_authorizable();
            $(document).trigger("createdRole");
          } else {
            $(document).trigger("error", data.message);
          }
        }).fail(function (xhr, textStatus, errorThrown) {
          $(document).trigger("error", xhr.responseText);
        });
      }
    }

    self.remove = function (role) {
      $(".jHueNotify").remove();
      $.post("/security/api/sentry/drop_sentry_role", {
        roleName: role.name,
        component: vm.component()
      }, function (data) {
        if (data.status == 0) {
          vm.removeRole(role.name());
          vm.list_sentry_privileges_by_authorizable();
          $(document).trigger("removedRole");
        } else {
          $(document).trigger("error", data.message);
        }
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
      });
    }

    self.savePrivileges = function (role) {
      $(".jHueNotify").remove();
      $.post("/security/api/sentry/save_privileges", {
        role: ko.mapping.toJSON(role),
        component: vm.component()
      }, function (data) {
        if (data.status == 0) {
          vm.list_sentry_privileges_by_authorizable();
          $(document).trigger("createdRole");
        } else {
          $(document).trigger("error", data.message);
        }
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
      });
    }
  }

  var Assist = function (vm, initial) {
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
    self.server = ko.observable(initial.sentry_provider);
    self.db = ko.computed(function () {
      var db = self.path().split(/[.]/)[0];
      return db ? db : null;
    });
    self.table = ko.computed(function () {
      var table = self.path().split(/[.]/)[1];
      return table ? table : null;
    });
    self.column = ko.computed(function () {
      var column = self.path().split(/[.]/)[2];
      return column ? column : null;
    });
    self.indexerPath = ko.computed(function () {
      if (self.table()) {
        return '/indexer/#edit/' + self.table();
      }
      else {
        return '/indexer/#manage';
      }
    });
    self.metastorePath = ko.computed(function(){
      if (self.column()) {
        return '/metastore/table/' + self.db() + "/" + self.table() + "#col=" + self.column();
      } else if (self.table()) {
        return '/metastore/table/' + self.db() + "/" + self.table();
      } else if (self.db()) {
        return '/metastore/tables/' + self.db();
      } else {
        return '/metastore/databases';
      }
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
      nodes: [{
          path: "",
          name: self.server(),
          withPrivileges: false,
          isServer: true,
          isDb: false,
          isTable: false,
          isColumn: false,
          isExpanded: true,
          isLoaded: true,
          isChecked: false,
          nodes: []
      }]
    };

    self.growingTree = ko.observable(jQuery.extend(true, {}, self.initialGrowingTree));

    self.checkedItems = ko.observableArray([]);

    self.addDatabases = function (path, databases, skipLoading) {
      var _tree = self.growingTree().nodes[0];
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
            withPrivileges: false,
            isServer: false,
            isDb: true,
            isTable: false,
            isColumn: false,
            isExpanded: false,
            isLoaded: false,
            isChecked: false,
            nodes: []
          };
          _tree.nodes.push(_item);
        }
      });
      if (typeof skipLoading == "undefined" || !skipLoading) {
        self.loadData(self.growingTree());
      }
    }

    self.addTables = function (path, tablesMeta, skipLoading) {
      var _branch = self.growingTree().nodes[0];
      _branch.nodes.forEach(function (node) {
        if (node.path == path) {
          _branch = node;
        }
      });

      tablesMeta.forEach(function (tableMeta) {
        var _mainFound = false;
        var _path = path + "." + tableMeta.name;
        _branch.nodes.forEach(function (node) {
          if (node.path == _path) {
            _mainFound = true;
          }
        });
        if (!_mainFound) {
          var _item = {
            path: _path,
            name: tableMeta.name,
            withPrivileges: false,
            isServer: false,
            isDb: false,
            isTable: true,
            isColumn: false,
            isExpanded: false,
            isLoaded: false,
            isChecked: false,
            nodes: []
          };
          _branch.nodes.push(_item);
        }
      });
      if (typeof skipLoading == "undefined" || !skipLoading) {
        self.loadData(self.growingTree());
      }
    }

    self.addColumns = function (path, columns, skipLoading) {
      var _branch = self.growingTree().nodes[0];
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
            withPrivileges: false,
            isServer: false,
            isDb: false,
            isTable: false,
            isColumn: true,
            isExpanded: false,
            isLoaded: false,
            isChecked: false,
            nodes: []
          };
          _branch.nodes.push(_item);
        }
      });
      if (typeof skipLoading == "undefined" || !skipLoading) {
        self.loadData(self.growingTree());
      }
    }

    self.collapseTree = function () {
      self.updateTreeProperty(self.growingTree(), "isExpanded", false);
      self.updatePathProperty(self.growingTree(), "__HUEROOT__", "isExpanded", true);
      self.updatePathProperty(self.growingTree(), "", "isExpanded", true);
      self.loadData(self.growingTree());
    }

    self.collapseOthers = function () {
      self.updateTreeProperty(self.growingTree(), "isExpanded", false);
      self.updatePathProperty(self.growingTree(), "__HUEROOT__", "isExpanded", true);
      self.updatePathProperty(self.growingTree(), "", "isExpanded", true);

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
      self.fetchAuthorizablesPath("", function () {
        Object.keys(self.treeAdditionalData).forEach(function (path) {
          if (path.indexOf(".") == -1 && path != "") {
            if (typeof force == "boolean" && force) {
              self.fetchAuthorizablesPath(path);
            }
            else {
              if (self.treeAdditionalData[path].loaded) {
                self.fetchAuthorizablesPath(path, function () {
                  self.updatePathProperty(self.growingTree(), path, "isExpanded", self.treeAdditionalData[path].expanded);
                  var _withTable = false;
                  Object.keys(self.treeAdditionalData).forEach(function (ipath) {
                    if (ipath.split(".").length == 2 && ipath.split(".")[0] == path) {
                      self.fetchAuthorizablesPath(ipath, function () {
                        _withTable = true;
                        self.updatePathProperty(self.growingTree(), ipath, "isExpanded", self.treeAdditionalData[ipath].expanded);
                        self.loadData(self.growingTree());
                      });
                    }
                  });
                  if (! _withTable){
                    self.loadData(self.growingTree());
                  }
                });
              }
            }
          }
        });
      });

      vm.list_sentry_privileges_by_authorizable();
    }

    self.setPath = function (obj, toggle, skipListAuthorizable) {
      if (self.getTreeAdditionalDataForPath(obj.path()).loaded || (!obj.isExpanded() && !self.getTreeAdditionalDataForPath(obj.path()).loaded)) {
        if (typeof toggle == "boolean" && toggle) {
          obj.isExpanded(!obj.isExpanded());
          self.getTreeAdditionalDataForPath(obj.path()).expanded = obj.isExpanded();
        }
        self.updatePathProperty(self.growingTree(), obj.path(), "isExpanded", obj.isExpanded());
      }
      else {
        if (typeof toggle == "boolean" && toggle) {
          obj.isExpanded(!obj.isExpanded());
        } else {
          obj.isExpanded(false);
        }
        self.getTreeAdditionalDataForPath(obj.path()).expanded = obj.isExpanded();
        self.updatePathProperty(self.growingTree(), obj.path(), "isExpanded", obj.isExpanded());
      }

      if (vm.component() === 'solr' && obj.path() !== '' && obj.path().indexOf('.') == -1) {
        self.path(obj.path() + '.*');
      }
      else {
        self.path(obj.path());
      }
      $(document).trigger("changedPath");

      if (self.getTreeAdditionalDataForPath(obj.path()).loaded){
        if (typeof skipListAuthorizable == "undefined" || !skipListAuthorizable) {
          vm.list_sentry_privileges_by_authorizable();
        }
      }
      else {
        self.fetchAuthorizablesPath();
      }
    }

    self.togglePath = function (obj) {
      self.setPath(obj, true);
    }

    self.showAuthorizable = function (obj, e) {
      e.preventDefault();
      e.stopPropagation();
      e.stopImmediatePropagation();
      self.fetchAuthorizablesPath(obj.path(), function (data) {
        if (vm.component() === 'solr') {
          location.href = data.authorizable_link;
        }
        else {
          location.href = "/security/hdfs#" + data.hdfs_link.substring("/filebrowser/view=".length);
        }
      });
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


    self.checkPath = function (obj) {
      obj.isChecked(!obj.isChecked());
      self.updatePathProperty(self.growingTree(), obj.path(), "isChecked", obj.isChecked());
      self.checkedItems(self.getCheckedItems());
    }

    self.getTreeAdditionalDataForPath = function (path) {
      if (typeof self.treeAdditionalData[path] == "undefined") {
        var _add = {
          loaded: false,
          expanded: true
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
      self.fetchAuthorizablesPath("", function () {
        self.updatePathProperty(self.growingTree(), "", "isExpanded", true);
        var _crumbs = self.path().split(".");
        self.fetchAuthorizablesPath(_crumbs[0], function () {
          self.updatePathProperty(self.growingTree(), _crumbs[0], "isExpanded", true);
          if (_crumbs.length > 1) {
            self.fetchAuthorizablesPath(_crumbs[0] + "." + _crumbs[1], function () {
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

    self.fetchAuthorizablesPath = function (optionalPath, loadCallback) {
      var _originalPath = typeof optionalPath != "undefined" ? optionalPath : self.path();

      if (vm.component() === 'solr' && _originalPath.indexOf('.*') > -1) {
        _originalPath = _originalPath.split('.')[0];
      }

      if (_originalPath.split(".").length < 4) {
        self.isLoadingTree(true);

        var _path = _originalPath.replace('.', '/');
        var request = {
          url: '/security/api/sentry/fetch_authorizables',
          data: {
            'path': _path,
            'component': vm.component(),
            'doas': vm.doAs(),
            'isDiffMode': self.isDiffMode()
          },
          dataType: 'json',
          type: 'GET',
          success: function (data) {
            var _hasCallback = typeof loadCallback != "undefined";

            self.getTreeAdditionalDataForPath(_originalPath).loaded = true;
            self.updatePathProperty(self.growingTree(), _originalPath, "isLoaded", true);

            if (data.databases) {
              self.addDatabases(_originalPath, data.databases, _hasCallback);
              if (vm.getPathHash() == ""){
                self.setPath(self.treeData().nodes()[0], false, true);
              }
            }
            else if (data.tables_meta && data.tables_meta.length > 0) {
              self.addTables(_originalPath, data.tables_meta, _hasCallback);
            }
            else if (data.columns && data.columns.length > 0) {
              self.addColumns(_originalPath, data.columns, _hasCallback);
            }

            self.isLoadingTree(false);

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
      $(document).trigger("renderedTree");
    }
  }

  var SentryViewModel = function (initial) {
    var self = this;

    self.isLoadingRoles = ko.observable(false);
    self.isLoadingPrivileges = ko.observable(true);
    self.isApplyingBulk = ko.observable(false);

    self.availablePrivileges = ko.observableArray();
    self.availableSolrConfigActions = ko.observableArray();
    if (initial.component == 'solr') {
      self.availableActions = function () {
        return ko.observableArray(['QUERY', 'UPDATE', 'ALL']);
      }
      self.availableSolrConfigActions(['ALL']);
    } else {
      self.availableActions = function (authorizables) {
        var actions = ['SELECT', 'INSERT', 'ALL'];
        var databaseActions = ['CREATE'];
        var tableActions = ['REFRESH']; // 'ALTER', 'DROP'
        if (authorizables.length < 2) { // server and database
          actions = actions.concat(databaseActions).concat(tableActions);
        }
        else {
          actions = actions.concat(tableActions);
        }
        return ko.observableArray(actions.sort());
      }
    }


    self.privilegeFilter = ko.observable("");

    // Models
    self.component = ko.observable(initial.component);
    self.user = ko.observable(initial.user);
    self.server = ko.observable(initial.sentry_provider);
    self.roles = ko.observableArray();
    self.tempRoles = ko.observableArray();
    self.originalRoles = ko.observableArray();
    self.roleFilter = ko.observable("");
    self.filteredRoles = ko.computed(function () {
      var _filter = self.roleFilter().toLowerCase();
      if (!_filter) {
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
            var matches = $.grep(priv.authorizables(), function(auth) {
              return auth.name_().toLowerCase().indexOf(_filter) > -1;
            });
            if (matches.length > 0 || priv.action().toLowerCase().indexOf(_filter) > -1) {
              _inPrivileges = true;
            }
          });
          return role.name().toLowerCase().indexOf(_filter) > -1 || _inGroups || _inPrivileges;
        });
      }
    }, self);

    self.selectableRoles = ko.computed(function () {
      var _roles = ko.utils.arrayMap(self.roles(), function (role) {
        return role.name();
      });
      return _roles.sort();
    }, self);

    self.is_sentry_admin = initial.is_sentry_admin;
    self.availableHadoopGroups = ko.observableArray();
    self.assist = new Assist(self, initial);

    // Editing
    self.showCreateRole = ko.observable(false);
    self.role = ko.observable(new Role(self, {}));
    self.roleToUpdate = ko.observable();

    self.grantToPrivilege = ko.observable();
    self.grantToPrivilegeRole = ko.observable();

    self.resetCreateRole = function() {
      self.roles(self.originalRoles());
      self.role(new Role(self, {}));
      $(document).trigger("createTypeahead");
    };

    self.deletePrivilegeModal = function (role) {
      var cascadeDeletes = $.grep(role.privilegesChanged(), function (privilege) {
        return privilege.status() == 'deleted' && (privilege.privilegeType() == 'SERVER' || privilege.privilegeType() == 'DATABASE');
      });

      if (cascadeDeletes.length > 0) {
        self.roleToUpdate(role);
        huePubSub.publish('show.delete.privilege.modal');
      } else {
        self.role().savePrivileges(role);
      }
    };

    self.privilege = new Privilege(self, {});

    self.doAs = ko.observable(initial.user);
    self.doAs.subscribe(function () {
      self.assist.refreshTree();
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
        role.selected(false);
      });
      ko.utils.arrayForEach(self.filteredRoles(), function (role) {
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
      $(document).trigger("deletedRole");
    };

    self.expandSelectedRoles = function () {
      ko.utils.arrayForEach(self.selectedRoles(), function (role) {
        if (! role.showPrivileges()) {
          self.list_sentry_privileges_by_role(role);
        }
      });
    };

    self.expandedRoles = ko.observableArray([]);

    self.init = function (path) {
      self.assist.isLoadingTree(true);
      self.isLoadingRoles(true);
      self.assist.path(path);
      window.setTimeout(function(){
        self.fetchUsers();
        self.list_sentry_roles_by_group();
        if (path != "") {
          self.assist.loadParents();
        } else {
          self.assist.fetchAuthorizablesPath();
        }
      }, 100);
    };

    self.removeRole = function (roleName) {
      $.each(self.roles(), function (index, role) {
        if (role.name() == roleName) {
          self.roles.remove(role);
          return false;
        }
      });
      $.each(self.originalRoles(), function (index, role) {
        if (role.name() == roleName) {
          self.originalRoles.remove(role);
          return false;
        }
      });
    };

    self.list_sentry_roles_by_group = function () {
      self.isLoadingRoles(true);
      $.ajax({
        type: "POST",
        url: "/security/api/sentry/list_sentry_roles_by_group",
        data: {
          'groupName': $('#selectedGroup').val(),
          'component': self.component()
        },
        success: function (data) {
          if (typeof data.status !== "undefined" && data.status == -1) {
            $(document).trigger("error", data.message);
          }
          else {
            self.roles.removeAll();
            self.originalRoles.removeAll();
            var _roles = [];
            var _originalRoles = [];
            $.each(data.roles, function (index, item) {
              _roles.push(new Role(self, item));
              _originalRoles.push(new Role(self, item));
            });
            self.roles(_roles);
            self.originalRoles(_originalRoles);
          }
        }
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
      }).always(function() {
        self.isLoadingRoles(false);
      });
    };

    self.refreshExpandedRoles = function () {
      ko.utils.arrayForEach(self.filteredRoles(), function (r) {
        if (self.expandedRoles().indexOf(r.name()) > -1){
          self.list_sentry_privileges_by_role(r);
        }
      });
    }

    self.showRole = function (role) {
      $(document).trigger("showRole", role);
      ko.utils.arrayForEach(self.filteredRoles(), function (r) {
        if (r.name() == role.name()){
          self.list_sentry_privileges_by_role(r);
        }
      });
    }

    self.list_sentry_privileges_by_role = function (role) {
      $.ajax({
        type: "POST",
        url: "/security/api/sentry/list_sentry_privileges_by_role",
        data: {
          'server': self.server(),
          'component': self.component(),
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
        'component': privilege.component,
        'serverName': privilege.serviceName,
        'authorizables': privilege.authorizables,
        'action': privilege.action,
        'timestamp': privilege.timestamp,
        'grantorPrincipal': privilege.grantorPrincipal,
        'grantOption': privilege.grantOption,
        'id': hueUtils.UUID()
      });
      return _privilege;
    }

    function _create_authorizable_from_ko(optionalPath) {
      var authorizables = [];

      var paths = optionalPath.split(/[.]/);

      if (self.component() == 'solr') {
        if (paths.length > 1) {
          if (paths[0] == 'admin') {
            authorizables.push({'type': 'ADMIN', 'name': paths[1]});
          } else if (paths[0] == 'configs') {
            authorizables.push({'type': 'CONFIG', 'name': paths[1]});
          } else {
            authorizables.push({'type': 'COLLECTION', 'name': paths[1]});
          }
        }
      } else { // TODO Hive
         if (optionalPath != null) {
          if (paths[0]) {
            authorizables.push({'type': 'DATABASE', 'name': paths[0]});
          }
          if (paths[1]) {
            authorizables.push({'type': 'TABLE', 'name': paths[1]});
          }
          if (paths[2]) {
            authorizables.push({'type': 'COLUMN', 'name': paths[2]});
          }
        } else {
          authorizables.push({'type': 'COLUMN', 'name': self.assist.db()});
          authorizables.push({'type': 'TABLE', 'name': self.assist.table()});
          authorizables.push({'type': 'COLUMN', 'name': self.assist.column()});
        }
     }

      return {
          'server': self.assist.server(),
          'authorizables': authorizables
      };
    }

    self.grant_privilege = function () {
      $(".jHueNotify").remove();
      $.ajax({
        type: "POST",
        url: "/security/api/sentry/grant_privilege",
        data: {
          'privilege': ko.mapping.toJSON(self.grantToPrivilege()),
          'roleName': ko.mapping.toJSON(self.grantToPrivilegeRole()),
          'component': self.component()
        },
        success: function (data) {
          if (data.status == 0) {
            $(document).trigger("info", data.message);
            self.assist.refreshTree();
            self.clearTempRoles();
            $(document).trigger("createdRole");
          } else {
            $(document).trigger("error", data.message);
          }
        }
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
      });
    }

    self.clearTempRoles = function () {
      var _roles = [];
      self.roles().forEach(function(role){
        var _found = false;
        self.tempRoles().forEach(function(tempRole){
          if (role.name() == tempRole.name()){
            _found = true;
          }
        });
        if (! _found){
          _roles.push(role);
        }
      });
      self.roles(_roles);
      self.tempRoles([]);
    }

    self.list_sentry_privileges_by_authorizable = function (optionalPath, skipList) {
      var _path = self.assist.path();
      if (optionalPath != null){
        _path = optionalPath;
      }
      self.isLoadingPrivileges(true);
      self.assist.roles.removeAll();
      self.assist.privileges.removeAll();

      $.ajax({
        type: "POST",
        url: "/security/api/sentry/list_sentry_privileges_by_authorizable",
        data: {
          server: self.server(),
          groupName: $('#selectedGroup').val(),
          roleSet: ko.mapping.toJSON({all: true, roles: []}),
          authorizableHierarchy: ko.mapping.toJSON(_create_authorizable_from_ko(_path)),
          component: self.component()
        },
        success: function (data) {
          if (data.status == 0) {
            var _privileges = [];
            $.each(data.privileges, function (index, item) {
              if (typeof skipList == "undefined" || (skipList != null && typeof skipList == "Boolean" && !skipList)){
                var _role = null;
                self.assist.roles().forEach(function (role) {
                  if (role.name() == item.roleName) {
                    _role = role;
                  }
                });
                if (_role == null) {
                  var _idx = self.assist.roles.push(new Role(self, { name: item.roleName }));
                  _role = self.assist.roles()[_idx - 1];
                }

                var privilege = _create_ko_privilege(item);
                var privilegeCopy = _create_ko_privilege(item);
                privilegeCopy.id(privilege.id());
                _role.privileges.push(privilege);
                _role.originalPrivileges.push(privilegeCopy);

                _privileges.push(privilege);
              }
            });
            if (typeof skipList == "undefined" || (skipList != null && typeof skipList == "Boolean" && !skipList)) {
              self.assist.privileges(_privileges);
            }
            self.assist.loadData(self.assist.growingTree());
          } else {
            $(document).trigger("error", data.message);
          }
        }
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
      }).always(function() {
        self.isLoadingPrivileges(false);
      });
    };

    self.bulkAction = ko.observable("");

    self.bulkPerfomAction = function () {
      switch (self.bulkAction()) {
        case "add":
          self.bulk_add_privileges();
          break;
        case "sync":
          self.bulk_delete_privileges({norefresh: true});
          self.bulk_add_privileges();
          break;
        case "delete":
          self.bulk_delete_privileges();
          break;
      }
      self.bulkAction("");
    }

    self.bulk_delete_privileges = function (norefresh) {
      $(".jHueNotify").remove();
      var checkedPaths = self.assist.checkedItems();
      $.post("/security/api/sentry/bulk_delete_privileges", {
        'authorizableHierarchy': ko.mapping.toJSON(_create_authorizable_from_ko()),
        'checkedPaths': ko.mapping.toJSON(checkedPaths),
        'recursive': false,
        'component': self.component()
      }, function (data) {
        if (data.status == 0) {
          if (norefresh == undefined) {
            self.list_sentry_privileges_by_authorizable(); // Refresh
            $(document).trigger("deletedBulkPrivileges");
          }
        } else {
          $(document).trigger("error", data.message);
        }
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
      });
    }

    self.bulk_add_privileges = function (role) {
      $(".jHueNotify").remove();
      var checkedPaths = self.assist.checkedItems();
      $.post("/security/api/sentry/bulk_add_privileges", {
        'privileges': ko.mapping.toJSON(self.assist.privileges),
        'authorizableHierarchy': ko.mapping.toJSON(_create_authorizable_from_ko()),
        'checkedPaths': ko.mapping.toJSON(checkedPaths),
        'recursive': false,
        'component': self.component()
      }, function (data) {
        if (data.status == 0) {
          self.list_sentry_privileges_by_authorizable(); // Refresh
          $(document).trigger("addedBulkPrivileges");
        } else {
          $(document).trigger("error", data.message);
        }
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
      });
    }

    self.bulk_refresh_privileges= function () {
      ko.utils.arrayForEach(self.assist.checkedItems(), function (item) {
        self.list_sentry_privileges_by_authorizable(item.path, true);
      });
    };

    self.fetchUsers = function () {
      var data = {
        'count': 2000,
        'include_myself': true,
        'extend_user': true
      };
      if (! self.is_sentry_admin) {
        data['only_mygroups'] = true;
      }

      $.getJSON('/desktop/api/users/autocomplete', data, function (data) {
        self.availableHadoopUsers(data.users);
        self.availableHadoopGroups(data.groups);
        $(document).trigger("loadedUsers");
      });
    }

    self.lastHash = '';

    self.updatePathHash = function (path) {
      var _hash = window.location.hash.replace(/(<([^>]+)>)/ig, "");
      if (_hash.indexOf("@") == -1) {
        window.location.hash = path;
      }
      else {
        window.location.hash = path + "@" + _hash.split("@")[1];
      }
      self.lastHash = window.location.hash;
    }

    self.updateSectionHash = function (section) {
      var _hash = window.location.hash.replace(/(<([^>]+)>)/ig, "");
      if (_hash == "") {
        window.location.hash = "@" + section;
      }
      if (_hash.indexOf("@") == -1) {
        window.location.hash = _hash + "@" + section;
      }
      else {
        window.location.hash = _hash.split("@")[0] + "@" + section;
      }
      self.lastHash = window.location.hash;
    }

    self.getPathHash = function () {
      if (window.location.hash != "") {
        var _hash = window.location.hash.substr(1).replace(/(<([^>]+)>)/ig, "");
        if (_hash.indexOf("@") > -1) {
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
        var _hash = window.location.hash.substr(1).replace(/(<([^>]+)>)/ig, "");
        if (_hash.indexOf("@") > -1) {
          return _hash.split("@")[1];
        }
      }
      return "edit";
    }

    self.linkToBrowse = function (path) {
      self.assist.path(path);
      $(document).trigger("changedPath");
      self.assist.loadParents();
      self.updateSectionHash("edit");
      $(document).trigger("showMainSection");
    }
  };

  return SentryViewModel;
})();
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

var HdfsViewModel = (function () {

  var Assist = function (vm, assist) {
    var self = this;

    self.compareNames = function (a, b) {
      if (a.name.toLowerCase() < b.name.toLowerCase())
        return -1;
      if (a.name.toLowerCase() > b.name.toLowerCase())
        return 1;
      return 0;
    }

    self.isLoadingAcls = ko.observable(false);
    self.isLoadingTree = ko.observable(false);
    self.showAclsAsText = ko.observable(false);
    self.isDiffMode = ko.observable(false);
    self.isDiffMode.subscribe(function () {
      self.refreshTree();
    });

    self.treeAdditionalData = {};
    self.treeData = ko.observable({nodes: []});
    self.loadData = function (data) {
      self.treeData(new TreeNodeModel(data));
    };

    self.initialGrowingTree = {
      name: "__HUEROOT__",
      path: "__HUEROOT__",
      aclBit: false,
      striked: false,
      selected: false,
      rwx: "",
      page: {
        number: -1,
        num_pages: -1
      },
      nodes: [
        {
          name: "/",
          path: "/",
          isDir: true,
          isExpanded: false,
          isLoaded: false,
          isChecked: false,
          aclBit: false,
          striked: false,
          selected: false,
          rwx: "",
          page: {
            number: -1,
            num_pages: -1
          },
          nodes: []
        }
      ]
    };

    self.growingTree = ko.observable(jQuery.extend(true, {}, self.initialGrowingTree));

    self.path = ko.observable('');
    self.path.subscribe(function (path) {
      self.pagenum(1);
      self.fetchPath();
      window.location.hash = path;
      vm.lastHash = window.location.hash;
    });
    self.pathType = ko.observable('');
    self.recursive = ko.observable(false);
    self.pagenum = ko.observable(1);
    self.fromLoadMore = false;
    self.fromRebuildTree = false;

    self.acls = ko.observableArray();
    self.originalAcls = ko.observableArray();
    self.regularAcls = ko.computed(function () {
      return $.grep(self.acls(), function (acl) {
        return !acl.isDefault();
      });
    });
    self.defaultAcls = ko.computed(function () {
      return $.grep(self.acls(), function (acl) {
        return acl.isDefault();
      });
    });
    self.changedRegularAcls = ko.computed(function () {
      return $.grep(self.regularAcls(), function (acl) {
        return ['new', 'deleted', 'modified'].indexOf(acl.status()) != -1 &&
          ! (['new', 'modified'].indexOf(acl.status()) != -1 && acl.name() == ''); // Empty groups/users
      });
    });
    self.changedDefaultAcls = ko.computed(function () {
      return $.grep(self.defaultAcls(), function (acl) {
        return ['new', 'deleted', 'modified'].indexOf(acl.status()) != -1;
      });
    });

    self.owner = ko.observable('');
    self.group = ko.observable('');

    self.checkedItems = ko.observableArray([]);

    self.afterRender = function () {
      if (!self.fromLoadMore && !self.fromRebuildTree) {
        $(document).trigger("renderedTree");
      }
      self.fromLoadMore = false;
      self.fromRebuildTree = false;
    }


    self.addAcl = function () {
      var newAcl = vm.parseAcl('group::---');
      newAcl.status('new');
      self.acls.push(newAcl);
    };

    self.addDefaultAcl = function () {
      var newAcl = vm.parseAcl('default:group::---');
      newAcl.status('new');
      self.acls.push(newAcl);
    };

    self.removeAcl = function (acl) {
      if (acl.status() == 'new') {
        self.acls.remove(acl);
      } else {
        acl.status('deleted');
      }
    };

    self.convertItemToObject = function (item) {
      if (item.path != null && item.name != "." && item.name != "..") {
        var _path = item.path;
        var _parent = _path.substr(0, _path.lastIndexOf("/"));
        if (_parent == "") {
          _parent = "/";
        }
        if (_path != "/") {
          self.growingTree(self.traversePath(self.growingTree(), _parent, item));
        }
      }
    }

    self.traversePath = function (leaf, parent, item) {
      var _mainFound = false;
      leaf.nodes.forEach(function (node) {
        if (node.path == item.path) {
          _mainFound = true;
        }
        if (parent.indexOf(node.path) > -1) {
          self.traversePath(node, parent, item);
        }
      });

      if (!_mainFound && leaf.path == parent) {
        var _chunks = item.path.split("/");
        leaf.nodes.push({
          name: _chunks[_chunks.length - 1],
          path: item.path,
          aclBit: item.rwx.indexOf('+') != -1,
          striked: item.striked != null,
          isExpanded: false,
          isLoaded: false,
          isChecked: false,
          rwx: item.rwx,
          isDir: item.type == "dir" || item.isDir == true,
          page: {
            number: -1,
            num_pages: -1
          },
          nodes: []
        });
        leaf.nodes.sort(self.compareNames);
      }
      return leaf;
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

    self.expandTree = function () {
      self.updateTreeProperty(self.growingTree(), "isExpanded", true);
      self.loadData(self.growingTree());
    }

    self.refreshTree = function (force) {
      $.ajaxSetup({
        async: false
      });
      self.growingTree(jQuery.extend(true, {}, self.initialGrowingTree));
      Object.keys(self.treeAdditionalData).sort().forEach(function (path) {
        if (typeof force == "boolean" && force) {
          self.fetchPath(path, function () {
            self.updatePathProperty(self.growingTree(), path, "isExpanded", self.treeAdditionalData[path].expanded);
            self.loadData(self.growingTree());
          });
        } else {
          if (self.treeAdditionalData[path].loaded) {
            self.fetchPath(path, function () {
              self.updatePathProperty(self.growingTree(), path, "isExpanded", self.treeAdditionalData[path].expanded);
              self.loadData(self.growingTree());
            });
          }
        }
      });
      $.ajaxSetup({
        async: true
      });
      self.getAcls();
    }

    self.rebuildTree = function (leaf, paths) {
      paths.push(leaf.path);
      if (leaf.nodes.length > 0) {
        leaf.nodes.forEach(function (node) {
          if (node.isDir) {
            self.rebuildTree(node, paths);
          }
        });
      }
      return paths;
    }

    self.setPath = function (obj, toggle) {
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
      self.path(obj.path());
    }

    self.togglePath = function (obj) {
      self.setPath(obj, true);
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

    self.openPath = function (obj) {
      window.open("/filebrowser/view=" + obj.path(), '_blank');
    }

    self.loadParents = function (breadcrumbs) {
      if (typeof breadcrumbs != "undefined" && breadcrumbs != null) {
        breadcrumbs.forEach(function (crumb, idx) {
          if (idx < breadcrumbs.length - 1 && crumb.url != "") {
            var _item = {
              path: crumb.url,
              name: crumb.label,
              rwx: "",
              isDir: true,
              page: {
                number: -1,
                num_pages: -1
              }
            }
            self.convertItemToObject(_item);
          }
        });
        $(document).trigger("loadedParents");
      }
    }

    self.fetchPath = function (optionalPath, loadCallback) {
      var _path = typeof optionalPath != "undefined" ? optionalPath : self.path();
      $.getJSON('/security/api/hdfs/list' + _path, {
            'pagesize': 15,
            'pagenum': self.pagenum(),
            'format': 'json',
            'doas': vm.doAs(),
            'isDiffMode': self.isDiffMode()
          },
          function (data) {
            if (data.error != null && data.error == "FILE_NOT_FOUND") {
              self.path("/");
              self.pathType("dir");
            }
            else {
              self.loadParents(data.breadcrumbs);
              function findDir(files) {
                if (files.length < 1) {
                  return false;
                }
                var foundDir = false;
                files.forEach(function (f) {
                  if (f.name === '.' && f.type === 'dir') {
                    foundDir = true;
                  }
                });
                return foundDir;
              }
              if (data['files'] && findDir(data['files'])) {
                self.pathType("dir");
                $.each(data.files, function (index, item) {
                  self.convertItemToObject(item);
                });
              }
              else {
                self.pathType("file");
                self.convertItemToObject(data);
              }
              self.getTreeAdditionalDataForPath(_path).loaded = true;
              self.updatePathProperty(self.growingTree(), _path, "isLoaded", true);
              if (data.page != null && data.page.number != null) {
                self.updatePathProperty(self.growingTree(), _path, "page", data.page);
              }
              if (typeof loadCallback != "undefined") {
                loadCallback(data);
              }
              else {
                self.loadData(self.growingTree());
              }
              if (typeof optionalPath == "undefined") {
                self.getAcls();
              }
          }
       }).fail(function (xhr, textStatus, errorThrown) {
          $(document).trigger("error", xhr.responseText);
       });
    };

    self.loadMore = function (what) {
      self.pagenum(what.page().next_page_number());
      self.fetchPath(what.path());
      self.fromLoadMore = true;
    }

    self.getAcls = function () {
      $(".jHueNotify").remove();
      var _isLoading = window.setTimeout(function () {
        self.isLoadingAcls(true);
      }, 1000);
      hueAnalytics.log('security/hdfs', 'get_acls');
      $.getJSON('/security/api/hdfs/get_acls', {
        'path': self.path()
      }, function (data) {
        window.clearTimeout(_isLoading);
        if (data != null) {
          self.acls.removeAll();
          self.originalAcls.removeAll();
          $.each(data.entries, function (index, item) {
            self.acls.push(vm.parseAcl(item));
            self.originalAcls.push(vm.parseAcl(item));
          });
          self.owner(data.owner);
          self.group(data.group);
          self.isLoadingAcls(false);
          $(document).trigger("loadedAcls");
        }
      }).fail(function (xhr, textStatus, errorThrown) {
        if (xhr.responseText.search('FileNotFoundException') == -1) { // TODO only fetch on existing path
          $(document).trigger("error", xhr.responseText);
          self.isLoadingAcls(false);
        }
      });
    };

    self.updateAcls = function () {
      $(".jHueNotify").remove();
      hueAnalytics.log('security/hdfs', 'updateAcls');

      $.post("/security/api/hdfs/update_acls", {
            'path': self.path(),
            'acls': ko.mapping.toJSON(self.acls()),
            'originalAcls': ko.mapping.toJSON(self.originalAcls())
          }, function (data) {
            var toDelete = []
            $.each(self.acls(), function (index, item) {
              if (item.status() == 'deleted') {
                toDelete.push(item);
              } else {
                item.status('');
              }
            });
            $.each(toDelete, function (index, item) {
              self.acls.remove(item);
            });
            self.refreshTree();
            $(document).trigger("updatedAcls");
          }
      ).fail(function (xhr, textStatus, errorThrown) {
         $(document).trigger("error", JSON.parse(xhr.responseText).message);
      });
    }

    self.bulkAction = ko.observable("");

    self.bulkPerfomAction = function () {
      switch (self.bulkAction()) {
        case "add":
          self.bulkAddAcls();
          break;
        case "sync":
          self.bulkSyncAcls();
          break;
        case "delete":
          self.bulkDeleteAcls();
          break;
      }
      self.bulkAction("");
    }

    self.bulkDeleteAcls = function () {
      $(".jHueNotify").remove();
      hueAnalytics.log('security/hdfs', 'bulkDeleteAcls');

      var checkedPaths = self.checkedItems();

      $.post("/security/api/hdfs/bulk_delete_acls", {
            'path': self.path(),
            'checkedPaths': ko.mapping.toJSON(checkedPaths),
            'recursive': ko.mapping.toJSON(self.recursive())
          }, function (data) {
            if (checkedPaths.indexOf(self.path()) != -1) {
              self.acls.removeAll();
            }
            self.refreshTree();
            $(document).trigger("deletedBulkAcls");
          }
      ).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", JSON.parse(xhr.responseText).message);
      });
    }

    self.bulkAddAcls = function () {
      $(".jHueNotify").remove();
      hueAnalytics.log('security/hdfs', 'bulkAddAcls');

      var checkedPaths = self.checkedItems();

      $.post("/security/api/hdfs/bulk_add_acls", {
            'path': self.path(),
            'acls': ko.mapping.toJSON(self.acls()),
            'checkedPaths': ko.mapping.toJSON(checkedPaths),
            'recursive': ko.mapping.toJSON(self.recursive())
          }, function (data) {
            self.refreshTree();
            $(document).trigger("addedBulkAcls");
          }
      ).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", JSON.parse(xhr.responseText).message);
      });
    }

    self.bulkSyncAcls = function () {
      $(".jHueNotify").remove();
      hueAnalytics.log('security/hdfs', 'bulkSyncAcls');

      var checkedPaths = self.checkedItems();

      $.post("/security/api/hdfs/bulk_sync_acls", {
            'path': self.path(),
            'acls': ko.mapping.toJSON(self.acls()),
            'checkedPaths': ko.mapping.toJSON(checkedPaths),
            'recursive': ko.mapping.toJSON(self.recursive())
          }, function (data) {
            self.refreshTree();
            $(document).trigger("syncdBulkAcls");
          }
      ).fail(function (xhr, textStatus, errorThrown) {
         $(document).trigger("error", JSON.parse(xhr.responseText).message);
      });
    }
  }

  var HdfsViewModel = function (initial) {
    var self = this;

    self.assist = new Assist(self, initial);
    self.lastHash = '';

    self.doAs = ko.observable(initial.user);
    self.doAs.subscribe(function () {
      self.assist.refreshTree();
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


    self.init = function (path) {
      self.fetchUsers();
      self.assist.path(path);
      $(document).one("loadedParents", function () {
        self.assist.isLoadingTree(true);
        var _paths = self.assist.rebuildTree(self.assist.growingTree().nodes[0], []);
        _paths.forEach(function (ipath, cnt) {
          self.assist.updatePathProperty(self.assist.growingTree(), ipath, "isExpanded", true);
          self.assist.fetchPath(ipath, function () {
            if (cnt == _paths.length - 1) {
              self.assist.fetchPath(path, function () {
                self.assist.updatePathProperty(self.assist.growingTree(), path, "isExpanded", true);
                self.assist.fromRebuildTree = true;
                self.assist.loadData(self.assist.growingTree());
                self.assist.isLoadingTree(false);
              });
            }
          });
        });
      });
    }

    self.fetchUsers = function () {
      $.getJSON('/desktop/api/users/autocomplete', {
        'count': 2000,
        'include_myself': true,
        'extend_user': true
      }, function (data) {
        self.availableHadoopUsers(data.users);
        self.availableHadoopGroups(data.groups);
        $(document).trigger("loadedUsers");
      });
    }

    self.parseAcl = function (acl) {
    // (default:)?(user|group|mask|other):[[A-Za-z_][A-Za-z0-9._-]]*:([rwx-]{3})?
    m = acl.match(/(default:)?(user|group|mask|other):(.*?):(.)(.)(.)/);
    var acl = ko.mapping.fromJS({
      'isDefault': m[1] != null,
      'type': m[2],
      'name': m[3],
      'r': m[4] != '-',
      'w': m[5] != '-',
      'x': m[6] != '-',
      'status': ''
    });

    acl.type.subscribe(function () {
      acl.status('modified');
    });
    acl.name.subscribe(function () {
      acl.status('modified');
    });
    acl.r.subscribe(function () {
      acl.status('modified');
    });
    acl.w.subscribe(function () {
      acl.status('modified');
    });
    acl.x.subscribe(function () {
      acl.status('modified');
    });

    return acl;
  }

    self.printAcl = function (acl) {
      return (acl.isDefault() ? 'default:' : '') + acl.type() + ':' + acl.name() + ':' + (acl.r() ? 'r' : '-') + (acl.w() ? 'w' : '-') + (acl.x() ? 'x' : '-');
    }
  };

  return HdfsViewModel;
})();
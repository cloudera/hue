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

function parseAcl(acl) {
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

function printAcl(acl) {
  return (acl.isDefault() ? 'default:' : '') + acl.type() + ':' + acl.name() + ':' + (acl.r() ? 'r' : '-') + (acl.w() ? 'w' : '-') + (acl.x() ? 'x' : '-');
}

var Assist = function (vm, assist) {
  var self = this;

  self.compareNames = function (a,b) {
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
        isExpanded: true,
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
  });
  self.pagenum = ko.observable(1);
  self.fromLoadMore = false;
  self.fromRebuildTree = false;

  self.acls = ko.observableArray();
  self.originalAcls = ko.observableArray();
  self.regularAcls = ko.computed(function () {
    return $.grep(self.acls(), function (acl) {
      return ! acl.isDefault();
    });
  });
  self.defaultAcls = ko.computed(function () {
    return $.grep(self.acls(), function (acl) {
      return acl.isDefault();
    });
  });
  self.changedAcls = ko.computed(function () {
    return $.grep(self.acls(), function (acl) {
      return ['new', 'deleted', 'modified'].indexOf(acl.status()) != -1;
    });
  });

  self.owner = ko.observable('');
  self.group = ko.observable('');

  self.afterRender = function() {
    if (! self.fromLoadMore && ! self.fromRebuildTree) {
      $(document).trigger("rendered.tree");
    }
    self.fromLoadMore = false;
    self.fromRebuildTree = false;
  }


  self.addAcl = function () {
    var newAcl = parseAcl('group::---');
    newAcl.status('new');
    self.acls.push(newAcl);
  };

  self.addDefaultAcl = function () {
    var newAcl = parseAcl('default:group::---');
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
        isExpanded: true,
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
    if (typeof self.treeAdditionalData[path] == "undefined"){
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

  self.expandTree = function () {
    self.updateTreeProperty(self.growingTree(), "isExpanded", true);
    self.loadData(self.growingTree());
  }

  self.refreshTree = function (force) {
    self.growingTree(jQuery.extend(true, {}, self.initialGrowingTree));
    Object.keys(self.treeAdditionalData).forEach(function (path) {
      if (typeof force == "boolean" && force) {
        self.fetchPath(path);
      } else {
        if (self.treeAdditionalData[path].loaded) {
          self.fetchPath(path);
        }
      }
    });
  }

  self.rebuildTree = function (leaf, paths) {
    paths.push(leaf.path);
    if (leaf.nodes.length > 0) {
      leaf.nodes.forEach(function (node) {
        if (node.isDir){
          self.rebuildTree(node, paths);
        }
      });
    }
    return paths;
  }

  self.setPath = function (obj, toggle) {
    if (self.getTreeAdditionalDataForPath(obj.path()).loaded || (! obj.isExpanded() && ! self.getTreeAdditionalDataForPath(obj.path()).loaded)) {
      if (typeof toggle == "boolean" && toggle){
        obj.isExpanded(!obj.isExpanded());
      } else {
        obj.isExpanded(true);
      }
      self.updatePathProperty(self.growingTree(), obj.path(), "isExpanded", obj.isExpanded());
    }
    self.path(obj.path());
  }

  self.togglePath = function (obj) {
    self.setPath(obj, true);
  }

  self.openPath = function (obj) {
    window.open("/filebrowser/view" + obj.path(), '_blank');
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
      $(document).trigger("loaded.parents");
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
        self.loadParents(data.breadcrumbs);
        if (data['files'] && data['files'][0] && data['files'][0]['type'] == 'dir') { // Hack for now
          $.each(data.files, function (index, item) {
            self.convertItemToObject(item);
          });
        }
        else {
          self.convertItemToObject(data);
        }
        self.getTreeAdditionalDataForPath(_path).loaded = true;
        if (data.page != null && data.page.number != null){
          self.updatePathProperty(self.growingTree(), _path, "page", data.page);
        }
        if (typeof loadCallback != "undefined"){
          loadCallback(data);
        }
        else {
          self.loadData(self.growingTree());
        }
        if (typeof optionalPath == "undefined"){
          self.getAcls();
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
    $(".jHueNotify").hide();
    var _isLoading = window.setTimeout(function () {
        self.isLoadingAcls(true);
      }, 1000);
        logGA('get_acls');

        $.getJSON('/security/api/hdfs/get_acls', {
        'path': self.path()
      }, function (data) {
      window.clearTimeout(_isLoading);
      if (data != null) {
        self.acls.removeAll();
        self.originalAcls.removeAll();
        $.each(data.entries, function (index, item) {
          self.acls.push(parseAcl(item));
          self.originalAcls.push(parseAcl(item));
        });
        self.owner(data.owner);
        self.group(data.group);
        self.isLoadingAcls(false);
        $(document).trigger("loaded.acls");
      }
    }).fail(function (xhr, textStatus, errorThrown) {
      if (xhr.responseText.search('FileNotFoundException') == -1) { // TODO only fetch on existing path
        $(document).trigger("error", xhr.responseText);
        self.isLoadingAcls(false);
      }
    });
  };

  self.updateAcls = function () {
    $(".jHueNotify").hide();
    logGA('updateAcls');

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
        $(document).trigger("info", 'Done!');
      }
    ).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", JSON.parse(xhr.responseText).message);
      });
  }
}


var HdfsViewModel = function (initial) {
  var self = this;

  self.assist = new Assist(self, initial);

  self.doAs = ko.observable(initial.user);
  self.doAs.subscribe(function () {
	self.assist.refreshTree();
  });
  self.availableHadoopUsers = ko.observableArray();
  self.availableHadoopGroups = ko.observableArray();

  self.selectableHadoopUsers = ko.computed(function() {
    var _users = ko.utils.arrayMap(self.availableHadoopUsers(), function(user) {
        return user.username;
    });
    return _users.sort();
  }, self);

  self.selectableHadoopGroups = ko.computed(function() {
    var _users = ko.utils.arrayMap(self.availableHadoopGroups(), function(group) {
        return group.name;
    });
    return _users.sort();
  }, self);


  self.init = function (path) {
    self.fetchUsers();
    self.assist.path(path);
    $(document).one("loaded.parents", function(){
      self.assist.isLoadingTree(true);
      var _paths = self.assist.rebuildTree(self.assist.growingTree().nodes[0], []);
      _paths.forEach(function(path, cnt){
        self.assist.fetchPath(path, function(){
          if (cnt == _paths.length -1){
            self.assist.fromRebuildTree = true;
            self.assist.loadData(self.assist.growingTree());
            self.assist.isLoadingTree(false);
          }
        });
      });
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
};

function logGA(page) {
  if (typeof trackOnGA == 'function') {
    trackOnGA('security/hdfs' + page);
  }
}

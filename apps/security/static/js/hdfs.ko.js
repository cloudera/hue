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
    updateTypeAheads(viewModel);
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

function updateTypeAheads(vm) { 
  $(".group-list").typeahead({'source': vm.availableHadoopGroups()});
  $(".user-list").typeahead({'source': vm.availableHadoopUsers()});
}


var Assist = function (vm, assist) {
  var self = this;

  self.isLoadingAcls = ko.observable(false);
  self.showAclsAsText = ko.observable(false);
  self.isDiffMode = ko.observable(false);

  self.treeAdditionalData = {};
  self.treeAdditionalDataObservable = ko.observable({});
  self.treeData = ko.observable({nodes: []});
  self.loadData = function (data) {
    self.treeData(new TreeNodeModel(data));
  };

  self.growingTree = ko.observable({
    name: "__HUEROOT__",
    path: "__HUEROOT__",
    aclBit: false,
    striked: false,
    selected: false,
    page: {},
    nodes: [
      {
        name: "/",
        path: "/",
        isDir: true,
        isExpanded: true,
        aclBit: false,
        striked: false,
        selected: false,
        page: {},
        nodes: []
      }
    ]
  });

  self.path = ko.observable('');
  self.path.subscribe(function (path) {
    self.pagenum(1);
    self.fetchPath();
    window.location.hash = path;
  });
  self.pagenum = ko.observable(1);
  self.files = ko.observableArray();

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
    $(document).trigger("rendered.tree");
  }


  self.addAcl = function () {
    var newAcl = parseAcl('group::---');
    newAcl.status('new');
    self.acls.push(newAcl);
    updateTypeAheads(vm);
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
    if (item.path != null) {
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
        isDir: item.type == "dir",
        page: {},
        nodes: []
      });
    }
    return leaf;
  }

  self.getTreeAdditionalDataForPath = function (path) {
    if (typeof self.treeAdditionalData[path] == "undefined"){
      var _add = {
        loaded: false,
        page: {}
      }
      self.treeAdditionalData[path] = _add;
      self.treeAdditionalDataObservable(self.treeAdditionalData);
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

  self.setPath = function (obj) {
    if (self.getTreeAdditionalDataForPath(obj.path()).loaded == true) {
      obj.isExpanded(!obj.isExpanded());
      self.updatePathProperty(self.growingTree(), obj.path(), "isExpanded", obj.isExpanded());
    }
    self.path(obj.path());
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
            isDir: true
          }
          self.convertItemToObject(_item);
        }
      });
    }
  }

  self.fetchPath = function () {
	$.getJSON('/security/api/hdfs/list' + self.path(), {
      'pagesize': 15,
      'pagenum': self.pagenum(),
      'format': 'json',
      'doas': vm.doAs(),
      'isDiffMode': self.isDiffMode()
    },
    function (data) {
      self.getTreeAdditionalDataForPath(self.path()).loaded = true;
      self.getTreeAdditionalDataForPath(self.path()).page = data.page;
      self.treeAdditionalDataObservable(self.treeAdditionalData);
      self.updatePathProperty(self.growingTree(), self.path(), "page", data.page);
      self.loadParents(data.breadcrumbs);
      if (data['files'] && data['files'][0] && data['files'][0]['type'] == 'dir') { // Hack for now
        self.files.removeAll();
        $.each(data.files, function (index, item) {
          self.convertItemToObject(item);
          self.files.push(ko.mapping.fromJS({
              'path': item.path,
              'aclBit': item.rwx.indexOf('+') != -1,
              'striked': item.striked != null
            })
          );
        });
      }
      else {
        self.convertItemToObject(data);
      }
      self.loadData(self.growingTree());
      self.getAcls();
    }).fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });
  };

  self.loadMore = function (what) {
    self.pagenum(what.page().next_page_number());
    self.fetchPath();
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
    self.assist.fetchPath();
  });
  self.availableHadoopUsers = ko.observableArray();
  self.availableHadoopGroups = ko.observableArray();

  self.init = function (path) {
    self.fetchUsers();
    self.assist.path(path);
  }

  self.fetchUsers = function () {
    $.getJSON('/desktop/api/users/autocomplete', function (data) {
      $.each(data.users, function (i, user) {
        self.availableHadoopUsers.push(user.username);
      });

      $.each(data.groups, function (i, group) {
        self.availableHadoopGroups.push(group.name);
      });
      
      updateTypeAheads(self);
    });
  }
};

function logGA(page) {
  if (typeof trackOnGA == 'function') {
    trackOnGA('security/hdfs' + page);
  }
}

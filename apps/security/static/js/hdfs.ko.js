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
  return acl.type() + ':' + acl.name() + ':' + (acl.r() ? 'r' : '-') + (acl.w() ? 'w' : '-') + (acl.x() ? 'x' : '-');
}

var Assist = function (vm, assist) {
  var self = this;

  self.isLoadingAcls = ko.observable(false);

  self.treeData = ko.observable({nodes:[]});
  self.loadData = function(data) {
    self.treeData(new NodeModel(data));
  };

  self.growingTree = ko.observable({
    name: "/",
    path: "/",
    aclBit: false,
    selected: false,
    nodes: []
  });

  self.path = ko.observable('');
  self.path.subscribe(function () {
    self.fetchPath();
  });
  self.files = ko.observableArray();

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
  self.changedAcls = ko.computed(function () {
    return $.grep(self.acls(), function (acl) {
      return ['new', 'deleted', 'modified'].indexOf(acl.status()) != -1;
    });
  });

  self.owner = ko.observable('');
  self.group = ko.observable('');

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
    var _path = item.path;
    var _parent =  _path.substr(0, _path.lastIndexOf("/"));
    if (_parent == "") {
      _parent = "/";
    }
    if (_path != "/") {
      self.growingTree(self.traversePath(self.growingTree(), _parent, item));
    }
  }

  self.traversePath = function(leaf, parent, item){
    var _mainFound = false;
    leaf.nodes.forEach(function(node){
      if (node.path == item.path){
        _mainFound = true;
      }
      if (parent.indexOf(node.path) > -1){
        self.traversePath(node, parent, item);
      }
    });
    if (!_mainFound && leaf.path == parent){
      var _chunks = item.path.split("/");
      leaf.nodes.push({
        name: _chunks[_chunks.length-1],
        path: item.path,
        aclBit: item.rwx.indexOf('+') != -1,
        isDir: item.type == "dir",
        nodes: []
      });
    }
    return leaf;
  }

  self.setPath = function (obj) {
    self.path(obj.path());
  }

  self.loadParents = function(breadcrumbs) {
    if (typeof breadcrumbs != "undefined" && breadcrumbs != null) {
      breadcrumbs.forEach(function (crumb, idx) {
        if (idx < breadcrumbs.length - 1 && crumb.url != "") {
          var _item = {
            path: crumb.url,
            name: crumb.label,
            rwx: ""
          }
          self.convertItemToObject(_item);
        }
      });
    }
  }

  self.fetchPath = function () {
    $.getJSON('/filebrowser/view' + self.path(), {
      'pagesize': 15,
      'format': 'json',
      'doas': vm.doAs(),
    }, function (data) {
      self.loadParents(data.breadcrumbs);
      if (data['files'] && data['files'][0]['type'] == 'dir') { // Hack for now
        self.files.removeAll();
        $.each(data.files, function (index, item) {
          self.convertItemToObject(item);
          self.files.push(ko.mapping.fromJS({
              'path': item.path,
              'aclBit': item.rwx.indexOf('+') != -1
            })
          );
        });
        self.loadData(self.growingTree());
      }
      self.getAcls();
    }).fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });
  };

  self.getAcls = function () {
    $(".jHueNotify").hide();
    var _isLoading = window.setTimeout(function(){
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


var NodeModel = function(data) {
  var self = this;

  self.isExpanded = ko.observable(true);
  self.description = ko.observable();
  self.name = ko.observable();
  self.nodes = ko.observableArray([]);

  self.toggleVisibility = function() {
    self.isExpanded(! self.isExpanded());
  };

  ko.mapping.fromJS(data, self.mapOptions, self);
};

NodeModel.prototype.mapOptions = {
  nodes: {
    create: function(args) {
      return new NodeModel(args.data);
    }
  }
};


var HdfsViewModel = function (initial) {
  var self = this;

  self.assist = new Assist(self, initial);

  self.doAs = ko.observable('');
  self.doAs.subscribe(function() {
    self.assist.fetchPath();
  });
  self.availableHadoopUsers = ko.observableArray();
  self.availableHadoopGroups = ko.observableArray();

  self.init = function () {  
    self.fetchUsers();
    self.assist.path('/');
  }


  self.fetchUsers = function () {
    $.getJSON('/desktop/api/users/autocomplete', function (data) {
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
    trackOnGA('security/hdfs' + page);
  }
}

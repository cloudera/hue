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
  // ^(default:)?(user|group|mask|other):[[A-Za-z_][A-Za-z0-9._-]]*:([rwx-]{3})?(,(default:)?(user|group|mask|other):[[A-Za-z_][A-Za-z0-9._-]]*:([rwx-]{3})?)*$
  m = acl.match(/(.*?):(.*?):(.)(.)(.)/);
  return ko.mapping.fromJS({
    'type': m[1],
    'name': m[2],
     'r': m[3] != '-',
     'w': m[4] != '-',
     'x': m[5] != '-',
     'status': '',
  });
}

function printAcl(acl) {
  return acl.type() + ':' + acl.name() + ':' + (acl.r() ? 'r' : '-') + (acl.w() ? 'w' : '-') + (acl.x() ? 'x' : '-');
}

var Assist = function (vm, assist) {
  var self = this;

  self.path = ko.observable('');
  self.path.subscribe(function () {
	self.fetchPath()
  });
  self.files = ko.observableArray();

  self.acls = ko.observableArray();
  self.owner = ko.observable('');
  self.group = ko.observable('');
  
  self.changed = ko.computed(function() {
	return [1]; //$.grep(self.acls(), function(acl){ return acl.changed(); });
  });
  
  self.addAcl = function() {
	var newAcl = parseAcl('group::---');
	newAcl.status('new');
	self.acls.push(newAcl);
  };
  
  self.removeAcl = function(acl) {
	if (acl.status() == 'new') {
	  self.acls.remove(acl);
	} else {
	  acl.status('deleted');
	}
  };

  self.fetchPath = function () {
    $.getJSON('/filebrowser/view' + self.path() + "?pagesize=15&format=json", function (data) { // Might need to create a cleaner API by calling directly webhdfs#LISTDIR
      if (data['files'] && data['files'][0]['type'] == 'dir') { // Hack for now
        self.files.removeAll();
        $.each(data.files, function(index, item) {
    	  self.files.push(item.path); 
        });
      }
      self.getAcls();
    }).fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });
  };  
  
  self.getAcls = function () {
    $.getJSON('/security/api/hdfs/get_acls', {
    	'path': self.path()
      }, function (data) {
        self.acls.removeAll();
        $.each(data.entries, function(index, item) {
    	  self.acls.push(parseAcl(item));
        });
        self.owner(data.owner);
        self.group(data.group);
    }).fail(function (xhr, textStatus, errorThrown) {
      if (xhr.responseText.search('FileNotFoundException') == -1) { // TODO only fetch on existing path
        $(document).trigger("error", xhr.responseText);
      }
    });
  };
  
  self.updateAcls = function () {
	var aclSpec = []
	$.each(self.acls(), function (index, acl) {
	  aclSpec.push(printAcl(acl));
	});
    
    $.ajax({
      type: "POST",
      url: "/security/api/hdfs/remove_acl_entries",
      data: {
        'path': self.path(),
        'aclspec': $.grep(self.acls(), function(acl){ return acl.status() == 'deleted'; }).join()
      },
      async: false
    }).fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });

    $.getJSON('/security/api/hdfs/modify_acl_entries', {
    	'path': self.path(),
    	'aclspec': aclSpec.join()
      }, function (data) {
        $(document).trigger("info", 'Done!');
    }).fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    }); 
  }
}

// Might rename Assist to Acls and create Assist for the tree widget?

var HdfsViewModel = function (context_json) {
  var self = this;

  self.assist = new Assist(self, context_json.assist);
  self.assist.path('/tmp/acl');


  function logGA(page) {
    if (typeof trackOnGA == 'function') {
      trackOnGA('security/hdfs' + page);
    }
  }
};

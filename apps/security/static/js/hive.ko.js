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


// groups, priviledges


var Priviledge = function (vm, priviledge) {
  var self = this;

  self.privilegeScope = ko.observable(typeof priviledge.privilegeScope != "undefined" && priviledge.privilegeScope != null ? priviledge.privilegeScope : "");
  self.serverName = ko.observable(typeof priviledge.serverName != "undefined" && priviledge.serverName != null ? priviledge.serverName : "");
  self.dbName = ko.observable(typeof priviledge.dbName != "undefined" && priviledge.dbName != null ? priviledge.dbName : "");
  self.tableName = ko.observable(typeof priviledge.tableName != "undefined" && priviledge.tableName != null ? priviledge.tableName : "");
  self.URI = ko.observable(typeof priviledge.URI != "undefined" && priviledge.URI != null ? priviledge.URI : "");
  self.action = ko.observable(typeof priviledge.action != "undefined" && priviledge.action != null ? priviledge.action : "");
  
  self.availablePriviledges = ko.observableArray(['SERVER', 'DATABASE', 'TABLE']);
  self.availableActions = ko.observableArray(['SELECT', 'INSERT', 'ALL']);
}

var Role = function(vm, priviledge) {
  var self = this;

  self.priviledges = ko.observableArray();
  self.groups = ko.observableArray();
  self.name = ko.observable('');
  
  self.addGroup = function() {
    self.groups.push('');
  }
  
  self.addPriviledge = function() {
	self.priviledges.push(new Priviledge(vm, {}));
  }
  
  self.edit = function() {
	$(".jHueNotify").hide();
    $.post("/security/api/hive/edit_role", {
        role: ko.mapping.toJSON(self)
      }, function (data) {
        if (data.status == 0) {
          $(document).trigger("info", data.message);
          self.roles.push(self);
        }
        else {
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
  self.files = ko.observableArray();
}


var HiveViewModel = function (initial) {
  var self = this;

  // Models
  self.roles = ko.observableArray();
  self.privileges = ko.observableArray();
  self.availableHadoopGroups = ko.mapping.fromJS(initial.hadoop_groups);
  self.assist = new Assist(self);
  
  // Edition
  self.role = new Role();

  
  self.init = function() {
    self.list_sentry_roles_by_group();
  };

  self.list_sentry_roles_by_group = function() {
    $.getJSON('/security/api/hive/list_sentry_roles_by_group', {    	
      }, function (data) {
        $.each(data.roles, function(index, item) {
    	  self.roles.push(item); 
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
        $.each(data.sentry_privileges, function(index, item) {
          self.privileges.push(item); 
        });
        window.location.hash = "#privileges";
      }
    }).fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });
  };  
};

function logGA(page) {
  if (typeof trackOnGA == 'function') {
    trackOnGA('security/' + page);
  }
}

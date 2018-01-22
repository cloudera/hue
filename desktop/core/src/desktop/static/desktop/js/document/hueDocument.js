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

var HueDocument = (function() {

  /**
   *
   * @param {Object} options
   * @param {ApiHelper} options.apiHelper
   * @param {HueFileEntry} options.fileEntry
   *
   * @constructor
   */
  function HueDocument (options) {
    var self = this;
    self.fileEntry = options.fileEntry;
    self.apiHelper = options.apiHelper;
    self.definition = ko.observable();
    self.loaded = ko.observable(false);
    self.loading = ko.observable(false);
    self.hasErrors = ko.observable(false);
    self.searchInput = ko.observable();
    self.selectedUserOrGroup = ko.observable();
    self.selectedPerm = ko.observable('read');


    self.userMap = {};
    self.idToUserMap = {};
    self.groupMap = {};
    self.items = [];
  };

  HueDocument.prototype.onShareAutocompleteUserEnter = function () {
    var self = this;

    searchAutoCompInput = $("#userSearchAutocomp").val();
    selectedUserOrGroup = self.userMap[searchAutoCompInput] ? self.userMap[searchAutoCompInput] : self.groupMap[searchAutoCompInput];
    if (selectedUserOrGroup != null) {
      if (typeof selectedUserOrGroup.username !== 'undefined') {
        self.definition().perms[self.selectedPerm()].users.push(selectedUserOrGroup);
      } else {
        self.definition().perms[self.selectedPerm()].groups.push(selectedUserOrGroup);
      }
      self.persistPerms();
    }
    $("#userSearchAutocomp").val("");

  };

  HueDocument.prototype.shareAutocompleteUserSource = function(request, callback) {
    var self = this;
    var successCallback = function (data) {
      var JSON_USERS_GROUPS = data;
      self.items = [];
      $.each(JSON_USERS_GROUPS.users, function (i, user) {
        var label = prettifyUsername(user);
        var highLightedLabel = hueUtils.highlight(label, request.term);
        self.userMap[label] = user;
        self.items.push({
          data: {
            "icon": "fa fa-user",
            "label": highLightedLabel
          },
          value: label
        });
        self.idToUserMap[user.id] = user;
      });
      $.each(JSON_USERS_GROUPS.groups, function (i, group) {
        self.groupMap[group.name] = group;
        var highLightedLabel = hueUtils.highlight(group.name, request.term);
        self.items.push({
          data: {
            "icon": "fa fa-users",
            "label": highLightedLabel
          },
          value: group.name
        });
      });

      if(self.items.length == 0){
        self.items.push({
          'noMatch': true
        });
      }

      callback(self.items);

      }

    self.apiHelper.fetchUsersAndGroups({
      data: {filter: request.term},
      successCallback: successCallback,
      errorCallback: errorCallback
    });
  };

  HueDocument.prototype.persistPerms = function () {
    var self = this;
    var postPerms = {
      read: {
        user_ids: $.map(self.definition().perms.read.users, function (user) { return user.id }),
        group_ids: $.map(self.definition().perms.read.groups, function (group) { return group.id }),
      },
      write: {
        user_ids: $.map(self.definition().perms.write.users, function (user) { return user.id }),
        group_ids: $.map(self.definition().perms.write.groups, function (group) { return group.id }),
      }
    };

    $.post("/desktop/api2/doc/share", {
      uuid: JSON.stringify(self.fileEntry.definition().uuid),
      data: JSON.stringify(postPerms)
    }, function (response) {
      if (response != null) {
        if (response.status != 0) {
          $(document).trigger("error", "There was an error processing your action: " + response.message);
        } else {
          self.load();
        }
      }
    }).fail(function (response) {
      $(document).trigger("error", "There was an error processing your action: " + response.responseText);
    });
  };

  HueDocument.prototype.load = function () {
    var self = this;
    if (self.loading()) {
      return;
    }

    self.loading(true);
    self.hasErrors(false);

    var fetchDocumentsSuccessCallback = function (data) {
      readusers = data.document.perms.read.users.map(function(user){return user.id});
      writeusers = data.document.perms.write.users.map(function(user){return user.id});
      allusers = readusers.concat(writeusers);
      if (allusers.length > 0) {
        var successCallback = function (response) {
          $.each(response.users, function (i, user) {
            // Needed for getting prettyusername of already shared users
            self.idToUserMap[user.id] = user;
          });
          self.definition(data.document);
        };
        self.apiHelper.fetchUsersByIds({
          userids: JSON.stringify(allusers),
          successCallback: successCallback,
          errorCallback: errorCallback
        });
      } else {
        self.definition(data.document);
      }
    }

    var fetchFunction = function () {
      self.apiHelper.fetchDocument({
        uuid: self.fileEntry.definition().uuid
      }).done(function (data) {
        fetchDocumentsSuccessCallback(data);
        self.loading(false);
        self.loaded(true);
      }).fail(function () {
        self.hasErrors(true);
        self.loading(false);
        self.loaded(true);
      })
    };

    fetchFunction();
  };


  HueDocument.prototype.prettifyUsernameById = function (id) {
    var self = this;
    return self.prettifyUserName(self.idToUserMap[id]);
  }

  HueDocument.prototype.prettifyUserName = function (user) {
    user.prettyName = '';
    if (user.first_name) {
      user.prettyName += user.first_name + ' ';
    }
    if (user.last_name) {
      user.prettyName += user.last_name + ' ';
    }
    if (user.prettyName) {
      user.prettyName += '(' + user.username + ')';
    } else {
      user.prettyName += user.username;
    }
    return user.prettyName;
  };

  HueDocument.prototype.removeFromPerms = function (perms, id) {
    var self = this;
    $(perms).each(function (cnt, item) {
      if (item.id == id) {
        perms.splice(cnt, 1);
      }
    });
    self.persistPerms();
  };

  HueDocument.prototype.removeUserReadShare = function (user) {
    var self = this;
    self.removeFromPerms(self.definition().perms.read.users, user.id);
  };

  HueDocument.prototype.removeUserWriteShare = function (user) {
    var self = this;
    self.removeFromPerms(self.definition().perms.write.users, user.id);
  };

  HueDocument.prototype.removeGroupReadShare = function (group) {
    var self = this;
    self.removeFromPerms(self.definition().perms.read.groups, group.id);
  };

  HueDocument.prototype.removeGroupWriteShare = function (group) {
    var self = this;
    self.removeFromPerms(self.definition().perms.write.groups, group.id);
  };

  return HueDocument;
})();

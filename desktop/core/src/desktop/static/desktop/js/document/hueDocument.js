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

    self.selectedUserOrGroup = ko.observable();
    self.selectedPerm = ko.observable('read');

    self.availableUsersAndGroups = {};
  };

  HueDocument.prototype.initUserTypeahead = function (callback) {
    var self = this;
    $.getJSON('/desktop/api/users/autocomplete', function (data) {
      self.availableUsersAndGroups = data;
      self.prettifyUserNames(self.availableUsersAndGroups.users);
      var dropdown = [];
      var usermap = {};
      var groupmap = {};

      $.each(self.availableUsersAndGroups.users, function (i, user) {
        usermap[user.prettyName] = user;
        dropdown.push(user.prettyName);
      });

      $.each(self.availableUsersAndGroups.groups, function (i, group) {
        groupmap[group.name] = group;
        dropdown.push(group.name);
      });

      $("#documentShareTypeahead").typeahead({
        source: function (query, process) {
          process(dropdown);
        },
        matcher: function (item) {
          if (item.toLowerCase() === this.query.trim().toLowerCase()) {
            self.selectedUserOrGroup(usermap[item] ? usermap[item] : groupmap[item]);
            return true;
          } else if (item.toLowerCase().indexOf(this.query.trim().toLowerCase()) != -1) {
            self.selectedUserOrGroup(undefined);
            return true;
          }
        },
        sorter: function (items) {
          return items.sort();
        },
        highlighter: function (item) {
          var _icon = "fa";
          if (usermap[item]) {
            _icon += " fa-user";
          }
          else {
            _icon += " fa-users";
          }
          var regex = new RegExp('(' + this.query + ')', 'gi');
          return "<i class='" + _icon + "'></i> " + item.replace(regex, "<strong>$1</strong>");
        },
        updater: function (item) {
          self.selectedUserOrGroup(usermap[item] ? usermap[item] : groupmap[item]);
          return item;
        }
      });

      $("#documentShareTypeahead").on("keyup", function (e) {
        var _code = (e.keyCode ? e.keyCode : e.which);
        if (_code == 13) {
          self.handleTypeAheadSelection();
        }
      });

      if (typeof id == "function"){
        id();
      }
      callback();
    }).fail(function (response) {
      $(document).trigger("error", "There was an error processing your action: " + response.responseText);
    });
  };

  HueDocument.prototype.handleTypeAheadSelection = function () {
    var self = this;
    if (self.selectedUserOrGroup()) {
      if (typeof self.selectedUserOrGroup().username !== 'undefined') {
        self.definition().perms[self.selectedPerm()].users.push(self.selectedUserOrGroup());
      } else {
        self.definition().perms[self.selectedPerm()].groups.push(self.selectedUserOrGroup());
      }
      self.persistPerms();
    }
    self.selectedUserOrGroup(null);
    $("#documentShareTypeahead").val("");
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

    var fetchFunction = function () {
      self.apiHelper.fetchDocument({
        uuid: self.fileEntry.definition().uuid
      }).done(function (data) {
        self.prettifyUserNames(data.document.perms.write.users);
        self.prettifyUserNames(data.document.perms.read.users);
        self.definition(data.document);
        self.loading(false);
        self.loaded(true);
      }).fail(function () {
        self.hasErrors(true);
        self.loading(false);
        self.loaded(true);
      })
    };

    self.initUserTypeahead(fetchFunction);
  };

  HueDocument.prototype.prettifyUserNames = function (users) {
    $.each(users, function (idx, user) {
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
    });
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

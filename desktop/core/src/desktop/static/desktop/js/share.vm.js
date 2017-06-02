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


var shareViewModel;

function ShareViewModel(updateDocF) {
  var self = this;

  self.hasInitBeenCalled = false;
  self.hasSetupBeenCalled = false;

  self.selectedPerm = ko.observable('read');
  self.selectedPermLabel = ko.computed(function() {
    if (self.selectedPerm() == 'write') {
      return 'Modify';
    } else {
      return 'Read';
    }
  });

  self.selectedDoc = ko.observable(ko.mapping.fromJS({
    perms: {
      read: {
        users: [],
        groups: []
      },
      write: {
        users: [],
        groups: []
      }
    }
  }))

  self.updateDoc = updateDocF

  self.setDocId = function(docId) {
    if (docId == -1) { return false; }
    $.get('/desktop/api/doc/get', { id : docId }, function (data) {
      shareViewModel.selectedDoc(data)
    }).fail(function (response) {
      $(document).trigger("error", "There was an error processing your action: " + response.responseText);
    });
  }
}


function openShareModal() {
  $("#documentShareModal").modal("show");
  setupSharing(function(){
    $("#documentShareAddBtn").removeClass("disabled");
    $("#documentShareCaret").removeClass("disabled");
    $("#documentShareTypeahead").removeAttr("disabled");
    $(".notpretty").each(function(){
      $(this).text(prettifyUsername($(this).attr("data-id")));
    });
  });
}

function isShared() {
  if (!shareViewModel) { return false; }
  read = shareViewModel.selectedDoc().perms.read;
  return read.users.length + read.groups.length > 0
}

function prettifyUsername(userId) {
  var _user = null;
  if (self.hasSetupBeenCalled) {
    for (var i = 0; i < JSON_USERS_GROUPS.users.length; i++) {
      if (JSON_USERS_GROUPS.users[i].id == userId) {
        _user = JSON_USERS_GROUPS.users[i];
      }
    }
    if (_user != null) {
      return (_user.first_name != "" ? _user.first_name + " " : "") + (_user.last_name != "" ? _user.last_name + " " : "") + ((_user.first_name != "" || _user.last_name != "") ? "(" : "") + _user.username + ((_user.first_name != "" || _user.last_name != "") ? ")" : "");
    }
  }
  return "";
}

function initSharing(id, updateFunc) {
  if(! updateFunc) {
    updateFunc = function () {}
  }
  shareViewModel = new ShareViewModel(updateFunc);
  ko.cleanNode($(id)[0]);
  ko.applyBindings(shareViewModel, $(id)[0]);
  shareViewModel.hasInitBeenCalled = true;
  return shareViewModel;
}

function setupSharing(id, updateFunc) {
  if (shareViewModel == null || !shareViewModel.hasInitBeenCalled) {
    shareViewModel = initSharing(id, updateFunc);
  }

  if (! self.hasSetupBeenCalled){
    $.getJSON('/desktop/api/users/autocomplete', function (data) {
      self.hasSetupBeenCalled = true;
      JSON_USERS_GROUPS = data;
      dropdown = [];
      usermap = {};
      groupmap = {};

      $.each(JSON_USERS_GROUPS.users, function (i, user) {
        var _display = prettifyUsername(user.id);
        usermap[_display] = user;
        dropdown.push(_display);
      });

      $.each(JSON_USERS_GROUPS.groups, function (i, group) {
        groupmap[group.name] = group;
        dropdown.push(group.name);
      });

      $("#documentShareTypeahead").typeahead({
        source: function (query, process) {
          process(dropdown);
        },
        matcher: function (item) {
          if (item.toLowerCase().indexOf(this.query.trim().toLowerCase()) != -1) {
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
          selectedUserOrGroup = usermap[item] ? usermap[item] : groupmap[item];
          return item;
        }
      });

      $("#documentShareTypeahead").on("keyup", function (e) {
        var _code = (e.keyCode ? e.keyCode : e.which);
        if (_code == 13) {
          handleTypeaheadSelection();
        }
      });

      if (typeof id == "function"){
        id();
      }
    }).fail(function (response) {
      $(document).trigger("error", "There was an error processing your action: " + response.responseText);
    });

    $("#documentShareAddBtn").on("click", function () {
      if (! $(this).hasClass("disabled")){
        handleTypeaheadSelection();  
      }
    });
  }
  else {
    if (typeof id == "function"){
      id();
    }
  }

  return shareViewModel;
}

function updateSharePerm(perms, user) {
  $(perms).each(function (cnt, item) {
    if (item.id == user.id) {
      perms.splice(cnt, 1);
    }
  });
  shareViewModel.selectedDoc.valueHasMutated();
  shareDocFinal();
}

function removeUserReadShare(user) {
  updateSharePerm(shareViewModel.selectedDoc().perms.read.users, user);
}

function removeUserWriteShare(user) {
  updateSharePerm(shareViewModel.selectedDoc().perms.write.users, user);
}

function removeGroupReadShare(group) {
  updateSharePerm(shareViewModel.selectedDoc().perms.read.groups, group);
}

function removeGroupWriteShare(group) {
  updateSharePerm(shareViewModel.selectedDoc().perms.write.groups, group);
}

function changeDocumentSharePerm(perm) {
  shareViewModel.selectedPerm(perm);
}

function handleTypeaheadSelection() {
  if (selectedUserOrGroup != null) {
    if (selectedUserOrGroup.hasOwnProperty("username")) {
      shareViewModel.selectedDoc().perms[shareViewModel.selectedPerm()].users.push(selectedUserOrGroup);
    }
    else {
      shareViewModel.selectedDoc().perms[shareViewModel.selectedPerm()].groups.push(selectedUserOrGroup);
    }
    shareViewModel.selectedDoc.valueHasMutated();
    shareDocFinal();
  }
  selectedUserOrGroup = null;
  $("#documentShareTypeahead").val("");
}

function shareDocFinal() {
  var _postPerms = {
    read: {
      user_ids: [],
      group_ids: []
    },
    write: {
      user_ids: [],
      group_ids: []
    }
  }

  $(shareViewModel.selectedDoc().perms.read.users).each(function (cnt, item) {
    _postPerms.read.user_ids.push(item.id);
  });

  $(shareViewModel.selectedDoc().perms.read.groups).each(function (cnt, item) {
    _postPerms.read.group_ids.push(item.id);
  });

  $(shareViewModel.selectedDoc().perms.write.users).each(function (cnt, item) {
    _postPerms.write.user_ids.push(item.id);
  });

  $(shareViewModel.selectedDoc().perms.write.groups).each(function (cnt, item) {
    _postPerms.write.group_ids.push(item.id);
  });

  $.post("/desktop/api/doc/update_permissions", {
    doc_id: shareViewModel.selectedDoc().id,
    data: JSON.stringify(_postPerms)
  }, function (response) {
    if (response != null) {
      if (response.status != 0) {
        $(document).trigger("error", "There was an error processing your action: " + response.message);
      }
      else {
        shareViewModel.updateDoc(response.doc);
      }
    }
  }).fail(function (response) {
    $(document).trigger("error", "There was an error processing your action: " + response.responseText);
  });
}

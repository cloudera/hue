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


var errorCallback = function(response) {
  $(document).trigger("error", "There was an error processing your action: " + response.responseText);
};

function ShareViewModel(updateDocF) {
  var self = this;
  self.userMap = {};
  self.idToUserMap = {};
  self.groupMap = {};
  self.items = [];
  self.apiHelper = window.apiHelper;
  self.searchInput = ko.observable();
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

  self.docUuid;

  self.setDocUuid = function(docUuid) {
    if (docUuid === '') { return false; }
    self.docUuid = docUuid;
    var fetchDocumentsSuccessCallback = function (data) {
      readusers = data.document.perms.read.users.map(function(user){return user.id});
      writeusers = data.document.perms.write.users.map(function(user){return user.id});
      allusers = readusers.concat(writeusers);
      if (allusers.length > 0) {
        var successCallback = function (response) {
          $.each(response.users, function (i, user) {
            // Needed for getting prettyusername of already shared users
            shareViewModel.idToUserMap[user.id] = user;
          });
          shareViewModel.selectedDoc(data.document);
        };
        shareViewModel.apiHelper.fetchUsersByIds({
          userids: JSON.stringify(allusers),
          successCallback: successCallback,
          errorCallback: errorCallback
        });
      } else {
        shareViewModel.selectedDoc(data.document);
      }
    }
    shareViewModel.apiHelper.fetchDocuments({
      uuid: docUuid,
      successCallback: fetchDocumentsSuccessCallback,
      errorCallback: errorCallback
    });
  }
}

function openShareModal() {
  $("#documentShareModal").modal("show");
  setupSharing();
}

function isShared() {
  if (!shareViewModel) { return false; }
  read = shareViewModel.selectedDoc().perms.read;
  return read.users.length + read.groups.length > 0
}

function prettifyUsernameById(id) {
  return prettifyUsername(shareViewModel.idToUserMap[id]);
}

function prettifyUsername(user) {
  if (user != null && user.hasOwnProperty("username")) {
    return (user.first_name != "" ? user.first_name + " " : "") + (user.last_name != "" ? user.last_name + " " : "") + ((user.first_name != "" || user.last_name != "") ? "(" : "") + user.username + ((user.first_name != "" || user.last_name != "") ? ")" : "");
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
  return shareViewModel;
}

function setupSharing(id, updateFunc) {
  if (shareViewModel == null ) {
    shareViewModel = initSharing(id, updateFunc);
  }

  $("#documentShareAddBtn").on("click", function () {
    handleTypeaheadSelection();
  });

  return shareViewModel;
}

function source(request, callback) {

  var successCallback = function (data) {
    var JSON_USERS_GROUPS = data;
    shareViewModel.items = [];
    $.each(JSON_USERS_GROUPS.users, function (i, user) {
      var label = prettifyUsername(user);
      var highLightedLabel = hueUtils.highlight(label, request.term);
      shareViewModel.userMap[label] = user;
      shareViewModel.items.push({
        data: {
          "icon": "fa fa-user",
          "label": highLightedLabel
        },
        value: label
      });
      shareViewModel.idToUserMap[user.id] = user;
    });
    $.each(JSON_USERS_GROUPS.groups, function (i, group) {
      shareViewModel.groupMap[group.name] = group;
      var highLightedLabel = hueUtils.highlight(group.name, request.term);
      shareViewModel.items.push({
        data: {
          "icon": "fa fa-users",
          "label": highLightedLabel
        },
        value: group.name
      });
    });

    if(shareViewModel.items.length == 0){
      shareViewModel.items.push({
        'noMatch': true
      });
    }

    callback(shareViewModel.items);

    }

  shareViewModel.apiHelper.fetchUsersAndGroups({
    data: {filter: request.term},
    successCallback: successCallback,
    errorCallback: errorCallback
  });
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
  searchAutoCompInput = $("#userSearchAutocomp").val();
  selectedUserOrGroup = shareViewModel.userMap[searchAutoCompInput] ? shareViewModel.userMap[searchAutoCompInput] : shareViewModel.groupMap[searchAutoCompInput];
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
  $("#userSearchAutocomp").val('');
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

  $.post("/desktop/api2/doc/share", {
    uuid: JSON.stringify(shareViewModel.docUuid),
    data: JSON.stringify(_postPerms)
  }, function (response) {
    if (response != null) {
      if (response.status != 0) {
        $(document).trigger("error", "There was an error processing your action: " + response.message);
      }
      else {
        shareViewModel.setDocUuid(shareViewModel.docUuid);
      }
    }
  }).fail(function (response) {
    $(document).trigger("error", "There was an error processing your action: " + response.responseText);
  });
}

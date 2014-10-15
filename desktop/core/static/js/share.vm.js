function ShareViewModel(updateDocF) {
  var self = this;

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
}

function prettifyUsername(userId) {
  var _user = null;
  for (var i = 0; i < JSON_USERS_GROUPS.users.length; i++) {
    if (JSON_USERS_GROUPS.users[i].id == userId) {
      _user = JSON_USERS_GROUPS.users[i];
    }
  }
  if (_user != null) {
    return (_user.first_name != "" ? _user.first_name + " " : "") + (_user.last_name != "" ? _user.last_name + " " : "") + ((_user.first_name != "" || _user.last_name != "") ? "(" : "") + _user.username + ((_user.first_name != "" || _user.last_name != "") ? ")" : "");
  }
  return "";
}

function setupSharing(updateFunc, id) {
  shareViewModel = new ShareViewModel(updateFunc);
  ko.applyBindings(shareViewModel, $(id)[0]);

  $.getJSON('/desktop/api/users/autocomplete', function (data) {
    JSON_USERS_GROUPS = data;
    dropdown = [];
    map = {};

    $.each(JSON_USERS_GROUPS.users, function (i, user) {
      var _display = prettifyUsername(user.id);
      map[_display] = user;
      dropdown.push(_display);
    });

    $.each(JSON_USERS_GROUPS.groups, function (i, group) {
      map[group.name] = group;
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
        var _display = "";
        if (map[item].hasOwnProperty("username")) {
          _icon += " fa-user";
        }
        else {
          _icon += " fa-users";
        }
        var regex = new RegExp('(' + this.query + ')', 'gi');
        return "<i class='" + _icon + "'></i> " + item.replace(regex, "<strong>$1</strong>");
      },
      updater: function (item) {
        selectedUserOrGroup = map[item];
        return item;
      }
    });

    $("#documentShareTypeahead").on("keyup", function (e) {
      var _code = (e.keyCode ? e.keyCode : e.which);
      if (_code == 13) {
        handleTypeaheadSelection();
      }
    });
  });

  $("#documentShareAddBtn").on("click", function () {
    handleTypeaheadSelection();
  });

  return shareViewModel;
}


function removeUserReadShare(user) {
  $(shareViewModel.selectedDoc().perms.read.users).each(function (cnt, item) {
    if (item.id == user.id) {
      shareViewModel.selectedDoc().perms.read.users.splice(cnt, 1);
    }
  });
  shareViewModel.selectedDoc.valueHasMutated();
  shareDocFinal();
}

function removeUserWriteShare(user) {
  $(shareViewModel.selectedDoc().perms.write.users).each(function (cnt, item) {
    if (item.id == user.id) {
      shareViewModel.selectedDoc().perms.write.users.splice(cnt, 1);
    }
  });
  shareViewModel.selectedDoc.valueHasMutated();
  shareDocFinal();
}

function removeGroupReadShare(group) {
  $(shareViewModel.selectedDoc().perms.read.groups).each(function (cnt, item) {
    if (item.id == group.id) {
      shareViewModel.selectedDoc().perms.read.groups.splice(cnt, 1);
    }
  });
  shareViewModel.selectedDoc.valueHasMutated();
  shareDocFinal();
}

function removeGroupWriteShare(group) {
  $(shareViewModel.selectedDoc().perms.write.groups).each(function (cnt, item) {
    if (item.id == group.id) {
      shareViewModel.selectedDoc().perms.write.groups.splice(cnt, 1);
    }
  });
  shareViewModel.selectedDoc.valueHasMutated();
  shareDocFinal();
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
  });
}

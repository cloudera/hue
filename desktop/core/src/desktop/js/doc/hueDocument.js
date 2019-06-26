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

import $ from 'jquery';
import ko from 'knockout';

import apiHelper from 'api/apiHelper';
import hueUtils from 'utils/hueUtils';

class HueDocument {
  /**
   *
   * @param {Object} options
   * @param {HueFileEntry} options.fileEntry
   *
   * @constructor
   */
  constructor(options) {
    this.fileEntry = options.fileEntry;
    this.definition = ko.observable();
    this.loaded = ko.observable(false);
    this.loading = ko.observable(false);
    this.hasErrors = ko.observable(false);
    this.searchInput = ko.observable();
    this.selectedUserOrGroup = ko.observable();
    this.selectedPerm = ko.observable('read');

    this.userMap = {};
    this.idToUserMap = {};
    this.groupMap = {};
    this.items = [];
  }

  onShareAutocompleteUserEnter() {
    const searchAutoCompInput = $('#userSearchAutocomp').val();
    const selectedUserOrGroup = self.userMap[searchAutoCompInput]
      ? self.userMap[searchAutoCompInput]
      : self.groupMap[searchAutoCompInput];
    if (selectedUserOrGroup != null) {
      if (typeof selectedUserOrGroup.username !== 'undefined') {
        this.definition().perms[self.selectedPerm()].users.push(selectedUserOrGroup);
      } else {
        this.definition().perms[self.selectedPerm()].groups.push(selectedUserOrGroup);
      }
      this.persistPerms();
    }
    $('#userSearchAutocomp').val('');
  }

  shareAutocompleteUserSource(request, callback) {
    const self = this;
    const successCallback = jsonUserGroups => {
      self.items = [];
      jsonUserGroups.users.forEach(user => {
        const label = self.prettifyUsername(user);
        const highLightedLabel = hueUtils.highlight(label, request.term);
        self.userMap[label] = user;
        self.items.push({
          data: {
            icon: 'fa fa-user',
            label: highLightedLabel
          },
          value: label
        });
        self.idToUserMap[user.id] = user;
      });
      jsonUserGroups.groups.forEach(group => {
        self.groupMap[group.name] = group;
        const highLightedLabel = hueUtils.highlight(group.name, request.term);
        self.items.push({
          data: {
            icon: 'fa fa-users',
            label: highLightedLabel
          },
          value: group.name
        });
      });

      if (self.items.length === 0) {
        self.items.push({
          noMatch: true
        });
      }

      callback(self.items);
    };

    apiHelper.fetchUsersAndGroups({
      data: { filter: request.term },
      successCallback: successCallback,
      errorCallback: () => {}
    });
  }

  persistPerms() {
    const self = this;
    const postPerms = {
      read: {
        user_ids: self.definition().perms.read.users.map(user => user.id),
        group_ids: self.definition().perms.read.groups.map(group => group.id)
      },
      write: {
        user_ids: self.definition().perms.write.users.map(user => user.id),
        group_ids: self.definition().perms.write.groups.map(group => group.id)
      }
    };

    $.post(
      '/desktop/api2/doc/share',
      {
        uuid: JSON.stringify(self.fileEntry.definition().uuid),
        data: JSON.stringify(postPerms)
      },
      response => {
        if (response != null) {
          if (response.status !== 0) {
            $(document).trigger(
              'error',
              'There was an error processing your action: ' + response.message
            );
          } else {
            self.load();
          }
        }
      }
    ).fail(response => {
      $(document).trigger(
        'error',
        'There was an error processing your action: ' + response.responseText
      );
    });
  }

  load() {
    const self = this;
    if (self.loading()) {
      return;
    }

    self.loading(true);
    self.hasErrors(false);

    const fetchDocumentsSuccessCallback = data => {
      const readUsers = data.document.perms.read.users.map(user => user.id);
      const writeUsers = data.document.perms.write.users.map(user => user.id);
      const allUsers = readUsers.concat(writeUsers);
      if (allUsers.length > 0) {
        apiHelper.fetchUsersByIds({
          userids: JSON.stringify(allUsers),
          successCallback: response => {
            response.users.forEach(user => {
              // Needed for getting prettyusername of already shared users
              self.idToUserMap[user.id] = user;
            });
            self.definition(data.document);
          },
          errorCallback: () => {}
        });
      } else {
        self.definition(data.document);
      }
    };

    apiHelper
      .fetchDocument({
        uuid: self.fileEntry.definition().uuid
      })
      .done(data => {
        fetchDocumentsSuccessCallback(data);
        self.loading(false);
        self.loaded(true);
      })
      .fail(() => {
        self.hasErrors(true);
        self.loading(false);
        self.loaded(true);
      });
  }

  prettifyUsernameById(id) {
    return this.prettifyUsername(this.idToUserMap[id]);
  }

  prettifyUsername(user) {
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
  }

  removeFromPerms(perms, id) {
    const self = this;
    $(perms).each((cnt, item) => {
      if (item.id === id) {
        perms.splice(cnt, 1);
      }
    });
    self.persistPerms();
  }

  removeUserReadShare(user) {
    this.removeFromPerms(this.definition().perms.read.users, user.id);
  }

  removeUserWriteShare(user) {
    this.removeFromPerms(this.definition().perms.write.users, user.id);
  }

  removeGroupReadShare(group) {
    this.removeFromPerms(this.definition().perms.read.groups, group.id);
  }

  removeGroupWriteShare(group) {
    this.removeFromPerms(this.definition().perms.write.groups, group.id);
  }
}

export default HueDocument;

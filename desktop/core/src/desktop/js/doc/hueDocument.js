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
import * as ko from 'knockout';

import apiHelper from 'api/apiHelper';
import escapeOutput from 'utils/html/escapeOutput';
import highlight from 'utils/html/highlight';
import huePubSub from 'utils/huePubSub';

export const DOCUMENT_UPDATED_EVENT = 'hue.document.updated';

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
    this.selectedUserOrGroup = null;
    this.groupMap = {};
    this.items = [];

    huePubSub.subscribe(DOCUMENT_UPDATED_EVENT, definition => {
      if (this.definition() && this.definition().uuid === definition.uuid) {
        this.definition(definition);
      }
    });
  }

  isShared() {
    const perms = this.definition() && this.definition().perms;
    return (
      perms &&
      (perms.read.users.length > 0 ||
        perms.read.groups.length > 0 ||
        perms.write.users.length > 0 ||
        perms.write.groups.length > 0 ||
        perms.link_sharing_on)
    );
  }
  onShareAutocompleteSelectEnter(event, selectedItem) {
    const self = this;
    self.selectedUserOrGroup = selectedItem.item;
  }
  onShareAutocompleteUserEnter() {
    const self = this;
    const searchAutoCompInput = $('#shareDocUserInput').val();
    if (self.selectedUserOrGroup && self.selectedUserOrGroup.value === searchAutoCompInput) {
      const selectedValue =
        self.selectedUserOrGroup.type === 'user'
          ? self.userMap[searchAutoCompInput]
          : self.groupMap[searchAutoCompInput];
      if (selectedValue != null) {
        if (typeof selectedValue.username !== 'undefined') {
          this.definition().perms[self.selectedPerm()].users.push(selectedValue);
        } else {
          this.definition().perms[self.selectedPerm()].groups.push(selectedValue);
        }
        this.persistPerms();
      }
    }
    self.selectedUserOrGroup = null;
    $('#shareDocUserInput').val('');
  }
  shareAutocompleteUserSource(request, callback) {
    const self = this;
    const successCallback = jsonUserGroups => {
      self.items = [];
      jsonUserGroups.users.forEach(user => {
        const label = escapeOutput(self.prettifyUsername(user));
        const highLightedLabel = highlight(label, request.term);
        self.userMap[label] = user;
        self.items.push({
          data: {
            icon: 'fa fa-user',
            label: highLightedLabel
          },
          value: label,
          type: 'user'
        });
        self.idToUserMap[user.id] = user;
      });
      jsonUserGroups.groups.forEach(group => {
        self.groupMap[group.name] = group;
        const highLightedLabel = highlight(escapeOutput(group.name), request.term);
        self.items.push({
          data: {
            icon: 'fa fa-users',
            label: highLightedLabel
          },
          value: group.name,
          type: 'group'
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

  persistLinkSharingPerms(perm) {
    // Perm is either: read, write, off
    const self = this;

    $.post(
      '/desktop/api2/doc/share/link',
      {
        uuid: JSON.stringify(self.fileEntry.definition().uuid),
        perm: JSON.stringify(perm)
      },
      response => {
        if (response != null) {
          if (response.status !== 0) {
            $(document).trigger(
              'error',
              'There was an error processing your action: ' + response.message
            );
          } else {
            // self.load();
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

  load(successCallback, errorCallback) {
    const self = this;
    if (self.loading()) {
      return;
    }

    self.loading(true);
    self.hasErrors(false);

    const fetchDocumentsSuccessCallback = async data =>
      new Promise(resolve => {
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
              resolve();
            },
            errorCallback: () => {}
          });
        } else {
          self.definition(data.document);
          resolve();
        }
      });

    apiHelper
      .fetchDocument({
        uuid: self.fileEntry.definition().uuid
      })
      .done(async data => {
        await fetchDocumentsSuccessCallback(data);
        self.loading(false);
        self.loaded(true);
        if (successCallback) {
          successCallback(this);
        }
      })
      .fail(() => {
        self.hasErrors(true);
        self.loading(false);
        self.loaded(true);
        if (errorCallback) {
          errorCallback();
        }
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

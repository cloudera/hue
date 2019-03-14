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

import componentUtils from './componentUtils';
import I18n from 'utils/i18n';
import hueUtils from 'utils/hueUtils';

const TEMPLATE = `
  <script type="text/html" id="sentry-privileges-component-role">
    <div class="acl-block-title">
      <i class="fa fa-cube muted"></i> <a class="pointer" data-bind="click: function(){  $parents[0].showRole($data); }"><span data-bind="text: name"></span></a>
    </div>
    <div data-bind="template: { name: 'sentry-privileges-component-privilege', foreach: privilegesForView }"></div>
    <div class="acl-block acl-actions">
      <span class="pointer" data-bind="visible: privilegesForViewTo() < privileges().length, click: function(){ privilegesForViewTo(privilegesForViewTo() + 50) }" title="${I18n(
        'Show 50 more...'
      )}"><i class="fa fa-ellipsis-h"></i></span>
      <span class="pointer" data-bind="click: addPrivilege, visible: $parents[0].isSentryAdmin && !$parents[0].readOnly" title="${I18n(
        'Add privilege'
      )}"><i class="fa fa-plus"></i></span>
      <span class="pointer" data-bind="click: function() { $parents[0].listSentryPrivilegesByAuthorizable() }, visible: privilegesChanged().length > 0" title="${I18n(
        'Undo'
      )}"> &nbsp; <i class="fa fa-undo"></i></span>
      <span class="pointer" data-bind="click: function() { $parents[0].deletePrivilegeModal($data) }, visible: privilegesChanged().length > 0" title="${I18n(
        'Save'
      )}"> &nbsp; <i class="fa fa-save"></i></span>
    </div>
  </script>

  <script type="text/html" id="sentry-privileges-component-privilege">
    <div data-bind="visible: status() != 'deleted' && status() != 'alreadydeleted'" class="acl-block acl-block-airy">
      <!-- ko if: editing -->
      <div class="pull-right privilege-actions" data-bind="visible: (grantOption() || $parents[1].isSentryAdmin) && !$parents[1].readOnly">
        <a class="pointer" style="margin-right: 4px" data-bind="click: function() { if (editing()) { editing(false); }}"><i class="fa fa-eye"></i></a>
        <a class="pointer" style="margin-right: 4px" data-bind="click: remove"><i class="fa fa-times"></i></a>
      </div>
    
      <div class="inline-block" style="vertical-align: middle">
        <a class="pointer" style="padding-top: 4px" data-bind="click: function(){ privilegeType('db'); action($parents[1].availableActions(privilegeScope())[0]) }">
          <i class="fa fa-fw fa-1halfx muted" data-bind="css: {'fa-circle-o': privilegeType() != 'db' , 'fa-check-circle-o': privilegeType() == 'db'}"></i>
        </a>
      </div>
      <input type="text" data-bind="hiveChooser: $data.path, enable: privilegeType() == 'db', apiHelperUser: '${
        window.LOGGED_USERNAME
      }', apiHelperType: 'hive'" placeholder="dbName.tableName <CTRL+SPACE>">
    
      <div class="inline-block" style="vertical-align: middle">
        <a class="pointer" style="padding-top: 4px" data-bind="click: function(){ privilegeType('uri'); action('ALL'); }">
          <i class="fa fa-fw fa-1halfx muted" data-bind="css: {'fa-circle-o': privilegeType() != 'uri' , 'fa-check-circle-o': privilegeType() == 'uri'}"></i>
        </a>
      </div>
      <input type="text" data-bind="filechooser: $data.URI, enable: privilegeType() == 'uri', valueUpdate: 'afterkeydown'" placeholder="URI">
    
      <select data-bind="options: $parents[1].availableActions(privilegeScope()), value: $data.action, enable: (privilegeType() == 'db')" style="width: 100px; margin-bottom: 0"></select>
    
      <div class="margin-top-10">
        <label class="checkbox pull-left"><input type="checkbox" data-bind="checked: grantOption"> ${I18n(
          'With grant'
        )}</label>
        <div class="inline-block margin-left-10" style="margin-top: 6px">
          <a class="pointer showAdvanced" data-bind="click: function(){ showAdvanced(true); }, visible: !showAdvanced()"><i class="fa fa-cog"></i> ${I18n(
            'Show advanced'
          )}</a>
          <a class="pointer showAdvanced" data-bind="click: function(){ showAdvanced(false); }, visible: showAdvanced()"><i class="fa fa-cog"></i> ${I18n(
            'Hide advanced'
          )}</a>
        </div>
        <div class="clearfix"></div>
      </div>
    
      <div class="acl-block-section" data-bind="visible: showAdvanced" style="margin-top: 0">
        ${I18n(
          'Server'
        )} <input type="text" data-bind="value: serverName" placeholder="serverName" style="margin-left: 6px">
      </div>
      <!-- /ko -->
  
      <!-- ko ifnot: editing -->
      <div class="pull-right privilege-actions" data-bind="visible: (grantOption() || $parents[1].isSentryAdmin) && !$parents[1].readOnly">
        <a title="${I18n(
          'Edit this privilege'
        )}" class="pointer" style="margin-right: 4px" data-bind="visible: $parents[1].isSentryAdmin, click: function() { if (! editing()) { editing(true); }}"><i class="fa fa-pencil"></i></a>
        <a title="${I18n(
          'Delete this privilege'
        )}" class="pointer" style="margin-right: 4px" data-bind="visible: $parents[1].isSentryAdmin, click: remove"><i class="fa fa-times"></i></a>
      </div>
  
      <span class="muted" data-bind="text: privilegeScope, attr: {title: moment(timestamp()).fromNow()}"></span>
      <!-- ko if: grantOption -->
        <i class="fa fa-unlock muted" title="${I18n('With grant option')}"></i>
      <!-- /ko -->
      <span data-bind="visible: metastorePath() != '' && privilegeType() == 'db'">
        <a data-bind="hueLink: metastorePath()" class="muted" style="margin-left: 4px" title="${I18n(
          'Open in Table Browser...'
        )}"><i class="fa fa-external-link"></i></a>
      </span>
      <br/>
  
      server=<span data-bind="text: serverName"></span>
  
      <!-- ko if: privilegeType() == 'db' -->
      <span data-bind="visible: dbName">
        <i class="fa fa-long-arrow-right"></i> db=<a class="pointer" data-bind="click: function(){ $parents[1].linkToBrowse(dbName()) }" title="${I18n(
          'Browse db privileges'
        )}"><span data-bind="text: dbName"></span></a>
      </span>
      <span data-bind="visible: tableName">
        <i class="fa fa-long-arrow-right"></i> table=<a class="pointer" data-bind="click: function(){ $parents[1].linkToBrowse(dbName() + '.' + tableName()) }" title="${I18n(
          'Browse table privileges'
        )}"><span data-bind="text: tableName"></span></a>
      </span>
      <span data-bind="visible: columnName">
        <i class="fa fa-long-arrow-right"></i> column=<a class="pointer" data-bind="click: function(){ $parents[1].linkToBrowse(dbName() + '.' + tableName() + '.' + columnName()) }" title="${I18n(
          'Browse column privileges'
        )}"><span data-bind="text: columnName"></span></a>
      </span>
      <!-- /ko -->
  
      <!-- ko if: privilegeType() == 'uri' -->
      <i class="fa fa-long-arrow-right"></i> <i class="fa fa-file-o"></i> <i class="fa fa-long-arrow-right"></i> <a data-bind="hueLink: '/filebrowser/view=/' + URI().split('/')[3]"><span data-bind="text: URI"></span></a>
      <!-- /ko -->
  
      <i class="fa fa-long-arrow-right"></i> action=<span data-bind="text: action"></span>
      <!-- /ko -->
    </div>
  </script>

  <!-- ko hueSpinner: { spin: isLoadingPrivileges, inline: true } --><!-- /ko -->
  <!-- ko if: roles().length -->
  <div data-bind="template: { name: 'sentry-privileges-component-role', foreach: roles }"></div>
  <!-- /ko -->
  <!-- ko ifnot: roles().length -->
  <em>${I18n('No privileges found for the selected object.')}</em>
  <!-- /ko -->
  
  <div id="sentryPrivilegesComponentDeletePrivilegeModal" class="modal hide fade in" role="dialog">
    <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal" aria-label="${I18n(
        'Close'
      )}"><span aria-hidden="true">&times;</span></button>
      <h2 class="modal-title">${I18n('Confirm the deletion?')}</h2>
    </div>
    <div class="modal-body">
      ${I18n(
        'Sentry will recursively delete the SERVER or DATABASE privileges you marked for deletion.'
      )}
    </div>
    <div class="modal-footer">
      <button class="btn" data-dismiss="modal" aria-hidden="true">${I18n('Cancel')}</button>
      <button data-loading-text="${I18n(
        'Deleting...'
      )}" class="btn btn-danger" data-bind="click: function() { roleToUpdate().savePrivileges(roleToUpdate()); }">${I18n(
  'Yes, delete'
)}</button>
    </div>
  </div>
`;

class Privilege {
  constructor(vm, privilege) {
    const self = this;

    self.id = ko.observable(
      typeof privilege.id != 'undefined' && privilege.id != null ? privilege.id : ''
    );
    self.roleName = ko.observable(
      typeof privilege.roleName != 'undefined' && privilege.roleName != null
        ? privilege.roleName
        : ''
    );
    self.status = ko.observable(
      typeof privilege.status != 'undefined' && privilege.status != null ? privilege.status : ''
    );
    self.editing = ko.observable(
      typeof privilege.editing != 'undefined' && privilege.editing != null
        ? privilege.editing
        : false
    );
    self.serverName = ko.observable(
      typeof privilege.serverName != 'undefined' && privilege.serverName != null
        ? privilege.serverName
        : ''
    );
    self.serverName.subscribe(() => {
      if (self.status() === '') {
        self.status('modified');
      }
    });
    self.dbName = ko.observable(
      typeof privilege.dbName != 'undefined' && privilege.dbName != null ? privilege.dbName : ''
    );
    self.dbName.subscribe(() => {
      if (self.status() === '') {
        self.status('modified');
      }
    });
    self.tableName = ko.observable(
      typeof privilege.tableName != 'undefined' && privilege.tableName != null
        ? privilege.tableName
        : ''
    );
    self.tableName.subscribe(() => {
      if (self.status() === '') {
        self.status('modified');
      }
    });
    self.columnName = ko.observable(
      typeof privilege.columnName != 'undefined' && privilege.columnName != null
        ? privilege.columnName
        : ''
    );
    self.columnName.subscribe(() => {
      if (self.status() === '') {
        self.status('modified');
      }
    });
    self.URI = ko.observable(
      typeof privilege.URI != 'undefined' && privilege.URI != null ? privilege.URI : ''
    );
    self.URI.subscribe(() => {
      if (self.status() === '') {
        self.status('modified');
      }
    });
    self.action = ko.observable(
      typeof privilege.action != 'undefined' && privilege.action != null
        ? privilege.action
        : 'SELECT'
    );
    self.action.subscribe(() => {
      if (self.status() === '') {
        self.status('modified');
      }
    });
    self.timestamp = ko.observable(
      typeof privilege.timestamp != 'undefined' && privilege.timestamp != null
        ? privilege.timestamp
        : 0
    );
    self.grantOption = ko.observable(
      typeof privilege.grantOption != 'undefined' && privilege.grantOption != null
        ? privilege.grantOption
        : false
    );
    self.grantOption.subscribe(() => {
      if (self.status() === '') {
        self.status('modified');
      }
    });

    // UI
    self.privilegeType = ko.observable(
      typeof privilege.privilegeScope != 'undefined' && privilege.privilegeScope === 'URI'
        ? 'uri'
        : 'db'
    );
    self.showAdvanced = ko.observable(false);
    self.path = ko.computed({
      read: function() {
        if (self.columnName().length > 0) {
          return self.dbName() + '.' + self.tableName() + '.' + self.columnName();
        } else if (self.tableName().length > 0) {
          return self.dbName() + '.' + self.tableName();
        } else {
          return self.dbName();
        }
      },
      write: function(value) {
        const _parts = value.split('.');
        this.dbName(_parts[0]);
        this.tableName(_parts.length > 1 ? _parts[1] : '');
        this.columnName(_parts.length > 2 ? _parts[2] : '');
      },
      owner: self
    });

    self.metastorePath = ko.computed(() => {
      if (self.columnName().length > 0) {
        return (
          '/metastore/table/' + self.dbName() + '/' + self.tableName() + '#col=' + self.columnName()
        );
      } else if (self.tableName().length > 0) {
        return '/metastore/table/' + self.dbName() + '/' + self.tableName();
      } else if (self.dbName().length > 0) {
        return '/metastore/tables/' + self.dbName();
      } else {
        return '';
      }
    });

    function getPrivilegeScope() {
      if (self.privilegeType() === 'uri') {
        return 'URI';
      } else if (self.columnName().length > 0) {
        return 'COLUMN';
      } else if (self.tableName().length > 0) {
        return 'TABLE';
      } else if (self.dbName().length > 0) {
        return 'DATABASE';
      } else {
        return 'SERVER';
      }
    }

    self.privilegeScope = ko.observable(
      typeof privilege.privilegeScope != 'undefined'
        ? privilege.privilegeScope
        : getPrivilegeScope()
    );

    self.privilegeType.subscribe(() => {
      self.privilegeScope(getPrivilegeScope());
    });

    self.columnName.subscribe(() => {
      self.privilegeScope(getPrivilegeScope());
    });

    self.tableName.subscribe(() => {
      self.privilegeScope(getPrivilegeScope());
    });

    self.dbName.subscribe(() => {
      self.privilegeScope(getPrivilegeScope());
    });

    self.remove = function(privilege) {
      if (privilege.status() === 'new') {
        privilege.status('alreadydeleted');
      } else {
        privilege.status('deleted');
      }
    };
  }
}

class Role {
  constructor(vm, role) {
    const self = this;

    self.name = ko.observable(
      typeof role.name != 'undefined' && role.name != null ? role.name : ''
    );
    self.name.subscribe(value => {
      let _found = false;
      vm.role().isEditing(false);
      ko.utils.arrayForEach(vm.roles(), role => {
        if (role.name() === value) {
          vm.role(role);
          _found = true;
        }
      });
      if (_found) {
        vm.role().isEditing(true);
        vm.list_sentry_privileges_by_role(vm.role());
        $(document).trigger('destroyTypeahead');
      }
    });
    self.selected = ko.observable(false);
    self.handleSelect = function() {
      self.selected(!self.selected());
    };

    self.groups = ko.observableArray();
    self.originalGroups = ko.observableArray();
    self.groups.extend({ rateLimit: 300 });
    self.originalGroups.extend({ rateLimit: 300 });
    $.each(
      typeof role.groups != 'undefined' && role.groups != null ? role.groups : [],
      (index, group) => {
        self.groups.push(group);
        self.originalGroups.push(group);
      }
    );
    self.privileges = ko.observableArray(); // Not included in the API
    self.originalPrivileges = ko.observableArray(); // Not included in the API
    self.privilegesForViewTo = ko.observable(49);
    self.showPrivileges = ko.observable(false);
    self.showPrivileges.subscribe(value => {
      const _expanded = vm.expandedRoles();
      if (value) {
        if (_expanded.indexOf(self.name()) === -1) {
          _expanded.push(self.name());
        }
      } else if (_expanded.indexOf(self.name()) > -1) {
        _expanded.splice(_expanded.indexOf(self.name()), 1);
      }
      vm.expandedRoles(_expanded);
    });

    self.showEditGroups = ko.observable(false);
    self.isEditing = ko.observable(false);
    self.isLoading = ko.observable(false);
    self.isValid = ko.computed(() => {
      return (
        self.name().length > 0 &&
        $.grep(self.privileges(), privilege => {
          return privilege.privilegeType() === 'uri' && privilege.URI() === '';
        }).length === 0
      );
    });

    self.privilegesChanged = ko.computed(() => {
      return $.grep(self.privileges(), privilege => {
        return ['new', 'deleted', 'modified'].indexOf(privilege.status()) !== -1;
      });
    });

    self.groupsChanged = ko.computed(() => {
      return !(
        $(self.groups()).not(self.originalGroups()).length === 0 &&
        $(self.originalGroups()).not(self.groups()).length === 0
      );
    });
    self.groupsChanged.extend({ rateLimit: 300 });

    self.privilegesForView = ko.computed(() => {
      return self.privileges().slice(0, self.privilegesForViewTo());
    });

    self.reset = function() {
      self.name('');
      self.groups.removeAll();
      self.privileges.removeAll();
      self.isEditing(false);
    };

    self.addGroup = function() {
      self.groups.push('');
    };

    self.addPrivilege = function() {
      self.privileges.push(
        new Privilege(vm, {
          serverName: vm.server(),
          status: 'new',
          editing: true,
          dbName: vm.db(),
          tableName: vm.table(),
          columnName: vm.column()
        })
      );
    };

    self.resetGroups = function() {
      self.groups.removeAll();
      $.each(self.originalGroups(), (index, group) => {
        self.groups.push(group);
      });
    };

    self.saveGroups = function() {
      $('.jHueNotify').remove();
      $.post(
        '/security/api/hive/update_role_groups',
        {
          role: ko.mapping.toJSON(self)
        },
        data => {
          if (data.status === 0) {
            self.showEditGroups(false);
            self.originalGroups.removeAll();
            $.each(self.groups(), (index, group) => {
              self.originalGroups.push(group);
            });
          } else {
            $(document).trigger('error', data.message);
          }
        }
      ).fail(xhr => {
        $(document).trigger('error', xhr.responseText);
      });
    };

    self.create = function() {
      $('.jHueNotify').remove();
      if (self.isValid()) {
        self.isLoading(true);
        $.post(
          '/security/api/hive/create_role',
          {
            role: ko.mapping.toJSON(self)
          },
          data => {
            if (data.status === 0) {
              $(document).trigger('info', data.message);
              vm.showCreateRole(false);
              self.reset();
              const role = new Role(vm, data.role);
              role.showPrivileges(true);
              vm.originalRoles.unshift(role);
              vm.listSentryPrivilegesByAuthorizable();
              $(document).trigger('createdRole');
            } else {
              $(document).trigger('error', data.message);
            }
          }
        )
          .fail(xhr => {
            $(document).trigger('error', xhr.responseText);
          })
          .always(() => {
            self.isLoading(false);
          });
      }
    };

    self.update = function() {
      $('.jHueNotify').remove();
      if (self.isValid()) {
        self.isLoading(true);
        $.post(
          '/security/api/hive/save_privileges',
          {
            role: ko.mapping.toJSON(self)
          },
          data => {
            if (data.status === 0) {
              $(document).trigger('info', data.message);
              vm.showCreateRole(false);
              vm.listSentryPrivilegesByAuthorizable();
              $(document).trigger('createdRole');
            } else {
              $(document).trigger('error', data.message);
            }
          }
        )
          .fail(xhr => {
            $(document).trigger('error', xhr.responseText);
          })
          .always(() => {
            self.isLoading(false);
          });
      }
    };

    self.remove = function(role) {
      $('.jHueNotify').remove();
      self.isLoading(true);
      $.post(
        '/security/api/hive/drop_sentry_role',
        {
          roleName: role.name
        },
        data => {
          if (data.status === 0) {
            vm.removeRole(role.name());
            vm.listSentryPrivilegesByAuthorizable();
            $(document).trigger('removedRole');
          } else {
            $(document).trigger('error', data.message);
          }
        }
      )
        .fail(xhr => {
          $(document).trigger('error', xhr.responseText);
        })
        .always(() => {
          self.isLoading(false);
        });
    };

    self.savePrivileges = function(role) {
      $('.jHueNotify').remove();
      $.post(
        '/security/api/hive/save_privileges',
        {
          role: ko.mapping.toJSON(role)
        },
        data => {
          if (data.status === 0) {
            vm.listSentryPrivilegesByAuthorizable();
            $(document).trigger('createdRole');
          } else {
            $(document).trigger('error', data.message);
          }
        }
      ).fail(xhr => {
        $(document).trigger('error', xhr.responseText);
      });
    };
  }
}

const _create_authorizable_from_ko = (server, path) => {
  if (path != null) {
    const paths = path.split(/[.]/);
    return {
      server: server,
      db: paths[0] ? paths[0] : null,
      table: paths[1] ? paths[1] : null,
      column: paths[2] ? paths[2] : null
    };
  }
};

const _create_ko_privilege = privilege =>
  new Privilege(self, {
    privilegeScope: privilege.scope,
    serverName: privilege.server,
    dbName: privilege.database,
    tableName: privilege.table,
    columnName: privilege.column,
    URI: privilege.URI,
    action: privilege.action,
    timestamp: privilege.timestamp,
    roleName: privilege.roleName,
    grantOption: privilege.grantOption,
    id: hueUtils.UUID()
  });

class SentryPrivilegesViewModel {
  constructor(params) {
    const self = this;
    self.server = ko.observable(params.server);
    self.path = ko.observable(params.path);
    self.isSentryAdmin = params.isSentryAdmin;
    self.readOnly = !!params.readOnly;
    self.apiVersion = params.apiVersion || 'v1';
    self.apiType = params.apiType || 'hive';
    self.showFilter = params.showFilter;
    self.enableCreateRole = params.enableCreateRole;

    self.path.subscribe(self.listSentryPrivilegesByAuthorizable);

    self.db = ko.computed(() => {
      const db = self.path().split(/[.]/)[0];
      return db ? db : null;
    });
    self.table = ko.computed(() => {
      const table = self.path().split(/[.]/)[1];
      return table ? table : null;
    });
    self.column = ko.computed(() => {
      const column = self.path().split(/[.]/)[2];
      return column ? column : null;
    });
    self.metastorePath = ko.computed(() => {
      if (self.column()) {
        return '/metastore/table/' + self.db() + '/' + self.table() + '#col=' + self.column();
      } else if (self.table()) {
        return '/metastore/table/' + self.db() + '/' + self.table();
      } else if (self.db()) {
        return '/metastore/tables/' + self.db();
      } else {
        return '/metastore/databases';
      }
    });

    self.privileges = ko.observableArray();
    self.roles = ko.observableArray();
    self.roleToUpdate = ko.observable();

    self.isLoadingPrivileges = ko.observable(false);

    self.availableActions = function(scope) {
      let actions = ['SELECT', 'INSERT', 'ALL'];
      const databaseActions = ['CREATE'];
      const tableActions = ['REFRESH', 'ALTER', 'DROP'];
      switch (scope) {
        case 'SERVER':
          actions = actions.concat(databaseActions).concat(tableActions);
          break;
        case 'DATABASE':
          actions = actions.concat(databaseActions);
          break;
        case 'TABLE':
          actions = actions.concat(tableActions);
          break;
      }
      return ko.observableArray(actions.sort());
    };

    self.deletePrivilegeModal = function(role) {
      const cascadeDeletes = role
        .privilegesChanged()
        .filter(
          privilege =>
            privilege.status() === 'deleted' &&
            (privilege.privilegeScope() === 'SERVER' || privilege.privilegeScope() === 'DATABASE')
        );
      if (cascadeDeletes.length > 0) {
        self.roleToUpdate(role);
        $('#sentryPrivilegesComponentDeletePrivilegeModal').modal('show');
      } else {
        role.savePrivileges(role);
      }
    };

    self.listSentryPrivilegesByAuthorizable = function() {
      self.isLoadingPrivileges(true);
      $.ajax({
        type: 'POST',
        url: '/security/api/hive/list_sentry_privileges_by_authorizable',
        data: {
          groupName: '',
          roleSet: ko.mapping.toJSON({ all: true, roles: [] }),
          authorizableHierarchy: ko.mapping.toJSON(
            _create_authorizable_from_ko(self.server(), self.path())
          )
        },
        success: function(data) {
          if (data.status === 0) {
            self.roles([]);
            const _privileges = [];
            $.each(data.privileges, (index, item) => {
              if (typeof window.skipList === 'undefined' || window.skipList === false) {
                let _role = null;
                self.roles().forEach(role => {
                  if (role.name() === item.roleName) {
                    _role = role;
                  }
                });
                if (_role == null) {
                  const _idx = self.roles.push(new Role(self, { name: item.roleName }));
                  _role = self.roles()[_idx - 1];
                }

                const privilege = _create_ko_privilege(item);
                const privilegeCopy = _create_ko_privilege(item);
                privilegeCopy.id(privilege.id());
                _role.privileges.push(privilege);
                _role.originalPrivileges.push(privilegeCopy);

                _privileges.push(privilege);
              }
            });
            if (typeof window.skipList === 'undefined' || window.skipList === false) {
              self.privileges(_privileges);
            }
          } else {
            $(document).trigger('error', data.message);
          }
        }
      })
        .fail(xhr => {
          $(document).trigger('error', xhr.responseText);
        })
        .always(() => {
          self.isLoadingPrivileges(false);
        });
    };

    self.linkToBrowse = function(path) {
      // TODO: implement smart linking
    };

    self.listSentryPrivilegesByAuthorizable();
  }
}

componentUtils.registerComponent('hue-sentry-privileges', SentryPrivilegesViewModel, TEMPLATE);

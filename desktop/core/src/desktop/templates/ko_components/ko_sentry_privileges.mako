## Licensed to Cloudera, Inc. under one
## or more contributor license agreements.  See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  Cloudera, Inc. licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.

<%!
from desktop import conf
from desktop.lib.i18n import smart_unicode

from django.utils.translation import ugettext as _
from desktop.views import _ko
%>

<%def name="sentryPrivileges()">

  <script type="text/html" id="sentry-privileges-component-template">
    <!-- ko hueSpinner: { spin: isLoadingPrivileges, inline: true } --><!-- /ko -->
    <!-- ko if: roles().length -->
    <div data-bind="template: { name: 'sentry-privileges-component-role', foreach: roles }"></div>
    <!-- /ko -->
    <!-- ko ifnot: roles().length -->
    <em>${ _('No privileges found for the selected object.') }</em>
    <!-- /ko -->

    <div id="sentryPrivilegesComponentDeletePrivilegeModal" class="modal hide fade in" role="dialog">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
        <h2 class="modal-title">${ _('Confirm the deletion?') }</h2>
      </div>
      <div class="modal-body">
        ${ _('Sentry will recursively delete the SERVER or DATABASE privileges you marked for deletion.') }
      </div>
      <div class="modal-footer">
        <button class="btn" data-dismiss="modal" aria-hidden="true">${ _('Cancel') }</button>
        <button data-loading-text="${ _('Deleting...') }" class="btn btn-danger" data-bind="click: function() { roleToUpdate().savePrivileges(roleToUpdate()); }">${ _('Yes, delete') }</button>
      </div>
    </div>

  </script>


<script type="text/html" id="sentry-privileges-component-role">
  <div class="acl-block-title">
    <i class="fa fa-cube muted"></i> <a class="pointer" data-bind="click: function(){  $parents[0].showRole($data); }"><span data-bind="text: name"></span></a>
  </div>
  <div data-bind="template: { name: 'sentry-privileges-component-privilege', foreach: privilegesForView }"></div>
  <div class="acl-block acl-actions">
    <span class="pointer" data-bind="visible: privilegesForViewTo() < privileges().length, click: function(){ privilegesForViewTo(privilegesForViewTo() + 50) }" title="${ _('Show 50 more...') }"><i class="fa fa-ellipsis-h"></i></span>
    <span class="pointer" data-bind="click: addPrivilege, visible: $parents[0].isSentryAdmin && !$parents[0].readOnly" title="${ _('Add privilege') }"><i class="fa fa-plus"></i></span>
    <span class="pointer" data-bind="click: function() { $parents[0].listSentryPrivilegesByAuthorizable() }, visible: privilegesChanged().length > 0" title="${ _('Undo') }"> &nbsp; <i class="fa fa-undo"></i></span>
    <span class="pointer" data-bind="click: function() { $parents[0].deletePrivilegeModal($data) }, visible: privilegesChanged().length > 0" title="${ _('Save') }"> &nbsp; <i class="fa fa-save"></i></span>
  </div>
</script>

<script type="text/html" id="sentry-privileges-component-privilege">
<div data-bind="visible: status() != 'deleted' && status() != 'alreadydeleted'" class="acl-block acl-block-airy">

  <!-- ko if: editing -->
    <div class="pull-right privilege-actions" data-bind="visible: (grantOption() || $parents[1].isSentryAdmin) && !$parents[1].readOnly">
##       <a title="${ _('Grant this privilege') }" class="pointer" style="margin-right: 4px" data-bind="click: function(){ $parents[1].grantToPrivilege($data); $('#grantPrivilegeModal').modal('show'); }"><i class="fa fa-send"></i></a>
      <a class="pointer" style="margin-right: 4px" data-bind="click: function() { if (editing()) { editing(false); }}"><i class="fa fa-eye"></i></a>
      <a class="pointer" style="margin-right: 4px" data-bind="click: remove"><i class="fa fa-times"></i></a>
    </div>

    <div class="inline-block" style="vertical-align: middle">
      <a class="pointer" style="padding-top: 4px" data-bind="click: function(){ privilegeType('db'); action($parents[1].availableActions(privilegeScope())[0]) }">
        <i class="fa fa-fw fa-1halfx muted" data-bind="css: {'fa-circle-o': privilegeType() != 'db' , 'fa-check-circle-o': privilegeType() == 'db'}"></i>
      </a>
    </div>
    <input type="text" data-bind="hivechooser: $data.path, enable: privilegeType() == 'db', apiHelperUser: '${ user }', apiHelperType: 'hive'" placeholder="dbName.tableName <CTRL+SPACE>">

    <div class="inline-block" style="vertical-align: middle">
      <a class="pointer" style="padding-top: 4px" data-bind="click: function(){ privilegeType('uri'); action('ALL'); }">
        <i class="fa fa-fw fa-1halfx muted" data-bind="css: {'fa-circle-o': privilegeType() != 'uri' , 'fa-check-circle-o': privilegeType() == 'uri'}"></i>
      </a>
    </div>
    <input type="text" data-bind="filechooser: $data.URI, enable: privilegeType() == 'uri', valueUpdate: 'afterkeydown'" placeholder="URI">

    <select data-bind="options: $parents[1].availableActions(privilegeScope()), value: $data.action, enable: (privilegeType() == 'db')" style="width: 100px; margin-bottom: 0"></select>

    <div class="margin-top-10">
      <label class="checkbox pull-left"><input type="checkbox" data-bind="checked: grantOption"> ${ _('With grant') }</label>
      <div class="inline-block margin-left-10" style="margin-top: 6px">
        <a class="pointer showAdvanced" data-bind="click: function(){ showAdvanced(true); }, visible: !showAdvanced()"><i class="fa fa-cog"></i> ${ _('Show advanced') }</a>
        <a class="pointer showAdvanced" data-bind="click: function(){ showAdvanced(false); }, visible: showAdvanced()"><i class="fa fa-cog"></i> ${ _('Hide advanced') }</a>
      </div>
      <div class="clearfix"></div>
    </div>

    <div class="acl-block-section" data-bind="visible: showAdvanced" style="margin-top: 0">
      ${ _('Server') } <input type="text" data-bind="value: serverName" placeholder="serverName" style="margin-left: 6px">
    </div>
  <!-- /ko -->

  <!-- ko ifnot: editing -->
    <div class="pull-right privilege-actions" data-bind="visible: (grantOption() || $parents[1].isSentryAdmin) && !$parents[1].readOnly">
##       <a title="${ _('Grant this privilege') }" class="pointer" style="margin-right: 4px" data-bind="click: function(){ $parents[1].grantToPrivilege($data); $('#grantPrivilegeModal').modal('show'); }"><i class="fa fa-send"></i></a>
      <a title="${ _('Edit this privilege') }" class="pointer" style="margin-right: 4px" data-bind="visible: $parents[1].isSentryAdmin, click: function() { if (! editing()) { editing(true); }}"><i class="fa fa-pencil"></i></a>
      <a title="${ _('Delete this privilege') }" class="pointer" style="margin-right: 4px" data-bind="visible: $parents[1].isSentryAdmin, click: remove"><i class="fa fa-times"></i></a>
    </div>

    <span class="muted" data-bind="text: privilegeScope, attr: {title: moment(timestamp()).fromNow()}"></span>
    <!-- ko if: grantOption -->
      <i class="fa fa-unlock muted" title="${ _('With grant option') }"></i>
    <!-- /ko -->
    <span data-bind="visible: metastorePath() != '' && privilegeType() == 'db'">
      <a data-bind="hueLink: metastorePath()" class="muted" style="margin-left: 4px" title="${ _('Open in Table Browser') }"><i class="fa fa-external-link"></i></a>
    </span>
    <br/>

    server=<span data-bind="text: serverName"></span>

    <!-- ko if: privilegeType() == 'db' -->
      <span data-bind="visible: dbName">
        <i class="fa fa-long-arrow-right"></i> db=<a class="pointer" data-bind="click: function(){ $parents[1].linkToBrowse(dbName()) }" title="${ _('Browse db privileges') }"><span data-bind="text: dbName"></span></a>
      </span>
      <span data-bind="visible: tableName">
        <i class="fa fa-long-arrow-right"></i> table=<a class="pointer" data-bind="click: function(){ $parents[1].linkToBrowse(dbName() + '.' + tableName()) }" title="${ _('Browse table privileges') }"><span data-bind="text: tableName"></span></a>
      </span>
      <span data-bind="visible: columnName">
        <i class="fa fa-long-arrow-right"></i> column=<a class="pointer" data-bind="click: function(){ $parents[1].linkToBrowse(dbName() + '.' + tableName() + '.' + columnName()) }" title="${ _('Browse column privileges') }"><span data-bind="text: columnName"></span></a>
      </span>
    <!-- /ko -->

    <!-- ko if: privilegeType() == 'uri' -->
      <i class="fa fa-long-arrow-right"></i> <i class="fa fa-file-o"></i> <i class="fa fa-long-arrow-right"></i> <a data-bind="hueLink: '/filebrowser/view=/' + URI().split('/')[3]"><span data-bind="text: URI"></span></a>
    <!-- /ko -->

    <i class="fa fa-long-arrow-right"></i> action=<span data-bind="text: action"></span>

  <!-- /ko -->
</div>
</script>

  <script type="text/javascript">
    (function () {

      var Privilege = function (vm, privilege) {
        var self = this;

        self.id = ko.observable(typeof privilege.id != "undefined" && privilege.id != null ? privilege.id : "");
        self.roleName = ko.observable(typeof privilege.roleName != "undefined" && privilege.roleName != null ? privilege.roleName : "");
        self.status = ko.observable(typeof privilege.status != "undefined" && privilege.status != null ? privilege.status : "");
        self.editing = ko.observable(typeof privilege.editing != "undefined" && privilege.editing != null ? privilege.editing : false);
        self.serverName = ko.observable(typeof privilege.serverName != "undefined" && privilege.serverName != null ? privilege.serverName : "");
        self.serverName.subscribe(function () {
          if (self.status() == '') {
            self.status('modified');
          }
        });
        self.dbName = ko.observable(typeof privilege.dbName != "undefined" && privilege.dbName != null ? privilege.dbName : "");
        self.dbName.subscribe(function () {
          if (self.status() == '') {
            self.status('modified');
          }
        });
        self.tableName = ko.observable(typeof privilege.tableName != "undefined" && privilege.tableName != null ? privilege.tableName : "");
        self.tableName.subscribe(function () {
          if (self.status() == '') {
            self.status('modified');
          }
        });
        self.columnName = ko.observable(typeof privilege.columnName != "undefined" && privilege.columnName != null ? privilege.columnName : "");
        self.columnName.subscribe(function () {
          if (self.status() == '') {
            self.status('modified');
          }
        });
        self.URI = ko.observable(typeof privilege.URI != "undefined" && privilege.URI != null ? privilege.URI : "");
        self.URI.subscribe(function () {
          if (self.status() == '') {
            self.status('modified');
          }
        });
        self.action = ko.observable(typeof privilege.action != "undefined" && privilege.action != null ? privilege.action : 'SELECT');
        self.action.subscribe(function () {
          if (self.status() == '') {
            self.status('modified');
          }
        });
        self.timestamp = ko.observable(typeof privilege.timestamp != "undefined" && privilege.timestamp != null ? privilege.timestamp : 0);
        self.grantOption = ko.observable(typeof privilege.grantOption != "undefined" && privilege.grantOption != null ? privilege.grantOption : false);
        self.grantOption.subscribe(function () {
          if (self.status() == '') {
            self.status('modified');
          }
        });

        // UI
        self.privilegeType = ko.observable(typeof privilege.privilegeScope != "undefined" && privilege.privilegeScope == 'URI' ? "uri" : "db");
        self.showAdvanced = ko.observable(false);
        self.path = ko.computed({
          read: function () {
            if (self.columnName().length > 0) {
              return self.dbName() + "." + self.tableName() + "." + self.columnName();
            } else if (self.tableName().length > 0) {
              return self.dbName() + "." + self.tableName();
            } else {
              return self.dbName();
            }
          },
          write: function (value) {
            var _parts = value.split(".");
            this.dbName(_parts[0]);
            this.tableName(_parts.length > 1 ? _parts[1] : "");
            this.columnName(_parts.length > 2 ? _parts[2] : "");
          },
          owner: self
        });

        self.metastorePath = ko.computed(function () {
          if (self.columnName().length > 0) {
            return '/metastore/table/' + self.dbName() + "/" + self.tableName() + "#col=" + self.columnName();
          } else if (self.tableName().length > 0) {
            return '/metastore/table/' + self.dbName() + "/" + self.tableName();
          } else if (self.dbName().length > 0) {
            return '/metastore/tables/' + self.dbName();
          } else {
            return '';
          }
        });

        function getPrivilegeScope() {
          if (self.privilegeType() == 'uri') {
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

        self.privilegeScope = ko.observable(typeof privilege.privilegeScope != "undefined" ? privilege.privilegeScope : getPrivilegeScope());

        self.privilegeType.subscribe(function (newVal) {
          self.privilegeScope(getPrivilegeScope());
        });

        self.columnName.subscribe(function (newVal) {
          self.privilegeScope(getPrivilegeScope());
        });

        self.tableName.subscribe(function (newVal) {
          self.privilegeScope(getPrivilegeScope());
        });

        self.dbName.subscribe(function (newVal) {
          self.privilegeScope(getPrivilegeScope());
        });

        self.remove = function (privilege) {
          if (privilege.status() == 'new') {
            privilege.status('alreadydeleted');
          } else {
            privilege.status('deleted');
          }
        }
      }

      var Role = function (vm, role) {
        var self = this;

        self.name = ko.observable(typeof role.name != "undefined" && role.name != null ? role.name : "");
        self.name.subscribe(function (value) {
          var _found = false;
          vm.role().isEditing(false);
          ko.utils.arrayForEach(vm.roles(), function (role) {
            if (role.name() == value) {
              vm.role(role);
              _found = true;
            }
          });
          if (_found) {
            vm.role().isEditing(true);
            vm.list_sentry_privileges_by_role(vm.role());
            $(document).trigger("destroyTypeahead");
          }
        });
        self.selected = ko.observable(false);
        self.handleSelect = function (row, e) {
          self.selected(!self.selected());
        }

        self.groups = ko.observableArray();
        self.originalGroups = ko.observableArray();
        self.groups.extend({rateLimit: 300});
        self.originalGroups.extend({rateLimit: 300});
        $.each(typeof role.groups != "undefined" && role.groups != null ? role.groups : [], function (index, group) {
          self.groups.push(group);
          self.originalGroups.push(group);
        });
        self.privileges = ko.observableArray(); // Not included in the API
        self.originalPrivileges = ko.observableArray(); // Not included in the API
        self.privilegesForViewTo = ko.observable(49);
        self.showPrivileges = ko.observable(false);
        self.showPrivileges.subscribe(function (value) {
          var _expanded = vm.expandedRoles();
          if (value) {
            if (_expanded.indexOf(self.name()) == -1) {
              _expanded.push(self.name());
            }
          }
          else {
            if (_expanded.indexOf(self.name()) > -1) {
              _expanded.splice(_expanded.indexOf(self.name()), 1);
            }
          }
          vm.expandedRoles(_expanded);
        });

        self.showEditGroups = ko.observable(false);
        self.isEditing = ko.observable(false);
        self.isLoading = ko.observable(false);
        self.isValid = ko.computed(function () {
          return self.name().length > 0 && $.grep(self.privileges(), function (privilege) {
            return privilege.privilegeType() === 'uri' && privilege.URI() === '';
          }).length === 0;
        });

        self.privilegesChanged = ko.computed(function () {
          return $.grep(self.privileges(), function (privilege) {
            return ['new', 'deleted', 'modified'].indexOf(privilege.status()) != -1;
          });
        });

        self.groupsChanged = ko.computed(function () {
          return !($(self.groups()).not(self.originalGroups()).length == 0 && $(self.originalGroups()).not(self.groups()).length == 0);
        });
        self.groupsChanged.extend({rateLimit: 300});

        self.privilegesForView = ko.computed(function () {
          //var _filter = vm.privilegeFilter().toLowerCase();
          //if (_filter == "") {
          return self.privileges().slice(0, self.privilegesForViewTo());
          //}
          //else {
          ##    var _filtered = ko.utils.arrayFilter(self.privileges(), function (priv) {
       ##      return priv.dbName().toLowerCase().indexOf(_filter) > -1 || priv.tableName().toLowerCase().indexOf(_filter) > -1 || priv.action().toLowerCase().indexOf(_filter) > -1;
       ##    });
       ##    return _filtered.slice(0, self.privilegesForViewTo());
       ##  }
     });

        self.reset = function () {
          self.name('');
          self.groups.removeAll();
          self.privileges.removeAll();
          self.isEditing(false);
        }

        self.addGroup = function () {
          self.groups.push('');
        }

        self.addPrivilege = function () {
          self.privileges.push(new Privilege(vm, {
            'serverName': vm.server(),
            'status': 'new',
            'editing': true,
            'dbName': vm.db(),
            'tableName': vm.table(),
            'columnName': vm.column()
          }));
        }

        self.resetGroups = function () {
          self.groups.removeAll();
          $.each(self.originalGroups(), function (index, group) {
            self.groups.push(group);
          });
        }

        self.saveGroups = function () {
          $(".jHueNotify").remove();
          $.post("/security/api/hive/update_role_groups", {
            role: ko.mapping.toJSON(self)
          }, function (data) {
            if (data.status == 0) {
              self.showEditGroups(false);
              self.originalGroups.removeAll();
              $.each(self.groups(), function (index, group) {
                self.originalGroups.push(group);
              });
            } else {
              $(document).trigger("error", data.message);
            }
          }).fail(function (xhr, textStatus, errorThrown) {
            $(document).trigger("error", xhr.responseText);
          });
        }

        self.create = function () {
          $(".jHueNotify").remove();
          if (self.isValid()) {
            self.isLoading(true);
            $.post("/security/api/hive/create_role", {
              role: ko.mapping.toJSON(self)
            }, function (data) {
              if (data.status == 0) {
                $(document).trigger("info", data.message);
                vm.showCreateRole(false);
                self.reset();
                var role = new Role(vm, data.role);
                role.showPrivileges(true);
                vm.originalRoles.unshift(role);
                vm.listSentryPrivilegesByAuthorizable();
                $(document).trigger("createdRole");
              } else {
                $(document).trigger("error", data.message);
              }
            }).fail(function (xhr, textStatus, errorThrown) {
              $(document).trigger("error", xhr.responseText);
            }).always(function () {
              self.isLoading(false);
            });
          }
        }

        self.update = function () {
          $(".jHueNotify").remove();
          if (self.isValid()) {
            self.isLoading(true);
            $.post("/security/api/hive/save_privileges", {
              role: ko.mapping.toJSON(self)
            }, function (data) {
              if (data.status == 0) {
                $(document).trigger("info", data.message);
                vm.showCreateRole(false);
                vm.listSentryPrivilegesByAuthorizable();
                $(document).trigger("createdRole");
              } else {
                $(document).trigger("error", data.message);
              }
            }).fail(function (xhr, textStatus, errorThrown) {
              $(document).trigger("error", xhr.responseText);
            }).always(function () {
              self.isLoading(false);
            });
          }
        }

        self.remove = function (role) {
          $(".jHueNotify").remove();
          self.isLoading(true);
          $.post("/security/api/hive/drop_sentry_role", {
            roleName: role.name
          }, function (data) {
            if (data.status == 0) {
              vm.removeRole(role.name());
              vm.listSentryPrivilegesByAuthorizable();
              $(document).trigger("removedRole");
            } else {
              $(document).trigger("error", data.message);
            }
          }).fail(function (xhr, textStatus, errorThrown) {
            $(document).trigger("error", xhr.responseText);
          }).always(function () {
            self.isLoading(false);
          });
        }

        self.savePrivileges = function (role) {
          $(".jHueNotify").remove();
          $.post("/security/api/hive/save_privileges", {
            role: ko.mapping.toJSON(role)
          }, function (data) {
            if (data.status == 0) {
              vm.listSentryPrivilegesByAuthorizable();
              $(document).trigger("createdRole");
            } else {
              $(document).trigger("error", data.message);
            }
          }).fail(function (xhr, textStatus, errorThrown) {
            $(document).trigger("error", xhr.responseText);
          });
        }
      }


      function _create_authorizable_from_ko(server, path) {
        if (path != null) {
          var paths = path.split(/[.]/);
          return {
            'server': server,
            'db': paths[0] ? paths[0] : null,
            'table': paths[1] ? paths[1] : null,
            'column': paths[2] ? paths[2] : null
          }
        }
      }

      function _create_ko_privilege(privilege) {
        var _privilege = new Privilege(self, {
          'privilegeScope': privilege.scope,
          'serverName': privilege.server,
          'dbName': privilege.database,
          'tableName': privilege.table,
          'columnName': privilege.column,
          'URI': privilege.URI,
          'action': privilege.action,
          'timestamp': privilege.timestamp,
          'roleName': privilege.roleName,
          'grantOption': privilege.grantOption,
          'id': UUID()
        });
        return _privilege;
      }


      function SentryPrivilegesViewModel(params) {
        var self = this;
        self.server = ko.observable(params.server);
        self.path = ko.observable(params.path);
        self.isSentryAdmin = params.isSentryAdmin;
        self.readOnly = !!params.readOnly;
        self.apiVersion = params.apiVersion || 'v1';
        self.apiType = params.apiType || 'hive';
        self.showFilter = params.showFilter;
        self.enableCreateRole = params.enableCreateRole;

        self.path.subscribe(self.listSentryPrivilegesByAuthorizable);

        self.db = ko.computed(function () {
          var db = self.path().split(/[.]/)[0];
          return db ? db : null;
        });
        self.table = ko.computed(function () {
          var table = self.path().split(/[.]/)[1];
          return table ? table : null;
        });
        self.column = ko.computed(function () {
          var column = self.path().split(/[.]/)[2];
          return column ? column : null;
        });
        self.metastorePath = ko.computed(function () {
          if (self.column()) {
            return '/metastore/table/' + self.db() + "/" + self.table() + "#col=" + self.column();
          } else if (self.table()) {
            return '/metastore/table/' + self.db() + "/" + self.table();
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
          var actions = ['SELECT', 'INSERT', 'ALL'];
          var databaseActions = ['CREATE'];
          var tableActions = ['REFRESH', 'ALTER', 'DROP'];
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
        }

        self.deletePrivilegeModal = function (role) {
          var cascadeDeletes = $.grep(role.privilegesChanged(), function (privilege) {
              return privilege.status() == 'deleted' && (privilege.privilegeScope() == 'SERVER' || privilege.privilegeScope() == 'DATABASE');
            }
          );
          if (cascadeDeletes.length > 0) {
            self.roleToUpdate(role);
            $('#sentryPrivilegesComponentDeletePrivilegeModal').modal('show');
          } else {
            role.savePrivileges(role);
          }
        };

        self.listSentryPrivilegesByAuthorizable = function () {
          self.isLoadingPrivileges(true);
          $.ajax({
            type: "POST",
            url: "/security/api/hive/list_sentry_privileges_by_authorizable",
            data: {
              groupName: '',
              roleSet: ko.mapping.toJSON({all: true, roles: []}),
              authorizableHierarchy: ko.mapping.toJSON(_create_authorizable_from_ko(self.server(), self.path()))
            },
            success: function (data) {
              if (data.status == 0) {
                self.roles([]);
                var _privileges = [];
                $.each(data.privileges, function (index, item) {
                  if (typeof skipList == "undefined" || (skipList != null && typeof skipList == "Boolean" && !skipList)) {
                    var _role = null;
                    self.roles().forEach(function (role) {
                      if (role.name() == item.roleName) {
                        _role = role;
                      }
                    });
                    if (_role == null) {
                      var _idx = self.roles.push(new Role(self, {name: item.roleName}));
                      _role = self.roles()[_idx - 1];
                    }

                    var privilege = _create_ko_privilege(item);
                    var privilegeCopy = _create_ko_privilege(item);
                    privilegeCopy.id(privilege.id());
                    _role.privileges.push(privilege);
                    _role.originalPrivileges.push(privilegeCopy);

                    _privileges.push(privilege);
                  }
                });
                if (typeof skipList == "undefined" || (skipList != null && typeof skipList == "Boolean" && !skipList)) {
                  self.privileges(_privileges);
                }
              } else {
                $(document).trigger("error", data.message);
              }
            }
          }).fail(function (xhr, textStatus, errorThrown) {
            $(document).trigger("error", xhr.responseText);
          }).always(function () {
            self.isLoadingPrivileges(false);
          });
        };

        self.linkToBrowse = function (path) {
          // TODO: implement smart linking
        }

        self.listSentryPrivilegesByAuthorizable();

      }

      ko.components.register('hue-sentry-privileges', {
        viewModel: SentryPrivilegesViewModel,
        template: {element: 'sentry-privileges-component-template'}
      });
    })();
  </script>

</%def>
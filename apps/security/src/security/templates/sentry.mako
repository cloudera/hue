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
from desktop.views import commonheader, commonfooter, _ko
from django.utils.translation import ugettext as _
%>

<%namespace name="actionbar" file="actionbar.mako" />
<%namespace name="layout" file="layout.mako" />
<%namespace name="tree" file="common_tree.mako" />

%if not is_embeddable:
${ commonheader(_('Hadoop Security'), "security", user, request) | n,unicode }
%endif

${ layout.menubar(section=component, is_embeddable=is_embeddable) }

<span id="securityComponents" class="security-components">

<script type="text/html" id="role">
  <div class="acl-block-title">
    <i class="fa fa-cube muted"></i> <a class="pointer" data-bind="click: function(){  $root.showRole($data); }"><span data-bind="text: name"></span></a>
  </div>
  <div data-bind="template: { name: 'privilege', foreach: privilegesForView }"></div>
  <!-- ko ifnot: $root.isApplyingBulk() -->
  <div class="acl-block acl-actions">
    <span class="pointer" data-bind="visible: privilegesForViewTo() < privileges().length, click: function(){ privilegesForViewTo(privilegesForViewTo() + 50) }" title="${ _('Show 50 more...') }"><i class="fa fa-ellipsis-h"></i></span>
    <span class="pointer" data-bind="click: addPrivilege, visible: $root.is_sentry_admin" title="${ _('Add privilege') }"><i class="fa fa-plus"></i></span>
    <span class="pointer" data-bind="click: function() { $root.list_sentry_privileges_by_authorizable() }, visible: privilegesChanged().length > 0" title="${ _('Undo') }"> &nbsp; <i class="fa fa-undo"></i></span>
    <span class="pointer" data-bind="click: function() { $root.deletePrivilegeModal($data) }, visible: privilegesChanged().length > 0" title="${ _('Save') }"> &nbsp; <i class="fa fa-save"></i></span>
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="privilege">
<div data-bind="visible: status() != 'deleted' && status() != 'alreadydeleted'" class="acl-block acl-block-airy">

  <!-- ko if: editing() -->
    <div class="pull-right privilege-actions" data-bind="visible: grantOption() || $root.is_sentry_admin">
      <!-- ko if: $root.component() != 'solr' -->
      <a title="${ _('Grant this privilege') }" class="pointer" style="margin-right: 4px" data-bind="click: function(){ $root.grantToPrivilege($data); $('#grantPrivilegeModal').modal('show'); }"><i class="fa fa-send"></i></a>
      <!-- /ko -->
      <a class="pointer" style="margin-right: 4px" data-bind="click: function() { if (editing()) { editing(false); }}"><i class="fa fa-eye"></i></a>
      <a class="pointer" style="margin-right: 4px" data-bind="click: remove"><i class="fa fa-times"></i></a>
    </div>

    <!-- ko if: $root.component() == 'hive' -->
      <div class="inline-block" style="vertical-align: middle">
        <a class="pointer" style="padding-top: 4px" data-bind="click: function(){ privilegeType('DATABASE'); action($root.availableActions(authorizables())[0]) }">
          <i class="fa fa-fw fa-1halfx muted" data-bind="css: {'fa-circle-o': privilegeType() != 'DATABASE', 'fa-check-circle-o': privilegeType() == 'DATABASE'}"></i>
        </a>
      </div>
      <input type="text" data-bind="hiveChooser: $data.path, enable: privilegeType() == 'DATABASE', apiHelperUser: '${ user }', apiHelperType: 'hive'" placeholder="dbName.tableName <CTRL+SPACE>">

      <div class="inline-block" style="vertical-align: middle">
        <a class="pointer" style="padding-top: 4px" data-bind="click: function(){ privilegeType('URI'); action('ALL'); }">
          <i class="fa fa-fw fa-1halfx muted" data-bind="css: {'fa-circle-o': privilegeType() != 'URI', 'fa-check-circle-o': privilegeType() == 'URI'}"></i>
        </a>
      </div>

      <input type="text" data-bind="filechooser: 'URI TODO', enable: privilegeType() == 'URI'" placeholder="URI">

      <select data-bind="options: $root.availableActions(authorizables()), value: $data.action, enable: (privilegeType() == 'DATABASE')" style="width: 100px; margin-bottom: 0"></select>
    <!-- /ko -->

    <!-- ko if: $root.component() == 'solr' -->
      <input type="text" class="input-xxlarge" data-bind="solrChooser: $data.path" placeholder="collection or config name <CTRL+SPACE>">
      <select data-bind="options: privilegeType() == 'CONFIG' ? $root.availableSolrConfigActions : $root.availableActions(authorizables()), value: $data.action, enable: privilegeType() != 'CONFIG'" style="width: 100px; margin-bottom: 0"></select>
    <!-- /ko -->

    <div class="new-line-if-small">
      <!-- ko if: $root.component() != 'solr' -->
      <label class="checkbox"><input type="checkbox" data-bind="checked: grantOption"> ${ _('With grant') }</label>
      <!-- /ko -->
      <a class="pointer showAdvanced" data-bind="click: function(){ showAdvanced(true); }, visible: ! showAdvanced()"><i class="fa fa-cog"></i> ${ _('Show advanced') }</a>
      <a class="pointer showAdvanced" data-bind="click: function(){ showAdvanced(false); }, visible: showAdvanced()"><i class="fa fa-cog"></i> ${ _('Hide advanced') }</a>
      <div class="clearfix"></div>
    </div>

    <div class="acl-block-section" data-bind="visible: showAdvanced" style="margin-top: 0">
      ${ _('Server') } <input type="text" data-bind="value: serverName" placeholder="serverName" style="margin-left: 6px">
    </div>
  <!-- /ko -->

  <!-- ko ifnot: editing() -->
    <!-- ko ifnot: $root.isApplyingBulk() -->
    <div class="pull-right privilege-actions" data-bind="visible: grantOption() || $root.is_sentry_admin">
      <!-- ko if: $root.component() != 'solr' -->
      <a title="${ _('Grant this privilege') }" class="pointer" style="margin-right: 4px" data-bind="click: function(){ $root.grantToPrivilege($data); $('#grantPrivilegeModal').modal('show'); }"><i class="fa fa-send"></i></a>
      <!-- /ko -->
      <a title="${ _('Edit this privilege') }" class="pointer" style="margin-right: 4px" data-bind="visible: $root.is_sentry_admin, click: function() { if (! editing()) { editing(true); }}"><i class="fa fa-pencil"></i></a>
      <a title="${ _('Delete this privilege') }" class="pointer" style="margin-right: 4px" data-bind="visible: $root.is_sentry_admin, click: remove"><i class="fa fa-times"></i></a>
    </div>
    <!-- /ko -->

    <span class="muted" data-bind="text: privilegeType, attr: {title: moment(timestamp()).fromNow()}"></span>
    <!-- ko if: $root.component() == 'solr' && authorizables().length > 0 && authorizables()[0].type() == 'COLLECTION'  && authorizables()[0].name_() != '*' -->
      <a data-bind="hueLink: indexerPath()" title="${ _('Open in Indexer') }" class="muted">
        <i class="fa fa-external-link"></i>
      </a>
    <!-- /ko -->

    <!-- ko if: grantOption -->
      <i class="fa fa-unlock muted" title="${ _('With grant option') }"></i>
    <!-- /ko -->

    <!-- ko if: $root.component() == 'hive' -->
      <span data-bind="visible: metastorePath() != '' && privilegeType() == 'DATABASE'">
        <a data-bind="hueLink: metastorePath()" class="muted" style="margin-left: 4px" title="${ _('Open in Metastore') }"><i class="fa fa-external-link"></i></a>
      </span>
      <br/>

      server=<span data-bind="text: serverName"></span>

      <!-- ko if: privilegeType() == 'DATABASE' -->
        // TODO
        <span data-bind="visible: dbName">
          <i class="fa fa-long-arrow-right"></i> db=<a class="pointer" data-bind="click: function(){ $root.linkToBrowse(dbName()) }" title="${ _('Browse db privileges') }"><span data-bind="text: dbName"></span></a>
        </span>
        <span data-bind="visible: tableName">
          <i class="fa fa-long-arrow-right"></i> table=<a class="pointer" data-bind="click: function(){ $root.linkToBrowse(dbName() + '.' + tableName()) }" title="${ _('Browse table privileges') }"><span data-bind="text: tableName"></span></a>
        </span>
        <span data-bind="visible: columnName">
          <i class="fa fa-long-arrow-right"></i> column=<a class="pointer" data-bind="click: function(){ $root.linkToBrowse(dbName() + '.' + tableName() + '.' + columnName()) }" title="${ _('Browse column privileges') }"><span data-bind="text: columnName"></span></a>
        </span>
      <!-- /ko -->

      <!-- ko if: privilegeType() == 'URI' -->
        <i class="fa fa-long-arrow-right"></i> <i class="fa fa-file-o"></i> <i class="fa fa-long-arrow-right"></i> <a data-bind="hueLink: '/filebrowser/view=/' + URI().split('/')[3]"><span data-bind="text: URI"></span></a>
      <!-- /ko -->

    <!-- /ko -->
    <!-- ko if: $root.component() == 'solr' -->
      <br/>

      <!-- ko foreach: authorizables -->
        <!-- ko if: name_() != '' -->
          <!-- ko if: $index() > 0 -->
            <i class="fa fa-long-arrow-right"></i>
          <!-- /ko -->
          <!-- ko if: type() == 'COLLECTION' && name_() != '*' -->
            <span data-bind="text: type"></span>=<a class="pointer" data-bind="click: function(){ $root.linkToBrowse('collections.' + name_()) }" title="${ _('Browse privileges') }"><span data-bind="text: name_"></span></a></span>
          <!-- /ko -->
          <!-- ko ifnot: type() == 'COLLECTION' && name_() != '*' -->
            <span data-bind="text: type"></span>=<span data-bind="text: name_"></span></span>
          <!-- /ko -->
        <!-- /ko -->
      <!-- /ko -->
    <!-- /ko -->

    <i class="fa fa-long-arrow-right"></i> action=<span data-bind="text: action"></span>
  <!-- /ko -->
</div>
</script>

<div class="container-fluid">
  <div class="row-fluid">
    <div class="span2">
      <div class="sidebar-nav">
        <ul class="nav nav-list">
          <li class="nav-header">${ _('Privileges') }</li>
          <li class="active"><a href="javascript:void(0)" data-toggleSection="edit"><i class="fa fa-sitemap fa-rotate-270"></i> ${ _('Browse') }</a></li>
          <li><a href="javascript:void(0)" data-toggleSection="roles"><i class="fa fa-cubes"></i> ${ _('Roles') }</a></li>
          <li class="nav-header"><i class="fa fa-group"></i> ${ _('Groups') }
            <div>
            <br/>
             <select id="selectedGroup" data-bind="options: $root.selectableHadoopGroups, select2: { dropdownAutoWidth: true, update: $data.action, type: 'action', allowClear: true, vm: $root }" style="width: 100%"></select>
            </div>
          </li>
        </ul>
      </div>
    </div>

    <div class="span10">

      <div id="edit" class="mainSection card card-small">
        <h1 class="card-heading simple">
          <!-- ko if: component() == 'hive' -->
          ${ _('Database and Table privileges') }
          <!-- /ko -->
          <!-- ko if: component() == 'solr' -->
          ${ _('Collections privileges') }
          <!-- /ko -->
          <div id="help-content" class="hide">
            ${ _('Check the') } <a href="http://gethue.com/apache-sentry-made-easy-with-the-new-hue-security-app/#howto" target="_blank">${ _('documentation!') }</a>
          </div>
          <div data-bind="visible: ! $root.is_sentry_admin" class="pull-right" rel="tooltip" data-original-title="${ _('Click to see some Help') }" data-placement="top">
            <i class="fa fa-question-circle help" style="cursor: pointer"></i>
          </div>
        </h1>

        <div class="card-body">
          <div class="row-fluid" data-bind="visible: $root.doAs() != '${ user.username }' && ! $root.assist.isDiffMode()">
            <div class="span12">
              <div class="alert"><i class="fa fa-warning"></i> ${ _('You are currently impersonating the user') } <strong data-bind="text: $root.doAs"></strong></div>
            </div>
          </div>
          <div class="row-fluid">
            <div class="span6">
              <div class="path-container">
                <div class="input-append span12">
                  <input id="path" class="path" type="text" autocomplete="off" />
                  <!-- ko if: $root.component() == 'solr' -->
                  <a data-bind="hueLink: $root.assist.indexerPath()" title="${ _('Open in Indexer') }" class="btn btn-inverse">
                    <i class="fa fa-external-link"></i>
                  </a>
                  <!-- /ko -->
                  <!-- ko ifnot: $root.component() == 'solr' -->
                  <a data-bind="hueLink: $root.assist.metastorePath()" title="${ _('Open in Metastore Browser') }" class="btn btn-inverse">
                    <i class="fa fa-external-link"></i>
                  </a>
                  <!-- /ko -->
                </div>
                <div class="clearfix"></div>
                <div class="tree-toolbar">
                  <div class="pull-right">
                    % if has_impersonation_perm:
                    <div class="dropdown inline-block" style="margin-right: 6px">
                      <a class="dropdown-toggle" data-toggle="dropdown" href="#">
                        <i class="fa fa-eye-slash" data-bind="visible: $root.assist.isDiffMode"></i>
                        <i class="fa fa-eye" data-bind="visible: ! $root.assist.isDiffMode()"></i>
                        <span data-bind="visible: $root.assist.isDiffMode">${ _('Show non accessible paths for') }</span>
                        <span data-bind="visible: ! $root.assist.isDiffMode()">${ _('Impersonate the user') }</span>
                      </a>
                      <ul class="dropdown-menu">
                        <li data-bind="visible: ! $root.assist.isDiffMode(), click: function() { $root.assist.isDiffMode(true); }">
                          <a tabindex="-1" href="#">${ _('Show non accessible paths for') }</a>
                        </li>
                        <li data-bind="visible: $root.assist.isDiffMode(), click: function() { $root.assist.isDiffMode(false); }">
                          <a tabindex="-1" href="#">${ _('Impersonate the user') }</a>
                        </li>
                      </ul>
                    </div>
                    <select class="user-list" data-bind="options: $root.selectableHadoopUsers, select2: { dropdownAutoWidth: true, placeholder: '${ _ko("Select a user") }', update: $root.doAs, type: 'user', vm: $root}" style="width: 120px"></select>
                    % endif
                  </div>
                  <div>
                    <a class="pointer" data-bind="click: $root.assist.collapseOthers" rel="tooltip" data-placement="right" title="${_('Close other nodes')}">
                      <i class="fa fa-compress"></i>
                    </a>
                    &nbsp;
                    <a class="pointer" data-bind="click: $root.assist.refreshTree" rel="tooltip" data-placement="right" title="${_('Refresh the tree')}">
                      <i class="fa fa-refresh"></i>
                    </a>
                    &nbsp;
                    <a class="pointer" data-bind="visible: $root.assist.checkedItems().length > 0, click: function(){ $root.isApplyingBulk(true); $('#bulkActionsModal').modal('show'); }" rel="tooltip" data-placement="right" title="${ _('Add, replace or remove ACLs for the checked paths') }">
                      <i class="fa fa-copy"></i>
                    </a>
                    &nbsp;
                    <i class="fa fa-spinner fa-spin" data-bind="visible: $root.assist.isLoadingTree()"></i>
                  </div>

                </div>
              </div>

              ${ tree.render(id='expandableTree', data='$root.assist.treeData', afterRender='$root.assist.afterRender', component='security') }

            </div>
            <div class="span6 acl-panel">
              <div class="acl-panel-content">
                <div class="pull-right">
                  <input class="input-medium no-margin" type="text" placeholder="${ _('Search privileges...') }" data-bind="value: privilegeFilter, valueUpdate: 'afterkeydown', visible: $root.assist.privileges().length > 1"> &nbsp;
                  <a data-bind="visible: $root.assist.privileges().length > 0 && $root.is_sentry_admin, click: function(){ $root.showCreateRole(true); $('#createRoleModal').modal('show'); }" class="btn pointer">
                    <i class="fa fa-plus-circle"></i> ${ _('Add role') }
                  </a>
                </div>
                <div data-bind="visible: $root.assist.privileges().length == 0 && $root.isLoadingPrivileges()"><i class="fa fa-spinner fa-spin" data-bind="visible: $root.isLoadingPrivileges()"></i> <em class="muted">${ _('Loading privileges...')}</em></div>
                <h4 style="margin-top: 4px" data-bind="visible: $root.assist.privileges().length > 0 && ! $root.isLoadingPrivileges()">${ _('Privileges') } &nbsp;</h4>
                <div data-bind="visible: $root.assist.privileges().length == 0 && ! $root.isLoadingPrivileges()">
                  <div class="span10 offset1 center" style="cursor: pointer" data-bind="click: function(){ if ($root.is_sentry_admin) { $root.showCreateRole(true); $('#createRoleModal').modal('show'); } }">
                    <i data-bind="visible: $root.is_sentry_admin" class="fa fa-plus-circle waiting"></i>
                    <h1 class="emptyMessage">
                      ${ _('No privileges found for the selected item') }<br/>
                      <a class="pointer" data-bind="visible: $root.is_sentry_admin">${ _('Click here to add some') }</a>
                    </h1>
                  </div>
                </div>
                <div data-bind="template: { name: 'role', foreach: $root.assist.roles }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>


      <div id="roles" class="mainSection hide card card-small">
        <h1 class="card-heading simple">
          ${ _('Roles') }
          <div data-bind="visible: ! $root.is_sentry_admin" class="pull-right" rel="tooltip" data-original-title="${ _('Click to see some Help') }" data-placement="top">
            <i class="fa fa-question-circle help" style="cursor: pointer"></i>
          </div>
        </h1>

        <div class="card-body">
          <h1 class="muted" data-bind="visible: $root.isLoadingRoles()"><i class="fa fa-spinner fa-spin"></i></h1>
          <div class="span10 offset1 center" style="cursor: pointer" data-bind="visible: $root.roles().length == 0 && ! $root.isLoadingRoles(), click: function(){ if ($root.is_sentry_admin) { $root.showCreateRole(true); $('#createRoleModal').modal('show'); } }">
            <i data-bind="visible: $root.is_sentry_admin" class="fa fa-plus-circle waiting"></i>
            <h1 class="emptyMessage">
              ${ _('There are currently no roles defined') }<br/>
              <a class="pointer" data-bind="visible: $root.is_sentry_admin">${ _('Click here to add one') }</a>
              <br/>
            </h1>
          </div>
          <div class="clearfix" data-bind="visible: $root.roles().length == 0 && ! $root.isLoadingRoles()"></div>
          <div data-bind="visible: $root.roles().length > 0 && ! $root.isLoadingRoles()">
            <%actionbar:render>
              <%def name="search()">
                <input id="filterInput" type="text" class="input-xlarge search-query" placeholder="${_('Search roles by name, groups, etc...')}" data-bind="clearable: $root.roleFilter, valueUpdate: 'afterkeydown'">
              </%def>

              <%def name="actions()">
                <button class="btn toolbarBtn" data-bind="click: $root.expandSelectedRoles, enable: $root.selectedRoles().length > 0"><i class="fa fa-expand"></i> ${ _('Expand') }</button>
                <button class="btn toolbarBtn" data-bind="visible: $root.is_sentry_admin, click: function(){ $('#deleteRoleModal').modal('show'); }, enable: $root.selectedRoles().length > 0">
                  <i class="fa fa-times"></i> ${ _('Delete') }
                </button>
              </%def>

              <%def name="creation()">
                <a data-bind="visible: $root.is_sentry_admin, click: function(){ $root.showCreateRole(true); $('#createRoleModal').modal('show'); }" class="btn pointer">
                  <i class="fa fa-plus-circle"></i> ${ _('Add') }
                </a>
              </%def>
            </%actionbar:render>
          </div>

          <table class="card-marginbottom" data-bind="visible: $root.roles().length > 0 && ! $root.isLoadingRoles()">
            <thead>
              <tr>
                <th width="1%"><div data-bind="click: $root.selectAllRoles, css: { 'hue-checkbox': true, 'fa': true, 'fa-check': allRolesSelected }"></div></th>
                <th width="2%"></th>
                <th width="20%" style="text-align:left">${ _('Name') }</th>
                <th width="74%" style="text-align:left">${ _('Groups') }</th>
                <th width="3%"></th>
              </tr>
            </thead>
            <tbody data-bind="foreach: $root.filteredRoles">
              <tr>
                <td class="center" data-bind="click: handleSelect" style="cursor: default">
                  <div data-bind="css: { 'hue-checkbox': true, 'fa': true, 'fa-check': selected }"></div>
                </td>
                <td class="center">
                  <a href="javascript:void(0);" title="${ _('Show privileges') }">
                    <i class="fa fa-2x fa-caret" data-bind="click: function() { if (showPrivileges()) { showPrivileges(false); } else { $root.list_sentry_privileges_by_role($data);} }, css: {'fa-caret-right' : ! showPrivileges(), 'fa-caret-down': showPrivileges() }"></i>
                  </a>
                </td>
                <td data-bind="click: function() { if (showPrivileges()) { showPrivileges(false); } else { $root.list_sentry_privileges_by_role($data);} }" class="pointer">
                  <a data-bind="attr: {'href': name}"></a>
                  <i class="fa fa-cube muted"></i>
                  <span data-bind="text: name"></span>
                </td>
                <td>


                  <!-- ko if: $root.is_sentry_admin -->
                    <!-- ko if: !showEditGroups() && !groupsChanged() -->
                      <a class="pointer" data-bind="click: function() { if ($root.is_sentry_admin) { showEditGroups(true); } }">
                        <!-- ko if: groups().length > 0 -->
                        <span data-bind="foreach: groups">
                          <span data-bind="text: $data"></span>
                        </span>
                        <!-- /ko -->
                        <!-- ko if: groups().length == 0 -->
                        <span>
                          <i class="fa fa-plus"></i> ${ _('Add a group') }
                        </span>
                        <!-- /ko -->
                      </a>
                    <!-- /ko -->
                    <!-- ko if: showEditGroups() || (groupsChanged() && ! $root.isLoadingRoles()) -->
                      <select data-bind="options: $root.selectableHadoopGroups, selectedOptions: groups, select2: { dropdownAutoWidth: true, update: groups, type: 'group', vm: $root }" size="5" multiple="true" style="width: 400px"></select>
                      <span data-bind="visible: groupsChanged() && !$root.isLoadingRoles()">
                        &nbsp;
                        <a class="pointer" data-bind="click: resetGroups"><i class="fa fa-undo"></i></a>
                        &nbsp;
                        <a class="pointer" data-bind="click: saveGroups"><i class="fa fa-save"></i></a>
                      </span>
                      <span data-bind="visible: !groupsChanged() && !$root.isLoadingRoles()">
                      &nbsp;
                      <a class="pointer" data-bind="click: function(){ showEditGroups(false); }"><i class="fa fa-times"></i></a>
                      </span>
                    <!-- /ko -->
                  <!-- /ko -->
                  <!-- ko ifnot: $root.is_sentry_admin -->
                    <span data-bind="foreach: groups">
                      <span data-bind="text: $data"></span>
                    </span>
                  <!-- /ko -->
                </td>
                <td>
                </td>
              </tr>
              <tr>
                <td></td>
                <td colspan="4">
                  <div data-bind="template: { name: 'privilege', foreach: $data.privileges }, visible: $data.showPrivileges">
                  </div>
                </td>
              </tr>
              <tr data-bind="visible: $data.showPrivileges">
                <td></td>
                <td colspan="4">
                  <div class="acl-block acl-actions" data-bind="click: privilegesChanged().length == 0 ? addPrivilege : void(0), visible: $root.is_sentry_admin">
                    <span class="pointer" data-bind="click: addPrivilege, visible: $data.showPrivileges" title="${ _('Add privilege') }"><i class="fa fa-plus"></i></span>
                    <span class="pointer" data-bind="click: $root.list_sentry_privileges_by_role, visible: privilegesChanged().length > 0" title="${ _('Undo') }"> &nbsp; <i class="fa fa-undo"></i></span>
                    <span class="pointer" data-bind="click: function() { $root.deletePrivilegeModal($data) }, visible: privilegesChanged().length > 0 && isValid()" title="${ _('Save') }"> &nbsp; <i class="fa fa-save"></i></span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div> <!-- /span10 -->
  </div>
</div>



<div id="createRoleModal" class="modal hide fade in" role="dialog">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
    <h2 class="modal-title" data-bind="visible: ! $root.role().isEditing()">${ _('Add or select a role') }</h2>
    <h2 class="modal-title" data-bind="visible: $root.role().isEditing()">${ _('Edit role') }</h2>
  </div>
  <div class="modal-body" data-bind="with: $root.role, visible: showCreateRole">

    <div class="row-fluid">
      <div class="span6">
        <h4>${ _('Name') }</h4>
        <input id="createRoleName" type="text" class="input-xlarge" data-bind="value: $data.name, visible: ! $data.isEditing()" placeholder="${ _('New or existing role name') }" style="width: 360px" />
        <strong data-bind="text: $data.name, visible: $data.isEditing()"></strong>
      </div>
      <div class="span6">
        <h4>${ _('Groups') }</h4>
        <select data-bind="options: $root.selectableHadoopGroups, selectedOptions: groups, select2: { dropdownAutoWidth: true, update: groups, type: 'group', placeholder: '${ _ko("Optional") }', vm: $root }" size="5" multiple="true" style="width: 360px"></select>
      </div>
    </div>

    <h4>${ _('Privileges') }</h4>
    <div data-bind="template: { name: 'privilege', foreach: privileges }"></div>
    <div class="acl-block acl-actions pointer" data-bind="click: addPrivilege">
      <span class="pointer" title="${ _('Add privilege') }"><i class="fa fa-plus"></i></span>
    </div>
  </div>
  <div class="modal-footer">
    <button class="btn" data-dismiss="modal" aria-hidden="true">${ _('Cancel') }</button>
    <button data-loading-text="${ _('Saving...') }" class="btn btn-primary disable-enter" data-bind="click: $root.role().create, visible: ! $root.role().isEditing(), enable: $root.role().isValid()">${ _('Save') }</button>
    <button data-loading-text="${ _('Saving...') }" class="btn btn-primary disable-enter" data-bind="click: $root.role().update, visible: $root.role().isEditing(), enable: $root.role().isValid()">${ _('Update') }</button>
  </div>
</div>


<div id="grantPrivilegeModal" class="modal hide fade in" role="dialog">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
    <h2 class="modal-title">${ _('Grant privilege') }</h2>
  </div>
  <div class="modal-body">

    <!-- ko if: $root.grantToPrivilege() -->
      <div data-bind="template: { name: 'privilege', data: $root.grantToPrivilege() }"></div>
    <!-- /ko -->

    <br/>
    <span>${ _('To role') }&nbsp;&nbsp;</span>
    <select data-bind="options: $root.selectableRoles(), value: $root.grantToPrivilegeRole, select2: { dropdownAutoWidth: true, update: $root.grantToPrivilegeRole, placeholder: '${ _ko("Select a role") }', type: 'role', vm: $root }" style="width: 360px"></select>
    <br/>

  </div>
  <div class="modal-footer">
    <button class="btn" data-dismiss="modal" aria-hidden="true">${ _('Cancel') }</button>
    <button data-loading-text="${ _('Saving...') }" class="btn btn-primary disable-enter" data-bind="click: $root.grant_privilege">${ _('Grant') }</button>
  </div>
</div>


<div id="deleteRoleModal" class="modal hide fade in" role="dialog">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
    <h2 class="modal-title">${ _('Do you really want to delete the selected role(s)?') }</h2>
  </div>
  <div class="modal-footer">
    <button class="btn" data-dismiss="modal" aria-hidden="true">${ _('Cancel') }</button>
    <button data-loading-text="${ _('Deleting...') }" class="btn btn-danger" data-bind="click: $root.deleteSelectedRoles">${ _('Yes') }</button>
  </div>
</div>


<div id="deletePrivilegeModal" class="modal hide fade in" role="dialog">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
    <h2 class="modal-title">${ _('Confirm the deletion?') }</h2>
  </div>
  <div class="modal-body">
    ${ _('Sentry will recursively delete the SERVER or DATABASE privileges you marked for deletion.') }
  </div>
  <div class="modal-footer">
    <button class="btn" data-dismiss="modal" aria-hidden="true">${ _('Cancel') }</button>
    <button data-loading-text="${ _('Deleting...') }" class="btn btn-danger" data-bind="click: function() { $root.role().savePrivileges($root.roleToUpdate()); }">${ _('Yes, delete') }</button>
  </div>
</div>


<div id="bulkActionsModal" class="modal hide fade in" role="dialog">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
    <h2 class="modal-title">${ _('Select one operation') }</h2>
  </div>
  <div class="modal-body" style="overflow-x: hidden">

    <div class="row-fluid">
      <div class="span8">
        <div class="row-fluid">
          <div class="span4 center">
            <div class="big-btn" data-bind="css: {'selected': $root.bulkAction() == 'add'}, click: function(){$root.bulkAction('add')}">
              <i class="fa fa-plus"></i><br/><br/>
              <span>${ _('Add current privileges to selection') }</span>
            </div>
          </div>
          <div class="span4 center">
            <div class="big-btn" data-bind="css: {'selected': $root.bulkAction() == 'sync'}, click: function(){$root.bulkAction('sync')}">
              <i class="fa fa-random"></i><br/><br/>
              <span>${ _('Replace selection with current privileges') }</span>
            </div>
          </div>
          <div class="span4 center">
            <div class="big-btn" data-bind="css: {'selected': $root.bulkAction() == 'delete'}, click: function(){$root.bulkAction('delete')}">
              <i class="fa fa-eraser"></i><br/><br/>
              <span>${ _('Delete all privileges of selection') }</span>
            </div>
          </div>
        </div>
      </div>
      <div class="span4">
        <h4>${ _('to apply to the selection') }</h4>
        <ul class="unstyled modal-panel" data-bind="foreach: $root.assist.checkedItems">
          <li data-bind="visible: path.indexOf('.') > -1" class="force-word-break">
            <i class="fa fa-database muted"></i>
            <span data-bind="text: path.split('.')[0]"></span>
            <i class="fa fa-long-arrow-right muted"></i>
            <i class="fa fa-table muted"></i>
            <span data-bind="text: path.split('.')[1]"></span>
            <span data-bind="visible: path.split('.')[2]">
              <i class="fa fa-long-arrow-right muted"></i>
              <i class="fa fa-columns muted"></i>
              <span data-bind="text: path.split('.')[2]"></span>
            </span>
          </li>
          <li data-bind="visible: path.indexOf('.') == -1" class="force-word-break">
            <i class="fa fa-database muted"></i> <span data-bind="text: path.split('.')[0]"></span>
          </li>
        </ul>
      </div>
    </div>
    <br/>
    <div class="row-fluid" data-bind="visible: $root.bulkAction() != '' && $root.bulkAction() != 'delete'">
      <div class="span12">

        <h4>${ _('Privileges to apply') }</h4>

        <div data-bind="visible: $root.assist.privileges().length == 0"><em class="muted">${ _('No privileges found for the selected item.')}</em></div>
        <div data-bind="template: { name: 'role', foreach: $root.assist.roles }" class="modal-panel"></div>
      </div>
    </div>

  </div>
  <div class="modal-footer">
    <button class="btn" data-dismiss="modal" aria-hidden="true">${ _('Cancel') }</button>
    <button class="btn" data-bind="enable: $root.bulkAction(), css: {'btn-primary': $root.bulkAction() != 'delete', 'btn-danger': $root.bulkAction() == 'delete'}, click: $root.bulkPerfomAction">${ _('Confirm') }</button>
  </div>
</div>

<%def name="treeIcons()">
  'fa-hdd-o': isServer(),
  'fa-database-open': isDb() && (nodes().length > 0 || isLoaded()),
  'fa-database': isDb() && nodes().length == 0,
  'fa-table': isTable(),
  'fa-columns': isColumn()
</%def>

<%def name="withPrivilegesPullRight()">
  <div class="pull-right">
    <i class="fa fa-shield" data-bind="visible: withPrivileges()" style="color: #0B7FAD" title="${ _('Has some privileges') }"></i>&nbsp;
    <i class="fa fa-file-o muted" data-bind="click: $root.assist.showAuthorizable ,visible: isTable()"></i>
  </div>
</%def>


${ tree.import_templates(itemClick='$root.assist.setPath', iconClick='$root.assist.togglePath', itemSelected='$root.assist.path() == path()', styleModifier='withPrivileges', iconModifier=treeIcons, anchorProperty='path', itemChecked='isChecked', styleModifierPullRight=withPrivilegesPullRight, component='security') }


<script src="${ static('security/js/sentry.ko.js') }" type="text/javascript" charset="utf-8"></script>


<script type="text/javascript">
  (function () {
    huePubSub.subscribe('show.delete.privilege.modal', function () {
      $('#deletePrivilegeModal').modal('show');
    });

    var viewModel = new SentryViewModel(${ initial | n,unicode });
    ko.cleanNode($('#securityComponents')[0]);
    ko.applyBindings(viewModel, $('#securityComponents')[0]);

    $(document).ready(function () {
      var _initialPath = viewModel.getPathHash();
      viewModel.init(_initialPath);
      $("#path").val(_initialPath);

      $(".help").popover({
        'title': "${ _('Looking for edit permissions?') }",
        'content': $("#help-content").html(),
        'trigger': 'click',
        'placement': 'left',
        'html': true
      });

      function setPathFromAutocomplete(path) {
        if (path.lastIndexOf(".") == path.length - 1) {
          path = path.substring(0, path.length - 1);
        }
        viewModel.assist.path(path);
        viewModel.assist.updatePathProperty(viewModel.assist.growingTree(), path, "isExpanded", true);
        viewModel.assist.fetchAuthorizablesPath();
      }

      $("#path").jHueGenericAutocomplete({
        skipColumns: true,
        apiHelperUser: '${ user }',
        apiHelperType: 'hive',
        serverType: viewModel.component().toUpperCase(),
        home: viewModel.assist.path(),
        onPathChange: function (path) {
          setPathFromAutocomplete(path);
        },
        onEnter: function (el) {
          setPathFromAutocomplete(el.val());
        },
        smartTooltip: "${_('Did you know? You can use the tab key or CTRL + Space to autocomplete file and folder names')}"
      });

      function resizeComponents() {
        $("#path").width($(".tree-toolbar").width() - 64);
        $("#expandableTree").height($(window).height() - 260);
        $(".acl-panel-content").height($(window).height() - 240);
      }

      resizeComponents();

      $(document).on("renderedTree", function () {
        var _path = viewModel.assist.path();
        if (_path[_path.length - 1] == "/") {
          _path = _path.substr(0, _path.length - 1);
        }
        if ($("a.anchor[href^='" + _path + "']").length > 0) {
          $("#expandableTree").animate({
            scrollTop: ($("a.anchor[href^='" + _path + "']:first").position().top + $("#expandableTree").scrollTop() - $("#expandableTree").position().top - 4) + "px"
          });
        }
      });

      $(document).on("createdRole", function () {
        $("#createRoleModal").modal("hide");
        $("#grantPrivilegeModal").modal("hide");
        $("#deletePrivilegeModal").modal("hide");
        viewModel.clearTempRoles();
        window.setTimeout(function () {
          viewModel.refreshExpandedRoles();
        }, 500);
      });

      $(document).on("deletedRole", function () {
        $("#deleteRoleModal").modal("hide");
      });

      $(document).on("changedPath", function () {
        if ($("#path").val() != viewModel.assist.path()) {
          $("#path").val(viewModel.assist.path());
        }
      });

      function showMainSection(mainSection) {
        if ($("#" + mainSection).is(":hidden")) {
          $(".mainSection").hide();
          $("#" + mainSection).show();
          highlightMainMenu(mainSection);
          viewModel.updateSectionHash(mainSection);
        }
        hueAnalytics.log('security/common', mainSection);
      }

      function highlightMainMenu(mainSection) {
        $(".nav.nav-list li").removeClass("active");
        $("a[data-toggleSection='" + mainSection + "']").parent().addClass("active");
      }

      $("[data-toggleSection]").on("click", function () {
        showMainSection($(this).attr("data-toggleSection"));
      });

      showMainSection(viewModel.getSectionHash());

      $(document).on("showMainSection", function () {
        showMainSection(viewModel.getSectionHash());
      });

      $(document).on("showRole", function (e, role) {
        if (typeof role != "undefined" && role.name != null) {
          $("#bulkActionsModal").modal("hide");
          showMainSection("roles");
          $("html, body").animate({
            scrollTop: ($("a[href='" + role.name() + "']").position().top - 90) + "px"
          });
        }
      });

      var _resizeTimeout = -1;
      $(window).resize(function () {
        window.clearTimeout(_resizeTimeout);
        _resizeTimeout = window.setTimeout(resizeComponents, 100);
      });

      window.onhashchange = function () {
        if (window.location.pathname.indexOf('/security/${component}') > -1) {
          viewModel.assist.path(viewModel.getPathHash());
        }
      };

      $("#createRoleModal").modal({
        show: false
      });

      $("#grantPrivilegeModal").modal({
        show: false
      });

      $("#createRoleModal").on("show", function () {
        $(document).trigger("create.typeahead");
      });

      $("#createRoleModal").on("hide", function () {
        $('#jHueGenericAutocomplete').hide();
        viewModel.resetCreateRole();
      });

      $("#grantPrivilegeModal").on("hide", function () {
        viewModel.clearTempRoles();
      });


      $("#deleteRoleModal").modal({
        show: false
      });

      $("#selectedGroup").select2("val", "");
      $("#selectedGroup").change(function () {
        viewModel.list_sentry_privileges_by_authorizable();
        viewModel.list_sentry_roles_by_group();
      });

      $(document).on("addedBulkPrivileges", function () {
        $(document).trigger("info", "${ _('The current privileges have been successfully added to the checked items.') }");
        $("#bulkActionsModal").modal("hide");
      });

      $(document).on("deletedBulkPrivileges", function () {
        $(document).trigger("info", "${ _('All the privileges have been successfully removed from the checked items.') }");
        $("#bulkActionsModal").modal("hide");
      });

      $(document).on("syncdBulkPrivileges", function () {
        $(document).trigger("info", "${ _('All the privileges for the checked items have been replaced with the current selection.') }");
        $("#bulkActionsModal").modal("hide");
      });

      $("#bulkActionsModal").modal({
        show: false
      });

      $("#bulkActionsModal").on("hidden", function () {
        viewModel.isApplyingBulk(false);
      });

      $(document).on("createTypeahead", function () {
        $("#createRoleName").typeahead({
          source: function (query) {
            var _options = [];
            viewModel.selectableRoles().forEach(function (item) {
              if (item.toLowerCase().indexOf(query.toLowerCase()) > -1) {
                _options.push(item);
              }
            });
            return _options;
          },
          minLength: 0,
          'updater': function (item) {
            return item;
          }
        });
      });
      $(document).on('focus', '#createRoleName', function () {
        if ($("#createRoleName").data('typeahead')) {
          $("#createRoleName").data('typeahead').lookup();
        }
      });
      $(document).on("destroyTypeahead", function () {
        $('.typeahead').unbind();
        $("ul.typeahead").hide();
      });

      $(document).trigger("createTypeahead");

      $("#deletePrivilegeModal").modal({
        show: false
      });

      %if component == 'hive':
      var loadedApp = 'security_hive2';
      %else:
      var loadedApp = 'security_solr';
      %endif
      huePubSub.subscribe('app.gained.focus', function (app) {
        if (app === loadedApp) {
          window.location.hash = viewModel.lastHash;
          showMainSection(viewModel.getSectionHash());
        }
      }, loadedApp);
    });
  })();
</script>
</span>

%if not is_embeddable:
${ commonfooter(request, messages) | n,unicode }
%endif

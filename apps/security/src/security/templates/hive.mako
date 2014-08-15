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
from desktop.views import commonheader, commonfooter
from django.utils.translation import ugettext as _
%>

<%namespace name="actionbar" file="actionbar.mako" />
<%namespace name="layout" file="layout.mako" />
<%namespace name="tree" file="common_tree.mako" />

${ commonheader(_('Hadoop Security'), "security", user) | n,unicode }
${ layout.menubar(section='hive') }


<script type="text/html" id="role">
  <div class="acl-block-title"><i class="fa fa-cube"></i> <a href="javascript: void(0)"><span data-bind="text: name"></span></a></div>
  <div data-bind="template: { name: 'privilege', foreach: privileges }"></div>
  <div class="acl-block acl-actions">
    <span class="pointer" data-bind="click: addPrivilege" title="${ _('Add privilege') }"><i class="fa fa-plus"></i></span>
    <span class="pointer" data-bind="click: $root.list_sentry_privileges_by_authorizable, visible: privilegesChanged().length > 0" title="${ _('Undo') }"> &nbsp; <i class="fa fa-undo"></i></span>
    <span class="pointer" data-bind="click: $root.role.savePrivileges, visible: privilegesChanged().length > 0" title="${ _('Save') }"> &nbsp; <i class="fa fa-save"></i></span>
  </div>
</script>


<script type="text/html" id="privilege">
<div data-bind="visible: status() != 'deleted' && status() != 'alreadydeleted'" class="acl-block acl-block-airy">

  <!-- ko if: editing() -->
    <div class="pull-right">
      <a href="javascript: void(0)" style="margin-right: 4px"><i class="fa fa-eye" data-bind="click: function() { if (editing()) { editing(false); }}"></i></a>
      <a href="javascript: void(0)" style="margin-right: 4px"><i class="fa fa-times" data-bind="click: remove"></i></a>
    </div>
    <input name="db" data-bind="attr: { name: 'privilege-' + $index() }" type="radio" checked/>
    <input type="text" data-bind="value: $data.path, valueUpdate: 'afterkeydown'" placeholder="dbName.tableName">

    <input name="uri" data-bind="attr: { name: 'privilege-' + $index() }" type="radio"/>
    <input type="text" data-bind="value: $data.URI" placeholder="URI">

    <select data-bind="options: $root.availableActions, select2: { update: $data.action, type: 'action'}" style="width: 100px"></select>

    &nbsp;&nbsp;<a class="pointer showAdvanced" data-bind="click: function(){ showAdvanced(true); }, visible: ! showAdvanced()"><i class="fa fa-cog"></i> ${ _('Show advanced options') }</a>

    <div class="acl-block-section" data-bind="visible: showAdvanced">
      <input type="text" data-bind="value: serverName" placeholder="serverName">
      <select data-bind="options: $root.availablePrivileges, select2: { update: $data.privilegeScope, type: 'scope'}" style="width: 100px"></select>
    </div>

  <!-- /ko -->
  
  <!-- ko ifnot: editing() -->
    <div class="pull-right">
      <a href="javascript: void(0)" style="margin-right: 4px"><i class="fa fa-pencil" data-bind="click: function() { if (! editing()) { editing(true); }}"></i></a>
      <a href="javascript: void(0)" style="margin-right: 4px"><i class="fa fa-times" data-bind="click: remove"></i></a>
    </div>

    <em class="muted" data-bind="text: moment(timestamp()).fromNow()"></em> <span data-bind="text: privilegeScope"></span><br/>
    <span data-bind="text: serverName"></span> ${_('Database')}: <a data-bind="attr: { href: '/metastore/table/' + dbName() }" target="_blank"><span data-bind="text: dbName"></span></a> <span data-bind="text: tableName"></span>
    <span data-bind="text: URI"></span>
    <br/>
    ${_('Action')}: <span data-bind="text: action"></span>
    <span data-bind="text: grantor"></span>    
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
             <select id="selectedGroup" data-bind="options: $root.selectableHadoopGroups, select2: { update: $data.action, type: 'action', allowClear: true }" style="width: 100%"></select>
            </div>
          </li>
        </ul>
      </div>
    </div>

    <div class="span10">

      <div id="edit" class="mainSection card card-small">
        <h1 class="card-heading simple">
          ${ _('Database and Tables privileges') }
        </h1>

        <div class="card-body">
          <div class="row-fluid">
            <div class="span6">
              <div class="path-container">
                <div class="input-append span12">
                  <input id="path" class="path" type="text" autocomplete="off" />
                  <a data-bind="attr: { href: '/metastore/' + $root.assist.path() }" target="_blank" title="${ _('Open in Metastore Browser') }" class="btn btn-inverse">
                    <i class="fa fa-external-link"></i>
                  </a>
                </div>
                <div class="clearfix"></div>
                <div class="tree-toolbar">
                  <div class="pull-right">
                    <a href="javascript: void(0)" data-bind="click: $root.assist.collapseOthers">
                      <i class="fa fa-compress"></i> ${_('Close others')}
                    </a>
                    <a href="javascript: void(0)" data-bind="click: $root.assist.refreshTree">
                      <i class="fa fa-refresh"></i>  ${_('Refresh')}
                    </a>                  
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
                    <select class="user-list" data-bind="options: $root.selectableHadoopUsers, select2: { placeholder: '${ _("Select a user") }', update: $root.doAs, type: 'user'}" style="width: 120px"></select>
                    <i class="fa fa-group" title="${ _('List of groups in popover for this user?') }"></i>
                  </div>
                  <div>
                    <a href="javascript: void(0)" data-bind="click: $root.bulk_add_privileges" title="${ _('Add current current privileges to checkbox selection') }">
                      <i class="fa fa-plus"></i>
                    </a>
                    <a href="javascript: void(0)" data-bind="click: $root.assist.bulkSyncAcls" title="${ _('Replace checkbox selection with current privileges') }">
                      <i class="fa fa-copy"></i>
                    </a>
                    <a href="javascript: void(0)" data-bind="click: $root.bulk_delete_privileges" title="${ _('Remove privileges of checkbox selection') }">
                      <i class="fa fa-times"></i>
                    </a>
                  </div>
                  <i class="fa fa-spinner fa-spin" data-bind="visible: $root.assist.isLoadingTree()"></i>
                </div>
              </div>

              ${ tree.render(id='expandableTree', data='$root.assist.treeData', afterRender='$root.assist.afterRender') }

            </div>
            <div class="span6 acl-panel">
              <div class="acl-panel-content">
                <h4 style="margin-top: 4px">${ _('Privileges') }</h4>
                <div data-bind="visible: $root.assist.privileges().length == 0"><em class="muted">${ _('No privileges found for the selected item.')}</em></div>
                  <div data-bind="template: { name: 'role', foreach: $root.assist.roles }">
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>


      <div id="roles" class="mainSection hide card card-small">
        <h1 class="card-heading simple">
          ${ _('Roles') }
        </h1>

        <div class="card-body">
          <div class="span10 offset1 center" style="cursor: pointer" data-bind="visible: $root.roles().length == 0, click: function(){ $root.showCreateRole(true); $('#createRoleModal').modal('show'); }">
            <i class="fa fa-plus-circle waiting"></i>
            <h1 class="emptyMessage">${ _('There are currently no roles defined.') }<br/><a href="javascript: void(0)">${ _('Click here to add') }</a> ${ _('one.') }</h1>
          </div>
          <div class="clearfix" data-bind="visible: $root.roles().length == 0"></div>
          <div data-bind="visible: $root.roles().length > 0">
            <%actionbar:render>
              <%def name="search()">
                <input id="filterInput" type="text" class="input-xlarge search-query" placeholder="${_('Search for name, groups, etc...')}" data-bind="value: $root.roleFilter, valueUpdate: 'afterkeydown'">
              </%def>

              <%def name="actions()">
                <button class="btn toolbarBtn" data-bind="click: $root.expandSelectedRoles, enable: $root.selectedRoles().length > 0"><i class="fa fa-expand"></i> ${ _('Expand') }</button>
                <button class="btn toolbarBtn" data-bind="click: function(){ $('#deleteRoleModal').modal('show'); }, enable: $root.selectedRoles().length > 0"><i class="fa fa-times"></i> ${ _('Delete') }</button>
              </%def>

              <%def name="creation()">
                <a href="javascript: void(0)" data-bind="click: function(){ $root.showCreateRole(true); $('#createRoleModal').modal('show'); }" class="btn"><i class="fa fa-plus-circle"></i> ${ _('Add') }</a>
              </%def>
            </%actionbar:render>
          </div>

          <table class="card-marginbottom" data-bind="visible: $root.roles().length > 0">
            <thead>
              <th width="1%"><div data-bind="click: $root.selectAllRoles, css: { hueCheckbox: true, 'fa': true, 'fa-check': allRolesSelected }"></div></th>
              <th width="2%"></th>
              <th width="20%">${ _('Name') }</th>
              <th width="54%">${ _('Groups') }</th>
              <th width="20%">${ _('Grantor Principal') }</th>
              <th width="3%"></th>
            </thead>
            <tbody data-bind="foreach: $root.filteredRoles">
              <tr>
                <td class="center" data-bind="click: handleSelect" style="cursor: default">
                  <div data-bind="css: { hueCheckbox: true, 'fa': true, 'fa-check': selected }"></div>
                </td>
                <td class="center">
                  <a href="javascript:void(0);" title="${ _('Show privileges') }">
                    <i class="fa fa-2x fa-caret" data-bind="click: function() { if (showPrivileges()) { showPrivileges(false); } else { $root.list_sentry_privileges_by_role($data);} }, css: {'fa-caret-right' : ! showPrivileges(), 'fa-caret-down': showPrivileges() }"></i>
                  </a>
                </td>
                <td>
                  <i class="fa fa-cube"></i>
                   <span data-bind="text: name, click: function() { if (showPrivileges()) { showPrivileges(false); } else { $root.list_sentry_privileges_by_role($data);} }" class="pointer"/>
                </td>
                <td>
                  <a href="javascript: void(0)" data-bind="click: function() { showEditGroups(true); }">
                    <span data-bind="foreach: groups, visible: ! showEditGroups() && ! groupsChanged()">
                      <span data-bind="text: $data"></span>
                    </span>
                    <span data-bind="visible: ! showEditGroups() && ! groupsChanged() && groups().length == 0">
                      <i class="fa fa-plus"></i> ${ _('Add a group') }
                    </span>
                  </a>
                  <div data-bind="visible: showEditGroups() || groupsChanged()">
                    <select data-bind="options: $root.selectableHadoopGroups, selectedOptions: groups, select2: { update: groups, type: 'group'}" size="5" multiple="true" style="width: 400px"></select>
                    <a href="javascript: void(0)" data-bind="visible: groupsChanged, click: resetGroups">
                      <i class="fa fa-undo"></i>
                    </a>
                    <a href="javascript: void(0)" data-bind="visible: groupsChanged, click: saveGroups">
                      <i class="fa fa-save"></i>
                    </a>
                  </div>
                </td>
                <td>
                  <a href=""><span data-bind="text: grantorPrincipal"></span></a>
                </td>
                <td>
                </td>
              </tr>
              <tr>
                <td colspan="2"></td>
                <td colspan="4">
                  <div data-bind="template: { name: 'privilege', foreach: $data.privileges }, visible: $data.showPrivileges">
                  </div>
                </td>
              </tr>
              <tr data-bind="visible: $data.showPrivileges">
                <td colspan="2"></td>
                <td colspan="4">
                  <div class="acl-block acl-actions">
                    <span class="pointer" data-bind="click: addPrivilege, visible: $data.showPrivileges" title="${ _('Add privilege') }"><i class="fa fa-plus"></i></span>
                    <span class="pointer" data-bind="click: $root.list_sentry_privileges_by_role, visible: privilegesChanged().length > 0" title="${ _('Undo') }"> &nbsp; <i class="fa fa-undo"></i></span>
                    <span class="pointer" data-bind="click: $root.role.savePrivileges, visible: privilegesChanged().length > 0" title="${ _('Save') }"> &nbsp; <i class="fa fa-save"></i></span>
                  </div>
                </td>
              </tr>              
            </tbody>
          </table>
        </div>
      </div>

    </div> <!-- /span10 -->
</div>



<div id="createRoleModal" class="modal hide fade in" role="dialog">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
    <h3>${ _('Add role') }</h3>
  </div>
  <div class="modal-body" data-bind="with: $root.role, visible: showCreateRole">

    <div class="row-fluid">
      <div class="span6">
        <h4>${ _('Name') }</h4>
        <input type="text" class="input-xlarge" data-bind="value: $data.name" placeholder="${ _('Required') }" style="width: 360px" />
      </div>
      <div class="span6">
        <h4>${ _('Groups') }</h4>
        <select data-bind="options: $root.selectableHadoopGroups, selectedOptions: groups, select2: { update: groups, type: 'group', placeholder: '${ _("Optional") }' }" size="5" multiple="true" style="width: 360px"></select>
      </div>
    </div>

    <h4>${ _('Privileges') }</h4>
    <div data-bind="template: { name: 'privilege', foreach: privileges }"></div>
    <div class="acl-block acl-actions">
      <span class="pointer" data-bind="click: addPrivilege" title="${ _('Add privilege') }"><i class="fa fa-plus"></i></span>
    </div>
  </div>
  <div class="modal-footer">
    <button class="btn" data-dismiss="modal" aria-hidden="true" data-bind="click: $root.role.reset">${ _('Cancel') }</button>
    <button data-loading-text="${ _('Saving...') }" class="btn btn-primary disable-enter" data-bind="click: $root.role.create">${ _('Save') }</button>
  </div>
</div>


<div id="deleteRoleModal" class="modal hide fade in" role="dialog">
  <div class="modal-header">
    <a href="#" class="close" data-dismiss="modal">&times;</a>
    <h3>${ _('Do you really want to delete the selected role(s)?') }</h3>
  </div>
  <div class="modal-footer">
    <button class="btn" data-dismiss="modal" aria-hidden="true">${ _('Cancel') }</button>
    <button data-loading-text="${ _('Deleting...') }" class="btn btn-danger" data-bind="click: $root.deleteSelectedRoles">${ _('Yes') }</button>
  </div>
</div>

<%def name="treeIcons()">
  'fa-database': isDb(),
  'fa-table': isTable(),
  'fa-columns': isColumn()
</%def>

${ tree.import_templates(itemClick='$root.assist.setPath', iconClick='$root.assist.togglePath', itemSelected='$root.assist.path() == path()', iconModifier=treeIcons, anchorProperty='path', itemChecked='isChecked') }

<script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout.mapping-2.3.2.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/routie-0.3.0.min.js" type="text/javascript" charset="utf-8"></script>

<script src="/security/static/js/common.ko.js" type="text/javascript" charset="utf-8"></script>
<script src="/security/static/js/hive.ko.js" type="text/javascript" charset="utf-8"></script>

<script src="/static/ext/js/moment.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/js/jquery.hiveautocomplete.js" type="text/javascript" charset="utf-8"></script>

  <script type="text/javascript" charset="utf-8">
    var viewModel = new HiveViewModel(${ initial | n,unicode });
    ko.applyBindings(viewModel);

    $(document).ready(function () {

      var _initialPath = viewModel.getPathHash();
      viewModel.init(_initialPath);
      $("#path").val(_initialPath);


      function setPathFromAutocomplete(path){
        if (path.lastIndexOf(".") == path.length -1){
          path = path.substring(0, path.length - 1);
        }
        viewModel.assist.path(path);
        viewModel.assist.updatePathProperty(viewModel.assist.growingTree(), path, "isExpanded", true);
        viewModel.assist.fetchHivePath();
      }

      $("#path").jHueHiveAutocomplete({
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

      $(document).on("rendered.tree", function() {
        var _path = viewModel.assist.path();
        if (_path[_path.length-1] == "/"){
          _path = _path.substr(0, _path.length - 1);
        }
        if ($("a.anchor[href^='"+_path+"']").length > 0){
          $("#expandableTree").animate({
            scrollTop: ($("a.anchor[href^='"+_path+"']:first").position().top + $("#expandableTree").scrollTop() - $("#expandableTree").position().top - 4)+"px"
          });
        }
      });

      $(document).on("created.role", function(){
        $("#createRoleModal").modal("hide");
      });

      $(document).on("deleted.role", function(){
        $("#deleteRoleModal").modal("hide");
      });

      $(document).on("changed.path", function(){
        if ($("#path").val() != viewModel.assist.path()){
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

        logGA(mainSection);
      }

      function highlightMainMenu(mainSection) {
        $(".nav.nav-list li").removeClass("active");
        $("a[data-toggleSection='" + mainSection + "']").parent().addClass("active");
      }

      $("[data-toggleSection]").on("click", function(){
        showMainSection($(this).attr("data-toggleSection"));
      });

      showMainSection(viewModel.getSectionHash());

      var _resizeTimeout = -1;
      $(window).resize(function(){
        window.clearTimeout(_resizeTimeout);
        _resizeTimeout = window.setTimeout(resizeComponents, 100);
      });

      window.onpopstate = function() {
        viewModel.assist.path(viewModel.getPathHash());
      };

      $("#createRoleModal").modal({
        show: false
      });

      $("#deleteRoleModal").modal({
        show: false
      });

      $("#selectedGroup").select2("val", "");
      $("#selectedGroup").change(function() {
        viewModel.list_sentry_privileges_by_authorizable();
        viewModel.list_sentry_roles_by_group(); 
      });

    });
</script>

${ commonfooter(messages) | n,unicode }

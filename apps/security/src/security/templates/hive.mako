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

<script type="text/html" id="privilege">
<div data-bind="visible: status() != 'deleted', click: function() { if (! editing()) { editing(true); } }" class="acl-block acl-block-airy">

  <!-- ko if: editing() -->
    <a href="javascript: void(0)" class="pull-right" style="margin-right: 4px">
      <i class="fa fa-times" data-bind="click: remove"></i>
    </a>
    ## todo, role name
    <input name="db" data-bind="attr: { name: 'privilege-' + $index() }" type="radio" checked/> 
    <input type="text" data-bind="value: $data.path, valueUpdate: 'afterkeydown'" placeholder="dbName.tableName">

    <input name="uri" data-bind="attr: { name: 'privilege-' + $index() }" type="radio"/>
    <input type="text" data-bind="value: $data.URI" placeholder="URI">

    ## <input type="text" class="input-small" data-bind="value: $data.action" placeholder="action">
    <select data-bind="options: $root.availableActions, select2: { update: $data.action, type: 'action'}" style="width: 100px"></select>

    &nbsp;&nbsp;<a class="pointer" data-bind="click: function(){ showAdvanced(true);}, visible: ! showAdvanced()"><i class="fa fa-cog"></i> ${ _('Show advanced options') }</a>

    <div class="acl-block-section" data-bind="visible: showAdvanced">
      <input type="text" data-bind="value: $data.server" placeholder="serverName">
      <select data-bind="options: $root.availablePrivileges, select2: { update: $data.privilegeScope, type: 'scope'}" style="width: 100px"></select>
    </div>

  <!-- /ko -->
  
  <!-- ko ifnot: editing() -->
    <a href="javascript: void(0)" class="pull-right" style="margin-right: 4px">
      <i class="fa fa-times" data-bind="click: remove"></i>
    </a>

    <strong data-bind="text: properties.name"></strong><br/>
    <em class="muted" data-bind="text: moment(properties.timestamp()).fromNow()"></em><br/>
    ${_('Database')}: <a data-bind="attr: { href: '/metastore/' + properties.database() }" target="_blank"><span data-bind="text: properties.database"></span></a><br/>
    <span data-bind="text: properties.action"></span>
    <span data-bind="text: properties.scope"></span>
    <span data-bind="text: properties.table"></span>
    <span data-bind="text: properties.URI"></span>
    <span data-bind="text: properties.grantor"></span>
    <span data-bind="text: properties.server"></span>
  <!-- /ko -->

</div>
</script>

<div class="container-fluid">
  <div class="row-fluid">
    <div class="span2">
      <div class="sidebar-nav">
        <ul class="nav nav-list">
          <li class="nav-header">${ _('Privileges') }</li>
          <li class="active"><a href="javascript:void(0)" data-toggleSection="edit"><i class="fa fa-sitemap  fa-rotate-270"></i> ${ _('Browse') }</a></li>
          <li><a href="javascript:void(0)" data-toggleSection="roles"><i class="fa fa-cubes"></i> ${ _('Roles') }</a></li>
          <li class="nav-header"><i class="fa fa-group"></i> ${ _('Groups') }
            </br>
            <input type="checkbox" checked> All
            </br>
            <select data-bind="options: $root.selectableHadoopGroups, select2: { update: $data.action, type: 'action'}" size="10" multiple="true" style="width: 100%"></select>
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
                    <i class="fa fa-group" title="List of groups in popover for this user?"></i>
                  </div>
                  <a href="javascript: void(0)" data-bind="click: $root.assist.collapseOthers">
                    <i class="fa fa-compress"></i> ${_('Close others')}
                  </a>
                  <a href="javascript: void(0)" data-bind="click: $root.assist.refreshTree">
                    <i class="fa fa-refresh"></i>  ${_('Refresh')}
                  </a>
                  <i class="fa fa-spinner fa-spin" data-bind="visible: $root.assist.isLoadingTree()"></i>
                </div>
              </div>

              ${ tree.render(id='expandableTree', data='$root.assist.treeData', afterRender='$root.assist.afterRender') }

            </div>
            <div class="span6 acl-panel">
              <div class="acl-panel-content">
                <h4>${ _('Privileges') }</h4>
                <div data-bind="visible: $root.assist.privileges().length == 0"><em class="muted">${ _('No privileges found for the selected item.')}</em></div>
                <div data-bind="template: { name: 'privilege', foreach: $root.assist.privileges }">
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
                <input id="filterInput" type="text" class="input-xlarge search-query" placeholder="${_('Search for name, groups, etc...')}">
              </%def>

              <%def name="actions()">
                <button class="btn toolbarBtn" data-bind="click: $root.expandSelectedRoles"><i class="fa fa-expand"></i> ${ _('Expand') }</button>
                <button class="btn toolbarBtn" data-bind="click: $root.deleteSelectedRoles"><i class="fa fa-times"></i> ${ _('Delete') }</button>
              </%def>

              <%def name="creation()">
                <a href="javascript: void(0)" data-bind="click: function(){ $root.showCreateRole(true); $('#createRoleModal').modal('show'); }" class="btn"><i class="fa fa-plus-circle"></i> ${ _('Add') }</a>
              </%def>
            </%actionbar:render>
          </div>

          <table class="card-marginbottom" data-bind="visible: $root.roles().length > 0">
            <thead>
              <th width="1%"><div data-bind="click: $root.selectAllRoles, css: {hueCheckbox: true, 'fa': true, 'fa-check': allRolesSelected}"></div></th>
              <th width="2%"></th>
              <th width="20%">${ _('Name') }</th>
              <th width="54%">${ _('Groups') }</th>
              <th width="20%">${ _('Grantor Principal') }</th>
              <th width="3%"></th>
            </thead>
            <tbody data-bind="foreach: $root.roles">
              <tr>
                <td class="center" data-bind="click: handleSelect" style="cursor: default">
                  <div data-bind="css: {hueCheckbox: true, 'fa': true, 'fa-check': selected}"></div>
                </td>
                <td class="center">
                  <a href="javascript:void(0);">
                    <i class="fa fa-2x fa-caret" data-bind="click: function() { if (showPrivileges()) { showPrivileges(false); } else { $root.list_sentry_privileges_by_role($data);} }, css: {'fa-caret-right' : ! showPrivileges(), 'fa-caret-down': showPrivileges() }"></i>
                  </a>
                </td>
                <td data-bind="text: name, click: function() { if (showPrivileges()) { showPrivileges(false); } else { $root.list_sentry_privileges_by_role($data);} }" class="pointer"></td>
                <td>
                  <span data-bind="foreach: groups">
                    <a href="/useradmin/groups"><span data-bind="text: $data"></span></a>
                  </span>
                </td>
                <td>
                  <a href=""><span data-bind="text: grantorPrincipal"></span></a>
                </td>
                <td>
                  <button type="button" rel="tooltip" data-placement="bottom" data-loading-text="${ _('Saving...') }" data-original-title="${ _('Save') }" class="btn btn-primary"
                    data-bind="click: $root.role.savePrivileges, visible: privilegesChanged().length">
                    <i class="fa fa-save"></i>
                  </button>
                </td>
              </tr>
              <tr>
                  <td colspan="2"></td>
                  <td colspan="4">
                    <div data-bind="template: { name: 'privilege', foreach: $data.privileges }, visible: $data.showPrivileges">
                    </div>
                  </td>
              </tr>
              <tr>
                <td colspan="2"></td>
                <td colspan="4">
                  <div class="acl-block pointer add-acl" data-bind="click: addPrivilege, visible: $data.showPrivileges">
                    <i class="fa fa-plus"></i>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div> <!-- /span10 -->
</div>



<div id="createRoleModal" class="modal hide fade" role="dialog">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
    <h3>${ _('Add role') }</h3>
  </div>
  <div class="modal-body" data-bind="with: $root.role, visible: showCreateRole">
    <p>
      Name <input type="text" class="input-small" data-bind="value: $data.name" />
      <br/>
      Privileges
      <div data-bind="template: { name: 'privilege', foreach: privileges }"></div>
      <a href="javascript: void(0)" data-bind="click: addPrivilege">
        <i class="fa fa-plus"></i>
      </a>
      <br/>
      Groups
      <select data-bind="options: $root.selectableHadoopGroups, selectedOptions: groups, select2: { update: groups, type: 'group'}" size="5" multiple="true" style="width: 120px"></select>

    </p>
  </div>
  <div class="modal-footer">
    <button class="btn" data-dismiss="modal" aria-hidden="true">Close</button>
    <button rel="tooltip" data-placement="bottom" data-loading-text="${ _('Saving...') }" data-original-title="${ _('Add role') }" class="btn btn-primary" data-bind="click: $root.role.create">${ _('Add role') }</button>
  </div>
</div>


<%def name="treeIcons()">
  'fa-database': isDb(),
  'fa-table': isTable(),
  'fa-columns': isColumn()
</%def>

${ tree.import_templates(itemClick='$root.assist.setPath', iconClick='$root.assist.togglePath', itemSelected='$root.assist.path() == path()', iconModifier=treeIcons, anchorProperty='path') }

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

      var _initialPath = "";
      if (window.location.hash != "") {
        _initialPath = window.location.hash.substr(1);
      }
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

      var _resizeTimeout = -1;
      $(window).resize(function(){
        window.clearTimeout(_resizeTimeout);
        _resizeTimeout = window.setTimeout(resizeComponents, 100);
      });

      window.onpopstate = function() {
        viewModel.assist.path(window.location.hash.substr(1));
      };

      $("#createRoleModal").modal({
        show: false
      });

    });
</script>

${ commonfooter(messages) | n,unicode }

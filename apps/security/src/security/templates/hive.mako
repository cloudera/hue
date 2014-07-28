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
<tr data-bind="visible: status() != 'deleted', click: function() { if (! editing()) { editing(true); } }">

  <!-- ko if: editing() -->
    <td><select data-bind="options: availablePrivileges, value: privilegeScope"></select></td>
    <td><input type="text" data-bind="value: $data.serverName" placeholder="serverName"></td>
    <td colspan="2"><input type="text" data-bind="value: $data.dbName" placeholder="dbName"></td>
    <td colspan="2"><input type="text" data-bind="value: $data.tableName" placeholder="tableName"></td>
    <td colspan="2"><input type="text" data-bind="value: $data.URI" placeholder="URI"></td>
    <td><input type="text" data-bind="value: $data.action" placeholder="action"></td>
    <td><a href="javascript:void(0)"><i class="fa fa-minus" data-bind="click: remove"></i></a></td>
  </div>
  <!-- /ko -->
  
  <!-- ko ifnot: editing() -->
    <td><span data-bind="text: properties.name"></span></td>
    <td><span data-bind="text: properties.timestamp"></span></td>
    <td><a data-bind="attr: { href: '/metastore/' + properties.database() }" target="_blank"><span data-bind="text: properties.database"></span></a></td>
    <td><span data-bind="text: properties.action"></span></td>
    <td><span data-bind="text: properties.scope"></span></td>
    <td><span data-bind="text: properties.table"></span></td>
    <td><span data-bind="text: properties.URI"></span></td>
    <td><span data-bind="text: properties.grantor"></span></td>
    <td><span data-bind="text: properties.server"></span></td>
    <td>
      <a href="javascript:void(0)"><i class="fa fa-minus" data-bind="click: remove"></i></a>
    </td>
  <!-- /ko -->  

</tr>
</script>

<div class="container-fluid">
  <div class="row-fluid">
    <div class="span2">
      <div class="sidebar-nav">
        <ul class="nav nav-list">
          <li class="nav-header">${ _('Privileges') }</li>
          <li class="active"><a href="#edit"><i class="fa fa-sitemap  fa-rotate-270"></i> ${ _('Browse') }</a></li>
          <li><a href="#roles"><i class="fa fa-cubes"></i> ${ _('Roles') }</a></li>
          <li class="nav-header"><i class="fa fa-group"></i> ${ _('Groups') }
            </br>
            <input type="checkbox" checked> All
            </br>
            <select data-bind="options: $root.selectableHadoopGroups" size="10" multiple="true"></select>
          </li>          
          <li class="nav-header"><i class="fa fa-group"></i> ${ _('Server') }
            <input type="text" data-bind="value: $root.assist.server" class="input-small" />
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
            <div class="span8">
              <div class="path-container">
                <div class="input-append span12">
                  <input id="path" class="path" type="text" data-bind="value: $root.assist.path, valueUpdate: 'afterkeydown'" autocomplete="off" />
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

              ${ tree.render(id='hdfsTree', data='$root.assist.treeData', afterRender='$root.assist.afterRender') }

            </div>
            <div class="span4">
               <table data-bind="template: { name: 'privilege', foreach: $root.assist.privileges }">
               </table>
            </div>
          </div>
        </div>
      </div>


      <div id="roles" class="mainSection hide card card-small">
        <h1 class="card-heading simple">
          ${ _('Roles') }
        </h1>

        <div class="card-body">
          <%actionbar:render>
		    <%def name="search()">
		      <input id="filterInput" type="text" class="input-xlarge search-query" placeholder="${_('Search for name, groups, etc...')}">
		    </%def>

		    <%def name="actions()">
              <div class="btn-toolbar" style="display: inline; vertical-align: middle">
                <button class="btn toolbarBtn"><i class="fa fa-expand"></i> ${ _('Expand') }</button>
              </div>
		      <div class="btn-toolbar" style="display: inline; vertical-align: middle">
		        <button class="btn toolbarBtn"><i class="fa fa-times"></i> ${ _('Delete') }</button>
		      </div>
		    </%def>

		    <%def name="creation()">
		      <a href="javascript: void(0)" data-bind="click: function(){ $root.showCreateRole(true); }" class="btn"><i class="fa fa-plus-circle"></i> ${ _('Add') }</a>
		    </%def>
		  </%actionbar:render>

          <div data-bind="with: $root.role, visible: showCreateRole">
            <div class="span1">
              Name
              <input type="text" class="input-small" data-bind="value: $data.name"></input>
            </div>
            <div class="span7">
              Privileges
              <div data-bind="template: { name: 'privilege', foreach: privileges }">
              </div>
              <a href="javascript: void(0)" data-bind="click: addPrivilege">
                <i class="fa fa-plus"></i>
              </a>
            </div>
            <div class="span4">
              Groups
              <select data-bind="options: $root.selectableHadoopGroups, selectedOptions: groups" size="5" multiple="true"></select>
            </div>
            <button type="button" rel="tooltip" data-placement="bottom" data-loading-text="${ _('Saving...') }" data-original-title="${ _('Save') }" class="btn"
                data-bind="click: $root.role.create">
              <i class="fa fa-save"></i>
            </button>
          </div>

        <table>
          <theader>
            <th style="width:1%"><div class="hueCheckbox selectAll fa"></div></th>
            <th style="width:3%"></th>
            <th style="width:20%">${ _('Name') }</th>
            <th style="width:67%">${ _('Groups') }</th>
            <th style="width:10%">${ _('Grantor Principal') }</th>
          </theader>
          <tbody data-bind="foreach: $root.roles">
            <tr>
              <td>
                <input type="checkbox" data-bind="click: $root.role.remove"></input>
              </td>
              <td>
                <a href="javascript:void(0);">
                  <i class="fa fa-2x" data-bind="click: function() { if (showPrivileges()) { showPrivileges(false); } else { $root.list_sentry_privileges_by_role($data);} }, css: {'fa-caret-right' : ! showPrivileges(), 'fa-caret-down': showPrivileges() }""></i>
                </a>
              </td>
              <td data-bind="text: name"></td>
              <td>
                <span data-bind="foreach: groups">
                  <a href="/useradmin/groups"><span data-bind="text: $data"></span></a>
                </span>
              </td>
              <td>
                <a href=""><span data-bind="text: grantorPrincipal"></span></a>
              </td>
            </tr>
            <tr>
                <td colspan="2"></td>
                <td colspan="3">
                  <table data-bind="template: { name: 'privilege', foreach: $data.privileges }, visible: $data.showPrivileges">
                  </table>
                </td>
            </tr>
            <tr>
              <td colspan="2"></td>
              <td colspan="3">
                <a href="javascript: void(0)" data-bind="click: addPrivilege, visible: $data.showPrivileges">
                  <i class="fa fa-plus"></i>
                </a>
              </td>
            </tr>
            <tr data-bind="visible: privilegesChanged().length">
              <td colspan="5">
                <button type="button" rel="tooltip" data-placement="bottom" data-loading-text="${ _('Saving...') }" data-original-title="${ _('Save') }" class="btn"
                  data-bind="click: $root.role.savePrivileges">
                  <i class="fa fa-save"></i>
                </button>
              </td>
            </tr>
        </tbody>
        </table>
        </div>
      </div>

    </div> <!-- /span10 -->
</div>

<%def name="treeIcons()">
  'fa-database': isDb(),
  'fa-table': isTable(),
  'fa-columns': isColumn()
</%def>

${ tree.import_templates(itemClick='$root.assist.setPath', iconClick='$root.assist.togglePath', itemSelected='$root.assist.path() == path()',iconModifier=treeIcons) }

<script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout.mapping-2.3.2.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/routie-0.3.0.min.js" type="text/javascript" charset="utf-8"></script>

<script src="/security/static/js/common.ko.js" type="text/javascript" charset="utf-8"></script>
<script src="/security/static/js/hive.ko.js" type="text/javascript" charset="utf-8"></script>


<script type="text/javascript" charset="utf-8">
  var viewModel = new HiveViewModel(${ initial | n,unicode });
  ko.applyBindings(viewModel);

  $(document).ready(function () {
    viewModel.init();

    function resizeComponents () {
      $("#path").width($(".tree-toolbar").width() - 64);
      $("#hdfsTree").height($(window).height() - 260);
      $(".acl-panel-content").height($(window).height() - 260);
    }

    resizeComponents();

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
    $("a[href='#" + mainSection + "']").parent().addClass("active");
  }

  routie({
    "edit": function () {
      showMainSection("edit");
    },
    "roles": function () {
      showMainSection("roles");
    },
    "privileges": function () {
      showMainSection("privileges");
    },
    "view": function () {
      showMainSection("view");
    }
  });
  });


</script>

${ commonfooter(messages) | n,unicode }

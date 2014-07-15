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

${ commonheader(_('Hadoop Security'), "security", user) | n,unicode }
${ layout.menubar(section='hive') }


<script type="text/html" id="privilege-template">
  <select data-bind="options: availablePrivileges, value: privilegeScope"></select>
  <input type="text" data-bind="value: $data.serverName" placeholder="serverName"></input>
  <input type="text" data-bind="value: $data.dbName" placeholder="dbName"></input>
  <input type="text" data-bind="value: $data.tableName" placeholder="tableName"></input>
  <input type="text" data-bind="value: $data.URI" placeholder="URI"></input>
  <i class="fa fa-minus"></i>
</script>


<div class="container-fluid">
  <div class="row-fluid">
    <div class="span2">
      <div class="sidebar-nav">
        <ul class="nav nav-list">
          <li class="nav-header">${ _('Properties') }</li>
          <li class="active"><a href="#edit"><i class="fa fa-eye"></i> ${ _('View') }</a></li>
          <li><a href="#roles"><i class="fa fa-cubes"></i> ${ _('Roles') }</a></li>
          <li class="nav-header"><i class="fa fa-group"></i> ${ _('Groups') }
            </br>
            <input type="checkbox" checked></input> All
            </br>
            <select data-bind="options: $root.availableHadoopGroups" size="10" multiple="true"></select>
          </li>
        </ul>
      </div>
    </div>

    <div class="span10">

      <div id="edit" class="mainSection card card-small">
        <h1 class="card-heading simple">${ _('Edit') }</h1>
        <div class="card-body">
          <input type="text" class="input-xxlarge" data-bind="value: $root.assist.path, valueUpdate:'afterkeydown'"/>
          <a class="btn btn-inverse" style="margin-left:10px", data-bind="attr: { href: '/metastore/' + $root.assist.path() }" target="_blank" title="${ _('Open in Metastore Browser') }">
            <i class="fa fa-external-link"></i>
          </a>
        </div>
        <div>
          <i class="fa fa-eye"></i>
          <i class="fa fa-eye-slash"></i>
        </div>
        <div>
          <div class="span8">
            <div data-bind="foreach: $root.assist.files">
              <div data-bind="text: $data, click: $root.list_sentry_privileges_for_provider"></div>
            </div>
          </div>
        </div>
      </div>

      <div id="roles" class="mainSection hide card card-small">
        <div class="card-heading simple">
        <h3>${ _('Roles') }</h3>
		  <%actionbar:render>
		    <%def name="search()">
		      <input id="filterInput" type="text" class="input-xlarge search-query" placeholder="${_('Search for name, groups, etc...')}">
		    </%def>
		
		    <%def name="actions()">
		      <div class="btn-toolbar" style="display: inline; vertical-align: middle">
		        <button class="btn toolbarBtn" id="submit-btn" disabled="disabled"><i class="fa fa-times"></i> ${ _('Delete') }</button>
		      </div>
		    </%def>
		
		    <%def name="creation()">
		      <a href="javascript: void(0)" data-bind="click: function(){ $root.showCreateRole(true); }" class="btn"><i class="fa fa-plus-circle"></i> ${ _('Add') }</a>
		    </%def>
		  </%actionbar:render>
        </div>


        <div class="card-body">
          <div data-bind="with: $root.role, visible: showCreateRole">
            <div class="span3">
              Name
              <input type="text" data-bind="value: $data.name"></input>
            </div>
            <div class="span5">
              Privileges
              <div data-bind="template: { name: 'privilege-template', foreach: privileges}">
              </div>
              <a href="javascript: void(0)" data-bind="click: addPrivilege">
                <i class="fa fa-plus"></i>
              </a>
            </div>
            <div class="span4">
              Groups
              <select data-bind="options: $root.availableHadoopGroups, selectedOptions: groups" size="5" multiple="true"></select>
            </div>
            <button type="button" rel="tooltip" data-placement="bottom" data-loading-text="${ _('Saving...') }" data-original-title="${ _('Save') }" class="btn"
                data-bind="click: $root.role.create">
              <i class="fa fa-save"></i>
            </button>
          </div>
          <div>
          </div>
        </div>

        </br></br>

        <div>
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
                <a href="javascript:void(0);"><i class="fa fa-2x" data-bind="click: $root.list_sentry_privileges_by_role, css: {'fa-caret-right' : ! showPrivileges(), 'fa-caret-down': showPrivileges() }""></i></a>
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
            <tr data-bind="foreach: $data.privileges, visible: $data.showPrivileges">
              <td colspan="2"></td>
              <td colspan="3">
                <span data-bind="text: name"></span>
                <span data-bind="text: timestamp"></span>
                <a data-bind="attr: { href: '/metastore/' + database() }" target="_blank"><span data-bind="text: database"></span></a>
                <span data-bind="text: action"></span>
                <span data-bind="text: scope"></span>
                <span data-bind="text: table"></span>
                <span data-bind="text: URI"></span>
                <span data-bind="text: grantor"></span>
                <span data-bind="text: server"></span>
                <span data-bind="text: ko.mapping.toJSON($data)"></span> <a href="javascript:void(0);"><i class="fa fa-minus"></i></a>
              </td>
            </tr>
            <tr data-bind="visible: $data.showPrivileges">
              <td colspan="2"></td>
              <td>
                <div data-bind="template: { name: 'privilege-template', foreach: newPrivileges }">
                </div>
                <div data-bind="visible: newPrivileges().length > 0">
		          <button type="button" rel="tooltip" data-placement="bottom" data-loading-text="${ _('Saving...') }" data-original-title="${ _('Save') }" class="btn"
		              data-bind="click: $root.role.saveNewPrivileges">
		            <i class="fa fa-save"></i>
		          </button>
                </div>
                <a href="javascript:void(0)" data-bind="click: $root.role.addNewPrivilege">
                  <i class="fa fa-plus"></i>
                </a>
              </td>
            </tr>
          </div>
        </tbody>
        </div>

      </div>

    </div>
  </div>

  </div>

</div>


<script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout.mapping-2.3.2.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/routie-0.3.0.min.js" type="text/javascript" charset="utf-8"></script>

<script src="/security/static/js/hive.ko.js" type="text/javascript" charset="utf-8"></script>


<script type="text/javascript" charset="utf-8">
  var viewModel;

  $(document).ready(function () {
    viewModel = new HiveViewModel(${ initial | n,unicode });
    ko.applyBindings(viewModel);

    viewModel.init();
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
</script>

${ commonfooter(messages) | n,unicode }

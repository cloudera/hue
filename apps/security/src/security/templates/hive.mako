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


<%namespace name="layout" file="layout.mako" />

${ commonheader(_('Hadoop Security'), "security", user) | n,unicode }
${ layout.menubar(section='hive') }


<div class="container-fluid">
  <div class="row-fluid">
    <div class="span2">
      <div class="sidebar-nav">
        <ul class="nav nav-list">
          <li class="nav-header">${ _('Properties') }</li>
          <li class="active"><a href="#edit"><i class="fa fa-pencil"></i> ${ _('Edit') }</a></li>
          <li><a href="#view"><i class="fa fa-eye"></i> ${ _('View') }</a></li>
          <li><a href="#roles"><i class="fa fa-group"></i> ${ _('Roles') }</a></li>
          <li><a href="#privileges"><i class="fa fa-cubes"></i> ${ _('Privileges') }</a></li>
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
          <div class="span8">
            <div data-bind="foreach: $root.assist.files">
              <div data-bind="text: $data"></div>
            </div>
          </div>
        </div>        
                      
        <div class="card-body">               
          <div data-bind="with: $root.role">
            Privileges
            <div>
              <div data-bind="foreach: priviledges">
                <select data-bind="options: availablePriviledges, value: privilegeScope"></select>
                <input type="text" data-bind="value: $data.serverName" placeholder="serverName"></input>
                <input type="text" data-bind="value: $data.dbName" placeholder="dbName"></input>                
                <input type="text" data-bind="value: $data.tableName" placeholder="tableName"></input>
                <input type="text" data-bind="value: $data.URI" placeholder="URI"></input>
                <select data-bind="options: availableActions, value: action"></select>
                <i class="fa fa-minus"></i>
              </div>
              <a href="javascript: void(0)" data-bind='click: addPriviledge'>
                <i class="fa fa-plus"></i>
              </a>
            </div>
            Groups
            <div>
              <select data-bind="options: $root.availableHadoopGroups, selectedOptions: groups" size="5" multiple="true"></select>
            </div>
            Name
            <div>
              <input type="text" data-bind="value: $data.name"></input>
            </div>
          </div>
          <div>
            <button type="button" rel="tooltip" data-placement="bottom" data-original-title="${ _('Cancel') }" class="btn">
              <i class="fa fa-undo"></i>
            </button>
            <button type="button" rel="tooltip" data-placement="bottom" data-loading-text="${ _('Saving...') }" data-original-title="${ _('Save') }" class="btn"
                data-bind="click: $root.role.edit">
              <i class="fa fa-save"></i>
            </button>
          </div>          
        </div>
      </div>

      <div id="view" class="mainSection hide card card-small">
        <div class="card-heading simple"><h3>${ _('View') }</h3></div>
      </div>

      <div id="roles" class="mainSection hide card card-small">
        <div class="card-heading simple"><h3>${ _('Roles') }</h3></div>
           
        <div data-bind="foreach: $root.roles">
          <div data-bind="text: ko.mapping.toJSON($data), click: $root.list_sentry_privileges_by_role"></div><i class="fa fa-minus"></i>
        </div>
      </div>

      <div id="privileges" class="mainSection hide card card-small">
        <div class="card-heading simple"><h3>${ _('Privileges') }</h3></div>      
        
        <div data-bind="foreach: $root.privileges">
          <div data-bind="text: ko.mapping.toJSON($data)"></div><i class="fa fa-minus"></i>
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

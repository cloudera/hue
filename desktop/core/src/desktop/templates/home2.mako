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

${ commonheader(_('Welcome Home'), "home", user) | n,unicode }

<style type="text/css">
  .sidebar-nav {
    margin-bottom: 10px;
  }

  .sidebar-nav img {
    margin-right: 6px;
  }

  .sidebar-nav .dropdown-menu a {
    padding-left: 6px;
  }

  .tag {
    float: left;
    margin-right: 6px;
    margin-bottom: 4px;
  }

  .tag-counter {
    margin-top: 3px;
    margin-right: 4px;
  }

  .fa-times-circle:hover {
    color: #d84a38;
  }

  .toggle-tag, .document-tags-modal-checkbox, .tags-modal-checkbox {
    cursor: pointer;
  }

  .badge-left {
    border-radius: 9px 0px 0px 9px;
    padding-right: 5px;
  }

  .badge-right {
    border-radius: 0px 9px 9px 0px;
    padding-left: 5px;
  }

  .airy li {
    margin-bottom: 6px;
  }

  .trash-share {
    cursor: pointer;
  }

  .white {
    padding: 9px 18px;
    margin-top: 1px;
    overflow: hidden;
    font-size: 14px;
    line-height: 1.4;
    color: #737373;
    text-overflow: ellipsis;
  }

</style>

<div class="navbar navbar-inverse navbar-fixed-top nokids">
  <div class="navbar-inner">
    <div class="container-fluid">
      <div class="nav-collapse">
        <ul class="nav">
          <li class="currentApp">
            <a href="${ url('desktop.views.home') }">
              <img src="/static/art/home.png" />
              ${ _('My documents') }
            </a>
           </li>
        </ul>
      </div>
    </div>
  </div>
</div>

<div class="container-fluid">
  <div class="row-fluid">
    <div class="span2">
      <div class="sidebar-nav">
         <ul class="nav nav-list">
          <li class="nav-header">${_('Actions')}</li>
           <li class="dropdown">
              <a href="#" data-toggle="dropdown"><i class="fa fa-plus-circle"></i> ${_('New document')}</a>
              <ul class="dropdown-menu" role="menu">
                % if 'beeswax' in apps:
                <li><a href="${ url('beeswax:index') }"><img src="${ apps['beeswax'].icon_path }"/> ${_('Hive Query')}</a></li>
                % endif
                % if 'impala' in apps:
                <li><a href="${ url('impala:index') }"><img src="${ apps['impala'].icon_path }"/> ${_('Impala Query')}</a></li>
                % endif
                % if 'pig' in apps:
                <li><a href="${ url('beeswax:index') }"><img src="${ apps['pig'].icon_path }"/> ${_('Pig Script')}</a></li>
                % endif
                % if 'spark' in apps:
                <li><a href="${ url('spark:index') }"><img src="${ apps['spark'].icon_path }"/> ${_('Spark Job')}</a></li>
                % endif
                % if 'oozie' in apps:
                <li class="dropdown-submenu">
                  <a href="#"><img src="${ apps['oozie'].icon_path }"/> ${_('Oozie Scheduler')}</a>
                  <ul class="dropdown-menu">
                    <li><a href="${ url('oozie:create_workflow') }"><img src="/oozie/static/art/icon_oozie_workflow_24.png"/> ${_('Workflow')}</a></li>
                    <li><a href="${ url('oozie:create_coordinator') }"><img src="/oozie/static/art/icon_oozie_coordinator_24.png"/> ${_('Coordinator')}</a></li>
                    <li><a href="${ url('oozie:create_bundle') }"><img src="/oozie/static/art/icon_oozie_bundle_24.png"/> ${_('Bundle')}</a></li>
                  </ul>
                </li>
                % endif
              </ul>
           </li>
           <!-- ko template: { name: 'tag-template', data: history } -->
           <!-- /ko -->
           <!-- ko template: { name: 'tag-template', data: trash } -->
           <!-- /ko -->
           <li class="nav-header tag-mine-header">
             ${_('My Projects')}
             <div class="edit-tags" style="display: inline;cursor: pointer;margin-left: 6px" title="${ _('Create project') }" rel="tooltip" data-placement="right">
               <i class="fa fa-plus-circle" data-bind="click: addTag"></i>
             </div>
           </li>
           <!-- ko template: { name: 'tag-template', foreach: myTags } -->
           <!-- /ko -->
           <li data-bind="visible: myTags().length == 0">
             <a href="javascript:void(0)" class="edit-tags" style="line-height:24px">
               <i class="fa fa-plus-circle"></i> ${_('You currently own no projects. Click here to add one now!')}
             </a>
           </li>
          <li class="nav-header tag-shared-header">
            ${_('Shared with me')}
          </li>
          <!-- ko template: { name: 'shared-tag-template', foreach: sharedTags } -->
          <!-- /ko -->
          <li data-bind="visible: sharedTags().length == 0">
            <a href="javascript:void(0)" style="line-height:24px"><i class="fa fa-plus-circle"></i> ${_('There are currently no projects shared with you.')}
            </a>
          </li>
        </ul>
      </div>

    </div>

    <div class="span10">
      <div class="card card-home" style="margin-top: 0">
        <input id="searchInput" type="text" placeholder="Search for name, description, etc..." class="input-xlarge search-query pull-right" style="margin-right: 10px;margin-top: 3px">
        <h2 class="card-heading simple">${_('My Documents')}</h2>

        <div class="card-body">
          <p>
          <table class="table table-striped table-condensed" data-bind="visible: documents().length > 0">
            <thead>
              <tr>
                <th style="width: 26px">&nbsp;</th>
                <th style="width: 200px">${_('Name')}</th>
                <th>${_('Description')}</th>
                <th style="width: 150px">${_('Projects')}</th>
                <th style="width: 100px">${_('Owner')}</th>
                <th style="width: 150px">${_('Last Modified')}</th>
                <th style="width: 40px">${_('Sharing')}</th>
              </tr>
            </thead>
            <tbody data-bind="template: { name: 'document-template', foreach: documents }">
            </tbody>
          </table>
          <div data-bind="visible: documents().length == 0">
            <h4 style="color: #777; margin-bottom: 30px">${_('There are currently no documents in this project or tag.')}</h4>
          </div>
          </p>
        </div>
      </div>
    </div>

  </div>
</div>


<script type="text/html" id="tag-template">
  <li data-bind="click: $root.filterDocs, css: {'active': $root.selectedTag().id == id}">
    <a href="javascript:void(0)" style="padding-right: 4px">
      <i data-bind="css: {'fa': true, 'fa-trash-o':name() == 'trash', 'fa-clock-o': name() == 'history', 'fa-tag': name() != 'trash' && name() != 'history'}"></i> <span data-bind="text: name"></span>
      <i data-bind="click: removeTag, visible: name() != 'trash' && name() != 'history'" class="pull-right fa fa-times-circle"></i>
      <span class="badge pull-right tag-counter" data-bind="text: docs().length"></span>
    </a>
  </li>
</script>

<script type="text/html" id="shared-tag-template">
  <li class="white">
    <i class="fa fa-user"></i> <span data-bind="text: name"></span>
  </li>
  <!-- ko foreach: projects-->
  <li data-bind="click: $root.filterDocs, css: {'active': $root.selectedTag().id == id}">
    <a href="javascript:void(0)">
      &nbsp;&nbsp;&nbsp;<i class="fa fa-tag"></i> <span data-bind="text: name"></span> <span class="badge pull-right tag-counter" data-bind="text: docs().length"></span>
    </a>
  </li>
  <!-- /ko -->
</script>

<script type="text/html" id="document-template">
  <tr>
    <td style="width: 26px"><img data-bind="attr: { src: icon }"></td>
    <td><a data-bind="attr: { href: url }, text: name"></a></td>
    <td data-bind="text: description"></td>
    <td>
      <div class="documentTags" data-bind="foreach: tags">
        <span class="badge" data-bind="text: name"></span>
      </div>
    </td>
    <td data-bind="text: owner"></td>
    <td data-bind="text: lastModified"></td>
    <td style="width: 40px; text-align: center">
      <a rel="tooltip" data-placement="left" style="padding-left:10px" data-original-title="${ _("Share My saved query") }">
        <i data-bind="visible: isMine" class="fa fa-share-square-o"></i>
        <i data-bind="visible: ! isMine" class="fa fa-user"></i>
      </a>
    </td>
  </tr>
</script>

<div id="tagsModal" class="modal hide fade">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
    <h3>${_('Manage projects')}</h3>
  </div>
  <div class="modal-body">
    <p>
      <div data-bind="template: { name: 'tag-edit-template', foreach: myTags }"></div>
      <div class="clearfix"></div>
    </p>
  </div>
  <div class="modal-footer">
    <a href="#" data-dismiss="modal" class="btn">${_('Cancel')}</a>
    <a id="removeTags" href="#" class="btn btn-danger disable-feedback">${_('Remove selected')}</a>
  </div>
</div>


<div id="addTagModal" class="modal hide fade">
  <form class="form-inline form-padding-fix" onsubmit="addTag()">
    <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
      <h3>${_('Create project')}</h3>
    </div>
    <div class="modal-body">
      <p>
          <label>
            ${_('Project name')} <input id="tagsNew" type="text" class="input-xlarge">
          </label>
      </p>
    </div>
    <div class="modal-footer">
      <a href="#" data-dismiss="modal" class="btn">${_('Cancel')}</a>
      <a id="tagsNewBtn" href="#" class="btn btn-primary disable-feedback">${ _('Add') }</a>
    </div>
  </form>
</div>

<div id="removeTagModal" class="modal hide fade">
    <div class="modal-header">
        <a href="#" class="close" data-dismiss="modal">&times;</a>
        <h3>${_('Confirm Delete')}</h3>
    </div>
    <div class="modal-body">
        <p>${_('Are you sure you want to delete the project')} <strong><span data-bind="text: selectedForDelete().name"></span></strong>?</p>
    </div>
    <div class="modal-footer">
        <a class="btn" data-dismiss="modal">${_('No')}</a>
        <a data-bind="click: removeTagFinal" class="btn btn-danger">${_('Yes')}</a>
    </div>
</div>


<script type="text/html" id="tag-sharer-template">
  <div style="margin-right:10px;margin-bottom: 6px;float:left;">
    <span class="tags-modal-checkbox badge">
       <i class="fa fa-trash-o"></i> <span data-bind="text: name"></span>
    </span>
    <div data-bind="template: { name: 'tag-template', foreach: projects }"></div>
  </div>
</script>


<script type="text/html" id="tag-edit-template">
  <div style="margin-right:10px;margin-bottom: 6px;float:left;">
    <span class="tags-modal-checkbox badge">
       <i class="fa fa-trash-o"></i> <span data-bind="text: name"></span>
    </span>
  </div>
</script>

<script src="/static/ext/js/datatables-paging-0.1.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout.mapping-2.3.2.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/js/home.vm.js"></script>


<script type="text/javascript" charset="utf-8">
  var viewModel;
  $(document).ready(function () {
    viewModel = new HomeViewModel(${ json_tags | n,unicode }, ${ json_documents | n,unicode });
    ko.applyBindings(viewModel);

    viewModel.selectedTag.subscribe(function (value) {
      $("#searchInput").val("");
      $.totalStorage("hueHomeSelectedTag", value.id());
    });

    if ($.totalStorage("hueHomeSelectedTag") != null) {
      var _preselectedTag = viewModel.getTagById($.totalStorage("hueHomeSelectedTag"));
      if (_preselectedTag != null) {
        viewModel.filterDocs(_preselectedTag);
      }
    }
    else {
      viewModel.filterDocs(viewModel.history());
    }

    $("#searchInput").jHueDelayedInput(function () {
      viewModel.searchDocs($("#searchInput").val());
    });

    $("#tagsNewBtn").on("click", function () {
      var tag_name = $("#tagsNew").val(); // use ko var + bind enable/disable button accordingly (blank, duplicate, reserved...)?
      $.post("/desktop/api/tag/add_tag", {
        name: tag_name
      },function (data) {
        viewModel.createTag(data);
        $("#tagsNew").val("");
        $(document).trigger("info", "${_('Project created')}");
        $("#addTagModal").modal("hide");
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText); // reserved name, duplicate etc
      });
    });

    $("a[rel='tooltip']").tooltip();

  });

  function addTag() {
    $("#addTagModal").modal("show");
  }

  function removeTag(tag) {
    viewModel.selectedForDelete(tag);
    $("#removeTagModal").modal("show");
  }

  function removeTagFinal() {
    var tag = viewModel.selectedForDelete();
    $.post("/desktop/api/tag/remove_tag", {
      tag_id: tag.id()
    }, function (response) {
      if (response != null) {
        if (response.status == 0) {
          $(document).trigger("info", response.message);
          $("#removeTagModal").modal("hide");
          viewModel.removeTag(tag);
          viewModel.filterDocs(viewModel.history());
        }
        else {
          $(document).trigger("error", "${_("There was an error processing your action: ")}" + response.message);
        }
      }
    });
  }
</script>


${ commonfooter(messages) | n,unicode }

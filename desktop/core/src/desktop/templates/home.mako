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
  from desktop.views import commonheader, commonfooter, commonshare, _ko
  from django.utils.translation import ugettext as _

  from desktop.conf import USE_NEW_EDITOR
  use_new_home = USE_NEW_EDITOR.get()
%>

${ commonheader(_('Welcome Home'), "home", user, request) | n,unicode }

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

  .toggle-tag, .document-tags-modal-checkbox, .tags-modal-checkbox {
    cursor: pointer;
  }

  .badge-left {
    border-radius: 9px 0px 0px 9px;
    padding-right: 5px;
    font-weight: normal;
  }

  .badge-right {
    border-radius: 0px 9px 9px 0px;
    padding-left: 5px;
  }

  .badge-right:hover {
    background-color: #b94a48;
  }

  .airy li {
    margin-bottom: 6px;
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

<div class="navbar hue-title-bar nokids">
  <div class="navbar-inner">
    <div class="container-fluid">
      <div class="nav-collapse">
        <ul class="nav">
          <li class="app-header">
            <a href="${ url('desktop_views_home') }">
              <img src="${ static('desktop/art/home.png') }" class="app-icon" alt="${ _('Home icon') }" />
              ${ _('My documents') }
            </a>
           </li>
        </ul>
      </div>
      % if use_new_home:
      <div class="nav-collapse pull-right">
        <ul class="nav">
          <li class="app-header">
            <a href="${ url('desktop_views_home2') }">
              <img src="${ static('desktop/art/home.png') }" class="app-icon" alt="${ _('Home icon') }" />
              ${ _('New Home') }
            </a>
           </li>
        </ul>
      </div>
      % endif
    </div>
  </div>
</div>

<div id="homeComponents" class="container-fluid">
  <div class="row-fluid">
    <div class="span2">
      <div class="sidebar-nav">
         <ul class="nav nav-list">
          <li class="nav-header">${_('Actions')}</li>
           <li class="dropdown">
              <a href="#" data-toggle="dropdown"><i class="fa fa-plus-circle"></i> ${_('New document')}</a>
              <ul class="dropdown-menu" role="menu">
                % if 'beeswax' in apps:
                  <li><a href="${ url('beeswax:index') }"><img src="${ static(apps['beeswax'].icon_path) }" class="app-icon" alt="${ _('Hive icon') }"/> ${_('Hive Query')}</a></li>
                % endif
                % if 'impala' in apps:
                  <li><a href="${ url('impala:index') }"><img src="${ static(apps['impala'].icon_path) }" class="app-icon" alt="${ _('Impala icon') }"/> ${_('Impala Query')}</a></li>
                % endif
                % if 'pig' in apps:
                  <li><a href="${ url('pig:index') }"><img src="${ static(apps['pig'].icon_path) }" class="app-icon" alt="${ _('Pig icon') }"/> ${_('Pig Script')}</a></li>
                % endif
                % if 'spark' in apps:
                  <li><a href="${ url('notebook:index') }"><img src="${ static(apps['spark'].icon_path) }" class="app-icon" alt="${ _('Spark icon') }"/> ${_('Spark Job')}</a></li>
                % endif
                % if 'oozie' in apps:
                <li class="dropdown-submenu">
                  <a href="#"><img src="${ static(apps['oozie'].icon_path) }" class="app-icon" alt="${ _('Oozie icon') }"/> ${_('Oozie Scheduler')}</a>
                  <ul class="dropdown-menu">
                    <li><a href="${ url('oozie:new_workflow') }"><img src="${ static('oozie/art/icon_oozie_workflow_48.png') }" class="app-icon" alt="${ _('Oozie workflow icon') }"/> ${_('Workflow')}</a></li>
                    <li><a href="${ url('oozie:new_coordinator') }"><img src="${ static('oozie/art/icon_oozie_coordinator_48.png') }" class="app-icon" alt="${ _('Oozie coordinator icon') }"/> ${_('Coordinator')}</a></li>
                    <li><a href="${ url('oozie:new_bundle') }"><img src="${ static('oozie/art/icon_oozie_bundle_48.png') }" class="app-icon" alt="${ _('Oozie bundle icon') }"/> ${_('Bundle')}</a></li>
                  </ul>
                </li>
                % endif
              </ul>
           </li>
           <!-- ko template: { name: 'tag-template', data: trash } -->
           <!-- /ko -->
           <li class="nav-header tag-mine-header">
             ${_('My Projects')}
             <div class="edit-tags" style="display: inline;cursor: pointer;margin-left: 6px">
               <i class="fa fa-plus-circle" data-bind="click: addTag" title="${ _('Create project') }" rel="tooltip" data-placement="right"></i>
               <i class="fa fa-minus-circle" data-bind="click: removeTag, visible: $root.selectedTag().hasOwnProperty('owner') && $root.selectedTag().owner() == '${user}' && $root.selectedTag().name() != 'history'  && $root.selectedTag().name() != 'trash'  && $root.selectedTag().name() != 'default'"
                       title="${ _('Remove selected project') }" rel="tooltip" data-placement="right"></i>
             </div>
           </li>
           <!-- ko template: { name: 'tag-template', foreach: myTags } -->
           <!-- /ko -->
           <li data-bind="visible: myTags().length == 0">
             <a href="javascript:void(0)" class="edit-tags" style="line-height:24px" data-bind="click: addTag">
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
        <input id="searchInput" type="text" placeholder="Search for name, description, etc..." class="input-xlarge search-query" style="margin-left: 20px;margin-top: 5px">
        ##<h2 class="card-heading simple">${_('My Documents')}</h2>

        <div class="card-body">
          <p>
          <table id="documents" class="table table-condensed" data-bind="visible: documents().length > 0">
            <thead>
              <tr>
                <th style="width: 26px">&nbsp;</th>
                <th style="width: 200px">${_('Name')}</th>
                <th>${_('Description')}</th>
                <th style="width: 150px">${_('Last Modified')}</th>
                <th style="width: 80px; text-align: center">${_('Project')}</th>
                <th style="width: 40px">${_('Sharing')}</th>
              </tr>
            </thead>
            <tbody data-bind="template: { name: 'document-template', foreach: renderableDocuments}">
            </tbody>
            <tfoot data-bind="visible: documents().length > 0">
              <tr>
                <td colspan="7">
                  <div class="pull-right" style="margin-top: 10px" data-bind="visible: hasPrevious() || hasNext()">
                    <span>${_('Page')} <input type="number" class="input-mini" style="text-align: center" data-bind="value: page"> ${_('of')} <span data-bind="text: totalPages"></span></span>
                  </div>
                  <div class="pagination">
                    <ul>
                      <li><a data-bind="click: previousPage, visible: hasPrevious">${_('Previous')}</a></li>
                      <li><a data-bind="click: nextPage, visible: hasNext">${_('Next')}</a></li>
                    </ul>
                  </div>
                </td>
              </tr>
            </tfoot>
          </table>
          <div data-bind="visible: documents().length == 0">
            <h4 style="color: #777; margin-bottom: 30px">${_('There are currently no documents in this project or tag.')}</h4>
          </div>
          </p>
        </div>
      </div>
    </div>

  </div>



  <div id="documentMoveModal" class="modal fade hide">
    <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
      <h2 class="modal-title">${_('Move to a project')}</h2>
    </div>
    <div class="modal-body">
      <p>
        ${_('Select the project you want to move this document to')}
        <ul class="unstyled">
          <!-- ko foreach: myTags -->
            <li>
              <a href="javascript:void(0)" style="padding-left: 4px" data-bind="click: moveDocFinal">
                <i class="fa fa-tag"></i> <span data-bind="text: name"></span>
              </a>
            </li>
          <!-- /ko -->
        </ul>
      </p>
    </div>
    <div class="modal-footer">
      <a class="btn" data-dismiss="modal">${_('Cancel')}</a>
    </div>
  </div>

</div>


<script type="text/html" id="tag-template">
  <li data-bind="click: $root.filterDocs, css: {'active': $root.selectedTag().id == id}">
    <a href="javascript:void(0)" style="padding-right: 4px">
      <i data-bind="css: {'fa': true, 'fa-trash-o':name() == 'trash', 'fa-clock-o': name() == 'history', 'fa-tag': name() != 'trash' && name() != 'history'}"></i> <span data-bind="html: name"></span>
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
    <a href="javascript:void(0)" style="padding-right: 4px">
      &nbsp;&nbsp;&nbsp;<i class="fa fa-tag"></i> <span data-bind="html: name"></span> <span class="badge pull-right tag-counter" data-bind="text: docs().length"></span>
    </a>
  </li>
  <!-- /ko -->
</script>

<script type="text/html" id="document-template">
  <tr>
    <td style="width: 26px"><img data-bind="attr: { src: icon }" class="app-icon" alt="${ _('Document icon') }"></td>
    <td><a data-bind="attr: { href: url }, html: name"></a></td>
    <td data-bind="html: description"></td>
    <td data-bind="text: lastModified"></td>
    <td style="text-align: center; white-space: nowrap">
      <a href="javascript:void(0)" rel="tooltip" data-placement="left" data-bind="click: moveDoc, attr: {'data-original-title': '${ _ko("Change project for") } '+name}" style="padding-left:8px; padding-right: 8px">
        <span data-bind="foreach: tags">
          <!-- ko if: name != 'trash'-->
          <span class="badge" data-bind="html: name"></span>
          <!-- /ko -->
        </span>
      </a>
    </td>
    <td style="width: 40px; text-align: center">
      <a class="share-link" rel="tooltip" data-placement="left" style="padding-left:10px; padding-right: 10px" data-bind="click: shareDoc, attr: {'data-original-title': '${ _ko("Share") } '+name}, visible: isMine , css: {'baseShared': true, 'isShared': perms.read.users.length + perms.read.groups.length + perms.write.users.length + perms.write.groups.length > 0}">
        <i class="fa fa-users"></i>
      </a>
      <i class="fa fa-ban" style="padding-left:8px; padding-right: 8px" data-bind="visible: !isMine"></i>
    </td>
  </tr>
</script>

<div id="addTagModal" class="modal hide fade">
  <form class="form-inline form-padding-fix" onsubmit="javascript:{return false;}">
    <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
      <h2 class="modal-title">${_('Create project')}</h2>
    </div>
    <div class="modal-body">
      <p>
          <label>
            ${_('Project name')} <input id="tagsNew" type="text" class="input-xlarge">
          </label>
      </p>
    </div>
    <div class="modal-footer">
      <div id="saveProjectAlert" class="alert-message error hide" style="position: absolute; left: 78px;">
        <span class="label label-important"></span>
      </div>
      <a href="#" data-dismiss="modal" class="btn">${_('Cancel')}</a>
      <a id="tagsNewBtn" href="#" class="btn btn-primary disable-feedback">${ _('Add') }</a>
    </div>
  </form>
</div>

<div id="removeTagModal" class="modal hide fade">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
    <h2 class="modal-title">${_('Confirm Delete')}</h2>
  </div>
  <div class="modal-body">
    <p>${_('Are you sure you want to delete the project')} <strong><span data-bind="text: selectedTagForDelete().name"></span></strong>? ${_('All its documents will be moved to the default tag.')}</p>
  </div>
  <div class="modal-footer">
    <a class="btn" data-dismiss="modal">${_('No')}</a>
    <a id="tagRemoveBtn" class="pointer btn btn-danger disable-feedback">${_('Yes')}</a>
  </div>
</div>

${ commonshare() | n,unicode }
<script src="${ static('desktop/ext/js/datatables-paging-0.1.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/js/home.vm.js') }"></script>
<script src="${ static('desktop/js/share.vm.js') }"></script>

<script type="text/javascript">
  var viewModel, shareViewModel, JSON_USERS_GROUPS;

  var JSON_TAGS = ${ json_tags | n,unicode };
  var JSON_DOCS = ${ json_documents | n,unicode };

  $(document).ready(function () {
    viewModel = new HomeViewModel(JSON_TAGS, JSON_DOCS);
    ko.applyBindings(viewModel, $('#homeComponents')[0]);

    shareViewModel = initSharing("#documentShareModal", viewModel.updateDoc);

    var selectedUserOrGroup, map, dropdown = null;

    viewModel.selectedTag.subscribe(function (value) {
      $("#searchInput").val("");
      $.totalStorage("hueHomeSelectedTag", value.id());
    });

    function getFirstAvailableDoc() {
      var _found = null;
      JSON_TAGS.mine.forEach(function(tag){
        if (_found == null && tag.docs.length > 0){
          _found = tag.id;
        }
      });
      JSON_TAGS.notmine.forEach(function(tag){
        tag.projects.forEach(function(project){
          if (_found == null && project.docs.length > 0){
            _found = project.id;
          }
        });
      });
      if (_found != null){
        return viewModel.getTagById(_found);
      }
      return viewModel.history();
    }

    if ($.totalStorage("hueHomeSelectedTag") != null) {
      var _preselectedTag = viewModel.getTagById($.totalStorage("hueHomeSelectedTag"));
      if (_preselectedTag != null) {
        viewModel.filterDocs(_preselectedTag);
      }
    }
    else {
      viewModel.filterDocs(getFirstAvailableDoc());
    }

    $("#searchInput").jHueDelayedInput(function () {
      viewModel.searchDocs($("#searchInput").val());
    });

    $("#tagsNewBtn").on("click", function () {
      var tag_name = $("#tagsNew").val();
  
    if ($.trim(tag_name) == "") {
      $("#saveProjectAlert span").text("${_('File name is required.')}");
      $("#saveProjectAlert").show();
      $("#tagsNew").addClass("fieldError");
      resetPrimaryButtonsStatus(); // Globally available
      return false;
    }

    $.post("/desktop/api/tag/add_tag", {
        name: tag_name
      }, function (data) {
        if (data.status == -1) {
          $("#saveProjectAlert span").text("${_('project name already exists')}");
          $("#saveProjectAlert").show();
          resetPrimaryButtonsStatus(); //globally available
        }
        else {
          data.name = hueUtils.htmlEncode(data.name);
          viewModel.createTag(data);
          $("#tagsNew").val("");
          $(document).trigger("info", "${_('Project created')}");
          $("#addTagModal").modal("hide");
        }
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", "${_("There was an error processing your action: ")}" + xhr.responseText); // reserved name, duplicate etc
      });
    });

    $("#tagRemoveBtn").on("click", function(){
      removeTagFinal();
    });

    $("a[rel='tooltip']").tooltip();

  });

  function addTag() {
    $("#tagsNew").val('');
    $("#addTagModal").modal("show");
    $("#saveProjectAlert").hide();
  }

  function removeTag() {
    viewModel.selectedTagForDelete(viewModel.selectedTag());
    $("#removeTagModal").modal("show");
  }

  function removeTagFinal() {
    var tag = viewModel.selectedTagForDelete();
    $.post("/desktop/api/tag/remove_tag", {
      tag_id: tag.id()
    }, function (response) {
      if (response != null) {
        if (response.status == 0) {
          $(document).trigger("info", response.message);
          $("#removeTagModal").modal("hide");
          viewModel.deleteTag(tag);
          viewModel.filterDocs(viewModel.history());
        }
        else {
          $(document).trigger("error", "${_("There was an error processing your action: ")}" + response.message);
        }
      }
    }).fail(function (response) {
      $(document).trigger("error", "${_("There was an error processing your action: ")}" + response.responseText);
    });
  }

  function shareDoc(doc) {
    shareViewModel.selectedDoc(doc);
    openShareModal();
  }

  function moveDoc(doc) {
    shareViewModel.selectedDoc(doc);
    $("#documentMoveModal").modal("show");
  }

  function moveDocFinal(tag) {
    $.post("/desktop/api/doc/update_tags", {
      data: JSON.stringify({
        doc_id: shareViewModel.selectedDoc().id,
        tag_ids: [tag.id()]
      })
    }, function (response) {
      if (response != null) {
        if (response.status != 0) {
          $(document).trigger("error", "${_("There was an error processing your action: ")}" + response.message);
        }
        else {
          $(document).trigger("info", "${ _("Project updated successfully.") }");
          viewModel.updateDoc(response.doc);
        }
      }
      $("#documentMoveModal").modal("hide");
    }).fail(function (response) {
      $(document).trigger("error", "${_("There was an error processing your action: ")}" + response.responseText);
    });
  }

</script>

${ commonfooter(request, messages) | n,unicode }

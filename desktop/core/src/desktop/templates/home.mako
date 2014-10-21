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
  from desktop.views import commonheader, commonfooter, commonshare
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

<div class="navbar navbar-inverse navbar-fixed-top nokids">
  <div class="navbar-inner">
    <div class="container-fluid">
      <div class="nav-collapse">
        <ul class="nav">
          <li class="currentApp">
            <a href="${ url('desktop.views.home') }">
              <img src="/static/art/home.png" class="app-icon" />
              ${ _('My documents') }
            </a>
           </li>
        </ul>
      </div>
    </div>
  </div>
</div>

<div id='documentList' class="container-fluid">
  <div class="row-fluid">
    <div class="span2">
      <div class="sidebar-nav">
         <ul class="nav nav-list">
          <li class="nav-header">${_('Actions')}</li>
           <li class="dropdown">
              <a href="#" data-toggle="dropdown"><i class="fa fa-plus-circle"></i> ${_('New document')}</a>
              <ul class="dropdown-menu" role="menu">
                % if 'beeswax' in apps:
                <li><a href="${ url('beeswax:index') }"><img src="${ apps['beeswax'].icon_path }" class="app-icon"/> ${_('Hive Query')}</a></li>
                % endif
                % if 'impala' in apps:
                <li><a href="${ url('impala:index') }"><img src="${ apps['impala'].icon_path }" class="app-icon"/> ${_('Impala Query')}</a></li>
                % endif
                % if 'pig' in apps:
                <li><a href="${ url('beeswax:index') }"><img src="${ apps['pig'].icon_path }" class="app-icon"/> ${_('Pig Script')}</a></li>
                % endif
                % if 'spark' in apps:
                <li><a href="${ url('spark:index') }"><img src="${ apps['spark'].icon_path }" class="app-icon"/> ${_('Spark Job')}</a></li>
                % endif
                % if 'oozie' in apps:
                <li class="dropdown-submenu">
                  <a href="#"><img src="${ apps['oozie'].icon_path }" class="app-icon"/> ${_('Oozie Scheduler')}</a>
                  <ul class="dropdown-menu">
                    <li><a href="${ url('oozie:create_workflow') }"><img src="/oozie/static/art/icon_oozie_workflow_48.png" class="app-icon"/> ${_('Workflow')}</a></li>
                    <li><a href="${ url('oozie:create_coordinator') }"><img src="/oozie/static/art/icon_oozie_coordinator_48.png" class="app-icon"/> ${_('Coordinator')}</a></li>
                    <li><a href="${ url('oozie:create_bundle') }"><img src="/oozie/static/art/icon_oozie_bundle_48.png" class="app-icon"/> ${_('Bundle')}</a></li>
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
          <table id="documents" class="table table-striped table-condensed" data-bind="visible: documents().length > 0">
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
    <td style="width: 26px"><img data-bind="attr: { src: icon }" class="app-icon"></td>
    <td><a data-bind="attr: { href: url }, html: name"></a></td>
    <td data-bind="html: description"></td>
    <td data-bind="text: lastModified"></td>
    <td style="text-align: center; white-space: nowrap">
      <a href="javascript:void(0)" rel="tooltip" data-placement="left" data-bind="click: moveDoc, attr: {'data-original-title': '${ _("Change project for") } '+name}" style="padding-left:8px; padding-right: 8px">
        <span data-bind="foreach: tags">
          <!-- ko if: name != 'trash'-->
          <span class="badge" data-bind="html: name"></span>
          <!-- /ko -->
        </span>
      </a>
    </td>
    <td style="width: 40px; text-align: center">
      <a class="share-link" rel="tooltip" data-placement="left" style="padding-left:10px; padding-right: 10px" data-bind="click: shareDoc, attr: {'data-original-title': '${ _("Share") } '+name}, visible: isMine , css: {'baseShared': true, 'isShared': perms.read.users.length + perms.read.groups.length > 0}">
        <i class="fa fa-users"></i>
      </a>
      <i class="fa fa-ban" style="padding-left:8px; padding-right: 8px" data-bind="visible: !isMine"></i>
    </td>
  </tr>
</script>

<div id="addTagModal" class="modal hide fade">
  <form class="form-inline form-padding-fix" onsubmit="javascript:{return false;}">
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
        <p>${_('Are you sure you want to delete the project')} <strong><span data-bind="text: selectedTagForDelete().name"></span></strong>? ${_('All its documents will be moved to the default tag.')}</p>
    </div>
    <div class="modal-footer">
        <a class="btn" data-dismiss="modal">${_('No')}</a>
        <a data-bind="click: removeTagFinal" class="btn btn-danger">${_('Yes')}</a>
    </div>
</div>

<div id="documentMoveModal" class="modal hide fade">
    <div class="modal-header">
        <a href="#" class="close" data-dismiss="modal">&times;</a>
        <h3>${_('Move to a project')}</h3>
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

${ commonshare() | n,unicode }
<script src="/static/ext/js/datatables-paging-0.1.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout.mapping-2.3.2.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/js/home.vm.js"></script>
<script src="/static/js/share.vm.js"></script>

<script type="text/javascript" charset="utf-8">
  var viewModel, shareViewModel, JSON_USERS_GROUPS;

  var JSON_TAGS = ${ json_tags | n,unicode };
  var JSON_DOCS = ${ json_documents | n,unicode };

  $(document).ready(function () {
    viewModel = new HomeViewModel(JSON_TAGS, JSON_DOCS);
    ko.applyBindings(viewModel, $('#documentList')[0]);

    shareViewModel = setupSharing("#documentShareModal", viewModel.updateDoc);

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
      $.post("/desktop/api/tag/add_tag", {
        name: tag_name
      },function (data) {
        data.name = hue.htmlEncode(data.name);
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
    });
  }

  function shareDoc(doc) {
    shareViewModel.selectedDoc(doc);
    $("#documentShareModal").modal("show");
  }

  function moveDoc(doc) {
    viewModel.selectedDoc(doc);
    $("#documentMoveModal").modal("show");
  }

  function moveDocFinal(tag) {
    $.post("/desktop/api/doc/update_tags", {
      data: JSON.stringify({
        doc_id: viewModel.selectedDoc().id,
        tag_ids: [tag.id()]
      })
    }, function (response) {
      if (response != null){
        if (response.status != 0) {
          $(document).trigger("error", "${_("There was an error processing your action: ")}" + response.message);
        }
        else {
          $(document).trigger("info", "${ _("Project updated successfully.") }");
          viewModel.updateDoc(response.doc);
        }
      }
      $("#documentMoveModal").modal("hide");
    })
  }

</script>


<style type="text/css">
  .tourSteps {
    min-height: 150px;
  }
</style>

<script src="/static/ext/js/routie-0.3.0.min.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript" charset="utf-8">
$(document).ready(function(){
  var currentStep = "tourStep1";

  routie({
    "tourStep1":function () {
      showStep("tourStep1");
    },
    "tourStep2":function () {
      showStep("tourStep2");
    },
    "tourStep3":function () {
      showStep("tourStep3");
    }
  });

  function showStep(step) {
    currentStep = step;

    $("a.tourStep").parent().removeClass("active");
    $("a.tourStep[href=#" + step + "]").parent().addClass("active");
    if (step == "tourStep3") {
      $("#tourLastStep").parent().addClass("active");
    }
    $(".tourStepDetails").hide();
    $("#" + step).show();
  }

  if ($.totalStorage("jHueTourHideModal") == null || $.totalStorage("jHueTourHideModal") == false) {
    $("#jHueTourModal").modal();
    $.totalStorage("jHueTourHideModal", true);
    $("#jHueTourModalChk").attr("checked", "checked");
    $("#jHueTourModalChk").on("change", function () {
      $.totalStorage("jHueTourHideModal", $(this).is(":checked"));
    });
    $("#jHueTourModalClose").on("click", function () {
      $("#jHueTourFlag").click();
      $("#jHueTourModal").modal("hide");
    });
  }
});
</script>

  <div id="jHueTourModal" class="modal hide fade" tabindex="-1">
    <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
      <h3>${_('Did you know?')}</h3>
    </div>
    <div class="modal-body">
     <div class="row-fluid">
       <div id="properties" class="section">
      <ul class="nav nav-tabs" style="margin-bottom: 0">
        <li class="active"><a href="#tourStep1" class="tourStep">${ _('Step 1:') } ${ _('Add data') }</a></li>
        <li><a href="#tourStep2" class="tourStep">${ _('Step 2:') }  ${ _('Query data') }</a></li>
        <li><a id="tourLastStep" href="#tourStep3" class="tourStep">${ _('Step 3:') } ${_('Do more!') }</a></li>
      </ul>
    </div>

    <div class="tourSteps">
      <div id="tourStep1" class="tourStepDetails">
        <div class="pull-left" style="color: #DDDDDD;font-size: 116px;margin: 10px; margin-right: 20px"><i class="fa fa-download"></i></div>
        <div style="margin: 40px">
          <p>
            ${ _('With') }  <span class="badge badge-info"><i class="fa fa-file"></i> File Browser</span>
            ${ _('and the apps in the') }  <span class="badge badge-info">Data Browsers <b class="caret"></b></span> ${ _('section, upload, view your data and create tables.') }
          </p>
          <p>
            ${ _('Pre-installed samples are also already there.') }
          </p>
        </div>
      </div>

      <div id="tourStep2" class="tourStepDetails hide">
          <div class="pull-left" style="color: #DDDDDD;font-size: 116px;margin: 10px; margin-right: 20px"><i class="fa fa-search"></i></div>
          <div style="margin: 40px">
            <p>
              ${ _('Then query and visualize the data with the') } <span class="badge badge-info">Query Editors <b class="caret"></b></span>
               ${ _('and') }  <span class="badge badge-info">Search <b class="caret"></b></span>
            </p>
          </div>
      </div>

      <div id="tourStep3" class="tourStepDetails hide">
        <div class="pull-left" style="color: #DDDDDD;font-size: 116px;margin: 10px; margin-right: 20px"><i class="fa fa-flag-checkered"></i></div>
        <div style="margin: 40px">
          % if tours_and_tutorials:
          <p>
            ${ _('Tours were created to guide you around.') }
            ${ _('You can see the list of tours by clicking on the checkered flag icon') } <span class="badge badge-info"><i class="fa fa-flag-checkered"></i></span>
            ${ ('at the top right of this page.') }
          </p>
          % endif
          <p>
            ${ _('Additional documentation is available at') } <a href="http://learn.gethue.com">learn.gethue.com</a>.
          </p>
        </div>
      </div>
     </div>
     </div>
     <div class="modal-footer">
       <label class="checkbox" style="float:left"><input id="jHueTourModalChk" type="checkbox" />${_('Do not show this dialog again')}</label>
       <a id="jHueTourModalClose" href="#" class="btn btn-primary disable-feedback">${_('Got it, prof!')}</a>
     </div>
   </div>

${ commonfooter(messages) | n,unicode }

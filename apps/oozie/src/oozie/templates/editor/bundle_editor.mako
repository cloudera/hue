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

<%namespace name="dashboard" file="/common_dashboard.mako" />

${ commonheader(_("Bundle Editor"), "Oozie", user) | n,unicode }

<script type="text/javascript">
  if (window.location.hash != "") {
    if (window.location.hash.indexOf("bundle") > -1) {
      location.href = "/oozie/editor/bundle/edit/?" + window.location.hash.substr(1);
    }
  }
</script>



<div class="search-bar">
  <div class="pull-right" style="padding-right:50px">
    <a title="${ _('Submit') }" rel="tooltip" data-placement="bottom" data-bind="click: showSubmitPopup, css: {'btn': true}">
      <i class="fa fa-play"></i>
    </a>
    <a title="${ _('Edit') }" rel="tooltip" data-placement="bottom" data-bind="click: toggleEditing, css: {'btn': true, 'btn-inverse': isEditing}">
      <i class="fa fa-pencil"></i>
    </a>
    &nbsp;&nbsp;&nbsp;
    % if user.is_superuser:
      <button type="button" title="${ _('Settings') }" rel="tooltip" data-placement="bottom" data-toggle="modal" data-target="#settingsModal" data-bind="css: {'btn': true}">
        <i class="fa fa-cog"></i>
      </button>
      &nbsp;&nbsp;&nbsp;
      <button type="button" title="${ _('Save') }" rel="tooltip" data-placement="bottom" data-loading-text="${ _("Saving...") }" data-bind="click: $root.save, css: {'btn': true}">
        <i class="fa fa-save"></i>
      </button>
      &nbsp;&nbsp;&nbsp;
      <a class="btn" href="${ url('oozie:new_bundle') }" title="${ _('New') }" rel="tooltip" data-placement="bottom" data-bind="css: {'btn': true}">
        <i class="fa fa-file-o"></i>
      </a>
      <a class="btn" href="${ url('oozie:list_editor_bundles') }" title="${ _('Bundles') }" rel="tooltip" data-placement="bottom" data-bind="css: {'btn': true}">
        <i class="fa fa-tags"></i>
      </a>
    % endif
  </div>

  <form class="form-search">
    <div class="inline object-name">
      <span data-bind="editable: $root.bundle.name, editableOptions: {enabled: $root.isEditing(), placement: 'right'}"></span>
    </div>
  </form>
</div>


<div class="container-fluid">
  <div class="row-fluid">
    <div class="span12 bundle">

      <div class="card card-home">
        <h1 class="card-heading simple">${ _('Which schedules to bundle?') }</h1>

        <div class="card-body">

          <a class="pointer" data-bind="click: function() { showChooseCoordinator(); }">
            <i class="fa fa-plus"></i> ${ _('Add a coordinator') }
          </a>

          
          <ul data-bind="foreach: bundle.coordinators" class="unstyled">
            <li>
              <h3><a class="pointer" data-bind="click: function() { showChooseCoordinator(this); }, text: $root.getCoordinatorById(coordinator()).name"></a></h3>

              <ul data-bind="foreach: properties" class="unstyled">
                <li>
                  <input data-bind="value: name"/>
                  <input data-bind="value: value"/>
                  <a href="#" data-bind="click: function(){ $parent.properties.remove(this); }">
                    <i class="fa fa-minus"></i>
                  </a>
                </li>
              </ul>

              <a class="pointer" data-bind="click: function(){ $data.properties.push({'name': '', 'value': ''}); }">
                <i class="fa fa-plus"></i> ${ _('Add a parameter') }
              </a>
            </li>          
          </ul>
        </div>
        
      </div>

    </div>
  </div>
</div>


<div id="chooseCoordinatorDemiModal" class="demi-modal hide" data-backdrop="false">
  <div class="modal-body">
    <a href="javascript: void(0)" data-dismiss="modal" class="pull-right"><i class="fa fa-times"></i></a>
    <div style="float: left; margin-right: 10px;text-align: center">
      <input type="text" data-bind="clearable: $root.coordinatorModalFilter, valueUpdate:'afterkeydown'" placeholder="${_('Filter coordinators')}" class="input" style="float: left" /><br/>
    </div>
    <div>
      <ul data-bind="foreach: $root.filteredModalCoordinators().sort(function (l, r) { return l.name() > r.name() ? 1 : -1 }), visible: $root.filteredModalCoordinators().length > 0"
          class="unstyled inline fields-chooser" style="height: 100px; overflow-y: auto">
        <li data-bind="click: selectCoordinator">
          <span class="badge badge-info"><span data-bind="text: name(), attr: {'title': uuid()}"></span>
          </span>
        </li>
      </ul>
      <div class="alert alert-info inline" data-bind="visible: $root.filteredModalCoordinators().length == 0" style="margin-left: 250px;margin-right: 50px; height: 42px;line-height: 42px">
        ${_('There are no coordinators matching your search term.')}
      </div>
    </div>
  </div>
</div>


<div id="settingsModal" class="modal hide fade">
  <div class="modal-header" style="padding-bottom: 2px">
    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>
    <h3 id="myModalLabel">${ _('Settings') }</h3>
  </div>
  <div class="modal-body">
      <h4>${ _('Kick off time') }</h4>
      <input data-bind="value: bundle.properties.kickoff"/>
        
      <h4>${ _('Submission Parameters') }</h4>
      <ul data-bind="foreach: bundle.properties.parameters" class="unstyled">
        <li>
          <input data-bind="value: name"/>
          <input data-bind="value: value"/>
          <a href="#" data-bind="click: function(){ $root.bundle.properties.parameters.remove(this); }">
            <i class="fa fa-minus"></i>
          </a>
        </li>
      </ul>
      <a class="pointer" data-bind="click: function(){ $root.bundle.properties.parameters.push({'name': '', 'value': ''}); }">
        <i class="fa fa-plus"></i> ${ _('Add parameter') }
      </a>
  </div>
</div>


<div id="submit-modal" class="modal hide"></div>

<div id="exposeOverlay"></div>

<link rel="stylesheet" href="/static/ext/css/hue-filetypes.css">
<link rel="stylesheet" href="/static/ext/css/hue-charts.css">
<link rel="stylesheet" href="/static/ext/chosen/chosen.min.css">
<link rel="stylesheet" href="/oozie/static/css/common-editor.css">
<link rel="stylesheet" href="/oozie/static/css/coordinator-editor.css">

${ dashboard.import_layout() }

<script src="/static/ext/js/bootstrap-editable.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/js/hue.utils.js"></script>
<script src="/static/js/ko.editable.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/chosen/chosen.jquery.min.js" type="text/javascript" charset="utf-8"></script>

${ dashboard.import_bindings() }

<script src="/oozie/static/js/bundle-editor.ko.js" type="text/javascript" charset="utf-8"></script>


<script type="text/javascript">
  var viewModel = new BundleEditorViewModel(${ bundle_json | n,unicode }, ${ coordinators_json | n,unicode });
  ko.applyBindings(viewModel);

  var tempCoordinator = null;
  function showChooseCoordinator(coord) {
    if (typeof coord != "undefined"){
      tempCoordinator = coord;  
    }
    $("#chooseCoordinatorDemiModal").modal("show");
  }

  function selectCoordinator(coord) {
    if (tempCoordinator != null){
      tempCoordinator.coordinator(coord.uuid());
      tempCoordinator = null;
    } 
    else  {
      viewModel.addBundledCoordinator(coord.uuid());
    }
    $("#chooseCoordinatorDemiModal").modal("hide");
  }

  $(document).on("showSubmitPopup", function(event, data){
    $('#submit-modal').html(data);
    $('#submit-modal').modal('show');
  });

  $(document).ready(function() {
    $("#chooseCoordinatorDemiModal").modal({
      show: false
    });
  });
</script>

${ commonfooter(messages) | n,unicode }

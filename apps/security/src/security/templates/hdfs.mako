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
${ layout.menubar(section='hdfs') }


<style type="text/css">
  #nav-bar ul {
    list-style-type: none;
    padding: 0;
  }

  .tree {
    margin-left: 0 !important;
    padding-left: 0 !important;
  }

  .node-row {
    margin: 4px;
    padding: 2px;
    cursor: pointer;
    border: 1px dashed #FFFFFF;
  }

  .node-row:hover {
    background-color: #F6F6F6;
  }

  .node-row a {
    cursor: pointer;
  }

  .node-row.selected {
    border: 1px dashed #CCCCCC;
  }

  #aclPopover {
    position: absolute;
    z-index: 1028;
    # # under the top menu
  }

  .loading-popover {
    width: 200px;
    height: 120px;
    line-height: 120px;
    color: #999999;
  }

  .popover-title {
    word-break: break-all;
  }
</style>


<script type="text/html" id="acl-edition">
  <div data-bind="visible: status() != 'deleted'">
    <input type="radio" value="group" data-bind="checked: type, attr: { name: 'aclType' + $index() + (isDefault() ? 'isDefault' : 'notDefault') }"/> ${ _('group') }
    <input type="radio" value="user" data-bind="checked: type, attr: { name: 'aclType' + $index() + (isDefault() ? 'isDefault' : 'notDefault') }"/> ${ _('user') }
    <input type="radio" value="mask" data-bind="checked: type, attr: { name: 'aclType' + $index() + (isDefault() ? 'isDefault' : 'notDefault') }"/> ${ _('mask') }
    <input type="radio" value="other" data-bind="checked: type, attr: { name: 'aclType' + $index() + (isDefault() ? 'isDefault' : 'notDefault') }"/> ${ _('other') }

    <input type="text" data-bind="value: name, valueUpdate:'afterkeydown'" class="input-small" placeholder="${ _('name...') }"/>
    ##<select data-bind="options: $root.availableHadoopGroups, value: name, optionsCaption: '', valueUpdate:'afterkeydown'" class="input-small" placeholder="${ _('name...') }"/>

    <input type="checkbox" data-bind="checked: r"/>
    <input type="checkbox" data-bind="checked: w"/>
    <input type="checkbox" data-bind="checked: x"/>
    <a href="javascript: void(0)">
      <i class="fa fa-minus" data-bind="click: $root.assist.removeAcl"></i>
    </a>
  </div>
</script>

<div class="container-fluid">
  <div class="row-fluid">
    <div class="span2">
      <div class="sidebar-nav">
        <ul class="nav nav-list">
          <li class="nav-header">${ _('ACLs') }</li>
          <li class="active"><a href="#edits"><i class="fa fa-pencil"></i> ${ _('Edit') }</a></li>
          <li><a href="#view"><i class="fa fa-eye"></i> ${ _('View') }</a></li>
          <li class="nav-header"><i class="fa fa-group"></i> ${ _('Users') }
            </br>
            <input type="checkbox" checked="checked"> ${_('Me')}
            </br>          
            <select data-bind="options: availableHadoopUsers, value: doAs" size="10"></select>
          </li>          
          <li class="nav-header"><i class="fa fa-group"></i> ${ _('Groups') }
            </br>
            <input type="checkbox" checked="checked"> ${_('Me')}
            </br>
            <select data-bind="options: availableHadoopGroups" size="10" multiple="true"></select>
          </li>    
        </ul>
      </div>
    </div>
    <div class="span10">
      <div id="edit" class="section card card-small">
        <h1 class="card-heading simple">${ _('Edit ACLs') }</h1>
        <div class="card-body">
          <div class="row-fluid">
            <div class="span8">
              <input type="text" class="input-xxlarge" data-bind="value: $root.assist.path, valueUpdate: 'afterkeydown'"/>
              <div id="nav-bar" data-bind="template: { name: 'tree-template', data: $root.assist.treeData }"></div>
            </div>
            <div class="span4">

              <div id="aclPopover" class="popover right">
                <div class="arrow"></div>
                <h3 class="popover-title"><a data-bind="attr: { href: '/filebrowser/view' + $root.assist.path() }" target="_blank" title="${ _('Open in File Browser') }"><span data-bind="text:$root.assist.path"></span> <i class="fa fa-external-link"></i></a></h3>
                <div class="popover-content">
                  <p>
                    <div class="left" data-bind="visible: !$root.assist.isLoadingAcls()">
                      <i class="fa fa-user" style="color: #999999"></i> <strong><span data-bind="text: $root.assist.owner"></span></strong>&nbsp;&nbsp;
                      <i class="fa fa-users" style="color: #999999"></i> <strong><span data-bind="text: $root.assist.group"></span></strong>

                      <a href="javascript: void(0)"><i class="fa fa-header"></i> View in text</a>

                      <br/>
                      <div data-bind="foreach: $root.assist.regularAcls">
                        <div data-bind="template: {name: 'acl-edition'}"></div>
                      </div>

                      <a href="javascript: void(0)" data-bind="click: $root.assist.addAcl"><i class="fa fa-plus"></i></a>

                      <br/>

                      Default (<i class="fa fa-times"></i> bulk delete?)
                      <div data-bind="foreach: $root.assist.defaultAcls">
                        <div data-bind="template: {name: 'acl-edition'}"></div>
                      </div>
                      <a href="javascript: void(0)" data-bind="click: $root.assist.addDefaultAcl"><i class="fa fa-plus"></i></a>

                      <div data-bind="visible: $root.assist.changedAcls().length">
                        <button type="button" data-bind="click: $root.assist.updateAcls" rel="tooltip" data-placement="bottom" data-loading-text="${ _('Saving...') }" data-original-title="${ _('Save') }" class="btn">
                          <i class="fa fa-save"></i>
                        </button>
                      </div>
                    </div>
                    <div class="loading-popover center" data-bind="visible: $root.assist.isLoadingAcls()"><i class="fa fa-spinner fa-spin fa-5x"></i></div>
                  </p>
                </div>
              </div>

            </div>
          </div>
        </div>
      </div>

      <div id="listDataset" class="section card card-small hide">
        <div class="alert alert-info"><h3>${ _('Existing datasets') }</h3></div>
      </div>
    </div>

  </div>
</div>

<script type="text/html" id="tree-template">
<!-- ko if: nodes != null -->
<ul class="tree" data-bind="foreach: nodes">
    <li>
        <span data-bind="
            template: { name: 'node-name-template', data: $data }"></span>
        <div data-bind="template: { name: 'folder-template', data: $data }, visible: isExpanded"></div>
    </li>    
</ul>
<!-- /ko -->
</script>

<script type="text/html" id="folder-template">
<!-- ko if: nodes != null -->
    <ul data-bind="foreach: nodes">
        <li>
            <div data-bind="template: { name: 'node-template', data: $data }"></div>
        </li>
    ## Should fetch more files here if needed
    <!-- ko if: $index() == 14 -->
      <li>
        <a href="javascript: void(0)">         
          <i class="fa fa-plus"></i> 
        </a>
      </li>
    <!-- /ko -->        
    </ul>
<!-- /ko -->
</script>

<script type="text/html" id="node-template">
    <!-- ko if: nodes != null -->
    <span data-bind="
        template: { name: 'node-name-template', data: $data },
        css: { 'pointer-icon': nodes().length > 0 }"></span>
    <!-- /ko -->

    <!-- ko if: nodes().length !== 0 -->
        <div data-bind="template: { name: 'folder-template', data: $data }, visible: isExpanded"></div>
    <!-- /ko -->
</script>

<script type="text/html" id="node-name-template">
    <div class="node-row" data-bind="click: $root.assist.setPath,style: { backgroundColor: aclBit() ? '#F6F6F6': '' }, css:{selected: $root.assist.path() == path()}">
      <i data-bind="
      css: {
          'fa': true,
          'fa-folder-open-o': isDir() && nodes().length > 0,
          'fa-folder-o': isDir() && nodes().length == 0,
          'fa-file-o': !isDir()
      }
      " style="color: #999"></i>
      <strong><a style="display: inline-block" data-bind="text:name"></a></strong>
      <div class="pull-right" style="margin-right: 20px" data-bind="visible: aclBit()">
        <i class="fa fa-lock"></i>
      </div>
    </div>
</script>


<script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout.mapping-2.3.2.js" type="text/javascript" charset="utf-8"></script>

<script src="/security/static/js/hdfs.ko.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript">

  ko.bindingHandlers.tooltip = {
    init: function (element, valueAccessor) {
      var local = ko.utils.unwrapObservable(valueAccessor()),
          options = {};

      ko.utils.extend(options, local);

      $(element).tooltip(options);

      ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
        $(element).tooltip("destroy");
      });
    }
  };

  function movePopover() {
    var _selectedRow = $(".node-row.selected");
    if (_selectedRow.length > 0) {
      $("#aclPopover")
          .css("left", _selectedRow.offset().left + _selectedRow.width())
          .css("top", _selectedRow.offset().top - $("#aclPopover").outerHeight() / 2 + _selectedRow.outerHeight() / 2)
          .show();
    }
  }

  var viewModel;

  $(document).ready(function () {
    viewModel = new HdfsViewModel(${ initial | n,unicode });
    ko.applyBindings(viewModel);

    viewModel.init();

    $(document).on("click", ".node-row", function () {
      movePopover();
    });

    $(document).on("loaded.acls", movePopover);
  });
</script>



${ commonfooter(messages) | n,unicode }
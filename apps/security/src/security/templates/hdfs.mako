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
  #hdfsTree ul {
    list-style-type: none;
    padding: 0;
  }

  .tree {
    margin-left: 0 !important;
    padding-left: 0 !important;
    min-height: 300px;
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
    background-color: #F6F6F6;
  }

  .loading-popover {
    width: 200px;
    height: 120px;
    line-height: 120px;
    color: #999999;
  }

  .path-container {
    background-color: #FFF;
    padding-top: 8px;
  }

  .acl-panel {
    border-left: 1px solid #CCC;
    padding-top: 6px;
    padding-left: 6px;
    min-height: 300px;
  }

</style>

<script type="text/html" id="acl-display">
  <div data-bind="visible: status() != 'deleted'">
    <span data-bind="text: printAcl($data)"></span>
  </div>
</script>


<script type="text/html" id="acl-edition">
  <div data-bind="visible: status() != 'deleted'">
    <input type="radio" value="group" data-bind="checked: type, attr: { name: 'aclType' + $index() + (isDefault() ? 'isDefault' : 'notDefault') }"/> ${ _('group') }
    <input type="radio" value="user" data-bind="checked: type, attr: { name: 'aclType' + $index() + (isDefault() ? 'isDefault' : 'notDefault') }"/> ${ _('user') }
    <input type="radio" value="mask" data-bind="checked: type, attr: { name: 'aclType' + $index() + (isDefault() ? 'isDefault' : 'notDefault') }"/> ${ _('mask') }
    <input type="radio" value="other" data-bind="checked: type, attr: { name: 'aclType' + $index() + (isDefault() ? 'isDefault' : 'notDefault') }"/> ${ _('other') }

    <input type="text" data-bind="value: name, valueUpdate:'afterkeydown'" class="input-small" placeholder="${ _('name...') }"/>
    ##<select data-bind="options: $root.availableHadoopGroups, value: name, optionsCaption: '', valueUpdate:'afterkeydown'" class="input-small" placeholder="${ _('name...') }"/>

    <input type="checkbox" title="r, ${ _('Read') }" data-bind="checked: r"/>
    <input type="checkbox" title="w, ${ _('Write') }" data-bind="checked: w"/>
    <input type="checkbox" title="x, ${ _('Execute') }" data-bind="checked: x"/>
    <a href="javascript: void(0)">
      <i class="fa fa-minus" data-bind="click: $root.assist.removeAcl"></i>
    </a>
  </div>
</script>

<div class="container-fluid">
  <div class="row-fluid">
    <div class="span12">
      <div class="card card-small">
        <h1 class="card-heading simple">
          <div class="pull-right">
            <i class="fa fa-eye"></i>
            <div class="btn-group pull-right">              
              <a class="btn dropdown-toggle" data-toggle="dropdown" href="#">
                View as...
                <span class="caret"></span>
              </a>
              <ul class="dropdown-menu">
                <li><a href="#"><strong>USERS</strong></a></li>
                <li><a href="#">My user</a></li>
                <!-- ko foreach: availableHadoopUsers -->
                  <li><a href="#" data-bind="text: $data"></a></li>
                <!-- /ko -->
                <li class="divider"></li>
                <li><a href="#"><strong>GROUPS</strong></a></li>
                <li><a href="#">My group</a></li>
                <!-- ko foreach: availableHadoopGroups -->
                  <li><a href="#" data-bind="text: $data"></a></li>
                <!-- /ko -->
              </ul>
            </div>
          </div>
          ${ _('HDFS ACLs') }
        </h1>
        <div class="card-body">
          <div class="row-fluid">
            <div class="span8">
              <div class="path-container">
                <div class="input-append span12">
                  <input id="path" type="text" style="width: 96%" data-bind="value: $root.assist.path, valueUpdate: 'afterkeydown'" autocomplete="off"/>
                  <a data-bind="attr: { href: '/filebrowser/view' + $root.assist.path() }" target="_blank" title="${ _('Open in File Browser') }" class="btn btn-inverse"><i class="fa fa-external-link"></i></a>
                </div>
              </div>
              <div class="path-container-ghost hide"></div>
              <div id="hdfsTree" data-bind="template: { name: 'tree-template', data: $root.assist.treeData }"></div>
            </div>
            <div class="span4">
              <div class="acl-panel" data-bind="visible: !$root.assist.isLoadingAcls()">
                  <a href="javascript: void(0)" data-bind="click: function() { $root.assist.showAclsAsText(! $root.assist.showAclsAsText()); }">
                    <i class="fa" data-bind="css: { 'fa-header': $root.assist.showAclsAsText(), 'fa-pencil': ! $root.assist.showAclsAsText() }">
                    </i>
                    <span data-bind="visible: $root.assist.showAclsAsText()">${ _('Text view') }</span>
                    <span data-bind="visible: ! $root.assist.showAclsAsText()">${ _('Edit') }</span>
                  </a>

                  <br/>

                  <span data-bind="visible: $root.assist.showAclsAsText">
                    <br/>
                    # file: <span data-bind="text: $root.assist.path"></span>
                    <br/>
                    # owner: <span data-bind="text: $root.assist.owner"></span>
                    <br/>
                    # group: <span data-bind="text: $root.assist.group"></span>
                    <br/>                  
                    <div data-bind="foreach: $root.assist.regularAcls">                    
                      <div data-bind="template: {name: 'acl-display'}"></div>
                    </div>
                    <div data-bind="foreach: $root.assist.defaultAcls">
                      <div data-bind="template: {name: 'acl-display'}"></div>
                    </div>
                  </span>

                  <span data-bind="visible: ! $root.assist.showAclsAsText()">
                    <dl>
                      <dt><a data-bind="attr: { href: '/filebrowser/view' + $root.assist.path() }, text: $root.assist.path()" target="_blank" title="${ _('Open in File Browser') }"></a></dt>
                      <dt>
                        <i class="fa fa-user" style="color: #999999" title="${_('User')}"></i> <span title="${_('User')}" data-bind="text: $root.assist.owner"></span>
                        <i class="fa fa-users" style="color: #999999" title="${_('Group')}"></i> <span title="${_('Group')}" data-bind="text: $root.assist.group"></span>
                      </dt>
                    </dl>

                    ${ _('ACLs') }
                    <br/>
                    <div data-bind="foreach: $root.assist.regularAcls">
                      <div data-bind="template: {name: 'acl-edition'}"></div>
                    </div>

                    <a href="javascript: void(0)" data-bind="click: $root.assist.addAcl"><i class="fa fa-plus"></i></a>

                    <br/>

                    ${ _('Default ACLs') }
                    <div data-bind="foreach: $root.assist.defaultAcls">
                      <div data-bind="template: {name: 'acl-edition'}"></div>
                    </div>
                    <a href="javascript: void(0)" data-bind="click: $root.assist.addDefaultAcl"><i class="fa fa-plus"></i></a>

                    <div data-bind="visible: $root.assist.changedAcls().length">
                      <button type="button" data-bind="click: $root.assist.updateAcls" rel="tooltip" data-placement="bottom" data-loading-text="${ _('Saving...') }" data-original-title="${ _('Save') }" class="btn">
                        <i class="fa fa-save"></i>
                      </button>
                    </div>
                  </span>
                </div>
                <div class="loading-popover center" data-bind="visible: $root.assist.isLoadingAcls()"><i class="fa fa-spinner fa-spin fa-5x"></i></div>


            </div>
          </div>
          </div>
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
    <div class="node-row" data-bind="click: $root.assist.setPath, event : { dblclick: $root.assist.openPath },  style: { border: aclBit() ? '1px dashed #CCCCCC': '' }, css:{selected: $root.assist.path() == path()}">
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
<script src="/static/js/jquery.hdfsautocomplete.js" type="text/javascript" charset="utf-8"></script>

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

  var viewModel;

  $(document).ready(function () {
    viewModel = new HdfsViewModel(${ initial | n,unicode });
    ko.applyBindings(viewModel);

    viewModel.init();

    //$(document).on("loaded.acls", movePopover);

    $("#path").jHueHdfsAutocomplete({
      home: viewModel.assist.path(),
      onEnter: function (el) {
        viewModel.assist.path(el.val());
      },
      smartTooltip: "${_('Did you know? You can use the tab key or CTRL + Space to autocomplete file and folder names')}"
    });


    $(".path-container").data("originalWidth", $(".path-container").width());
    $(".acl-panel").data("originalWidth", $(".acl-panel").width());
    $(".path-container-ghost").height($(".path-container").outerHeight());
    resetPathContainer();

    $(window).scroll(function () {
      if ($(window).scrollTop() > 85) {
        $(".path-container").width($(".path-container").data("originalWidth"));
        $(".acl-panel").width($(".acl-panel").data("originalWidth"));
        $(".path-container").css("position", "fixed").css("top", "70px");
        $(".acl-panel").css("position", "fixed").css("top", "70px");
        $(".path-container-ghost").removeClass("hide");
      }
      else {
        resetPathContainer();
      }
    });

    function resetPathContainer() {
      $(".path-container").attr("style", "min-width: 190px");
      $(".acl-panel").attr("style", "min-width: 190px");
      $(".path-container").data("originalWidth", $(".path-container").width());
      $(".acl-panel").data("originalWidth", $(".acl-panel").width());
      $(".path-container-ghost").addClass("hide");
    }
  });
</script>



${ commonfooter(messages) | n,unicode }
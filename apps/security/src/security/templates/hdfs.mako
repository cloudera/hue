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
<%namespace name="tree" file="common_tree.mako" />

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

  .node-row a.striked {
    text-decoration: line-through;
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
    border-left: 1px solid #e5e5e5;
    padding-top: 6px;
    padding-left: 12px;
    min-height: 300px;
  }

  #path {
    height: 34px;
    font-size: 14px;
  }

  .path-container .btn-inverse {
    height: 34px;
    width: 34px;
    font-size: 14px;
    line-height: 34px;
  }

  .fake-pre {
    display: block;
    padding: 9.5px;
    margin: 0 0 10px;
    font-size: 12px;
    line-height: 20px;
    word-break: break-all;
    word-wrap: break-word;
    font-family: Monaco, Menlo, Consolas, "Courier New", monospace;
    background-color: #f5f5f5;
    border: 1px solid #ccc;
    border: 1px solid rgba(0, 0, 0, 0.15);
    -webkit-border-radius: 2px;
    -moz-border-radius: 2px;
    border-radius: 2px;
  }

  .tree-toolbar {
    padding: 3px;
    border-bottom: 1px solid #e5e5e5;
  }

  .tree-toolbar .fa {
    margin-left: 5px;
  }

  .tree-toolbar .fa-sitemap {
    color: #cccccc;
    margin-right: 6px;
  }

  .tree-toolbar input {
    margin-bottom: 0;
    height: 25px;
    min-height: 25px;
  }

  .tree-toolbar .pull-right {
    margin-top: -3px;
  }

  .inline-block {
    display: inline-block;
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
    <input type="text" data-bind="value: name, valueUpdate: 'afterkeydown', css: { 'user-list': type() == 'user', 'group-list': type() == 'group' }" class="input-small" placeholder="${ _('name...') }"/>
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
          ${ _('HDFS ACLs') }
        </h1>
        <div class="card-body">
          <div class="row-fluid">
            <div class="span8">
              <div class="path-container">
                <div class="input-append span12">
                  <input id="path" type="text" data-bind="value: $root.assist.path, valueUpdate: 'afterkeydown'" autocomplete="off" />
                  <a data-bind="attr: { href: '/filebrowser/view' + $root.assist.path() }" target="_blank" title="${ _('Open in File Browser') }" class="btn btn-inverse">
                    <i class="fa fa-external-link"></i>
                  </a>
                </div>
                <div class="clearfix"></div>
                <div class="tree-toolbar">
                  <div class="pull-right">

                    <div class="dropdown inline-block" style="margin-right: 6px">
                      <a class="dropdown-toggle" data-toggle="dropdown" href="#"><i class="fa fa-eye-slash" data-bind="visible: $root.assist.isDiffMode"></i><i class="fa fa-eye" data-bind="visible: ! $root.assist.isDiffMode()"></i> <span data-bind="visible: $root.assist.isDiffMode">${ _('Show non accessible files for') }</span><span data-bind="visible: ! $root.assist.isDiffMode()">${ _('Impersonate the user') }</span></a>
                      <ul class="dropdown-menu">
                        <li data-bind="click: function() { $root.assist.isDiffMode(true); }"><a tabindex="-1" href="#">${ _('Show non accessible files for') } <strong data-bind="text: $root.doAs"></strong></a></li>
                        <li data-bind="click: function() { $root.assist.isDiffMode(false); }"><a tabindex="-1" href="#">${ _('Impersonate the user') } <strong data-bind="text: $root.doAs"></strong></a></li>
                      </ul>
                    </div>
                    <select class="user-list" data-bind="options: $root.selectableHadoopUsers, select2: { placeholder: '${ _("Select a user") }', update: $root.doAs}" style="width: 120px"></select>
                    <i class="fa fa-group" title="List of groups in popover for this user?"></i>
                  </div>
                  <i class="fa fa-sitemap fa-rotate-270"></i>
                  <a href="javascript: void(0)" data-bind="click: $root.assist.collapseTree">
                    <i class="fa fa-compress"></i> ${_('Collapse')}
                  </a>
                  <a href="javascript: void(0)" data-bind="click: $root.assist.expandTree">
                    <i class="fa fa-expand"></i> ${_('Expand')}
                  </a>
                  <a href="javascript: void(0)" data-bind="click: $root.assist.refreshTree">
                    <i class="fa fa-refresh"></i>  ${_('Refresh')}
                  </a>
                </div>
              </div>
              <div class="path-container-ghost hide"></div>

              ${ tree.render(id='hdfsTree', data='$root.assist.treeData', afterRender='$root.assist.afterRender') }
            </div>
            <div class="span4">
              <div class="acl-panel" data-bind="visible: ! $root.assist.isLoadingAcls()">

                  <ul class="nav nav-tabs">
                    <li data-bind="css: {'active': ! $root.assist.showAclsAsText()}"><a href="javascript: void(0)" data-bind="click: function() { $root.assist.showAclsAsText(false); }"><i class="fa fa-pencil"></i> ${ _('Edit') }</a></li>
                    <li data-bind="css: {'active': $root.assist.showAclsAsText()}"><a href="javascript: void(0)" data-bind="click: function() { $root.assist.showAclsAsText(true); }"><i class="fa fa-header"></i> ${ _('View as text') }</a></li>
                  </ul>

                  <span class="fake-pre" data-bind="visible: $root.assist.showAclsAsText">
                    # file: <span data-bind="text: $root.assist.path"></span><br/>
                    # owner: <span data-bind="text: $root.assist.owner"></span><br/>
                    # group: <span data-bind="text: $root.assist.group"></span><br/>
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

                    <h4>${ _('ACLs') }</h4>
                    <div data-bind="foreach: $root.assist.regularAcls">
                      <div data-bind="template: {name: 'acl-edition'}"></div>
                    </div>

                    <a href="javascript: void(0)" data-bind="click: $root.assist.addAcl"><i class="fa fa-plus"></i></a>

                    <br/>

                    <h4>${ _('Default ACLs') }</h4>
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

<%def name="treeIcons()">
  'fa-folder-open-o': isDir() && nodes().length > 0,
  'fa-folder-o': isDir() && nodes().length == 0,
  'fa-file-o': !isDir()
</%def>

<%def name="aclBitPullRight()">
  <div class="pull-right muted"  data-bind="visible: striked">
    This is not visible by current user <span data-bind="text: $root.doAs"></span>
  </div>
  
  <div class="pull-right" style="margin-right: 20px" data-bind="visible: aclBit()">
    <i class="fa fa-lock"></i>
  </div>
</%def>


${ tree.import_templates(itemClick='$root.assist.setPath', itemDblClick='$root.assist.openPath', itemSelected='$root.assist.path() == path()', iconModifier=treeIcons, styleModifier='aclBit', styleModifierPullRight=aclBitPullRight, anchorProperty='path', showMore='$root.assist.loadMore') }


<script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout.mapping-2.3.2.js" type="text/javascript" charset="utf-8"></script>

<script src="/security/static/js/hdfs.ko.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/js/jquery.hdfsautocomplete.js" type="text/javascript" charset="utf-8"></script>

<link rel="stylesheet" href="/static/ext/select2/select2.css">
<script src="/static/ext/select2/select2.min.js" type="text/javascript" charset="utf-8"></script>


<script type="text/javascript">

  ko.bindingHandlers.select2 = {
    init: function(element, valueAccessor, allBindingsAccessor, vm) {
      var options = ko.toJS(valueAccessor()) || {};
      $(element).select2(options).on("change", function(e){
        if (typeof e.val != "undefined"){
          vm.doAs(e.val);
        }
      });
    },
    update: function(element, valueAccessor, allBindingsAccessor, vm) {
      $(element).select2("val", vm.doAs());
    }
};

  var INITIAL = ${ initial | n,unicode };
  var viewModel = new HdfsViewModel(INITIAL);
  ko.applyBindings(viewModel);

  $(document).ready(function () {

    $(document).on("loaded.users", function(){
      $(".user-list").select2("val", viewModel.doAs());
    });


    var _initialPath = "/";
    if (window.location.hash != "") {
      _initialPath = window.location.hash.substr(1);
    }
    viewModel.init(_initialPath);

    //$(document).on("loaded.acls", movePopover);

    $("#path").jHueHdfsAutocomplete({
      home: viewModel.assist.path(),
      onPathChange: function (path) {
        viewModel.assist.path(path);
      },
      onEnter: function (el) {
        viewModel.assist.path(el.val());
      },
      smartTooltip: "${_('Did you know? You can use the tab key or CTRL + Space to autocomplete file and folder names')}"
    });

    function resizePathInput () {
      $("#path").width($(".tree-toolbar").width() - 64);
    }

    resizePathInput();

    $(document).on("rendered.tree", function() {
      var _path = viewModel.assist.path();
      if (_path[_path.length-1] == "/"){
        _path = _path.substr(0, _path.length - 1);
      }
      if ($("a.anchor[href^='"+_path+"']").length > 0){
        $("html, body").animate({
          scrollTop: ($("a.anchor[href^='"+_path+"']").position().top - 140)+"px"
        });
      }
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

    var _resizeTimeout = -1;
    $(window).resize(function(){
      window.clearTimeout(_resizeTimeout);
      _resizeTimeout = window.setTimeout(resizePathInput, 100);
    });

    window.onpopstate = function() {
      viewModel.assist.path(window.location.hash.substr(1));
    };

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

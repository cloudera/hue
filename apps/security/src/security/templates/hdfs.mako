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


<script type="text/html" id="acl-display">
  <div data-bind="visible: status() != 'deleted'">
    <span data-bind="text: printAcl($data)"></span>
  </div>
</script>


<script type="text/html" id="acl-edition">
  <div data-bind="visible: status() != 'deleted'" class="acl-block">
    <a href="javascript: void(0)" class="pull-right" style="margin-right: 4px">
      <i class="fa fa-times" data-bind="click: $root.assist.removeAcl"></i>
    </a>
    <label class="radio inline-block">
      <input type="radio" value="group" data-bind="checked: type, attr: { name: 'aclType' + $index() + (isDefault() ? 'isDefault' : 'notDefault') }"/> ${ _('group') }
    </label>
    <label class="radio inline-block">
      <input type="radio" value="user" data-bind="checked: type, attr: { name: 'aclType' + $index() + (isDefault() ? 'isDefault' : 'notDefault') }"/> ${ _('user') }
    </label>
    <label class="radio inline-block">
      <input type="radio" value="mask" data-bind="checked: type, attr: { name: 'aclType' + $index() + (isDefault() ? 'isDefault' : 'notDefault') }"/> ${ _('mask') }
    </label>
    <label class="radio inline-block">
      <input type="radio" value="other" data-bind="checked: type, attr: { name: 'aclType' + $index() + (isDefault() ? 'isDefault' : 'notDefault') }"/> ${ _('other') }
    </label>
    <div style="margin-left: 6px">
      <div data-bind="visible: type() == 'user'">
        <select class="user-list-acl" data-bind="options: $root.selectableHadoopUsers, select2: { placeholder: '${ _("Select a user") }', update: name, type: 'user'}" style="width: 200px"></select>
      </div>

      <div data-bind="visible: type() == 'group'">
        <select class="group-list-acl" data-bind="options: $root.selectableHadoopGroups, select2: { placeholder: '${ _("Select a group") }', update: name, type: 'group'}" style="width: 200px"></select>
      </div>

      <input type="text" data-bind="value: name, valueUpdate: 'afterkeydown', visible: type() == 'mask' || type() == 'other'" placeholder="${ _('name ...') }" style="width: 180px; margin-bottom: 0px; height: 26px; min-height: 26px"/>
    </div>

    <br/>
    <label class="checkbox inline-block">
      <input type="checkbox" data-bind="checked: r"/>
      ${ _('Read') } <span class="muted">(r)</span>
    </label>
    <label class="checkbox inline-block">
      <input type="checkbox" data-bind="checked: w"/>
      ${ _('Write') } <span class="muted">(w)</span>
    </label>
    <label class="checkbox inline-block">
      <input type="checkbox" data-bind="checked: x"/>
      ${ _('Execute') } <span class="muted">(x)</span>
    </label>
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
                  <input id="path" class="path" type="text" data-bind="value: $root.assist.path, valueUpdate: 'afterkeydown'" autocomplete="off" />
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
                        <li data-bind="visible: ! $root.assist.isDiffMode(), click: function() { $root.assist.isDiffMode(true); }"><a tabindex="-1" href="#">${ _('Show non accessible files') }</a></li>
                        <li data-bind="visible: $root.assist.isDiffMode(), click: function() { $root.assist.isDiffMode(false); }"><a tabindex="-1" href="#">${ _('Impersonate the user') }</a></li>
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

              ${ tree.render(id='expandableTree', data='$root.assist.treeData', afterRender='$root.assist.afterRender') }
            </div>
            <div class="span4">
              <div class="acl-panel" data-bind="visible: ! $root.assist.isLoadingAcls()">

                  <div data-bind="visible: $root.assist.changedAcls().length" class="pull-right" style="margin-right: 6px; margin-top: 4px">
                    <button type="button" data-bind="click: $root.assist.updateAcls" class="btn disable-feedback">
                      <i class="fa fa-save"></i> ${ _('Save') }
                    </button>
                  </div>

                  <ul class="nav nav-tabs">
                    <li data-bind="css: {'active': ! $root.assist.showAclsAsText()}"><a href="javascript: void(0)" data-bind="click: function() { $root.assist.showAclsAsText(false); }"><i class="fa fa-pencil"></i> ${ _('Edit') }</a></li>
                    <li data-bind="css: {'active': $root.assist.showAclsAsText()}"><a href="javascript: void(0)" data-bind="click: function() { $root.assist.showAclsAsText(true); }"><i class="fa fa-header"></i> ${ _('View as text') }</a></li>
                  </ul>

                  <div class="acl-panel-content">
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
                      <h4>${ _('Path') }</h4>
                      <a class="force-word-break" data-bind="attr: { href: '/filebrowser/view' + $root.assist.path() }, text: $root.assist.path()" target="_blank" title="${ _('Open in File Browser') }" rel="tooltip"></a>

                      <h4>${ _('User/Group') }</h4>
                      <i class="fa fa-user" style="color: #999999" title="${_('User')}"></i> <span title="${_('User')}" data-bind="text: $root.assist.owner"></span>&nbsp;
                      <i class="fa fa-users" style="color: #999999" title="${_('Group')}"></i> <span title="${_('Group')}" data-bind="text: $root.assist.group"></span>

                      <h4>${ _('ACLs') }</h4>
                      <div data-bind="foreach: $root.assist.regularAcls">
                        <div data-bind="template: {name: 'acl-edition'}"></div>
                      </div>

                      <div class="acl-block pointer add-acl" data-bind="click: $root.assist.addAcl">
                        <i class="fa fa-plus"></i>
                      </div>

                      <h4>${ _('Default ACLs') }</h4>
                      <div data-bind="foreach: $root.assist.defaultAcls">
                        <div data-bind="template: {name: 'acl-edition'}"></div>
                      </div>

                      <div class="acl-block pointer add-acl" data-bind="click: $root.assist.addDefaultAcl">
                        <i class="fa fa-plus"></i>
                      </div>
                    </span>
                  </div>
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
  'fa-folder-open-o': isDir() && nodes().length > 0 && !aclBit(),
  'fa-folder-open': isDir() && nodes().length > 0 && aclBit(),
  'fa-folder-o': isDir() && nodes().length == 0 && !aclBit(),
  'fa-folder': isDir() && nodes().length == 0 && aclBit(),
  'fa-file-o': !isDir() && !aclBit(),
  'fa-file': !isDir() && aclBit(),
  'striked': striked()
</%def>

<%def name="aclBitPullRight()">
  <div class="pull-right rwx" data-bind="style: { color: aclBit() ? '#338bb8': '#999999'}">
    <span data-bind="text: rwx"></span>
  </div>
  <div class="pull-right">
    <i class="fa fa-lock" data-bind="visible: aclBit()" style="color: #338bb8"></i>
  </div>
</%def>


${ tree.import_templates(itemClick='$root.assist.setPath', iconClick='$root.assist.togglePath', itemSelected='$root.assist.path() == path()', iconModifier=treeIcons, styleModifier='aclBit', styleModifierPullRight=aclBitPullRight, anchorProperty='path', showMore='$root.assist.loadMore', strikedProperty='striked') }


<script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout.mapping-2.3.2.js" type="text/javascript" charset="utf-8"></script>

<script src="/security/static/js/common.ko.js" type="text/javascript" charset="utf-8"></script>
<script src="/security/static/js/hdfs.ko.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/js/jquery.hdfsautocomplete.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript">

  var viewModel = new HdfsViewModel(${ initial | n,unicode });
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

    function resizeComponents () {
      $("#path").width($(".tree-toolbar").width() - 64);
      $("#expandableTree").height($(window).height() - 260);
      $(".acl-panel-content").height($(window).height() - 260);
    }

    resizeComponents();

    $(document).on("rendered.tree", function() {
      var _path = viewModel.assist.path();
      if (_path[_path.length-1] == "/"){
        _path = _path.substr(0, _path.length - 1);
      }
      if ($("a.anchor[href^='"+_path+"']").length > 0){
        $("#expandableTree").animate({
          scrollTop: ($("a.anchor[href^='"+_path+"']:first").position().top + $("#expandableTree").scrollTop() - $("#expandableTree").position().top - 4)+"px"
        });
      }
    });

    var _resizeTimeout = -1;
    $(window).resize(function(){
      window.clearTimeout(_resizeTimeout);
      _resizeTimeout = window.setTimeout(resizeComponents, 100);
    });

    window.onpopstate = function() {
      viewModel.assist.path(window.location.hash.substr(1));
    };

  });
</script>


${ commonfooter(messages) | n,unicode }

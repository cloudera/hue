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


<div class="container-fluid">
  <div class="row-fluid">
    <div class="span2">
      <div class="sidebar-nav">
        <ul class="nav nav-list">
          <li class="nav-header">${ _('ACLs') }</li>
          <li class="active"><a href="#edits"><i class="fa fa-pencil"></i> ${ _('Edit') }</a></li>
          <li><a href="#view"><i class="fa fa-eye"></i> ${ _('View') }</a></li>
        </ul>
      </div>
    </div>
    <div class="span10">
      <div id="edit" class="section card card-small">
        <h1 class="card-heading simple">${ _('Edit ACLs') }</h1>        
        <div class="card-body">          
          <div>
            <input type="text" class="input-xxlarge" data-bind="value: $root.assist.path, valueUpdate:'afterkeydown'"/>
            <a class="btn btn-inverse" style="margin-left:10px", data-bind="attr: { href: '/filebrowser/view' + $root.assist.path() }" target="_blank" title="${ _('Open in File Browser') }">
              <i class="fa fa-external-link"></i>                
            </a>
          </div>
          <div>
            <div class="span8">
              <div data-bind="foreach: $root.assist.files">
                <div data-bind="text: $data"></div>
              </div>
            </div>
            <div class="span4">
              <span data-bind="text: $root.assist.owner"></span>
              <span data-bind="text: $root.assist.group"></span>
              <div data-bind="foreach: $root.assist.acls">
                ## Xeditable for edition?
                <div>
                  <input type="radio" value="group" data-bind="checked: type, attr: { name: 'aclType' + $index()} "/> ${ _('Group') }
                  <input type="radio" value="user" data-bind="checked: type, attr: { name: 'aclType' + $index()}"/> ${ _('User') }
                  <input type="text" data-bind="value: name" class="input-small" placeholder="${ _('name...') }"/>
                  <input type="checkbox" data-bind="checked: r() != '-'"/>
                  <input type="checkbox" data-bind="checked: w() != '-'"/>
                  <input type="checkbox" data-bind="checked: x() != '-'"/>
                  <a href="javascript: void(0)"
                    <i class="fa fa-minus" data-bind="click: $root.assist.removeAcl"></i>
                  </a>
                </div>
              </div>
              <a href="javascript: void(0)" data-bind="click: $root.assist.addAcl">
                <i class="fa fa-plus"></i>
              </a>
              <div data-bind="visible: $root.assist.changed().length">
                <button type="button" rel="tooltip" data-placement="bottom" data-original-title="${ _('Cancel') }" class="btn">
                  <i class="fa fa-times"></i>
                </button>
                <button type="button" data-bind="click: $root.assist.updateAcls" rel="tooltip" data-placement="bottom" data-loading-text="${ _('Saving...') }" data-original-title="${ _('Save') }" class="btn">
                  <i class="fa fa-save"></i>
                </button>
              <div>              
            </div>
          </div>
        </div>
      </div>

      <div id="listDataset" class="section card card-small hide">
        <div class="alert alert-info"><h3>${ _('Existing datasets') }</h3></div>
      </div>

      <div id="listHistory" class="section  card card-small hide">
        <div class="alert alert-info"><h3>${ _('History') }</h3></div>          
      </div>
    </div>

  </div>
</div>


<script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout.mapping-2.3.2.js" type="text/javascript" charset="utf-8"></script>

<script src="/security/static/js/hdfs.ko.js" type="text/javascript" charset="utf-8"></script>


<script type="text/javascript" charset="utf-8">
  var viewModel;
  
  $(document).ready(function () {
    viewModel = new HdfsViewModel(${ assist | n,unicode });
    ko.applyBindings(viewModel);
  });
</script>

${ commonfooter(messages) | n,unicode }

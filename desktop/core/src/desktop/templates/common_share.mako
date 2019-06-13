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
from django.utils.translation import ugettext as _
%>

<script type="text/html" id="user-search-autocomp-item">
  <a>
    <div>
      <i data-bind="css: icon"></i>
      <span data-bind="html: label"></span>
    </div>
  </a>
</script>

<script type="text/html" id="user-search-autocomp-no-match">
   <div class="no-match">
     <span>${ _('No match found') }</span>
   </div>
 </script>


<div id="documentShareModal" class="modal hide fade">
  <!-- ko if: selectedDoc() -->
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
    <h2 class="modal-title">${_('Sharing settings')}</h2>
  </div>
  <div class="modal-body" style="overflow: visible; height: 240px">
    <div class="row-fluid" style="max-height: 114px">
      <div class="span6">
        <h4 class="muted" style="margin-top:0px">${_('Read')}</h4>
        <div data-bind="visible: (selectedDoc().perms.read.users.length == 0 && selectedDoc().perms.read.groups.length == 0)">${_('The document is not shared for read.')}</div>
        <ul class="unstyled airy" data-bind="foreach: selectedDoc().perms.read.users">
          <li><span class="badge badge-info badge-left"><i class="fa fa-user"></i> <span data-bind="text: prettifyUsernameById(id), attr:{'data-id': id}"></span></span><span class="badge badge-right trash-share" data-bind="click: removeUserReadShare"> <i class="fa fa-times"></i></span></li>
        </ul>
        <ul class="unstyled airy" data-bind="foreach: selectedDoc().perms.read.groups">
          <li><span class="badge badge-info badge-left"><i class="fa fa-users"></i> ${ _('Group') } <span data-bind="text: name"></span></span><span class="badge badge-right trash-share" data-bind="click: removeGroupReadShare"> <i class="fa fa-times"></i></span></li>
        </ul>
      </div>
      <div class="span6">
        <h4 class="muted" style="margin-top:0px">${_('Read and Modify')}</h4>
        <div data-bind="visible: (selectedDoc().perms.write.users.length == 0 && selectedDoc().perms.write.groups.length == 0)">${_('The document is not shared for read and modify.')}</div>
        <ul class="unstyled airy" data-bind="foreach: selectedDoc().perms.write.users">
          <li><span class="badge badge-info badge-left"><i class="fa fa-user"></i> <span data-bind="text: prettifyUsernameById(id), attr:{'data-id': id}"></span></span><span class="badge badge-right trash-share" data-bind="click: removeUserWriteShare"> <i class="fa fa-times"></i></span></li>
        </ul>
        <ul class="unstyled airy" data-bind="foreach: selectedDoc().perms.write.groups">
          <li><span class="badge badge-info badge-left"><i class="fa fa-users"></i> ${ _('Group') } <span data-bind="text: name"></span></span><span class="badge badge-right trash-share" data-bind="click: removeGroupWriteShare"> <i class="fa fa-times"></i></span></li>
        </ul>
      </div>
    </div>
    <div class="clearfix"></div>
    <div style="margin-top: 20px">
      <div class="input-append">
        <div id="menu" style="font-size: 14px;"></div>
        <input id="userSearchAutocomp" placeholder="${_('Type a username or a group name')}" type="text" data-bind="autocomplete: { source: source, itemTemplate: 'user-search-autocomp-item', noMatchTemplate: 'user-search-autocomp-no-match',valueObservable: searchInput, showSpinner: true, classPrefix: 'hue-', onEnter: handleTypeaheadSelection, appendTo: $('#menu') }, clearable: { value: searchInput }, textInput: searchInput" class="ui-autocomplete-input" autocomplete="off" style="width: 460px">
        <div class="btn-group">
          <a id="documentShareAddBtn" class="btn"><span data-bind="text: selectedPermLabel"></span></a>
          <a id="documentShareCaret" class="btn dropdown-toggle" data-toggle="dropdown">
            <span class="caret"></span>
          </a>
          <ul class="dropdown-menu pull-right">
            <li><a data-bind="click: changeDocumentSharePerm.bind(null, 'read')" href="javascript:void(0)">${ _('Read') }</a></li>
            <li><a data-bind="click: changeDocumentSharePerm.bind(null, 'write')" href="javascript:void(0)">${ _('Read and Modify') }</a></li>
          </ul>
        </div>
      </div>
    </div>
  </div>
  <div class="modal-footer">
    <a href="#" data-dismiss="modal" class="btn btn-primary disable-feedback disable-enter">${_('Done')}</a>
  </div>
  <!-- /ko -->
</div>

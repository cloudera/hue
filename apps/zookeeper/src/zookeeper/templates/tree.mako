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
  from desktop.auth.backend import is_admin
%>

<%namespace name="shared" file="shared_components.mako" />

${ commonheader("ZooKeeper Browser > Tree > %s > %s" % (cluster['nice_name'], path), app_name, user, request) | n,unicode }
${ shared.menubar() }

<%
  _split = path.split("/");
  _breadcrumbs = [
    [_("Clusters"), url('zookeeper:index')],
    [cluster['nice_name'].lower(), url('zookeeper:view', id=cluster['id'])],
  ]
  for idx, p in enumerate(_split):
    if p != "":
      _breadcrumbs.append([p, url('zookeeper:tree', id=cluster['id'], path= "/".join(_split[:idx+1]))]);
%>


${ shared.header(_breadcrumbs, clusters, False) }
<div class="row-fluid" style="margin-top: 20px">
  <div class="span3">
    <div class="sidebar-nav">
      <ul class="nav nav-list" style="border: 0">
        <li class="nav-header">${ _('Znodes') }</li>
        % for child in children:
        <li>
          <a href="${url('zookeeper:tree', id=cluster['id'], path=("%s/%s" % (path, child)).replace('//', '/'))}">${child}</a>
        </li>
        % endfor
        % if len(children) == 0:
          <li class="white">${ _('No children available') }</li>
        % endif
        % if is_admin(user):
        <li class="white">
          <button class="btn" onclick="location.href='${url('zookeeper:create', id=cluster['id'], path=path)}'">
            <i class="fa fa-plus-circle"></i> ${ _('Add') }
          </button>
          <button id="removeBtn" class="btn btn-danger disable-feedback" data-msg="${_('Are you sure you want to delete %s?' % path)}" data-url="${url('zookeeper:delete', id=cluster['id'], path=path)}">
            <i class="fa fa-times-circle"></i> ${ _('Remove current ZNode') }
          </button>
        </li>
        % endif
      </ul>
    </div>
  </div>
  <div class="span9">
    <ul class="nav nav-tabs">
      %if znode.get('dataLength', 0) != 0:
        <li class="active"><a href="#text" data-toggle="tab">${ _('Text') }</a></li>
        <li><a href="#base64" data-toggle="tab">${ _('Base64') } (${ znode.get('dataLength', 0) })</a></li>        
        <li><a href="#stats" data-toggle="tab">${ _('Stats') }</a></li>
      %else:
        <li><a href="#stats" data-toggle="tab">${ _('Stats') }</a></li>
      %endif
    </ul>
    <div class="tab-content">
      %if znode.get('dataLength', 0) != 0:
      <div class="tab-pane active" id="text">
        <textarea id="textareaText" rows="25" readonly="readonly"></textarea>
        % if is_admin(user):
        <a href="${url('zookeeper:edit_as_text', id=cluster['id'], path=path)}" class="btn"><i class="fa fa-pencil"></i> ${_('Edit as Text')}</a>
        % endif
      </div>      
      <div class="tab-pane" id="base64">
        <textarea id="textarea64" rows="25" readonly="readonly">${znode.get('data64', '')}</textarea>
        % if is_admin(user):
        <a href="${url('zookeeper:edit_as_base64', id=cluster['id'], path=path)}" class="btn"><i class="fa fa-pencil"></i> ${_('Edit as Base64')}</a>
        % endif
      </div>
      <div class="tab-pane" id="stats">
      %else:
      <div class="tab-pane active" id="stats">
      %endif
        <table class="table">
          <thead>
          <tr>
            <th width="20%">Key</th>
            <th>Value</th>
          </tr>
          </thead>
          % for key in ('pzxid', 'ctime', 'aversion', 'mzxid', 'ephemeralOwner', 'version', 'mtime', 'cversion', 'czxid'):
          <tr>
            <td>${key}</td>
            <td>${znode[key]}</td>
          </tr>
          % endfor
        </table>
      </div>
    </div>
  </div>
</div>


${ shared.footer() }

<div id="removeModal" class="modal hide fade">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
    <h2 class="modal-title">${ _('Delete Znode?') }</h2>
  </div>
  <div class="modal-body">
    <p class="question"></p>
  </div>
  <div class="modal-footer">
    <a href="#" class="btn" data-dismiss="modal">${ _('Cancel') }</a>
    <a id="removeBtnModal" href="#" class="btn btn-danger disable-feedback">${ _('Yes, delete it!') }</a>
  </div>
</div>

<script type="text/javascript">
  $(document).ready(function () {
  %if znode.get('dataLength', 0) != 0:
    var txt = Base64.decode($("#textarea64").val());
    $("#textareaText").val(txt);
  %endif
    $("#removeModal").modal({
      show: false
    });
    $("#removeBtn").on("click", function(){
      var _url = $(this).data("url");
      var _msg = $(this).data("msg");
      $("#removeModal").find(".question").text(_msg);
      $("#removeBtnModal").data("url", _url);
      $("#removeModal").modal("show");
    });
    $("#removeBtnModal").on("click", function(){
      $(this).addClass("disabled");
      $.post($(this).data("url"), function(data){
        location.href = data.redirect;
      })
    })
  });
</script>


${ commonfooter(request, messages) | n,unicode }

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

<script src="${ static('desktop/ext/js/bootstrap-fileupload.js') }" type="text/javascript" charset="utf-8"></script>
<link rel="stylesheet" href="${ static('desktop/ext/css/bootstrap-fileupload.css') }">

<div id="export-documents" class="modal hide">
  <form method="POST" action="/desktop/api2/doc/export" style="display: inline">
    ${ csrf_token(request) | n,unicode }
    <input type="hidden" name="documents"/>
  </form>
</div>

<div id="import-documents" class="modal hide fade fileupload-modal">
  <div class="modal-header">
    <a href="#" class="close" data-dismiss="modal" data-clear="fileupload">&times;</a>
    <h3>${_('Import Hue documents')}</h3>
  </div>
  <form method="POST" action="/desktop/api2/doc/import" style="display: inline" enctype="multipart/form-data">
    <div class="modal-body form-inline">
      <div class="pull-right">
        <a href="#" class="btn" data-dismiss="modal" data-clear="fileupload">${ _('Cancel') }</a>
        <input type="submit" class="btn btn-danger" value="${ _('Import') }"/>
      </div>
      <div class="fileupload fileupload-new" data-provides="fileupload">
        <span class="btn btn-file" style="line-height: 29px">
          <span class="fileupload-new">${ _('Select json file') }</span>
          <span class="fileupload-exists">${ _('Change') }</span>
          <input type="file" name="documents" accept=".json" />
        </span>
        &nbsp;&nbsp;<span class="fileupload-preview"></span>
          <a href="#" class="fileupload-exists" data-clear="fileupload"><i class="fa fa-times"></i></a>
      </div>
      ${ csrf_token(request) | n,unicode }
      <input type="hidden" name="redirect" value="${ request.get_full_path() }"/>
    </div>
  </form>
</div>

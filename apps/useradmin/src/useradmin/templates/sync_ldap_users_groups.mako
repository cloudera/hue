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

<%def name="render_field(field)">
  %if not field.is_hidden:
    <% group_class = len(field.errors) and "error" or "" %>
    <div class="control-group ${group_class}" style="margin-bottom: 10px;">
      <label class="control-label" for="id_${field.html_name}">${field.label}</label>
      <div class="controls">
        ${unicode(field) | n}
        % if len(field.errors):
          <span class="help-inline">${unicode(field.errors) | n}</span>
        % endif
        &nbsp;
      </div>
    </div>
  %endif
</%def>

<form action="${path}" method="POST" class="form form-horizontal">
  ${ csrf_token(request) | n,unicode }
  % if is_embeddable:
    <input type="hidden" value="true" name="is_embeddable" />
  % endif
  <div class="modal-header left">
    <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
    <h2 class="modal-title">${_('Sync LDAP users and groups')}</h2>
  </div>
  <div class="modal-body">
    <div class="alert alert-info left">
      <p>${_("This will not import any users or groups that don't already exist in Hue. Only users and groups imported from LDAP can be synced.")}</p>
      <p>${_("All user information and group memberships will be updated based on the LDAP server's current state.")}</p>
    </div>
    % for field in form:
      ${render_field(field)}
    % endfor
  </div>
  <div class="modal-footer">
    <a href="#" class="btn" data-dismiss="modal">${_('Cancel')}</a>
    <input type="submit" class="btn btn-primary disable-feedback" value="${_('Sync')}"/>
  </div>
</form>
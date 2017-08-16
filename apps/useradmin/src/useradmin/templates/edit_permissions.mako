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
import urllib

from desktop.views import commonheader, commonfooter
from django.utils.translation import ugettext as _
%>

<%namespace name="layout" file="layout.mako" />

%if not is_embeddable:
${ commonheader(_('Hue Permissions'), "useradmin", user, request) | n,unicode }
%endif

${layout.menubar(section='permissions')}

<%def name="render_field(field)">
  %if not field.is_hidden:
    <% group_class = len(field.errors) and "error" or "" %>
    <div class="control-group ${group_class}">
      <label class="control-label" for="id_${field.html_name}">${field.label}</label>
    <div class="controls">
    ${unicode(field) | n}
    % if len(field.errors):
        <span class="help-inline">${unicode(field.errors) | n}</span>
    % endif
    </div>
    </div>
  %endif
</%def>

<div id="editPermissionsComponents" class="useradmin container-fluid">
  <div class="card card-small">
    <h1 class="card-heading simple">${_('Hue Permissions - Edit app: %(app)s') % dict(app=app)}</h1>
    <br/>

    <form id="editForm" action="${urllib.quote(action)}" method="POST" class="form form-horizontal">
      ${ csrf_token(request) | n,unicode }
      <fieldset>
          % for field in form:
          ${render_field(field)}
          % endfor
      </fieldset>
      <br/>

      <div class="form-actions">
        <input type="submit" class="btn btn-primary disable-feedback" value="${_('Update permission')}"/>
        % if is_embeddable:
          <input type="hidden" value="true" name="is_embeddable" />
        % endif
        <a href="/useradmin/permissions" class="btn">${_('Cancel')}</a>
      </div>
    </form>
  </div>
</div>

<script type="text/javascript">
  $(document).ready(function () {
    var $editPermissionsComponents = $('#editPermissionsComponents');
    $("#id_groups").jHueSelector({
      selectAllLabel: "${_('Select all')}",
      searchPlaceholder: "${_('Search')}",
      noChoicesFound: "${_('No groups found.')}",
      width: 600,
      height: 500
    });
    % if is_embeddable:
    $editPermissionsComponents.find('#editForm').ajaxForm({
      dataType:  'json',
      success: function(data) {
        if (data && data.status == -1) {
          renderUseradminErrors(data.errors);
        }
        else if (data && data.url) {
          huePubSub.publish('open.link', data.url);
          $.jHueNotify.info("${ _('Permission information updated correctly') }");
        }
      }
    });
    % endif
  });
</script>

${layout.commons()}

%if not is_embeddable:
${ commonfooter(request, messages) | n,unicode }
%endif

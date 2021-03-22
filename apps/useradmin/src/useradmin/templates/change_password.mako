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
import sys
from desktop.views import commonheader, commonfooter
if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _
from useradmin.hue_password_policy import is_password_policy_enabled, get_password_hint
%>

<%namespace name="layout" file="layout.mako" />

% if not is_embeddable:
  ${ commonheader(_('Hue Users'), "useradmin", user, request) | n,unicode }
% endif

${ layout.menubar(section='users') }

<div id="editUserComponents"  class="useradmin container-fluid">
  <div class="card card-small">
    <h1 class="card-heading simple">${_('Hue Users - Change password: %(username)s') % dict(username=username)}</h1>

    <br/>
    <form id="editForm" method="POST" class="form form-horizontal" autocomplete="off">
    ${ csrf_token(request) | n,unicode }
    <div id="properties" class="section">
      <ul class="nav nav-tabs" style="margin-bottom: 0">
        <li class="active">
          <a href="#step1" class="step">${ _('Credentials') }
          % if not username:
            ${ _('(required)') }
          % endif
          </a>
        </li>
      </ul>

    <div class="steps">
      <div id="step1" class="stepDetails">
        ${layout.render_field(form["username"], extra_attrs={'validate':'true'})}
        % if "password1" in form.fields:
          % if username and "password_old" in form.fields:
            ${layout.render_field(form["password_old"], extra_attrs=username is None and {'validate':'true'} or {})}
          % endif
          ${layout.render_field(form["password1"], extra_attrs=username is None and {'validate':'true'} or {})}
          % if is_password_policy_enabled():
            <div class="password_rule" style="margin-left:180px; width:500px;">
              <p>${get_password_hint()}</p>
            </div>
          % endif
          ${layout.render_field(form["password2"], extra_attrs=username is None and {'validate':'true'} or {})}
        % endif
      </div>
      <div class="form-actions">
        <input type="submit" class="btn btn-primary" value="${_('Change password')}"/>
      </div>
    </form>
  </div>
</div>
<script type="text/javascript">
$(document).ready(function(){
 var currentStep = "step1";
  var $editUserComponents = $('#editUserComponents');
  % if is_embeddable:
  $editUserComponents.find('#editForm').attr('action', window.location.pathname.substr((window.HUE_BASE_URL + '/hue').length).replace(/\/$/, ''));
  $editUserComponents.find('#editForm').ajaxForm({
    dataType:  'json',
    success: function(data) {
      if (data && data.status == -1) {
        renderUseradminErrors(data.errors);
      }
      else if (data && data.url) {
        huePubSub.publish('open.link', data.url);
        $.jHueNotify.info("${ _('User information updated correctly') }");
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

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
from desktop.lib.django_util import extract_field_data
import urllib
from django.utils.translation import ugettext as _
%>

<%namespace name="layout" file="layout.mako" />

${ commonheader(_('Hue Users'), "useradmin", user) | n,unicode }
${ layout.menubar(section='users') }


<div class="container-fluid">
  <div class="card card-small">
    <h1 class="card-heading simple">${_('Hue Users - Add/Sync LDAP user')}</h1>
    <br/>

  <form id="editForm" method="POST" class="form form-horizontal" autocomplete="off">
    ${ csrf_token(request) | n,unicode }
    <fieldset>
          % for field in form.fields:
                  % if form[field].is_hidden:
                      ${ form[field] }
                  % else:
                      ${ layout.render_field(form[field]) }
                  % endif
          % endfor
    </fieldset>
    <br/>
    <div class="form-actions">
      % if username:
        <input type="submit" class="btn btn-primary" value="${_('Update user')}"/>
      % else:
          <input type="submit" class="btn btn-primary" value="${_('Add/Sync user')}"/>
      % endif
      <a href="${url('useradmin.views.list_users')}" class="btn">${_('Cancel')}</a>
    </div>
  </form>
</div>
  </div>

<script type="text/javascript" charset="utf-8">
  $(document).ready(function(){
    $("#id_groups").jHueSelector({
            selectAllLabel: "${_('Select all')}",
            searchPlaceholder: "${_('Search')}",
            noChoicesFound: "${_('No groups found.')} <a href='${url('useradmin.views.edit_group')}'>${_('Create a new group now')} &raquo;</a>",
            width:618,
            height:240
        });
  });
</script>

${ commonfooter(messages) | n,unicode }

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

${ commonheader(_('Hue Users'), "useradmin", user, "100px") | n,unicode }

% if user.is_superuser:
  ${layout.menubar(section='users', _=_)}
% endif

<div class="container-fluid">
    % if username:
        <h1>${_('Hue Users - Edit user: %(username)s') % dict(username=username)}</h1>
    % else:
        <h1>${_('Hue Users - Create user')}</h1>
    % endif

    <br/>

    <form id="editForm" method="POST" class="form form-horizontal" autocomplete="off">
        <fieldset>
            <h3>${ _('Information') }</h3>

            ${layout.render_field(form["username"])}

            % if "password1" in form.fields:
            <div class="row">
                <div class="span5">
                ${layout.render_field(form["password1"])}
                </div>
                <div class="span4">
                ${layout.render_field(form["password2"])}
                </div>
            </div>
            % endif

            <h3>${ _('Optional') }</h3>

            % if "first_name" in form.fields:
            <div class="row">
                <div class="span5">
                ${layout.render_field(form["first_name"])}
                </div>
                <div class="span4">
                ${layout.render_field(form["last_name"])}
                </div>
            </div>
            % endif

            ${layout.render_field(form["email"])}
            % if user.is_superuser:
              ${layout.render_field(form["groups"])}
              ${layout.render_field(form["is_active"])}
            % endif
            ${layout.render_field(form["ensure_home_directory"])}
            % if user.is_superuser:
              ${'is_superuser' in form.fields and layout.render_field(form["is_superuser"])}
            % endif
        </fieldset>
        <br/>
        <div class="form-actions">
            % if username:
                <input type="submit" class="btn btn-primary" value="${_('Update user')}"/>
            % else:
                <input type="submit" class="btn btn-primary" value="${_('Add user')}"/>
            % endif
            <a class="btn" onclick="history.back()">${ _('Cancel') }</a>
        </div>
    </form>
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

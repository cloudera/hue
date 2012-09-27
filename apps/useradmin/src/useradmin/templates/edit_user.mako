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

${commonheader(_('Hue Users'), "useradmin", user, "100px")}
${layout.menubar(section='users', _=_)}

<%def name="render_field(field)">
  %if not field.is_hidden:
    <% group_class = len(field.errors) and "error" or "" %>
    <div class="control-group ${group_class}">
      <label class="control-label" for="id_${field.html_name}">${_(field.label)}</label>
      <div class="controls">
		${unicode(field) | n}
        % if len(field.errors):
          <span class="help-inline">${unicode(field.errors) | n}</span>
        % endif
      </div>
    </div>
  %endif
</%def>

<div class="container-fluid">
	% if username:
		<h1>${_('Hue Users - Edit user: %(username)s') % dict(username=username)}</h1>
	% else:
		% if ldap:
			<h1>${_('Hue Users - Add/Sync LDAP user')}</h1>
		% else:
			<h1>${_('Hue Users - Create user')}</h1>
		% endif
	% endif

    <br/>

	<form id="editForm" action="${urllib.quote(action)}" method="POST" class="form form-horizontal">
		<fieldset>
			% for field in form:
                %if field.name == "username" and "password1" in form.fields:
                    ${render_field(form["username"])}
                    <div class="row">
                        <div class="span5">
                        ${render_field(form["password1"])}
                        </div>
                        <div class="span4">
                        ${render_field(form["password2"])}
                        </div>
                    </div>
                %elif field.name == "first_name":
                    <div class="row">
                        <div class="span5">
                        ${render_field(form["first_name"])}
                        </div>
                        <div class="span4">
                        ${render_field(form["last_name"])}
                        </div>
                    </div>
                %elif field.name == "last_name" or field.name == "password1" or field.name == "password2":
                    ## skip rendering
                %else:
				    ${render_field(field)}
                %endif
			% endfor
		</fieldset>
		<br/>
		<div class="form-actions">
			% if username:
				<input type="submit" class="btn btn-primary" value="${_('Update user')}"/>
			% else:
				% if ldap:
					<input type="submit" class="btn btn-primary" value="${_('Add/Sync user')}"/>
				% else:
					<input type="submit" class="btn btn-primary" value="${_('Add user')}"/>
				% endif
			% endif
			<a href="/useradmin/users" class="btn">${_('Cancel')}</a>
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
${commonfooter(messages)}

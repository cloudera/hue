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
<%namespace name="edit" file="editor_components.mako" />
<%namespace name="comps" file="fb_components.mako" />
${comps.header('Change Owner / Group: ' + path.split('/')[-1])}
<%! from desktop.lib.django_util import extract_field_data %>

## Puts together a selection list with an "other" field as well.
<%def name="selection(name, choices, current_value, other_key)">
    <% seen = False %>
    % if len(choices) == 0:
      <select name="${name}" class="ccs-hidden">
    % else:
      <select name="${name}">
    % endif
    % for choice in choices:
      % if choice == current_value:
        <% seen = True %>
        <option selected>${choice}</option>
      % else:
        <option>${choice}</option>
      % endif
    % endfor
    % if seen or not current_value:
      <option value="__other__">Other</option>
    % else:
      <option value="__other__" selected="true">Other</option>
    % endif

    </select>
    % if seen or not current_value:
      <input name="${other_key}" class="ccs-hidden">
    % else:
      <input name="${other_key}" value="${current_value}">
    % endif
</%def>


<div class="prompt_popup">
<form action="/filebrowser/chown?next=${next|u}" method="POST" enctype="multipart/form-data">
  <h4 class="ccs-hidden">Change Owner / Group: ${path}</h4>
  <dl class="fb-side-by-side">
    ${edit.render_field(form["path"], hidden=True)}

    <dt><label>User</label></dt>
    <dd class="ccs-select-with-other">${ selection("user", form.all_users, extract_field_data(form["user"]), "user_other") }</dd>
    <dt><label>Group</label></dt>
    <dd class="ccs-select-with-other">${ selection("group", form.all_groups, extract_field_data(form["group"]), "group_other") }</dd>
  </dl>
  <input class="ccs-hidden" type="submit" value="Submit" />
</form>
</div>

<div class="ccs-hidden">Go back to where you were: <a href="${next|u}">${next}</a>.</div>


${comps.footer()}

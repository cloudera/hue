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
${comps.header('Change Permissions: ' + path.split('/')[-1])}

<div class="prompt_popup">
<form action="/filebrowser/chmod?next=${next|u}" method="POST" enctype="multipart/form-data">
  <h4 class="ccs-hidden">Change Permissions: ${path}</h4>
  <dl>
    ${edit.render_field(form["path"], hidden=True)}
    <table class="fb-chmod">
      <thead>
        <tr>
          <th class="fb-empty"></th>
          <th>User</th>
          <th>Group</th>
          <th>Other</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td class="fb-label">Read</td>
          <td>${edit.render_field(form["user_read"], notitle=True)}</td>
          <td>${edit.render_field(form["group_read"], notitle=True)}</td>
          <td>${edit.render_field(form["other_read"], notitle=True)}</td>
        </tr>
        <tr>
          <td class="fb-label">Write</td>
          <td>${edit.render_field(form["user_write"], notitle=True)}</td>
          <td>${edit.render_field(form["group_write"], notitle=True)}</td>
          <td>${edit.render_field(form["other_write"], notitle=True)}</td>
        </tr>
        <tr>
          <td class="fb-label">Execute</td>
          <td>${edit.render_field(form["user_execute"], notitle=True)}</td>
          <td>${edit.render_field(form["group_execute"], notitle=True)}</td>
          <td>${edit.render_field(form["other_execute"], notitle=True)}</td>
        </tr>
      </tbody>
    </table>
  </dl>
  <input class="ccs-hidden" type="submit" value="Submit" />
</form>
</div>

<div class="ccs-hidden">Go back to where you were: <a href="${next|u}">${next}</a>.</div>


${comps.footer()}
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
<%namespace name="wrappers" file="header_footer.mako" />

${wrappers.head()}
    <div id="useradmin_userlist" class="view">
      <table data-filters="HtmlTable" class="sortable" cellpadding="0" cellspacing="0">
        <thead>
          <tr>
            <th>Username</th>
            <th>First Name</th>
            <th>Last Name</th>
            <th>E-mail</th>
            <th colspan="2">Last Login</th>
          </tr>
        </head>
        <tbody>
        % for user in users:
          <tr>
            <td>${user.username}</td>
            <td>${user.first_name}</td>
            <td>${user.last_name}</td>
            <td>${user.email}</td>
            <td>
              <span class="jframe-hidden">
                ${int(user.last_login.strftime("%s"))}
              </span>
              ${user.last_login.strftime('%c')}
            </td>
            <td>
              <a title="Edit ${user.username}" class="edit frame_tip" href="${ url('useradmin.views.edit_user', username=user.username) }">Edit</a>
              <a title="Delete ${user.username}" class="delete frame_tip confirm_and_post" alt="Are you sure you want to delete ${user.username}?" href="${ url('useradmin.views.delete_user', username=user.username) }">Delete</a>
            </td>
          </tr>
        % endfor
        </tbody>
      </table>
      <a class="useradmin_add_user" href="${ url('useradmin.views.edit_user') }">Add User</a>
    </div>
${wrappers.foot()}

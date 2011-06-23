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
import datetime
from django.template.defaultfilters import urlencode, stringformat, filesizeformat, date, time
from desktop.lib.django_util import reverse_with_get
%>


<%def name="list_table_chooser(files, path, current_request_path)">
  ${_table(files, path, current_request_path, 'chooser')}
</%def>
<%def name="list_table_browser(files, path, current_request_path, cwd_set=True)">
  ${_table(files, path, current_request_path, 'view', cwd_set)}
</%def>
<%def name="_table(files, path, current_request_path, view, cwd_set=False)">
  <%
  # Sortable takes a while for big lists; skip it in that case.
  if len(files) < 100:
    optional_sortable = "sortable"
  else:
    optional_sortable = ""
  # FitText doesn't scale well with many rows, so we disable it for
  # larger views.
  if len(files) < 30:
    optional_fit_text = 'data-filters="FitText"'
  else:
    optional_fit_text = ''
  %>
  <table data-filters="HtmlTable" class="fb-file-list selectable ${optional_sortable}" cellpadding="0" cellspacing="0">
    <thead>
      <tr>
        % if cwd_set:
          <th>Name</th>
        % else:
          <th>Path</th>
        % endif
        <th>Size</th>
        <th>User</th>
        <th>Group</th>
        <th>Permissions</th>
        <th colspan="2">Date</th>
      </tr>
    </thead>
    <tbody>
      % for file in files:
        <%
          cls = ''
          if (file_filter == 'dir' and file['type'] != 'dir') or (file_filter != 'dir' and file['type'] == 'dir'):
            if (file_filter != 'any'):
              cls = ' not-selectable'

          if cwd_set:
            display_name = file['name']
          else:
            display_name = file['path']
          endif
        %>
  ## Since path is in unicode, Django and Mako handle url encoding and
  ## iri encoding correctly for us.
        <% path = file['path'] %>
        <tr class="jframe-no_select fb-item-row ${cls}"
         data-filters="ContextMenu"
         data-context-menu-actions="[{'events':['contextmenu','click:relay(.fb-item-options)'],'menu':'ul.context-menu'}]"
         data-dblclick-delegate= "{'dblclick_loads':'a.fb-item'}" data-filedata="{'path':'${path}','type':'${file['type']|u}'}">
          <td class="fb-name">
            <div class="fb-name-container">
              % if "dir" == file['type']:
                <a ${optional_fit_text | n} class="fb-item fb-dir jframe_ignore" href="${url('filebrowser.views.'+view, path=urlencode(path))}?file_filter=${file_filter}">${display_name}</a>
              % else:
                <a ${optional_fit_text | n} class="fb-item fb-file jframe_ignore" target="FileViewer" href="${url('filebrowser.views.'+view, path=urlencode(path))}?file_filter=${file_filter}">${display_name}</a>
              % endif
              % if ".." != file['name']:
                <ul class="fb-item-actions context-menu">
                  % if "dir" == file['type']:
                    <li class="fb-rmdir-container"><a class="fb-rmdir confirm_unencode_and_post" alt="Are you sure you want to delete this directory and its contents?" href="${reverse_with_get('filebrowser.views.rmdir', get=dict(path=path,next=current_request_path))}">Delete</a></li>
                    <li class="fb-rmtree-container"><a class="fb-rmtree confirm_unencode_and_post fb-default-rm" alt="Are you sure you want to delete ${display_name} and its contents?" href="${reverse_with_get('filebrowser.views.rmtree', get=dict(path=path,next=current_request_path))}"">Delete</a></li>
                  % else:
                    <li><a class="fb-viewfile" href="${url('filebrowser.views.view', path=urlencode(path))}" target="FileViewer">View File</a></li>
                    <li><a class="fb-editfile" href="${url('filebrowser.views.edit', path=urlencode(path))}" target="FileEditor">Edit File</a></li>
                    <li><a class="fb-downloadfile" href="${url('filebrowser.views.download', path=urlencode(path))}" target="_blank">Download File</a></li>
                    <li class="fb-rm-container"><a class="fb-rm fb-default-rm confirm_unencode_and_post" alt="Are you sure you want to delete ${display_name}?" href="${reverse_with_get('filebrowser.views.remove', get=dict(path=path, next=current_request_path))}">Delete</a></li>
                  % endif
                  <li class="fb-rename-container"><a class="fb-rename" href="${reverse_with_get('filebrowser.views.rename',get=dict(src_path=path,next=current_request_path))}">Rename</a></li>
                  <li class="fb-chown-container"><a class="fb-chown" href="${reverse_with_get('filebrowser.views.chown',get=dict(path=path,user=file['stats']['user'],group=file['stats']['group'],next=current_request_path))}">Change Owner / Group</a></li>
                  <li class="fb-chmod-container"><a class="fb-chmod" href="${reverse_with_get('filebrowser.views.chmod',get=dict(path=path,mode=stringformat(file['stats']['mode'], "o"),next=current_request_path))}">Change Permissions</a></li>
                  <%
                    if "dir" == file['type']:
                      cls = "fb-move-dir"
                    else:
                      cls = "fb-move-file"
                  %>
                  <li><a class="fb-move ${cls}" href="${reverse_with_get('filebrowser.views.move',get=dict(src_path=path,mode=stringformat(file['stats']['mode'], "o"),next=current_request_path))}">Move</a></li>
              </ul>
              % endif
            </div>
          </td>
          <%
            if "dir" == file['type']:
              sortValue = 0;
            else:
              sortValue = file['stats']['size']
          %>
          <td class="fb-filesize">
            % if "dir" == file['type']:
              <span data-sort-numeric="${sortValue}">~</span>
            % else:
              <span data-sort-numeric="${sortValue}">${file['stats']['size']|filesizeformat}</span>
            % endif
          </td>
          <td class="fb-user">${file['stats']['user']}</td>
          <td class="fb-group">${file['stats']['group']}</td>
          <td class="fb-perm">${file['rwx']}</td>
          <td class="fb-date"><span data-sort-numeric="${file['stats']['mtime']}">${date(datetime.datetime.fromtimestamp(file['stats']['mtime']))} ${time(datetime.datetime.fromtimestamp(file['stats']['mtime']))}</span></td>
          <td class="fb-option-links">
            % if ".." != file['name']:
              <a class="fb-item-options">options</a>
            % endif
          </td>
        </tr>
      % endfor
    </tbody>
  </table>
</%def>

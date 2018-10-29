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

<html>
  <head><title>${ _('Save File As...') }</title></head>
  <body>
    % if form.errors:
      <div class="alert_popup">
        % for field in form:
          % if len(field.errors):
               ${unicode(field.errors) | n}
          % endif
        % endfor
      </div>
    % endif
    <div class="saveAsPrompt_popup">
      <form method="post" action="${url('filebrowser_views_save_file')}">
          ${ csrf_token(request) | n,unicode }
          ${ _('Enter the location where you would like to save the file.') }
          ${edit.render_field(form["path"], notitle=True)}
          <div>${edit.render_field(form["contents"], hidden=True)}</div>
          <div>${edit.render_field(form["encoding"], hidden=True)}</div>
          <input type="submit" name="save" value="save"/>
      </form>
    </div>
  </body>
</html>

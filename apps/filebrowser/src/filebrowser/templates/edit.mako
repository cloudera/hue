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
<%!
  from django.template.defaultfilters import urlencode
  from filebrowser.views import truncate
%>
<%
  path_enc = urlencode(path)
  dirname_enc = urlencode(dirname)
%>
<%namespace name="wrappers" file="header_footer.mako" />
${wrappers.head('${truncate(filename)} :: File Editor', show_upload=False, show_new_directory=False, show_side_bar=False)}


<h1>${truncate(path, 91)}</h1>
<div class="well" >
    <form class="form-stacked" method="post" action="${url('filebrowser.views.save_file')}">
    <div class="toolbar"><a class="btn" href="${url('filebrowser.views.view', path=dirname_enc)}" target="FileBrowser">View Location</a></div>



% if form.errors:
  <div class="alert-message">
    % for field in form:
      % if len(field.errors):
       ${unicode(field.errors) | n}
      % endif
    % endfor
  </div>
% endif
        ${edit.render_field(form["path"], hidden=True, notitle=True)}
        ${edit.render_field(form["encoding"], hidden=True, notitle=True)}
        
        <div style="width: 100%; height: 100%;">${edit.render_field(form["contents"], tag="textarea", notitle=True, attrs=dict(
          style="width:100%; height:400px;")) | n}</div>
        <input class="btn primary" type="submit" name="save" value="save">
        <input class="btn" type="submit" name="save" value="saveAs">

    </form>
</div>

${wrappers.foot()}


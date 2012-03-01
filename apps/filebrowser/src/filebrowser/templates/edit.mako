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
${wrappers.head(truncate(filename)+' :: File Viewer', show_upload=False, show_new_directory=False, show_side_bar=False)}


<h1>${truncate(path, 91)}</h1>
<div class="well" >
    <form class="form-stacked" method="post" action="${url('filebrowser.views.save_file')}">
    <div class="toolbar">
		<a class="btn" href="${url('filebrowser.views.view', path=dirname_enc)}">View Location</a>
	</div>
	<br/>

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
        <input class="btn primary" type="submit" name="save" value="Save">
        <a id="saveAsBtn" class="btn">Save As</a>
    </form>
</div>


<div id="saveAsModal" class="modal hide fade">
    <form id="saveAsForm" action="${url('filebrowser.views.save_file')}" method="POST" class="form-stacked form-padding-fix">
    <div class="modal-header">
        <a href="#" class="close">&times;</a>
        <h3>Save As</h3>
    </div>
    <div class="modal-body">
		${edit.render_field(form["path"], notitle=True, klass="xlarge")}
		<span class="help-block">Please enter the location where you'd like to save the file.</span>
    </div>
    <div class="modal-footer">
        <div id="saveAsNameRequiredAlert" class="alert-message error hide" style="position: absolute; left: 10;">
            <p><strong>Sorry, name is required.</strong>
        </div>
		${edit.render_field(form["contents"], hidden=True)}
		${edit.render_field(form["encoding"], hidden=True)}
        <input type="submit" value="Save" class="btn primary" />
        <a id="cancelSaveAsBtn" class="btn">Cancel</a>
    </div>
    </form>
</div>

<script type="text/javascript" charset="utf-8">
	$(document).ready(function(){
		$("#saveAsBtn").click(function(){
			$("#saveAsModal").modal({
				backdrop: "static",
				keyboard: true,
				show: true
			})
		});
		
		
		$("#cancelSaveAsBtn").click(function(){
			$("#saveAsModal").modal("hide");
		});
		
		$("#saveAsForm").submit(function() {
			if ($.trim($("#saveAsForm").find("input[name='path']").val()) == ""){
				$("#saveAsForm").find("input[name='path']").addClass("fieldError");
				$("#saveAsNameRequiredAlert").show();
				return false;
			}
			return true;
		});
		
		$("#saveAsForm").find("input[name='path']").focus(function(){
			$(this).removeClass("fieldError");
			$("#saveAsNameRequiredAlert").hide();
		});
	});
</script>

${wrappers.foot()}


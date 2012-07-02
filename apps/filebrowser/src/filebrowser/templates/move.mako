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
from django.utils.translation import ugettext as _
%>
<%namespace name="edit" file="editor_components.mako" />

<form id="moveForm" action="/filebrowser/move?next=${next|u}" method="POST" enctype="multipart/form-data" class="form-inline form-padding-fix">
    <div class="modal-header">
        <a href="#" class="close" data-dismiss="modal">&times;</a>
        <h3>${_('Move:')} ${src_path}</h3>
    </div>
    <div class="modal-body">
        <div style="padding-left: 15px;">
        ${edit.render_field(form["src_path"], hidden=True)}
        ${edit.render_field(form["dest_path"], notitle=True, klass="input-xlarge pathChooser")}
        </div>
        <br/>
        <div id="fileChooserModal" class="smallModal well hide">
            <a href="#" class="close" data-dismiss="modal">&times;</a>
        </div>
    </div>
    <div class="modal-footer">
        <div id="moveNameRequiredAlert" class="hide" style="position: absolute; left: 10;">
            <span class="label label-important">${_('Sorry, name is required.')}</span>
        </div>
        <input class="btn primary" type="submit" value="${_('Submit')}"/>
        <a class="btn" onclick="$('#moveModal').modal('hide');">${_('Cancel')}</a>
    </div>
</form>

<script type="text/javascript" charset="utf-8">
    $(".pathChooser").click(function(){
        var self = this;
        $("#fileChooserModal").jHueFileChooser({
            initialPath: $(self).val(),
            onFileChoose: function(filePath) {
                $(self).val(filePath);
            },
            onFolderChange: function(folderPath){
                $(self).val(folderPath);
            },
            createFolder: false,
            uploadFile: false
        });
        $("#fileChooserModal").slideDown();
    });
</script>

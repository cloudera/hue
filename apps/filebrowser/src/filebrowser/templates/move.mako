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

<form action="/filebrowser/move?next=${next|u}" method="POST" enctype="multipart/form-data"
      class="form-stacked form-padding-fix">
    <div class="modal-header">
        <a href="#" class="close">&times;</a>
        <h3>Move: ${src_path}</h3>
    </div>
    <div class="change-owner-modal-body clearfix" >
        <div style="padding-left: 15px;">
        ${edit.render_field(form["src_path"], hidden=True)}
        ${edit.render_field(form["dest_path"], notitle=True)}
        </div>
    </div>
    <div class="modal-footer">
        <input class="btn primary" type="submit" value="Submit"/>
        <a class="btn" onclick="$('#move-modal').modal('hide');">Cancel</a>
    </div>
</form>
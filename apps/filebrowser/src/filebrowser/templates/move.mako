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
<%namespace name="wrappers" file="header_footer.mako" />
${wrappers.head('Move: ' + src_path.split('/')[-1])}

<h1>Move: ${src_path}</h1>
<form action="/filebrowser/move?next=${next|u}" method="POST" enctype="multipart/form-data" class="form-stacked">

  <div class="well">
    ${edit.render_field(form["src_path"], hidden=True)}
    ${edit.render_field(form["dest_path"], notitle=True)}
    <div>
        <input class="btn primary" type="submit" value="Submit" />
        <a class="btn" href="${next|u}">Cancel</a>
    </div>
  </div>

</form>
${wrappers.foot()}
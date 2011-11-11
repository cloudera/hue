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
${wrappers.head('Upload Files', 'upload', show_new_directory=False)}

<h1>Upload Files</h1>
    <form action="/filebrowser/upload?next=${next|u}" method="POST" enctype="multipart/form-data" class="form-stacked">

      <div class="well">
        ${edit.render_field(form["hdfs_file"], render_default=True, notitle=True)}
        ${edit.render_field(form["dest"], hidden=True)}
        <div>
            <input class="btn primary" type="submit" value="Submit" />
            <a class="btn" href="/filebrowser/view${next}">Cancel</a>
        </div>
      </div>
    </form>
    <!--<span class="alert-message block-message info">Go back to where you were: <a href="/filebrowser/view${next}">${next}</a>.</span>-->

${wrappers.foot()}

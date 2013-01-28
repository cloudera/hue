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

<%namespace name="dir" file="listdir_components.mako" />

<div class="fb-actions" data-filters="ArtButtonBar">
  <a class="fb-upload" data-filters="ArtButton" data-icon-styles="{'width': 16, 'height' : 16}" href="${url('filebrowser.views.upload_file')}?dest=${path|u}&next=${current_request_path|u}">Upload Files</a>
  <a class="fb-mkdir" data-filters="ArtButton" data-icon-styles="{'width': 16, 'height': 16}" href="${url('filebrowser.views.mkdir')}?path=${path|u}&next=${current_request_path|u}">New Directory</a>
</div>

${dir.list_table_chooser(files, path_enc, current_request_path)}

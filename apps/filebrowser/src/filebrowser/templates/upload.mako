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


<script src="/static/ext/js/fileuploader.js" type="text/javascript" charset="utf-8"></script>
<link rel="stylesheet" href="/static/ext/css/fileuploader.css" type="text/css" media="screen" title="no title" charset="utf-8" />


<div class="well">
    <form action="/filebrowser/upload?next=${next|u}" method="POST" enctype="multipart/form-data" class="form-stacked">
        <h1>${_('Upload Files')}</h1>
        <div id="file-uploader">
            <noscript>
                <p>${_('Please enable JavaScript to use the file uploader.')}</p>
                <!-- or put a simple form for upload here -->
            </noscript>
        </div>
    </form>
</div>

<!--<span class="alert-message block-message info">Go back to where you were: <a href="/filebrowser/view${next}">${next}</a>.</span>-->

<script>
    function createUploader(){
        var uploader = new qq.FileUploader({
            element: document.getElementById('file-uploader'),
            action: '/filebrowser/upload',
            template: '<div class="qq-uploader">' +
                    '<div class="qq-upload-drop-area"><span>${_('Drop files here to upload')}</span></div>' +
                    '<div class="qq-upload-button">${_('Upload a file')}</div>' +
                    '<ul class="qq-upload-list"></ul>' +
                    '</div>',
            fileTemplate: '<li>' +
                    '<span class="qq-upload-file"></span>' +
                    '<span class="qq-upload-spinner"></span>' +
                    '<span class="qq-upload-size"></span>' +
                    '<a class="qq-upload-cancel" href="#">${_('Cancel')}</a>' +
                    '<span class="qq-upload-failed-text">${_('Failed')}</span>' +
                    '</li>',
            params:{
                dest: '${next}',
                fileFieldLabel: 'hdfs_file'
            },
            onComplete:function(id, fileName, responseJSON){
                window.location = "/filebrowser/view${next}";
            },
            debug: true
        });
    }

    // in your app create uploader as soon as the DOM is ready
    // don't wait for the window to load
    window.onload = createUploader;
</script>


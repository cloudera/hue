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
import md5
from django.template.defaultfilters import urlencode, stringformat, filesizeformat, date, time, escape
from desktop.lib.django_util import reverse_with_get
from django.utils.encoding import smart_str
from django.utils.translation import ugettext as _
%>


<%def name="list_table_chooser(files, path, current_request_path)">
  ${_table(files, path, current_request_path, 'chooser')}
</%def>
<%def name="list_table_browser(files, path, current_request_path, cwd_set=True)">
  ${_table(files, path, current_request_path, 'view', cwd_set)}
</%def>
<%def name="_table(files, path, current_request_path, view, cwd_set=False)">
    <script src="/static/ext/js/fileuploader.js" type="text/javascript" charset="utf-8"></script>
    <script src="/static/ext/js/datatables-paging-0.1.js" type="text/javascript" charset="utf-8"></script>
    <link rel="stylesheet" href="/static/ext/css/fileuploader.css" type="text/css" media="screen" title="no title" charset="utf-8" />
    <style type="text/css">
        .pull-right {
            margin: 4px;
        }
        .sortable {
            cursor: pointer;
        }
    </style>
    <div class="well hueWell">
        <p class="pull-right">
            <a href="#" class="btn upload-link">${_('Upload files')}</a>
            <a href="#" class="btn create-directory-link">${_('New directory')}</a>
        </p>
        <form class="form-search">
            ${_('Filter: ')}<input id="filterInput" class="input-xlarge search-query" placeholder="${_('Search for file name')}">
        </form>
    </div>

    <table class="table table-condensed table-striped datatables">
        <thead>
            <tr>
            % if cwd_set:
                <th>${_('Name')}</th>
            % else:
                <th>${_('Path')}</th>
            % endif
                <th>${_('Size')}</th>
                <th>${_('User')}</th>
                <th>${_('Group')}</th>
                <th>${_('Permissions')}</th>
                <th>${_('Date')}</th>
                <th>&nbsp;</th>
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

            <% path = file['path'] %>
            <tr class="file-row" data-search="${display_name}">
                <td>
                    <h5><a href="${url('filebrowser.views.'+view, path=urlencode(path))}?file_filter=${file_filter}" data-row-selector="true">${display_name}</a></h5>
                </td>
                <td>
                    % if "dir" == file['type']:
                    <span>~</span>
                    % else:
                    <span>${file['stats']['size']|filesizeformat}</span>
                    % endif
                </td>
                <td>${file['stats']['user']}</td>
                <td>${file['stats']['group']}</td>
                <td>${file['rwx']}</td>
                <td>${date(datetime.datetime.fromtimestamp(file['stats']['mtime']))} ${time(datetime.datetime.fromtimestamp(file['stats']['mtime'])).replace("p.m.","PM").replace("a.m.","AM")}</td>
                <td>
                    % if ".." != file['name']:
                    <%
                    path_digest = urlencode(md5.md5(smart_str(path)).hexdigest())
                    %>
                    <div class="btn-group">
                        <a class="btn dropdown-toggle" data-toggle="dropdown" href="#">
                            ${_('Options')}
                            <span class="caret"></span>
                        </a>
                        <ul class="dropdown-menu">
                            % if "dir" == file['type']:
                            <li><a class="delete" delete-type="rmdir" file-to-delete="${path}" data-backdrop="static" data-keyboard="true">${_('Delete')}</a></li>
                            <li><a class="delete" delete-type="rmtree" file-to-delete="${path}" data-backdrop="static" data-keyboard="true">${_('Delete Recursively')}</a></li>
                            % else:
                            <li><a class="delete" delete-type="remove" file-to-delete="${path}" data-backdrop="static" data-keyboard="true">${_('Delete')}</a></li>
                            <li><a href="${url('filebrowser.views.view', path=urlencode(path))}">${_('View File')}</a></li>
                            <li><a href="${url('filebrowser.views.edit', path=urlencode(path))}">${_('Edit File')}</a></li>
                            <li><a href="${url('filebrowser.views.download', path=urlencode(path))}" target="_blank">${_('Download File')}</a></li>
                            % endif
                            <li><a class="rename" file-to-rename="${path}">${_('Rename')}</a></li>
                            <li><a onclick="openChownWindow('${path}','${file['stats']['user']}','${file['stats']['group']}','${current_request_path}')">${_('Change Owner / Group')}</a></li>
                            <li><a onclick="openChmodWindow('${path}','${stringformat(file['stats']['mode'], "o")}','${current_request_path}')">${_('Change Permissions')}</a></li>
                            <li><a onclick="openMoveModal('${path}','${stringformat(file['stats']['mode'], "o")}', '${current_request_path}')">${_('Move')}</a></li>
                        </ul>
                    </div>
                    % endif
                </td>
            </tr>
            % endfor
        </tbody>
    </table>

<!-- delete modal -->
<div id="deleteModal" class="modal hide fade">
    <div class="modal-header">
        <a href="#" class="close" data-dismiss="modal">&times;</a>
        <h3>${_('Please Confirm')}</h3>
    </div>
    <div class="modal-body">
        <p>${_('Are you sure you want to delete this file?')}</p>
    </div>
    <div class="modal-footer">
        <form id="deleteForm" action="" method="POST" enctype="multipart/form-data" class="form-stacked">
            <input type="submit" value="${_('Yes')}" class="btn primary" />
            <a id="cancelDeleteBtn" class="btn">${_('No')}</a>
            <input id="fileToDeleteInput" type="hidden" name="path" />
        </form>
    </div>
</div>

<!-- rename modal -->
<div id="renameModal" class="modal hide fade">
    <form id="renameForm" action="/filebrowser/rename?next=${current_request_path}" method="POST" enctype="multipart/form-data" class="form-inline form-padding-fix">
    <div class="modal-header">
        <a href="#" class="close" data-dismiss="modal">&times;</a>
        <h3>${_('Renaming:')} <span id="renameFileName">file name</span></h3>
    </div>
    <div class="modal-body">
        <label>${_('New name')} <input id="newNameInput" name="dest_path" value="" type="text" class="input-xlarge"/></label>
    </div>
    <div class="modal-footer">
        <div id="renameNameRequiredAlert" class="hide" style="position: absolute; left: 10;">
            <span class="label label-important">${_('Sorry, name is required.')}</span>
        </div>

        <input id="renameSrcPath" type="hidden" name="src_path" type="text">
        <input type="submit" value="${_('Submit')}" class="btn primary" />
        <a id="cancelRenameBtn" class="btn">${_('Cancel')}</a>
    </div>
    </form>
</div>

<!-- upload modal -->
<div id="uploadModal" class="modal hide fade">
    <form id="uploadForm" action="/filebrowser/rename?next=${current_request_path}" method="POST" enctype="multipart/form-data" class="form-stacked form-padding-fix">
    <div class="modal-header">
        <a href="#" class="close" data-dismiss="modal">&times;</a>
        <h3>${_('Uploading to:')} <span id="uploadDirName">${current_dir_path}</span></h3>
    </div>
    <div class="modal-body">
        <form action="/filebrowser/upload?next=${current_dir_path}" method="POST" enctype="multipart/form-data" class="form-stacked">
            <div id="fileUploader">
            <noscript>
                <p>${_('Please enable JavaScript to use file uploader.')}</p>
            </noscript>
            </div>
        </form>
    </div>
    <div class="modal-footer"></div>
    </form>
</div>

<!-- create directory modal -->
<div id="createDirectoryModal" class="modal hide fade">
    <form id="createDirectoryForm" action="/filebrowser/mkdir?next=${current_request_path}" method="POST" enctype="multipart/form-data" class="form-inline form-padding-fix">
    <div class="modal-header">
        <a href="#" class="close" data-dismiss="modal">&times;</a>
        <h3>${_('Create Directory')}</h3>
    </div>
    <div class="modal-body">
        <label>${_('Directory Name')} <input id="newDirectoryNameInput" name="name" value="" type="text" class="input-xlarge"/></label>
        <input type="hidden" name="path" type="text" value="${current_dir_path}"/>
    </div>
    <div class="modal-footer">
         <div id="directoryNameRequiredAlert" class="alert-message error hide" style="position: absolute; left: 10;">
            <p><strong>${_('Sorry, directory name is required.')}</strong>
        </div>
        <input class="btn primary" type="submit" value="${_('Submit')}" />
        <a id="cancelCreateDirectoryBtn" class="btn" href="#">${_('Cancel')}</a>
    </div>
    </form>
</div>


<div id="changeOwnerModal" class="modal hide fade">
</div>

<div id="changePermissionModal" class="modal hide fade">
</div>

<div id="moveModal" class="modal hide fade">
</div>

<script type="text/javascript" charset="utf-8">
    // ajax modal windows
    function openChownWindow(path, user, group, next){
        $.ajax({
            url: "/filebrowser/chown",
            data: {"path":path, "user":user, "group" : group, "next" : next},
            beforeSend: function(xhr){
                xhr.setRequestHeader("X-Requested-With", "Hue");
            },
            dataType: "html",
            success: function(data){
                $("#changeOwnerModal").html(data);
                $("#changeOwnerModal").modal({
                    backdrop: "static",
                    keyboard: true,
                    show: true
                });
            }
        });
    }

    function openChmodWindow(path, mode, next){
        $.ajax({
            url: "/filebrowser/chmod",
            data: {"path":path, "mode":mode, "next" : next},
            beforeSend: function(xhr){
                xhr.setRequestHeader("X-Requested-With", "Hue");
            },
            dataType: "html",
            success: function(data){
                $("#changePermissionModal").html(data);
                $("#changePermissionModal").modal({
                    backdrop: "static",
                    keyboard: true,
                    show: true
                });
            }
        });
    }

    function openMoveModal(src_path, mode, next){
        $.ajax({
            url: "/filebrowser/move",
            data: {"src_path":src_path, "mode":mode, "next" : next},
            beforeSend: function(xhr){
                xhr.setRequestHeader("X-Requested-With", "Hue");
            },
            dataType: "html",
            success: function(data){
                $("#moveModal").html(data);
                $("#moveModal").modal({
                    backdrop: "static",
                    keyboard: true,
                    show: true
                });
            }
        });
    }
    //uploader
    var num_of_pending_uploads = 0;
    function createUploader(){
        var uploader = new qq.FileUploader({
            element: document.getElementById("fileUploader"),
            action: "/filebrowser/upload",
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
                dest: "${current_dir_path}",
                fileFieldLabel: "hdfs_file"
            },
            onComplete:function(id, fileName, responseJSON){
                num_of_pending_uploads--;
                if(num_of_pending_uploads == 0){
                    window.location = "/filebrowser/view${current_dir_path}";
                }
            },
            onSubmit:function(id, fileName, responseJSON){
                num_of_pending_uploads++;
            },
            debug: true
        });
    }

    // in your app create uploader as soon as the DOM is ready
    // don"t wait for the window to load
    window.onload = createUploader;

    $(document).ready(function(){
        //filter handlers
        var oTable = $('.datatables').dataTable( {
          "sPaginationType": "bootstrap",
          "bLengthChange": false,
          "iDisplayLength": 15,
          "sDom": "<'row'r>t<'row'<'span8'i><''p>>",
          "aoColumns": [
                null,
                null,
                null,
                null,
                null,
                { "sType": "date" },
                null
            ]
        });

        $("#filterInput").keyup(function() {
            oTable.fnFilter($(this).val(), 0 /* Column Idx */);
        });

        //delete handlers
        $(".delete").live("click", function(e){
            $("#fileToDeleteInput").attr("value", $(e.target).attr("file-to-delete"));
            $("#deleteForm").attr("action", "/filebrowser/" + $(e.target).attr("delete-type") + "?next=" + encodeURI("${current_request_path}") + "&path=" + encodeURI("${path}"));
            $("#deleteModal").modal({
                backdrop: "static",
                keyboard: true,
                show: true
            });
        });

        $("#cancelDeleteBtn").click(function(){
            $("#deleteModal").modal("hide");
        });

        //rename handlers
        $(".rename").live("click",function(eventObject){
            $("#renameSrcPath").attr("value", $(eventObject.target).attr("file-to-rename"));
            $("#renameFileName").text($(eventObject.target).attr("file-to-rename"));
            $("#renameModal").modal({
                backdrop: "static",
                keyboard: true,
                show: true
            });
        });

        $("#cancelRenameBtn").click(function(){
            $("#renameModal").modal("hide");
        });

        $("#renameForm").submit(function(){
            if($("#newNameInput").val() == ""){
                $("#renameNameRequiredAlert").show();
                $("#newNameInput").addClass("fieldError");
                return false;
            }
        });

        $("#newNameInput").focus(function(){
            $("#renameNameRequiredAlert").hide();
            $("#newNameInput").removeClass("fieldError");
        });

        $("#moveForm").live("submit", function(){
            if ($.trim($("#moveForm").find("input[name='dest_path']").val()) == ""){
                $("#moveNameRequiredAlert").show();
                $("#moveForm").find("input[name='dest_path']").addClass("fieldError");
                return false;
            }
            return true;
        });

        $("#moveForm").find("input[name='dest_path']").live("focus", function(){
            $("#moveNameRequiredAlert").hide();
            $("#moveForm").find("input[name='dest_path']").removeClass("fieldError");
        });


        //upload handlers
        $(".upload-link").click(function(){
            $("#uploadModal").modal({
                backdrop: "static",
                keyboard: true,
                show: true
            });
        });

        //create directory handlers
        $(".create-directory-link").click(function(){
            $("#createDirectoryModal").modal({
                backdrop: "static",
                keyboard: true,
                show: true
            });
        });

        $("#cancelCreateDirectoryBtn").click(function(){
            $("#createDirectoryModal").modal("hide");
        });

        $("#createDirectoryForm").submit(function(){
            if ($.trim($("#newDirectoryNameInput").val())==""){
                $("#directoryNameRequiredAlert").show();
                $("#newDirectoryNameInput").addClass("fieldError");
                return false;
            }
            return true;
        });

        $("#newDirectoryNameInput").focus(function(){
            $("#newDirectoryNameInput").removeClass("fieldError");
            $("#directoryNameRequiredAlert").hide();
        });

        $(".pathChooser").click(function(){
            var self = this;
            $("#fileChooserRename").jHueFileChooser({
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
            $("#fileChooserRename").slideDown();
        });

        $("a[data-row-selector='true']").jHueRowSelector();
    });
</script>

</%def>

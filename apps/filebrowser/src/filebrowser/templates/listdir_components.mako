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
from desktop.lib.django_util import reverse_with_get, extract_field_data
from django.utils.encoding import smart_str
from django.utils.translation import ugettext as _
%>

<%namespace name="edit" file="editor_components.mako" />

<%def name="list_table_chooser(files, path, current_request_path)">
  ${_table(files, path, current_request_path, 'chooser')}
</%def>

<%def name="list_table_browser(files, path, current_request_path, cwd_set=True)">
  ${_table(files, path, current_request_path, 'view')}
</%def>

<%def name="_table(files, path, current_request_path, view)">
    <script src="/static/ext/js/knockout-2.1.0.js" type="text/javascript" charset="utf-8"></script>
    <script src="/static/ext/js/moment.min.js" type="text/javascript" charset="utf-8"></script>
    <script src="/static/ext/js/datatables-paging-0.1.js" type="text/javascript" charset="utf-8"></script>
    <style type="text/css">
        .fixed {
            position: fixed;
            top: 40px;
            filter: progid:dximagetransform.microsoft.gradient(startColorstr='#ffffffff', endColorstr='#fff2f2f2', GradientType=0);
            -webkit-box-shadow: 0 1px 4px rgba(0, 0, 0, 0.065);
            -moz-box-shadow: 0 1px 4px rgba(0, 0, 0, 0.065);
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.065);
        }
        .pull-right {
            margin: 4px;
        }
        .sortable {
            cursor: pointer;
        }
        .file-row {
            height:37px;
        }
        .fileChooserModal {
            padding: 14px;
        }
        .fileChooserModal .hueBreadcrumb {
            margin: 0 0 18px!important;
        }
    </style>

    <table class="table table-striped table-condensed datatables">
        <thead>
            <tr>
                <th width="1%"><div data-bind="click: selectAll, css: {hueCheckbox: true, 'icon-ok': allSelected}"></div></th>
                <th class="sortable sorting" data-sort="type" width="4%" data-bind="click: sort">Type</th>
                <th class="sortable sorting" data-sort="name" data-bind="click: sort">${_('Name')}</th>
                <th class="sortable sorting" data-sort="size" width="10%" data-bind="click: sort">${_('Size')}</th>
                <th class="sortable sorting" data-sort="user" width="10%" data-bind="click: sort">${_('User')}</th>
                <th class="sortable sorting" data-sort="group" width="10%" data-bind="click: sort">${_('Group')}</th>
                <th width="10%">${_('Permissions')}</th>
                <th class="sortable sorting" data-sort="mtime" width="15%" data-bind="click: sort">${_('Date')}</th>
            </tr>
        </thead>
        <tbody id="files" data-bind="template: {name: 'fileTemplate', foreach: files}">

        </tbody>
        <tfoot>
        <tr data-bind="visible: isLoading()">
            <td colspan="8" class="left">
                <img src="/static/art/spinner.gif" />
            </td>
        </tr>
            <tr data-bind="visible: files().length == 0 && !isLoading()">
                <td colspan="8">
                    <div class="alert">
                        There are no files matching the search criteria.
                    </div>
                </td>
            </tr>
        </tfoot>
    </table>

    <script id="fileTemplate" type="text/html">
        <tr style="cursor: pointer">
            <td class="center" data-bind="click: handleSelect" style="cursor: default">
                <div data-bind="visible: name != '..', css: {hueCheckbox: name != '..', 'icon-ok': selected}"></div>
            </td>
            <td data-bind="click: $root.viewFile" class="left"><i data-bind="css: {'icon-file': type == 'file', 'icon-folder-close': type != 'file'}"></i></td>
            <td data-bind="click: $root.viewFile">
                <strong><a href="#" data-bind="click: $root.viewFile, text: name"></a></strong>
            </td>
            <td data-bind="click: $root.viewFile">
                <span data-bind="visible: type=='file', text: stats.size"></span>
            </td>
            <td data-bind="click: $root.viewFile, text: stats.user"></td>
            <td data-bind="click: $root.viewFile, text: stats.group"></td>
            <td data-bind="click: $root.viewFile, text: permissions"></td>
            <td data-bind="click: $root.viewFile, text: stats.mtime" style="white-space: nowrap;"></td>
        </tr>
    </script>


    <div class="pagination" data-bind="visible: !isLoading()">
        <ul class="pull-right">
            <li class="prev" data-bind="visible: page().number > 1"><a href="#" data-bind="click: firstPage" title="${_('Beginning of List')}">&larr; ${_('Beginning of List')}</a></li>
            <li data-bind="visible: page().number > 1"><a href="#" data-bind="click: previousPage" title="${_('Previous Page')}">${_('Previous Page')}</a></li>
            <li data-bind="visible: page().number < page().num_pages"><a href="#" data-bind="click: nextPage" title="${_('Next page')}">${_('Next Page')}</a></li>
            <li class="next" data-bind="visible: page().number < page().num_pages"><a href="#" data-bind="click: lastPage" title="${_('End of List')}">${_('End of List')} &rarr;</a></li>
        </ul>
        <p>${_('Show')}
            <select class="input-mini" data-bind="options: recordsPerPageChoices, value: recordsPerPage"></select>
        ${_('items per page')}.
        ${_('Showing')} <span data-bind="text: page().start_index"></span> ${_('to')} <span data-bind="text: page().end_index"></span> ${_('of')} <span data-bind="text: page().total_count"></span> ${_('items, page')}
            <span data-bind="text: page().number"></span> ${_('of')} <span data-bind="text: page().num_pages"></span></p>
    </div>

    <!-- delete modal -->
    <div id="deleteModal" class="modal hide fade">
        <div class="modal-header">
            <a href="#" class="close" data-dismiss="modal">&times;</a>
            <h3>${_('Please Confirm')}</h3>
        </div>
        <div class="modal-body">
            <p>${_('Are you sure you want to delete these files?')}</p>
        </div>
        <div class="modal-footer">
            <form id="deleteForm" action="/filebrowser/rmtree" method="POST" enctype="multipart/form-data" class="form-stacked">
                <input type="submit" value="${_('Yes')}" class="btn primary" />
                <a id="cancelDeleteBtn" class="btn">${_('No')}</a>
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
            <a id="cancelRenameBtn" class="btn">${_('Cancel')}</a>
            <input type="submit" value="${_('Submit')}" class="btn primary" />
        </div>
        </form>
    </div>

    <!-- chown modal -->
    % if is_superuser:
    <div id="changeOwnerModal" class="modal hide fade">
        <%
          select_filter = is_superuser and 'SelectWithOther' or ''
        %>
        <form id="chownForm" action="/filebrowser/chown" method="POST" enctype="multipart/form-data" class="form-stacked form-padding-fix">
            <div class="modal-header">
                <a href="#" class="close" data-dismiss="modal">&times;</a>
                <h3>${_('Change Owner / Group')}</h3>
            </div>
            <div class="modal-body change-owner-modal-body clearfix" >
                <div class="alert alert-message block-message info">${_('Note: Only the Hadoop superuser, "%(superuser)s" on this file system, may change the owner of a file.') % dict(superuser=superuser)}</div>
                <div style="padding-left: 15px; padding-bottom: 10px;">
                    <label>${_('User')}</label>
                    ${ edit.selection("user", users, user.username, "user_other") }
                    <label>${_('Group')}</label>
                    ${ edit.selection("group", groups, 'supergroup', "group_other") }
                    <br />
                    <label style="display: inline;">${_('Recursive')}</label><input type="checkbox" name="recursive">
                </div>


            </div>
            <div class="modal-footer" style="padding-top: 10px;">
                <div id="chownRequired" class="hide" style="position: absolute; left: 10;">
                    <span class="label label-important">${_('Sorry, name is required.')}</span>
                </div>
                <a class="btn" onclick="$('#changeOwnerModal').modal('hide');">${_('Cancel')}</a>
                <input class="btn primary" type="submit" value="${_('Submit')}" />
            </div>
        </form>
    </div>
    % endif

    <!-- chmod modal -->
    <div id="changePermissionModal" class="modal hide fade">
        <form action="/filebrowser/chmod" method="POST" enctype="multipart/form-data" class="form-inline form-padding-fix" id="chmodForm">
            <div class="modal-header">
                <a href="#" class="close" data-dismiss="modal">&times;</a>
                <h3>${_('Change Permissions:')} </h3>
            </div>
            <div class="modal-body table-margin">
                <table class="table table-striped">
                    <thead>
                    <tr>
                        <th>&nbsp;</th>
                        <th class="center">${_('User')}</th>
                        <th class="center">${_('Group')}</th>
                        <th class="center">${_('Other')}</th>
                        <th class="center">&nbsp;</th>
                        <th width="120">&nbsp</th>
                    </tr>
                    </thead>
                    <tbody>
                    <tr>
                        <td><strong>${_('Read')}</strong></td>
                        <td class="center"><input type="checkbox" data-bind="attr: {checked: selectedFile.mode }" checked="" name="user_read"></td>
                        <td class="center"><input type="checkbox" data-bind="attr: {checked: selectedFile.mode }" checked="" name="group_read"></td>
                        <td class="center"><input type="checkbox" data-bind="attr: {checked: selectedFile.mode }" checked="" name="other_read"></td>
                        <td colspan="2">&nbsp;</td>
                    </tr>
                    <tr>
                        <td><strong>${_('Write')}</strong></td>
                        <td class="center"><input type="checkbox" data-bind="attr: {checked: selectedFile.mode }" checked="" name="user_write"></td>
                        <td class="center"><input type="checkbox" data-bind="attr: {checked: selectedFile.mode }" checked="" name="group_write"></td>
                        <td class="center"><input type="checkbox" data-bind="attr: {checked: selectedFile.mode }" checked="" name="other_write"></td>
                        <td colspan="2">&nbsp;</td>
                    </tr>
                    <tr>
                        <td><strong>${_('Execute')}</strong></td>
                        <td class="center"><input type="checkbox" checked="" name="user_execute"></td>
                        <td class="center"><input type="checkbox" checked="" name="group_execute"></td>
                        <td class="center"><input type="checkbox" checked="" name="other_execute"></td>
                        <td colspan="2">&nbsp;</td>
                    </tr>
                    <tr>
                        <td><strong>${_('Sticky')}</strong></td>
                        <td colspan="3">&nbsp;</td>
                        <td class="center"><input type="checkbox" name="sticky"></td>
                        <td>&nbsp;</td>
                    </tr>
                    <tr>
                        <td><strong>${_('Recursive')}</strong></td>
                        <td colspan="3">&nbsp;</td>
                        <td class="center"><input type="checkbox" name="recursive"></td>
                        <td>&nbsp;</td>
                    </tbody>
                </table>
            </div>
            <div class="modal-footer" style="padding-top: 10px;">
                <a class="btn" onclick="$('#changePermissionModal').modal('hide');">${_('Cancel')}</a>
                <input class="btn primary" type="submit" value="${_('Submit')}"/>
            </div>
        </form>
    </div>

    <!-- move modal -->
    <div id="moveModal" class="modal hide fade">
        <form id="moveForm" action="/filebrowser/move" method="POST" enctype="multipart/form-data" class="form-inline form-padding-fix">
            <div class="modal-header">
                <a href="#" class="close" data-dismiss="modal">&times;</a>
                <h3>${_('Move:')}</h3>
            </div>
            <div class="modal-body">
                <div style="padding-left: 15px;">
                    <label for="moveDestination">${_('Destination')}</label>
                    <input type="text" class="input-xlarge pathChooser" value="" name="dest_path" id="moveDestination" /><a class="btn fileChooserBtn" href="#" data-filechooser-destination="dest_path">..</a>
                </div>
                <br/>
                <div class="fileChooserModal" class="hide">
                </div>
            </div>
            <div class="modal-footer">
                <div id="moveNameRequiredAlert" class="hide" style="position: absolute; left: 10;">
                    <span class="label label-important">${_('Sorry, name is required.')}</span>
                </div>
                <a class="btn" onclick="$('#moveModal').modal('hide');">${_('Cancel')}</a>
                <input class="btn primary" type="submit" value="${_('Submit')}"/>
            </div>
        </form>
    </div>

    <!-- upload file modal -->
    <div id="uploadFileModal" class="modal hide fade">
        <div class="modal-header">
            <a href="#" class="close" data-dismiss="modal">&times;</a>
            <h3>${_('Uploading to:')} <span id="uploadDirName" data-bind="text: currentPath"></span></h3>
        </div>
        <div class="modal-body form-inline">
            <div id="fileUploader" class="uploader">
            <noscript>
                <p>${_('Please enable JavaScript to use the file uploader.')}</p>
            </noscript>
            </div>
        </div>
        <div class="modal-footer"></div>
    </div>

    <!-- upload archive modal -->
    <div id="uploadArchiveModal" class="modal hide fade">
        <div class="modal-header">
            <a href="#" class="close" data-dismiss="modal">&times;</a>
            <h3>${_('Uploading to:')} <span id="uploadDirName" data-bind="text: currentPath"></span></h3>
            <p>${_('The file will then be extracted in the path specified above.')}</p>
        </div>
        <div class="modal-body form-inline">
            <div id="archiveUploader" class="uploader">
            <noscript>
                <p>${_('Please enable JavaScript to use the file uploader.')}</p>
            </noscript>
            </div>
        </div>
        <div class="modal-footer"></div>
    </div>

    <!-- new directory modal -->
    <div id="createDirectoryModal" class="modal hide fade">
        <form id="createDirectoryForm" data-bind="submit: createDirectory" method="POST" enctype="multipart/form-data" class="form-inline form-padding-fix">
        <div class="modal-header">
            <a href="#" class="close" data-dismiss="modal">&times;</a>
            <h3>${_('Create Directory')}</h3>
        </div>
        <div class="modal-body">
            <label>${_('Directory Name')} <input id="newDirectoryNameInput" name="name" value="" type="text" class="input-xlarge"/></label>
            <input type="hidden" name="path" type="text" data-bind="value: currentPath"/>
        </div>
        <div class="modal-footer">
             <div id="directoryNameRequiredAlert" class="alert-message error hide" style="position: absolute; left: 10;">
                <p><strong>${_('Sorry, directory name is required.')}</strong>
            </div>
            <a id="cancelCreateDirectoryBtn" class="btn" href="#">${_('Cancel')}</a>
            <input class="btn primary" type="submit" value="${_('Submit')}" />
        </div>
        </form>
    </div>

    <!-- new directory modal -->
    <div id="createFileModal" class="modal hide fade">
        <form id="createFileForm" data-bind="submit: createFile" method="POST" enctype="multipart/form-data" class="form-inline form-padding-fix">
        <div class="modal-header">
            <a href="#" class="close" data-dismiss="modal">&times;</a>
            <h3>${_('Create File')}</h3>
        </div>
        <div class="modal-body">
            <label>${_('File Name')} <input id="newFileNameInput" name="name" value="" type="text" class="input-xlarge"/></label>
            <input type="hidden" name="path" type="text" data-bind="value: currentPath"/>
        </div>
        <div class="modal-footer">
             <div id="fileNameRequiredAlert" class="alert-message error hide" style="position: absolute; left: 10;">
                <p><strong>${_('Sorry, file name is required.')}</strong>
            </div>
            <a id="cancelCreateFileBtn" class="btn" href="#">${_('Cancel')}</a>
            <input class="btn primary" type="submit" value="${_('Submit')}" />
        </div>
        </form>
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
                        keyboard: true,
                        show: true
                    });
                }
            });
        }

        // Modal file chooser
        // The file chooser should be at least 2 levels deeper than the modal container
        $(".fileChooserBtn").on('click', function(e){
            e.preventDefault();
            var _destination = $(this).attr("data-filechooser-destination");
            var fileChooser = $(this).parent().parent().find(".fileChooserModal");
            fileChooser.jHueFileChooser({
                initialPath: $("input[name='"+_destination+"']").val(),
                onFolderChange: function(folderPath){
                    $("input[name='"+_destination+"']").val(folderPath);
                },
                onFolderChoose: function(folderPath){
                    $("input[name='"+_destination+"']").val(folderPath);
                    fileChooser.slideUp();
                },
                selectFolder: true,
                createFolder: true,
                uploadFile: false
            });
            fileChooser.slideDown();
        });

        $(document).ready(function(){
            $("#chownForm select[name='user']").change(function(){
                if ($(this).val() == "__other__"){
                    $("input[name='user_other']").show();
                }
                else {
                    $("input[name='user_other']").hide();
                }
            });
            $("#chownForm  select[name='group']").change(function(){
                if ($(this).val() == "__other__"){
                    $("input[name='group_other']").show();
                }
                else {
                    $("input[name='group_other']").hide();
                }
            });

            $("#chownForm").submit(function(){
                if ($("#chownForm select[name='user']").val() == null){
                    $("#chownRequired").find(".label").text("${_('Sorry, user is required.')}");
                    $("#chownRequired").show();
                    return false;
                }
                else if ($("#chownForm select[name='group']").val() == null){
                    $("#chownRequired").find(".label").text("${_('Sorry, group is required.')}");
                    $("#chownRequired").show();
                    return false;
                }
                else {
                    if ($("#chownForm select[name='group']").val() == "__other__" && $("input[name='group_other']").val() == ""){
                        $("#chownRequired").find(".label").text("${_('Sorry, you need to specify another group.')}");
                        $("#chownForm input[name='group_other']").addClass("fieldError");
                        $("#chownRequired").show();
                        return false;
                    }
                    if ($("#chownForm select[name='user']").val() == "__other__" && $("input[name='user_other']").val() == ""){
                        $("#chownRequired").find(".label").text("${_('Sorry, you need to specify another user.')}");
                        $("#chownForm input[name='user_other']").addClass("fieldError");
                        $("#chownRequired").show();
                        return false;
                    }
                    return true;
                }
            });

            $("#cancelDeleteBtn").click(function(){
                $("#deleteModal").modal("hide");
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
                if ($.trim($("#moveForm").find("input.pathChooser").val()) == ""){
                    $("#moveNameRequiredAlert").show();
                    $("#moveForm").find("input[name='*dest_path']").addClass("fieldError");
                    return false;
                }
                return true;
            });

            $("#moveForm").find("input[name='dest_path']").live("focus", function(){
                $("#moveNameRequiredAlert").hide();
                $("#moveForm").find("input[name='dest_path']").removeClass("fieldError");
            });

            $(".create-directory-link").click(function(){
                $("#createDirectoryModal").modal({
                    keyboard: true,
                    show: true
                });
            });

            $(".create-file-link").click(function(){
                $("#createFileModal").modal({
                    keyboard: true,
                    show: true
                });
            });

            $("#cancelCreateDirectoryBtn").click(function(){
                $("#createDirectoryModal").modal("hide");
            });

            $("#cancelCreateFileBtn").click(function(){
                $("#createFileModal").modal("hide");
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

            $("*[rel='tooltip']").tooltip({ placement: "bottom" });
            if (window.location.hash != null && window.location.hash.length > 1){
                viewModel.targetPath("${url('filebrowser.views.view', path=urlencode('/'))}" + window.location.hash.substring(2));
            }
            viewModel.retrieveData();

            var filterTimeout = -1;
            $(".search-query").keyup(function(){
                window.clearTimeout(filterTimeout);
                filterTimeout = window.setTimeout(function(){
                    viewModel.searchQuery($(".search-query").val());
                    viewModel.filter();
                }, 500);
            });

            $("#editBreadcrumb").click(function(){
                $(this).hide();
                $(".hueBreadcrumb").hide();
                $("#hueBreadcrumbText").show().focus();
            });

            $("#hueBreadcrumbText").keyup(function(e){
                if (e.keyCode == 13) {
                    var _el = $(this);
                    viewModel.targetPath("${url('filebrowser.views.view', path=urlencode('/'))}" + _el.val().substring(1));
                    viewModel.getStats(function (data) {
                        if (data.type != null && data.type == "file") {
                            location.href = data.url;
                            return false;
                        }
                        else {
                            window.location.hash = _el.val();
                        }
                    });
                }
            });

            $("#hueBreadcrumbText").blur(function(){
                $(this).hide();
                $(".hueBreadcrumb").show();
                $("#editBreadcrumb").show();
            });

            $.ajaxSetup({
                error: function(x, e) {
                    if (x.status == 500) {
                        $.jHueNotify.error("${_('There was a problem with your request.')}");
                        $("#hueBreadcrumbText").blur();
                    }
                }
            });

            $(window).bind("hashchange", function() {
                var target = "";
                var hash = window.location.hash.substring(1);
                if (hash != null && hash != "") {
                    target = "${url('filebrowser.views.view', path=urlencode('/'))}" + hash.substring(1);
                }
                if (window.location.href.indexOf("#") == -1){
                    target = "${current_request_path}";
                }
                if (target != ""){
                    viewModel.targetPath(target);
                    viewModel.retrieveData();
                }
            });

        });


        var Page = function (page) {
            if (page != null) {
                return {
                    number:page.number,
                    num_pages:page.num_pages,
                    previous_page_number:page.previous_page_number,
                    next_page_number:page.next_page_number,
                    start_index:page.start_index,
                    end_index:page.end_index,
                    total_count:page.total_count
                }
            }
            return {
            }
        }

        var File = function (file) {
            return {
                name:file.name,
                path:file.path,
                url:file.url,
                type:file.type,
                permissions:file.rwx,
                mode:file.mode,
                stats:{
                    size:file.humansize,
                    user:file.stats.user,
                    group:file.stats.group,
                    mtime:moment.unix(file.stats.mtime).format("MMMM DD, YYYY hh:mm a")
                },
                selected:ko.observable(false),
                handleSelect:function (row, e) {
                    this.selected(!this.selected());
                }
            }
        }

        var Breadcrumb = function (breadcrumb) {
            return {
                url:breadcrumb.url,
                label:breadcrumb.label,
                show:function () {
                    if (this.url == null || this.url == ""){
                        // forcing root on empty breadcrumb url
                        this.url = "/";
                    }
                    viewModel.targetPath("${url('filebrowser.views.view', path=urlencode('/'))}" + this.url);
                    window.location.hash = this.url;
                }
            }
        }

        var FileBrowserModel = function (files, page, breadcrumbs, currentDirPath) {
            var self = this;

            self.page = ko.observable(new Page(page));
            self.recordsPerPageChoices = ["15", "30", "45", "60", "100", "200"],
                    self.recordsPerPage = ko.observable("30");
            self.targetPageNum = ko.observable(1);
            self.targetPath = ko.observable("${current_request_path}");

            self.sortBy = ko.observable("name");
            self.sortDescending = ko.observable(false);

            self.searchQuery = ko.observable("");

            self.files = ko.observableArray(ko.utils.arrayMap(files, function (file) {
                return new File(file);
            }));

            self.breadcrumbs = ko.observableArray(ko.utils.arrayMap(breadcrumbs, function (breadcrumb) {
                return new Breadcrumb(breadcrumb);
            }));

            self.sort = function (viewModel, event) {
                var el = $(event.currentTarget);
                el.siblings(".sortable").attr("class", "sortable sorting");
                self.sortBy(el.data("sort"))
                el.removeClass("sorting");
                if (el.hasClass("sorting_asc")) {
                    self.sortDescending(true);
                }
                else {
                    self.sortDescending(false);
                }
                el.attr("class", "sortable");
                if (self.sortDescending() == true) {
                    el.addClass("sorting_desc");
                }
                else {
                    el.addClass("sorting_asc");
                }
                self.retrieveData();
            }

            self.isLoading = ko.observable(true);

            self.allSelected = ko.observable(false);

            self.selectedFiles = ko.computed(function () {
                return ko.utils.arrayFilter(self.files(), function (file) {
                    return file.selected();
                });
            }, self);

            self.selectedFile = ko.computed(function () {
                return self.selectedFiles()[0];
            }, self);

            self.currentPath = ko.observable(currentDirPath);

            self.getStats = function (callback) {
                $.getJSON(self.targetPath() + "?pagesize=1&format=json", callback);
            }

            self.retrieveData = function () {
                self.isLoading(true);
                $.getJSON(self.targetPath() + "?pagesize=" + self.recordsPerPage() + "&pagenum=" + self.targetPageNum() + "&filter=" + self.searchQuery() + "&sortby=" + self.sortBy() + "&descending=" + self.sortDescending() + "&format=json", function (data) {
                    if (data.type != null && data.type == "file"){
                        location.href = data.url;
                        return false;
                    }
                    self.updateFileList(data.files, data.page, data.breadcrumbs, data.current_dir_path);
                    if ($("#hueBreadcrumbText").is(":visible")){
                        $(".hueBreadcrumb").show();
                        $("#hueBreadcrumbText").hide();
                        $("#editBreadcrumb").show();
                    }
                });
            };

            self.updateFileList = function (files, page, breadcrumbs, currentDirPath) {
                self.page(new Page(page));
                self.files(ko.utils.arrayMap(files, function (file) {
                    return new File(file);
                }));
                self.breadcrumbs(ko.utils.arrayMap(breadcrumbs, function (breadcrumb) {
                    return new Breadcrumb(breadcrumb);
                }));
                self.currentPath(currentDirPath);

                $('.uploader').trigger('fb:updatePath', {dest: self.currentPath()});

                self.isLoading(false);
                $(".scrollable").jHueTableScroller();
            };

            self.recordsPerPage.subscribe(function (newValue) {
                self.retrieveData();
            });

            self.goToPage = function (pageNumber) {
                self.targetPageNum(pageNumber);
                self.retrieveData();
            };

            self.firstPage = function () {
                self.goToPage(1)
            };

            self.previousPage = function () {
                self.goToPage(self.page().previous_page_number)
            };

            self.nextPage = function () {
                self.goToPage(self.page().next_page_number)
            };

            self.lastPage = function () {
                self.goToPage(self.page().num_pages)
            };

            self.selectAll = function () {
                self.allSelected(!self.allSelected());
                ko.utils.arrayForEach(self.files(), function (file) {
                    if (file.name != "..") {
                        file.selected(self.allSelected());
                    }
                });
                return true;
            };

            self.searchQuery.subscribe(function (newValue) {
                self.filter();
            });

            self.filter = function () {
                self.targetPageNum(1);
                self.retrieveData();
            };

            self.viewFile = function (file) {
                if (file.type == "dir") {
                    self.targetPath("${url('filebrowser.views.view', path=urlencode('/'))}" + "." + file.path);
                    window.location.hash = file.path;
                }
                else {
                    location.href = "${url('filebrowser.views.view', path=urlencode('/'))}" + file.path;
                }
            };

            self.editFile = function () {
                location.href = "${url('filebrowser.views.edit', path=urlencode('/'))}" + self.selectedFile().path;
            };

            self.downloadFile = function () {
                location.href = "${url('filebrowser.views.download', path=urlencode('/'))}" + self.selectedFile().path;
            };

            self.renameFile = function () {
                $("#renameSrcPath").attr("value", self.selectedFile().path);
                $("#renameFileName").text(self.selectedFile().path);
                $("#newNameInput").val(self.selectedFile().name);
                $("#renameForm").attr("action", "/filebrowser/rename?next=${url('filebrowser.views.view', path=urlencode('/'))}"+ "." + self.currentPath());
                $("#renameModal").modal({
                    keyboard:true,
                    show:true
                });
            };

            self.move = function () {
                var paths = [];
                $(self.selectedFiles()).each(function(index, file) {
                    paths.push(file.path);
                });
                hiddenFields($("#moveForm"), "src_path", paths);
                $("#moveForm").attr("action", "/filebrowser/move?next=${url('filebrowser.views.view', path=urlencode('/'))}" + "." + self.currentPath());
                $("#moveModal").modal({
                    keyboard:true,
                    show:true
                });
            };

            self.changeOwner = function () {
                var paths = [];
                $(self.selectedFiles()).each(function(index, file) {
                    paths.push(file.path);
                });
                hiddenFields($("#chownForm"), 'path', paths);
                $("#chownForm").attr("action", "/filebrowser/chown?next=${url('filebrowser.views.view', path=urlencode('/'))}" + "." + self.currentPath());
                $("#changeOwnerModal").modal({
                    keyboard:true,
                    show:true
                });

            };

            self.changePermissions = function () {
                var paths = [];
                $(self.selectedFiles()).each(function(index, file) {
                    paths.push(file.path);
                });
                hiddenFields($("#chmodForm"), 'path', paths);
                $("#chmodForm").attr("action", "/filebrowser/chmod?next=${url('filebrowser.views.view', path=urlencode('/'))}" + "." + self.currentPath());
                $("#changePermissionModal").modal({
                    keyboard:true,
                    show:true
                });

                // Initial values for form
                permissions = ["sticky", "user_read", "user_write", "user_execute", "group_read", "group_write", "group_execute", "other_read", "other_write", "other_execute"].reverse();
                var mode = octal(self.selectedFile().mode) & 01777;
                for (var i = 0; i < permissions.length; i++) {
                    if (mode & 1) {
                        $("#chmodForm input[name=" + permissions[i] + "]").attr("checked", true);
                    } else {
                        $("#chmodForm input[name=" + permissions[i] + "]").attr("checked", false);
                    }
                    mode >>>= 1;
                }
            };

            self.deleteSelected = function () {
                var paths = [];
                $(self.selectedFiles()).each(function(index, file) {
                    paths.push(file.path);
                });
                hiddenFields($("#deleteForm"), 'path', paths);
                $("#deleteForm").attr("action", "/filebrowser/rmtree" + "?next=${url('filebrowser.views.view', path=urlencode('/'))}" + "." + self.currentPath());
                $("#deleteModal").modal({
                    keyboard:true,
                    show:true
                });
            };

            self.createDirectory = function (formElement) {
                $(formElement).attr("action", "/filebrowser/mkdir?next=${url('filebrowser.views.view', path=urlencode('/'))}"+ "." + self.currentPath());
                return true;
            };

            self.createFile = function (formElement) {
                $(formElement).attr("action", "/filebrowser/touch?next=${url('filebrowser.views.view', path=urlencode('/'))}"+ "." + self.currentPath());
                return true;
            };

            self.uploadFile = (function() {
                var num_of_pending_uploads = 0;
                var uploader = new qq.FileUploader({
                    element: document.getElementById("fileUploader"),
                    action: "/filebrowser/upload/file",
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
                        dest: self.currentPath(),
                        fileFieldLabel: "hdfs_file"
                    },
                    onComplete:function(id, fileName, responseJSON){
                        num_of_pending_uploads--;
                        if(num_of_pending_uploads == 0){
                            window.location = "/filebrowser/view" + self.currentPath();
                        }
                    },
                    onSubmit:function(id, fileName, responseJSON){
                        num_of_pending_uploads++;
                    },
                    debug: false
                });

                $("#archiveUploader").on('fb:updatePath', function(e, options) {
                    uploader.setParams({
                        dest: options.dest,
                        fileFieldLabel: "hdfs_file"
                    });
                });

                return function() {
                    $("#uploadFileModal").modal({
                        keyboard: true,
                        show: true
                    });
                };
            })();

            self.uploadArchive = (function() {
                var num_of_pending_uploads = 0;
                var uploader = new qq.FileUploader({
                    element: document.getElementById("archiveUploader"),
                    action: "/filebrowser/upload/archive",
                    template: '<div class="qq-uploader">' +
                            '<div class="qq-upload-drop-area"><span>${_('Drop files here to upload')}</span></div>' +
                            '<div class="qq-upload-button">${_('Upload an archive')}</div>' +
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
                        dest: self.currentPath(),
                        fileFieldLabel: "archive"
                    },
                    onComplete:function(id, fileName, responseJSON){
                        num_of_pending_uploads--;
                        if(num_of_pending_uploads == 0){
                            window.location = "/filebrowser/view" + self.currentPath();
                        }
                    },
                    onSubmit:function(id, fileName, responseJSON){
                        num_of_pending_uploads++;
                    },
                    debug: false
                });

                $("#archiveUploader").on('fb:updatePath', function(e, options) {
                    uploader.setParams({
                        dest: options.dest,
                        fileFieldLabel: "archive"
                    });
                });

                return function() {
                    $("#uploadArchiveModal").modal({
                        keyboard: true,
                        show: true
                    });
                };
            })();

            // Place all values into hidden fields under parent element.
            // Looks for managed hidden fields and handles sizing appropriately.
            var hiddenFields = function(parentEl, name, values) {
                parentEl = $(parentEl);
                var fields = parentEl.find("input.hidden-field");

                // Create or delete hidden fields according to needs.
                var resize = values.length - fields.length;
                while(resize > 0) {
                    resize--;
                    var field = $("<input type='hidden' />");
                    field.attr("name", name);
                    field.attr("class", "hidden-field")
                    parentEl.append(field);
                }
                while (resize < 0) {
                    resize++;
                    var field = fields[fields.length - resize - 1]
                    parentEl.remove(field);
                }

                // Set values
                fields = parentEl.find("input.hidden-field");
                $(values).each(function(index, value) {
                    $(fields[index]).val(value);
                });
            }

            var octal = function(strInt) {
                return parseInt("0" + strInt);
            }
        };

        var viewModel = new FileBrowserModel([], null, [], "/");
        ko.applyBindings(viewModel);

    </script>

</%def>

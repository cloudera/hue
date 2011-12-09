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
from django.template.defaultfilters import urlencode, stringformat, filesizeformat, date, time
from desktop.lib.django_util import reverse_with_get
%>


<%def name="list_table_chooser(files, path, current_request_path)">
  ${_table(files, path, current_request_path, 'chooser')}
</%def>
<%def name="list_table_browser(files, path, current_request_path, cwd_set=True)">
  ${_table(files, path, current_request_path, 'view', cwd_set)}
</%def>
<%def name="_table(files, path, current_request_path, view, cwd_set=False)">
  <%
  # Sortable takes a while for big lists; skip it in that case.
  if len(files) < 100:
    optional_sortable = "sortable"
  else:
    optional_sortable = ""
  # FitText doesn't scale well with many rows, so we disable it for
  # larger views.
  if len(files) < 30:
    optional_fit_text = 'data-filters="FitText"'
  else:
    optional_fit_text = ''
  %>
  <script src="/static/ext/js/fileuploader.js" type="text/javascript" charset="utf-8"></script>
  <link rel="stylesheet" href="/static/ext/css/fileuploader.css" type="text/css" media="screen" title="no title" charset="utf-8" />
  <style type="text/css">
    .form-padding-fix{
        display: inline;
        padding: 0;
        margin: 0;
    }
  </style>
  <div  class="well">Filter by name: <input id="filter-input"/><a href="#" id="clear-filter-button" class="btn">Clear</a></div>
  <table class="datatables">
    <thead>
      <tr>
        % if cwd_set:
          <th>Name</th>
        % else:
          <th>Path</th>
        % endif
        <th>Size</th>
        <th>User</th>
        <th>Group</th>
        <th>Permissions</th>
        <th>Date</th>
        <th></th>
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
  ## Since path is in unicode, Django and Mako handle url encoding and
  ## iri encoding correctly for us.

        <% path = file['path'] %>
        <tr class="file-row" file-name="${display_name}">
          <td>
            <div>
              % if "dir" == file['type']:
                <h5><a ${optional_fit_text | n} href="${url('filebrowser.views.'+view, path=urlencode(path))}?file_filter=${file_filter}">${display_name}</a></h5>
              % else:
                <h5><a ${optional_fit_text | n} href="${url('filebrowser.views.'+view, path=urlencode(path))}?file_filter=${file_filter}">${display_name}</a></h5>
              % endif

            </div>
          </td>
          <%
            if "dir" == file['type']:
              sortValue = 0;
            else:
              sortValue = file['stats']['size']
          %>
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
          <td><span>${date(datetime.datetime.fromtimestamp(file['stats']['mtime']))} ${time(datetime.datetime.fromtimestamp(file['stats']['mtime']))}</span></td>
          <td>
             % if ".." != file['name']:
                % if "dir" == file['type']:
                  <a class="btn danger small delete" delete-type="rmdir" file-to-delete="${path}" data-backdrop="true" data-keyboard="true">Delete</a></li>
                  <a class="btn danger small delete" delete-type="rmtree" file-to-delete="${path}" >Delete Recursively</a>
                % else:
                  <a class="btn small danger delete" delete-type="remove" file-to-delete="${path}">Delete</a>
                  <a class="btn small" href="${url('filebrowser.views.view', path=urlencode(path))}">View File</a>
                  <a class="btn small" href="${url('filebrowser.views.edit', path=urlencode(path))}">Edit File</a>
                  <a class="btn small" href="${url('filebrowser.views.download', path=urlencode(path))}" target="_blank">Download File</a>

                % endif
                <a class="btn small rename" file-to-rename="${path}">Rename</a>
                <a class="btn small" onclick="openChownWindow('${path}','${file['stats']['user']}','${file['stats']['group']}','${current_request_path}')">Change Owner / Group</a>

                <a class="btn small" onclick="openChmodWindow('${path}','${stringformat(file['stats']['mode'], "o")}','${current_request_path}')">Change Permissions</a>
                <a class="btn small" onclick="openMoveModal('${path}','${stringformat(file['stats']['mode'], "o")}', '${current_request_path}')">Move</a>


              % endif
          </td>
        </tr>
      % endfor
    </tbody>
  </table>
<!-- delete modal -->
<div id="delete-modal" class="modal hide fade">

    <div class="modal-header">
        <a href="#" class="close">&times;</a>
        <h3>Please Confirm</h3>
    </div>
    <div class="modal-body">
        <p>Are you sure you want to delete this file?</p>
    </div>
    <div class="modal-footer">
        <a id="cancel-delete-button" class="btn primary">No</a>
        <form id="delete-form" action="" method="POST" enctype="multipart/form-data" class="form-stacked">
        <input id="file-to-delete-input" type="hidden" name="path" id="id_path" />
        <input type="submit" value="Yes" class="btn" />
        </form>
    </div>

</div>
<!-- rename modal -->

<div id="rename-modal" class="modal hide fade">
    <form id="rename-form" action="/filebrowser/rename?next=${current_request_path}" method="POST" enctype="multipart/form-data" class="form-stacked form-padding-fix">
    <div class="modal-header">
        <a href="#" class="close">&times;</a>
        <h3>Renaming: <span id="rename-file-name">file name</span></h3>
    </div>
    <div class="modal-body">
        <div class="clearfix">
            <label>New name</label>
            <div class="input">
                <input id="new-name-input" name="dest_path" value="" type='text'/>
            </div>
        </div>

    </div>
    <div class="modal-footer">
        <div id="rename-name-required-alert" class="alert-message warning hide" style="position: absolute; left: 10;">

            <p><strong>Sorry, name is required.</strong>
        </div>

        <input id="rename_src_path" type="hidden" name="src_path" type='text'>
        <input type="submit" value="Submit" class="btn primary" />
        <a id="cancel-rename-button" class="btn">Cancel</a>

    </div>
    </form>
</div>

<!-- upload modal -->
<div id="upload-modal" class="modal hide fade">
    <form id="upload-form" action="/filebrowser/rename?next=${current_request_path}" method="POST" enctype="multipart/form-data" class="form-stacked form-padding-fix">
    <div class="modal-header">
        <a href="#" class="close">&times;</a>
        <h3>Uploading to: <span id="upload-dir-name">${current_dir_path}</span></h3>
    </div>
    <div class="modal-body">
        <form action="/filebrowser/upload?next=${current_dir_path}" method="POST" enctype="multipart/form-data" class="form-stacked">
         <div id="file-uploader">
		<noscript>
			<p>Please enable JavaScript to use file uploader.</p>
			<!-- or put a simple form for upload here -->
		</noscript>
	</div>
        </form>

    </div>
    <div class="modal-footer">

    </div>
    </form>
</div>


<!-- create directory modal -->
<div id="create-directory-modal" class="modal hide fade">
    <form id="create-directory-form" action="/filebrowser/mkdir?next=${current_request_path}" method="POST" enctype="multipart/form-data" class="form-stacked form-padding-fix">
    <div class="modal-header">
        <a href="#" class="close">&times;</a>
        <h3>Create Directory</h3>
    </div>
    <div class="modal-body">
        <div class="clearfix">
            <label>Directory Name</label>
            <div class="input">
                <input id="new-directory-name-input" name="name" value="" type='text'/>
                <input type="hidden" name="path" type='text' value="${current_dir_path}"/>
            </div>
        </div>

    </div>
    <div class="modal-footer">
         <div id="directory-name-required-alert" class="alert-message warning hide" style="position: absolute; left: 10;">

            <p><strong>Sorry, directory name is required.</strong>
        </div>
        <input class="btn primary" type="submit" value="Submit" />
        <a id="cancel-create-directory-button" class="btn" href="#">Cancel</a>
    </div>
    </form>
</div>

<!-- create directory modal -->
<div id="change-owner-modal" class="modal hide fade">

</div>
<div id="change-permission-modal" class="modal hide fade">

</div>
<div id="move-modal" class="modal hide fade">

</div>

<script type="text/javascript" charset="utf-8">
    // ajax modal windows
    function openChownWindow(path, user, group, next){
        $.ajax({
            url: '/filebrowser/chown',
            data: {'path':path, 'user':user, 'group' : group, 'next' : next},
            beforeSend: function(xhr){
                xhr.setRequestHeader("X-Requested-With", "Hue");
            },
            dataType: 'html',
            success: function(data){
                $('#change-owner-modal').html(data);
                $('#change-owner-modal').modal('show');
            }
        });
    }

    function openChmodWindow(path, mode, next){

        $.ajax({
            url: '/filebrowser/chmod',
            data: {'path':path, 'mode':mode, 'next' : next},
            beforeSend: function(xhr){
                xhr.setRequestHeader("X-Requested-With", "Hue");
            },
            dataType: 'html',
            success: function(data){
                $('#change-permission-modal').html(data);
                $('#change-permission-modal').modal('show');
            }
        });
    }

    function openMoveModal(src_path, mode, next){

        $.ajax({
            url: '/filebrowser/move',
            data: {'src_path':src_path, 'mode':mode, 'next' : next},
            beforeSend: function(xhr){
                xhr.setRequestHeader("X-Requested-With", "Hue");
            },
            dataType: 'html',
            success: function(data){
                $('#move-modal').html(data);
                $('#move-modal').modal('show');
            }
        });
    }
    //uploader
    var num_of_pending_uploads = 0;
    function createUploader(){
        var uploader = new qq.FileUploader({
            element: document.getElementById('file-uploader'),
            action: '/filebrowser/upload',
            params:{
                dest: '${current_dir_path}',
                fileFieldLabel: 'hdfs_file'
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
    // don't wait for the window to load
    window.onload = createUploader;

	$(document).ready(function(){
		$(".datatables").dataTable({
			"bPaginate": false,
		    "bLengthChange": false,
		    "bFilter": false,
			"bInfo": false
		});
	});

    //delete handlers
    $(".delete").click(function(eventObject){
        $('#file-to-delete-input').attr('value', $(eventObject.target).attr('file-to-delete'));
        $('#delete-form').attr('action', '/filebrowser/' + $(eventObject.target).attr('delete-type') + '?next=' + encodeURI('${current_request_path}') + '&path=' + encodeURI('${path}'));
        $('#delete-modal').modal('show');
    })

    $('#cancel-delete-button').click(function(){
        $('#delete-modal').modal('hide');
    })

    //rename handlers
    $(".rename").click(function(eventObject){
        $('#rename_src_path').attr('value', $(eventObject.target).attr('file-to-rename'));
        $('#rename-file-name').text($(eventObject.target).attr('file-to-rename'));
        $('#rename-modal').modal('show');
    })

    $('#cancel-rename-button').click(function(){
        $('#rename-modal').modal('hide');
    })

    $('#rename-form').submit(function(){
        if($('#new-name-input').val() == ''){
            $('#rename-name-required-alert').show(250);
            return false;
        }
    })

    //upload handlers
    $('.upload-link').click(function(){
        $('#upload-modal').modal('show');
    })

    //create directory handlers
    $('.create-directory-link').click(function(){
        $('#create-directory-modal').modal('show');
    })
    $('#cancel-create-directory-button').click(function(){
        $('#create-directory-modal').modal('hide');
    })
    $('#create-directory-form').submit(function(){

        if($('#new-directory-name-input').val()==''){
            $('#directory-name-required-alert').alert().show(250)
            return false;
        }

    })

    //filter handlers
    $('#filter-input').keyup(function(){
        $.each($('.file-row'), function(index, value) {

          if($(value).attr('file-name').toLowerCase().indexOf($('#filter-input').val().toLowerCase()) == -1 && $('#filter-input').val() != ''){
             // alert('hide: ' + $(value).attr('file-name'));
            $(value).hide(250);
          }else{
            $(value).show(250);
          }
        });

    })

    $('#clear-filter-button').click(function(){
        $('#filter-input').val('');
        $.each($('.file-row'), function(index, value) {
            $(value).show(250);
        });
    })

</script>

</%def>

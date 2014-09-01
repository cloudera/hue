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
  from django.template.defaultfilters import urlencode, stringformat, date, filesizeformat, time
  from filebrowser.views import truncate
  from desktop.views import commonheader, commonfooter
  from django.utils.translation import ugettext as _
%>

<%
  path_enc = urlencode(path)
  dirname_enc = urlencode(dirname)
%>

<%namespace name="edit" file="editor_components.mako" />
<%namespace name="fb_components" file="fb_components.mako" />

${ commonheader(_('%(filename)s - File Viewer') % dict(filename=truncate(filename)), 'filebrowser', user) | n,unicode }
${ fb_components.menubar() }

<div class="container-fluid">
  <div class="row-fluid">
    <div class="span2">
      ${ fb_components.file_sidebar(path_enc, dirname_enc, stats) }
    </div>
    <div class="span10">
      <div class="card card-small">
      % if breadcrumbs:
        ${fb_components.breadcrumbs(path, breadcrumbs)}
      %endif
        <div class="card-body">
          <p>
            <form class="form-stacked" method="post" action="${url('filebrowser.views.save_file')}">
              ${ csrf_token(request) | n,unicode }
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
              <div style="width: 98%; height: 100%;">${edit.render_field(form["contents"], tag="textarea", nolabel=True, notitle=True, attrs=dict(
                style="width:100%; height:400px; resize:none")) | n}</div>
              <input class="btn btn-primary" type="submit" name="save" value="${_('Save')}">
              <a id="saveAsBtn" class="btn">${_('Save as')}</a>
            </form>
          </p>
        </div>
      </div>
    </div>
  </div>
</div>


<div id="saveAsModal" class="modal hide fade">
    <form id="saveAsForm" action="${url('filebrowser.views.save_file')}" method="POST" class="form-stacked form-padding-fix">
    ${ csrf_token(request) | n,unicode }
    <div class="modal-header">
        <a href="#" class="close" data-dismiss="modal">&times;</a>
        <h3>${_('Save as')}</h3>
    </div>
    <div class="modal-body">
        <span class="help-block">${_("Enter the location where you would like to save the file.")}</span>
        ${ edit.render_field(form["path"], notitle=True, nolabel=True, klass="pathChooser input-xxlarge") }
        <br/>
        <div id="fileChooserSaveModal" class="hide"></div>
    </div>
    <div class="modal-footer">
        <div id="saveAsNameRequiredAlert" class="alert-message error hide" style="position: absolute; left: 10;">
            <p><strong>${_('Name is required.')}</strong>
        </div>
        ${edit.render_field(form["contents"], hidden=True)}
        ${edit.render_field(form["encoding"], hidden=True)}
        <a id="cancelSaveAsBtn" class="btn">${_('Cancel')}</a>
        <input type="submit" value="${_('Save')}" class="btn btn-primary" />
    </div>
    </form>
</div>

  <script type="text/javascript" charset="utf-8">
    $(document).ready(function () {
      $("#saveAsBtn").click(function () {
        $("#saveAsModal").modal({
          backdrop: "static",
          keyboard: true,
          show: true
        })
      });

      $("#cancelSaveAsBtn").click(function () {
        $("#saveAsModal").modal("hide");
      });

      $("#saveAsForm").submit(function () {
        if ($.trim($("#saveAsForm").find("input[name='path']").val()) == "") {
          $("#saveAsForm").find("input[name='path']").addClass("fieldError");
          $("#saveAsNameRequiredAlert").show();
          resetPrimaryButtonsStatus(); //globally available
          return false;
        }
        return true;
      });

      $("#saveAsForm").find("input[name='path']").focus(function () {
        $(this).removeClass("fieldError");
        $("#saveAsNameRequiredAlert").hide();
      });

      $(".pathChooser").click(function() {
        var self = this;
        $("#fileChooserSaveModal").jHueFileChooser({
          initialPath:$(self).val(),
          onFileChoose:function (filePath) {
            $(self).val(filePath);
          },
          onFolderChange:function (folderPath) {
            $(self).val(folderPath);
          },
          createFolder:false,
          uploadFile:false
        });
        $("#fileChooserSaveModal").slideDown();
      });

      $("#refreshBtn").click(function(){
        window.location.reload();
      });

      function resizeTextarea() {
        var RESIZE_CORRECTION = 246;
        $("textarea[name='contents']").height( $(window).height() - RESIZE_CORRECTION);
      }

      var _resizeTimeout = -1;
      $(window).on("resize", function () {
        window.clearTimeout(_resizeTimeout);
        _resizeTimeout = window.setTimeout(function () {
          resizeTextarea();
        }, 100);
      });

      resizeTextarea();

    });
  </script>

${ commonfooter(messages) | n,unicode }

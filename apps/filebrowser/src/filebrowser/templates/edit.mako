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

%if not is_embeddable:
${ commonheader(_('%(filename)s - File Viewer') % dict(filename=truncate(filename)), 'filebrowser', user, request) | n,unicode }
${ fb_components.menubar() }
%endif


<div class="container-fluid" style="padding: 0">
  <div class="row-fluid">
    <div class="span12">
      <div class="card card-small">
      % if breadcrumbs and not is_embeddable:
        ${fb_components.breadcrumbs(path, breadcrumbs)}
      %endif
        <div class="card-body">
          <p>
            <form id="saveForm" class="form-stacked" method="post" action="${url('filebrowser_views_save_file')}">
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
              <div style="width: 98%; height: 100%;">${edit.render_field(form["contents"], tag="textarea", nolabel=True, notitle=True, klass="monospace file-editor", attrs=dict(
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
    <form id="saveAsForm" action="${url('filebrowser_views_save_file')}" method="POST" class="form-stacked form-padding-fix">
    ${ csrf_token(request) | n,unicode }
    <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
      <h2 class="modal-title">${ _('Save as') }</h2>
    </div>
    <div class="modal-body" style="max-height: 430px">
        <span class="help-block">${_("Enter the location where you would like to save the file.")}</span>
        ${ edit.render_field(form["path"], notitle=True, nolabel=True, klass="pathChooser input-xxlarge", attrs={ 'style': 'margin-bottom: 0; width: 510px' }) }
        <br/>
        <div id="fileChooserSaveModal" class="hide margin-top-20"></div>
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

  <script type="text/javascript">
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

      $('#saveForm').ajaxForm({
        dataType: 'json',
        success: function (data) {
          if (data && data.exists) {
            resetPrimaryButtonsStatus();
            $.jHueNotify.info(data.path + " ${ _('saved correctly') }")
          }
        }
      });

      $('#saveAsForm').ajaxForm({
        dataType: 'json',
        beforeSubmit: function(data) {
          if ($.trim($("#saveAsForm").find("input[name='path']").val()) == "") {
            $("#saveAsForm").find("input[name='path']").addClass("fieldError");
            $("#saveAsNameRequiredAlert").show();
            resetPrimaryButtonsStatus(); //globally available
            return false;
          }
          // Contents of SaveAs form is not updated. Need to do it manually
          data.forEach(dataUnit => {
            if (dataUnit.name.toLowerCase() === 'contents') {
                dataUnit.value = $('#saveForm textarea').val();
            }
          });
          return true;
        },
        success: function (data) {
          if (data && data.exists) {
            resetPrimaryButtonsStatus();
            $("#saveAsModal").modal("hide");
            $.jHueNotify.info(data.path + " ${ _('saved correctly') }")
          }
        }
      });

      $("#saveAsForm").find("input[name='path']").focus(function () {
        $(this).removeClass("fieldError");
        $("#saveAsNameRequiredAlert").hide();
      });

      function getBrowseButton() {
        var self = $('.pathChooser');
        return $('<a>').addClass('btn').addClass('fileChooserBtn').text('..').click(function (e) {
          e.preventDefault();
          $('#fileChooserSaveModal').jHueFileChooser({
            initialPath: $(self).val(),
            onFileChoose: function (filePath) {
              $(self).val(filePath);
            },
            onFolderChange: function (folderPath) {
              $(self).val(folderPath);
            },
            createFolder: false,
            uploadFile: false
          });
          $('#fileChooserSaveModal').slideDown();
        });

      }

      $('.pathChooser').after(getBrowseButton());


      function resizeTextarea() {
        var RESIZE_CORRECTION = 246;
        $("textarea[name='contents']").height($(window).height() - RESIZE_CORRECTION);
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

%if not is_embeddable:
${ commonfooter(request, messages) | n,unicode }
%endif

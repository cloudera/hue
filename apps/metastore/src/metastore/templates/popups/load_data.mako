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

<%namespace name="comps" file="../components.mako" />

<form method="POST" class="form-horizontal" id="load-data-form" onsubmit="return false;">
    ${ csrf_token(request) | n,unicode }
    <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
      <h2 class="modal-title">${_('Import Data')}</h2>
    </div>
    <div class="modal-body">
        <input id="load_data_is_embeddable" type="hidden" name="is_embeddable" value="false">
        <input id="load_data_source_type" type="hidden" name="source_type" value="${ source_type }">
        <input type="hidden" name="start_time" value=""/>

        <div class="control-group">
            ${comps.bootstrapLabel(load_form["path"])}
            <div class="controls">
                ${comps.field(load_form["path"], placeholder="/user/user_name/data_dir/file", klass="pathChooser input-xlarge", file_chooser=True, show_errors=True)}
            </div>
        </div>

        <div id="filechooser"></div>

        % for pf in load_form.partition_columns:
            <div class="control-group">
                 ${comps.bootstrapLabel(load_form[pf])}
                 <div class="controls">
                   ${comps.field(load_form[pf], render_default=True, attrs={'klass': 'input-xxlarge'})}
                </div>
            </div>
        % endfor

        <div class="control-group">
          <div class="controls">
            <label class="checkbox inline-block">
                <input type="checkbox" name="overwrite"/> ${_('Overwrite existing data')}
              </label>
            </div>
        </div>

        <p class="alert alert-warning">${_("Note that loading data will move data from its location into the table's storage location.")}</p>
        <p id="load-data-error" class="alert alert-error hide"></p>
    </div>

    <div class="modal-footer">
        <a href="#" class="btn" data-dismiss="modal">${_('Cancel')}</a>
        <button class="btn btn-primary" id="load-data-submit-btn" disabled="disabled">${_('Submit')}</button>
    </div>
</form>


<style type="text/css">
   #filechooser {
     display: none;
     min-height: 100px;
     height: 380px;
     overflow-y: auto;
     margin-top: 10px;
   }

   .modal-body {
     max-height: 540px;
   }

   .form-horizontal .controls {
     margin-left: 0;
   }

   .form-horizontal .control-label {
     width: auto;
     padding-right: 10px;
   }
</style>

<script type="text/javascript">
  $(document).ready(function () {
    $(".fileChooserBtn").click(function (e) {
      e.preventDefault();
      var _destination = $(this).attr("data-filechooser-destination");
      $("#filechooser").jHueFileChooser({
        initialPath: $("input[name='" + _destination + "']").val(),
        onFileChoose: function (filePath) {
          $("input[name='" + _destination + "']").val(filePath);
          toggleLoadBtn($("input[name='" + _destination + "']"));
          $("#filechooser").slideUp();
        },
        onFolderChange: function (filePath) {
          $("input[name='" + _destination + "']").val(filePath);
        },
        onFolderChoose: function (filePath) {
          $("input[name='" + _destination + "']").val(filePath);
          $("#filechooser").slideUp();
        },
        createFolder: false,
        selectFolder: true,
        uploadFile: true
      });
      $("#filechooser").slideDown();
    });

    var _keydownTimeout = -1;
    $("input[name='" + $(".fileChooserBtn").data("filechooser-destination") + "']").on("keydown", function () {
      window.clearTimeout(_keydownTimeout);
      var _fld = $(this);
      window.setTimeout(function () {
        toggleLoadBtn(_fld);
      }, 300)
    });

    function toggleLoadBtn(fld) {
      $("#load-data-submit-btn").attr("disabled", "disabled");
      if ($.trim(fld.val()) != "") {
        $("#load-data-submit-btn").removeAttr("disabled");
      }
    }

    $("#load-data-submit-btn").click(function (e) {
      $("#load_data_is_embeddable").val("true");
      $("#load-data-form").find('input[name=start_time]').val(ko.mapping.toJSON(new Date().getTime()));
      $.post("${ url('metastore:load_table', database=database, table=table.name) }",
        $("#load-data-form").serialize(),
        function (response) {
          if (response['status'] != 0) {
            if (response['status'] == 1) {
              $('#load-data-error').html(response['data']);
              $('#load-data-error').show();
            } else {
              $('#import-data-modal').html(response['data']);
            }
          } else {
            huePubSub.publish('notebook.task.submitted', response.history_uuid);
            $("#import-data-modal").modal("hide");
          }
        }
      ).always(function () {
        $("#load-data-submit-btn").button('reset');
        $("#load-data-submit-btn").removeAttr("disabled");
      });
    });
  });
</script>

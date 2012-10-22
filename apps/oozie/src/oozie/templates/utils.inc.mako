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


#
# Include this in order to use the functions:
# <%namespace name="utils" file="utils.inc.mako" />
#


<%!
  import time

  from django.template.defaultfilters import date, time as dtime
  from django.utils.translation import ugettext as _

  from desktop.lib.view_util import format_duration_in_millis
  from hadoop.fs.hadoopfs import Hdfs
  from liboozie.utils import format_time
%>


<%def name="is_selected(section, matcher)">
  <%
    if section == matcher:
      return "active"
    else:
      return ""
  %>
</%def>


<%def name="job_duration(job)">
  <%
    if job.endTime and job.startTime:
      return ( time.mktime(job.endTime) - time.mktime(job.startTime) ) * 1000
    else:
      return None
  %>
</%def>


<%def name="format_job_duration(job)">
  <%
    duration = job_duration(job)
    if duration is not None:
      return format_duration_in_millis(duration)
    else:
      return None
  %>
</%def>


<%def name="format_date(python_date)">
  <%
    try:
      return format_time(python_date)
    except:
      return '%s %s' % (date(python_date), dtime(python_date).replace("p.m.","PM").replace("a.m.","AM"))
  %>
</%def>


<%def name="format_time(st_time)">
  % if st_time is None:
    -
  % else:
    ${ time.strftime("%a, %d %b %Y %H:%M:%S", st_time) }
  % endif
</%def>


<%def name="hdfs_link(url)">
  % if url:
    <% path = Hdfs.urlsplit(url)[2] %>
    % if path:
      <a href="/filebrowser/view${path}">${ url }</a>
    % else:
      ${ url }
    % endif
  % else:
      ${ url }
  % endif
</%def>


<%def name="display_conf(configs)">
  <table class="table table-condensed table-striped">
    <thead>
      <tr>
        <th>${ _('Name') }</th>
        <th>${ _('Value') }</th>
      </tr>
    </thead>
    <tbody>
      % for name, value in sorted(configs.items()):
        <tr>
          <td>${ name }</td>
          <td>
            ${ guess_hdfs_link(name, str(value)) }
          </td>
        </tr>
      % endfor
    </tbody>
  </table>
</%def>


<%def name="guess_hdfs_link(name, path)">
  <%
    if name.endswith('dir') or name.endswith('path') or path.startswith('/') or path.startswith('hdfs://'):
      return hdfs_link(path)
    else:
      return path
    endif
  %>
</%def>


<%def name="if_true(cond, return_value, else_value='')">
  <%
    if cond:
      return return_value
    else:
      return else_value
    endif
  %>
</%def>


<%def name="if_false(cond, return_value)">
  ${ if_true(not cond, return_value)}
</%def>


<%def name="get_status(status)">
   % if status in ('SUCCEEDED', 'OK'):
     label-success
   % elif status in ('RUNNING', 'PREP', 'WAITING', 'SUSPENDED', 'PREPSUSPENDED', 'PREPPAUSED', 'PAUSED'):
      label-warning
   % elif status == 'READY':
      label-success
   % else:
      label-important
   % endif
</%def>


<%def name="render_field(field, show_label=True)">
  % if not field.is_hidden:
    <% group_class = field.errors and "error" or "" %>
    <div class="control-group ${group_class}"
      rel="popover" data-original-title="${ field.label }" data-content="${ field.help_text }">
      % if show_label:
        <label class="control-label">${ field.label | h }</label>
      % endif
      <div class="controls">
        ${ field }
        % if field.errors:
          <span class="help-inline">${ unicode(field.errors) }</span>
        % endif
      </div>
    </div>
  %endif
</%def>


<%def name="render_constant(label, value)">
  <div class="control-group">
    <label class="control-label">${ label | h }</label>
    <div class="controls">
      <div style="padding-top:4px">
      ${ value }
      </div>
    </div>
  </div>
</%def>


<%def name="path_chooser_libs(select_folder=False)">
  <div id="chooseFile" class="modal hide fade">
    <div class="modal-header">
      <a href="#" class="close" data-dismiss="modal">&times;</a>
      <h3>${ _('Choose a') } ${ if_true(select_folder, _('folder'), _('file')) }</h3>
    </div>
    <div class="modal-body">
      <div id="fileChooserModal">
      </div>
    </div>
    <div class="modal-footer">
    </div>
  </div>

  <script type="text/javascript" charset="utf-8">
    $(document).ready(function(){
      $(".pathChooser").each(function(){
        var self = $(this);
        self.after(getFileBrowseButton(self));
      });

      function getFileBrowseButton(inputElement) {
        return $("<button>").addClass("btn").addClass("fileChooserBtn").text("..").click(function(e){
          e.preventDefault();
          // check if it's a relative path
          var pathAddition = "";
          if ($.trim(inputElement.val()) != ""){
            $.getJSON("/filebrowser/chooser${ workflow.deployment_dir }" + inputElement.val(), function (data) {
              pathAddition = "${ workflow.deployment_dir }";
              callFileChooser();
            }).error(function(){
              callFileChooser();
            });
          }
          else {
            callFileChooser();
          }

          function callFileChooser() {
            $("#fileChooserModal").jHueFileChooser({
              % if select_folder:
              selectFolder: true,
              onFolderChoose: function(filePath) {
              % else:
              onFileChoose: function(filePath) {
              % endif
                if (filePath.indexOf("${ workflow.deployment_dir }") > -1){
                  filePath = filePath.substring("${ workflow.deployment_dir }".length);
                  if (filePath == ""){
                    filePath = "/";
                  }
                }
                inputElement.val(filePath);
                inputElement.change();
                $("#chooseFile").modal("hide");
              },
              createFolder: false,
              uploadFile: false,
              initialPath: $.trim(inputElement.val()) != "" ? pathAddition + inputElement.val() : "${ workflow.deployment_dir }",
              errorRedirectPath: "${ workflow.deployment_dir }"
            });
            $("#chooseFile").modal("show");
          }
        });
      }
    });
  </script>
</%def>


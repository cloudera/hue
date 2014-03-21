## -*- coding: utf-8 -*-
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
  import posixpath
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
      % if path.startswith(posixpath.sep):
        <a href="/filebrowser/view${path}">${ url }</a>
      % else:
        <a href="/filebrowser/home_relative_view/${path}">${ url }</a>
      % endif
    % else:
      ${ url }
    % endif
  % else:
      ${ url }
  % endif
</%def>

<%def name="hdfs_link_js(url)">
  % if url:
    <% path = Hdfs.urlsplit(url)[2] %>
    % if path:
      % if path.startswith(posixpath.sep):
        /filebrowser/view${path}
      % else:
        /filebrowser/home_relative_view/${path}
      % endif
    % else:
      javascript:void(0)
    % endif
  % else:
    javascript:void(0)
  % endif
</%def>


<%def name="display_conf(configs, id=None)">
  <table class="table table-condensed table-striped"
    % if id is not None:
      id="${ id }"
    % endif
  >
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
    import re

    if re.search('(dir|path|output|input)', name, re.I) or path.startswith('/') or path.startswith('hdfs://'):
      return hdfs_link(path)
    else:
      return path
    endif
  %>
</%def>

<%def name="is_linkable(name, path)">
  <%
    import re

    if re.search('(dir|path|output|input)', name, re.I) or path.startswith('/') or path.startswith('hdfs://'):
      return True
    else:
      return False
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
   % if status in ('SUCCEEDED', 'OK', 'NORMAL', 'DONE'):
     label-success
   % elif status in ('RUNNING', 'PREP', 'WAITING', 'SUSPENDED', 'PREPSUSPENDED', 'PREPPAUSED', 'PAUSED', 'STARTED', 'FINISHING'):
      label-warning
   % elif status == 'READY':
      label-success
   % else:
      label-important
   % endif
</%def>


<%def name="render_field(field, show_label=True, extra_attrs={}, control_extra='')">
  % if not field.is_hidden:
    <% group_class = field.errors and "error" or "" %>
    <div class="control-group ${group_class}"
      rel="popover" data-original-title="${ field.label }" data-content="${ field.help_text }" ${control_extra}>
      % if show_label:
        <label class="control-label">${ field.label }</label>
      % endif
      <div class="controls"
      % if not show_label:
        style="margin-left: 0"
      % endif
              >
        <% field.field.widget.attrs.update(extra_attrs) %>
        ${ field | n,unicode }
        % if field.errors:
          <span class="help-inline">${ field.errors | n,unicode }</span>
        % endif
      </div>
    </div>
  %endif
</%def>

<%def name="render_field_no_popover(field, show_label=True, extra_attrs={})">
  % if not field.is_hidden:
    <% group_class = field.errors and "error" or "" %>
    <div class="control-group ${group_class}">
    % if show_label:
        <label class="control-label">${ field.label }</label>
    % endif
    <div class="controls">
    <% field.field.widget.attrs.update(extra_attrs) %>
    ${ field | n,unicode }
    % if field.errors:
        <span class="help-inline">${ field.errors | n,unicode }</span>
    % endif
    % if field.help_text:
        <span class="help-block">${ field.help_text }</span>
    % endif
    </div>
    </div>
  %endif
</%def>


<%def name="render_field_with_error_js(field, error_name, show_label=True, extra_attrs={})">
  % if not field.is_hidden:
    <div class="control-group" rel="popover" data-original-title="${ field.label }" data-content="${ field.help_text }" data-bind="attr: {'class': ( errors.${ error_name }().length > 0 ) ? 'control-group error' : 'control-group'}">
      % if show_label:
        <label class="control-label">${ field.label }</label>
      % endif
      <div class="controls">
        <% field.field.widget.attrs.update(extra_attrs) %>
        ${ field | n,unicode }
        <ul class="help-inline" data-bind="foreach: errors.${ error_name }()">
          <li class="error" data-bind="html: $data"></li>
        </ul>
      </div>
    </div>
  %endif
</%def>


<%def name="slaForm()">
  <div data-bind="foreach: { 'data': sla, 'afterRender': addSLATextAndPlaceholder }">
    <div class="control-group control-row" style="margin-bottom: 2px">
      <label class="control-label" style="text-align: left"></label>
      <div class="controls">
        <!-- ko if:  key() == 'enabled' -->
        <input type="checkbox" data-bind="checked: value"/>
        <!-- /ko -->
        <!-- ko if:  key() != 'enabled' -->
        <input type="text" data-bind="value: value" class="span7">
        <!-- /ko -->
      </div>
    </div>
  </div>
</%def>


## Would be nice include it in slaForm() somehow
<%def name="slaGlobal()">
  function addSLATextAndPlaceholder(elements, $data) {
    var SLA_TEXT = {
      'enabled': {'niceName': '${ _("Enable") }', 'placeHolder': ''},
      'nominal-time': {'niceName': '${ _("Nominal time") } *', 'placeHolder': '${"$"}{nominal_time}'},
      'should-start': {'niceName': '${ _("Should start") }', 'placeHolder': '${"$"}{10 * MINUTES}'},
      'should-end': {'niceName': '${ _("Should end") } *', 'placeHolder': '${"$"}{30 * MINUTES}'},
      'max-duration': {'niceName': '${ _("Max duration") }', 'placeHolder': '${"$"}{30 * MINUTES}'},
      'alert-events': {'niceName': '${ _("Alert events") }', 'placeHolder': 'start_miss,end_miss,duration_miss'},
      'alert-contact': {'niceName': '${ _("Alert contact") }', 'placeHolder': 'joe@example.com,bob@example.com'},
      'notification-msg': {'niceName': '${ _("Notification message") }', 'placeHolder': '${ _("My Job has encountered an SLA event!") }'},
      'upstream-apps': {'niceName': '${ _("Upstream apps") }', 'placeHolder': 'dependent-app-1, dependent-app-2'}
    };
    var text = SLA_TEXT[$data.key()];
    if (text) {
      $(elements).find('input').attr('placeholder', text.placeHolder);
      $(elements).find('.control-label').text(text.niceName);
    } else {
      $(elements).find('input').attr('placeholder', '');
      $(elements).find('.control-label').text('');
    }
  }
</%def>


<%def name="render_constant(label, value)">
  <div class="control-group">
    <label class="control-label">${ label }</label>
    <div class="controls">
      <div style="padding-top:4px">
      ${ value }
      </div>
    </div>
  </div>
</%def>


<%def name="path_chooser_libs(select_folder=False, skip_init=False)">
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

      $("*").on("focusin", false); //fixes an infinite loop on Firefox

      % if not skip_init:
        $(".pathChooser").each(function(){
          var self = $(this);
          % if select_folder:
              self.after(getFileBrowseButton(self, true));
          % else:
              self.after(getFileBrowseButton(self));
          % endif
        });
      % endif
    });

    function getFileBrowseButton(inputElement, selectFolder) {
      return $("<button>").addClass("btn").addClass("fileChooserBtn").text("..").click(function (e) {
        e.preventDefault();
        // check if it's a relative path
        var pathAddition = "";
        if ($.trim(inputElement.val()) != "") {
          var checkPath = "/filebrowser/chooser${ workflow.deployment_dir }" + "/" + inputElement.val();
          $.getJSON(checkPath, function (data) {
            pathAddition = "${ workflow.deployment_dir }/";
            callFileChooser();
          }).error(function () {
            callFileChooser();
          });
        }
        else {
          callFileChooser();
        }

        function callFileChooser() {
          $("#fileChooserModal").jHueFileChooser({
            selectFolder:(selectFolder) ? true : false,
            onFolderChoose:function (filePath) {
              handleChoice(filePath);
              if (selectFolder) {
                $("#chooseFile").modal("hide");
              }
            },
            onFileChoose:function (filePath) {
              handleChoice(filePath);
              $("#chooseFile").modal("hide");
            },
            createFolder:false,
            uploadFile:true,
            initialPath:$.trim(inputElement.val()) != "" ? pathAddition + inputElement.val() : "${ workflow.deployment_dir }",
            errorRedirectPath:"",
            forceRefresh:true
          });
          $("#chooseFile").modal("show");
        }

        function handleChoice(filePath) {
          if (filePath.indexOf("${ workflow.deployment_dir }") > -1) {
            filePath = filePath.substring("${ workflow.deployment_dir }".length + 1);
            if (filePath == "") {
              filePath = "./";
            }
            if (filePath.indexOf("//") == 0){
              filePath = filePath.substr(1);
            }
          }
          inputElement.val(filePath);
          inputElement.change();
        }
      });
    }
  </script>
</%def>


<%def name="decorate_datetime_fields(is_range=True)">

  <link rel="stylesheet" href="/static/ext/css/bootstrap-datepicker.min.css" type="text/css" media="screen" title="no title" charset="utf-8" />
  <link rel="stylesheet" href="/static/ext/css/bootstrap-timepicker.min.css" type="text/css" media="screen" title="no title" charset="utf-8" />

  <style type="text/css">
    .datepicker {
      z-index: 4999;
    }
  </style>

  <script src="/static/ext/js/moment.min.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/ext/js/bootstrap-datepicker.min.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/ext/js/bootstrap-timepicker.min.js" type="text/javascript" charset="utf-8"></script>

  <script type="text/javascript" charset="utf-8">

    var DATE_FORMAT = "MM/DD/YYYY";
    var TIME_FORMAT = "hh:mm A";
    var DATETIME_FORMAT = DATE_FORMAT + " " + TIME_FORMAT;

    function decorateDateTime () {
      $(".date:not('.input-append')").each(function () {
        $(this).removeClass("date").addClass("dateInput").wrap($("<div>").addClass("input-append").addClass("date").css("marginRight", "8px"));
        $(this).parent().data("date", $(this).val());
        $("<span>").addClass("add-on").html('<i class="fa fa-th"></i>').appendTo($(this).parent());
      });

      $("input[name='end_0']").data("original-val", $("input[name='end_0']").val());

      $(".dateInput").parent().datepicker({
        format:DATE_FORMAT.toLowerCase()
      });

      $(".dateInput").on("change", function () {
        var _this = $(this);
        var startDate = moment(_this.val() + " " + _this.parent().parent().find(".timepicker-default").val(), DATETIME_FORMAT);
        _this.parent().datepicker('setValue', startDate.format(DATE_FORMAT));
        %if is_range:
          rangeHandler(_this.attr("name").indexOf("start") > -1);
        %endif
      });

      $("input[name='start_0']").parent().datepicker().on("changeDate", function () {
        rangeHandler(true);
      });

      $("input[name='end_0']").parent().datepicker().on("changeDate", function () {
        rangeHandler(false);
      });

      $(".time:not('.input-append')").each(function () {
        $(this).attr("class", "input-mini timepicker-default").wrap($("<div>").addClass("input-append").addClass("date").addClass("bootstrap-timepicker-component"));
        $("<span>").addClass("add-on").html('<i class="fa fa-clock-o"></i>').appendTo($(this).parent());
      });

      $(".timepicker-default").timepicker({
        defaultTime:"value"
      });

      $("input[name='start_1']").on("change", function (e) {
        // the timepicker plugin doesn't have a change event handler
        // so we need to wait a bit to handle in with the default field event
        window.setTimeout(function () {
          rangeHandler(true)
        }, 200);
      });

      $("input[name='end_1']").on("change", function () {
        window.setTimeout(function () {
          rangeHandler(true)
        }, 200);
      });

      function rangeHandler(isStart) {
        var startDate = moment($("input[name='start_0']").val() + " " + $("input[name='start_1']").val(), DATETIME_FORMAT);
        var endDate = moment($("input[name='end_0']").val() + " " + $("input[name='end_1']").val(), DATETIME_FORMAT);
        if (startDate.valueOf() > endDate.valueOf()) {
          if (isStart) {
            $("input[name='end_0']").val(startDate.format(DATE_FORMAT));
            $("input[name='end_0']").parent().datepicker('setValue', startDate.format(DATE_FORMAT));
            $("input[name='end_0']").data("original-val", $("input[name='end_0']").val());
            $("input[name='end_1']").val(startDate.format(TIME_FORMAT));
          }
          else {
            if ($("input[name='end_0']").val() == $("input[name='start_0']").val()) {
              $("input[name='end_1']").val(startDate.format(TIME_FORMAT));
              $("input[name='end_1']").data("timepicker").setValues(startDate.format(TIME_FORMAT));
            }
            else {
              $("input[name='end_0']").val($("input[name='end_0']").data("original-val"));
              $("input[name='end_0']").parent().datepicker("setValue", $("input[name='end_0']").data("original-val"));
            }
            // non-sticky error notification
            $.jHueNotify.notify({
              level:"ERROR",
              message:"${ _("The end cannot be before the starting moment") }"
            });
          }
        }
        else {
          $("input[name='end_0']").data("original-val", $("input[name='end_0']").val());
          $("input[name='start_0']").parent().datepicker("hide");
          $("input[name='end_0']").parent().datepicker("hide");
        }
      }
    }

    $(document).ready(function(){
      decorateDateTime();
    });
  </script>

</%def>

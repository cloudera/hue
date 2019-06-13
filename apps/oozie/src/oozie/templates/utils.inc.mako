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
  import logging
  import posixpath
  import time

  from django.template.defaultfilters import date, time as dtime
  from django.utils.translation import ugettext as _

  from desktop.lib.view_util import format_duration_in_millis
  from hadoop.fs.hadoopfs import Hdfs
  from liboozie.utils import format_time

  LOG = logging.getLogger(__name__)
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
      LOG.exception('failed to format time: %s' % python_date)
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
        <a href="/filebrowser/view=${path}">${ url }</a>
      % else:
        <a href="/filebrowser/home_relative_view=/${path}">${ url }</a>
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
        /filebrowser/view=${path}
      % else:
        /filebrowser/home_relative_view=/${path}
      % endif
    % else:
      javascript:void(0)
    % endif
  % else:
    javascript:void(0)
  % endif
</%def>


<%def name="display_conf(configs, id=None)">
  <table class="table table-condensed"
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
            ${ guess_hdfs_link(name, unicode(value)) }
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
      <!-- ko if:  key() == 'enabled' -->
      <label class="checkbox" style="text-align: left"><span class="control-label"></span> <input type="checkbox" data-bind="checked: value"/></label>
      <!-- /ko -->
      <!-- ko if:  key() != 'enabled' -->
      <span data-bind="visible: ko.utils.arrayFilter($parent.sla(), function(item) { return item.key() == 'enabled' && item.value()==true }).length == 1">
      <label class="control-label" style="text-align: left"></label>
      <div class="controls">
        <input type="text" data-bind="value: value" class="span7">
      </div>
      </span>
      <!-- /ko -->
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
  <div id="chooseFileModal" class="modal hide fade">
    <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
      <h2 class="modal-title">${ _('Choose a') } ${ if_true(select_folder, _('folder'), _('file')) }</h2>
    </div>
    <div class="modal-body">
      <div id="fileChooserModal">
      </div>
    </div>
    <div class="modal-footer">
    </div>
  </div>

  <script type="text/javascript">
    $(document).ready(function(){

      $("*").on("focusin", false); //fixes an infinite loop on Firefox

      % if not skip_init:
        $(".pathChooser").each(function(){
          var self = $(this);
          % if select_folder:
              self.after(hueUtils.getFileBrowseButton(self, true));
          % else:
              self.after(hueUtils.getFileBrowseButton(self));
          % endif
        });
      % endif
    });
  </script>
</%def>


<%def name="decorate_datetime_fields(is_range=True)">

  <link rel="stylesheet" href="${ static('desktop/ext/css/bootstrap-datepicker.min.css') }" type="text/css" media="screen" title="no title" charset="utf-8" />
  <link rel="stylesheet" href="${ static('desktop/ext/css/bootstrap-timepicker.min.css') }" type="text/css" media="screen" title="no title" charset="utf-8" />

  <style type="text/css">
    .datepicker {
      z-index: 4999;
    }
  </style>

  <script src="${ static('desktop/ext/js/bootstrap-datepicker.min.js') }" type="text/javascript" charset="utf-8"></script>
  <script src="${ static('desktop/ext/js/bootstrap-timepicker.min.js') }" type="text/javascript" charset="utf-8"></script>

  <script type="text/javascript">

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

<%def name="cron_js()">
var cron_i18n = {
    empty: '${_('-all-')}',
    name_minute: '${_('minute')}',
    name_hour: '${_('hour')}',
    name_day: '${_('day')}',
    name_week: '${_('week')}',
    name_month: '${_('month')}',
    name_year: '${_('year')}',
    text_period: '${_('Every')} <b />',
    text_mins: ' ${_('at')} <b /> ${_('minutes past the hour')}',
    text_time: ' ${_('at')} <b />:<b />',
    text_dow: ' ${_('on')} <b />',
    text_month: ' ${_('of')} <b />',
    text_dom: ' ${_('on the')} <b />',
    error1: '${_('The tag %s is not supported !')}',
    error2: '${_('Bad number of elements')}',
    error3: '${_('The jquery_element should be set into jqCron settings')}',
    error4: '${_('Unrecognized expression')}',
    weekdays: ['${_('sunday')}', '${_('monday')}', '${_('tuesday')}', '${_('wednesday')}', '${_('thursday')}', '${_('friday')}', '${_('saturday')}'],
    months: ['${_('january')}', '${_('february')}', '${_('march')}', '${_('april')}', '${_('may')}', '${_('june')}', '${_('july')}', '${_('august')}', '${_('september')}', '${_('october')}', '${_('november')}', '${_('december')}']
}
function renderCrons() {
    $(".cron-frequency").each(function(){
      var _val = $(this).find(".value");
      $(this).data("originalValue", _val.val());
      _val.jqCron({
        texts: {
          i18n: cron_i18n // comes from utils.inc.mako
        },
        readonly: true,
        enabled_minute: false,
        multiple_dom: true,
        multiple_month: true,
        multiple_mins: true,
        multiple_dow: true,
        multiple_time_hours: true,
        multiple_time_minutes: false,
        default_period: 'day',
        default_value: _val.val(),
        no_reset_button: true,
        lang: 'i18n'
      })
      .jqCronGetInstance();
      var _container = $(this).find(".jqCron-container");
      if (_container.hasClass("jqCron-error")){
        _container.parent().text($(this).data("originalValue"));
      }
    });
}
</%def>

<%def name="submit_popup_event()">
  <script type="text/javascript">
    $(document).ready(function () {
      $(document).off('showSubmitPopup');
      $(document).on('showSubmitPopup', function (event, data) {
        $('.submit-modal').html(data);
        $('.submit-modal').modal('show');
        $('.submit-modal').on('hidden', function () {
          huePubSub.publish('hide.datepicker');
        });
        var _sel = $('.submit-form .control-group[rel!="popover"]:visible');
        if (_sel.length > 0) {
          $('.submit-modal .modal-body').height($('.submit-modal .modal-body').height() + 60);
        }
      });
    });
  </script>
</%def>

<%def name="bulk_dashboard_functions()">

<div id="bulkConfirmation" class="modal hide">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
    <h2 class="modal-title">${ _('Do you really want to kill the selected jobs?') }</h2>
  </div>
  <div class="modal-footer">
    <a href="#" class="btn" data-dismiss="modal">${_('No')}</a>
    <a class="btn btn-danger disable-feedback" href="javascript:void(0);">${_('Yes')}</a>
  </div>
</div>

<script type="text/javascript">

  $(document).ready(function(){
    $(".bulkToolbarBtn").on("click", function(){
      if ($(this).data("operation") == "kill"){
        bulkOperationConfirmation($(this).data("operation"));
      }
      else {
        bulkOperation($(this).data("operation"));
        $(".btn-toolbar").find(".loader").removeClass("hide");
        $(".bulkToolbarBtn").hide();
      }
    });

    function toggleBulkButtons() {
      if ($(".hue-checkbox.fa-check:not(.select-all)").length > 0){
        var _allResume = true;
        var _allSuspended = true;
        $(".hue-checkbox.fa-check:not(.select-all)").each(function(){
          if (['RUNNING', 'PREP', 'WAITING'].indexOf($(this).parents("tr").find(".label").text()) > -1){
            _allResume = false;
          }
          else {
            _allSuspended = false;
          }
        });
        if (! _allResume) {
          $(".bulk-suspend").removeAttr("disabled");
        }
        if (! _allSuspended) {
          $(".bulk-resume").removeAttr("disabled");
        }
        $(".bulk-kill").removeAttr("disabled");
      }
      else {
        $(".bulkToolbarBtn").attr("disabled", "disabled");
      }
    }

    $("#bulkConfirmation").modal({
      show: false
    });

    function bulkOperationConfirmation(what){
      $("#bulkConfirmation").modal("show");
      $("#bulkConfirmation a.btn-danger").off("click");
      $("#bulkConfirmation a.btn-danger").on("click", function(){
        $(".btn-toolbar").find(".loader").removeClass("hide");
        $(".bulkToolbarBtn").hide();
        bulkOperation(what);
        $("#bulkConfirmation").modal("hide");
      });
    }

    function bulkOperation(what) {
      var _ids = [];
      $(".hue-checkbox.fa-check:not(.select-all)").each(function(){
        _ids.push($(this).parents("tr").find("a[data-row-selector='true']").text());
      });

      $.post("${ url('oozie:bulk_manage_oozie_jobs') }",
        {
          "job_ids": _ids.join(" "),
          "action": what
        },
        function (response) {
          ## we get this from each dashboard page
          refreshRunning();
          var _messages = {
            suspend: "${ _('The selected jobs have been suspended correctly.') }",
            suspendErrors: "${ _('Some of the selected jobs may not have been suspended correctly:') }",
            resume: "${ _('The selected jobs have been resumed correctly.') }",
            resumeErrors: "${ _('Some of the selected jobs may not have been resumed correctly:') }",
            kill: "${ _('The selected jobs have been killed correctly.') }",
            killErrors: "${ _('Some of the selected jobs may not have been killed correctly:') }"
          }
          if (response.totalErrors > 0){
            $.jHueNotify.warn(_messages[what + "Errors"] + " " + response.messages);
          }
          else {
            $.jHueNotify.info(_messages[what]);
          }
          $(".hue-checkbox").removeClass("fa-check");
          toggleBulkButtons();
          $(".btn-toolbar").find(".loader").addClass("hide");
          $(".bulkToolbarBtn").show();
      });
    }

    $(document).on("click", ".hue-checkbox", function(){
      var _check = $(this);
      if (_check.hasClass("select-all")){
        if (_check.hasClass("fa-check")){
          $(".hue-checkbox").removeClass("fa-check");
        }
        else {
          $(".hue-checkbox").addClass("fa-check");
        }
      }
      else {
        if (_check.hasClass("fa-check")){
          _check.removeClass("fa-check");
        }
        else {
          _check.addClass("fa-check");
        }
      }
      toggleBulkButtons();
    });

    toggleBulkButtons();
  });

</script>
</%def>


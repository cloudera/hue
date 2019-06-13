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

<%namespace name="utils" file="../utils.inc.mako" />

<link rel="stylesheet" href="${ static('oozie/css/common-editor.css') }">

<form action="${ action }" method="POST" class="form submit-form">
  ${ csrf_token(request) | n,unicode }
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
    % if header:
      <h2 class="modal-title">${header}</h2>
    % else:
      <h2 class="modal-title">${ _('Submit %(job)s?') % {'job': name} }</h2>
    % endif
  </div>
  <div class="modal-body">

      <div id="param-container">

       ${ params_form.management_form | n,unicode }

       % for form in params_form.forms:
          % for hidden in form.hidden_fields():
            ${ hidden | n,unicode }
          % endfor

          <div class="control-group"
            % if form['name'].form.initial.get('name').startswith('oozie.'):
                style="display: none"
            % endif
          >
            <label class="control-label">${ form['name'].form.initial.get('name') }</label>
            <div class="controls">
              ${ utils.render_field(form['value'], show_label=False, extra_attrs={'class': 'filechooser-input input-xlarge'}) }
              <div class="btn-group">
                <a class="btn btn-default dropdown-toggle" data-toggle="dropdown">
                  <i class="fa fa-calendar"></i>
                  <span class="caret"></span>
                </a>
                <ul class="dropdown-menu pull-right" role="menu">
                  <li>
                    <a class="pointer now-link">
                      ${ _('Now') }
                    </a>
                    <a class="pointer calendar-link">
                      ${ _('Calendar') }
                    </a>
                  </li>
                </ul>
              </div>
            </div>
          </div>

         % endfor
      </div>
      <div class="clearfix"></div>

      % if show_dryrun:
         <label class="checkbox" style="display: inline-block; margin-top: 5px">
           <input type="checkbox" name="dryrun_checkbox" /> ${ _('Do a dryrun before submitting the job') }
         </label>
      % endif
      % if is_oozie_mail_enabled:
        <br/>
        <label class="checkbox" style="display: inline-block; margin-top: 5px">
          <input type="checkbox" name="email_checkbox"
          % if not email_id:
            disabled
          % endif
          />
        % if email_id:
          ${_('Send completion email to ')}<a href="/useradmin/users/edit/${user.username}#step2"> ${email_id} </a>
        % else:
          ${_('Email not set in ')}<a href="/useradmin/users/edit/${user.username}#step2"> ${_('profile.')} </a>
        % endif
        % if cluster_json:
          <input type="hidden" name="cluster" value="${ cluster_json }"></input>
        % endif
        </label>
        %endif       
      % if return_json:
        <input type="hidden" name="format" value="json">
      % endif
  </div>
  <div class="modal-footer">
    <a href="#" class="btn" data-dismiss="modal">${ _('Cancel') }</a>
    <input id="submit-btn" type="submit" class="btn btn-primary" value="${ _('Submit') }"/>
  </div>
</form>


<link rel="stylesheet" href="${ static('desktop/ext/css/bootstrap-datepicker.min.css') }" type="text/css" media="screen" title="no title" charset="utf-8" />
<link rel="stylesheet" href="${ static('desktop/ext/css/bootstrap-timepicker.min.css') }" type="text/css" media="screen" title="no title" charset="utf-8" />

<style type="text/css">
  .datepicker {
    z-index: 4999;
  }
  #param-container input[type="text"].filechooser-input.input-xlarge {
    width: 450px;
  }
  #param-container .control-group {
    float: left;
  }
  #param-container .btn-group {
    margin-left: 10px;
  }
</style>

<script src="${ static('desktop/ext/js/bootstrap-datepicker.min.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/bootstrap-timepicker.min.js') }" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript">
  $('.submit-form .filechooser-input').each(function(){
    $(this).after(hueUtils.getFileBrowseButton($(this), true, null, true));
  });

  $(".now-link").on("click", function(){
    $(this).parents(".controls").find("input[type='text']").val(moment().format("YYYY-MM-DD[T]HH:mm"));
  });

  $(".calendar-link").on("click", function () {
    var DATE_FORMAT = "YYYY-MM-DD";
    var _el = $(this).parents(".controls").find("input[type='text']");
    _el.off("keyup");
    _el.on("keyup", function () {
      _el.data("lastValue", _el.val());
    });
    _el.data("lastValue", _el.val());
    _el.datepicker({
      format: DATE_FORMAT.toLowerCase()
    }).on("changeDate", function () {
      _el.datepicker("hide");
    }).on("hide", function () {
      var _val = _el.data("lastValue") ? _el.data("lastValue") : _el.val();
      if (_val.indexOf("T") == -1) {
        _el.val(_el.val() + "T00:00Z");
      }
      else if (_el.val().indexOf("T") == "-1") {
        _el.val(_el.val() + "T" + _val.split("T")[1]);
      }
    });
    _el.datepicker('show');
    huePubSub.subscribeOnce('hide.datepicker', function () {
      _el.datepicker('hide');
    });
  });

  % if return_json:
    $('.submit-form').submit(function (e) {
      $.ajax({
        type: "POST",
        url: '${ action }',
        data: $('.submit-form').serialize(),
        dataType: "json",
        success: function (data) {
          if (data.status == 0) {
            huePubSub.publish('submit.popup.return', data);
          } else {
            var message = "${ _('Submission was not successful') }";
            if (data.message) {
              message = data.message;
            }
            $.jHueNotify.error(data.message + (data.detail ? (': ' + data.detail) : ''));
          }
        }
      });
      e.preventDefault();
    });
  % endif

</script>

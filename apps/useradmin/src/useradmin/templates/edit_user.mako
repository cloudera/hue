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

from desktop.views import commonheader, commonfooter

from useradmin.hue_password_policy import is_password_policy_enabled, get_password_hint
from useradmin.views import is_user_locked_out
from desktop.auth.backend import is_admin
%>

<%namespace name="layout" file="layout.mako" />

%if not is_embeddable:
${ commonheader(_('Hue Users'), "useradmin", user, request) | n,unicode }
%endif

${ layout.menubar(section='users') }


<div id="editUserComponents" class="useradmin container-fluid">
  <div class="card card-small title">
    % if username:
      <h1 class="card-heading simple">${_('Hue Users - Edit user: %(username)s') % dict(username=username)}</h1>
    % else:
      <h1 class="card-heading simple">${_('Hue Users - Create user')}</h1>
    % endif

    <br/>

    <form id="editForm" method="POST" class="form form-horizontal" autocomplete="off">
    ${ csrf_token(request) | n,unicode }
    <div id="properties" class="section">
      <ul class="nav nav-tabs" style="margin-bottom: 0">
        <li class="active">
          <a href="javascript:void(0)" class="step" data-step="step1">${ _('Step 1: Credentials') }
          % if not username:
            ${ _('(required)') }
          % endif
          </a>
        </li>
        <li><a href="javascript:void(0)" class="step" data-step="step2">${ is_admin(user) and _('Step 2: Profile and Groups') or _('Step 2: Profile') }</a>
        </li>
        % if is_admin(user):
            <li><a href="javascript:void(0)" class="step" data-step="step3">${ _('Step 3: Advanced') }</a></li>
        % endif
      </ul>

    <div class="steps">
      <div id="step1" class="stepDetails">
        ${layout.render_field(form["username"], extra_attrs={'validate':'true'})}
        % if "password1" in form.fields:
          % if username and "password_old" in form.fields:
            ${layout.render_field(form["password_old"], extra_attrs=username is None and {'validate':'true'} or {})}
          % endif
          ${layout.render_field(form["password1"], extra_attrs=username is None and {'validate':'true'} or {})}
          % if is_password_policy_enabled():
            <div class="password_rule" style="margin-left:180px; width:500px;">
              <p>${get_password_hint()}</p>
            </div>
          % endif
          ${layout.render_field(form["password2"], extra_attrs=username is None and {'validate':'true'} or {})}
        % endif
        ${layout.render_field(form["ensure_home_directory"])}
        </div>
        <div id="step2" class="stepDetails hide">
          % if "first_name" in form.fields:
            ${layout.render_field(form["first_name"])}
            ${layout.render_field(form["last_name"])}
          % endif

          ${layout.render_field(form["email"])}

          %if request.user.username == username:
            ${layout.render_field(form["language"])}
          % endif

          % if is_admin(user):
            ${layout.render_field(form["groups"])}
          % endif
        </div>
      % if is_admin(user):
        <div id="step3" class="stepDetails hide">
          ${layout.render_field(form["is_active"])}
          ${'is_superuser' in form.fields and layout.render_field(form["is_superuser"])}
          % if is_user_locked_out(username):
            ${layout.render_field(form["unlock_account"])}
          % endif
        </div>
      % endif
      </div>

      <div class="form-actions">
        <a class="backBtn btn disabled">${ _('Back') }</a>
        <a class="nextBtn btn btn-primary disable-feedback">${ _('Next') }</a>
        % if is_embeddable:
          <input type="hidden" value="true" name="is_embeddable" />
        % endif
        % if username:
        <input type="submit" class="btn btn-primary disable-feedback" value="${_('Update user')}"/>
        % else:
        <input type="submit" class="btn btn-primary disable-feedback" value="${_('Add user')}"/>
        % endif
      </div>
    </form>
  </div>
</div>

<script type="text/javascript">

$(document).ready(function(){
  var $editUserComponents = $('#editUserComponents');

  $editUserComponents.find("#id_groups").jHueSelector({
    selectAllLabel: "${_('Select all')}",
    searchPlaceholder: "${_('Search')}",
    noChoicesFound: "${_('No groups found.')} <a href='${url('useradmin.views.edit_group')}'>${_('Create a new group now')} &raquo;</a>",
    width:618,
    height:240
  });


  % if is_embeddable:
  $editUserComponents.find('#editForm').attr('action', window.location.pathname.substr((window.HUE_BASE_URL + '/hue').length).replace(/\/$/, ''));
  $editUserComponents.find('#editForm').ajaxForm({
    dataType:  'json',
    success: function(data) {
      if (data && data.status == -1) {
        renderUseradminErrors(data.errors);
      }
      else if (data && data.url) {
        huePubSub.publish('open.link', data.url);
        $.jHueNotify.info("${ _('User information updated correctly') }");
      }
    }
  });
  % endif

 var currentStep = "step1";

  function showStep(step) {
    currentStep = step;
    if (step != "step1") {
      $editUserComponents.find(".backBtn").removeClass("disabled");
    } else {
      $editUserComponents.find(".backBtn").addClass("disabled");
    }

    if (step != $editUserComponents.find(".stepDetails:last").attr("id")) {
      $editUserComponents.find(".nextBtn").removeClass("disabled");
    } else {
      $editUserComponents.find(".nextBtn").addClass("disabled");
    }

    $editUserComponents.find("a.step").parent().removeClass("active");
    $editUserComponents.find("a.step[data-step=" + step + "]").parent().addClass("active");
    $editUserComponents.find(".stepDetails").hide();
    $editUserComponents.find("#" + step).show();
  }

  function validateStep(step) {
    var proceed = true;
    $editUserComponents.find("#" + step).find("[validate=true]").each(function () {
      if ($(this).val().trim() == "") {
        proceed = false;
        router(step);
        $(this).parents(".control-group").addClass("error");
        $(this).parent().find(".help-inline").remove();
        $(this).after("<span class=\"help-inline\"><strong>${ _('This field is required.') }</strong></span>");
      }
    });
    return proceed;
  }

  function router(step) {
    switch (step) {
      case 'step1':
        showStep('step1');
        break;
      case 'step2':
        if (validateStep('step1')){
          showStep('step2');
        }
        break;
      case 'step3':
        if (validateStep('step1') && validateStep('step2')){
          showStep('step3');
        }
        break;
    }
  }

  $editUserComponents.find(".step").on('click', function () {
    router($(this).data('step'));
  });

  $editUserComponents.find(".backBtn").click(function () {
    var nextStep = (currentStep.substr(4) * 1 - 1);
    if (nextStep >= 1) {
      router('step' + nextStep);
    }
  });

  $editUserComponents.find(".nextBtn").click(function () {
    var nextStep = (currentStep.substr(4) * 1 + 1);
    if (nextStep <= $(".step").length) {
      router('step' + nextStep);
    }
  });

  $editUserComponents.find("[validate=true]").change(function () {
    $(this).parents(".control-group").removeClass("error");
    $(this).parent().find(".help-inline").remove();
  });

  % if not is_embeddable:
  $editUserComponents.find("#editForm").on("submit", function(){
    if (validateStep("step1") && validateStep("step2")) {
      return true;
    }
    return false;
  })
  % endif
});
</script>

${layout.commons()}

%if not is_embeddable:
${ commonfooter(None, messages) | n,unicode }
%endif

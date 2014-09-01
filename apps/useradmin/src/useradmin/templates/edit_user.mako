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
from desktop.views import commonheader, commonfooter
from django.utils.translation import ugettext as _
%>

<%namespace name="layout" file="layout.mako" />

${ commonheader(_('Hue Users'), "useradmin", user) | n,unicode }
${ layout.menubar(section='users') }

<div class="container-fluid">
  <div class="card card-small">
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
          <a href="#step1" class="step">${ _('Step 1: Credentials') }
          % if not username:
            ${ _('(required)') }
          % endif
          </a>
        </li>
        <li><a href="#step2" class="step">${ user.is_superuser and _('Step 2: Names and Groups') or _('Step 2: Names') }</a>
        </li>
        % if user.is_superuser:
            <li><a href="#step3" class="step">${ _('Step 3: Advanced') }</a></li>
        % endif
      </ul>

    <div class="steps">
      <div id="step1" class="stepDetails">
        ${layout.render_field(form["username"], extra_attrs={'validate':'true'})}
        % if "password1" in form.fields:
          ${layout.render_field(form["password1"], extra_attrs=username is None and {'validate':'true'} or {})}
          ${layout.render_field(form["password2"], extra_attrs=username is None and {'validate':'true'} or {})}
          % if username:
            ${layout.render_field(form["password_old"], extra_attrs=username is None and {'validate':'true'} or {})}
          % endif
        % endif
        ${layout.render_field(form["ensure_home_directory"])}
        </div>
        <div id="step2" class="stepDetails hide">
        % if "first_name" in form.fields:
                  ${layout.render_field(form["first_name"])}
                  ${layout.render_field(form["last_name"])}
                % endif

                ${layout.render_field(form["email"])}
                % if user.is_superuser:
                  ${layout.render_field(form["groups"])}
                % endif
        </div>
      % if user.is_superuser:
        <div id="step3" class="stepDetails hide">
        ${layout.render_field(form["is_active"])}
                ${'is_superuser' in form.fields and layout.render_field(form["is_superuser"])}
        </div>
      % endif
      </div>
      <div class="form-actions">
        <a id="backBtn" class="btn disabled">${ _('Back') }</a>
        <a id="nextBtn" class="btn btn-primary disable-feedback">${ _('Next') }</a>

      % if username:
        <input type="submit" class="btn btn-primary" value="${_('Update user')}"/>
      % else:
        <input type="submit" class="btn btn-primary" value="${_('Add user')}"/>
      % endif
      </div>
    </form>
  </div>
</div>

<script src="/static/ext/js/routie-0.3.0.min.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript" charset="utf-8">

$(document).ready(function(){
  $("#id_groups").jHueSelector({
    selectAllLabel: "${_('Select all')}",
    searchPlaceholder: "${_('Search')}",
    noChoicesFound: "${_('No groups found.')} <a href='${url('useradmin.views.edit_group')}'>${_('Create a new group now')} &raquo;</a>",
    width:618,
    height:240
  });

 var currentStep = "step1";

 routie({
    "step1":function () {
      showStep("step1");
    },
    "step2":function () {
      if (validateStep("step1")) {
        showStep("step2");
      }
    },
    "step3":function () {
      if (validateStep("step1") && validateStep("step2")) {
        showStep("step3");
      }
    }
  });

  function showStep(step) {
    currentStep = step;
    if (step != "step1") {
      $("#backBtn").removeClass("disabled");
    } else {
      $("#backBtn").addClass("disabled");
    }

    if (step != $(".stepDetails:last").attr("id")) {
      $("#nextBtn").removeClass("disabled");
    } else {
      $("#nextBtn").addClass("disabled");
    }

    $("a.step").parent().removeClass("active");
    $("a.step[href=#" + step + "]").parent().addClass("active");
    $(".stepDetails").hide();
    $("#" + step).show();
  }

  function validateStep(step) {
    var proceed = true;
    $("#" + step).find("[validate=true]").each(function () {
      if ($(this).val().trim() == "") {
        proceed = false;
        routie(step);
        $(this).parents(".control-group").addClass("error");
        $(this).parent().find(".help-inline").remove();
        $(this).after("<span class=\"help-inline\"><strong>${ _('This field is required.') }</strong></span>");
      }
    });
    return proceed;
  }

  $("#backBtn").click(function () {
    var nextStep = (currentStep.substr(4) * 1 - 1);
    if (nextStep >= 1) {
      routie("step" + nextStep);
    }
  });

  $("#nextBtn").click(function () {
    var nextStep = (currentStep.substr(4) * 1 + 1);
    if (nextStep <= $(".step").length) {
      routie("step" + nextStep);
    }
  });

  $("[validate=true]").change(function () {
    $(this).parents(".control-group").removeClass("error");
    $(this).parent().find(".help-inline").remove();
  });

  $("#editForm").on("submit", function(){
    if (validateStep("step1") && validateStep("step2")) {
      return true;
    }
    return false;
  })
});
</script>

${layout.commons()}

${ commonfooter(messages) | n,unicode }

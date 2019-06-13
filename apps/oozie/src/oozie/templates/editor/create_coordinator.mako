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

<%namespace name="layout" file="../navigation-bar.mako" />
<%namespace name="utils" file="../utils.inc.mako" />
<%namespace name="coordinator_utils" file="coordinator_utils.mako" />


${ commonheader(_("Create Coordinator"), "oozie", user, request) | n,unicode }
${ layout.menubar(section='coordinators') }

<style type="text/css">
  .steps {
    min-height: 350px;
    margin-top: 10px;
  }
  .nav {
    margin-bottom: 0;
  }
  .help-block {
    color: #999999;
  }
</style>

<script src="${ static('desktop/js/hue.routie.js') }" type="text/javascript" charset="utf-8"></script>

<div class="container-fluid">
  <div class="row-fluid">
    <div class="span2">
      <div class="sidebar-nav">
        <ul class="nav nav-list" style="min-height: 150px">
          <li class="nav-header">${ _('Properties') }</li>
          <li class="active"><a href="#">${ _('Edit properties') }</a></li>
         </ul>
        </div>
    </div>
    <div class="span10">
      <div class="card card-small">
        <h1 class="card-heading simple">${ _('Coordinator Editor') } ${ coordinator.name }</h1>
      <ul class="nav nav-pills">
        <li class="active"><a href="#step1" class="step">${ _('Step 1: Details') }</a></li>
        <li><a href="#step2" class="step">${ _('Step 2: Frequency') }</a></li>
        <li><a href="#step3" class="step">${ _('Step 3: Inputs') }</a></li>
        <li><a href="#step4" class="step">${ _('Step 4: Outputs') }</a></li>
        <li><a href="#step5" class="step">${ _('Step 5: Advanced settings') }</a></li>
      </ul>
      <form class="form-horizontal" action="${ url('oozie:create_coordinator') }" method="POST">
        ${ csrf_token(request) | n,unicode }
        <div class="steps">

          <div id="step1" class="stepDetails">
            <div class="alert alert-info"><h3>${ _('Schedule') }</h3></div>
            <div class="fieldWrapper">
              ${ utils.render_field_no_popover(coordinator_form['name'], extra_attrs = {'validate':'true'}) }
              ${ utils.render_field_no_popover(coordinator_form['description']) }
              ${ utils.render_field_no_popover(coordinator_form['coordinatorworkflow'], extra_attrs = {'validate':'true'}) }
              ${ coordinator_form['parameters'] | n,unicode }
              ${ coordinator_form['job_properties'] | n,unicode }
              <div class="hide">
                ${ utils.render_field_no_popover(coordinator_form['is_shared']) }
                ${ utils.render_field(coordinator_form['timeout']) }
                ${ coordinator_form['schema_version'] | n,unicode }
              </div>
            </div>
          </div>

          <div id="step2" class="stepDetails hide">
            <div class="alert alert-info"><h3>${ _('Frequency') }</h3></div>
            <div class="fieldWrapper">
              <div class="row-fluid">
                <div class="alert alert-warning">
                  ${ _('UTC time only. (e.g. if you want 10pm PST (UTC+8) set it 8 hours later to 6am the next day.') }
                </div>
              </div>
            </div>
            <div class="fieldWrapper">
              % if enable_cron_scheduling:
                ${ coordinator_utils.frequency_fields() }
              % else:
                <div class="row-fluid">
                  <div class="span6">
                    ${ utils.render_field_no_popover(coordinator_form['frequency_number']) }
                  </div>
                  <div class="span6">
                    ${ utils.render_field_no_popover(coordinator_form['frequency_unit']) }
                  </div>
                </div>
              % endif
            </div>
            <div class="fieldWrapper">
              <div class="row-fluid">
                <div class="span6">
                  ${ utils.render_field_no_popover(coordinator_form['start']) }
                </div>
                <div class="span6">
                  ${ utils.render_field_no_popover(coordinator_form['end']) }
                </div>
              </div>
              ${ utils.render_field_no_popover(coordinator_form['timezone']) }
            </div>
          </div>

        </div>

        <div class="form-actions">
          <a id="backBtn" class="btn disabled">${ _('Back') }</a>
          <a id="nextBtn" class="btn btn-primary">${ _('Next') }</a>
        </div>

      </form>
    </div>
    </div>

  </div>
</div>

% if enable_cron_scheduling:
<link href="${ static('desktop/css/jqCron.css') }" rel="stylesheet" type="text/css" />
<script src="${ static('desktop/js/jqCron.js') }" type="text/javascript"></script>
% endif

<script type="text/javascript" src="${ static('oozie/js/coordinator.js') }"></script>


<script type="text/javascript">
  $(document).ready(function () {

    % if enable_cron_scheduling:
      ${ utils.cron_js() }
      initCoordinator(${ coordinator_frequency | n,unicode }, cron_i18n); // cron_i18n comes from utils.inc.mako
    % endif

    var currentStep = "step1";

    routie({
      "step1":function () {
        showStep("step1");
      },
      "step2":function () {
        if (validateStep("step1")) {
          showStep("step2");
        }
        else {
          routie("step1");
        }
      },
      "step3":function () {
        if (validateStep("step1") && validateStep("step2")) {
          $("form").submit();
        }
      },
      "step4":function () {
        if (validateStep("step1") && validateStep("step2")) {
          $("form").submit();
        }
      },
      "step5":function () {
        if (validateStep("step1") && validateStep("step2")) {
          $("form").submit();
        }
      },
      "submit":function () {
        if (validateStep("step1") && validateStep("step2")) {
          $("form").submit();
        }
        else {
          routie("");
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
      $("a.step").parent().removeClass("active");
      $("a.step[href='#" + step + "']").parent().addClass("active");
      $(".stepDetails").hide();
      $("#" + step).show();
    }

    function validateStep(step) {
      var proceed = true;
      $("#" + step).find("[validate=true]").each(function () {
        if ($(this).val().trim() == "") {
          proceed = false;
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
  });
</script>

${ utils.decorate_datetime_fields() }

${ commonfooter(request, messages) | n,unicode }

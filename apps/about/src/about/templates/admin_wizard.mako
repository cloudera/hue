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
from django.core.urlresolvers import reverse
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext as _
%>

<%namespace name="layout" file="/about_layout.mako" />

%if not is_embeddable:
${ commonheader(_('Quick Start'), "quickstart", user, request) | n,unicode }
%endif
${ layout.menubar(section='quick_start') }

<div class="container-fluid">
  <div class="row-fluid" style="margin-bottom: 100px;">
    <div class="card card-small">
      <h2 class="card-heading simple">
        % if user.is_superuser:
          ${ _('Quick Start Wizard') } -
        % endif
        Hue&trade; ${version} - <a href="http://gethue.com" target="_blank" style="color:#777" title="${ _('Visit the project website!') }">${ _("The Hadoop UI") }</a>
      </h2>

     % if user.is_superuser:

      <div class="card-body">
        <br/>

         <div class="row-fluid">
          <div id="properties" class="section">
            <ul class="nav nav-tabs" style="margin-bottom: 0">
              <li class="active"><a href="#step1" class="step">${ _('Step 1:') } <i class="fa fa-cogs"></i> ${ _('Check Configuration') }</a></li>
              <li><a href="#step2" class="step">${ _('Step 2:') } <i class="fa fa-book"></i> ${ _('Examples') }</a></li>
              <li><a href="#step3" class="step">${ _('Step 3:') } <i class="fa fa-group"></i> ${ _('Users') }</a></li>
              <li><a id="lastStep" href="#step4" class="step">${ _('Step 4:') } <i class="fa fa-flag"></i> ${_('Go!') }</a></li>
            </ul>

          <div class="steps">
          <div id="step1" class="stepDetails">
            <div class="card card-tab">
              <h2 class="card-heading simple">${ _('Checking current configuration') }</h2>

              <div class="card-body">
                <div id="check-config-section" style="margin-bottom:20px">
                  <div class="spinner">
                    <i class="fa fa-spinner fa-spin" style="font-size: 60px; color: #DDD"></i>
                  </div>
                  <div class="info hide"></div>
                </div>
              </div>
            </div>

          </div>

          <div id="step2" class="stepDetails hide">
            <div class="card card-tab card-listcontent">
              <h2 class="card-heading simple">${ _('Install individual application examples') }</h2>
              <div class="card-body">
                <ul>
                % if 'beeswax' in app_names:
                    <li>
                      <a href="javascript:void(0)" class="installBtn" data-loading-text="${ _('Installing...') }"
                         data-sample-url="${ url('beeswax:install_examples') }">
                        <i class="fa fa-download"></i> ${ apps['beeswax'].nice_name }
                      </a>
                    </li>
                % endif
                % if 'impala' in app_names:
                    <li>
                      <a href="javascript:void(0)" class="installBtn" data-loading-text="${ _('Installing...') }"
                         data-sample-url="${ url('impala:install_examples') }">
                        <i class="fa fa-download"></i> ${ apps['impala'].nice_name }
                      </a>
                    </li>
                % endif
                % if 'search' in app_names:
                    <li>
                      <a href="javascript:void(0)" class="installBtn" data-loading-text="${ _('Installing...') }"
                         data-sample-url="${ url('search:install_examples') }">
                        <i class="fa fa-download"></i> ${ apps['search'].nice_name }
                      </a>
                    </li>
                % endif
                % if 'spark' in app_names:
                    <li>
                      <a href="javascript:void(0)" class="installBtn" data-loading-text="${ _('Installing...') }"
                         data-sample-url="${ url('notebook:install_examples') }">
                        <i class="fa fa-download"></i> ${ apps['spark'].nice_name }
                      </a>
                    </li>
                % endif
                % if 'oozie' in app_names:
                    <li>
                      <a href="javascript:void(0)" class="installBtn" data-loading-text="${ _('Installing...') }"
                         data-sample-url="${ url('oozie:install_examples') }">
                        <i class="fa fa-download"></i> ${ apps['oozie'].nice_name }
                      </a>
                    </li>
                % endif
                % if 'hbase' in app_names:
                    <li>
                      <a href="javascript:void(0)" class="installBtn" data-loading-text="${ _('Installing...') }"
                         data-sample-url="${ url('hbase:install_examples') }">
                        <i class="fa fa-download"></i> ${ apps['hbase'].nice_name }
                      </a>
                    </li>
                % endif
                % if 'pig' in app_names:
                    <li>
                      <a href="javascript:void(0)" class="installBtn" data-loading-text="${ _('Installing...') }"
                         data-sample-url="${ url('pig:install_examples') }">
                        <i class="fa fa-download"></i> ${ apps['pig'].nice_name }
                      </a>
                    </li>
                % endif
                % if 'jobsub' in app_names:
                    <li>
                      <a href="javascript:void(0)" class="installBtn" data-loading-text="${ _('Installing...') }"
                         data-sample-url="${ url('oozie:install_examples') }">
                        <i class="fa fa-download"></i> ${ apps['jobsub'].nice_name }
                      </a>
                    </li>
                % endif
                </ul>
              </div>
            </div>
          </div>

          <div id="step3" class="stepDetails hide">
            <div class="card card-tab card-listcontent">
              <h2 class="card-heading simple">${ _('Create or import users') }</h2>

              <div class="card-body" style="margin-top: 10px">
                <a href="${ url('useradmin.views.list_users') }" target="_blank" style="padding-left: 2px"><img
                    src="${ static('useradmin/art/icon_useradmin_48.png') }" class="app-icon"
                    style="margin-right: 4px;" alt="${ _('User Admin') }"> ${ _('User Admin') }</a>
              </div>
            </div>

            <div class="card card-home card-tab card-tab-bordertop card-listcontent margin-top-30">
              <h2 class="card-heading simple">${ _('Anonymous usage analytics') }</h2>

              <div class="card-body" style="margin-top: 10px">
                <label class="checkbox">
                  <input class="updatePreferences" type="checkbox" name="collect_usage" style="margin-right: 10px" title="${ _('Check to enable usage analytics') }" ${ collect_usage and 'checked' or '' }/>
                  ${ _('Help improve Hue with anonymous usage analytics.') }
                  <a href="javascript:void(0)" style="display: inline" data-trigger="hover" data-toggle="popover" data-placement="right" rel="popover"
                     title="${ _('How does it work?') }"
                     data-content="${ _('We are using Google Analytics to see how many times an application or specific section of an application is used, nothing more.') }">
                     <i class="fa fa-question-circle"></i>
                  </a>
                </label>
              </div>
            </div>
          </div>

          <div id="step4" class="stepDetails hide">
            <div class="card card-tab card-listcontent">
              <h2 class="card-heading simple">${ _('Use the applications') }</h2>

              <div class="card-body">
                <a href="${ url('desktop.views.home2') }" style="padding-left: 2px; line-height: 24px; margin-right: 4px"><i class="fa fa-home" style="font-size: 24px; color: #0B7FAD; vertical-align: middle;"></i> ${ _('Hue Home') }</a>
              </div>
            </div>

            <div class="card card-home card-tab card-tab-bordertop card-listcontent">
              <h2 class="card-heading simple">${ _('Skip wizard next time') }</h2>

              <div class="card-body">
                <label class="checkbox">
                  <input id="updateSkipWizard" type="checkbox"
                         style="margin-right: 10px"
                         title="${ _('Check to skip this wizard next time.') }"/>
                  ${ _('Skip the Quick Start Wizard at next login and land directly on the home page.') }
                </label>
              </div>
            </div>

          </div>
          </div>

          </div>
          </div>
      </div>

      <div class="form-actions">
        <a id="backBtn" class="btn disabled">${ _('Back') }</a>
        <a id="nextBtn" class="btn btn-primary disable-feedback">${ _('Next') }</a>
        <a id="doneBtn" class="btn btn-primary disable-feedback hide">${ _('Done') }</a>
        <div class="pull-right muted">${ _('Hue and the Hue logo are trademarks of Cloudera, Inc.') }</div>
      </div>
      % else:
       <div class="card-body">
        <p>
          ${ _('Learn more about Hue and Hadoop on') } <a href="http://gethue.com" target="_blank">http://gethue.com</a>.
          <span class="muted">${ _('Hue and the Hue logo are trademarks of Cloudera, Inc.') }</span>
          % if not user.is_authenticated():
            <br/>
            <a href="${ url('desktop.views.home2') }" class="btn btn-primary" style="margin-top: 50px;margin-bottom: 20px"><i class="fa fa-sign-in"></i> ${ _('Sign in now!') }</a>
          % endif
        </p>
       </div>
      % endif

    </div>
  </div>

</div>

% if user.is_superuser:
<style type="text/css">
  .steps {
    min-height: 300px;
  }

  input[type=submit] {
    margin-left: 50px;
  }

  @media all and (max-height: 800px) {
    .form-actions {
      position:fixed;
      bottom:0;
      margin:0;
      left:0;
      right:0;
    }
  }

  .footer {
    text-align: center;
  }

  .stepDetails .card .card-heading.simple {
    border-bottom: none;
  }

</style>

<script src="${ static('desktop/js/hue.routie.js') }" type="text/javascript" charset="utf-8"></script>
<script>
  routie.setPathname('/about');
</script>


<script type="text/javascript">

$(document).ready(function(){

  window.setTimeout(function(){
    $.get("${ url('desktop.views.check_config') }", function(response) {
      $("#check-config-section .spinner").css({
        'position': 'absolute',
        'top': '-100px'
      });
      $("#check-config-section .info").html(response);
      $("#check-config-section .info").removeClass('hide');
    })
    .fail(function() { $(document).trigger('error', '${ _("Check config failed: ")}'); });
  }, 100);

  $("[rel='popover']").popover();

  $(".installBtn").click(function() {
    var button = $(this);
    $(button).button('loading');
    $.post($(this).data("sample-url"), function(data) {
      if (data.status == 0) {
        $(document).trigger('info','${ _("Examples refreshed") }');
      } else {
        $(document).trigger('error', data.message);
      }
    })
    .always(function(data) {
      $(button).button('reset');
    });
  });

  $(".installAllBtn").click(function() {
    var button = $(this);
    $(button).button('loading');
    var calls = jQuery.map($("[data-sample-url]"), function(app) {
      return $.post($(app).data("sample-url"), function(data) {
        if (data.status != 0) {
          $(document).trigger('error', data.message);
        }
      });
    });
    $.when.apply(this, calls)
      .then(function() {
        $(document).trigger('info', '${ _("Examples refreshed") }');
      })
      .always(function(data) {
        $(button).button('reset');
      });
  });

  var currentStep = "step1";

  routie({
    "step1":function () {
      showStep("step1");
    },
    "step2":function () {
      showStep("step2");
    },
    "step3":function () {
      showStep("step3");
    },
    "step4":function () {
      showStep("step4");
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
      $("#nextBtn").removeClass("hide");
      $("#doneBtn").addClass("hide");
    } else {
      $("#nextBtn").addClass("hide");
      $("#doneBtn").removeClass("hide");
    }

    $("a.step").parent().removeClass("active");
    $("a.step[href=#" + step + "]").parent().addClass("active");
    if (step == "step4") {
      $("#lastStep").parent().addClass("active");
    }
    $(".stepDetails").hide();
    $("#" + step).show();
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

  $("#doneBtn").click(function () {
    location.href = "${ url('desktop.views.home2') }";
  });

  $(".updatePreferences").click(function () {
    $.post("${ url('about:update_preferences') }", $("input").serialize(), function(data) {
      if (data.status == 0) {
        $(document).trigger('info', '${ _("Configuration updated") }');
      } else {
        $(document).trigger('error', data.data);
      }
    });
  });

  $("#updateSkipWizard").prop('checked', $.cookie("hueLandingPage", {path: "/"}) == "home");

  $("#updateSkipWizard").change(function () {
    $.cookie("hueLandingPage", this.checked ? "home" : "wizard", {
      path: "/",
      secure: window.location.protocol.indexOf('https') > -1
    });
  });

});
</script>
% endif

%if not is_embeddable:
${ commonfooter(request, messages) | n,unicode }
%endif

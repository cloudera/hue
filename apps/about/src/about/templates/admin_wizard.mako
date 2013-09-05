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
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext as _
%>

${ commonheader(_('Quick Start'), "quickstart", user, "100px") | n,unicode }

% if user.is_superuser:
  <div class="row-fluid">
    <div class="subnav subnav-fixed">
      <div class="container-fluid">
        <ul class="nav nav-pills">
          <li class="active"><a href="${url("about:admin_wizard")}">${_('Quick Start')}</a></li>
          <li><a href="${url("desktop.views.dump_config")}">${_('Configuration')}</a></li>
          <li><a href="${url("desktop.views.log_view")}">${_('Server Logs')}</a></li>
        </ul>
      </div>
    </div>
  </div>
% endif

<div class="container-fluid">
  <div class="row-fluid">
    <div class="card" style="margin-bottom: 100px;">
      <h2 class="card-heading simple">
        % if user.is_superuser:
          ${ _('Quick Start Wizard') } -
        % endif
        Hue ${version}
      </h2>

      <div class="card-body">
          % if user.is_superuser:
            <br/>

          <div class="row-fluid">
          <div id="properties" class="section">
            <ul class="nav nav-tabs" style="margin-bottom: 0">
              <li class="active"><a href="#step1" class="step">${ _('Step 1:') } <i
                  class="icon-cogs"></i> ${ _('Check Configuration') }</a></li>
              <li><a href="#step2" class="step">${ _('Step 2:') } <i class="icon-book"></i> ${ _('Examples') }</a></li>
              <li><a href="#step3" class="step">${ _('Step 3:') } <i class="icon-group"></i> ${ _('Users') }</a></li>
              <li><a id="lastStep" href="#step4" class="step">${ _('Step 4:') } <i class="icon-flag"></i> ${_('Go!') }
              </a></li>
            </ul>

          <div class="steps">
          <div id="step1" class="stepDetails">
            <div class="card card-tab">
              <h2 class="card-heading simple">${ _('Checking current configuration') }</h2>

              <div class="card-body">
                <div id="check-config-section">
                  <!--[if !IE]><!--><i class="icon-spinner icon-spin" style="font-size: 60px;"></i><!--<![endif]-->
                  <!--[if IE]><img src="/hbase/static/art/loader.gif" /><![endif]-->
                </div>
              </div>
            </div>

          <div class="card card-home card-tab card-tab-bordertop">
            <h2 class="card-heading simple">${ _('HDFS Trash Configuration') }</h2>
          <div class="card-body">
          <p>
            % if not trash_enabled:
            <h5>${ _('Trash is active.')}</h5>
            % else:
            ${ _('You can activate trash collection by setting fs.trash.interval in core-site.xml:')}<br/><br/>
            <pre>
  &#60;property&#62;
    &#60;name&#62;fs.trash.interval&#60;/name&#62;
    &#60;value&#62;10060&#60;/value&#62;
  &#60;/property&#62;</pre>
            % endif
          </p>
          </div>
          </div>
          </div>

          <div id="step2" class="stepDetails hide">
            <div class="card card-tab card-listcontent">
              <h2 class="card-heading simple">${ _('Install all the application examples') }</h2>

              <div class="card-body">
                <p>
                <ul>
                  <li>
                    <a href="#" class="installAllBtn" data-loading-text="${ _('Installing...') }">
                      <i class="icon-download-alt"></i> ${ _('All') }
                    </a>
                  </li>
                </ul>
                </p>
              </div>
            </div>

          <div class="card card-home card-tab card-tab-bordertop card-listcontent">
            <h2 class="card-heading simple">${ _('Install individual application examples') }</h2>
          <div class="card-body">
            <p>
          <ul>
          % if 'beeswax' in app_names:
              <li>
                <a href="#" class="installBtn" data-loading-text="${ _('Installing...') }"
                   data-sample-url="${ url('beeswax:install_examples') }">
                  <i class="icon-download-alt"></i> ${ apps['beeswax'].nice_name }
                </a>
              </li>
          % endif
          % if 'impala' in app_names:
              <li>
                <a href="#" class="installBtn" data-loading-text="${ _('Installing...') }"
                   data-sample-url="${ url('impala:install_examples') }">
                  <i class="icon-download-alt"></i> ${ apps['impala'].nice_name }
                </a>
              </li>
          % endif
          % if 'jobsub' in app_names:
              <li>
                <a href="#" class="installBtn" data-loading-text="${ _('Installing...') }"
                   data-sample-url="${ url('oozie:install_examples') }">
                  <i class="icon-download-alt"></i> ${ apps['jobsub'].nice_name }
                </a>
              </li>
          % endif
          % if 'oozie' in app_names:
              <li>
                <a href="#" class="installBtn" data-loading-text="${ _('Installing...') }"
                   data-sample-url="${ url('oozie:install_examples') }">
                  <i class="icon-download-alt"></i> ${ apps['oozie'].nice_name }
                </a>
              </li>
          % endif
          % if 'pig' in app_names:
              <li>
                <a href="#" class="installBtn" data-loading-text="${ _('Installing...') }"
                   data-sample-url="${ url('pig:install_examples') }">
                  <i class="icon-download-alt"></i> ${ apps['pig'].nice_name }
                </a>
              </li>
          % endif
          </ul>
            </p>
          </div>
          </div>
          </div>

            <div id="step3" class="stepDetails hide">
              <div class="card card-tab card-listcontent">
                <h2 class="card-heading simple">${ _('Create or import users') }</h2>

                <div class="card-body">
                  <p>
                    <a href="${ url('useradmin.views.list_users') }" target="_blank" style="padding-left: 2px"><img
                        src="/useradmin/static/art/icon_useradmin_24.png"
                        style="margin-right: 4px;"> ${ _('User Admin') }</a>
                  </p>
                </div>
              </div>

              <div class="card card-home card-tab card-tab-bordertop card-listcontent">
                <h2 class="card-heading simple">${ _('Tours and tutorials') }</h2>

                <div class="card-body">
                  <p>
                    <label class="checkbox">
                      <input class="updatePreferences" type="checkbox" name="tours_and_tutorials"
                             style="margin-right: 10px"
                             title="${ ('Check to enable the tours and tutorials') }" ${ tours_and_tutorials and "checked" }/>
                    ${ ('Display the "Available Tours" question mark when tours are available for a specific page.') }
                    </label>
                  </p>
                </div>
              </div>
            </div>

            <div id="step4" class="stepDetails hide">
              <div class="card card-tab card-listcontent">
                <h2 class="card-heading simple">${ _('Use the applications') }</h2>

                <div class="card-body">
                  <p>
                    <a href="${ url('desktop.views.home') }" class="step"><i class="icon-home"></i> ${_('Hue Home') }
                    </a>
                  </p>
                </div>
              </div>
            </div>
          </div>

          </div>
          </div>
          % endif
      </div>
    </div>
  </div>

  <div class="form-actions" style="position:fixed;bottom:0;margin:0;margin-left:-20px;width:100%">
    <a id="backBtn" class="btn disabled">${ _('Back') }</a>
    <a id="nextBtn" class="btn btn-primary disable-feedback">${ _('Next') }</a>
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

</style>

<script src="/static/ext/js/routie-0.3.0.min.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript" charset="utf-8">
$(document).ready(function(){

  $.get("${ url('desktop.views.check_config') }", function(response) {
    $("#check-config-section").html(response);
  })
  .fail(function() { $(document).trigger('error', '${ _("Check config failed: ")}'); });

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
      return $.post($(app).data("sample-url"));
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
      $("#nextBtn").removeClass("disabled");
    } else {
      $("#nextBtn").addClass("disabled");
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

  $(".updatePreferences").click(function () {
    $.post("${ url('about:update_preferences') }", $("input").serialize(), function(data) {
      if (data.status == 0) {
        $(document).trigger('info', '${ _("Configuration updated") }');
      } else {
        $(document).trigger('error', data.data);
      }
    });
  });

});
</script>
% endif

${ commonfooter(messages) | n,unicode }

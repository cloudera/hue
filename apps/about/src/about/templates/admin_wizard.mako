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
import sys

from django.urls import reverse

from metadata.conf import OPTIMIZER, has_optimizer

from desktop.auth.backend import is_admin
from desktop.conf import has_connectors
from desktop.views import commonheader, commonfooter

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _
%>

<%namespace name="layout" file="/about_layout.mako" />

% if not is_embeddable:
  ${ commonheader(_('Quick Start'), "quickstart", user, request, "70px") | n,unicode }
% endif

${ layout.menubar(section='quick_start') }

<div class="container-fluid" id="adminWizardComponents">
  <div class="row-fluid" style="margin-bottom: 100px;">
    <div>
      <h1 class="margin-top-20 margin-bottom-30">
        % if is_admin(user):
          ${ _('Quick Start') } -
        % endif
        <a href="https://gethue.com" target="_blank" title="${ _('Open Hue\'s website in a new tab') }">
          Hue&trade;
          ${ version }
        </a>
        -
        Query. Explore. Repeat.
      </h1>

     % if is_admin(user):
      <div class="margin-bottom-30">
         <div class="row-fluid">

           <div class="span2">
            <ul class="nav nav-pills nav-vertical-pills">
              <li class="active"><a href="#step1" class="step">${ _('Step 1:') } <i class="fa fa-check"></i> ${ _('Checks') }</a></li>
              <li><a href="#step2" class="step">${ _('Step 2:') } <i class="fa fa-exchange"></i> ${ _('Connectors') }</a></li>
              <li><a href="#step3" class="step">${ _('Step 3:') } <i class="fa fa-book"></i> ${ _('Examples') }</a></li>
              <li><a id="lastStep" href="#step4" class="step">${ _('Step 4:') } <i class="fa fa-group"></i> ${ _('Users') }</a></li>
            </ul>
           </div>

          <div class="span10 steps">
          <div id="step1" class="stepDetails">
            <div>
              <h3>${ _('Checking current configuration') }</h3>

              <div id="check-config-section" class="margin-bottom-20">
                <div class="spinner">
                  <i class="fa fa-spinner fa-spin" style="font-size: 60px; color: #DDD"></i>
                </div>
                <div class="info hide"></div>
              </div>
            </div>
          </div>

          <div id="step2" class="stepDetails hide">
            <h3>${ _('Add connectors to data services') }</h3>

            % if has_connectors():
            <span id="connectorCounts">...</span> ${ _('connectors installed') }

            <ul class="unstyled samples margin-top-20">
              <li>
                <a href="${ url('desktop.lib.connectors.views.index') }" title="${ _('Open the connector configuration page') }">
                  <i class="fa fa-plus"></i> ${ _('Add a Database') }
                </a>
              </li>
              <li>
                <a href="javascript:void(0)" class="installBtn" title="${ _('Install the connector examples') }" data-is-connector="true"
                  data-loading-text="${ _('Installing...') }" data-sample-url="${ url('connectors.api.install_connector_examples') }">
                  <i class="fa fa-download"></i> ${ _('Install examples') }
                </a>
              </li>
            </ul>
            % else:
              <a href="${ url('desktop.views.dump_config') }" target="_blank">${ _('Configuration') }</a>
              <br>
              <a href="https://docs.gethue.com/administrator/configuration/" target="_blank">${ _('Documentation') }</a>
            % endif
          </div>

          <div id="step3" class="stepDetails hide">
            <div>
              <h3>${ _('Install some data examples') }</h3>
              <ul class="unstyled samples">

              % if has_connectors():
                <!-- ko foreach: connectors -->
                  <!-- ko if: ['hive', 'impala', 'mysql', 'postgresql', 'presto', 'phoenix', 'flink', 'ksql'].indexOf(dialect) != -1 -->
                  <li>
                    <a href="javascript:void(0)" data-bind="click: $root.installConnectorDataExample">
                      <i class="fa fa-download"></i> <span data-bind="text: name"></span>
                    </a>
                  </li>
                  <!-- /ko -->
                <!-- /ko -->

                <li>
                  <div id="check-config-section" class="margin-bottom-20" data-bind="visible: isInstallingSample">
                    <div class="spinner">
                      <i class="fa fa-spinner fa-spin" style="font-size: 60px; color: #DDD"></i>
                    </div>
                  </div>
                </li>
              % else:
                % if 'hive' in app_names:
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
                % if has_optimizer() and OPTIMIZER.QUERY_HISTORY_UPLOAD_LIMIT.get() > 0:
                  <li>
                    <a href="javascript:void(0)" class="installBtn" data-loading-text="${ _('Uploading...') }"
                       data-sample-url="${ url('metadata:upload_history') }" title="${ _('Send and analyze past %s executed queries to provide smarter SQL recommendations') % OPTIMIZER.QUERY_HISTORY_UPLOAD_LIMIT.get() }">
                      <i class="fa fa-download"></i> ${ _('SQL Query history') }
                    </a>
                  </li>
                % endif
                % if 'search' in app_names:
                  <li>
                    <a href="javascript:void(0)" class="installAllBtn" data-loading-text="${ _('Installing...') }"
                       data-sample-url="${ url('search:install_examples') }" data-sample-data='["log_analytics_demo", "twitter_demo", "yelp_demo"]'>
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
                % if 'oozie' in app_names:
                  <li>
                    <a href="javascript:void(0)" class="installBtn" data-loading-text="${ _('Installing...') }"
                       data-sample-url="${ url('oozie:install_examples') }">
                      <i class="fa fa-download"></i> ${ _('Job Editor') }
                    </a>
                  </li>
                % elif 'jobsub' in app_names:
                  <li>
                    <a href="javascript:void(0)" class="installBtn" data-loading-text="${ _('Installing...') }"
                       data-sample-url="${ url('oozie:install_examples') }">
                      <i class="fa fa-download"></i> ${ apps['jobsub'].nice_name }
                    </a>
                  </li>
                % endif
              % endif
              </ul>
            </div>
          </div>

          <div id="step4" class="stepDetails hide">
            <div>
              <h3>${ _('Create or import users') }</h3>
              <a href="${ url('useradmin:useradmin.views.list_users') }"
                 % if not is_embeddable:
                 target="_blank"
                 % endif
              ><i class="fa fa-user"></i> ${ _('User Admin') }</a>
            </div>

            <div class="margin-top-30">
              <h3>${ _('Anonymous usage analytics') }</h3>
              <label class="checkbox">
                <input class="updatePreferences" type="checkbox" name="collect_usage" style="margin-right: 10px"
                  title="${ _('Check to enable usage analytics') }" ${ collect_usage and 'checked' or '' }/>
                ${ _('Help improve Hue with anonymous usage analytics.') }
                <a href="javascript:void(0)" style="display: inline" data-trigger="hover" data-toggle="popover"
                  data-placement="right" rel="popover"
                  title="${ _('How does it work?') }"
                  data-content="${ _('Hue is using Google Analytics to see how many times an application or specific section of an application is used, nothing more.') }">
                   <i class="fa fa-question-circle"></i>
                </a>
              </label>
            </div>

            % if not is_embeddable:
            <div class="margin-top-30">
              <h3>${ _('Skip wizard next time') }</h3>
              <label class="checkbox">
                <input id="updateSkipWizard" type="checkbox" style="margin-right: 10px" title="${ _('Check to skip this wizard next time.') }"/>
                ${ _('Skip the Quick Start Wizard at next login and land directly on your starred application.') }
              </label>
            </div>
            % endif

          </div>
          </div>

        </div>
      </div>
      <div class="card-body">
        <div class="form-actions">
          <a id="backBtn" class="btn disabled">${ _('Back') }</a>
          <a id="nextBtn" class="btn btn-primary disable-feedback">${ _('Next') }</a>
          <a id="doneBtn" class="btn btn-primary disable-feedback hide">${ _('Done') }</a>
          <span class="pull-right muted" style="padding-right:30px">${ _('Hue and the Hue logo are trademarks of Cloudera, Inc.') }</span>
        </div>
      </div>
      % else:
       <div class="card-body">
        <p>
          ${ _('Learn more about Hue and SQL Querying on') } <a href="https://gethue.com" target="_blank">https://gethue.com</a>.
          <br/>
          <br/>
          <span class="pull-right muted">${ _('Hue and the Hue logo are trademarks of Cloudera, Inc.') }</span>
          % if not user.is_authenticated:
            <br/>
            <a href="${ url('desktop_views_home2') }" class="btn btn-primary" style="margin-top: 50px;margin-bottom: 20px">
              <i class="fa fa-sign-in"></i> ${ _('Sign in now!') }
            </a>
          % endif
        </p>
       </div>
      % endif

    </div>
  </div>

</div>

% if is_admin(user):
<style type="text/css">
  .steps {
    min-height: 300px;
  }

  input[type=submit] {
    margin-left: 50px;
  }

  ul.samples li {
    padding-bottom: 5px;
  }

  .nav-pills.nav-vertical-pills li {
    float: none;
    margin-bottom: 10px;
  }

  .nav-pills.nav-vertical-pills li a {
    line-height: 20px;
  }

</style>

<script src="${ static('desktop/js/hue.routie.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/js/admin-wizard-inline.js') }" type="text/javascript"></script>
% endif

% if not is_embeddable:
  ${ commonfooter(request, messages) | n,unicode }
% endif

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
  from liboozie.oozie_api import get_oozie
%>


<%def name="frequency_fields()">
  <div class="control-group">
    <label class="control-label">${ _('When') }</label>
    <div class="controls">
      <div class="row-fluid">
        <div class="span9">
          <a data-bind="visible: isAdvancedCron" href="http://www.quartz-scheduler.org/documentation/quartz-2.x/tutorials/crontrigger.html" class="pull-right" target="_blank">&nbsp;<i class="fa fa-question-circle" title="${ _('Check syntax ?') }"></i></a>
          <input data-bind="visible: isAdvancedCron" id="coord-frequency" name="cron_frequency" class="pull-right"/>
          <span data-bind="visible: isAdvancedCron" class="pull-right" style="padding-right:20px">
            ${ _('Crontab') }
          </span>&nbsp;
          <label class="checkbox" style="display: inline-block"><input type="checkbox" name="isAdvancedCron" data-bind="checked: isAdvancedCron" /> (${ _('advanced') })</label>
        </div>
        <div class="span3">
        </div>
      </div>
      <span class="help-block">${ _('The time frequency at which interval a workflow should be submitted by the coordinator. For example, once a day, every Monday at midnight, every week days, every three days...') }</span>
    </div>
  </div>
</%def>

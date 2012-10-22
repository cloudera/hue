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

${ commonheader(_("Oozie App"), "oozie", user, "100px") }
${ layout.menubar(section='coordinators') }


<script src="/static/ext/js/knockout-2.1.0.js" type="text/javascript" charset="utf-8"></script>


<div class="container-fluid">
    <h1>${ _('Coordinator') } ${ coordinator.name }</h1>

    <div class="well">
      % if coordinator.workflow:
      <br/>
        ${ _('Workflow') }: <a href="${ coordinator.workflow.get_absolute_url() }">${ coordinator.workflow }</a>
      % endif
    </div>

  <form class="form-horizontal" id="workflowForm" action="${ url('oozie:create_coordinator') }" method="POST">

    <div class="row-fluid">
        <div class="span2"></div>

        <div class="span8">
           <h2>${ _('Coordinator') }</h2>
           <div class="fieldWrapper">
             ${ utils.render_field(coordinator_form['name']) }
             ${ utils.render_field(coordinator_form['description']) }
             ${ utils.render_field(coordinator_form['workflow']) }
             ${ coordinator_form['parameters'] }
             <div class="hide">
               ${ utils.render_field(coordinator_form['timeout']) }
               ${ coordinator_form['schema_version'] }
             </div>
           </div>

          <hr/>
          <h2>${ _('Frequency') }</h2>

          <div class="fieldWrapper">
            <div class="row-fluid">
              <div class="span6">
              ${ utils.render_field(coordinator_form['frequency_number']) }
            </div>
            <div class="span6">
              ${ utils.render_field(coordinator_form['frequency_unit']) }
            </div>
          </div>
        </div>

        <div class="fieldWrapper">
          <div class="row-fluid">
            <div class="span6">
              ${ utils.render_field(coordinator_form['start']) }
            </div>
            <div class="span6">
              ${ utils.render_field(coordinator_form['end']) }
             </div>
            </div>
            ${ utils.render_field(coordinator_form['timezone']) }
          </div>
        </div>
        <div class="span2"></div>
    </div>

    <div class="form-actions center">
      <a class="btn" onclick="history.back()">${ _('Back') }</a>
      <button data-bind="click: submit" class="btn btn-primary">${ _('Save') }</button>
    </div>

  </form>

</div>


<link rel="stylesheet" href="/static/ext/css/jquery-ui-datepicker-1.8.23.css" type="text/css" media="screen" title="no title" charset="utf-8" />
<link rel="stylesheet" href="/static/ext/css/jquery-timepicker.css" type="text/css" media="screen" title="no title" charset="utf-8" />

<script src="/static/ext/js/jquery/plugins/jquery-ui-datepicker-1.8.23.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/jquery/plugins/jquery-timepicker.min.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript" charset="utf-8">
  $(document).ready(function(){
    var timeOptions = {
      show24Hours: false,
      startTime: '00:00',
      endTime: '23:59',
      step: 60
    };
    $( "input.date" ).datepicker();
    $( "input.time" ).timePicker(timeOptions);
  });
</script>

${commonfooter(messages)}

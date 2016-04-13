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
  from oozie.models import DATASET_FREQUENCY
%>


<%namespace name="utils" file="../utils.inc.mako" />


<fieldset>
  ${ utils.render_field(dataset_form['name']) }
  ${ utils.render_field(dataset_form['description']) }

  <div class="row-fluid">
    <div class="span6">
      ${ utils.render_field(dataset_form['start']) }
    </div>
    <div class="span6">
      <div class="alert alert-warning">
        ${ _('UTC time only.') } ${ _('Recommended to be before the coordinator start date.') }
      </div>
    </div>
  </div>
  <div class="row-fluid">
    <div class="span6">
      ${ utils.render_field(dataset_form['frequency_number']) }
    </div>
    <div class="span6">
      ${ utils.render_field(dataset_form['frequency_unit']) }
    </div>
  </div>

  <div class="alert alert-info">
    ${ _('You can parameterize the values using') }
    % for frequency in DATASET_FREQUENCY:
      <code>${"${"}${ frequency }}</code>
      % if not loop.last:
        ,
      % endif
    % endfor
    .
  </div>
  ${ utils.render_field(dataset_form['uri']) }

  <%include file="dataset_utils.mako"/>

  ${ utils.render_field(dataset_form['timezone']) }
  ${ utils.render_field(dataset_form['done_flag']) }
</fieldset>

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

<%namespace name="utils" file="../utils.inc.mako" />
<%namespace name="layout" file="../navigation-bar.mako" />

${ commonheader(_("History Record"), "oozie", user, request) | n,unicode }
${ layout.menubar(section='history') }


<div class="container-fluid">
  <div class="card card-small">

  <h1 class="card-heading simple">${ _('History') } ${ record.job.name }</h1>

  <div class="card-body">
    <p>


  <div>
    <h2>${ _('Details') }</h2>
    <div class="row-fluid">
      <div class="span3">
        ${ _('Name') }
      </div>
      <div class="span3">
        <a href="${ record.job.get_absolute_url() }">${ record.job.name }</a>
      </div>
    </div>
    <div class="row-fluid">
      <div class="span3">
        ${ _('Id') }
      </div>
      <div class="span3">
        <a href="${ record.get_absolute_oozie_url() }">${ record.oozie_job_id }</a>
      </div>
    </div>
    <div class="row-fluid">
      <div class="span3">
        ${ _('Submitter') }
      </div>
      <div class="span3">
        ${ record.submitter.username }
      </div>
    </div>
    <div class="row-fluid">
      <div class="span3">
        ${ _('Type') }
      </div>
      <div class="span3">
        ${ record.job.get_type().title() }
      </div>
    </div>
    <div class="row-fluid">
      <div class="span3">
        ${ _('Submission Date') }
      </div>
      <div class="span3">
        ${ utils.format_date(record.submission_date) }
      </div>
    </div>
  </div>

  <div>
    <h2>${ _('Properties') }</h2>
    ${ utils.display_conf(record.properties_dict) }
  </div>

   <a href="${ url('oozie:list_history') }" class="btn">${ _('Back') }</a>

    </p>
  </div>
</div>
</div>

${ commonfooter(request, messages) | n,unicode }

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

${ commonheader(_("Create Workflow"), "oozie", user, request) | n,unicode }
${ layout.menubar(section='workflows') }


<div class="container-fluid">


  <div class="row-fluid">
    <div class="span2">
      <div id="workflowControls" class="sidebar-nav">
        <ul class="nav nav-list">
          <li class="nav-header">${ _('New workflow') }</li>
          <li class="active"><a href="#properties"><i class="fa fa-reorder"></i> ${ _('Properties') }</a></li>
        </ul>
      </div>
    </div>
    <div class="span10">
      <div class="card card-small">
        <div class="alert alert-info"><h3>${ _('Properties') }</h3></div>
          <div class="card-body">
            <p>
              <form class="form-horizontal" id="workflowForm" action="${ url('oozie:create_workflow') }" method="POST">
                ${ csrf_token(request) | n,unicode }
              <fieldset>
              ${ utils.render_field(workflow_form['name']) }
              ${ utils.render_field(workflow_form['description']) }

              <div class="control-group ">
                <label class="control-label">
                  <a href="#" id="advanced-btn" onclick="$('#advanced-container').toggle('hide')">
                    <i class="fa fa-share"></i> ${ _('advanced') }
                  </a>
                </label>
                <div class="controls"></div>
              </div>

                <div id="advanced-container" class="hide">
                  ${ utils.render_field(workflow_form['deployment_dir']) }
                  ${ utils.render_field(workflow_form['job_xml']) }
               </div>

               <div class="hide">
                 ${ utils.render_field(workflow_form['is_shared']) }
                 ${ workflow_form['schema_version'] | n,unicode }
                 ${ workflow_form['job_properties'] | n,unicode }
                 ${ workflow_form['parameters'] | n,unicode }
             </div>
             </fieldset>
              <div class="form-actions center">
                <input class="btn btn-primary" type="submit" value="${ _('Save') }" />
                <a class="btn" onclick="history.back()">${ _('Back') }</a>
              </div>
            </form>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>

${ utils.path_chooser_libs(True, True) }

<link rel="stylesheet" href="${ static('oozie/css/workflow.css') }">

<script>
  $(document).ready(function(){
    $("input[name='deployment_dir']").after(hueUtils.getFileBrowseButton($("input[name='deployment_dir']"), true));
    $("input[name='job_xml']").after(hueUtils.getFileBrowseButton($("input[name='job_xml']"), false));
  });
</script>

${ commonfooter(request, messages) | n,unicode }

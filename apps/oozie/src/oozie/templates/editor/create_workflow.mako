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
${ layout.menubar(section='workflows') }


<div class="container-fluid">
  <h1>${ _('Create Workflow') }</h1>

    <div class="well">
      <br/>
    </div>

    <div style="min-height:300px">
      <form class="form-horizontal" id="workflowForm" action="${ url('oozie:create_workflow') }" method="POST">

      <div class="row-fluid">
        <div class="span2">
        </div>
        <div class="span8">
          <h2>${ _('Properties') }</h2>
          <br/>
          <fieldset>
          ${ utils.render_field(workflow_form['name']) }
          ${ utils.render_field(workflow_form['description']) }

          <div class="control-group ">
            <label class="control-label">
              <a href="#" id="advanced-btn" onclick="$('#advanced-container').toggle('hide')">
                <i class="icon-share-alt"></i> ${ _('advanced') }
              </a>
            </label>
            <div class="controls"></div>
          </div>

            <div id="advanced-container" class="hide">
              ${ utils.render_field(workflow_form['is_shared']) }
              ${ utils.render_field(workflow_form['deployment_dir']) }
              ${ utils.render_field(workflow_form['job_xml']) }
           </div>

           <div class="hide">
             ${ workflow_form['schema_version'] }
             ${ workflow_form['job_properties'] }
             ${ workflow_form['parameters'] }
         </div>
         </fieldset>

        <div class="span2"></div>
        </div>
      </div>

      <div class="form-actions center">
        <a class="btn" onclick="history.back()">${ _('Back') }</a>
        <input class="btn btn-primary" type="submit" value="${ _('Save') }"></input>
      </div>
      </form>
    </div>
</div>

${ utils.path_chooser_libs(True) }

${ commonfooter(messages) }

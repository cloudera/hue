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
%>

<%namespace name="utils" file="../utils.inc.mako" />


<form action="${ action }" method="POST">
  ${ csrf_token(request) | n,unicode }
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
    <h2 class="modal-title">${ _('Submit this job?') }</h2>
  </div>
  <div class="modal-body">
    <fieldset>
      <div id="param-container">

       ${ params_form.management_form | n,unicode }

       % for form in params_form.forms:
          % for hidden in form.hidden_fields():
            ${ hidden | n,unicode }
          % endfor
          <div class="fieldWrapper">
            <div class="row-fluid
              % if form['name'].form.initial.get('name') == 'oozie.use.system.libpath':
                hide
              % endif
              ">
              <div class="span6">
                ${ form['name'].form.initial.get('name') }
              </div>
              <div class="span6">
                ${ utils.render_field(form['value'], show_label=False) }
              </div>
            </div>
          </div>
         % endfor
      </div>
    </fieldset>

    % if show_dryrun:
      <label class="checkbox" style="display: inline-block; margin-top: 5px">
        <input type="checkbox" name="dryrun_checkbox" /> ${ _('Do a dryrun before submitting the job?') }
      </label>
    % endif
  </div>
  <div class="modal-footer">
    <a href="#" class="btn" data-dismiss="modal">${ _('Cancel') }</a>
    <input id="submit-btn" type="submit" class="btn btn-primary" value="${ _('Submit') }"/>
  </div>
</form>

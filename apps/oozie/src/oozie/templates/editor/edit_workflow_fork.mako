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
  <h1>${ _('Workflow') } <a href="${ url('oozie:edit_workflow', workflow=workflow.id) }">${ workflow.name }</a>
    : ${ fork.node_type.title() } ${ fork }
  </h1>

  <br/>

  <form class="form-horizontal" action="${ url('oozie:edit_workflow_fork', action=fork.id) }" method="POST">
    <fieldset>

      % if not fork.has_decisions():
        <div class="control-group">
          <label class="control-label"></label>
          <div class="controls span8">
            <div class="alert alert-info">
              ${ _('You can convert this') } <code>${ _('Fork') }</code> ${ _('into a') } <code>${ _('Decision') }</code> ${ _('switch by adding some conditions on the branching.') }
            </div>
          </div>
        </div>
      % endif

      <div class="control-group">
        <label class="control-label"></label>
        <div class="controls span8">
          <div>${ _('Examples of predicates:') }</div>
          <div class="well">
            ${"${"} fs:fileSize(secondjobOutputDir) gt 10 * GB }
            <br/>
            ${"${"} hadoop:counters('secondjob')[RECORDS][REDUCE_OUT] lt 1000000 }
          </div>
        </div>
      </div>

      ${ link_formset.management_form }

      <div class="control-group">
        <label class="control-label"></label>
        <div class="controls">
          <table class="table-condensed">
            <thead>
              <tr>
                <th>${ _('Predicate') }</th>
                <th/>
                <th>${ _('Action') }</th>
              </tr>
            </thead>
            <tbody>
              % for form in link_formset.forms:
                  % for hidden in form.hidden_fields():
                    ${ hidden }
                  % endfor
              <tr>
                <td>
                  ${ utils.render_field(form['comment']) }
                </td>
                <td class="center">
                  ${ _('go to') }
                </td>
                <td class="right">
                  <a href="${ form.instance.child.get_full_node().get_edit_link() }" class="span3">${ form.instance.child }</a>
                </td>
              </tr>
              % endfor
                <tr>
                  <td>
             <div class="control-group">
                <label class="control-label"></label>
                <div class="controls span8">
                    <div>${ _('default') }</div>
                </div>
              </div>
                  </td>
                  <td class="center">
                  ${ _('go to') }
                  </td>
                  <td class="right">
                    ${ utils.render_field(default_link_form['child']) }
                  </td>
                </tr>
            </tbody>
          </table>
        </div>
      </div>

    </fieldset>

    <div class="form-actions">
      <a href="${ url('oozie:edit_workflow', workflow=workflow.id) }" class="btn">${ _('Cancel') }</a>
      <button data-bind="click: submit" class="btn btn-primary">${ _('Save') }</button>
    </div>

  </form>
</div>

${commonfooter(messages)}

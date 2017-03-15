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
  from desktop.views import _ko
%>

<%namespace name="utils" file="../utils.inc.mako" />


<%def name="fork_convert_form(node_type, template=True, javascript_attrs={})">
% if template:
  <script type="text/html" id="${node_type}ConvertTemplate">
% endif
  <div data-bind="with: context().node">
    <form class="form-horizontal" id="${node_type}-convert-form" method="POST">
      ${ csrf_token(request) | n,unicode }
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
        <h2 class="modal-title message" data-bind="text: '${_ko('Edit Node: ')}' + name()"></h2>
      </div>

      <div class="modal-content">
        <div class="alert alert-info">
          ${ _('Convert this fork into a decision?') }
        </div>
      </div>

      <div class="modal-footer">
        <button data-dismiss="modal" class="btn">${ _('No')}</button>
        % if 'convert' in javascript_attrs:
          <button data-dismiss="modal" class="btn btn-primary" data-bind="visible: !$root.context().read_only, click: ${ javascript_attrs['convert'] }">${ _('Yes') }</button>
        % endif
      </div>

    </form>
  </div>

% if template:
  </script>
% endif
</%def>


<%def name="fork_edit_form(form, node_type, template=True, javascript_attrs={})">
% if template:
  <script type="text/html" id="${node_type}EditTemplate">
% endif
  <div data-bind="with: context().node">
    <form class="form-horizontal" id="${node_type}-action-form" method="POST">
      ${ csrf_token(request) | n,unicode }
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
        <h2 class="modal-title message" data-bind="text: '${_ko('Edit Node: ')}' + name()"></h2>
      </div>

      <div class="modal-content">
        <div class="container-fluid">
          <div class="row-fluid">
            <fieldset class="span12">
              % for field in form:
                % if field.html_name in ('name', 'description'):
                  ${ utils.render_field_with_error_js(field, field.name, extra_attrs={'class': 'input-xlarge', 'data-bind': 'disable: $root.context().read_only, value: %s' % field.name}) }
                % endif
              % endfor
            </fieldset>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <a class="btn cancelButton" href="javascript:void(0);">Cancel</a>
        <button class="btn btn-primary doneButton" type="button" data-bind="visible: !$root.context().read_only">${ _('Done')}</button>
      </div>

    </form>
  </div>

% if template:
  </script>
% endif
</%def>


<%def name="decision_form(node_form, link_form, default_link_form, node_type, template=True, javascript_attrs={})">
% if template:
  <script type="text/html" id="${node_type}EditTemplate">
% endif
  <div data-bind="with: context().node">
    <form class="form-horizontal" id="${node_type}-action-form" method="POST">
      ${ csrf_token(request) | n,unicode }
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
        <h2 class="modal-title message" data-bind="text: '${_ko('Edit Node: ')}' + name()"></h2>
      </div>

      <div class="modal-content">
        <div class="container-fluid">
          <div class="row-fluid">
            <fieldset class="span12">
          % for field in node_form:
            % if field.html_name in ('name', 'description'):
              ${ utils.render_field_with_error_js(field, field.name, extra_attrs={'class': 'input-xlarge', 'data-bind': 'disable: $root.context().read_only, value: %s' % field.name}) }
            % endif
          % endfor

          <div class="control-group">
            <label class="control-label"></label>
            <div class="controls">
              <div style="padding: 10px; background-color: #EEEEEE">
                <strong>${ _('Examples of predicates:') }</strong><br/>
                ${"${"} fs:fileSize(secondjobOutputDir) gt 10 * GB }
                <br/>
                ${"${"} hadoop:counters('secondjob')[RECORDS][REDUCE_OUT] lt 1000000 }
                <br/>
                <a href="http://oozie.apache.org/docs/3.3.0/WorkflowFunctionalSpec.html#a4.2_Expression_Language_Functions">${ _('More on predicates') }</a>
              </div>
            </div>
          </div>

          <table class="table-condensed">
            <thead>
              <tr>
                <th>${ _('Predicate') }</th>
                <th/>
                <th>${ _('Action') }</th>
              </tr>
            </thead>
            <tbody>
              <!-- ko foreach: links() -->
              <tr>
                <td>
                  ${ utils.render_field(link_form['comment'], extra_attrs={'class': 'input-xxlarge', 'data-bind': 'value: comment'}, control_extra='style=margin-bottom:0') }
                </td>
                <td class="center" style="vertical-align: middle">
                  ${ _('go to') }
                </td>
                <td style="vertical-align: middle">
                  <a class="edit-node-link" data-bind="text: $parent.registry.get(child()).name()"></a>
                </td>
              </tr>
              <!-- /ko -->

              <!-- ko foreach: meta_links() -->
                <!-- ko if: $data.name() == 'default' -->
                <tr>
                  <td>
                   <div class="control-group" style="margin-bottom: 0">
                      <label class="control-label"></label>
                      <div class="controls">
                        <div>${ _('default') }</div>
                      </div>
                    </div>
                  </td>
                  <td class="center nowrap" style="vertical-align: middle">
                    ${ _('go to') }
                  </td>
                  <td>
                    ${ utils.render_field(default_link_form['child'], extra_attrs={'class': 'input-xxlarge', 'data-bind': 'value: child'}, control_extra='style=margin-bottom:0', show_label=False) }
                  </td>
                </tr>
                <!-- /ko -->
              <!-- /ko -->
            </tbody>
          </table>

        </fieldset>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <a class="btn cancelButton" href="javascript:void(0);">Cancel</a>
        <button class="btn btn-primary doneButton" type="button" data-bind="visible: !$root.context().read_only">${ _('Done')}</button>
      </div>

    </form>
  </div>

% if template:
  </script>
% endif
</%def>


<%def name="links_form_fields(link_form, default_link_form, javascript_attrs={})">

<div class="control-group" rel="popover" data-original-title="${ field.label }" data-content="${ field.help_text }">
  <label class="control-label">${ _('Params') }</label>
  <div class="controls">
    % if 'name' in javascript_attrs:
      <table class="table-condensed designTable" data-bind="visible: ${ javascript_attrs['name'] }().length > 0">
        <thead>
          <tr>
            <th>${ _('Type') }</th>
            <th>${ _('Value') }</th>
            <th/>
          </tr>
        </thead>
        <tbody data-bind="foreach: ${ javascript_attrs['name'] }">
          <tr>
            <td>
              <span class="span4 required" data-bind="text: type" />
            </td>
            <td>
              <input type="text" class="input-xxlarge required" data-bind="fileChooser: $data, value: value, uniqueName: false" />
            </td>
            <td>
            % if 'remove' in javascript_attrs:
              <a class="btn" href="#" data-bind="click: ${ javascript_attrs['remove'] }">${ _('Delete') }</a>
            % endif
            </td>
          </tr>
        </tbody>
      </table>

      % if 'add' in javascript_attrs:
        % for method in javascript_attrs['add']:
          <button class="btn" data-bind="click: ${ method['method'] }">${ _(method['label']) }</button>
        % endfor
      % endif
    % endif
  </div>
</div>
</%def>

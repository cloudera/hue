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

<%namespace name="utils" file="../utils.inc.mako" />


<%def name="import_jobsub_form(template=True)">
% if template:
  <script type="text/html" id="ImportNodeTemplate">
% endif

  <div data-bind="with: context().node">
    <form class="form-horizontal" id="import-node-form" method="POST">
      <div class="modal-header">
        <a href="#" class="close">&times;</a>
        <h3 class="message">${_('Import Action')}</h3>
      </div>

      <div class="modal-content">
        <fieldset class="span12">
          <table id="jobdesignerActionsTable" class="table datatables">
            <thead>
              <tr>
                <th></th>
                <th>${ _('Name') }</th>
                <th>${ _('Description') }</th>
              </tr>
            </thead>
            <tbody data-bind="visible: available_nodes().length > 0, foreach: available_nodes">
              <tr class="action-row">
                <td class=".btn-large action-column" data-row-selector-exclude="true" style="background-color: white;">
                  <input type="radio" name="jobsub_id" data-bind="attr: { 'value': id }, click: $parent.setJobDesignerId, disable: $root.context().read_only" />
                </td>
                <td data-bind="text: $data.name"></td>
                <td data-bind="text: $data.description"></td>
              </tr>
            </tbody>
            <tbody data-bind="visible: available_nodes().length == 0">
              <tr class="action-row">
                <td>${ _('N/A') }</td><td></td><td></td>
              </tr>
            </tbody>
          </table>
        </fieldset>
      </div>

      <div class="modal-footer">
        <a class="btn cancelButton" href="javascript:void(0);">${ _('Cancel') }</a>
        <button class="btn btn-primary doneButton" type="button" data-bind="visible: !$root.context().read_only">${ _('Import') }</button>
      </div>

    </form>
  </div>

  <script src="/static/ext/js/datatables-paging-0.1.js" type="text/javascript" charset="utf-8"></script>

  <script type="text/javascript" charset="utf-8">
    $(document).ready(function() {
      $(".action-row").click(function(e){
        var select_btn = $(this).find('input');
        select_btn.prop("checked", true);

        $(".action-row").css("background-color", "");
        $(this).css("background-color", "#ECF4F8");
      });

      $("a[data-row-selector='true']").jHueRowSelector();
    });
  </script>

% if template:
  </script>
% endif
</%def>

<%def name="action_form(action_form, node_type, template=True)">
% if template:
  <script type="text/html" id="${node_type}EditTemplate">
% endif
  <div data-bind="with: context().node">
    <form class="form-horizontal" id="${node_type}-action-form" method="POST">
      <div class="modal-header">
        <a href="#" class="close">&times;</a>
        <h3 class="message" data-bind="text: '${_('Edit Node: ')}' + name()"></h3>
      </div>

      <div class="modal-content">
        <fieldset class="span12">
          % for field in action_form:
            % if field.html_name in ('name', 'description'):
              ${ utils.render_field_with_error_js(field, field.name, extra_attrs={'data-bind': 'disable: $root.context().read_only, value: %s' % field.name}) }
            % endif
          % endfor

          ${ utils.render_constant(_('Action type'), node_type) }

          <hr/>

          <div class="control-group">
            <label class="control-label"></label>
            <div class="controls">
            <p class="alert alert-info span7">
              % if node_type != 'fs':
                ${ _('All the paths are relative to the deployment directory. They can be absolute but this is not recommended.') }
              % else:
                ${ _('All the paths need to be absolute.') }
              % endif
              <br/>
              ${ _('You can parameterize values using case sensitive') } <code>${"${"}parameter}</code>.
            </p>
            % if node_type == 'ssh':
              <p class="alert alert-warn span5">
                ${ _('The ssh server requires passwordless login') }.
              </p>
            % endif
            % if node_type == 'java':
              % if get_oozie().security_enabled:
                <p class="alert alert-warn span5">
                  ${ _('The delegation token needs to be propagated from the launcher job to the MR job') }.
                  <a href="https://issues.apache.org/jira/browse/OOZIE-1172">OOZIE-1172</a>
                </p>
              % endif
            % endif
            % if node_type == 'email':
              <p class="alert alert-warn span5">
                ${ _('Requires some SMTP server configuration to be present (in oozie-site.xml)') }.
              </p>
            % endif
            </div>
          </div>

          % for field in action_form:
            % if field.html_name not in ('name', 'description', 'node_type', 'job_xml'):
              % if field.html_name in ('capture_output', 'is_single', 'sub_workflow'):
                ${ utils.render_field_with_error_js(field, field.name, extra_attrs={'data-bind': 'disable: $root.context().read_only, checked: %s' % field.name}) }
              % else:
                ${ utils.render_field_with_error_js(field, field.name, extra_attrs={'data-bind': 'disable: $root.context().read_only, value: %s' % field.name}) }
              % endif
            % endif
          % endfor

          % if 'prepares' in action_form.fields:
            <%
              prepares_field(action_form['prepares'], {
                'name': 'prepares',
                'add': [
                  {'label': _('Add delete'), 'method': 'addPrepareDelete'},
                  {'label': _('Add mkdir'), 'method': 'addPrepareMkdir'},
                ],
                'remove': '$parent.removePrepare'
              })
            %>
          % endif

          % if 'params' in action_form.fields:
            % if node_type == 'pig':
              <%
              params_field(action_form['params'], {
                'name': 'params',
                'add': [
                  {'label': _('Add Param'), 'method': 'addParam'},
                  {'label': _('Add Argument'), 'method': 'addArgument'},
                ],
                'remove': '$parent.removeParam'
              })
              %>
            % endif

            % if node_type == 'shell':
              <%
              params_field(action_form['params'], {
                'name': 'params',
                'add': [
                  {'label': _('Add Argument'), 'method': 'addArgument'},
                  {'label': _('Add Env-Var'), 'method': 'addEnvVar'},
                ],
                'remove': '$parent.removeParam'
              })
              %>
            % endif

            % if node_type == 'hive':
              <%
              params_field(action_form['params'], {
                'name': 'params',
                'add': [
                  {'label': _('Add Param'), 'method': 'addParam'},
                ],
                'remove': '$parent.removeParam'
              })
              %>
            % endif

            % if node_type == 'distcp':
              <%
              params_field(action_form['params'], {
                'name': 'params',
                'add': [
                  {'label': _('Add Argument'), 'method': 'addArgument'},
                ],
                'remove': '$parent.removeParam'
              })
              %>
            % endif

            % if node_type in ('sqoop', 'ssh'):
              <%
              params_field(action_form['params'], {
                'name': 'params',
                'add': [
                  {'label': _('Add Arg'), 'method': 'addArg'},
                ],
                'remove': '$parent.removeParam'
              })
              %>
            % endif
          % endif

          % if 'job_properties' in action_form.fields:
            <%
            job_properties_field(action_form['job_properties'], {
              'name': 'job_properties',
              'add': 'addProp',
              'remove': '$parent.removeProp'
            })
            %>
          % endif

          % if 'files' in action_form.fields:
            <%
            file_field(action_form['files'], {
              'name': 'files',
              'add': 'addFile',
              'remove': '$parent.removeFile'
            })
            %>
          % endif

          % if 'archives' in action_form.fields:
            <%
            archives_field(action_form['archives'], {
              'name': 'archives',
              'add': 'addArchive',
              'remove': '$parent.removeArchive'
            })
            %>
          % endif

          % if 'job_xml' in action_form.fields:
            ${ utils.render_field_with_error_js(action_form['job_xml'], action_form['job_xml'].name, extra_attrs={'data-bind': 'disable: $root.context().read_only, value: %s' % action_form['job_xml'].name}) }
          % endif

          % if 'deletes' in action_form.fields:
            <%
            file_field(action_form['deletes'], {
              'name': 'deletes',
              'add': 'addDelete',
              'remove': '$parent.removeDelete'
            })
            %>
          % endif

          % if 'mkdirs' in action_form.fields:
            <%
            file_field(action_form['mkdirs'], {
              'name': 'mkdirs',
              'add': 'addMkdir',
              'remove': '$parent.removeMkdir'
            })
            %>
          % endif

          % if 'moves' in action_form.fields:
            <%
            move_field(action_form['moves'], {
              'name': 'moves',
              'add': 'addMove',
              'remove': '$parent.removeMove'
            })
            %>
          % endif

          % if 'chmods' in action_form.fields:
            <%
            chmod_field(action_form['chmods'], {
              'name': 'chmods',
              'add': 'addChmod',
              'remove': '$parent.removeChmod'
            })
            %>
          % endif

          % if 'touchzs' in action_form.fields:
            <%
            file_field(action_form['touchzs'], {
              'name': 'touchzs',
              'add': 'addTouchz',
              'remove': '$parent.removeTouchz'
            })
            %>
          % endif

        </fieldset>
      </div>

      <div class="modal-footer">
        <a class="btn cancelButton" href="javascript:void(0);">Cancel</a>
        <button class="btn btn-primary doneButton disable-feedback" type="button" data-bind="visible: !$root.context().read_only">${ _('Done')}</button>
      </div>

    </form>
  </div>
% if template:
  </script>
% endif
</%def>

<%def name="file_field(field, javascript_attrs={})">
<div class="control-group" rel="popover" data-original-title="${ field.label }" data-content="${ field.help_text }">
  <label class="control-label">${ field.label }</label>
  <div class="controls">
    % if 'name' in javascript_attrs:
      <table class="table-condensed designTable" data-bind="visible: ${ javascript_attrs['name'] }().length > 0">
        <tbody data-bind="foreach: ${ javascript_attrs['name'] }">
          <tr>
            <td>
              <input type="text" class="span5 required pathChooserKo" data-bind="disable: $root.context().read_only, fileChooser: $data, value: name, uniqueName: false" />
            </td>
            <td>
              % if 'remove' in javascript_attrs:
                <a class="btn" href="#" data-bind="disable: $root.context().read_only, click: ${ javascript_attrs['remove'] }">${ _('Delete') }</a>
              % endif
            </td>
          </tr>
        </tbody>
      </table>

      % if 'add' in javascript_attrs:
        <button class="btn" data-bind="disable: $root.context().read_only, click: ${ javascript_attrs['add'] }">${ _('Add Path') }</button>
      % endif
    % endif
  </div>
</div>
</%def>

<%def name="archives_field(field, javascript_attrs={})">
<div class="control-group" rel="popover" data-original-title="${ field.label }" data-content="${ field.help_text }">
  <label class="control-label">${ _('Archives') }</label>
  <div class="controls">
    % if 'name' in javascript_attrs:
      <table class="table-condensed designTable" data-bind="visible: ${ javascript_attrs['name'] }().length > 0">
        <tbody data-bind="foreach: ${ javascript_attrs['name'] }">
          <tr>
            <td>
              <input type="text" class="span5 required pathChooserKo" data-bind="disable: $root.context().read_only, fileChooser: $data, value: name, uniqueName: false" />
            </td>
            <td>
              % if 'remove' in javascript_attrs:
                <a class="btn" href="#" data-bind="disable: $root.context().read_only, click: ${ javascript_attrs['remove'] }">${ _('Delete') }</a>
              % endif
            </td>
          </tr>
        </tbody>
      </table>

      % if 'add' in javascript_attrs:
        <button class="btn" data-bind="disable: $root.context().read_only, click: ${ javascript_attrs['add'] }">${ _('Add Archive') }</button>
      % endif
    % endif
  </div>
</div>
</%def>

<%def name="job_properties_field(field, javascript_attrs={})">
<div class="control-group" rel="popover" data-original-title="${ field.label }" data-content="${ field.help_text }">
  <label class="control-label">${ _('Job Properties') }</label>
  <div class="controls">
    % if 'name' in javascript_attrs:
      <table class="table-condensed designTable" data-bind="visible: ${ javascript_attrs['name'] }().length > 0">
        <thead>
          <tr>
            <th>${ _('Property name') }</th>
            <th>${ _('Value') }</th>
            <th/>
          </tr>
        </thead>
        <tbody data-bind="foreach: ${ javascript_attrs['name'] }">
          <tr>
            <td><input type="text" class="span4 required propKey" data-bind="disable: $root.context().read_only, value: name, uniqueName: false" /></td>
            <td><input type="text" class="span4 required pathChooserKo" data-bind="disable: $root.context().read_only, fileChooser: $data, value: value, uniqueName: false" /></td>
            <td>
            % if 'remove' in javascript_attrs:
              <a class="btn" href="#" data-bind="disable: $root.context().read_only, click: ${ javascript_attrs['remove'] }">${ _('Delete') }</a>
            % endif
            </td>
          </tr>
        </tbody>
      </table>

      % if 'add' in javascript_attrs:
        <button class="btn" data-bind="disable: $root.context().read_only, click: ${ javascript_attrs['add'] }">${ _('Add Property') }</button>
      % endif
    % endif
  </div>
</div>
</%def>

<%def name="move_field(field, javascript_attrs={})">
<div class="control-group" rel="popover" data-original-title="${ field.label }" data-content="${ field.help_text }">
  <label class="control-label">${ field.label }</label>
  <div class="controls">
    % if 'name' in javascript_attrs:
      <table class="table-condensed designTable" data-bind="visible: ${ javascript_attrs['name'] }().length > 0">
        <thead>
          <tr>
            <th>${ _('Source') }</th>
            <th>${ _('Destination') }</th>
            <th/>
          </tr>
        </thead>
        <tbody data-bind="foreach: ${ javascript_attrs['name'] }">
          <tr>
            <td><input type="text" class="span4 required propKey" data-bind="disable: $root.context().read_only, fileChooser: $data, value: source, uniqueName: false" /></td>
            <td><input type="text" class="span4 required pathChooserKo" data-bind="disable: $root.context().read_only, fileChooser: $data, value: destination, uniqueName: false" /></td>
            <td>
            % if 'remove' in javascript_attrs:
              <a class="btn" href="#" data-bind="disable: $root.context().read_only, click: ${ javascript_attrs['remove'] }">${ _('Delete') }</a>
            % endif
            </td>
          </tr>
        </tbody>
      </table>

      % if 'add' in javascript_attrs:
        <button class="btn" data-bind="disable: $root.context().read_only, click: ${ javascript_attrs['add'] }">${ _('Add move') }</button>
      % endif
    % endif
  </div>
</div>
</%def>

<%def name="chmod_field(field, javascript_attrs={})">
<div class="control-group" rel="popover" data-original-title="${ field.label }" data-content="${ field.help_text }">
  <label class="control-label">${ field.label }</label>
  <div class="controls">
    % if 'name' in javascript_attrs:
      <table class="table-condensed designTable" data-bind="visible: ${ javascript_attrs['name'] }().length > 0">
        <thead>
          <tr>
            <th>${ _('Path') }</th>
            <th>${ _('Permissions') }</th>
            <th>${ _('Recursive') }</th>
            <th/>
          </tr>
        </thead>
        <tbody data-bind="foreach: ${ javascript_attrs['name'] }">
          <tr>
            <td><input type="text" class="span4 required pathChooserKo" data-bind="disable: $root.context().read_only, fileChooser: $data, value: path, uniqueName: false" /></td>
            <td><input type="text" class="span2 required propKey" data-bind="disable: $root.context().read_only, value: permissions, uniqueName: false" /></td>
            <td><input type="checkbox" class="span1 required" data-bind="disable: $root.context().read_only, checked: recursive, uniqueName: false" /></td>
            <td>
            % if 'remove' in javascript_attrs:
              <a class="btn" href="#" data-bind="disable: $root.context().read_only, click: ${ javascript_attrs['remove'] }">${ _('Delete') }</a>
            % endif
            </td>
          </tr>
        </tbody>
      </table>

      % if 'add' in javascript_attrs:
        <button class="btn" data-bind="disable: $root.context().read_only, click: ${ javascript_attrs['add'] }">${ _('Add chmod') }</button>
      % endif
    % endif
  </div>
</div>
</%def>

<%def name="params_field(field, javascript_attrs={})">
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
              <input type="text" class="input span4 required pathChooserKo" data-bind="disable: $root.context().read_only, fileChooser: $data, value: value, uniqueName: false" />
            </td>
            <td>
            % if 'remove' in javascript_attrs:
              <a class="btn" href="#" data-bind="disable: $root.context().read_only, click: ${ javascript_attrs['remove'] }">${ _('Delete') }</a>
            % endif
            </td>
          </tr>
        </tbody>
      </table>

      % if 'add' in javascript_attrs:
        % for method in javascript_attrs['add']:
          <button class="btn" data-bind="disable: $root.context().read_only, click: ${ method['method'] }">${ _(method['label']) }</button>
        % endfor
      % endif
    % endif
  </div>
</div>
</%def>

<%def name="prepares_field(field, javascript_attrs={})">
<div class="control-group" rel="popover" data-original-title="${ field.label }" data-content="${ field.help_text }">
  <label class="control-label">${ _('Prepare') }</label>
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
              <input type="text" class="input span4 required pathChooserKo" data-bind="disable: $root.context().read_only, fileChooser: $data, value: value, uniqueName: false" />
            </td>
            <td>
              % if 'remove' in javascript_attrs:
                <a class="btn" href="#" data-bind="disable: $root.context().read_only, click: ${ javascript_attrs['remove'] }">${ _('Delete') }</a>
              % endif
            </td>
          </tr>
        </tbody>
      </table>

      % if 'add' in javascript_attrs:
        % for method in javascript_attrs['add']:
          <button class="btn" data-bind="disable: $root.context().read_only, click: ${ method['method'] }">${ _(method['label']) }</button>
        % endfor
      % endif
    % endif
  </div>
</div>
</%def>

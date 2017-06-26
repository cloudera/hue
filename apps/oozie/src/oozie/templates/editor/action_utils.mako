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
  from desktop.views import _ko
%>

<%namespace name="utils" file="../utils.inc.mako" />


<%def name="action_form_modal_template(action_form, node_type, template=True)">
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
              ${ action_form_fields(action_form, node_type) }
            </fieldset>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <a class="btn cancelButton" href="javascript:void(0);">${_('Cancel')}</a>
        <button class="btn btn-primary doneButton disable-feedback" type="button" data-bind="visible: !$root.context().read_only">${ _('Done')}</button>
      </div>

    </form>
  </div>
% if template:
  </script>
% endif
</%def>

<%def name="action_form_fields(action_form, node_type, show_primary=True)">
% if show_primary:
  % for field in action_form:
    % if field.html_name in ('name', 'description'):
      ${ utils.render_field_with_error_js(field, field.name, extra_attrs={'class': 'input-xlarge', 'data-bind': 'disable: $root.context().read_only, value: %s' % field.name}) }
    % endif
  % endfor

  ${ utils.render_constant(_('Action type'), node_type) }


  <div class="control-group ">
    <label class="control-label">
      <a href="javascript:void(0);" id="advanced-btn" onclick="$('#node-advanced-container').toggle('hide')">
        <i class="fa fa-share"></i> ${ _('Advanced') }</a>
    </label>
    <div class="controls"></div>
  </div>

  <div id="node-advanced-container" class="hide">

    <div class="control-group">
      <label class="control-label">${ _('SLA Configuration') }</label>
      <div class="controls">
          ${ utils.slaForm() }
      </div>
    </div>

    <div class="control-group" data-bind="visible: credentials().length > 0">
      <label class="control-label">${ _('Credentials') }</label>
      <div class="controls">
          <div data-bind="foreach: credentials">
            <div class="control-group control-row" style="margin-bottom: 2px">
              <label class="control-label" data-bind="text: name"></label>
              <div class="controls">
                <input type="checkbox" data-bind="checked: value"/>
                <span data-bind="visible: name() == 'hbase'">${ _('Requires hbase-site.xml in job-xml field') }</span>
              </div>
            </div>
          </div>
      </div>
    </div>

    <!-- ko if: $root.context().nodes && $root.context().error_node -->
    <div class="control-group">
      <label class="control-label">${_('Error link to')}</label>
      <div class="controls">
        <div style="padding-top:4px">
          <select data-bind="options: $root.context().nodes,
                             optionsText: function(item) {
                               return (item.name()) ? item.name() : item.node_type() + '-' + item.id();
                             },
                             optionsValue: function(item) {
                               return item.id();
                             },
                             value: $root.context().error_node">
           </select>
        </div>
      </div>
    </div>
    <!-- /ko -->

  </div>


  <hr/>
% endif

<div class="control-group">
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
    <br style="clear: both" />
    <p class="alert alert-warn span5">
      ${ _('The SSH server requires passwordless login') }.
    </p>
  % endif
  % if node_type == 'java':
    % if oozie_api.security_enabled:
    <br style="clear: both" />
      <p class="alert alert-warn span5">
        ${ _('The delegation token needs to be propagated from the launcher job to the MR job') }.
        <a href="https://issues.apache.org/jira/browse/OOZIE-1172">OOZIE-1172</a>
      </p>
    % endif
  % endif
  % if node_type == 'email':
    <br style="clear: both" />
    <p class="alert alert-warn span5">
      ${ _('Requires some SMTP server configuration to be present (in oozie-site.xml)') }.
    </p>
  % endif
  </div>
</div>

% for field in action_form:
  % if field.html_name not in ('name', 'description', 'node_type', 'job_xml'):
    % if field.html_name in ('capture_output', 'is_single', 'sub_workflow', 'propagate_configuration'):
      ${ utils.render_field_with_error_js(field, field.name, extra_attrs={'class': 'span11', 'data-bind': 'disable: $root.context().read_only, checked: %s' % field.name}) }
    % else:
      ${ utils.render_field_with_error_js(field, field.name, extra_attrs={'class': 'span11', 'data-bind': 'disable: $root.context().read_only, valueUpdate:"afterkeydown", value: %s' % field.name}) }
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
      'remove': '$parent.removePrepare.bind($parent)'
    })
  %>
% endif

% if 'params' in action_form.fields:
  % if node_type == 'pig':
    <%
    params_field(action_form['params'], {
      'name': 'params',
      'add': [
        {'label': _('Add param'), 'method': 'addParam'},
        {'label': _('Add argument'), 'method': 'addArgument'},
      ],
      'remove': '$parent.removeParam.bind($parent)'
    })
    %>
  % endif

  % if node_type == 'shell':
    <%
    params_field(action_form['params'], {
      'name': 'params',
      'add': [
        {'label': _('Add argument'), 'method': 'addArgument'},
        {'label': _('Add env-var'), 'method': 'addEnvVar'},
      ],
      'remove': '$parent.removeParam.bind($parent)'
    })
    %>
  % endif

  % if node_type == 'hive':
    <%
    params_field(action_form['params'], {
      'name': 'params',
      'add': [
        {'label': _('Add param'), 'method': 'addParam'},
      ],
      'remove': '$parent.removeParam.bind($parent)'
    })
    %>
  % endif

  % if node_type == 'distcp':
    <%
    params_field(action_form['params'], {
      'name': 'params',
      'add': [
        {'label': _('Add argument'), 'method': 'addArgument'},
      ],
      'remove': '$parent.removeParam.bind($parent)'
    })
    %>
  % endif

  % if node_type in ('sqoop', 'ssh'):
    <%
    params_field(action_form['params'], {
      'name': 'params',
      'add': [
        {'label': _('Add arg'), 'method': 'addArg'},
      ],
      'remove': '$parent.removeParam.bind($parent)'
    })
    %>
  % endif
% endif

% if 'job_properties' in action_form.fields:
  <%
  job_properties_field(action_form['job_properties'], {
    'name': 'job_properties',
    'add': 'addProperty',
    'remove': '$parent.removeProperty.bind($parent)'
  })
  %>
% endif

% if 'files' in action_form.fields:
  <%
  file_field(action_form['files'], {
    'name': 'files',
    'add': 'addFile',
    'remove': '$parent.removeFile.bind($parent)'
  })
  %>
% endif

% if 'archives' in action_form.fields:
  <%
  archives_field(action_form['archives'], {
    'name': 'archives',
    'add': 'addArchive',
    'remove': '$parent.removeArchive.bind($parent)'
  })
  %>
% endif

% if 'job_xml' in action_form.fields:
  ${ utils.render_field_with_error_js(action_form['job_xml'], action_form['job_xml'].name, extra_attrs={'data-bind': 'disable: $root.context().read_only, fileChooser: $data, value: %s' % action_form['job_xml'].name}) }
% endif

% if 'deletes' in action_form.fields:
  <%
  file_field(action_form['deletes'], {
    'name': 'deletes',
    'add': 'addDelete',
    'remove': '$parent.removeDelete.bind($parent)'
  })
  %>
% endif

% if 'mkdirs' in action_form.fields:
  <%
  file_field(action_form['mkdirs'], {
    'name': 'mkdirs',
    'add': 'addMkdir',
    'remove': '$parent.removeMkdir.bind($parent)'
  })
  %>
% endif

% if 'moves' in action_form.fields:
  <%
  move_field(action_form['moves'], {
    'name': 'moves',
    'add': 'addMove',
    'remove': '$parent.removeMove.bind($parent)'
  })
  %>
% endif

% if 'chmods' in action_form.fields:
  <%
  chmod_field(action_form['chmods'], {
    'name': 'chmods',
    'add': 'addChmod',
    'remove': '$parent.removeChmod.bind($parent)'
  })
  %>
% endif

% if 'touchzs' in action_form.fields:
  <%
  file_field(action_form['touchzs'], {
    'name': 'touchzs',
    'add': 'addTouchz',
    'remove': '$parent.removeTouchz.bind($parent)'
  })
  %>
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
              <input type="text" class="input-xxlarge required pathChooserKo" data-bind="disable: $root.context().read_only, fileChooser: $data, value: name, uniqueName: false" />
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
        <button class="btn" data-bind="disable: $root.context().read_only, click: ${ javascript_attrs['add'] }">${ _('Add path') }</button>
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
              <input type="text" class="input-xxlarge required pathChooserKo" data-bind="disable: $root.context().read_only, fileChooser: $data, value: name, uniqueName: false" />
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
        <button class="btn" data-bind="disable: $root.context().read_only, click: ${ javascript_attrs['add'] }">${ _('Add archive') }</button>
      % endif
    % endif
  </div>
</div>
</%def>

<%def name="job_properties_field(field, javascript_attrs={})">
<div class="control-group" rel="popover" data-original-title="${ field.label }" data-content="${ field.help_text }">
  <label class="control-label">${ _('Job properties') }</label>
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
            <td><input type="text" class="input-xlarge required propKey" data-bind="disable: $root.context().read_only, value: name, uniqueName: false" /></td>
            <td><input type="text" class="input-xlarge required pathChooserKo" data-bind="disable: $root.context().read_only, fileChooser: $data, value: value, uniqueName: false" /></td>
            <td>
            % if 'remove' in javascript_attrs:
              <a class="btn" href="#" data-bind="disable: $root.context().read_only, click: ${ javascript_attrs['remove'] }">${ _('Delete') }</a>
            % endif
            </td>
          </tr>
        </tbody>
      </table>

      % if 'add' in javascript_attrs:
        <button class="btn" data-bind="disable: $root.context().read_only, click: ${ javascript_attrs['add'] }">${ _('Add property') }</button>
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
            <td><input type="text" class="input-xlarge required propKey" data-bind="disable: $root.context().read_only, fileChooser: $data, value: source, uniqueName: false" /></td>
            <td><input type="text" class="input-xlarge required pathChooserKo" data-bind="disable: $root.context().read_only, fileChooser: $data, value: destination, uniqueName: false" /></td>
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
            <td><input type="text" class="input-xlarge required pathChooserKo" data-bind="disable: $root.context().read_only, fileChooser: $data, value: path, uniqueName: false" /></td>
            <td><input type="text" class="input-xlarge required propKey" data-bind="disable: $root.context().read_only, value: permissions, uniqueName: false" /></td>
            <td><input type="checkbox" class="input-medium required" data-bind="disable: $root.context().read_only, checked: recursive, uniqueName: false" /></td>
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
              <input type="text" class="input-xxlarge required pathChooserKo" data-bind="disable: $root.context().read_only, fileChooser: $data, value: value, uniqueName: false" />
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
              <input type="text" class="input-xxlarge required pathChooserKo" data-bind="disable: $root.context().read_only, fileChooser: $data, value: value, uniqueName: false" />
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

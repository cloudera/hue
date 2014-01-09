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
<%def name="render_error(err)">
  <div>
    ${unicode(err) | n}
  </div>
</%def>

<%def name="render_field(field)">
  % if field.is_hidden:
    ${unicode(field) | n}
  % else:
    <dt>${field.label_tag() | n}</dt>
    <dd>${unicode(field) | n}</dd>
    % if len(field.errors):
      <dd>
        ${render_error(field.errors)}
      </dd>
    % endif
  % endif
</%def>

<%def name="render_formset(formset)">
  <dl>
  % for f in formset.forms:
    ${render_form(f)}
  % endfor
  ${unicode(formset.management_form) | n }
  </dl>
</%def>

<%def name="render_form(form)">
  % for err in form.non_field_errors():
    ${render_error(err)}
  % endfor

  % for field in form:
    ${render_field(field)}
  % endfor
</%def>

<%def name="render_query_context(query_context)">
  % if query_context:
    % if query_context[0] == 'table':
      <% tablename, database = query_context[1].split(':') %>
      <a href="${ url(app_name + ':describe_table', database, tablename) }">${tablename}</a>
    % elif query_context[0] == 'design':
      <% design = query_context[1] %>
      % if design.is_auto:
		<a href="${ url(app_name + ':execute_design', design.id)}">${_('Unsaved Query')}</a>
      % else:
        <a href="${ url(app_name + ':execute_design', design.id)}">${design.name}</a>
      % endif
    % else:
      ${_('Query Results')}
    % endif
  % endif
</%def>

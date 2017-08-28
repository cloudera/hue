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
  from desktop.lib.django_util import extract_field_data
%>

<%def name="render_field(
  field,
  render_default=False,
  data_filters=None,
  hidden=False,
  notitle=False,
  tag='input',
  name=None,
  klass=None,
  attrs=None,
  value=None,
  help=False,
  help_attrs=None,
  dd_attrs=None,
  dt_attrs=None,
  title_klass=None,
  button_text=False,
  nolabel=False,
  file_chooser=False,
  )">
<%
  if value is None:
    value = extract_field_data(field)

  def make_attr_str(attributes):
    if attributes is None:
      attributes = {}
    ret_str = ""
    for key, value in attributes.iteritems():
      if key == "klass":
        key = "class"
      ret_str += "%s='%s'" % (key.replace("_", "-"), unicode(value))
    return ret_str

  if not attrs:
    attrs = {}
  if not render_default:
    attrs.setdefault('type', 'text')

  if data_filters:
    attrs.data_filters = data_filters

  classes = []
  if klass:
    classes.append(klass)
  if hidden:
    classes.append("hide")
  cls = ' '.join(classes)

  title_classes = []
  if title_klass:
    title_classes.append(title_klass)
  if notitle or hidden:
    title_classes.append("hide")
  titlecls = ' '.join(title_classes)
%>

    % if not hidden:
		%if nolabel == False:
			${field.label_tag() | n}
		%endif
    % endif
      % if render_default:
        ${unicode(field) | n}
      % else:
        % if tag == 'textarea':
          <textarea name="${name or field.html_name | n}" ${make_attr_str(attrs) | n} class="${cls}">${extract_field_data(field) or ''}</textarea>
        % elif tag == 'button':
          <button name="${name or field.html_name | n}" ${make_attr_str(attrs) | n} value="${value}" class="${cls}">${button_text or field.name or ''}</button>
        % elif tag == 'checkbox':
          <input type="checkbox" name="${name or field.html_name | n}" ${make_attr_str(attrs) | n} ${value and "CHECKED" or ""} class="${cls}"/>${button_text or field.name or ''}
        % elif hidden:
          <input type="hidden" name="${name or field.html_name | n}" ${make_attr_str(attrs) | n} value="${extract_field_data(field)}" class="${cls}"/>
        % else:
          %if file_chooser:
            <${tag} type="text" name="${name or field.html_name | n}" value="${extract_field_data(field) or ''}" class="${cls}" ${make_attr_str(attrs) | n}/><a class="btn fileChooserBtn" href="#" data-filechooser-destination="${field.html_name | n}">..</a>
          %else:
            <${tag} type="text" name="${name or field.html_name | n}" value="${extract_field_data(field) or ''}" class="${cls}" ${make_attr_str(attrs) | n}/>
          %endif
        % endif
      % endif
      % if help:
        <p data-filters="HelpTip" ${make_attr_str(help_attrs) | n}>${help}</p>
      % endif

    % if len(field.errors):
      <div class="beeswax_error">
         ${unicode(field.errors) | n}
      </div>
    % endif
</%def>

## Puts together a selection list with an "other" field as well.
<%def name="selection(name, choices, current_value, other_key=None)">
    <% seen = False %>
    % if len(choices) == 0:
      <select name="${name}" class="hide">
    % else:
      <select name="${name}">
    % endif
    % for choice in choices:
      % if choice == current_value:
        <% seen = True %>
        <option selected>${choice}</option>
      % else:
        <option>${choice}</option>
      % endif
    % endfor
    % if is_fs_superuser:
      % if seen or not current_value:
        <option value="__other__">Other</option>
      % else:
        <option value="__other__" selected="true">Other</option>
      % endif
    % endif

    </select>
    % if is_fs_superuser:
      % if seen or not current_value:
        <input name="${other_key}" class="hide">
      % else:
        <input name="${other_key}" value="${current_value}" style="margin-bottom: 10px">
      % endif
    % endif
</%def>

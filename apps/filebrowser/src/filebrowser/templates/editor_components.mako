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
  klass=None, 
  attrs=None, 
  value=None, 
  help=False, 
  help_attrs=None, 
  dd_attrs=None, 
  dt_attrs=None, 
  title_klass=None,
  button_text=False
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
    classes.append("jframe-hidden")
  cls = ' '.join(classes)

  title_classes = []
  if title_klass:
    title_classes.append(title_klass)
  if notitle or hidden:
    title_classes.append("jframe-hidden")
  titlecls = ' '.join(title_classes)
%>

    % if not hidden:
    <div class="clearfix">

        ${field.label_tag() | n}

    <div class="input">
    % endif
      % if render_default:
        ${unicode(field) | n}
      % else:
        % if tag == 'textarea':
          <textarea name="${field.html_name | n}" ${make_attr_str(attrs) | n} />${extract_field_data(field) or ''}</textarea>
        % elif tag == 'button':
          <button name="${field.html_name | n}" ${make_attr_str(attrs) | n} value="${value}"/>${button_text or field.name or ''}</button>
        % elif tag == 'checkbox':
          <input type="checkbox" name="${field.html_name | n}" ${make_attr_str(attrs) | n} ${value and "CHECKED" or ""}/>${button_text or field.name or ''}</input>
        % elif hidden:
          <input type="hidden" name="${field.html_name | n}" ${make_attr_str(attrs) | n} value="${extract_field_data(field)}"></input>
        % else:
          <${tag} name="${field.html_name | n}" value="${extract_field_data(field) or ''}" ${make_attr_str(attrs) | n}/>
        % endif
      % endif
      % if help:
        <p class="jframe-inline" data-filters="HelpTip" ${make_attr_str(help_attrs) | n}>${help}</p>
      % endif

    % if not hidden:
    </div>
    </div>
    % endif
    % if len(field.errors):
      <div class="beeswax_error jframe-error">
         ${unicode(field.errors) | n}
      </div>
    % endif
</%def>


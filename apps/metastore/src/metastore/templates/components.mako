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
  from django.utils.translation import ugettext as _
%>

<%def name="menubar()">
  <div class="navbar navbar-inverse navbar-fixed-top nokids">
      <div class="navbar-inner">
        <div class="container-fluid">
          <div class="nav-collapse">
            <ul class="nav">
              <li class="currentApp">
                <a href="/${app_name}">
                  <img src="${ static('metastore/art/icon_metastore_48.png') }" class="app-icon" />
                  ${ _('Metastore Manager') }
                </a>
              </li>
            </ul>
          </div>
        </div>
      </div>
  </div>
</%def>


<%def name="breadcrumbs(breadcrumbs)">
  <ul class="nav nav-pills hueBreadcrumbBar" id="breadcrumbs">
    <li>
      <a href="${url('metastore:databases')}">${_('Databases')}</a><span class="divider">&gt;</span>
    </li>
    % for crumb in breadcrumbs:
    <li>
      % if not loop.last:
        <a href="${ crumb['url'] }">${ crumb['name'] }</a>
        <span class="divider">&gt;</span>
      % else:
        <span style="padding-left:12px">${ crumb['name'] }</span>
      % endif
    </li>
    % endfor
  </ul>
</%def>

<%def name="bootstrapLabel(field)">
    <label for="${field.html_name | n}" class="control-label">${field.label}</label>
</%def>

<%def name="field(
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
  button_text=False,
  placeholder=None,
  file_chooser=False,
  show_errors=True
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
      ret_str += "%s='%s' " % (key.replace("_", "-"), unicode(value))
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

  plc = ""
  if placeholder:
    plc = "placeholder=\"%s\"" % placeholder
%>
    % if field.is_hidden:
        ${unicode(field) | n}
    % else:
        % if render_default:
            ${unicode(field) | n}
        % else:
            % if tag == 'textarea':
                <textarea name="${field.html_name | n}" ${make_attr_str(attrs) | n} class="${cls}" />${extract_field_data(field) or ''}</textarea>
            % elif tag == 'button':
                <button name="${field.html_name | n}" ${make_attr_str(attrs) | n} value="${value}"/>${button_text or field.name or ''}</button>
            % elif tag == 'checkbox':
                % if help:
                    <input type="checkbox" name="${field.html_name | n}" ${make_attr_str(attrs) | n} ${value and "CHECKED" or ""}/ /> <span rel="tooltip" data-original-title="${help}" >${button_text or field.name or ''}</span>
                % else:
                    <input type="checkbox" name="${field.html_name | n}" ${make_attr_str(attrs) | n} ${value and "CHECKED" or ""}/> <span>${button_text or field.name or ''}</span>
                % endif
            % else:
                %if file_chooser:
                    <${tag} name="${field.html_name | n}" value="${extract_field_data(field) or ''}" ${make_attr_str(attrs) | n} class="${cls}" ${plc | n,unicode} /><a class="btn fileChooserBtn" href="#" data-filechooser-destination="${field.html_name | n}">..</a>
                %else:
                    <${tag} name="${field.html_name | n}" value="${extract_field_data(field) or ''}" ${make_attr_str(attrs) | n} class="${cls}" ${plc | n,unicode} />
                %endif
            % endif
        % endif
        % if show_errors and len(field.errors):
            ${unicode(field.errors) | n}
        % endif
    % endif
</%def>

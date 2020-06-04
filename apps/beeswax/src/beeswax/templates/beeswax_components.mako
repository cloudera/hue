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

<%def name="getEllipsifiedCell(val, placement='bottom', klass='')">
  % if len(val) > 25:
    <td class="${ klass }" rel="tooltip" title="${ val[:300] }" data-placement="${ placement }" >${ (val[:25]) }&hellip;</td>
  % else:
    <td class="${ klass }">${ val }</td>
  % endif
</%def>

<%def name="fieldName(field)">
</%def>

<%def name="bootstrapLabel(field)">
    <label for="${field.html_name | n}" class="control-label">${field.label}</label>
</%def>

<%def name="label(
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
    classes.append("hide")
  cls = ' '.join(classes)

  title_classes = []
  if title_klass:
    title_classes.append(title_klass)
  if notitle or hidden:
    title_classes.append("hide")
  titlecls = ' '.join(title_classes)
%>
${field.label_tag() | n}
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


<%def name="pageref(num)">
  % if hasattr(filter_params, "urlencode"):
    href="?q-page=${num}&${filter_params.urlencode()}"
  % else:
    href="?q-page=${num}&${filter_params}"
  % endif
</%def>

<%def name="prevpage(page)">
  ${pageref(page.previous_page_number())}
</%def>

<%def name="nextpage(page)">
  ${pageref(page.next_page_number())}
</%def>

<%def name="toppage(page)">
  ${pageref(1)}
</%def>

<%def name="bottompage(page)">
  ${pageref(paginator.num_pages)}
</%def>

<%def name="pagination(page)">
    <div class="pagination">
        <ul class="pull-right">
            <li class="prev"><a title="${_('Beginning of List')}" ${toppage(page)}>&larr; ${_('Beginning of List')}</a></li>
            % if page and page.has_previous():
            <li><a title="${_('Previous Page')}" ${prevpage(page)}>${_('Previous Page')}</a></li>
            % endif
            % if page and page.has_next():
            <li><a title="${_('Next page')}" ${nextpage(page)}>${_('Next Page')}</a></li>
            % endif
            <li class="next"><a title="${_('End of List')}" ${bottompage(page)}>${_('End of List')} &rarr;</a></li>
        </ul>
        % if page:
          <p>${_('Showing %(start)s to %(end)s of %(count)s items, page %(page)s of %(pages)s') % dict(start=page.start_index(),end=page.end_index(),count=paginator.count,page=page.number,pages=paginator.num_pages)}</p>
        % else:
          <p>${_('Showing %(start)s to %(end)s of %(count)s items, page %(page)s of %(pages)s') % dict(start=0,end=0,count=paginator.count,page=0,pages=paginator.num_pages)}</p>
        % endif
    </div>
</%def>

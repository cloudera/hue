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
  % if field.is_hidden:
    ${unicode(field) | n}
  % else:
    <dt class="${titlecls}" ${make_attr_str(dt_attrs) | n}>${field.label_tag() | n}</dt>
    <dd class="${cls}" ${make_attr_str(dd_attrs) | n}>
      % if render_default:
        ${unicode(field) | n}
      % else:
        % if tag == 'textarea':
          <textarea name="${field.html_name | n}" ${make_attr_str(attrs) | n} />${extract_field_data(field) or ''}</textarea>
        % elif tag == 'button':
          <button name="${field.html_name | n}" ${make_attr_str(attrs) | n} value="${value}"/>${button_text or field.name or ''}</button>
        % elif tag == 'checkbox':
          <input type="checkbox" name="${field.html_name | n}" ${make_attr_str(attrs) | n} ${value and "CHECKED" or ""}/>${button_text or field.name or ''}</input>
        % else:
          <${tag} name="${field.html_name | n}" value="${extract_field_data(field) or ''}" ${make_attr_str(attrs) | n} />
        % endif
      % endif
      % if help:
        <p class="jframe-inline" data-filters="HelpTip" ${make_attr_str(help_attrs) | n}>${help}</p>
      % endif
    </dd>
    % if len(field.errors):
      <dd class="beeswax_error jframe-error">
         ${unicode(field.errors) | n}
       </dd>
    % endif
  % endif
</%def>


<%def name="pageref(num)">
  % if hasattr(filter_params, "urlencode"):
    href="?page=${num}&${filter_params.urlencode()}"
  % else:
    href="?page=${num}&${filter_params}"
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
  ${pageref(page.num_pages())}
</%def>
<%def name="pagination(page)">
  <div class="toolbar bw-designs_toolbar bw-navigation">
    <p class="bw-showing_msg">Showing ${page.start_index()} to ${page.end_index()} of ${page.total_count()} items</p>
    <div class="bw-nav_links">
      <a title="Beginning of List" ${toppage(page)} class="bw-firstBlock">Beginning of List</a>
      <a title="Previous Page" ${prevpage(page)} class="bw-prevBlock">Previous Page</a>
      <p>page ${page.number} of ${page.num_pages()}</p>
      <a title="Next page" ${nextpage(page)} class="bw-nextBlock">Next Page</a>
      <a title="End of List" ${bottompage(page)} class="bw-lastBlock">End of List</a>
    </div>
  </div>
</%def>

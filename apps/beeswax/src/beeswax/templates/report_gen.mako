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
%>
<%namespace name="layout" file="layout.mako" />
<%namespace name="util" file="util.mako" />
${commonheader("Beeswax: Query Constructor", "beeswax", "100px")}
${layout.menubar(section='report generator')}
<div class="container-fluid">
<h1>Report Generator</h1>
% if design and not design.is_auto and design.name:
<b>Working on saved query: ${design.name}</b>
% endif

% if error_message:
Error: <b>${error_message}</b>
% endif
% if log:
## The log should probably be in another tab
<p><a href="#log">View logs</a><p/>
% endif

<form action="${action}" method="POST">

    ## columns management form
    Add column:
    ${unicode(mform.columns.management_form) | n}

    ## colums formset errors
    % for err in mform.columns.non_form_errors():
      ${util.render_error(err)}
    % endfor

    ## columns
    <table>
    <tr>
    % for form in mform.columns.forms:
      <td valign="top" style="border-width:1px; border-style:solid; border-color:black">
	${util.render_form(form)}
      </td>
    % endfor
    </tr>
    </table>

    <br/>

    ## conditions
    <h2>Conditions</h2>
    <%def name="render_conds_formset(formset)">
      % for form in formset.forms:
	<table>
	## formset level errors
	% for err in form.non_field_errors():
	  <tr><td colspan="5">
	  ${util.render_error(err)}
	  </td></tr>
	% endfor
	<tr>
	% for field in form:
	  <td>
	  ${util.render_field(field)}
	  </td>
	% endfor
      </tr></table>
      % endfor
      ${unicode(formset.management_form) | n }
    </%def>

    <%def name="render_union_mform(umform, level)">
      <div style="margin-left:${level * 30}px;">
	${unicode(umform.mgmt) | n}
	${util.render_form(umform.bool)}
	<div style="border-width:1px; border-style:solid; border-color:black">
	${render_conds_formset(umform.conds)}
	</div>
	% for i in range(0, umform.mgmt.form_counts()):
	  <%
	    childname = 'sub%s' % (i,)
	    childform = getattr(umform, childname)
	  %>
	  % if childform:
	    ${render_union_mform(childform, level + 1)}
	  % endif
	% endfor
      </div>
    </%def>

    ${render_union_mform(mform.union, 0)}

    <hr/>
    <input type="submit" name="button-submit" value="Submit"/>
    <input type="submit" name="button-advanced" value="Advanced ..."/>
    <br/>

    ## design info
    ${util.render_form(mform.saveform)}
</form>

% if log:
<br/>
<a name="log"><h3>Server Log</h3></a>
<pre>
${log}
</pre>
% endif
</div>
${commonfooter()}

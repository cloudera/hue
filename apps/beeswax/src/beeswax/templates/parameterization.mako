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
from django.utils.translation import ugettext as _
%>
<%namespace name="comps" file="beeswax_components.mako" />
<%namespace name="layout" file="layout.mako" />

${commonheader(_('Parameterize Query'), "beeswax", user, "100px")}

${layout.menubar()}

<div class="container-fluid">
    <%
        if explain:
            action = url('beeswax.views.explain_parameterized_query', design.id)
            btn = _("Explain query")
        else:
            action = url('beeswax.views.execute_parameterized_query', design.id)
            btn = _("Execute query")
    %>
    <form method="POST" action="${action}" class="form-horizontal">
        <fieldset>
            <legend>${_('Please specify parameters for this query:')}</legend>
            % for field in form:
                <div class="control-group">
                    <label class="control-label">${comps.bootstrapLabel(field)}</label>
                    <div class="controls">
                    ${comps.field(field)}
                    </div>
                </div>
            % endfor
            <div class="hide">
              ${query_servers}
            </div>
            <div class="form-actions">
                <button type="submit" class="btn btn-primary">${btn}</button>
                <a class="btn" href="javascript:history.go(-1);">${_('Cancel')}</a>
            </div>
        </fieldset>
    </form>
</div>

${commonfooter(messages)}

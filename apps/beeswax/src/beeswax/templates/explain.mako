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
<%namespace name="util" file="util.mako" />

${ commonheader(_('Query Explanation'), app_name, user, '100px') | n,unicode }
${layout.menubar(section='saved queries')}

<div class="container-fluid">
    <h1>${_('Query Explanation:')} ${util.render_query_context(query_context)}</h1>

    <ul class="nav nav-tabs">
        <li class="active"><a href="#explanation" data-toggle="tab">${_('Explanation')}</a></li>
        <li><a href="#query" data-toggle="tab">${_('Query')}</a></li>
    </ul>

    <div class="tab-content">
        <div class="tab-pane active" id="explanation">
            <pre>${explanation | h}</pre>
        </div>
        <div class="tab-pane" id="query">
            <pre>${query.hql_query | h}</pre>
        </div>
    </div>

  <br/>
  <a class="btn" onclick="history.back()">${ _('Back') }</a>

</div>

${ commonfooter(messages) | n,unicode }

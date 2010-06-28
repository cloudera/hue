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
##
##
## no spaces in this method please; we're declaring a CSS class, and ART uses this value for stuff, and it splits on spaces, and 
## multiple spaces and line breaks cause issues
<%!
def is_selected(section, matcher):
  if section == matcher:
    return "selected"
  else:
    return ""
%>

<%def name="head(title='Beeswax for Hive', toolbar=True, section=False)">
<html>
  <head>
    <title>${title}</title>
  </head>
  <body class="ccs-shared">
  <div class="toolbar">
    <a href="${ url('beeswax.views.index') }"><img src="/beeswax/static/art/beeswax-logo.png" width="55" height="55" alt="Beeswax" class="beeswax_logo"></a>
    % if toolbar:
    <ul class="bw-nav ccs-button_bar">
      <li><a href="${ url('beeswax.views.execute_query') }" 
        class="ccs-art_button bw-nav_icon bw-query_nav ${is_selected(section, 'query')}" 
        data-icon-styles="{'width': 16, 'height': 16, 'top': 4, 'left': 5}">Query Editor</a></li>
      <li><a href="${ url('beeswax.views.my_queries') }"
        class="ccs-art_button bw-nav_icon bw-my_queries_nav ${is_selected(section, 'my queries')}"
        data-icon-styles="{'width': 16, 'height': 16, 'top': 4, 'left': 5}">My Queries</a></li>
      <li><a href="${ url('beeswax.views.list_designs') }" 
        class="ccs-art_button bw-nav_icon bw-queries_nav ${is_selected(section, 'saved queries')}" 
        data-icon-styles="{'width': 16, 'height': 16, 'top': 4, 'left': 5}">Saved Queries</a></li>
    ## <li><a href="${ url('beeswax.views.edit_report') }" class="ccs-art_button bw-nav_icon bw-new_report_gen_nav ${is_selected(section, 'report generator')}" data-icon-styles="{'width': 16, 'height': 16, 'top': 4, 'left': 5}">Report Generator</a></li>
      <li><a href="${ url('beeswax.views.list_query_history') }" 
        class="ccs-art_button bw-nav_icon bw-history_nav ${is_selected(section, 'history')}" 
        data-icon-styles="{'width': 16, 'height': 16, 'top': 4, 'left': 5}">History</a></li>
      <li><a href="${ url('beeswax.views.show_tables') }" 
        class="ccs-art_button bw-nav_icon bw-tables_nav ${is_selected(section, 'tables')}" 
        data-icon-styles="{'width': 16, 'height': 16, 'top': 4, 'left': 5}">Tables</a></li>
      <li><a href="${ url('beeswax.views.configuration') }" 
        class="ccs-art_button bw-nav_icon bw-config_nav ${is_selected(section, 'hive configuration')}" 
        data-icon-styles="{'width': 16, 'height': 16, 'top': 4, 'left': 5}">Settings</a>
      </li>
      <li><a class="ccs-art_button ccs-refresh large">Refresh</a></li>
    </ul>
    % endif
  </div>
  <hr class="ccs-hidden"/>
</%def>

<%def name="foot()">
  </body>
</html>
</%def>



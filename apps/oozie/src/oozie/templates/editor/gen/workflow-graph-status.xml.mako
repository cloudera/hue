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

<%namespace name="graph" file="workflow-graph.xml.mako" />
<%namespace name="utils" file="../../utils.inc.mako" />

<%!
  from django.utils.translation import ugettext as _
%>

<%def name="print_status_node(form)">
  <%
    is_fork = form.instance.get_full_node().node_type == 'fork'
    action = actions.get(form.instance.__unicode__())
  %>

  % if form.instance.get_full_node().is_visible():
    <div class="row-fluid">
      <div class="span12 action
        % if not is_fork and action:
            action-link
            ${ utils.get_status(action.status) }
          " data-edit="${ url('oozie:list_oozie_workflow_action', action=action.id) }
        % endif
        ">
        <div class="span10">
          <div>
            % if not is_fork:
              ${ form.instance.__unicode__() }
            % endif
          </div>
          <div class="row-fluid">
            ${ form.instance.node_type }<br/>
            % if not is_fork:
              ${ form.instance.description }<br/>
              % if action:
                ${ action.errorMessage or '' }
              % endif
            % endif
          </div>
        </div>
        <div class="span2">
          % if action and action.externalId:
           <a href="${ url('jobbrowser.views.job_single_logs', jobid=action.externalId) }" data-row-selector-exclude="true" id="advanced-btn">
              <i class="icon-tasks"></i> ${ _('View the logs') }
            </a>
          % endif
        </div>
      </div>
    </div>
  % endif

</%def>

${ graph.display_graph(nodes, print_status_node) }

<style>
  .node-text-failed {color:white; font-weight:bold;};
  .node-text-pass {color:black; font-weight:bold;};
</style>

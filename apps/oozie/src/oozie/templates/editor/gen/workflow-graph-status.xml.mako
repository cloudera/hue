## -*- coding: utf-8 -*-
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
    is_join = form.instance.get_full_node().node_type == 'join'
    is_decision = form.instance.get_full_node().node_type == 'decision'
    is_decision_end = form.instance.get_full_node().node_type == 'decisionend'
    action = actions.get(unicode(form.instance))
    control = controls.get(unicode(form.instance))
    box_class = ""
    if is_fork:
      box_class = "node-fork"
    if is_join:
      box_class = "node-join"
    if is_decision:
      box_class = "node-decision"
    if is_decision_end:
      box_class = "node-decision-end"
    if action:
      box_class = "node-action"
  %>

  % if form.instance.get_full_node().is_visible():

      <div class="span12 action ${ box_class }">
        <div class="row-fluid">
          <div class="span12">
            <h4>${ form.instance.__unicode__() }</h4>
            <span class="muted">${ form.instance.node_type }</span>
            <div class="node-description">${ form.instance.description }</div>
            % if action:
              ${ action.errorMessage or '' }
            % elif control:
              ${ control.errorMessage or '' }
            % endif
          </div>
        </div>
        % if action and action.externalId:
        <div class="row-fluid node-action-bar">
          <div class="span2" style="text-align:left;padding-left: 6px">
            % if action:
              <span class="label ${ utils.get_status(action.status) }">${ action.status }</span>
            % endif
          </div>
          <div class="span10" style="text-align:right">
            % if action:
              <a href="${ action.get_absolute_url() }" class="btn btn-mini" title="${ _('View workflow action') }" rel="tooltip"><i class="icon-eye-open"></i></a>
            % endif
            <a href="${ url('jobbrowser.views.job_single_logs', job=action.externalId) }" class="btn btn-mini" title="${ _('View the logs') }" rel="tooltip" data-row-selector-exclude="true" id="advanced-btn"><i class="icon-tasks"></i></a>
            &nbsp;
          </div>
        </div>
        % elif control:
        <div class="row-fluid node-action-bar">
          <div class="span2" style="text-align:left;padding-left: 6px">
            % if control:
              <span class="label ${ utils.get_status(control.status) }">${ control.status }</span>
            % endif
          </div>
          <div class="span10" style="text-align:right">
            &nbsp;
          </div>
        </div>
        % endif

      </div>

  % endif

</%def>

${ graph.display_graph(nodes, print_status_node) }

<style>
  .node-text-failed {color:white; font-weight:bold;};
  .node-text-pass {color:black; font-weight:bold;};
</style>

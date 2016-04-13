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

<%def name="get_tab(form, action, control, css_box_class)">
  <ul style="margin-bottom:0" class="nav nav-tabs">
    <li class="active"><a style="line-height:10px
    % if not action:
          ;background-color: #F9F9F9;
    % endif
    " data-toggle="tab"><i class="fa ${css_box_class}" style="color:#DDD"></i> &nbsp; <strong style="color:#999">
      % if action and action.externalId:
        ${ form.instance.node_type }
      % else:
        ${ form.instance.__unicode__() }
      % endif
    </strong> &nbsp;&nbsp;
      % if action and action.externalId:
        <span class="label ${ utils.get_status(action.status) }">${ action.status }</span>
      % elif control:
        <span class="label ${ utils.get_status(control.status) }">${ control.status }</span>
      % endif
    </a>
    </li>
  </ul>
</%def>

<%def name="get_content(form, action, control, inverse=False)">
  <div class="row-fluid">
    % if action and action.externalId:
      <div style="text-align:left; padding:10px;border:1px solid #DDD; border-top:0" class="span12">
          <div style="font-size: 30px; margin-top:14px" class="pull-right"><a href="${ url('jobbrowser.views.job_single_logs', job=action.externalId) }" title="${ _('View the logs') }" rel="tooltip" data-row-selector-exclude="true"><i class="fa fa-tasks"></i></a></div>
          <h4><a href="${ action.get_absolute_url() }" title="${ _('View workflow action') }" rel="tooltip">${ form.instance.__unicode__() }</a></h4>
          <span class="muted">${ form.instance.description }&nbsp;</span>
          % if action:
            ${ action.errorMessage or '' }
          % elif control:
            ${ control.errorMessage or '' }
          % endif
      </div>
    % else:
      <div style="border:0;" class="span12
      %if inverse:
      inverse_gradient
      %else:
      gradient
      %endif
      ">
      </div>
    % endif
  </div>
</%def>


<%def name="print_status_node(form)">
  <%
    is_start = form.instance.get_full_node().node_type == 'start'
    is_end = form.instance.get_full_node().node_type == 'end'
    is_fork = form.instance.get_full_node().node_type == 'fork'
    is_join = form.instance.get_full_node().node_type == 'join'
    is_decision = form.instance.get_full_node().node_type == 'decision'
    is_decision_end = form.instance.get_full_node().node_type == 'decisionend'
    action = actions.get(unicode(form.instance))
    control = controls.get(unicode(form.instance))
    css_box_class = ""
    if is_start:
      css_box_class = "fa-thumbs-up"
    if is_end:
      css_box_class = "fa-dot-circle-o"
    if is_fork:
      css_box_class = "fa-sitemap"
    if is_join:
      css_box_class = "fa-sitemap fa-rotate-180"
    if is_decision:
      css_box_class = "fa-magic"
    if is_decision_end:
      css_box_class = "fa-magic"
    if action:
      css_box_class = "fa-cogs"
  %>

  % if form.instance.get_full_node().is_visible():
      <div class="span12 action" style="margin-top:0">
        % if is_end or is_join:
          ${get_content(form, action, control, True)}
          <div class="tabbable tabs-below">
          ${get_tab(form, action, control, css_box_class)}
          </div>
        % else:
          ${get_tab(form, action, control, css_box_class)}
          ${get_content(form, action, control)}
        % endif
      </div>
  % endif

</%def>

${ graph.display_graph(nodes, print_status_node) }

<style type="text/css">
  .node-text-failed {color:white; font-weight:bold;};
  .node-text-pass {color:black; font-weight:bold;};
</style>

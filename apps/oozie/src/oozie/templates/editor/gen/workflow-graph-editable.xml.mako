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
  from django.utils.translation import ugettext as _
%>

<%namespace name="graph" file="workflow-graph.xml.mako" />
<%namespace name="utils" file="../../utils.inc.mako" />


<%def name="print_editable_node(form)">
  <%
    node = form.instance.get_full_node()
  %>
  <div class="row-fluid">
    % if not node.is_visible():
       <div class="hide">
           ${ form }
       </div>
    % else:
      <div class="span12 action">
        % for hidden in form.hidden_fields():
          ${ hidden }
        % endfor
        <div class="row-fluid">
            % if node.is_editable():
            <div class="span10 action-link" data-edit="${ node.get_edit_link() }" title="${ _('Edit') }">
          % else:
            <div class="span10">
          % endif
              <span class="label label-info"><b>${ node }</b></span>
          </div>
            <div class="span2"></div>
        </div>
        <div class="row-fluid">
          % if node.is_editable():
            <div class="span10 action-link" data-edit="${ node.get_edit_link() }" title="${ _('Edit') }">
          % else:
            <div class="span10">
          % endif

          <span class="">${ node.node_type }</span>

          <br/>
          ${ node.description }
        </div>
        <div class="span2">
          % if node.can_move():
          <button class="btn" name="move_up_action" value="${ node.id }" title="${ _('Move Up') }" ${ utils.if_false(node.can_move_up(), 'disabled') }>
            <i class="icon-arrow-up"></i>
          </button>
          <button class="btn" name="move_down_action" value="${ node.id }" title="${ _('Move Down') }" ${ utils.if_false(node.can_move_down(), 'disabled') }>
            <i class="icon-arrow-down"></i>
          </button>
          % endif
        </div>
        </div>
        <div class="row-fluid">
          % if node.can_move():
          <div class="span10">
            <button class="btn" name="clone_action" value="${ node.id }" title="${ _('Clone') }"><i class="icon-retweet"></i></button>
            <button class="btn" name="delete_action" value="${ node.id }" title="${ _('Delete') }"><i class="icon-remove"></i></button>
          </div>
          <div class="span2">
          </div>
          % endif
        </div>
      </div>
    % endif
  </div>
</%def>

${ graph.display_graph(nodes, print_editable_node) }


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

<%def name="print_graph(nodes, print_node)">
  % for node in nodes:
    % if type(node) != list:
      <div class="row-fluid">
        ${ print_node(index[node.id]) }
      </div>
    % else:
      % if type(node[0]) != list:
      <div class="row-fluid">
        ${ print_graph(node, print_node) }
      </div>
      % else:
         <div class="row-fluid">
         <%
           children = [n for n in node if n]
           columns = 12 / len(children)
         %>
          % for n in children:
          <div class="${ 'span%d' % columns } action2">
            ${ print_graph(n, print_node) }
          </div>
        % endfor
        </div>
      % endif
    % endif
  % endfor
</%def>


<%def name="display_graph(form, print_node)">
  <div class="row action2" style="min-height:400px;margin-left:1px">
    ${ print_graph(nodes, print_node) }
  </div>

  <style type="text/css">
    .action2 {text-align: center;}
    .action {border-style:solid; border-width:1px; border-color:LightGrey; padding: 3px; margin:25px;}
    .action-link:hover {cursor: pointer;}
  </style>
</%def>

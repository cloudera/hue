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
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN">
<html>
	<head>
		<title>Process Viewer</title>
	</head>
	<body>
        
<a href="${request_path}?show_all=true">Show everything</a>
<table data-filters="HtmlTable" class="treeView">

<%def name="r(node, depth, path)">
  <tr class="table-folder table-depth-${depth}">
  % if node.children:
    <td class="expand">${node.pid}</td>
  % else:
    <td>${node.pid}</td>
  % endif
  <td>
  % if path in open_paths:
    <a href="${remove(path)}">collapse</a>
  % elif node.children:
    <a href="${add(path)}">expand</a>
  % endif

  <a href="${request_path}?subtree=${node.pid}">subset</a>
  </td>
  <td>${node.user}</td>
  <td>${node.cputime}</td>
  <td>${node.command}</td>
  </tr>
  % if path in open_paths or show_all:
    % for child in node.children:
      ${r(child, depth+1, path+"/"+str(child.pid))}
    % endfor
  % endif
</%def>

<thead>
<th>pid</th>
<th>links</th>
<th>user</th>
<th>cputime</th>
<th>command</th>
</thead>
<tbody>
% for top in tops:
 ${r(top, 0, "/" + str(top.pid))}
% endfor
</tbody>
</table>


        </body>
</html>

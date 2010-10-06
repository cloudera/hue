<%!
  import urllib
%>
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
    <title>HtmlTable Treeview w/ Ajax</title>
    <style>
    .table-depth-0>td:first-child { padding-left: 10px; }
    .table-depth-1>td:first-child { padding-left: 25px; }
    .table-depth-2>td:first-child { padding-left: 40px; }
    .table-depth-3>td:first-child { padding-left: 55px; }
    .table-depth-4>td:first-child { padding-left: 70px; }
    .table-depth-5>td:first-child { padding-left: 85px; }
    .table-depth-6>td:first-child { padding-left: 100px; }
    .table-depth-7>td:first-child { padding-left: 115px; }
    .table-depth-8>td:first-child { padding-left: 130px; }
    .table-depth-9>td:first-child { padding-left: 145px; }
    .table-depth-10>td:first-child { padding-left: 160px; }
    .table-depth-11>td:first-child { padding-left: 175px; }
    </style>
    <meta http-equiv="refresh" content="5" />
  </head>
  <body>
    <div class="jframe_padded partial_refresh"> 
      <input value="you can put some text in here to verify that the whole view doesn't refresh" style="width: 500px;"/>
      <p><a href="${request_path}?show_all=true">Show everything</a> || <a href="${request_path}">back to top</a></p>
      <table data-filters="HtmlTable" class="selectable treeView" style="border: 1px solid #999; width: 98%">

      <%def name="create_row(node, depth, path)">
        <%
          expanded = ""
          if path in open_paths:
            expanded = "table-expanded"
          folder = ""
          if node.children:
            folder = "table-folder"
        %>
        <tr class="${folder} table-depth-${depth} ${expanded} pstree-${node.pid}"
          data-dblclick-delegate="{'dblclick_loads':'.sub'}"
          data-partial-line-id="pstree-line-${node.pid}">
          <td style="max-width:400px">
            % if path in open_paths:
              <a href="${remove(path)}" class="ccs-hidden">collapse</a>
            % elif node.children:
              <a href="${add(path)}" class="ccs-hidden">expand</a>
            % endif

            % if node.children:
              <a href="${request_path}?subtree=${node.pid}&depth=${int(depth)+1}" class="expand"
                data-spinner-target=".pstree-${node.pid}"
                data-livepath-toggle="${urllib.urlencode([('paths', node.path)])}"
                data-ajax-after=".pstree-${node.pid}" data-ajax-filter="tbody tr">subset</a>
              <a href="${request_path}?subtree=${node.pid}" class="sub ccs-hidden">browse</a>
            % endif

            <div style="overflow:hidden; white-space:nowrap;" data-filters="FitText">${node.command}</div></td>
          <td>${node.pid}</td>
          <td>${node.user}</td>
          <td data-partial-id="pstree-cputime-${node.pid}">${node.cputime}</td>
        </tr>
        % if path in open_paths or show_all:
          % for child in node.children:
            ${create_row(child, depth+1, path+"/"+str(child.pid))}
          % endfor
        % endif
      </%def>

      <thead>
        <tr>
          <th>command</th>
          <th>pid</th>
          <th>user</th>
          <th>cputime</th>
        </tr>
      </thead>
      <tbody data-partial-container-id="pstree-body">
        % for top in tops:
         ${create_row(top, depth, "/" + str(top.pid))}
        % endfor
      </tbody>
      </table>
    </div>
  </body>
</html>

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
from django.template.defaultfilters import urlencode, escape
%>

<%def name="header(clusters)">
    <div data-filters="SplitView">
    <div class="left_col jframe_padded" style="width:150px;">
        <h2>Clusters</h2>
        <ul>
            % for id, c in enumerate(clusters):
                <li>
                  <a href="${ url('zookeeper:view', id=id) }">
                    ${ c }
                  </a>
                </li>
            % endfor
        </ul>
    </div>
</%def>


<%def name="info_button(url, text)">
  <a data-filters="ArtButton" href="${url}" style="background: url(/static/art/info.png) left 50%; padding: 6px 6px 6px 20px; margin: 10px;"
    data-icon-styles="{'width': 14, 'height': 14}">
      ${text}
  </a>
</%def>

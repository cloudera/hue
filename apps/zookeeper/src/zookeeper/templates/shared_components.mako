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
  from django.utils.translation import ugettext as _
%>

<%def name="header(breadcrumbs, clusters, withBody=True)">
  <div class="container-fluid">
  <div class="row-fluid">
    <div class="card card-small">
      <h1 class="card-heading simple">
        <div class="btn-group pull-right">
          <a class="btn dropdown-toggle" data-toggle="dropdown" href="#">
            ${ _('Go to cluster') }
            <span class="caret"></span>
          </a>
          <ul class="dropdown-menu">
            % for c in clusters:
              <li>
                <a href="${ url('zookeeper:view', id=c) }">
                  ${ c }
                </a>
              </li>
            % endfor
          </ul>
        </div>
      % for idx, crumb in enumerate(breadcrumbs):
        %if crumb[1] != "":
          <a href="${crumb[1]}">${crumb[0]}</a>
        %else:
          ${crumb[0]}
        %endif

        %if idx < len(breadcrumbs) - 1:
          &gt;
        %endif
      % endfor
      </h1>
      %if withBody:
      <div class="card-body">
        <p>
      %endif
</%def>

<%def name="footer(withBody=True)">
      %if withBody:
        </p>
      </div>
      %endif
    </div>
  </div>
</div>
<link rel="stylesheet" href="${ static('zookeeper/css/zookeeper.css') }">
<script src="${ static('zookeeper/js/base64.js') }" type="text/javascript" charset="utf-8"></script>
</%def>

<%def name="menubar()">
  <div class="navbar hue-title-bar nokids">
      <div class="navbar-inner">
        <div class="container-fluid">
          <div class="nav-collapse">
            <ul class="nav">
              <li class="app-header">
                <a href="/${app_name}">
                  <img src="${ static('zookeeper/art/icon_zookeeper_48.png') }" class="app-icon" alt="${ _('Zookeeper icon') }"/>
                  ${ _('ZooKeeper Browser') }
                </a>
               </li>
            </ul>
          </div>
        </div>
      </div>
  </div>
</%def>


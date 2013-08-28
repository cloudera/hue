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
  from desktop.views import commonheader, commonfooter
  from django.utils.translation import ugettext as _
%>

${ commonheader(_('Welcome Home'), "home", user) | n,unicode }

  <div class="navbar navbar-inverse navbar-fixed-top nokids">
      <div class="navbar-inner">
        <div class="container-fluid">
          <div class="nav-collapse">
            <ul class="nav">
              <li class="currentApp">
                <a href="/home">
                  <img src="/static/art/home.png" />
                  ${ _('Home') }
                </a>
               </li>
            </ul>
          </div>
        </div>
      </div>
  </div>

<div style="position: absolute;top:80px;right:30px"><img src="/static/art/hue-logo-subtle.png"/></div>

<div class="container-fluid">
  <div class="row-fluid">
    <div class="span12">
      <h1>${_('Welcome Home.')}</h1>
    </div>
  </div>
  <div class="row-fluid" style="margin-top: 30px">

    <div class="span2">
      <div class="card card-home card-listcontent">
        <h2 class="card-heading simple">${_('New')}</h2>
      </div>

      <div class="card card-home card-listcontent">
        <h2 class="card-heading simple">${_('Tags')}</h2>

        <div class="card-body">
          <p>
          <ul>
            % for tag in tags:            
            <li>
              <span class="label label-info">${ tag.tag }</span>
              % if loop.first: 
                (selected)
              % endif
            </li>
            % endfor
          </ul>
          </p>
        </div>
      </div>
    </div>

    <div class="span10">
      <div class="card card-home card-listcontent">
        <h2 class="card-heading simple">${_('Documents')}</h2>

        <div class="card-body">
          <p>
          <table>
            % for doc in documents:
              <tr>
                <td>${ doc.content_type }</td>
                <td><a href="${ doc.content_object.get_absolute_url() }">${ doc.name }</a></td>
                <td>${ doc.description }</td>
                <td class="span1">
                  % for tag in doc.tags.all():
                    <span class="label label-info">${ tag.tag }</span>
                  % endfor
                </td>
                <td class="span1">${ doc.owner }</td>
                <td class="span1">${ doc.last_modified }</td>
              </tr>
            % endfor
          </table>
          </p>
        </div>
      </div>
    </div>

  </div>
</div>

${ commonfooter(messages) | n,unicode }

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

<%! from django.utils.translation import ugettext as _ %>

<%!
def is_selected(section, matcher):
  if section == matcher:
    return "active"
  else:
    return ""
%>

## Nav bar is also duplicated in beeswax layout.mako.

<%def name="navbar(section='editor')">
  <div class="navbar navbar-inverse navbar-fixed-top">
    <div class="navbar-inner">
      <div class="container-fluid">
        <div class="nav-collapse">
          <ul class="nav">
            <li class="currentApp">
              <a href="/spark">
                <img src="/spark/static/art/icon_spark_48.png" class="app-icon"/>
                ${ _('Spark Igniter') }
              </a>
            </li>
            <li class="${is_selected(section, 'editor')}"><a href="${ url('spark:editor') }">${_('Editor')}</a></li>
            ##<li class="${is_selected(section, 'my queries')}"><a href="${ url(app_name + ':my_queries') }">${_('My Queries')}</a></li>
            <li class="${is_selected(section, 'saved queries')}"><a href="${ url('spark:list_designs') }">${_('Applications')}</a></li>
            ##<li class="${is_selected(section, 'history')}"><a href="${ url('spark:list_query_history') }">${_('History')}</a></li>
            <li class="${is_selected(section, 'jobs')}"><a href="${ url('spark:list_jobs') }">${_('Dashboard')}</a></li>
            <li class="${is_selected(section, 'contexts')}"><a href="${ url('spark:list_contexts') }">${_('Contexts')}</a></li>
            <li class="${is_selected(section, 'applications')}"><a href="${ url('spark:list_applications') }">${_('Uploads')}</a></li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</%def>

<%def name="createContextModal()">
<div id="createContextModal" class="modal hide fade">
  <div class="modal-header">
    <a href="#" class="close" data-dismiss="modal">&times;</a>
    <h3>${_('Create context')}</h3>
  </div>
  <div class="modal-body">
    <form class="form-horizontal" id="createContextForm">
      <div class="control-group">
        <label class="control-label">${ _("Name") }</label>
        <div class="controls">
          <input type="text" name="name" data-default="">
        </div>
      </div>
      <div class="control-group">
        <label class="control-label">${ _("Num cpu cores") }</label>
        <div class="controls">
          <input type="text" name="num-cpu-cores" value="1" data-default="1">
        </div>
      </div>
      <div class="control-group">
        <label class="control-label">${ _("Memory per node") }</label>
        <div class="controls">
          <input type="text" name="mem-per-node" value="512m" data-default="512m">
        </div>
      </div>
    </form>
  </div>
  <div class="modal-footer">
    <button class="btn" data-dismiss="modal">${_('Cancel')}</button>
    <button id="createContextBtn" data-bind="click: createContext" class="btn btn-primary disable-feedback">${_('Create')}</button>
  </div>
</div>
</%def>


<%def name="uploadAppModal()">
<div id="uploadAppModal" class="modal hide fade">
  <form class="form-horizontal" id="uploadAppForm" action="${ url('spark:upload_app') }" method="POST" enctype="multipart/form-data">
  ${ csrf_token(request) | n,unicode }
  <div class="modal-header">
    <a href="#" class="close" data-dismiss="modal">&times;</a>
    <h3>${_('Upload application')}</h3>
  </div>
  <div class="modal-body">
    ${ _('One class of the jar should implement SparkJob.') }
    <div class="control-group">
      <label class="control-label">${ _("Local jar file") }</label>
      <div class="controls">
        <input type="file" name="jar_file" id="jar_file">
      </div>
    </div>
    <div class="control-group">
      <label class="control-label">${ _("App name") }</label>
      <div class="controls">
        <input type="text" name="app_name" id="app_name">
      </div>
    </div>
  </div>
  <div class="modal-footer">
    <button class="btn" data-dismiss="modal">${_('Cancel')}</button>
    <input type="submit" class="btn btn-primary" value="${_('Upload')}"/>
  </div>
  </form>
</div>
</%def>

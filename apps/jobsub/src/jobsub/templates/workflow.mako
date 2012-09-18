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
  import time

  from desktop.views import commonheader, commonfooter
  from hadoop.fs.hadoopfs import Hdfs
  from django.utils.translation import ugettext as _
%>
<%namespace name="layout" file="layout.mako" />

${commonheader(_("Job Designer"), "jobsub", user, "100px")}
${layout.menubar(section='history')}

<%def name="format_time(st_time)">
  % if st_time is None:
    -
  % else:
    ${time.strftime("%a, %d %b %Y %H:%M:%S", st_time)}
  % endif
</%def>

<%def name="hdfs_link(url)">
  <% path = Hdfs.urlsplit(url)[2] %>
  % if path:
    <a href="/filebrowser/view${path}" target="FileBrowser">${url}</a>
  % else:
    ${url}
  % endif
</%def>

<%def name="configModal(elementId, title, configs)">
  <div id="${elementId}" class="modal hide fade">
      <div class="modal-header">
          <a href="#" class="close" data-dismiss="modal">&times;</a>
          <h3>${title}</h3>
      </div>
      <div class="modal-body">
          <table class="table table-condensed table-striped">
            <thead>
              <tr>
                <th>${_('Name')}</th>
                <th>${_('Value')}</th>
              </tr>
            </thead>
            <tbody>
              % for name, value in sorted(configs.items()):
                <tr>
                  <td>${name}</td>
                  <td>
                    ## Try to detect paths
                    %if name.endswith('dir') or name.endswith('path'):
                      ${hdfs_link(value)}
                    %else:
                      ${value}
                    %endif
                  </td>
                </tr>
              % endfor
            </tbody>
          </table>
      </div>
  </div>
</%def>

<div class="container-fluid">
    %if design_link is not None:
    <h1><a title="${_('Edit design')}" href="${design_link}">${workflow.appName}</a> (${workflow.id})</h1>
    %else:
    <h1>${workflow.appName} (${workflow.id})</h1>
    %endif

    ## Tab headers
    <ul class="nav nav-tabs">
        <li class="active"><a href="#actions" data-toggle="tab">${_('Actions')}</a></li>
        <li><a href="#details" data-toggle="tab">${_('Details')}</a></li>
        <li><a href="#definition" data-toggle="tab">${_('Definition')}</a></li>
        <li><a href="#log" data-toggle="tab">${_('Log')}</a></li>
    </ul>

    <div id="workflow-tab-content" class="tab-content">
      ## Tab: Actions
      <div class="tab-pane active" id="actions">
        <table data-filters="HtmlTable" class="table table-striped table-condensed selectable sortable" cellpadding="0" cellspacing="0">
          <thead>
            <tr>
              <th>${_('Name')}</th>
              <th>${_('Type')}</th>
              <th>${_('Status')}</th>
              <th>${_('External Id')}</th>

              <th>${_('Start Time')}</th>
              <th>${_('End Time')}</th>

              <th>${_('Retries')}</th>
              <th>${_('Error Message')}</th>
              <th>${_('Transition')}</th>

              <th>${_('Data')}</th>
            </tr>
          </thead>
          <tbody>
            % for i, action in enumerate(workflow.actions):
              <tr>
                <td>
                  ## Include a modal for action configuration
                  ${action.name}
                  <% modal_id = "actionConfigModal" + str(i) %>
                  <a href="#${modal_id}" data-toggle="modal"><img src="/static/art/led-icons/cog.png"
                      alt="Show Configuration"></a>
                  ${configModal(modal_id, "Action Configuration", action.conf_dict)}
                </td>
                <td>${action.type}</td>
                <td>${action.status}</td>
                <td>${action.externalId}</td>

                <td>${format_time(action.startTime)}</td>
                <td>${format_time(action.endTime)}</td>

                <td>${action.retries}</td>
                <td>${action.errorMessage}</td>
                <td>${action.transition}</td>

                <td>${action.data}</td>
              </tr>
            % endfor
          <tbody>
        </table>
      </div>

        ## Tab: Job details
        <div class="tab-pane" id="details">
          <table data-filters="HtmlTable" class="table table-striped table-condensed selectable sortable" cellpadding="0" cellspacing="0">
            <tbody>
              <tr>
                ## App name + configuration
                <td>${_('Application Name')}</td>
                <td>
                  ${workflow.appName}
                  <a href="#appConfigModal" data-toggle="modal"><img src="/static/art/led-icons/cog.png"
                      alt="Show Configuration"/></a>
                </td>
              </tr>
              <tr>
                <td>${_('User')}</td>
                <td>${workflow.user}</td>
              </tr>
              <tr>
                <td>${_('Group')}</td>
                <td>${workflow.group}</td>
              </tr>
              <tr>
                <td>${_('Status')}</td>
                <td>${workflow.status}</td>
              </tr>
              <tr>
                <td>${_('External Id')}</td>
                <td>${workflow.externalId or "-"}</td>
              </tr>
              <tr>
                <td>${_('Start Time')}</td>
                <td>${format_time(workflow.startTime)}</td>
              </tr>
              <tr>
                <td>${_('Created Time')}</td>
                <td>${format_time(workflow.createdTime)}</td>
              </tr>
              <tr>
                <td>${_('End Time')}</td>
                <td>${format_time(workflow.endTime)}</td>
              </tr>
              <tr>
                <td>${_('Application Path')}</td>
                <td>${hdfs_link(workflow.appPath)}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        ## Tab: Definition
        <div class="tab-pane" id="definition">
            <pre>${definition|h}</pre>
        </div>

        ## Tab: Log
        <div class="tab-pane" id="log">
            <pre>${log|h}</pre>
        </div>
    </ul>
  </div>
</div>

${configModal("appConfigModal", "Application Configuration", workflow.conf_dict)}

${commonfooter(messages)}

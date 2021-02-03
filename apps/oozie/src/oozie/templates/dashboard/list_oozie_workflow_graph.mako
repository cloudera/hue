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
<%!
  from django.utils.translation import ugettext as _
%>


<%namespace name="workflow" file="../editor2/common_workflow.mako" />
<%namespace name="utils" file="../utils.inc.mako" />
<%namespace name="dashboard" file="/common_dashboard.mako" />

<link rel="stylesheet" href="${ static('oozie/css/common-editor.css') }">
<link rel="stylesheet" href="${ static('oozie/css/workflow-editor.css') }">
<link rel="stylesheet" href="${ static('desktop/ext/css/bootstrap-editable.css') }">

${ dashboard.import_layout() }

<script src="${ static('oozie/js/workflow-editor.ko.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('oozie/js/workflow-editor.utils.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/jquery/plugins/jquery.curvedarrow.js') }" type="text/javascript" charset="utf-8"></script>

<div class="oozie_workflowComponents">

  ${ workflow.render() }

  <div id="loaded${doc_uuid}graph">
    ${ workflow_graph | n,unicode }
  </div>

</div>

<script type="text/javascript">

  ${ utils.slaGlobal() }

  var globalFilechooserOptions;

  (function () {

    % if layout_json != '':
      var viewModel = new WorkflowEditorViewModel(${ layout_json | n,unicode }, ${ workflow_json | n,unicode }, ${ credentials_json | n,unicode }, ${ workflow_properties_json | n,unicode }, ${ subworkflows_json | n,unicode }, ${ can_edit_json | n,unicode });
      ko.cleanNode($("#${graph_element_id}")[0]);
      ko.applyBindings(viewModel, $("#${graph_element_id}")[0]);
      viewModel.isViewer = ko.observable(true);
      viewModel.isEmbeddable = ko.observable(true);
      viewModel.init();
      fullLayout(viewModel);

      globalFilechooserOptions = {
        skipInitialPathIfEmpty: true,
        showExtraHome: true,
        uploadFile: true,
        createFolder: true,
        extraHomeProperties: {
          label: '${ _('Workspace') }',
          icon: 'fa-folder-open',
          path: viewModel.workflow.properties.deployment_dir()
        },
        deploymentDir: viewModel.workflow.properties.deployment_dir()
      }

      var refreshViewTimeout = -1;

      function refreshView() {
        if ($('#loaded${doc_uuid}graph').is(':visible')) {
          $.getJSON("${ oozie_workflow.get_absolute_url(format='json') }", function (data) {

            if (data.actions) {
              % if layout_json != '':
                ko.utils.arrayForEach(data.actions, function (action) {
                  var _w, actionId = action.id.substr(action.id.lastIndexOf('@'));
                  if (actionId === '@End') {
                    _w = viewModel.getWidgetById('33430f0f-ebfa-c3ec-f237-3e77efa03d0a');
                  }
                  else {
                    var actionName = actionId.toLowerCase().substr(actionId.lastIndexOf('@') + 1)
                    if ($("[id^=wdg_][id*=" + actionName + "]").length > 0) {
                      _w = viewModel.getWidgetById($("[id^=wdg_][id*=" + actionName + "]").attr("id").substr(4));
                    }
                    else {
                      _w = viewModel.getWidgetById('33430f0f-ebfa-c3ec-f237-3e77efa03d0a');
                    }
                  }
                  if (_w != null) {
                    if (['SUCCEEDED', 'OK', 'DONE'].indexOf(action.status) > -1) {
                      _w.status("success");
                      _w.progress(100);
                    }
                    else if (['RUNNING', 'READY', 'PREP', 'WAITING', 'SUSPENDED', 'PREPSUSPENDED', 'PREPPAUSED', 'PAUSED', 'SUBMITTED', 'SUSPENDEDWITHERROR', 'PAUSEDWITHERROR'].indexOf(action.status) > -1) {
                      _w.status("running");
                      _w.progress(50);
                    }
                    else {
                      _w.status("failed");
                      _w.progress(100);
                    }
                    _w.actionURL(action.url);
                    _w.logsURL(action.log);
                    _w.externalIdUrl(action.externalIdUrl);
                    _w.externalId(action.id);
                    _w.externalJobId(action.externalJobId);
                  }
                });
              %endif
            }
            %if not is_jb2:
            if (data.status != "RUNNING" && data.status != "PREP") {
              return;
            }
            else {
              refreshViewTimeout = window.setTimeout(refreshView, 1000);
            }
            %endif
          });
        }
        else {
          refreshViewTimeout = window.setTimeout(refreshView, 1000);
        }
      }

      huePubSub.subscribe('graph.refresh.view', refreshView);

      huePubSub.subscribe('graph.stop.refresh.view', function(){
        window.clearTimeout(refreshViewTimeout);
        huePubSub.removeAll('graph.draw.arrows');
      });

      huePubSub.subscribe('graph.draw.arrows', function(){
        viewModel.drawArrows();
      });

    %endif
    % if layout_json == '':
      $.ajax({
        'url': "${oozie_workflow.get_absolute_url()}?format=svg",
        'type': 'GET',
        success: function (svgData) {
          $("#workflow_graph").append(svgData);
        }
        });
    % endif

    $(document).ready(function () {
      % if layout_json != '':
        viewModel.drawArrows();
        refreshView();
      %endif
    });
  })();
</script>

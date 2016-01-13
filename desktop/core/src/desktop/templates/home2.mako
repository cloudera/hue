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
  from desktop.views import commonheader, commonfooter, commonshare2, commonimportexport, _ko
  from django.utils.translation import ugettext as _
%>

<%namespace name="assist" file="/assist.mako" />
<%namespace name="fileBrowser" file="/file_browser.mako" />
<%namespace name="tableStats" file="/table_stats.mako" />
<%namespace name="require" file="/require.mako" />

${ commonheader(_('Welcome Home'), "home", user) | n,unicode }

${ require.config() }

${ tableStats.tableStats() }
${ assist.assistPanel() }
${ fileBrowser.fileBrowser() }

<style type="text/css">

  html {
    height: 100%;
  }

  body {
    height:100%;
    margin: 0;
    padding: 0;
    background-color: #FFF;
  }

  .vertical-full {
    height:100%;
  }

  .main-content {
    height: auto;
    width: 100%;
    position: absolute;
    top: 82px;
    bottom: 0;
    background-color: #FFF;
  }

  .panel-container {
    position: relative;
  }

  .left-panel {
    position: absolute;
    height: 100%;
    overflow: auto;
  }

  .resizer {
    position: absolute;
    height: 100%;
    width: 4px;
    cursor: col-resize;
  }

  .resize-bar {
    position: absolute;
    height: 100%;
    width: 2px;
    background-color: #F1F1F1;
  }

  .right-panel {
    position: absolute;
    height: 100%;
    overflow: auto;
  }

  .show-assist {
    position: fixed;
    top: 80px;
    background-color: #FFF;
    width: 16px;
    height: 24px;
    line-height: 24px;
    margin-left: -2px;
    text-align: center;
    -webkit-border-top-right-radius: 3px;
    -webkit-border-bottom-right-radius: 3px;
    -moz-border-radius-topright: 3px;
    -moz-border-radius-bottomright: 3px;
    border-top-right-radius: 3px;
    border-bottom-right-radius: 3px;
    z-index: 1000;
    -webkit-transition: margin-left 0.2s linear;
    -moz-transition: margin-left 0.2s linear;
    -ms-transition: margin-left 0.2s linear;
    transition: margin-left 0.2s linear;
  }

  .show-assist:hover {
    margin-left: 0;
  }

  .hide-assist {
    position: absolute;
    top: 2px;
    right: 4px;
    z-index: 1000;
    color: #D1D1D1;
    font-size: 12px;
    -webkit-transition: margin-right 0.2s linear, color 0.5s ease;
    -moz-transition: margin-right 0.2s linear, color 0.5s ease;
    -ms-transition: margin-right 0.2s linear, color 0.5s ease;
    transition: margin-right 0.2s linear, color 0.5s ease;
  }

  .hide-assist:hover {
    margin-right: 2px;
    color: #338bb8;
  }
</style>

<div class="navbar navbar-inverse navbar-fixed-top nokids">
  <div class="navbar-inner">
    <div class="container-fluid">
      <div class="nav-collapse">
        <ul class="nav">
          <li class="currentApp">
            <a href="${ url('desktop.views.home2') }">
              <img src="${ static('desktop/art/home.png') }" class="app-icon" />
              ${ _('My documents') }
            </a>
           </li>
        </ul>
        </div>
      <div class="nav-collapse pull-right">
        <ul class="nav">
          <li class="currentApp">
            <a href="${ url('desktop.views.home') }">
              <img src="${ static('desktop/art/home.png') }" class="app-icon" />
              ${ _('Old home') }
            </a>
           </li>
        </ul>
      </div>
    </div>
  </div>
</div>

<div id="documentList" class="main-content">
  <a title="${_('Toggle Assist')}" class="pointer show-assist" data-bind="visible: !$root.isLeftPanelVisible(), click: function() { $root.isLeftPanelVisible(true); }" style="display:none;">
    <i class="fa fa-chevron-right"></i>
  </a>

  <div class="vertical-full container-fluid" data-bind="style: { 'padding-left' : $root.isLeftPanelVisible() ? '0' : '20px' }">
    <div class="vertical-full row-fluid panel-container">
      <div class="assist-container left-panel" data-bind="visible: $root.isLeftPanelVisible" style="display: none;">
        <a title="${_('Toggle Assist')}" class="pointer hide-assist" data-bind="click: function() { $root.isLeftPanelVisible(false) }">
          <i class="fa fa-chevron-left"></i>
        </a>
        <div class="assist" data-bind="component: {
        name: 'assist-panel',
        params: {
          sourceTypes: [{
            name: 'hive',
            type: 'hive'
          }],
          user: '${user.username}',
          navigationSettings: {
            openItem: true,
            showPreview: true,
            showStats: false
          },
          visibleAssistPanels: ['sql']
        }
      }"></div>
      </div>
      <div class="resizer" data-bind="visible: $root.isLeftPanelVisible, splitDraggable : { appName: 'notebook', leftPanelVisible: $root.isLeftPanelVisible }" style="display:none;"><div class="resize-bar">&nbsp;</div></div>
      <div class="right-panel" data-bind="style: { 'padding-left' : $root.isLeftPanelVisible() ? '20px' : '0' }">
        <input id="searchInput" type="text" placeholder="${ _('Search for name, description, etc...') }" class="input-xlarge search-query" style="margin-left: 20px;margin-top: 5px">
        <div class="dropdown" style="float: right;">
          <a href="#" data-toggle="dropdown"><i class="fa fa-plus-circle"></i> ${_('New document')}</a>
          <ul class="dropdown-menu" role="menu">
            % if 'beeswax' in apps:
              <li><a href="${ url('beeswax:index') }"><img src="${ static(apps['beeswax'].icon_path) }" class="app-icon"/> ${_('Hive Query')}</a></li>
            % endif
            % if 'impala' in apps:
              <li><a href="${ url('impala:index') }"><img src="${ static(apps['impala'].icon_path) }" class="app-icon"/> ${_('Impala Query')}</a></li>
            % endif
            % if 'pig' in apps:
              <li><a href="${ url('pig:index') }"><img src="${ static(apps['pig'].icon_path) }" class="app-icon"/> ${_('Pig Script')}</a></li>
            % endif
            % if 'spark' in apps:
              <li><a href="${ url('notebook:index') }"><img src="${ static(apps['spark'].icon_path) }" class="app-icon"/> ${_('Spark Job')}</a></li>
            % endif
            % if 'oozie' in apps:
              <li class="dropdown-submenu">
                <a href="#"><img src="${ static(apps['oozie'].icon_path) }" class="app-icon"/> ${_('Oozie Scheduler')}</a>
                <ul class="dropdown-menu">
                  <li><a href="${ url('oozie:new_workflow') }"><img src="${ static('oozie/art/icon_oozie_workflow_48.png') }" class="app-icon"/> ${_('Workflow')}</a></li>
                  <li><a href="${ url('oozie:new_coordinator') }"><img src="${ static('oozie/art/icon_oozie_coordinator_48.png') }" class="app-icon"/> ${_('Coordinator')}</a></li>
                  <li><a href="${ url('oozie:new_bundle') }"><img src="${ static('oozie/art/icon_oozie_bundle_48.png') }" class="app-icon"/> ${_('Bundle')}</a></li>
                </ul>
              </li>
            % endif
          </ul>
        </div>
        <h2 class="card-heading simple">${_('My Documents')}</h2>
        <br/>
        <input data-bind="value: mkdirFormPath" placeholder="dir name, e.g. projects" />
        <a href="javascript:void(0);" class="btn" data-bind="click: mkdir"><i class="fa fa-plus-circle"></i> ${ _('Create Directory') }</a>

        <input data-bind="value: deleteFormPath" placeholder="doc id, e.g. 50491" />
        <a href="javascript:void(0);" class="btn" data-bind="click: deleteDocument"><i class="fa fa-times"></i> ${ _('Delete') }</a>

        <input data-bind="value: shareFormDocId" placeholder="doc id, e.g. 50491" />
        <a class="share-link btn" rel="tooltip" data-placement="bottom" style="margin-left:20px" data-bind="click: function(e){ prepareShareModal(e) },
          attr: {'data-original-title': '${ _ko("Share") } ' + name}">
          <i class="fa fa-users"></i> ${ _('Share') }
        </a>

        <input data-bind="value: exportFormDocIds" placeholder="doc id, e.g. 50491,50492" />
        <a class="share-link btn" data-bind="click: exportDocuments">
          <i class="fa fa-download"></i> ${ _('Export') }
        </a>

        <a data-bind="click: function() { $('#import-documents').modal('show'); }" class="btn">
          <i class="fa fa-upload"></i> ${ _('Import') }
        </a>

        <div class="file-browser" data-bind="component: {
          name: 'file-browser',
          params: {
            currentDirectory: currentDirectory
          }
        }"></div>
      </div>
    </div>
  </div>
</div>

<script type="text/html" id="document-template">
  <tr>
    <td style="width: 26px"></td>
    <td><a data-bind="attr: { href: absoluteUrl }, html: name"></a></td>
    <td data-bind="text: ko.mapping.toJSON($data)"></td>
  </tr>
</script>

## ${ commonshare2() | n,unicode }
${ commonimportexport(request) | n,unicode }

<script type="text/javascript" charset="utf-8">
  require([
    'knockout',
    'desktop/js/home2.vm',
    'desktop/js/share2.vm',
    'assistPanel',
    'tableStats',
    'fileBrowser',
    'knockout-mapping',
    'knockout-sortable',
    'ko.hue-bindings'
  ], function (ko, HomeViewModel, ShareViewModel) {

    ko.options.deferUpdates = true;

    $(document).ready(function () {
      var options = {
        user: '${ user.username }',
        i18n: {
          errorFetchingTableDetails: '${_('An error occurred fetching the table details. Please try again.')}',
          errorFetchingTableFields: '${_('An error occurred fetching the table fields. Please try again.')}',
          errorFetchingTableSample: '${_('An error occurred fetching the table sample. Please try again.')}',
          errorRefreshingTableStats: '${_('An error occurred refreshing the table stats. Please try again.')}',
          errorLoadingDatabases: '${ _('There was a problem loading the databases. Please try again.') }',
          errorLoadingTablePreview: '${ _('There was a problem loading the table preview. Please try again.') }'
        }
      };

      var viewModel = new HomeViewModel(options);
      if (location.getParameter('path')) {
        viewModel.openPath(location.getParameter('path'));
      }
      viewModel.currentDirectory().open(true);
      ko.applyBindings(viewModel, $('#documentList')[0]);

##       ShareViewModel.initSharing("#documentShareModal");
##       shareViewModel.setDocId(-1);
##
##
##       prepareShareModal = function(job) {
##         shareViewModel.setDocId(viewModel.shareFormDocId());
##         openShareModal();
##       };
    });
  });
</script>

${ commonfooter(request, messages) | n,unicode }

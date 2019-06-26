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

  from desktop.views import commonheader, commonfooter, _ko
  from desktop import conf
%>

<%namespace name="assist" file="/assist.mako" />
<%namespace name="common_home" file="/common_home.mako" />

%if not is_embeddable:
${ commonheader(_('Welcome Home'), "home", user, request) | n,unicode }
${ assist.assistPanel() }
%endif

${ common_home.homeJSModels(is_embeddable) }

%if is_embeddable:

<style type="text/css">

  .step-icon {
    color: #DDDDDD;
    font-size: 116px;
    margin: 10px;
    margin-right: 20px;
    width: 130px;
  }

  .nav-tabs > li.active {
    padding: 0;
  }

  svg.hi {
    width: 24px;
  }
</style>

%else:

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
  % if conf.CUSTOM.BANNER_TOP_HTML.get():
    top: 112px;
  % else:
    top: 82px;
  % endif
    bottom: 0;
    background-color: #FFF;
  }

  .panel-container {
    position: relative;
  }

  .left-panel {
    position: absolute;
    height: 100%;
    overflow: hidden;
    outline: none !important;
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

  .content-panel {
    position: absolute;
    height: 100%;
    overflow: hidden;
    outline: none !important;
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
    color: #0B7FAD;
  }

  .home-container {
    height: 100%;
  }

  .tab-content {
    min-height: 200px;
  }

  .step-icon {
    color: #DDDDDD;
    font-size: 116px;
    margin: 10px;
    margin-right: 20px;
    width: 130px;
  }

  .nav-tabs > li.active {
    padding: 0;
  }

  svg.hi {
    width: 24px;
  }
</style>

${ common_home.navbar() }
%endif

%if is_embeddable:
  <div id="homeComponents" class="main-content">
  <div class="vertical-full container-fluid" data-bind="style: { 'padding-left' : $root.isLeftPanelVisible() ? '0' : '20px' }">
    <div class="vertical-full row-fluid panel-container">
      <div class="content-panel home-container" data-bind="style: { 'padding-left' : $root.isLeftPanelVisible() ? '8px' : '0' }">
        <div class="doc-browser" data-bind="component: {
          name: 'doc-browser',
          params: {
            activeEntry: activeEntry
          }
        }"></div>
      </div>
    </div>
  </div>
</div>

%else :

<div id="homeComponents" class="main-content">
  <div class="vertical-full container-fluid" data-bind="style: { 'padding-left' : $root.isLeftPanelVisible() ? '0' : '20px' }">
    <div class="vertical-full row-fluid panel-container">
      <div class="assist-container left-panel" data-bind="visible: $root.isLeftPanelVisible" style="display: none;">
        <a title="${_('Toggle Assist')}" class="pointer hide-assist" data-bind="click: function() { $root.isLeftPanelVisible(false) }">
          <i class="fa fa-chevron-left"></i>
        </a>
        <div class="assist" data-bind="component: {
          name: 'assist-panel',
          params: {
            user: '${user.username}',
            sql: {
              navigationSettings: {
                openItem: false,
                showStats: true
              },
            },
            visibleAssistPanels: ['documents']
          }
        }"></div>
      </div>
      <div class="resizer" data-bind="visible: $root.isLeftPanelVisible, splitDraggable : { appName: 'notebook', leftPanelVisible: $root.isLeftPanelVisible }" style="display:none;"><div class="resize-bar">&nbsp;</div></div>
      <div class="content-panel home-container" data-bind="style: { 'padding-left' : $root.isLeftPanelVisible() ? '8px' : '0' }">
        <div class="doc-browser" data-bind="component: {
          name: 'doc-browser',
          params: {
            activeEntry: activeEntry
          }
        }"></div>
      </div>
    </div>
  </div>
</div>

%endif

${ common_home.vm(is_embeddable) }

%if not is_embeddable:
${ commonfooter(request, messages) | n,unicode }
%endif

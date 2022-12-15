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
  import sys

  from desktop.views import commonheader, commonfooter, _ko
  from desktop import conf

  if sys.version_info[0] > 2:
    from django.utils.translation import gettext as _
  else:
    from django.utils.translation import ugettext as _
%>

<%namespace name="common_home" file="/common_home.mako" />

${ common_home.homeJSModels() }

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

${ common_home.vm() }

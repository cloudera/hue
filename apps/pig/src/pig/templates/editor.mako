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

<%namespace name="navigation" file="navigation-bar.inc.mako" />
<%namespace name="utils" file="utils.inc.mako" />

${ commonheader(_('Pig'), "pig", user, "100px") | n,unicode }

<script src="/static/ext/js/datatables-paging-0.1.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout-2.1.0.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/moment.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/pig/static/js/pig.ko.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/routie-0.3.0.min.js" type="text/javascript" charset="utf-8"></script>

<div class="container-fluid">
  ${ navigation.menubar(section='editor') }
  
</div>

<br/>

<div class="container-fluid">
    <div class="row-fluid">
        <div class="span3">
            <div class="well sidebar-nav">
                <form id="advancedSettingsForm" method="POST" class="form form-horizontal noPadding">
                    <ul class="nav nav-list">
                        <li class="nav-header">${_('Editor')}</li>
                        <li class="active"><a href="#editor">${ _('Edit script') }</a></li>                        
                        <li class="nav-header">${_('Properties')}</li>
                        <li><a href="#edit-properties">${ _('Edit properties') }</a></li>
                        ##<li class="nav-header">${_('UDF')}</li>
                        ##<li><a href="#createDataset">${ _('New') }</a></li>
                        ##<li><a href="#createDataset">${ _('Add') }</a></li>
                        <li class="nav-header">${_('Actions')}</li>
                        <li>
                          <a href="#save" title="${ _('Save the script') }" rel="tooltip" data-placement="right">
                            <i class="icon-save"></i> ${ _('Save') }
                          </a>
                        </li>                            
                        <li>
                          <a id="clone-btn" href="javascript:void(0)" data-clone-url="" title="${ _('Copy the script') }" rel="tooltip" data-placement="right">
                            <i class="icon-retweet"></i> ${ _('Copy') }
                          </a>
                        </li>
                    </ul>
                </form>
            </div>
        </div>

        <div id="editor" class="section span9">
          <h1>${_('Editor')}</h1>
            <ul class="nav nav nav-pills">
              <li class="active"><a href="#pig" data-toggle="tab">${ _('Pig') }</a></li>
            </ul>                  
		    <form id="queryForm">
		      <textarea class="span11" rows="20" placeholder="A = LOAD '/user/${ user }/data';" name="script" id="script"></textarea>
		    </form>
            <br/>
        </div>
        
        <div id="edit-properties" class="section hide span9">
          <div class="alert alert-info"><h3>${ _('Edit properties') }</h3></div>
          <div id="edit-properties-body">
            None for now
          </div>
          <div class="form-actions">
            <a href="#" class="btn btn-primary" id="add-dataset-btn">${ _('Save') }</a>
          </div>
        </div>        
        
      </div>
   </div>

    <div data-bind="visible: isLoading()">
      <img src="/static/art/spinner.gif"/>
    </div>
    <div class="alert" data-bind="visible: apps().length == 0  && !isLoading()">
      ${ _('Sorry, there are no editor matching the search criteria.') }
    </div>
    <div data-bind="template: {name: 'appTemplate', foreach: apps}"></div>
  </div>

    </div>
  </div>
</div>


<script id="appTemplate" type="text/html">
  <div class="appWidget" data-bind="css: {isRunning: isRunning()}">
    <div class="appWidgetHeader">
      <div class="row-fluid">
        <div class="span11">
          <h4>
            <span data-bind="text: name"></span>
            <img src="/static/art/spinner.gif" data-bind="visible: isRunning()" align="middle" style="margin-left: 14px"/>
          </h4>
          <p data-bind="text: description"></p>
          <div data-bind="visible: output() != '' && output() != null" style="margin-bottom:6px">
            <a data-bind="attr: {'href': output(), 'target': '_blank'}"><i class="icon-file"></i> ${ _('Output') }</a>
          </div>
        </div>
        <div class="span1 shortcuts">
          <a class="shortcut" data-bind="click: $root.manageApp, attr: {'title': tooltip()}" rel="tooltip">
            <i data-bind="css: {'shortcutIcon': name != '', 'icon-play': status() == '' || status() == 'STOPPED' || status() == 'SUCCEEDED', 'icon-stop': status() == 'RUNNING'}"></i>
          </a>
        </div>
      </div>
    </div>
    <div data-bind="visible: name != '', css: {'demoProgress': progress() != '', 'running': status() == 'RUNNING', 'succeeded': status() == 'SUCCEEDED', 'failed': status() == 'FAILED' || status() == 'STOPPED'}, attr: { style: progressCss }"></div>
    <div class="appWidgetContent" data-bind="visible: status() != ''">
      <div data-bind="foreach: actions">
        <div data-bind="css: {'action': name != '' ,'running': status == 'RUNNING' || status == 'PREP', 'succeeded': status == 'OK', 'failed': status == 'FAILED' || $parent.status() == 'STOPPED'}">
          <img src="/static/art/spinner.gif"
               data-bind="visible: (status == 'RUNNING' || status == 'PREP') && $parent.isRunning()" class="pull-right"
               style="margin-right: 10px;margin-top:10px"/>
          <h6 data-bind="text: name"></h6>
        </div>
        ## scroll to top + go up or 'Log' tab?
        <pre data-bind="text: logs, visible: logs.length > 0"></pre>
      </div>
    </div>
  </div>
</script>


<link rel="stylesheet" href="/pig/static/css/pig.css">

<script type="text/javascript" charset="utf-8">
  $(document).ready(function () {
    var LABELS = {
      KILL_ERROR:"${ _('The pig job could not be killed.') }",
      TOOLTIP_PLAY:"${ _('Run this pig script') }",
      TOOLTIP_STOP:"${ _('Stop the execution') }",
      SAVED:"${ _('Saved') }",
    }
    
    var viewModel = new pigModel("${ url('pig:load_script') }", LABELS);
    ko.applyBindings(viewModel);

    viewModel.retrieveData();

    $(document).bind("updateTooltips", function () {
      $("a[rel=tooltip]").tooltip("destroy");
      $("a[rel=tooltip]").tooltip();
    });
  
    function showSection(section) {
      $(".section").hide();
      $("#" + section).show();
      highlightMenu(section);
    }
       
    function highlightMenu(section) {
      $(".nav-list li").removeClass("active");
      $("a[href='#" + section + "']").parent().addClass("active");
    }       
          
    routie({
      "editor":function () {
        showSection("editor");
      },
      "edit-properties":function () {
        showSection("edit-properties");
      },
      "save":function () {
	    viewModel.save();
      }      
    });    
  });
</script>

${ commonfooter(messages) | n,unicode }

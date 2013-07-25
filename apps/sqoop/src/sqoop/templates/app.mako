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

<%namespace name="actionbar" file="actionbar.mako" />

${ commonheader(None, "sqoop", user, "40px") | n,unicode }

<div class="top-bar" data-bind="visible:shownSection() == 'jobs-list'">
  <div style="margin-top: 4px; margin-right: 20px" class="pull-right">
    <a title="${_('Create a new job')}" href="#job/new"><i class="icon-plus-sign"></i> ${_('New job')}</a>
  </div>
  <h4>${_('Sqoop Jobs')}</h4>
  <input id="filter" type="text" class="input-xlarge search-query" placeholder="${_('Search for job name or content')}"  data-bind="visible: !isLoading()">
</div>

<div class="top-bar" data-bind="visible:shownSection() == 'job-editor', with: job">
  <!-- ko ifnot: $root.job().persisted -->
  <h4><a title="${_('Back to jobs list')}" href="#jobs">${_('Sqoop Jobs')}</a> <span class="muted">/</span> ${_('New Job')}</h4>
  <!-- /ko -->
  <!-- ko if: $root.job().persisted -->
  <h4><a title="${_('Back to jobs list')}" href="#jobs">${_('Sqoop Jobs')}</a> <span class="muted">/</span> <i data-bind="css:{'icon-download-alt': $root.job().type() == 'IMPORT', 'icon-upload-alt': $root.job().type() == 'EXPORT'}"></i> &nbsp;<span data-bind="text: $root.job().type"></span> <span class="muted" data-bind="editable: $root.job().name, editableOptions: {'placement': 'right'}"></span></h4>
  <!-- /ko -->
</div>

<div class="top-bar" data-bind="visible:shownSection() == 'connection-editor', with: editConnection">
  <!-- ko ifnot: persisted -->
  <h4><a title="${_('Back to jobs list')}" href="#jobs">${_('Sqoop Jobs')}</a> <span class="muted">/</span> <a href="#connection/edit-cancel" data-bind="text: $root.job().name"></a> <span class="muted">/</span> ${_('New Connection')}</h4>
  <!-- /ko -->
  <!-- ko if: persisted -->
  <h4><a title="${_('Back to jobs list')}" href="#jobs">${_('Sqoop Jobs')}</a> <span class="muted">/</span> <a href="#connection/edit-cancel"><i data-bind="css:{'icon-download-alt': $root.job().type() == 'IMPORT', 'icon-upload-alt': $root.job().type() == 'EXPORT'}"></i> &nbsp;<span data-bind="text: $root.job().type"></span> <span data-bind="text: $root.job().name"></span></a> <span class="muted">/</span> <span data-bind="text: name"></span></h4>
  <!-- /ko -->
</div>

<div class="container-fluid">
  <div id="sqoop-error" class="row-fluid mainSection hide">
    <div class="alert alert-error"><i class="icon-warning-sign"></i> <strong>${_('Sqoop error')}:</strong> <span class="message"></span></div>
  </div>

  <div id="jobs" class="row-fluid mainSection hide">
    <div id="jobs-list" class="row-fluid section hide">
      <div class="row-fluid" data-bind="if: !isLoading()">
        <!-- ko if: filteredJobs().length > 0 -->
        <ul class="major-list" data-bind="foreach: filteredJobs">
          <!-- ko if: submission() -->
          <li data-bind="routie: 'job/edit/' + id()" title="${ _('Click to edit') }">
            <div class="pull-right">
              <span class="label label-success" data-bind="visible: submission().status() == 'SUCCEEDED'">
                <span data-bind="text: ('${_('Last run: ')}' + submission().createdFormatted()), routie: 'job/status/' + id()"></span>
              </span>
              <span class="label label-warning" data-bind="visible: $.inArray(submission().status(), ['BOOTING', 'RUNNING', 'UNKNOWN']) > -1">
                <span data-bind="text: submission().status, routie: 'job/status/' + id()"></span>
              </span>
              <span class="label label-error" style="display: inline-block" data-bind="visible: $.inArray(submission().status(), ['FAILURE_ON_SUBMIT', 'FAILED']) > -1">
                <span data-bind="text: ('${_('Last run: ')}' + submission().createdFormatted()), routie: 'job/status/' + id()"></span>
              </span>
            </div>
            <div class="main" data-bind="template: {name: 'job-list-item'}"></div>
            <div class="sqoop-progress" data-bind="style:{ width: submission().progressFormatted() }"></div>
          </li>
          <!-- /ko -->

          <!-- ko ifnot: submission() -->
          <li data-bind="routie: 'job/edit/' + id()" title="${ _('Click to edit') }">
            <div class="main" data-bind="template: {name: 'job-list-item'}"></div>
          </li>
          <!-- /ko -->
        </ul>
        <!-- /ko -->

        <div class="span10 offset1 center" data-bind="if: filteredJobs().length == 0">
          <i class="icon-plus-sign waiting"></i>
          <h1 class="emptyMessage">${ _('There are currently no jobs.') }<br/>${ _('Please click on New Job to add one.') }</h1>
        </div>
      </div>

      <div class="row-fluid" data-bind="if: isLoading">
        <div class="span10 offset1 center">
          <i class="icon-spinner icon-spin" style="font-size: 60px; color: #DDD"></i>
        </div>
      </div>
    </div>

    <div id="job-editor" class="row-fluid section hide" data-bind="with: job">
      <div class="well sidebar-nav span2" data-bind="visible: $root.job().persisted">
        <form id="advanced-settings" method="POST" class="form form-horizontal noPadding">
          <ul class="nav nav-list">
            <li class="nav-header" data-bind="visible: $root.job().persisted">${_('Actions')}</li>
            <li data-bind="visible: $root.job().persisted() && !$root.job().isRunning()">
              <a data-placement="right" rel="tooltip" title="${_('Run the job')}" href="#job/save-and-run">
                <i class="icon-play"></i> ${_('Run')}
              </a>
            </li>
            <li data-bind="visible: $root.job().isRunning()">
              <a data-placement="right" rel="tooltip" title="${_('Stop the job')}" href="#job/stop">
                <i class="icon-stop"></i> ${_('Stop')}
              </a>
            </li>
            <li data-bind="visible: $root.job().persisted">
              <a data-placement="right" rel="tooltip" title="${_('Copy the job')}" href="#job/copy">
                <i class="icon-copy"></i> ${_('Copy')}
              </a>
            </li>
            <li data-bind="visible: $root.job().persisted">
              <a data-placement="right" rel="tooltip" title="${_('Delete the job')}" href="#job/delete">
                <i class="icon-remove"></i> ${_('Delete')}
              </a>
            </li>
            <li class="nav-header" data-bind="visible: $root.job().persisted">${_('Submissions')}</li>
            <li data-bind="visible: $root.job().persisted()">
              <a data-bind="attr: { 'href': $root.job().outputDirectoryFilebrowserURL }" data-placement="right" rel="tooltip" title="${_('Browse output directory')}" href="javascript:void(0);" target="_new">
                <i class="icon-folder-open"></i> ${_('Output directory')}
              </a>
            </li>
            <li class="nav-header" data-bind="visible: $root.job().persisted">${_('Last status')}</li>
            <li data-bind="visible: $root.job().persisted">
              <span class="label label-success" data-bind="visible: submission().status() == 'SUCCEEDED'">
                <span data-bind="text:  submission().createdFormatted(), routie: 'job/status/' + id()"></span>
              </span>
              <span class="label label-warning" data-bind="visible: $.inArray(submission().status(), ['BOOTING', 'RUNNING', 'UNKNOWN']) > -1">
                <span data-bind="text: submission().status, routie: 'job/status/' + id()"></span>
              </span>
              <span class="label label-error" style="display: inline-block" data-bind="visible: $.inArray(submission().status(), ['FAILURE_ON_SUBMIT', 'FAILED']) > -1">
                <span data-bind="text: submission().createdFormatted(), routie: 'job/status/' + id()"></span>
              </span>
            </li>
            <li data-bind="visible: $root.job().isRunning()">
              <div class="progress progress-striped active" style="margin-top: 10px">
                <div class="bar bar-warning" data-bind="style:{ width: submission().progressFormatted() }"></div>
              </div>
            </li>
          </ul>
        </form>
      </div>

      <div id="job-forms" data-bind="css: { span10: $root.job().persisted, span12: !$root.job().persisted}">
        <!-- ko if: $root.jobWizard.page -->
          <!-- ko with: $root.jobWizard -->
          <ul class="nav nav-pills" data-bind="foreach: pages">
            <li data-bind="css: {'active': $parent.index() == $index()}">
              <a href="javascript:void(0);" data-bind="routie: 'job/edit/wizard/' + identifier(), text: caption"></a>
            </li>
          </ul>
          <form method="POST" class="form form-horizontal noPadding" data-bind="with: page">
            <div class="job-form" data-bind="template: {'name': template(), 'data': node}">
            </div>

            <div class="form-actions row-fluid">
              <div data-bind="css: { span10: $root.job().persisted, offset2: $root.job().persisted, span12: !$root.job().persisted}">
              <!-- ko if: $parent.hasPrevious -->
              <a class="btn" data-bind="routie: 'job/edit/wizard/' + $parent.previousIndex()">${_('Back')}</a>
              &nbsp;
              <!-- /ko -->
              <!-- ko if: $parent.hasNext -->
              <a class="btn btn-primary" data-bind="routie: 'job/edit/wizard/' + $parent.nextIndex()">${_('Next')}</a>
              <!-- /ko -->
              <!-- ko ifnot: $parent.hasNext -->
              <a class="btn" href="#job/save">${_('Save')}</a>
              &nbsp;
              <a class="btn btn-primary" href="#job/save-and-run">${_('Save and run')}</a>
              <!-- /ko -->
              </div>
            </div>
          </form>
          <!-- /ko -->
        <!-- /ko -->
      </div>
    </div>

    <div id="connection-editor" class="row-fluid section hide" data-bind="with: editConnection">
      <div id="connection-forms" class="span12">
        <form method="POST" class="form form-horizontal noPadding">
          <div class="control-group">
            <label class="control-label">${ _('Name') }</label>
            <div class="controls">
              <input type="text" name="connection-name" data-bind="value: name">
            </div>
          </div>
          <div class="control-group" data-bind="visible: !persisted()">
            <label class="control-label">${ _('Connector') }</label>
            <div class="controls">
              <select class="input-xlarge" name="connector" data-bind="'options': $root.connectors, 'optionsText': function(item) { return item.name(); }, 'optionsValue': function(item) { return item.id(); }, 'value': connector_id">
              </select>
              </div>
          </div>
          <fieldset data-bind="foreach: connector">
            <div data-bind="foreach: inputs">
              <div data-bind="template: 'connector-' + type().toLowerCase()"></div>
            </div>
          </fieldset>
          <fieldset data-bind="foreach: framework">
            <div data-bind="foreach: inputs">
              <div data-bind="template: 'framework-' + type().toLowerCase()"></div>
            </div>
          </fieldset>
          <div class="form-actions">
            <a href="#connection/edit-cancel" class="btn">${_('Cancel and return to job')}</a>
            <a href="#connection/save" class="btn btn-primary">${_('Save')}</a>
          </div>
        </form>
      </div>
    </div>

    <div id="job-status" class="row-fluid section hide" data-bind="with: job">
      <div class="well sidebar-nav span2">
        <form id="advanced-settings" method="POST" class="form form-horizontal noPadding">
          <ul class="nav nav-list">
            <li>
              <a rel="tooltip" title="${_('Logs')}" href="javascript:void(0);" target="_new" data-bind="attr: {href: '/jobbrowser/jobs/' + $root.job().submission().external_id()}">
                <i class="icon-list"></i>
                ${_('Logs')}
              </a>
            </li>
            <li>
              <a rel="tooltip" title="${_('Back to editing a job')}" href="#job/edit">
                <i class="icon-arrow-left"></i>
                ${_('Back to job')}
              </a>
            </li>
          </ul>
        </form>
      </div>

    </div>
  </div>
</div>


<script type="text/html" id="job-list-item">
<h4 style="display: inline-block">
  <!-- ko if: type() == 'IMPORT' -->
  <i class="icon-download-alt"></i>&nbsp;
  <span data-bind="text: type"></span>
  <span data-bind="text: name"></span>
  <span class="muted">
    <span>${_('From ')}</span>
    <span data-bind="text: $root.getDatabaseByConnectionId(connection_id())"></span>
    <span>${_('To ')}</span>
    <span data-bind="text: storageType"></span>
  </span>
  <!-- /ko -->
  <!-- ko if: type() == 'EXPORT' -->
  <i class="icon-upload-alt"></i>&nbsp;
  <span data-bind="text: type"></span>
  <span class="muted">
    <span>${_('From ')}</span>
    <span data-bind="text: storageType"></span>
    <span>${_('To ')}</span>
    <span data-bind="text: $root.getDatabaseByConnectionId(connection_id())"></span>
  </span>
  <!-- /ko -->
</h4>
</script>

<script type="text/html" id="job-editor-form-error">
<!-- ko if: name() in $root.errors() -->
  <div class="alert alert-error">
  <!-- ko foreach: $root.errors()[name()]  -->
    <span data-bind="text: message"></span>
  <!-- /ko -->
  </div>
<!-- /ko -->
<!-- ko if: name() in $root.warnings() -->
  <div class="alert">
  <!-- ko foreach: $root.warnings()[name()]  -->
    <span data-bind="text: message"></span>
  <!-- /ko -->
  </div>
<!-- /ko -->
</script>

<script type="text/html" id="job-editor-form-field-error">
<!-- ko if: name() in $root.errors() -->
  <!-- ko foreach: $root.errors()[name()]  -->
    <span data-bind="text: message" class="help-inline"></span>
  <!-- /ko -->
<!-- /ko -->
<!-- ko if: name() in $root.warnings() -->
  <!-- ko foreach: $root.warnings()[name()]  -->
    <span data-bind="text: message" class="help-inline"></span>
  <!-- /ko -->
<!-- /ko -->
</script>

<script type="text/html" id="job-editor-begin">
<fieldset>
  <div class="control-group">
    <label class="control-label">${ _('Name') }</label>
    <div class="controls">
      <input type="text" name="connection-name" data-bind="value: name">
    </div>
  </div>

  <div class="control-group">
    <label class="control-label">${ _('Job type') }</label>
    <div class="controls">
      <div data-bind="css:{ 'big-btn': type() != '', 'selected': type() == 'IMPORT' }, click: setImport">
        <i class="icon-download-alt"></i><br/>
        ${ _('Import') }
      </div>
      <div data-bind="css:{ 'big-btn': type() != '', 'selected': type() == 'EXPORT' }, click: setExport">
        <i class="icon-upload-alt"></i><br/>
        ${ _('Export') }
      </div>
      <input name="type" type="hidden" data-bind="value: type" />
    </div>
  </div>

  <div class="control-group">
    <label class="control-label">${ _('Connection') }</label>
    <div class="controls">
      <select name="connection" class="input-xlarge" data-bind="'options': $root.persistedConnections, 'optionsText': function(item) {return item.name();}, 'value': $root.connection">
      </select>
      <!-- ko if: $root.connection() -->
      <div style="display:inline">
        <a data-bind="routie: 'connection/edit/' + $root.connection().id()" href="javascript:void(0);" class="subbtn" style="margin-left: 5px">
          <i class="icon-edit"></i> ${_('Edit')}
        </a>
        <a data-bind="routie: 'connection/delete/' + $root.connection().id()" href="javascript:void(0);" class="subbtn" style="margin-left: 5px">
          <i class="icon-remove"></i> ${_('Delete')}
        </a>
      </div>
      <!-- /ko -->
      <div class="clearfix"></div>
      <a data-bind="routie: 'connection/new'" href="javascript:void(0);" style="margin: 5px; display: block">
        <i class="icon-plus"></i> ${_('Add a new connection')}
      </a>
    </div>
  </div>
</fieldset>
</script>

<script type="text/html" id="job-editor-connector">
<fieldset data-bind="foreach: connector">
  <div data-bind="template: {'name': 'job-editor-form-error'}" class=""></div>
  <div data-bind="foreach: inputs">
    <div data-bind="template: 'connector-' + type().toLowerCase()"></div>
  </div>
</fieldset>
</script>

<script type="text/html" id="job-editor-framework">
<fieldset data-bind="foreach: framework">
  <div data-bind="template: {'name': 'job-editor-form-error'}" class=""></div>
  <div data-bind="foreach: inputs">
    <div data-bind="template: 'framework-' + type().toLowerCase()"></div>
  </div>
</fieldset>
</script>

<script type="text/html" id="framework-enum">
<div data-bind="css:{'control-group': id() != null, warning: name() in $root.warnings(), error: name() in $root.errors()}">
  <label class="control-label" data-bind="text: $root.label('framework', name())"></label>
  <div class="controls">
    <select class="input-xlarge" data-bind="'options': values, 'value': value, 'optionsCaption': '${ _('Choose...') }', 'attr': { 'name': name, 'title': $root.help('framework', name())}" rel="tooltip">
    </select>
    <span data-bind="template: {'name': 'job-editor-form-field-error'}" class="help-inline"></span>
  </div>
</div>
</script>

<script type="text/html" id="framework-map">
<div data-bind="css: {
                  warning: name() in $root.warnings(),
                  error: name() in $root.errors()
                }" class="control-group">
  <label class="control-label" data-bind="text: $root.label('framework', name())" rel="tooltip"></label>
  <div class="controls">
    <input class="input-xlarge" data-bind="value: value, attr: {'type': (sensitive() ? 'password' : 'text'), 'name': name, 'title': $root.help('framework', name())}" rel="tooltip">
    <span data-bind="template: {'name': 'job-editor-form-field-error'}" class="help-inline"></span>
  </div>
</div>
</script>

<script type="text/html" id="framework-string">
<div data-bind="css: {
                  warning: name() in $root.warnings(),
                  error: name() in $root.errors()
                }" class="control-group">
  <label class="control-label" data-bind="text: $root.label('framework', name())" rel="tooltip"></label>
  <div class="controls">
    <input class="input-xlarge" data-bind="value: value, attr: { 'type': (sensitive() ? 'password' : 'text'), 'name': name, 'title': $root.help('framework', name()) }" rel="tooltip">
    <span data-bind="template: { 'name': 'job-editor-form-field-error' }" class="help-inline"></span>
  </div>
</div>
</script>

<script type="text/html" id="framework-integer">
<div data-bind="css: {
                  warning: name() in $root.warnings(),
                  error: name() in $root.errors()
                }" class="control-group">
  <label class="control-label" data-bind="text: $root.label('framework', name())" rel="tooltip"></label>
  <div class="controls">
    <input class="input-xlarge" data-bind="value: value, attr: { 'type': (sensitive() ? 'password' : 'text'), 'name': name, 'title': $root.help('framework', name()) }" rel="tooltip">
    <span data-bind="template: { 'name': 'job-editor-form-field-error' }" class="help-inline"></span>
  </div>
</div>
</script>

<script type="text/html" id="framework-boolean">
<div data-bind="css: {
                  warning: name() in $root.warnings(),
                  error: name() in $root.errors()
                }" class="control-group">
  <label class="control-label" data-bind="text: $root.label('framework', name())" rel="tooltip"></label>
  <div class="controls">
    <div class="btn-group inline" data-toggle="buttons-radio" style="display: inline">
      <button data-bind="clickValue: value, attr: {'name': name}" type="button" value="true" class="btn" data-toggle="button">${_('True')}</button>
      <button data-bind="clickValue: value, attr: {'name': name}" type="button" value="false" class="btn" data-toggle="button">${_('False')}</button>
    </div>
    <span data-bind="template: {
                       'name': 'job-editor-form-field-error'
                     }" class="help-inline"></span>
  </div>
</div>
</script>

<script type="text/html" id="connector-enum">
<div data-bind="css: {
                  warning: name() in $root.warnings(),
                  error: name() in $root.errors()
                }" class="control-group">
  <label class="control-label" data-bind="text: $root.label('connector', name())" rel="tooltip"></label>
  <div class="controls">
    <select class="input-xlarge" data-bind="'options': values, 'value': value, 'optionsCaption': '${ _('Choose...') }', attr: { 'name': name, 'title': $root.help('connector', name()) }" rel="tooltip">
    </select>
    <span data-bind="template: { 'name': 'job-editor-form-field-error' }" class="help-inline"></span>
  </div>
</div>
</script>

<script type="text/html" id="connector-map">
<div data-bind="css: {
                  warning: name() in $root.warnings(),
                  error: name() in $root.errors()
                }" class="control-group">
  <label class="control-label" data-bind="text: $root.label('connector', name())" rel="tooltip"></label>
  <div class="controls">
    <input class="input-xlarge" data-bind="value: value, attr: { 'type': (sensitive() ? 'password' : 'text'), 'name': name, 'title': $root.help('connector', name()) }" rel="tooltip">
    <span data-bind="template: { 'name': 'job-editor-form-field-error' }" class="help-inline"></span>
  </div>
</div>
</script>

<script type="text/html" id="connector-string">
<div data-bind="css: {
                  warning: name() in $root.warnings(),
                  error: name() in $root.errors()
                }" class="control-group">
  <label class="control-label" data-bind="text: $root.label('connector', name())" rel="tooltip"></label>
  <div class="controls">
    <input class="input-xlarge" data-bind="value: value, attr: { 'type': (sensitive() ? 'password' : 'text'), 'name': name, 'title': $root.help('connector', name()) }" rel="tooltip">
    <span data-bind="template: { 'name': 'job-editor-form-field-error' }" class="help-inline"></span>
  </div>
</div>
</script>

<script type="text/html" id="connector-integer">
<div data-bind="css: {
                  warning: name() in $root.warnings(),
                  error: name() in $root.errors()
                }" class="control-group">
  <label class="control-label" data-bind="text: $root.label('connector', name())" rel="tooltip"></label>
  <div class="controls">
    <input class="input-xlarge" data-bind="value: value, attr: { 'type': (sensitive() ? 'password' : 'text'), 'name': name, 'title': $root.help('connector', name())}" rel="tooltip">
    <span data-bind="template: {'name': 'job-editor-form-field-error'}" class="help-inline"></span>
  </div>
</div>
</script>

<script type="text/html" id="connector-boolean">
<div data-bind="css: {
                  warning: name() in $root.warnings(),
                  error: name() in $root.errors()
                }" class="control-group">
  <label class="control-label" data-bind="text: $root.label('connector', name())" rel="tooltip"></label>
  <div class="controls">
    <div class="btn-group inline" data-toggle="buttons-radio" style="display: inline">
      <button data-bind="clickValue: value, attr: {'name': name}" type="button" value="true" class="btn" data-toggle="button">${_('True')}</button>
      <button data-bind="clickValue: value, attr: {'name': name}" type="button" value="false" class="btn" data-toggle="button">${_('False')}</button>
    </div>
    <span data-bind="template: {
                       'name': 'job-editor-form-field-error'
                     }" class="help-inline"></span>
  </div>
</div>
</script>

<script src="/static/ext/js/datatables-paging-0.1.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/routie-0.3.0.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/moment.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout.mapping-2.3.2.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/bootstrap-editable.min.js"></script>
<script src="/static/ext/js/knockout.x-editable.js"></script>
<script src="/sqoop/static/js/cclass.js" type="text/javascript" charset="utf-8"></script>
<script src="/sqoop/static/js/koify.js" type="text/javascript" charset="utf-8"></script>
<script src="/sqoop/static/js/sqoop.utils.js" type="text/javascript" charset="utf-8"></script>
<script src="/sqoop/static/js/sqoop.wizard.js" type="text/javascript" charset="utf-8"></script>
<script src="/sqoop/static/js/sqoop.models.js" type="text/javascript" charset="utf-8"></script>
<script src="/sqoop/static/js/sqoop.framework.js" type="text/javascript" charset="utf-8"></script>
<script src="/sqoop/static/js/sqoop.connectors.js" type="text/javascript" charset="utf-8"></script>
<script src="/sqoop/static/js/sqoop.connections.js" type="text/javascript" charset="utf-8"></script>
<script src="/sqoop/static/js/sqoop.jobs.js" type="text/javascript" charset="utf-8"></script>
<script src="/sqoop/static/js/sqoop.submissions.js" type="text/javascript" charset="utf-8"></script>
<script src="/sqoop/static/js/sqoop.js" type="text/javascript" charset="utf-8"></script>

<link href="/static/ext/css/bootstrap-editable.css" rel="stylesheet">
<link href="/sqoop/static/css/sqoop.css" rel="stylesheet">

<script type="text/javascript" charset="utf-8">
//// Job Wizard
viewModel.job.subscribe(function(job) {
  if (job) {
    viewModel.jobWizard.clearPages();
    if (job.persisted()) {
      viewModel.jobWizard.addPage(new wizard.Page({
        'identifier': 'job-editor-connector',
        'caption': '${_("Step 1: Job info")}',
        'node': job,
        'template': 'job-editor-connector',
      }));
      viewModel.jobWizard.addPage(new wizard.Page({
        'identifier': 'job-editor-framework',
        'caption': '${_("Step 2: Sqoop specific")}',
        'node': job,
        'template': 'job-editor-framework',
      }));
    } else {
      viewModel.jobWizard.addPage(new wizard.Page({
        'identifier': 'job-editor-begin',
        'caption': '${_("Step 1: Manage connections")}',
        'node': job,
        'template': 'job-editor-begin',
      }));
      viewModel.jobWizard.addPage(new wizard.Page({
        'identifier': 'job-editor-connector',
        'caption': '${_("Step 2: Job info")}',
        'node': job,
        'template': 'job-editor-connector',
      }));
      viewModel.jobWizard.addPage(new wizard.Page({
        'identifier': 'job-editor-framework',
        'caption': '${_("Step 3: Sqoop specific job info")}',
        'node': job,
        'template': 'job-editor-framework',
      }));
    }
  }
});

//// Render all data
ko.applyBindings(viewModel);

//// Events
function handle_form_errors(e, node, options, data) {
  // Add errors and warnings to viewModel.errors and viewModel.warnings
  var errors = data.errors;
  viewModel.errors({});
  viewModel.warnings({});
  switch(data.status) {
    case 1:
    $.each(errors, function(component, err) {
      $.jHueNotify.error(err);
    });
    break;
    case 100:
    $.each(errors, function(component, dict) {
      $.each(dict['messages'], function(resource, message_dict) {
        var el = $('*[name="' + resource + '"]');
        var has_error = false;

        switch(message_dict.status) {
          case 'ACCEPTABLE':
          $.setdefault(viewModel.warnings(), resource, []).push(message_dict);
          has_error = true;
          break;

          default:
          case 'UNACCEPTABLE':
          $.setdefault(viewModel.errors(), resource, []).push(message_dict);
          has_error = true;
          break;
        }

        if (has_error && el.length > 0) {
          ko.dataFor(el[0]).name.valueHasMutated();
        }
      });
    });
    break;
  }
}

$(document).on('connection_error.jobs', function(e, name, options, jqXHR) {
  $('#sqoop-error .message').text("${ _('Cannot connect to sqoop server.') }");
  routie('error');
});

$(document).on('started.job', function(e, job, options, submission_dict) {
  $.jHueNotify.info("${ _('Started job.') }");
});

$(document).on('start_fail.job', function(e, job, options, message) {
  $.jHueNotify.error("${ _('Could not start job: ') }" + message);
});

$(document).on('stopped.job', function(e, job, options, submission_dict) {
  $.jHueNotify.info("${ _('Stopped job.') }");
});

$(document).on('stop_fail.job', function(e, job, options, submission_dict) {
  $.jHueNotify.info("${ _('Could not stop job.') }");
});

$(document).on('save_fail.job', handle_form_errors);
$(document).on('save_fail.connection', handle_form_errors);
$(document).on('delete_fail.job', handle_form_errors);

$(document).on('show_section', function(e, section){
  viewModel.shownSection(section);
});

$(document).on('keyup', 'input#filter', function() {
  viewModel.filter($('#filter').val());
});

$("#jobs-list tbody").on('click', 'tr', function() {
  var job = ko.dataFor(this);
  job.selected(!job.selected());
});

//// Load all the data
var framework = new framework.Framework({modelDict: {}});
$(document).one('loaded.jobs', function() {
  framework.load();
  connectors.fetchConnectors();
  connections.fetchConnections();
  submissions.fetchSubmissions();
});
jobs.fetchJobs();


//// Routes
$(document).ready(function () {
  window.location.hash = 'jobs';
  routie({
    "error": function() {
      showMainSection("sqoop-error");
      routie.removeAll();
    },
    "jobs": function() {
      showSection("jobs", "jobs-list");
    },
    "job/edit": function() {
      if (!viewModel.job()) {
        routie('jobs');
      }
      showSection("jobs", "job-editor");
      $("*[rel=tooltip]").tooltip({
        placement: 'right'
      });
    },
    "job/edit/wizard/:page": function(page) {
      if ($.isNumeric(page)) {
        viewModel.jobWizard.index(parseInt(page));
      } else {
        viewModel.jobWizard.index(viewModel.jobWizard.getIndex(page));
      }
      $("*[rel=tooltip]").tooltip({
        placement: 'right'
      });
    },
    "job/edit/:id": function(id) {
      viewModel.chooseJobById(id);
      showSection("jobs", "job-editor");
      $("*[rel=tooltip]").tooltip({
        placement: 'right'
      });
    },
    "job/new": function() {
      viewModel.newJob("${_('Untitled Job')}");
      showSection("jobs", "job-editor");
      $("*[rel=tooltip]").tooltip({
        placement: 'right'
      });
    },
    "job/save": function() {
      viewModel.saveJob();
      $(document).one('saved.job', function(){
        routie('jobs');
      });
      $(document).one('save_fail.job', function(){
        routie('job/edit');
      });
    },
    "job/run": function() {
      if (viewModel.job()) {
        viewModel.job().start();
      }
      routie('jobs');
    },
    "job/run/:id": function(id) {
      viewModel.chooseJobById(id);
      viewModel.job().start();
      routie('jobs');
    },
    "job/save-and-run": function() {
      viewModel.saveJob();
      $(document).one('saved.job', function(){
        routie('job/run');
      });
      $(document).one('save_fail.connection', function(){
        routie('job/edit');
      });
    },
    "job/stop": function() {
      if (viewModel.job()) {
        viewModel.job().stop();
      }
      routie('jobs');
    },
    "job/stop/:id": function(id) {
      viewModel.chooseJobById(id);
      routie('job/stop');
    },
    "job/status": function() {
      showSection("jobs", "job-status");
    },
    "job/status/:id": function(id) {
      viewModel.chooseJobById(id);
      routie('job/status');
    },
    "job/copy": function() {
      if (viewModel.job()) {
        viewModel.job().clone();
      }
      routie('jobs');
    },
    "job/copy/:id": function(id) {
      viewModel.chooseJobById(id);
      routie('job/copy');
    },
    "job/delete": function() {
      if (viewModel.job()) {
        $(document).one('deleted.job', function(){routie('jobs');});
        viewModel.job().delete();
      } else {
        routie('jobs');
      }
    },
    "job/delete/:id": function(id) {
      viewModel.chooseJobById(id);
      routie('job/delete');
    },
    "connection/edit": function() {
      if (viewModel.connection()) {
        routie('')
      }
      showSection("jobs", "connection-editor");
      $("*[rel=tooltip]").tooltip({
        placement: 'right'
      });
    },
    "connection/edit/:id": function(id) {
      viewModel.chooseConnectionById(id);
      showSection("jobs", "connection-editor");
      $("*[rel=tooltip]").tooltip({
        placement: 'right'
      });
    },
    "connection/edit-cancel": function() {
      if (!viewModel.connection().persisted()) {
        viewModel.connections.pop();
      }
      routie('job/edit');
    },
    "connection/new": function() {
      viewModel.newConnection();
      routie('connection/edit');
    },
    "connection/save": function() {
      viewModel.saveConnection();
      $(document).one('saved.connection', function(){
        routie('job/edit');
      });
      $(document).one('save_fail.connection', function(){
        routie('connection/edit');
      });
    },
    "connection/copy": function() {
      if (viewModel.connection()) {
        viewModel.connection().clone();
      }
      routie('job/edit');
    },
    "connection/delete": function() {
      if (viewModel.connection()) {
        viewModel.connection().delete();
        $(document).one('deleted.connection', function(){
          routie('job/edit');
        });
      } else {
        routie('job/edit');
      }
    },
    "connection/delete/:id": function(id) {
      viewModel.chooseConnectionById(id);
      viewModel.connection().delete();
      $(document).one('deleted.connection', function(){
        routie('job/edit');
      });
    }
  });

  $("*[rel=tooltip]").tooltip({
    placement: 'right'
  });
});
</script>

${ commonfooter(messages) | n,unicode }

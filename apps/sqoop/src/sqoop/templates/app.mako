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
  from desktop.views import commonheader, commonfooter, _ko
  from desktop import conf
  from django.utils.translation import ugettext as _
  from django.urls import reverse
%>

<%namespace name="actionbar" file="actionbar.mako" />

%if not is_embeddable:
${ commonheader(None, "sqoop", user, request) | n,unicode }
%endif

<div id="sqoopComponents">
  <div data-bind="if: !isLoading(), css: {'hide': isLoading}" id="top-bar-container" class="hide">
    <div class="top-bar" data-bind="visible:shownSection() == 'jobs-list'">
      <div style="margin-top: 4px; margin-right: 40px" class="pull-right">
        <a title="${_('Create a new job')}" href="#job/new" data-bind="visible: isReady"><i class="fa fa-plus-circle"></i> ${_('New job')}</a>
      </div>
      <div style="margin-top: 4px; margin-right: 40px" class="pull-right">
        <a title="${_('Manage links')}" href="#links" data-bind="visible: isReady"><i class="fa fa-list"></i> ${_('Manage links')}</a>
      </div>
      <h4>${_('Sqoop Jobs')}</h4>
      <input id="filter-jobs" type="text" class="input-xlarge search-query sqoop-filter" placeholder="${_('Search for job name or content')}"  data-bind="visible: isReady">
    </div>

    <div class="top-bar" data-bind="visible:shownSection() == 'links-list'">
      <div style="margin-top: 4px; margin-right: 40px" class="pull-right">
        <a title="${_('Create a new link')}" href="#link/new" data-bind="visible: isReady"><i class="fa fa-plus-circle"></i> ${_('New link')}</a>
      </div>
      <div style="margin-top: 4px; margin-right: 40px" class="pull-right">
        <a title="${_('Manage jobs')}" href="#jobs" data-bind="visible: isReady"><i class="fa fa-list"></i> ${_('Manage jobs')}</a>
      </div>
      <h4>${_('Sqoop Links')}</h4>
      <input id="filter-links" type="text" class="input-xlarge search-query sqoop-filter" placeholder="${_('Search for link name or content')}"  data-bind="visible: isReady">
    </div>

    <!-- ko if: job -->
    <div class="top-bar" data-bind="visible:shownSection() == 'job-editor', with: job">
      <div style="margin-top: 4px; margin-right: 40px" class="pull-right">
        <a title="${_('Create a new job')}" href="#job/new"><i class="fa fa-plus-circle"></i> ${_('New job')}</a>
      </div>
      <h4 data-bind="visible: !persisted()"><a title="${_('Back to jobs list')}" href="#jobs">${_('Sqoop Jobs')}</a> <span class="muted">/</span> ${_('New Job')}</h4>
      <h4 data-bind="visible: persisted"><a title="${_('Back to jobs list')}" href="#jobs">${_('Sqoop Jobs')}</a> <span class="muted">/</span> <i class="fa fa-arrow-circle-o-down"></i> &nbsp; <span class="muted" data-bind="editable: name, editableOptions: {'placement': 'right'}"></span></h4>
    </div>
    <!-- /ko -->

    <!-- ko if: link -->
    <div class="top-bar" data-bind="visible:shownSection() == 'link-editor', with: link">
      <h4 data-bind="visible: !persisted()"><a title="${_('Back to jobs list')}" href="#links">${_('Sqoop Links')}</a> <span class="muted">/</span> <a href="#link/edit-cancel" data-bind="text: name"></a> <span class="muted">/</span> ${_('New Connection')}</h4>
      <h4 data-bind="visible: persisted()"><a title="${_('Back to jobs list')}" href="#links">${_('Sqoop Links')}</a> <span class="muted">/</span> <a href="#link/edit-cancel"><i class="fa fa-arrow-circle-o-down"></i> &nbsp; <span data-bind="text: $root.link().name"></span></a></h4>
    </div>
    <!-- /ko -->
  </div>

  <div class="container-fluid">
    <div data-bind="foreach: sqoop_errors" id="sqoop-error" class="row-fluid mainSection hide" style="margin-top: 10px">
      <div class="alert alert-error">
        <i class="fa fa-exclamation-triangle"></i>
        <strong>${_('Sqoop error')}:</strong>
        <span data-bind="text: $data" class="message"></span>
      </div>
    </div>

    <div class="row-fluid" data-bind="if: isLoading">
      <div class="span10 offset1 center" style="margin-top: 30px">
        <i class="fa fa-spinner fa-spin big-spinner"></i>
      </div>
    </div>

    <div id="jobs" class="row-fluid mainSection hide">
      <div id="jobs-list" class="row-fluid section hide">
        <div class="row-fluid" data-bind="if: isReady">
          <ul class="major-list" data-bind="foreach: filteredJobs">
            <!-- ko if: submission -->
            <li data-bind="routie: 'job/edit/' + id()" title="${ _('Click to edit') }">
              <div class="pull-right">
                <span class="label label-success" data-bind="visible: hasSucceeded">
                  <span data-bind="text: ('${_ko('Last run: ')}' + submission().createdFormatted())"></span>
                </span>
                <span class="label label-warning" data-bind="visible: isRunning">
                  <span data-bind="text: submission().status"></span>
                </span>
                <span class="label label-error" style="display: inline-block" data-bind="visible: hasFailed">
                  <span data-bind="text: ('${_ko('Last run: ')}' + submission().createdFormatted())"></span>
                </span>
              </div>
              <div class="main" data-bind="template: {name: 'job-list-item'}"></div>
              <div class="sqoop-progress" data-bind="style:{ width: submission().progressFormatted() }, visible: submission().progress() > 0"></div>
            </li>
            <!-- /ko -->

            <!-- ko ifnot: submission -->
            <li data-bind="routie: 'job/edit/' + id()" title="${ _('Click to edit') }">
              <div class="main" data-bind="template: {name: 'job-list-item'}"></div>
            </li>
            <!-- /ko -->
          </ul>
          <div class="card" data-bind="visible: filteredJobs().length == 0">
            <div class="span10 offset1 center nojobs">
              <a href="#job/new" class="nounderline"><i class="fa fa-plus-circle waiting"></i></a>
              <h1 class="emptyMessage">${ _('There are currently no jobs.') }<br/><a href="#job/new">${ _('Click here to add one.') }</a></h1>
            </div>
            <div class="clearfix"></div>
          </div>
        </div>
      </div>

      <div id="job-editor" class="row-fluid section hide" data-bind="with: job">
        <div class="sidebar-nav span2" data-bind="visible: $root.job().persisted">
          <form id="advanced-settings" method="POST" class="form form-horizontal no-padding">
            ${ csrf_token(request) | n,unicode }
            <ul class="nav nav-list">
              <li class="nav-header" data-bind="visible: $root.job().persisted">${_('Actions')}</li>
              <li data-bind="visible: $root.job().persisted() && !$root.job().isRunning()">
                <a id="save-run-link" data-placement="right" rel="tooltip" title="${_('Run the job')}" href="#job/save-and-run">
                  <i class="fa fa-play"></i> ${_('Run')}
                </a>
              </li>
              <li data-bind="visible: $root.job().isRunning()">
                <a data-placement="right" rel="tooltip" title="${_('Stop the job')}" href="#job/stop">
                  <i class="fa fa-stop"></i> ${_('Stop')}
                </a>
              </li>
              <li data-bind="visible: $root.job().persisted">
                <a data-placement="right" rel="tooltip" title="${_('Copy the job')}" href="#job/copy">
                  <i class="fa fa-files-o"></i> ${_('Copy')}
                </a>
              </li>
              <li data-bind="visible: $root.job().persisted">
                <a data-bind="click: $root.showDeleteJobModal.bind($root)" data-placement="right" rel="tooltip" title="${_('Delete the job')}" href="javascript:void(0);">
                  <i class="fa fa-times"></i> ${_('Delete')}
                </a>
              </li>
              <li class="nav-header" data-bind="visible: $root.job().persisted() && ($root.job().outputDirectoryFilebrowserURL() || $root.job().inputDirectoryFilebrowserURL() || $root.job().submission().external_id())">${_('Submissions')}</li>
              <li data-bind="visible: $root.job().persisted() && $root.job().outputDirectoryFilebrowserURL">
                <a data-bind="attr: { 'href': $root.job().outputDirectoryFilebrowserURL }" data-placement="right" rel="tooltip" title="${_('Browse output directory')}" href="javascript:void(0);" target="_blank">
                  <i class="fa fa-folder-open"></i> ${_('Output directory')}
                </a>
              </li>
              <li data-bind="visible: $root.job().persisted() && $root.job().inputDirectoryFilebrowserURL">
                <a data-bind="attr: { 'href': $root.job().inputDirectoryFilebrowserURL }" data-placement="right" rel="tooltip" title="${_('Browse input directory')}" href="javascript:void(0);" target="_blank">
                  <i class="fa fa-folder-open"></i> ${_('Input directory')}
                </a>
              </li>
              <li data-bind="visible: $root.job().submission().external_id()">
                <a rel="tooltip" title="${_('Logs')}" href="javascript:void(0);" target="_new" data-bind="attr: {href: '/jobbrowser/jobs/' + $root.job().submission().external_id() + '/single_logs'}">
                  <i class="fa fa-list"></i>
                  ${_('Logs')}
                </a>
              </li>
              <li class="nav-header" data-bind="visible: $root.job().persisted && $.inArray(submission().status(), ['BOOTING', 'RUNNING', 'UNKNOWN', 'SUCCEEDED', 'FAILURE_ON_SUBMIT', 'FAILED']) > -1">${_('Last status')}</li>
              <li data-bind="visible: $root.job().persisted">
                <span class="label label-success" data-bind="visible: submission().status() == 'SUCCEEDED'">
                  <span data-bind="text:  submission().createdFormatted()"></span>
                </span>
                <span class="label label-warning" data-bind="visible: $.inArray(submission().status(), ['BOOTING', 'RUNNING', 'UNKNOWN']) > -1">
                  <span data-bind="text: submission().status"></span>
                </span>
                <span class="label label-error" style="display: inline-block" data-bind="visible: $.inArray(submission().status(), ['FAILURE_ON_SUBMIT', 'FAILED']) > -1">
                  <span data-bind="text: submission().createdFormatted()"></span>
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

        <div id="job-forms" data-bind="css: {span10: $root.job().persisted, span12: !$root.job().persisted}">
          <div class="card">
          <!-- ko if: $root.jobWizard.page -->
            <!-- ko with: $root.jobWizard -->
            <ul class="nav nav-pills" data-bind="foreach: pages">
              <li data-bind="css: {'active': $parent.index() == $index()}">
                <a href="javascript:void(0);" data-bind="routie: 'job/edit/wizard/' + identifier(), text: caption"></a>
              </li>
            </ul>

            <form method="POST" class="form form-horizontal no-padding" data-bind="with: page">
              ${ csrf_token(request) | n,unicode }
              <div class="alert alert-info"><h3 data-bind="text: description"></h3></div>
              <div class="job-form" data-bind="template: {'name': template(), 'data': node}">
              </div>

              <div class="form-actions">
                <!-- ko if: $parent.hasPrevious -->
                <a class="btn" data-bind="routie: 'job/edit/wizard/' + $parent.previousIndex()">${_('Back')}</a>
                &nbsp;
                <!-- /ko -->
                <!-- ko if: $parent.hasNext -->
                <a class="btn btn-primary" data-bind="routie: 'job/edit/wizard/' + $parent.nextIndex()">${_('Next')}</a>
                <!-- /ko -->
                <!-- ko ifnot: $parent.hasNext -->
                <a id="save-btn" class="btn" href="#job/save">${_('Save')}</a>
                &nbsp;
                <a id="save-run-btn" class="btn btn-primary disable-feedback" href="#job/save-and-run">${_('Save and run')}</a>
                <!-- /ko -->
              </div>
            </form>
            <!-- /ko -->
          <!-- /ko -->
            </div>
        </div>
      </div>
    </div>

    <div id="links" class="row-fluid mainSection hide">
      <div id="links-list" class="row-fluid section hide">
        <div class="row-fluid" data-bind="if: isReady">
          <ul class="major-list" data-bind="foreach: filteredLinks">
            <li data-bind="routie: 'link/edit/' + id()" title="${ _('Click to edit') }">
              <div class="main" data-bind="template: {name: 'link-list-item'}"></div>
            </li>
          </ul>
          <div class="card" data-bind="visible: filteredLinks().length == 0">
            <div class="span10 offset1 center nojobs">
              <a href="#link/new" class="nounderline"><i class="fa fa-plus-circle waiting"></i></a>
              <h1 class="emptyMessage">${ _('There are currently no links.') }<br/><a href="#link/new">${ _('Click here to add one.') }</a></h1>
            </div>
            <div class="clearfix"></div>
          </div>
        </div>
      </div>

      <div id="link-editor" class="row-fluid section hide" data-bind="with: link">
        <div id="link-forms" class="span12">
          <div class="card">
            <form method="POST" class="form form-horizontal no-padding">
              ${ csrf_token(request) | n,unicode }
              <div data-bind="template: {'name': 'link-editor-form-error', 'data': {'name': ko.observable('linkConfig')}}" class=""></div>
              <div class="control-group">
                <label class="control-label">${ _('Name') }</label>
                <div class="controls">
                  <input type="text" name="link-name" data-bind="value: name">
                </div>
              </div>
              <div class="control-group" data-bind="visible: !persisted()">
                <label class="control-label">${ _('Connector') }</label>
                <div class="controls">
                  <select class="input-xlarge" name="connector" data-bind="'options': $root.connectors, 'optionsText': function(item) { return item.name(); }, 'optionsValue': function(item) { return item.id(); }, 'value': connector_id">
                  </select>
                </div>
              </div>
              <fieldset data-bind="foreach: link_config_values">
                <div data-bind="foreach: inputs">
                  <div data-bind="template: 'connector-' + type().toLowerCase()"></div>
                </div>
              </fieldset>
              <fieldset data-bind="foreach: driver">
                <div data-bind="foreach: inputs">
                  <div data-bind="template: 'driver-' + type().toLowerCase()"></div>
                </div>
              </fieldset>
              <div class="form-actions">
                <a href="#link/edit-cancel" class="btn">${_('Cancel')}</a>
                <a href="#link/save" class="btn btn-primary">${_('Save')}</a>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div data-bind="template: {'name': modal.name(), 'if': modal.name()}" id="modal-container" class="modal hide fade"></div>

</div>
<script type="text/html" id="delete-job-modal">
<div class="modal-header">
  <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
  <h2 class="modal-title">${_("Are you sure you'd like to delete this job?") }</h2>
</div>
<div class="modal-body"></div>
<div class="modal-footer" data-bind="if: $root.job">
  <a class="btn" href="javascript:void(0);" data-dismiss="modal">${_('No')}</a>
  <a data-bind="routie: {'url': 'job/delete/' + $root.job().id(), 'bubble': true}" data-dismiss="modal" class="btn btn-danger" href="javascript:void(0);">${_('Yes, delete it')}</a>
</div>
</script>

<script type="text/html" id="delete-link-modal">
<div class="modal-header">
  <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
  <h2 class="modal-title">${_("Are you sure you'd like to delete this link?") }</h2>
</div>
<div class="modal-body"></div>
<div class="modal-footer" data-bind="if: $root.link">
  <a class="btn" href="javascript:void(0);" data-dismiss="modal">${_('No')}</a>
  <a data-bind="routie: {'url': 'link/delete/' + $root.link().id(), 'bubble': true}" data-dismiss="modal" class="btn btn-danger" href="javascript:void(0);">${_('Yes, delete it')}</a>
</div>
</script>

<script type="text/html" id="link-list-item">
<h4 style="display: inline-block">
  <i class="fa fa-cog"></i>&nbsp;
  <span data-bind="text: name" class="muted"></span>

  <!-- ko if: type() && hostAndPort() -->
  &nbsp;&nbsp;
  <span data-bind="text: type"></span>
  <span>${_("server at ")}</span>
  <span data-bind="text: hostAndPort"></span>
  <!-- /ko -->
</h4>
</script>

<script type="text/html" id="job-list-item">
<h4 style="display: inline-block">
  <i class="fa fa-download"></i>&nbsp;

  <span data-bind="text: name" class="muted"></span>

  <!-- ko if: fromLabel() && toLabel() -->
  <span data-bind="text: fromLabel"></span>
  <span>${_(' to ')}</span>
  <span data-bind="text: toLabel"></span>
  <!-- /ko -->

  <!-- ko if: (!fromLabel() || !toLabel()) && (fromLink() && toLink()) -->
  <span data-bind="text: fromLink().name()"></span>
  <span>${_(' to ')}</span>
  <span data-bind="text: toLink().name()"></span>
  <!-- /ko -->
</h4>
</script>

<script type="text/html" id="link-editor-form-error">
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
  <div data-bind="template: {'name': 'job-editor-form-error', 'data': {'name': ko.observable('link')}}" class=""></div>

  <div class="control-group">
    <label class="control-label">${ _('Name') }</label>
    <div class="controls">
      <input type="text" name="link-name" data-bind="value: name">
    </div>
  </div>

  <div class="control-group">
    <label class="control-label">${ _('From link') }</label>
    <div class="controls">
      <select name="from-link" class="input-xlarge" data-bind="'options': $root.persistedLinks, 'optionsText': function(item) {return item.name();}, 'value': $root.from_link">
      </select>
      <!-- ko if: $root.editLink() -->
      <div style="display:inline">
        <a data-bind="routie: 'link/edit/' + $root.from_link().id()" href="javascript:void(0);" class="subbtn" style="margin-left: 5px">
          <i class="fa fa-edit"></i> ${_('Edit')}
        </a>
        <a data-bind="click: $root.showDeleteLinkModal.bind($root)" href="javascript:void(0);" class="subbtn" style="margin-left: 5px">
          <i class="fa fa-times"></i> ${_('Delete')}
        </a>
      </div>
      <!-- /ko -->
    </div>
  </div>

  <div class="control-group">
    <label class="control-label">${ _('To link') }</label>
    <div class="controls">
      <select name="from-link" class="input-xlarge" data-bind="'options': $root.persistedLinks, 'optionsText': function(item) {return item.name();}, 'value': $root.to_link">
      </select>
      <!-- ko if: $root.editLink() -->
      <div style="display:inline">
        <a data-bind="routie: 'link/edit/' + $root.to_link().id()" href="javascript:void(0);" class="subbtn" style="margin-left: 5px">
          <i class="fa fa-edit"></i> ${_('Edit')}
        </a>
        <a data-bind="click: $root.showDeleteLinkModal.bind($root)" href="javascript:void(0);" class="subbtn" style="margin-left: 5px">
          <i class="fa fa-times"></i> ${_('Delete')}
        </a>
      </div>
      <!-- /ko -->
    </div>
  </div>

  <div class="control-group">
    <div class="controls">
      <a data-bind="routie: 'link/new'" href="javascript:void(0);" style="margin: 5px; display: block">
        <i class="fa fa-plus"></i> ${_('Add a new link')}
      </a>
    </div>
  </div>
</fieldset>
</script>

<script type="text/html" id="job-editor-from">
<fieldset data-bind="foreach: from_config_values">
  <div data-bind="template: {'name': 'job-editor-form-error'}" class=""></div>
  <div data-bind="foreach: inputs">
    <div data-bind="template: 'connector-' + type().toLowerCase()"></div>
  </div>
</fieldset>

<fieldset data-bind="foreach: driver_config_values">
  <div data-bind="template: {'name': 'job-editor-form-error'}" class=""></div>
  <div data-bind="foreach: inputs">
    <div data-bind="template: 'driver-' + type().toLowerCase()"></div>
  </div>
</fieldset>
</script>

<script type="text/html" id="job-editor-to">
<fieldset data-bind="foreach: to_config_values">
  <div data-bind="template: {'name': 'job-editor-form-error'}" class=""></div>
  <div data-bind="foreach: inputs">
    <div data-bind="template: 'connector-' + type().toLowerCase()"></div>
  </div>
</fieldset>

<fieldset data-bind="foreach: driver">
  <div data-bind="template: {'name': 'job-editor-form-error'}" class=""></div>
  <div data-bind="foreach: inputs">
    <div data-bind="template: 'driver-' + type().toLowerCase()"></div>
  </div>
</fieldset>
</script>

<script type="text/html" id="driver-map">
<div data-bind="css: {
                  warning: name() in $root.warnings(),
                  error: name() in $root.errors()
                }" class="control-group">
  <label class="control-label" data-bind="text: $root.label('driver', name())"></label>
  <div class="controls">

    <table data-bind="visible: value() && value().length > 0" style="margin-bottom: 4px">
      <thead>
        <tr>
          <th>${ _('Property name') }</th>
          <th>${ _('Value') }</th>
          <th/>
        </tr>
      </thead>
      <tbody data-bind="foreach: value()">
        <tr>
          <td>
            <input data-bind="'value': key,
                              'attr': {
                                'title': $root.help('driver', $parent.name())
                              }" type="text" class="span12 required propKey" />
          </td>
          <td>
            <input data-bind="value: value" type="text" class="span12 required" />
          </td>
          <td>
            <a data-bind="click: $parent.removeFromMap.bind($parent, [$index()])" class="btn" href="javascript:void(0);">${ _('Delete') }</a>
          </td>
        </tr>
      </tbody>
    </table>

    <a data-bind="click: $data.addToMap.bind($data, [])" href="javascript:void(0);" class="btn">${_('Add')}</a>
  </div>
</div>
</script>

<script type="text/html" id="driver-enum">
<div data-bind="css:{'control-group': id() != null, warning: name() in $root.warnings(), error: name() in $root.errors()}">
  <label class="control-label" data-bind="text: $root.label('driver', name())"></label>
  <div class="controls">
    <select class="input-xlarge" data-bind="'options': values, 'value': value, 'optionsCaption': '${ _ko('Choose...') }', 'attr': { 'name': name, 'title': $root.help('driver', name())}" rel="tooltip">
    </select>
    <span data-bind="template: {'name': 'job-editor-form-field-error'}" class="help-inline"></span>
  </div>
</div>
</script>

<script type="text/html" id="driver-string">
<div data-bind="css: {
                  warning: name() in $root.warnings(),
                  error: name() in $root.errors()
                }" class="control-group">
  <label class="control-label" data-bind="text: $root.label('driver', name())" rel="tooltip"></label>
  <div class="controls">
    <input data-bind="css: {'input-xxlarge': name != '', 'pathChooser': name != '', 'pathChooserExport': $root.job().type() == 'EXPORT'}, value: value, attr: { 'type': (sensitive() ? 'password' : 'text'), 'name': name, 'title': $root.help('driver', name()) }" rel="tooltip"><button class="btn fileChooserBtn" data-bind="click: $root.showFileChooser">..</button>
    <span data-bind="template: { 'name': 'job-editor-form-field-error' }" class="help-inline"></span>
  </div>
</div>
</script>

<script type="text/html" id="driver-integer">
<div data-bind="css: {
                  warning: name() in $root.warnings(),
                  error: name() in $root.errors()
                }" class="control-group">
  <label class="control-label" data-bind="text: $root.label('driver', name())" rel="tooltip"></label>
  <div class="controls">
    <input class="input-xlarge" data-bind="value: value, attr: { 'type': (sensitive() ? 'password' : 'text'), 'name': name, 'title': $root.help('driver', name()) }" rel="tooltip">
    <span data-bind="template: { 'name': 'job-editor-form-field-error' }" class="help-inline"></span>
  </div>
</div>
</script>

<script type="text/html" id="driver-boolean">
<div data-bind="css: {
                  warning: name() in $root.warnings(),
                  error: name() in $root.errors()
                }" class="control-group">
  <label class="control-label" data-bind="text: $root.label('driver', name())" rel="tooltip"></label>
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

<script type="text/html" id="connector-map">
<div data-bind="css: {
                  warning: name() in $root.warnings(),
                  error: name() in $root.errors()
                }" class="control-group">
  <label class="control-label" data-bind="text: $root.label('connector', name())"></label>
  <div class="controls">

    <table data-bind="visible: value() && value().length > 0" style="margin-bottom: 4px">
      <thead>
        <tr>
          <th>${ _('Property name') }</th>
          <th>${ _('Value') }</th>
          <th/>
        </tr>
      </thead>
      <tbody data-bind="foreach: value()">
        <tr>
          <td>
            <input data-bind="'value': key,
                              'attr': {
                                'title': $root.help('connector', $parent.name())
                              }" type="text" class="span12 required propKey" />
          </td>
          <td>
            <input data-bind="value: value" type="text" class="span12 required" />
          </td>
          <td>
            <a data-bind="click: $parent.removeFromMap.bind($parent, [$index()])" class="btn" href="javascript:void(0);">${ _('Delete') }</a>
          </td>
        </tr>
      </tbody>
    </table>

    <a data-bind="click: $data.addToMap.bind($data, [])" href="javascript:void(0);" class="btn">${_('Add')}</a>
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
    <select class="input-xlarge" data-bind="'options': values, 'value': value, 'optionsCaption': '${ _ko('Choose...') }', attr: { 'name': name, 'title': $root.help('connector', name()) }" rel="tooltip">
    </select>
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

<script src="${ static('desktop/ext/js/datatables-paging-0.1.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/js/hue.routie.js') }" type="text/javascript" charset="utf-8"></script>
<script>
  routie.setPathname('/sqoop');
</script>
<script src="${ static('sqoop/js/cclass.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('sqoop/js/koify.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('sqoop/js/sqoop.autocomplete.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('sqoop/js/sqoop.utils.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('sqoop/js/sqoop.wizard.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('sqoop/js/sqoop.configs.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('sqoop/js/sqoop.driver.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('sqoop/js/sqoop.connectors.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('sqoop/js/sqoop.links.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('sqoop/js/sqoop.jobs.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('sqoop/js/sqoop.submissions.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('sqoop/js/sqoop.js') }" type="text/javascript" charset="utf-8"></script>

<link href="${ static('desktop/ext/css/bootstrap-editable.css') }" rel="stylesheet">
<link href="${ static('sqoop/css/sqoop.css') }" rel="stylesheet">

<style type="text/css">
% if conf.CUSTOM.BANNER_TOP_HTML.get() or not is_embeddable:
  #sqoopComponents .top-bar {
    top: 58px!important;
  }
% endif
</style>

<script type="text/javascript">

var FB_STAT = '${reverse('filebrowser.views.stat', kwargs={'path': '/'})}';

//// Job Wizard
viewModel.job.subscribe(function(job) {
  if (job) {
    viewModel.jobWizard.clearPages();
    if (job.persisted()) {
      viewModel.jobWizard.addPage(new wizard.Page({
        'identifier': 'job-editor-from',
        'caption': '${_("Step 1: From")}',
        'description': '${_("Database")}',
        'node': job,
        'template': 'job-editor-from'
      }));
      viewModel.jobWizard.addPage(new wizard.Page({
        'identifier': 'job-editor-to',
        'caption': '${_("Step 2: To")}',
        'description': '${_("HDFS")}',
        'node': job,
        'template': 'job-editor-to'
      }));
    } else {
      viewModel.jobWizard.addPage(new wizard.Page({
        'identifier': 'job-editor-begin',
        'caption': '${_("Step 1: Information")}',
        'description': '${_("Connection")}',
        'node': job,
        'template': 'job-editor-begin'
      }));
      viewModel.jobWizard.addPage(new wizard.Page({
        'identifier': 'job-editor-from',
        'caption': '${_("Step 2: From")}',
        'description': '${_("Database")}',
        'node': job,
        'template': 'job-editor-from'
      }));
      viewModel.jobWizard.addPage(new wizard.Page({
        'identifier': 'job-editor-to',
        'caption': '${_("Step 3: To")}',
        'description': '${_("HDFS")}',
        'node': job,
        'template': 'job-editor-to'
      }));
    }
  }
});

//// Render all data
ko.applyBindings(viewModel, $('#sqoopComponents')[0]);

//// Events
function handle_form_errors(e, node, options, data) {
  // Resets save and run btns
  reset_save_buttons();
  // Add errors and warnings to viewModel.errors and viewModel.warnings
  var errors = data.errors;
  viewModel.errors({});
  viewModel.warnings({});

  switch(data.status) {
    case 1:
    $.each(errors, function(index, err) {
      $(document).trigger("error", err);
    });
    break;
    case 100:
    $.each(errors['errors'], function(index, message_dict) {
      $.each(message_dict, function(resource, message_arr) {
        var el = $('*[name="' + resource + '"]');
        var has_error = false;

        switch(message_dict.status) {
          case 'WARN':
            viewModel.warnings()[resource] = message_arr;
            has_error = true;
            break;

          default:
          case 'ERROR':
            viewModel.errors()[resource] = message_arr;
            has_error = true;
            break;
        }

        viewModel.errors.valueHasMutated();

        if (has_error) {
          if (el.length > 0) {
            ko.dataFor(el[0]).name.valueHasMutated();
          }
        }
      });
    });
    break;
  }

  routie('job/edit/wizard/job-editor-from');
}

function link_missing_error(e, node) {
  // Resets save and run btns
  reset_save_buttons();
  viewModel.errors({
    'link': [{
      'status': 'UNACCEPTABLE',
      'message': '${_("Please specify a link.")}'
    }]
  });
  viewModel.warnings({});
  routie('job/edit/wizard/job-editor-begin');
}

$(document).on('link_error.jobs', function(e, name, options, jqXHR) {
  viewModel.sqoop_errors.removeAll();
  viewModel.sqoop_errors.push("${ _('Cannot connect to sqoop server.') }");
  routie('error');
});

$(document).on('start.job', function(e, options, job) {
  $(document).trigger("info", "${ _('The job is starting...') }");
});

$(document).on('started.job', function(e, job, options, submission_dict) {
  $(document).trigger("info", "${ _('Started job.') }");
});

$(document).on('start_fail.job', function(e, job, options, error) {
  $(document).trigger("error", "${ _('Error: ') }" + (typeof error.exception != "undefined" ? error.exception : error));
});

$(document).on('stopped.job', function(e, job, options, submission_dict) {
  $(document).trigger("info", "${ _('Stopped job.') }");
});

$(document).on('stop_fail.job', function(e, job, options, submission_dict) {
  $(document).trigger("error", "${ _('Could not stop job.') }");
});

$(document).one('load_fail.job', function() {
  $(document).trigger("error", "${ _('Could not load node.') }");
});

$(document).on('save_fail.job', handle_form_errors);
$(document).on('link_missing.job', link_missing_error);
$(document).on('save_fail.link', handle_form_errors);
$(document).on('delete_fail.job', handle_form_errors);

$(document).on('show_section', function(e, section){
  viewModel.shownSection(section);
});
$(document).on('changed.page', function(e, jobWizard) {
  // Autocomplete fields and table name
  $('input[name="table.tableName"]').typeahead({
    'source': function(query, process) {
      var database = viewModel.link().database();
      switch (viewModel.link().jdbcDriver()) {
        case 'com.mysql.jdbc.Driver':
        return autocomplete.tables('mysql', database);
        case 'org.postgresql.Driver':
        return autocomplete.tables('postgresql', database);
        case 'oracle.jdbc.OracleDriver':
        return autocomplete.tables('oracle', database);
      }
      return [];
    }
  });
  $('input[name="table.partitionColumn"],input[name="table.columns"]').typeahead({
    'source': function(query, process) {
      var database = viewModel.link().database();
      if (viewModel.job()) {
        var table = viewModel.job().table();
        switch (viewModel.link().jdbcDriver()) {
          case 'com.mysql.jdbc.Driver':
          return autocomplete.columns('mysql', database, table);
          break;
          case 'org.postgresql.Driver':
          return autocomplete.columns('postgresql', database, table);
          break;
          case 'oracle.jdbc.OracleDriver':
          return autocomplete.columns('oracle', database, table);
        }
        return [];
      }
    }
  });
  // Autocomplete HDFS paths
  $('input[name="output.outputDirectory"],input[name="input.inputDirectory"]').jHueHdfsAutocomplete({
    home: "/user/${ user }/",
    smartTooltip: "${_('Did you know? You can use the tab key or CTRL + Space to autocomplete file and folder names')}"
  });
});
$(document).on('shown_section', (function(){
  var linkEditorShown = false;
  return function(e, section) {
    if (section == 'link-editor' && !linkEditorShown) {
      linkEditorShown = true;
      $('input[name="link.jdbcDriver"]').typeahead({
        'source': [
          'com.mysql.jdbc.Driver',
          'org.postgresql.Driver',
          'oracle.jdbc.OracleDriver'
        ]
      });
      $('input[name="link.linkString"]').typeahead({
        'source': function(query, process) {
          var arr = [];
          switch (viewModel.link().jdbcDriver()) {
            case 'com.mysql.jdbc.Driver':
            arr = $.map(autocomplete.databases('mysql'), function(value, index) {
              return 'jdbc:mysql://' + host + ':' + port + '/' + value;
            });
            arr.push('jdbc:mysql://[host]:[port]/[database]');
            break;
            case 'org.postgresql.Driver':
            arr = $.map(autocomplete.databases('postgresql'), function(value, index) {
              return 'jdbc:postgresql://' + host + ':' + port + '/' + value;
            });
            arr.push('jdbc:postgresql://[host]:[port]/[database]');
            break;
            case 'oracle.jdbc.OracleDriver':
            arr = $.map(autocomplete.databases('oracle'), function(value, index) {
              return 'jdbc:oracle:thin:' + host + '@:' + port + ':' + value;
            });
            arr.push('jdbc:oracle:thin:@[host]:[port]:[sid]');
            break;
          }
          return arr;
        }
      });
    }
  };
})());

$(document).on('keyup', 'input.sqoop-filter', function(e) {
  viewModel.filter($(e.target).val());
});

$("#jobs-list tbody").on('click', 'tr', function() {
  var job = ko.dataFor(this);
  job.selected(!job.selected());
});

//// Load all the data
var driver = new driver.Driver();
(function() {
  function fail(e, options, data) {
    viewModel.isLoading(false);
    viewModel.isReady(false);
    viewModel.sqoop_errors.removeAll();
    if (data.errors) {
      $.each(data.errors, function(i, error_msg) {
        viewModel.sqoop_errors.push(error_msg);
      });
    } else {
      if (data.status == 500){
        viewModel.sqoop_errors.push('${_("There was a problem with the server. Look at the Sqoop2 server logs for more details.")}');
      }
      else {
        viewModel.sqoop_errors.push('${_("Unknown error.")}');
      }
    }
    window.location.hash = 'error';
  }
  $(document).one('load_error.jobs', fail);
  $(document).one('load_error.driver', fail);
  $(document).one('load_error.connectors', fail);
  $(document).one('load_error.links', fail);
  $(document).one('load_error.submissions', fail);
  $(document).one('link_error.jobs', fail);
  $(document).one('link_error.driver', fail);
  $(document).one('link_error.connectors', fail);
  $(document).one('link_error.links', fail);
  $(document).one('link_error.submissions', fail);

  var count = 0;
  function check() {
    if (++count == 5) {
      viewModel.isLoading(false);
      viewModel.isReady(true);
    }
  }

  $(document).one('loaded.jobs', check);
  $(document).one('loaded.driver', check);
  $(document).one('loaded.connectors', check);
  $(document).one('loaded.connectors', function() {
    links.fetchLinks();
  });
  $(document).one('loaded.links', check);
  $(document).one('loaded.links', function() {
    jobs.fetchJobs();
  });
  $(document).one('loaded.submissions', check);
  $(document).one('loaded.jobs', function() {
    submissions.fetchSubmissions();
  });
  viewModel.isLoading(true);
  viewModel.isReady(false);
  driver.load();
  connectors.fetchConnectors();
})();

var fetch_links = function() {
  viewModel.isLoading(true);
  links.fetchLinks();
  $(document).one('loaded.links', function() {
    viewModel.isLoading(false);
  });
  $(document).one('load_error.links', function() {
    viewModel.isLoading(false);
  });
};

var fetch_jobs = function() {
  viewModel.isLoading(true);
  jobs.fetchJobs();
  $(document).one('loaded.jobs', function() {
    viewModel.isLoading(false);
  });
  $(document).one('load_error.jobs', function() {
    viewModel.isLoading(false);
  });
};

$(document).on('saved.link', fetch_links);
$(document).on('saved.job', fetch_jobs);
$(document).on('cloned.link', fetch_links);
$(document).on('cloned.job', fetch_jobs);
$(document).on('deleted.link', fetch_links);
$(document).on('deleted.job', fetch_jobs);

function enable_save_buttons() {
  $("#save-btn").attr("data-loading-text", $("#save-btn").text());
  $("#save-run-btn").attr("data-loading-text", $("#save-run-btn").text());
  $("#save-btn").button("loading");
  $("#save-run-btn").button("loading");
  $("#save-run-link").addClass("muted");
}

function reset_save_buttons() {
  $("#save-btn").button("reset");
  $("#save-run-btn").button("reset");
  $("#save-run-link").removeClass("muted");
}

//// Routes
$(document).ready(function () {
  $(document).on("blur", ".pathChooserExport", function () {
    var _fld = $(this);
    if (_fld.val().trim() != "") {
      $.ajax({
        type: "GET",
        url: FB_STAT + _fld.val().trim(),
        dataType: "json",
        success: function (results) {
          _fld.parents(".control-group").removeClass("warning");
          $(".tooltip").remove();
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
          _fld.parents(".control-group").addClass("warning");
          _fld.parents(".control-group").tooltip({
            placement: "top",
            trigger: "manual",
            title: "${ _('Watch out! This path currently does not exist.') }"
          }).tooltip("show");
          $(".tooltip").css("left", $(".tooltip").position().left - 200);
          window.setTimeout(function () {
            $(".tooltip").remove();
          }, 5000);
        }
      });
    }
  });

  $(document).on("focus", ".pathChooserExport", function () {
    $(this).parents(".control-group").removeClass("warning");
    $(".tooltip").remove();
  });

  function isAllowedRefreshHash(hash){
    var _allowedRefresh = ["job/edit/\\d", "job/new?", "job/run/\\d"];
    for (var i=0;i<_allowedRefresh.length;i++){
      if (hash.match(_allowedRefresh[i]) != null){
        return true;
      }
    }
    return false;
  }

  if (window.location.hash == "" || !isAllowedRefreshHash(window.location.hash)){
    window.location.hash = 'jobs';
  }

  function retryUntilLoaded(fn) {
    var _args = arguments;
    if (viewModel.isLoading()) {
      window.setTimeout(function () {
        retryUntilLoaded(_args[0]);
      }, 200);
    } else {
      fn.apply(this, _args[0]);
    }
  }

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
      $(document).trigger('changed.page', [viewModel.jobWizard]);
      $("*[rel=tooltip]").tooltip({
        placement: 'right'
      });
    },
    "job/edit/:id": function(id) {
      retryUntilLoaded(function () {
        viewModel.chooseJobById(id);
        showSection("jobs", "job-editor");
        $("*[rel=tooltip]").tooltip({
          placement: 'right'
        });
        routie('job/edit/wizard/' + 0);
      });
    },
    "job/new": function () {
      retryUntilLoaded(function () {
        viewModel.newJob("${_('Untitled Job')}");
        showSection("jobs", "job-editor");
        $("*[rel=tooltip]").tooltip({
          placement: 'right'
        });
      });
    },
    "job/save": function() {
      enable_save_buttons();
      viewModel.saveJob();
      $(document).one('saved.job', function(){
        routie('jobs');
      });
    },
    "job/run": function() {
      if (viewModel.job()) {
        viewModel.job().start();
      }
      routie('jobs');
    },
    "job/run/:id": function (id) {
      retryUntilLoaded(function () {
        viewModel.chooseJobById(id);
        viewModel.job().start();
        routie('jobs');
      });
    },
    "job/save-and-run": function() {
      enable_save_buttons();
      $(document).one('saved.job', function(e, node, options, data) {
        var options = $.extend(true, {}, node.options);

        // To get all properties correct.
        if ('model' in options) {
          delete options['model'];
        }
        if ('modelDict' in options) {
          delete options['modelDict'];
        }
        options['modelDict'] = data.job;
        node.initialize(options);

        // Reload node.
        $(document).one('loaded.job', function() {
          routie('job/run/' + node.id());
        });
        $(document).one('load_fail.job', function() {
          routie('jobs');
        });
        node.load();
      });
      viewModel.saveJob();
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
    "links": function() {
      showSection("links", "links-list");
    },
    "link/edit": function() {
      // if (viewModel.link()) {
      //   routie('')
      // }
      showSection("links", "link-editor");
      $("*[rel=tooltip]").tooltip({
        placement: 'right'
      });
    },
    "link/edit/:id": function(id) {
      viewModel.chooseLinkById(id);
      showSection("links", "link-editor");
      $("*[rel=tooltip]").tooltip({
        placement: 'right'
      });
    },
    "link/edit-cancel": function() {
      window.history.go(-2);
    },
    "link/new": function() {
      $(window).one('hashchange', function() {
        viewModel.newLink();
        routie('link/edit');
      });
      window.history.back();
    },
    "link/save": function() {
      viewModel.saveLink();
      $(document).one('saved.link', function(){
        routie('job/edit');
      });
      $(document).one('save_fail.link', function(){
        routie('link/edit');
      });
    },
    "link/copy": function() {
      if (viewModel.editLink()) {
        viewModel.link().clone();
      }
      routie('job/edit');
    },
    "link/delete": function() {
      if (viewModel.editLink()) {
        viewModel.link().delete();
        $(document).one('deleted.link', function(){
          routie('job/edit');
        });
      } else {
        routie('job/edit');
      }
    },
    "link/delete/:id": function(id) {
      viewModel.chooseLinkById(id);
      viewModel.link().delete();
      $(document).one('deleted.link', function(){
        routie('job/edit');
      });
    }
  });

  $(".nojobs").on("click", function(){
    routie("job/new");
  });

  $("*[rel=tooltip]").tooltip({
    placement: 'right'
  });
});

</script>

%if not is_embeddable:
${ commonfooter(request, messages) | n,unicode }
%endif

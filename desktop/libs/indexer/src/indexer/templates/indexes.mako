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

  from desktop import conf

  from desktop.views import commonheader, commonfooter, commonshare, commonimportexport, _ko

  if sys.version_info[0] > 2:
    from django.utils.translation import gettext as _
  else:
    from django.utils.translation import ugettext as _
%>

<%namespace name="actionbar" file="actionbar.mako" />

<%
MAIN_SCROLLABLE = is_embeddable and ".page-content" or ".content-panel"
%>

%if not is_embeddable:
${ commonheader(_("Index Browser"), "search", user, request, "60px") | n,unicode }
<script src="${ static('desktop/ext/js/jquery/plugins/jquery.mousewheel.min.js') }"></script>

<link rel="stylesheet" href="${ static('notebook/css/notebook-layout.css') }">
<style type="text/css">
% if conf.CUSTOM.BANNER_TOP_HTML.get():
  .show-assist {
    top: 110px!important;
  }
  .main-content {
    top: 112px!important;
  }
% endif
</style>
%endif

<link rel="stylesheet" href="${ static('notebook/css/notebook.css') }" type="text/css">
<link rel="stylesheet" href="${ static('indexer/css/indexes.css') }" type="text/css">
<script src="${ static('dashboard/js/search.ko.js') }" type="text/javascript" charset="utf-8"></script>

<script type="text/html" id="indexes-breadcrumbs">
  <h1>
    <!-- ko with: index() -->
    <div class="inline-block pull-right">
      <a class="btn btn-default" data-bind="hueLink: '/search/browse/' + name(), tooltip: { placement: 'bottom', delay: 750 }" title="${_('Query in a Dashboard')}" href="javascript:void(0)">
        <i class="fa fa-search fa-fw"></i> ${_('Query')}
      </a>

      <a class="btn btn-default" href="javascript:void(0)" data-bind="hueLink: '/indexer/importer/prefill/all/index/' + name(), tooltip: { placement: 'bottom', delay: 750 }" title="${_('Add data to the index')}">
        <i class="fa fa-upload fa-fw"></i> ${_('Index')}
      </a>

      <a class="btn btn-default" href="javascript:void(0)" data-toggle="modal" data-bind="click: function() { $('#deleteIndex').modal('show') }, tooltip: { placement: 'bottom', delay: 750 }" title="${_('Delete the index')}">
        <i class="fa fa-times fa-fw"></i> ${_('Delete')}
      </a>
    </div>
    <!-- /ko -->
    <ul class="nav nav-pills hue-breadcrumbs-bar">
      <li>
        <a href="javascript:void(0);" data-bind="click: showIndexes">${ _('Indexes') }
          <!-- ko if: index -->
          <span class="divider">&gt;</span>
          <!-- /ko -->
        </a>
      </li>
      <!-- ko with: index -->
      <li>
        <a href="javascript:void(0);" data-bind="text: name"></a>
      </li>
      <!-- /ko -->
    </ul>
  </h1>
</script>

<div class="navbar hue-title-bar nokids">
    <div class="navbar-inner">
      <div class="container-fluid">
        <div class="nav-collapse">
          <ul class="nav">
            <li class="app-header">
              <a href="/indexer">
                ${ _('Index Browser') }
              </a>
            </li>
          </ul>
        </div>
      </div>
    </div>
</div>

<div id="indexesComponents" class="notebook">

  % if not is_embeddable:
  <a title="${_('Toggle Assist')}" class="pointer show-assist" data-bind="visible: !$root.isLeftPanelVisible() && $root.assistAvailable(), click: function () { $root.isLeftPanelVisible(true); }">
    <i class="fa fa-chevron-right"></i>
  </a>
  % endif

  <div class="main-content">
    <div class="vertical-full container-fluid" data-bind="style: { 'padding-left' : $root.isLeftPanelVisible() ? '0' : '20px' }">
      <div class="vertical-full row-fluid panel-container">
        % if not is_embeddable:
        <div class="assist-container left-panel" data-bind="visible: $root.isLeftPanelVisible() && $root.assistAvailable()">
          <a title="${_('Toggle Assist')}" class="pointer hide-assist" data-bind="click: function() { $root.isLeftPanelVisible(false) }">
            <i class="fa fa-chevron-left"></i>
          </a>
          <div class="assist" data-bind="component: {
              name: 'assist-panel',
              params: {
                user: '${user.username}',
                sql: {
                  navigationSettings: {
                    openItem: true,
                    showStats: true
                  }
                },
                visibleAssistPanels: ['sql']
              }
            }"></div>
        </div>
        <div class="resizer" data-bind="visible: $root.isLeftPanelVisible() && $root.assistAvailable(), splitDraggable : { appName: 'notebook', leftPanelVisible: $root.isLeftPanelVisible }"><div class="resize-bar">&nbsp;</div></div>
        % endif
        <div class="content-panel">


          <div class="indexer-main">
            <!-- ko template: { name: 'indexes-breadcrumbs' } --><!-- /ko -->

            <!-- ko if: section() === 'list-indexes' -->
            <%actionbar:render>
              <%def name="search()">
                <input data-bind="clearable: indexFilter, value: indexFilter, valueUpdate: 'afterkeydown'" type="text" class="input-xlarge search-query" placeholder="${_('Search for name...')}">
              </%def>

              <%def name="actions()">
                <div class="btn-toolbar" style="display: inline; vertical-align: middle">
                  <a data-bind="click: function() { atLeastOneSelected() ? $('#deleteIndexes').modal('show') : void(0) }, css: {'btn': true, 'disabled': ! atLeastOneSelected() }">
                    <i class="fa fa-times"></i> ${ _('Delete') }
                  </a>
                </div>
              </%def>

              <%def name="creation()">
                <a href="javascript:void(0)" class="btn" data-bind="hueLink: '/indexer/importer/prefill/all/index/'">
                  <i class="fa fa-plus-circle"></i> ${ _('Create index') }
                </a>
                <a data-bind="click: function() { $root.alias.name(''); $root.alias.chosenCollections.removeAll(); $('#createAlias').modal('show'); }" class="btn">
                  <i class="fa fa-plus-circle"></i> ${ _('Create alias') }
                </a>
              </%def>
            </%actionbar:render>
            <!-- /ko -->

            <!-- ko template: { if: section() == 'list-indexes', name: 'list-indexes' }--><!-- /ko -->
            <!-- ko template: { if: section() == 'list-index', name: 'list-index', data: index() }--><!-- /ko -->

          </div>

          <!-- ko hueSpinner: { spin: isLoading, center: true, size: 'xlarge' } --><!-- /ko -->


          <div id="deleteIndexes" class="modal hide fade">
            <form id="deleteIndexesForm" method="POST" data-bind="submit: deleteIndexes">
              ${ csrf_token(request) | n,unicode }
              <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
                <h2 class="modal-title">${ _('Delete the selection?') }</h2>
              </div>
              <div class="modal-body">
                <ul data-bind="foreach: selectedIndexes">
                  <li>
                    <span data-bind="text: name"></span>
                  </li>
                </ul>
              </div>
              <div class="modal-footer">
                <a href="javascript: void(0)" class="btn" data-dismiss="modal">${ _('No') }</a>
                <input type="submit" class="btn btn-danger" value="${ _('Yes') }"/>
              </div>
            </form>
          </div>

          <div id="deleteIndex" class="modal hide fade">
            <form id="deleteIndexForm" method="POST" data-bind="submit: function() { $root.index().delete() }">
              ${ csrf_token(request) | n,unicode }
              <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
                <h2 class="modal-title">${ _('Delete?') }</h2>
              </div>
              <div class="modal-body">
                <!-- ko if: $root.index() -->
                  <span data-bind="text: $root.index().name"></span>
                <!-- /ko -->
              </div>
              <div class="modal-footer">
                <a href="javascript: void(0)" class="btn" data-dismiss="modal">${ _('No') }</a>
                <input type="submit" class="btn btn-danger" value="${ _('Yes') }"/>
              </div>
            </form>
          </div>

          <div id="createAlias" class="modal hide fade">
            <div class="modal-header">
              <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
              <h2 class="modal-title">${ _('Create alias') }</h2>
            </div>
            <div class="modal-body">
              <label class="margin-bottom-20">${ _('Alias name') } <input type="text" data-bind="textInput: alias.name" class="input-xlarge no-margin-bottom margin-left-10"></label>

              <table id="indexesChecksTable" class="table table-condensed table-nowrap">
                <thead>
                  <tr>
                    <th style="width: 1%">
                      <div class="hue-checkbox fa" data-bind="hueCheckAll: { allValues: alias.availableCollections, selectedValues: alias.chosenCollections }"></div>
                    </th>
                    <th>${_('Collection')}</th>
                  </tr>
                </thead>
                <tbody>
                <!-- ko foreach: alias.availableCollections -->
                <tr>
                  <td>
                    <div class="hue-checkbox fa" data-bind="multiCheck: '#indexesChecksTable', value: $data, hueChecked: $parent.alias.chosenCollections"></div>
                  </td>
                  <td data-bind="text: name"></td>
                </tr>
                <!-- /ko -->
                </tbody>
              </table>
            </div>
            <div class="modal-footer">
              <a href="javascript: void(0)" class="btn" data-dismiss="modal">${ _('Cancel') }</a>
              <button class="btn btn-primary disable-feedback" data-bind="click: alias.create, enable: alias.chosenCollections().length > 0 && alias.name() !== ''">
                 ${ _('Create') }
              </button>
            </div>
          </div>

        </div>
      </div>
    </div>
  </div>


</div>


<script type="text/html" id="list-indexes">
  <table class="table table-condensed datatables" id="list-indexes-table">
    <thead>
      <tr>
        <th class="vertical-align-middle" width="1%"><div data-bind="click: selectAll, css: { 'hue-checkbox': true, 'fa': true, 'fa-check': allSelected}" class="select-all"></div></th>
        <th>${ _('Name') }</th>
        <th>${ _('Type') }</th>
        <th>${ _('Collections') }</th>
      </tr>
    </thead>
    <tbody data-bind="foreach: { data: filteredIndexes }">
      <tr>
        <td data-bind="click: $root.handleSelect" class="center" style="cursor: default">
          <div data-bind="multiCheck: '#list-indexes-table', css: { 'hue-checkbox': true, 'fa': true, 'fa-check': isSelected}"></div>
        </td>
        <td><a class="pointer" data-bind="text: name, click: function() { $root.fetchIndex($data); }"></a></td>
        <td data-bind="text: type"></td>
        <td>
          <span data-bind="text: collections"></span>
          <a class="pointer" data-bind="click: $root.alias.edit, visible: type() == 'alias'">
            <i class="fa fa-pencil"></i> ${ _('Edit') }
          </a>
        </td>
      </tr>
    </tbody>
  </table>
</script>


<script type="text/html" id="list-index">
  <ul class="nav nav-tabs nav-tabs-border">
    <li class="active"><a href="#index-overview" data-toggle="tab" data-bind="click: function(){ $root.tab('index-overview'); }">${_('Overview')}</a></li>
    <li><a href="#index-columns" data-toggle="tab" data-bind="click: function(){ $root.tab('index-columns'); }">${_('Fields')} (<span data-bind="text: fields().length"></span>)</a></li>
    <li><a href="#index-sample" data-toggle="tab" data-bind="click: function(){ $root.tab('index-sample'); }">${_('Sample')} (<span data-bind="text: sample().length"></span>)</a></li>
    <li><a href="#index-config" data-toggle="tab" data-bind="click: function(){ if (!config()) { getConfig(); }; $root.tab('index-config'); }">${_('Config')}</a></li>
  </ul>

  <div class="tab-content" style="border: none; overflow: hidden">
    <div class="tab-pane active margin-top-30" id="index-overview">
      <!-- ko template: { if: $root.tab() == 'index-overview', name: 'indexes-index-overview' }--><!-- /ko -->
    </div>

    <div class="tab-pane margin-top-10" id="index-columns">
      <!-- ko if: $root.tab() == 'index-columns' -->
        <input class="input-xlarge search-query margin-left-10" type="text" placeholder="${ _('Search for a field...') }" data-bind="clearable: $root.fieldFilter, value: $root.fieldFilter, valueUpdate: 'afterkeydown'"/>
        <div class="margin-top-10">
        <!-- ko template: 'indexes-index-fields' --><!-- /ko -->
        </div>
      <!-- /ko -->
    </div>

    <div class="tab-pane" id="index-sample">
      <!-- ko if: sample() && sample().length > 0 -->
        <!-- ko template: { if: $root.tab() == 'index-sample', name: 'indexes-index-sample', data: sample(), full: true }--><!-- /ko -->
      <!-- /ko -->
      <!-- ko if: !sample() || sample().length === 0 -->
        <div class="margin-top-10 margin-left-10">${ _('The index does not contain any data.')}</div>
      <!-- /ko -->
    </div>

    <div class="tab-pane" id="index-config">
      <!-- ko hueSpinner: { spin: $root.index().loadingConfig, center: true, size: 'xlarge' } --><!-- /ko -->

      <!-- ko if: config() -->
        <div data-bind="readOnlyAce: config, type: 'json'"></div>
      <!-- /ko -->
      <!-- ko if: !config() -->
        <div class="margin-top-10 margin-left-10">${ _('The config could not be retrieved.')}</div>
      <!-- /ko -->
    </div>
  </div>
</script>


<script type="text/html" id="indexes-index-overview">
  <div>
    <!-- ko template: 'indexes-index-properties' --><!-- /ko -->

    <h4>${ _('Fields') } (<span data-bind="text: fields().length"></span>)</h4>
    <!-- ko template: { name: 'indexes-index-fields-fields', data: fieldsPreview }--><!-- /ko -->
    <a class="pointer" data-bind="visible: fields().length > fieldsPreview().length, click: function() { $('li a[href=\'#index-columns\']').click(); }">
      ${_('View more...')}
    </a>

    <br><br>

    <h4>${ _('Sample') } (<span data-bind="text: sample().length"></span>)</h4>
    <!-- ko if: samplePreview() && samplePreview().length > 0 -->
    <div style="overflow: auto">
      <!-- ko template: { name: 'indexes-index-sample', data: samplePreview, full: false }--><!-- /ko -->
    </div>
    <a class="pointer" data-bind="visible: sample().length > samplePreview().length, click: function() { $('li a[href=\'#index-sample\']').click(); }">
      ${_('View more...')}
    </a>
    <!-- /ko -->
    <!-- ko if: !samplePreview() || samplePreview().length === 0 -->
    <div class="margin-top-10 margin-bottom-30">${ _('The index does not contain any data.')}</div>
    <!-- /ko -->
  </div>
</script>


<script type="text/html" id="indexes-index-properties">
  <h4>${ _('Properties') }</h4>
  <div class="row-fluid">
    <div title="${ _('Unique Key') }">
      <i class="fa fa-fw fa-key muted"></i> <span data-bind="text: uniqueKey"></span>
    </div>
  </div>
  <br>
</script>


<script type="text/html" id="indexes-index-fields-fields">
  <div style="overflow: auto">
    <table class="table table-condensed table-nowrap">
      <thead>
        <tr>
          <th style="width: 1%">&nbsp;</th>
          <th style="width: 2%"></th>
          <th>${ _('Name') }</th>
          <th>${ _('Type') }</th>
          <th>${ _('Indexed') }</th>
          <th>${ _('Stored') }</th>
          <th>${ _('Required') }</th>
          <th>${ _('Multivalued') }</th>
          <th>${ _('Term Vectors') }</th>
          <th>${ _('Tokenized') }</th>
          <th>${ _('Term Positions') }</th>
          <th>${ _('Term Offsets') }</th>
          <th>${ _('Omit Norms') }</th>
          <th>${ _('Omit TermFreq and Positions') }</th>
          <th>${ _('Sort Missing Last') }</th>
          <th>${ _('DocValues') }</th>
        </tr>
      </thead>
      <tbody data-bind="foreach: $data">
        <tr>
          <td data-bind="text: $index() + 1"></td>
          <td>
            <i class="fa fa-info muted pointer analysis" data-bind="click: $root.showContextPopover, attr: {'title': '${ _ko('Analyze') }'}, visible: type() != 'aggr'"></i>
          </td>
          <td data-bind="text: name"></td>
          <td data-bind="text: type"></td>
          <td><i data-bind="visible: typeof $data.indexed == 'undefined' || $data.indexed" class="fa fa-check muted"></i></td>
          <td><i data-bind="visible: typeof $data.stored == 'undefined' || $data.stored" class="fa fa-check muted"></i></td>
          <td><i data-bind="visible: $data.required " class="fa fa-check muted"></i></td>
          <td><i data-bind="visible: $data.multiValued" class="fa fa-check muted"></i></td>
          <td><i data-bind="visible: $data.termVectors" class="fa fa-check muted"></i></td>
          <td><i data-bind="visible: $data.tokenized" class="fa fa-check muted"></i></td>
          <td><i data-bind="visible: $data.termPositions" class="fa fa-check muted"></i></td>
          <td><i data-bind="visible: $data.termOffsets" class="fa fa-check muted"></i></td>
          <td><i data-bind="visible: (typeof $data.omitNorms == 'undefined' && type().indexOf('text') == -1) || $data.omitNorms" class="fa fa-check muted"></i></td>
          <td><i data-bind="visible: (typeof $data.omitTermFreqAndPositions == 'undefined' && type().indexOf('text') == -1) || $data.omitTermFreqAndPositions" class="fa fa-check muted"></i></td>
          <td><i data-bind="visible: !$data.sortMissingLast" class="fa fa-check muted"></i></td>
          <td><i data-bind="visible: $data.docValues" class="fa fa-check muted"></i></td>
        </tr>
      </tbody>
    </table>
  </div>
</script>


<script type="text/html" id="indexes-index-fields">
  <div>
    <!-- ko template: { name: 'indexes-index-fields-fields', data: filteredFields }--><!-- /ko -->

    <!-- ko if: copyFields() && copyFields().length > 0 -->
    <h4>${ _('Copy Fields') }</h4>
    <table class="table table-condensed table-nowrap sample-table old-datatable">
      <thead>
        <tr>
          <th>${ _('Destination') }</th>
          <th>${ _('Source') }</th>
        </tr>
      </thead>
      <tbody>
        <!-- ko foreach: copyFields() -->
          <tr>
            <td data-bind="text: dest"></td>
            <td data-bind="text: source"></td>
          </tr>
        <!-- /ko -->
      </tbody>
    </table>
    <!-- /ko -->

    <!-- ko if: dynamicFields() && dynamicFields().length > 0 -->
    <h4>${ _('Dynamic Fields') }</h4>
    <!-- ko template: { name: 'indexes-index-fields-fields', data: dynamicFields }--><!-- /ko -->
    <!-- /ko -->
  </div>
</script>


<script type="text/html" id="indexes-index-sample">
  <!-- ko hueSpinner: { spin: $root.index().loadingSample, center: true, size: 'xlarge' } --><!-- /ko -->

  <!-- ko ifnot: $root.index().loadingSample -->
  <!-- ko if: $root.index().fields().length != 0 -->
  <table class="table table-condensed table-nowrap sample-table old-datatable">
    <thead>
      <tr>
        <th style="width: 1%">&nbsp;</th>
        <!-- ko foreach: $root.index().fields() -->
        <th data-bind="text: name"></th>
        <!-- /ko -->
      </tr>
    </thead>
    <tbody>
      <!-- ko foreach: $data -->
        <tr>
          <td data-bind="text: $index() + 1"></td>
          <!-- ko foreach: $root.index().fields() -->
            <td data-bind="text: $parent[name()]"></td>
          <!-- /ko -->
        </tr>
      <!-- /ko -->
    </tbody>
  </table>
  <!-- /ko -->

  ## Schemaless collections
  <!-- ko if: $root.index().fields().length == 0 && $data.length > 0 -->
  <table class="table table-condensed table-nowrap sample-table old-datatable">
    <thead>
      <tr>
        <th style="width: 1%">&nbsp;</th>
        <!-- ko foreach: Object.keys($data[0]) -->
        <th data-bind="text: $data"></th>
        <!-- /ko -->
      </tr>
    </thead>
    <tbody>
      <!-- ko foreach: $data -->
        <tr>
          <td data-bind="text: $index() + 1"></td>
          <!-- ko foreach: Object.keys($parent[0]) -->
            <td data-bind="text: $parent[$data]"></td>
          <!-- /ko -->
        </tr>
      <!-- /ko -->
    </tbody>
  </table>
  <!-- /ko -->

  <!-- /ko -->
</script>


<script type="application/json" id="indexOptions">
  {"index": "${index}"}
</script>


<script src="${ static('desktop/js/indexes_inline.js') }" type="text/javascript"></script>

%if not is_embeddable:
${ commonfooter(request, messages) | n,unicode }
%endif

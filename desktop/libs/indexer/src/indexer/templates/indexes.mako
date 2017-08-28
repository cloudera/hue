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
  from desktop import conf

  from desktop.views import commonheader, commonfooter, commonshare, commonimportexport, _ko
%>

<%namespace name="assist" file="/assist.mako" />
<%namespace name="actionbar" file="actionbar.mako" />

<%
MAIN_SCROLLABLE = is_embeddable and ".page-content" or ".content-panel"
%>

%if not is_embeddable:
${ commonheader(_("Index Browser"), "search", user, request, "60px") | n,unicode }
<script src="${ static('desktop/ext/js/jquery/plugins/jquery-ui-1.10.4.custom.min.js') }"></script>
<script src="${ static('desktop/ext/js/jquery/plugins/jquery.mousewheel.min.js') }"></script>

${ assist.assistJSModels() }
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

${ assist.assistPanel() }
%endif

<link rel="stylesheet" href="${ static('notebook/css/notebook.css') }" type="text/css">
<link rel="stylesheet" href="${ static('indexer/css/indexes.css') }" type="text/css">
<script src="${ static('desktop/js/hue.json.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('dashboard/js/search.ko.js') }" type="text/javascript" charset="utf-8"></script>

<script type="text/html" id="indexes-breadcrumbs">
  <h1>
    <!-- ko with: index() -->
    <div class="inline-block pull-right">
      <a class="inactive-action" data-bind="hueLink: '/search/browse/' + name(), tooltip: { placement: 'bottom', delay: 750 }" title="${_('Search the index')}" href="javascript:void(0)">
        <i class="fa fa-search fa-fw"></i>
      </a>

      <a class="inactive-action" href="javascript:void(0)" data-bind="hueLink: '/indexer/importer/prefill/all/index/' + name(), tooltip: { placement: 'bottom', delay: 750 }" title="${_('Add Data')}">
        <i class="fa fa-upload fa-fw"></i>
      </a>

      <a class="inactive-action" href="javascript:void(0)" data-toggle="modal" data-bind="click: function() { $('#deleteIndex').modal('show') }, tooltip: { placement: 'bottom', delay: 750 }">
        <i class="fa fa-times fa-fw"></i>
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

<script type="text/html" id="analysis-popover">
  <!-- ko if: $root.fieldAnalysesName() -->
  <div data-bind="with: $root.getFieldAnalysis()">
    <div class="pull-right">
      <input type="text" data-bind="visible: section() == 'terms', clearable: terms.prefix, valueUpdate:'afterkeydown'" placeholder="${ _('Prefix filter...') }"/>
    </div>
    <ul class="nav nav-tabs" role="tablist" style="margin-bottom: 20px">
      <li class="active"><a href="#analysis-terms-index" role="tab" data-toggle="tab" data-bind="click: function() { section('terms'); }">${ _('Terms') }</a></li>
      <li><a href="#analysis-stats-index" role="tab" data-toggle="tab" data-bind="click: function() { section('stats'); }">${ _('Stats') }</a></li>
    </ul>
    <div class="tab-content" style="max-height: 370px; height: 370px; border: none">
      <div class="tab-pane active" id="analysis-terms-index" data-bind="with: terms">
        <div class="widget-spinner" data-bind="visible: $parent.isLoading()">
          <i class="fa fa-spinner fa-spin"></i>
        </div>
        <div class="alert" data-bind="visible: ! $parent.isLoading() && $data.data().length == 0">${ _('There are no terms to be shown') }</div>
        <table style="width: 100%" data-bind="visible: ! $parent.isLoading() && $data.data().length > 0" class="table table-condensed">
          <tbody data-bind="foreach: $data.data">
          <tr>
            <td data-bind="text: val.value"></td>
            <td style="width: 40px">
              <div class="progress">
                <div class="bar-label" data-bind="text:val.count"></div>
                <div class="bar bar-info" style="margin-top:-20px;" data-bind="style: {'width': ((val.count / $parent.data()[0].val.count) * 100) + '%'}"></div>
              </div>
            </td>
          </tr>
          </tbody>
        </table>
      </div>
      <div class="tab-pane" id="analysis-stats-index" data-bind="with: stats">
        <div class="widget-spinner" data-bind="visible: $parent.isLoading()">
          <i class="fa fa-spinner fa-spin"></i>
        </div>
        <div class="alert" data-bind="visible: !$parent.isLoading() && $data.data().length > 0 && $data.data()[0].key.toLowerCase() == 'error'">${ _('This field does not support stats') }</div>
        <div class="alert" data-bind="visible: !$parent.isLoading() && $data.data().length == 0">${ _('There are no stats to be shown') }</div>
        <table style="width: 100%" data-bind="visible: ! $parent.isLoading() && $data.data().length > 0 && $data.data()[0].key.toLowerCase() != 'error'" class="table table-condensed">
          <tbody data-bind="foreach: $data.data">
          <tr>
            <td style="vertical-align: top"><strong data-bind="text: key"></strong></td>
            <!-- ko if: key == 'facets' -->
            <td>
              <!-- ko if: val[Object.keys(val)[0]] != null -->
              <table style="width: 400px">
                <tbody data-bind="foreach: Object.keys(val[Object.keys(val)[0]])">
                  <tr>
                    <td style="vertical-align: top; padding-left: 4px; padding-right: 4px"><strong data-bind="text: $data"></strong></td>
                    <td data-bind="template: 'stats-facets'"></td>
                  </tr>
                </tbody>
              </table>
              <!-- /ko -->
              <!-- ko ifnot: val[Object.keys(val)[0]] != null -->
              ${ _('Not available') }
              <!-- /ko -->
            </td>
            <!-- /ko -->
            <!-- ko ifnot: key == 'facets' -->
            <td data-bind="text: val"></td>
            <!-- /ko -->
          </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
  <!-- /ko -->
</script>

<div class="navbar hue-title-bar nokids">
    <div class="navbar-inner">
      <div class="container-fluid">
        <div class="nav-collapse">
          <ul class="nav">
            <li class="app-header">
              <a href="/${app_name}">
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
        <div class="content-panel" ${ not is_embeddable and 'data-bind="niceScroll"' or ''}>


          <div class="indexer-main">
            <!-- ko template: { name: 'indexes-breadcrumbs' }--><!-- /ko -->

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

            <div id="fieldAnalysisIndexes" class="popover mega-popover right">
              <div class="arrow"></div>
              <h3 class="popover-title" style="text-align: left">
                <a class="pull-right pointer" data-bind="click: function(){ $('#fieldAnalysisIndexes').hide(); $root.fieldAnalysesName(''); }"><i class="fa fa-times"></i></a>
                <strong data-bind="text: $root.fieldAnalysesName"></strong>
                <!-- ko if: $root.getFieldAnalysis() -->
                  (<span data-bind="text: $root.getFieldAnalysis().type"></span>)
                <!-- /ko -->
              </h3>
              <div class="popover-content" data-bind="template: { name: 'analysis-popover' }" style="text-align: left"></div>
            </div>

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
                <a href="#" class="btn" data-dismiss="modal">${ _('No') }</a>
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
                <a href="#" class="btn" data-dismiss="modal">${ _('No') }</a>
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
                      <div class="hueCheckbox fa" data-bind="hueCheckAll: { allValues: alias.availableCollections, selectedValues: alias.chosenCollections }"></div>
                    </th>
                    <th>${_('Collection')}</th>
                  </tr>
                </thead>
                <tbody>
                <!-- ko foreach: alias.availableCollections -->
                <tr>
                  <td>
                    <div class="hueCheckbox fa" data-bind="multiCheck: '#indexesChecksTable', value: $data, hueChecked: $parent.alias.chosenCollections"></div>
                  </td>
                  <td data-bind="text: name"></td>
                </tr>
                <!-- /ko -->
                </tbody>
              </table>
            </div>
            <div class="modal-footer">
              <a href="#" class="btn" data-dismiss="modal">${ _('Cancel') }</a>
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
  <table class="table table-condensed datatables">
    <thead>
      <tr>
        <th class="vertical-align-middle" width="1%"><div data-bind="click: selectAll, css: {hueCheckbox: true, 'fa': true, 'fa-check': allSelected}" class="select-all"></div></th>
        <th>${ _('Name') }</th>
        <th>${ _('Type') }</th>
        <th>${ _('Collections') }</th>
      </tr>
    </thead>
    <tbody data-bind="foreach: { data: filteredIndexes }">
      <tr>
        <td data-bind="click: $root.handleSelect" class="center" style="cursor: default">
          <div data-bind="css: {'hueCheckbox': true, 'fa': true, 'fa-check': isSelected}"></div>
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
    <li><a href="#index-sample" data-toggle="tab" data-bind="click: function(){ $root.tab('index-sample'); }">${_('Sample')}</a></li>
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
  </div>
</script>


<script type="text/html" id="indexes-index-overview">
  <div>
    <!-- ko template: 'indexes-index-properties' --><!-- /ko -->
    <h4>${ _('Fields') }</h4>
    <!-- ko template: { name: 'indexes-index-fields-fields', data: fieldsPreview }--><!-- /ko -->
    <a class="pointer" data-bind="visible: fields().length > fieldsPreview().length, click: function() { $('li a[href=\'#index-columns\']').click(); }">
      ${_('View more...')}
    </a>

    <br><br>

    <h4>${ _('Sample') }</h4>

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
  <div>
    <table class="table table-condensed table-nowrap">
      <thead>
        <tr>
          <th style="width: 1%">&nbsp;</th>
          <th style="width: 2%"></th>
          <th>${ _('Name') }</th>
          <th>${ _('Type') }</th>
          <th>${ _('Required') }</th>
          <th>${ _('Stored') }</th>
          <th>${ _('Indexed') }</th>
          <th>${ _('Multivalued') }</th>
        </tr>
      </thead>
      <tbody data-bind="foreach: $data">
        <tr>
          <td data-bind="text: $index() + 1"></td>
          <td>
            <i class="fa fa-info muted pointer analysis" data-bind="click: function(data, e) { $root.fieldAnalysesName(name()); $root.showFieldAnalysis(data, e); }, attr: {'title': '${ _ko('Analyze') }'}, visible: type() != 'aggr'"></i>
          </td>
          <td data-bind="text: name"></td>
          <td data-bind="text: type"></td>
          <td><i data-bind="visible: $data.required" class="fa fa-check muted"></i></td>
          <td><i data-bind="visible: $data.stored" class="fa fa-check muted"></i></td>
          <td><i data-bind="visible: $data.indexed" class="fa fa-check muted"></i></td>
          <td><i data-bind="visible: $data.multiValued" class="fa fa-check muted"></i></td>
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
    <table class="table table-condensed table-nowrap sample-table">
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
  <table class="table table-condensed table-nowrap sample-table">
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
  <table class="table table-condensed table-nowrap sample-table">
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



<script type="text/javascript">

  var IndexesViewModel = (function () {

    var Alias = function (vm) {
      var self = this;

      self.name = ko.observable('');
      self.chosenCollections = ko.observableArray();
      self.availableCollections = ko.computed(function () {
        return $.grep(vm.indexes(), function (index) {
          return index.type() == 'collection';
        });
      });

      self.create = function () {
        $.post("${ url('indexer:create_alias') }", {
          "name": self.name,
          "collections": ko.mapping.toJSON($.map(self.chosenCollections(), function (collection) {
            return collection.name();
          }))
        }, function (data) {
          if (data.status == 0) {
            vm.indexes.push(ko.mapping.fromJS(data.alias));
            huePubSub.publish('assist.collections.refresh');
          } else {
            $(document).trigger("error", data.message);
          }
          $('#createAlias').modal('hide');
        }).fail(function (xhr, textStatus, errorThrown) {
          $(document).trigger("error", xhr.responseText);
        });
        hueAnalytics.log('indexes', 'create_alias');
      }

      self.edit = function (alias) {
        self.name(alias.name());
        self.chosenCollections($.grep(vm.indexes(), function(collection) { return alias.collections().indexOf(collection.name()) != -1; }));
        $('#createAlias').modal('show');
      }
    };


    var Index = function (vm, data) {
      var self = this;

      self.name = ko.observable(data.name);
      self.type = ko.observable(data.type);
      self.uniqueKey = ko.observable(data.schema.uniqueKey);
      self.fields = ko.mapping.fromJS(data.schema.fields);
      self.fieldsPreview = ko.pureComputed(function () {
        return self.fields().slice(0, 5)
      });
      self.filteredFields = ko.computed(function () {
        var returned = self.fields();
        if (vm.fieldFilter() !== '') {
          returned = $.grep(self.fields(), function (field) {
            return field.name().toLowerCase().indexOf(vm.fieldFilter().toLowerCase()) > -1;
          });
        }
        return returned;
      });

      self.dynamicFields = ko.mapping.fromJS(data.schema.dynamicFields);
      self.copyFields = ko.mapping.fromJS(data.schema.copyFields);

      self.sample = ko.observableArray();
      self.samplePreview = ko.pureComputed(function () {
        return self.sample().splice(0, 5)
      });

      self.loadingSample = ko.observable(false);

      self.getSample = function () {
        self.loadingSample(true);
        $.post("${ url('indexer:sample_index') }", {
          name: self.name(),
          rows: 100
        }, function (data) {
          if (data.status == 0) {
            self.sample(data.sample);
          } else {
            $(document).trigger("error", data.message);
          }
        }).fail(function (xhr, textStatus, errorThrown) {
          $(document).trigger("error", xhr.responseText);
        }).always(function () {
          self.loadingSample(false);
        });
      };

      self.delete = function () {
        var indexName = self.name();
        $.post("${ url('indexer:delete_indexes') }", {
          "indexes": ko.mapping.toJSON([{'name': indexName, 'type': self.type()}])
        }, function (data) {
          if (data.status == 0) {
            vm.indexes.remove(function(index) { return index.name() == indexName; });
            huePubSub.publish('assist.collections.refresh');
          } else {
            $(document).trigger("error", data.message);
          }
          $('#deleteIndex').modal('hide');
        }).fail(function (xhr, textStatus, errorThrown) {
          $(document).trigger("error", xhr.responseText);
        });
        hueAnalytics.log('indexes', 'delete_index');
      };
    };

    var Collection = function () {
      var self = this;

      self.id = ko.observable('');
      self.name = ko.observable('');
      self.engine = 'solr';
    }


    var Query = function () {
      var self = this;
      self.qs = ko.observableArray([ ko.mapping.fromJS({q:''}) ]);
      self.fqs = ko.observableArray([]);
    }


    var IndexesViewModel = function (options) {
      var self = this;

      self.baseURL = (IS_HUE_4 ? '/hue' : '') + '/indexer/indexes/';

      self.assistAvailable = ko.observable(true);
      self.apiHelper = ApiHelper.getInstance();
      self.isHue4 = ko.observable(options.hue4);
      self.isLeftPanelVisible = ko.observable();
      self.apiHelper.withTotalStorage('assist', 'assist_panel_visible', self.isLeftPanelVisible, true);

      self.section = ko.observable('list-indexes');
      self.tab = ko.observable('');
      self.tab.subscribe(function(tab){
        if (tab === 'index-sample'){
          var selector = '#index-sample .sample-table';
          % if conf.CUSTOM.BANNER_TOP_HTML.get():
            var bannerTopHeight = 30;
          % else:
            var bannerTopHeight = 0;
          % endif
          if ($(selector).parents('.dataTables_wrapper').length == 0){
            hueUtils.waitForRendered(selector, function(el){ return el.find('td').length > 0 }, function(){
              $(selector).dataTable({
                "bPaginate": false,
                "bLengthChange": false,
                "bInfo": false,
                "bDestroy": true,
                "bFilter": false,
                "bAutoWidth": false,
                "oLanguage": {
                  "sEmptyTable": "${_('No data available')}",
                  "sZeroRecords": "${_('No matching records')}"
                },
                "fnDrawCallback": function (oSettings) {
                  $(selector).parents('.dataTables_wrapper').css('overflow-x', 'hidden');
                  $(selector).jHueTableExtender2({
                    fixedHeader: true,
                    fixedFirstColumn: true,
                    includeNavigator: false,
                    parentId: 'index-sample',
                    classToRemove: 'sample-table',
                    mainScrollable: '${ MAIN_SCROLLABLE }',
                    % if is_embeddable:
                      stickToTopPosition: 51 + bannerTopHeight,
                    % else:
                      stickToTopPosition: 76 + bannerTopHeight,
                    % endif
                    clonedContainerPosition: 'fixed',
                    app: 'indexes'
                  });
                  $(selector).jHueHorizontalScrollbar();
                },
                "aoColumnDefs": [
                  {
                    "sType": "numeric",
                    "aTargets": [ "sort-numeric" ]
                  },
                  {
                    "sType": "string",
                    "aTargets": [ "sort-string" ]
                  },
                  {
                    "sType": "date",
                    "aTargets": [ "sort-date" ]
                  }
                ]
              });
            });
          }
        }
      });

      self.indexes = ko.observableArray([]);
      self.alias = new Alias(self);
      self.index = ko.observable();

      self.indexFilter = ko.observable('');
      self.fieldFilter = ko.observable('');

      self.filteredIndexes = ko.computed(function () {
        var returned = self.indexes();
        if (self.indexFilter() !== '') {
          returned = $.grep(self.indexes(), function (idx) {
            return idx.name().toLowerCase().indexOf(self.indexFilter().toLowerCase()) > -1;
          });
        }
        return returned;
      });

      self.selectedIndexes = ko.computed(function () {
        return $.grep(self.indexes(), function (index) {
          return index.isSelected();
        });
      });
      self.isLoading = ko.observable(false);

      self.oneSelected = ko.computed(function () {
        return self.selectedIndexes().length == 1;
      });
      self.atLeastOneSelected = ko.computed(function () {
        return self.selectedIndexes().length >= 1;
      });
      self.allSelected = ko.observable(false);

      self.handleSelect = function (index) {
        index.isSelected(!index.isSelected());
      }

      self.selectAll = function () {
        self.allSelected(!self.allSelected());
        ko.utils.arrayForEach(self.indexes(), function (index) {
          index.isSelected(self.allSelected());
        });
      }

      self.datatable = null;

      self.showIndexes = function () {
        self.section('list-indexes');
        self.index(null);
        hueUtils.changeURL(self.baseURL);
        self.fetchIndexes();
        $('#fieldAnalysisIndexes').hide();
      }

      self.fetchIndexes = function (callback) {
        self.isLoading(true);
        $.post("${ url('indexer:list_indexes') }", {}, function (data) {
          if (data.status == 0) {
            var indexes = []
            data.collections.forEach(function (index) {
              index.isSelected = false;
              indexes.push(ko.mapping.fromJS(index));
            });
            self.indexes(indexes);
            if (callback) {
              callback();
            }
          } else {
            $(document).trigger("error", data.message);
          }
        }).fail(function (xhr, textStatus, errorThrown) {
          $(document).trigger("error", xhr.responseText);
        }).always(function () {
          self.isLoading(false);
        });
        hueAnalytics.log('indexes', 'list_indexes');
      };

      self.getIndexByName = function (name) {
        var found = null;
        self.indexes().forEach(function (idx) {
          if (idx.name() === name) {
            found = idx;
          }
        });
        return found;
      }

      self.fetchIndex = function (index) {
        $.post("${ url('indexer:list_index') }", {
          name: index.name()
        }, function (data) {
          if (data.status == 0) {
            self.index(new Index(self, data));
            self.index().type(index.type());
            self.index().getSample();
            hueUtils.changeURL(self.baseURL + self.index().name());
            self.collection.name(self.index().name());
            self.section('list-index');
            self.tab('index-overview');
          } else {
            $(document).trigger("error", data.message);
          }
        }).fail(function (xhr, textStatus, errorThrown) {
          $(document).trigger("error", xhr.responseText);
        });
        hueAnalytics.log('indexes', 'list_index');
      };

      self.deleteIndexes = function () {
        $.post("${ url('indexer:delete_indexes') }", {
          "indexes": ko.mapping.toJSON(self.selectedIndexes)
        }, function (data) {
          if (data.status == 0) {
            self.indexes.removeAll(self.selectedIndexes());
            huePubSub.publish('assist.collections.refresh');
          } else {
            $(document).trigger("error", data.message);
          }
          $('#deleteIndexes').modal('hide');
        }).fail(function (xhr, textStatus, errorThrown) {
          $(document).trigger("error", xhr.responseText);
        });
        hueAnalytics.log('indexes', 'delete_indexes');
      };

      self.fieldAnalyses = ko.observableArray([]);
      self.fieldAnalysesName = ko.observable('');
      self.collection = new Collection();
      self.query = new Query();

      self.showFieldAnalysis = function (data, e) {
        if (self.fieldAnalysesName()) {
          var analyse = self.getFieldAnalysis();

          if (analyse == null) {
            analyse = new FieldAnalysis(self, self.fieldAnalysesName(), data.type());
            self.fieldAnalyses.push(analyse);
          }

          analyse.update();
          huePubSub.publish('show.analysis', e);
        }
      }

      self.getFieldAnalysis = function () {
        var fieldName = self.fieldAnalysesName();
        var _analyse = null;

        $.each(self.fieldAnalyses(), function (index, analyse) {
          if (analyse.name() == fieldName) {
            _analyse = analyse;
            return false;
          }
        });

        return _analyse;
      };

    };
    return IndexesViewModel;
  })();


  (function () {
    $(document).ready(function () {
      var options = {
        user: '${ user.username }',
        % if is_embeddable:
          hue4: true,
        % endif
        index: '${ index }'
      };
      var viewModel = new IndexesViewModel(options);
      ko.applyBindings(viewModel, $('#indexesComponents')[0]);

      huePubSub.subscribe('open.index', function (index) {
        var foundIndex = viewModel.getIndexByName(index);
        if (foundIndex) {
          viewModel.fetchIndex(foundIndex);
        }
      }, 'indexes');

      huePubSub.subscribe('show.analysis', function (originalEvent) {
        if (originalEvent.pageX == null && originalEvent.clientX != null) {
          var doc = document.documentElement, body = document.body;
          originalEvent.pageX = originalEvent.clientX + (doc && doc.scrollLeft || body && body.scrollLeft || 0) - (doc && doc.clientLeft || body && body.clientLeft || 0);
          originalEvent.pageY = originalEvent.clientY + (doc && doc.scrollTop || body && body.scrollTop || 0) - (doc && doc.clientTop || body && body.clientTop || 0);
        }
        if ($('#indexesComponents').offset().left > 0) {
          originalEvent.pageX = originalEvent.pageX - $('#indexesComponents').offset().left;
          originalEvent.pageY = originalEvent.pageY - $('#indexesComponents').offset().top;
        }
        else {
          originalEvent.pageX = originalEvent.pageX - $('.content-panel').position().left;
          originalEvent.pageY = originalEvent.pageY + $('.content-panel').scrollTop();
        }
        $("#fieldAnalysisIndexes").show().css({
          top: Math.max(0, originalEvent.pageY + ${ is_embeddable and '48' or '-70'} - $("#fieldAnalysisIndexes").outerHeight() / 2),
          left: originalEvent.pageX
        });
      }, 'indexes');

      viewModel.fetchIndexes(function () {
        if (options.index) {
          var foundIndex = viewModel.getIndexByName(options.index);
          if (foundIndex) {
            viewModel.fetchIndex(foundIndex);
          }
          else {
            $.jHueNotify.error('${ _('The specified index has not been found') }')
            viewModel.showIndexes();
          }
        }
      });
    });
  })();
</script>

%if not is_embeddable:
${ commonfooter(request, messages) | n,unicode }
%endif

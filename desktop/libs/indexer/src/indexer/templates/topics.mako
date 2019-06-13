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
${ commonheader(_("Streams Browser"), "search", user, request, "60px") | n,unicode }
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
<script src="${ static('dashboard/js/search.ko.js') }" type="text/javascript" charset="utf-8"></script>


<script type="text/html" id="indexes-breadcrumbs">
  <h1>
    <!-- ko with: index() -->
    <div class="inline-block pull-right">
      <a class="btn btn-default" href="javascript:void(0)" data-bind="hueLink: '/indexer/importer/prefill/kafka/' + name(), tooltip: { placement: 'bottom', delay: 750 }" title="${_('Inport stream data into a table or file')}">
        <i class="fa fa-download fa-fw"></i> ${_('Consume')}
      </a>

      <a class="btn btn-default" href="javascript:void(0)" data-toggle="modal" data-bind="click: function() { $('#deleteIndex').modal('show') }, tooltip: { placement: 'bottom', delay: 750 }" title="${_('Delete the index')}">
        <i class="fa fa-times fa-fw"></i> ${_('Delete')}
      </a>
    </div>
    <!-- /ko -->
    <ul class="nav nav-pills hue-breadcrumbs-bar">
      <li>
        <a href="javascript:void(0);" data-bind="click: showIndexes">${ _('Topics') }
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
              <a href="/${app_name}">
                ${ _('Kafka Browser') }
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
                <a data-bind="click: function() { $root.alias.name(''); $('#createAlias').modal('show'); }" class="btn">
                  <i class="fa fa-plus-circle"></i> ${ _('Create') }
                </a>
                <a href="javascript:void(0)" class="btn" data-bind="hueLink: '/indexer/importer/prefill/kafka'">
                  <i class="fa fa-cloud-download"></i> ${ _('Consume') }
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
              <h2 class="modal-title">${ _('Create topic') }</h2>
            </div>
            <div class="modal-body">
              <label class="margin-bottom-20">${ _('Name') } <input type="text" data-bind="textInput: alias.name" class="input-xlarge no-margin-bottom margin-left-10"></label>
            </div>
            <div class="modal-footer">
              <a href="javascript: void(0)" class="btn" data-dismiss="modal">${ _('Cancel') }</a>
              <button class="btn btn-primary disable-feedback" data-bind="click: alias.create, enable: alias.name() !== ''">
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
      </tr>
    </thead>
    <tbody data-bind="foreach: { data: filteredIndexes }">
      <tr>
        <td data-bind="click: $root.handleSelect" class="center" style="cursor: default">
          <div data-bind="multiCheck: '#list-indexes-table', css: { 'hue-checkbox': true, 'fa': true, 'fa-check': isSelected}"></div>
        </td>
        <td><a class="pointer" data-bind="text: name, click: function() { $root.fetchIndex($data); }"></a></td>
      </tr>
    </tbody>
  </table>
</script>


<script type="text/html" id="list-index">
  <br/>
  <br/>

  <ul class="nav nav-tabs nav-tabs-border">
    <li class="active"><a href="#index-overview" data-toggle="tab" data-bind="click: function(){ $root.tab('index-overview'); }">${_('Overview')}</a></li>
    <li><a href="#index-columns" data-toggle="tab" data-bind="click: function(){ $root.tab('index-columns'); }">${_('Partitions')} (<span data-bind="text: fields().length"></span>)</a></li>
    <li>
      <a href="#index-consumer" data-toggle="tab" data-bind="click: function(){ $root.tab('index-consumer'); }">${_('Consumers')} (0)</a>
    </li>
    <li>
      <a href="#index-sample" data-toggle="tab" data-bind="click: function(){ $root.tab('index-sample'); }">${_('Permissions')} (2)</a>
    </li>
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
      <div class="acl-panel-content" style="height: 988px;">
        <div class="acl-block-title">
          <i class="fa fa-cube muted"></i> <a class="pointer"><span>finance</span></a>
        </div>
        <div>
          <div class="acl-block acl-block-airy">
            <span class="muted" title="3 months ago">TOPIC</span>
            <span>
              <a class="muted" style="margin-left: 4px" title="Open in Sentry" href="/security/hive"><i class="fa fa-external-link"></i></a>
            </span>
            <br>
            server=<span>server1</span>
            <i class="fa fa-long-arrow-right"></i> action=READ
          </div>

          <div class="acl-block acl-block-airy">
            <span class="muted" title="3 months ago">TOPIC</span>
            <span>
              <a class="muted" style="margin-left: 4px" title="Open in Sentry" href="/security/hive"><i class="fa fa-external-link"></i></a>
            </span>
            <br>
            server=server1
            <i class="fa fa-long-arrow-right"></i> action=<span>WRITE</span>
          </div>
        </div>
      </div>
    </div>

    <div class="tab-pane margin-top-10" id="index-consumer">
      <div class="row-fluid">
        <div>
          <label class="control-label"><div>${ _('Consumer 1') }</div>
            Type
          </label>
          <label class="control-label"><div>${ _('Consumer 2') }</div>
            Type
          </label>
        </div>
      </div>
    </div>

  </div>
</script>


<script type="text/html" id="indexes-index-overview">
  <div>
    <!-- ko template: 'indexes-index-properties' --><!-- /ko -->

    <h4>${ _('Partitions') } (<span data-bind="text: fields().length"></span>)</h4>
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
  <h4>${ _('Schema') }</h4>
  <div class="row-fluid">
    <div>
      <label class="control-label"><div>${ _('Type') }</div>
        <select class="input-medium" data-bind="options: ['delimited', 'bitarray'], value: 'delimited'"></select>
      </label>
      <label class="control-label"><div>${ _('Field names') }</div>
        <input type="text" class="input-xxlarge" data-bind="value: kafkaFieldNames" placeholder="${ _('The list of fields to consume, e.g. orders,returns') }">
      </label>
      <label class="control-label"><div>${ _('Field types') }</div>
        <input type="text" class="input-xxlarge" data-bind="value: kafkaFieldTypes" placeholder="${ _('The list of field typs, e.g. string,int') }">
      </label>
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
        </tr>
      </thead>
      <tbody data-bind="foreach: $data">
        <tr>
          <td data-bind="text: $index() + 1"></td>
          <td>
            <i class="fa fa-info muted pointer analysis"></i>
          </td>
          <td data-bind="text: ko.mapping.toJSON($data)"></td>
        </tr>
      </tbody>
    </table>
  </div>
</script>


<script type="text/html" id="indexes-index-fields">
  <div>
    <!-- ko template: { name: 'indexes-index-fields-fields', data: filteredFields }--><!-- /ko -->
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



<script type="text/javascript">

  var IndexesViewModel = (function () {

    var Alias = function (vm) {
      var self = this;

      self.name = ko.observable('');
      self.chosenCollections = ko.observableArray();
      self.availableCollections = ko.computed(function () {
        return vm.indexes();
      });

      self.create = function () {
        $.post("${ url('kafka:create_topic') }", {
          "name": self.name
        }, function (data) {
          if (data.status == 0) {
            vm.indexes.push(ko.mapping.fromJS(data.topic));
            huePubSub.publish('assist.collections.refresh');
          } else {
            $(document).trigger("error", data.message);
          }
          $('#createAlias').modal('hide');
        }).fail(function (xhr, textStatus, errorThrown) {
          $(document).trigger("error", xhr.responseText);
        });
        hueAnalytics.log('kafka', 'create_topic');
      }
    };


    var Index = function (vm, index) {
      var self = this;

      self.name = ko.observable(index.name);
      self.type = ko.observable(index.type);
      self.fields = ko.mapping.fromJS(index.partitions);
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

      // Should come from Kafka Schema or ZooKeeper
      var userPrefix = 'pai';
      self.kafkaFieldNames = ko.observable($.totalStorage(userPrefix + '_kafka_topics_' + self.name() + '_kafkaFieldNames'));
      self.kafkaFieldNames.subscribe(function(newValue) {
        $.totalStorage(userPrefix + '_kafka_topics_' + self.name() + '_kafkaFieldNames', newValue);
      });
      self.kafkaFieldTypes = ko.observable($.totalStorage(userPrefix + '_kafka_topics_' + self.name() + '_kafkaFieldTypes'));
      self.kafkaFieldTypes.subscribe(function(newValue) {
        $.totalStorage(userPrefix + '_kafka_topics_' + self.name() + '_kafkaFieldTypes', newValue)
      });

      self.sample = ko.observableArray();
      self.samplePreview = ko.pureComputed(function () {
        return self.sample().slice(0, 5)
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
            vm.showIndexes(false);
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

    var IndexesViewModel = function (options) {
      var self = this;

      self.baseURL = '/hue/indexer/topics/';

      self.activeNamespace = ko.observable();
      self.activeCompute = ko.observable();

      contextCatalog.getNamespaces({ sourceType: 'solr' }).done(function (context) {
        // TODO: Namespace selection
        self.activeNamespace(context.namespaces[0]);
        self.activeCompute(context.namespaces[0].computes[0]);
      });

      self.assistAvailable = ko.observable(true);
      self.apiHelper = window.apiHelper;
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
                    lockSelectedRow: false,
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

      self.showIndexes = function (reload) {
        self.section('list-indexes');
        self.index(null);
        hueUtils.changeURL(self.baseURL);
        if (typeof reload == 'undefined' || reload) {
          self.fetchIndexes();
        }
      }

      self.fetchIndexes = function (callback) {
        self.isLoading(true);
        $.post("${ url('kafka:list_topics') }", {}, function (data) {
          if (data.status == 0) {
            var indexes = []
            data.topics.forEach(function (index) {
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
        hueAnalytics.log('kafka', 'list_topics');
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
        $.post("${ url('kafka:list_topic') }", {
          name: index.name()
        }, function (data) {
          if (data.status == 0) {
            self.index(new Index(self, data.topic));
            //self.index().getSample();
            hueUtils.changeURL(self.baseURL + self.index().name());
            self.section('list-index');
            self.tab('index-overview');
          } else {
            $(document).trigger("error", data.message);
          }
        }).fail(function (xhr, textStatus, errorThrown) {
          $(document).trigger("error", xhr.responseText);
        });
        hueAnalytics.log('kafka', 'list_topic');
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

      self.showContextPopover = function (field, event) {
        var $source = $(event.target);
        var offset = $source.offset();

        huePubSub.publish('context.popover.show', {
          data: {
            type: 'collection',
            namespace: self.activeNamespace(),
            compute: self.activeCompute(),
            identifierChain: [
              {}, // empty, needed by the context popover
              ko.mapping.toJS(self.index),
              ko.mapping.toJS(field)
            ]
          },
          showInAssistEnabled: true,
          orientation: 'right',
          pinEnabled: false,
          source: {
            element: event.target,
            left: offset.left,
            top: offset.top - 3,
            right: offset.left + $source.width() + 1,
            bottom: offset.top + $source.height() - 3
          }
        });
      };

    };
    return IndexesViewModel;
  })();


  (function () {
    $(document).ready(function () {
      var options = {
        user: '${ user.username }',
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

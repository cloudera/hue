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
  from desktop.views import commonheader, commonfooter, commonshare2, _ko
  from django.utils.translation import ugettext as _
%>

${ commonheader(_('Welcome Home'), "home", user) | n,unicode }

<style type="text/css">
  .sidebar-nav {
    margin-bottom: 10px;
  }

  .sidebar-nav img {
    margin-right: 6px;
  }

  .sidebar-nav .dropdown-menu a {
    padding-left: 6px;
  }

  .tag {
    float: left;
    margin-right: 6px;
    margin-bottom: 4px;
  }

  .tag-counter {
    margin-top: 3px;
    margin-right: 4px;
  }

  .toggle-tag, .document-tags-modal-checkbox, .tags-modal-checkbox {
    cursor: pointer;
  }

  .badge-left {
    border-radius: 9px 0px 0px 9px;
    padding-right: 5px;
    font-weight: normal;
  }

  .badge-right {
    border-radius: 0px 9px 9px 0px;
    padding-left: 5px;
  }

  .badge-right:hover {
    background-color: #b94a48;
  }

  .airy li {
    margin-bottom: 6px;
  }

  .white {
    padding: 9px 18px;
    margin-top: 1px;
    overflow: hidden;
    font-size: 14px;
    line-height: 1.4;
    color: #737373;
    text-overflow: ellipsis;
  }


</style>

<div class="navbar navbar-inverse navbar-fixed-top nokids">
  <div class="navbar-inner">
    <div class="container-fluid">
      <div class="nav-collapse">
        <ul class="nav">
          <li class="currentApp">
            <a href="${ url('desktop.views.home') }">
              <img src="${ static('desktop/art/home.png') }" class="app-icon" />
              ${ _('My documents') }
            </a>
           </li>
        </ul>
      </div>
    </div>
  </div>
</div>

<div id='documentList' class="container-fluid">
  <div class="row-fluid">
    <div class="span2">
      <div class="sidebar-nav">
         <ul class="nav nav-list">
          <li class="nav-header">${_('Actions')}</li>
           <li class="dropdown">
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
           </li>
        </ul>
      </div>

    </div>

    <div class="span10">
      <div class="card card-home" style="margin-top: 0">
        <input id="searchInput" type="text" placeholder="${ _('Search for name, description, etc...') }" class="input-xlarge search-query" style="margin-left: 20px;margin-top: 5px">
        <h2 class="card-heading simple">${_('My Documents')}</h2>
        <span data-bind="text: path"></span>
        <br/>
        <input data-bind="value: mkdirFormPath" placeholder="dir name, e.g. projects"></input>
        <a href="javascript:void(0);" class="btn" data-bind="click: mkdir"><i class="fa fa-plus-circle"></i> ${ _('Create Directory') }</a>

        <input data-bind="value: deleteFormPath" placeholder="doc id, e.g. 50491"></input>
        <a href="javascript:void(0);" class="btn" data-bind="click: deleteDocument"><i class="fa fa-times"></i> ${ _('Delete') }</a>

        <input data-bind="value: shareFormDocId" placeholder="doc id, e.g. 50491"></input>
        <a class="share-link btn" rel="tooltip" data-placement="bottom" style="margin-left:20px" data-bind="click: function(e){ prepareShareModal(e) },
          attr: {'data-original-title': '${ _ko("Share") } ' + name}">
          <i class="fa fa-users"></i> ${ _('Share') }
        </a>

        <div class="card-body">
          <p>
          <table id="documents" class="table table-striped table-condensed" data-bind="visible: documents().length > 0">
            <thead>
              <tr>
                <th style="width: 26px">&nbsp;</th>
                <th style="width: 200px">${_('Name')}</th>
                <th>${_('Description')}</th>
                <th style="width: 150px">${_('Last Modified')}</th>
                <th style="width: 80px; text-align: center">${_('Project')}</th>
                <th style="width: 40px">${_('Sharing')}</th>
              </tr>
            </thead>
            <tbody data-bind="template: { name: 'document-template', foreach: renderableDocuments}">
            </tbody>
            <tfoot data-bind="visible: documents().length > 0">
              <tr>
                <td colspan="7">
                  <div class="pull-right" style="margin-top: 10px" data-bind="visible: hasPrevious() || hasNext()">
                    <span>${_('Page')} <input type="number" class="input-mini" style="text-align: center" data-bind="value: page"> ${_('of')} <span data-bind="text: totalPages"></span></span>
                  </div>
                  <div class="pagination">
                    <ul>
                      <li><a data-bind="click: previousPage, visible: hasPrevious">${_('Previous')}</a></li>
                      <li><a data-bind="click: nextPage, visible: hasNext">${_('Next')}</a></li>
                    </ul>
                  </div>
                </td>
              </tr>
            </tfoot>
          </table>
          <div data-bind="visible: documents().length == 0">
            <h4 style="color: #777; margin-bottom: 30px">${_('There are currently no documents in this project or tag.')}</h4>
          </div>
          </p>
        </div>
      </div>
    </div>

  </div>
</div>


<script type="text/html" id="document-template">
  <tr>
    <td style="width: 26px"></td>
    <td><a data-bind="attr: { href: absoluteUrl }, html: name"></a></td>
    <td data-bind="text: ko.mapping.toJSON($data)"></td>
    <td></td>
    <td style="text-align: center; white-space: nowrap">
    </td>
    <td style="width: 40px; text-align: center">    
    </td>
  </tr>
</script>


${ commonshare2() | n,unicode }


<script src="${ static('desktop/ext/js/datatables-paging-0.1.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/knockout.min.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/knockout-mapping.min.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/js/home2.vm.js') }"></script>
<script src="${ static('desktop/js/share2.vm.js') }"></script>


<script type="text/javascript" charset="utf-8">
  var viewModel, shareViewModel;

  $(document).ready(function() {
    viewModel = new HomeViewModel();
    ko.applyBindings(viewModel, $('#documentList')[0]);

    shareViewModel = initSharing("#documentShareModal");
    shareViewModel.setDocId(-1);

    viewModel.loadDocuments(location.getParameter('path') ? location.getParameter('path') : '/');
    
    prepareShareModal = function(job) {
      shareViewModel.setDocId(viewModel.shareFormDocId());
      openShareModal();
    };
  });
</script>


<style type="text/css">
  .tourSteps {
    min-height: 150px;
  }
</style>


##
## Add a Tour?
##

${ commonfooter(request, messages) | n,unicode }

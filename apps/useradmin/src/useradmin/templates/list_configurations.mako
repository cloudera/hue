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
from django.contrib.auth.models import Group

from desktop.views import commonheader, commonfooter
from desktop.views import _ko

from useradmin.models import group_permissions

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _
%>

<%namespace name="actionbar" file="actionbar.mako" />
<%namespace name="configKoComponents" file="/config_ko_components.mako" />
<%namespace name="layout" file="layout.mako" />

% if not is_embeddable:
  ${ commonheader(_('Configurations'), "useradmin", user, request) | n,unicode }
% endif

${layout.menubar(section='configurations')}

<script id="app-list" type="text/html">
  <div class="card card-small">
    <h1 class="card-heading simple">${ _('Configurations') }</h1>

    <table class="table table-condensed datatables margin-top-20">
      <thead>
      <tr>
        <th>${ _('Application') }</th>
        <th>${ _('Groups') }</th>
      </tr>
      </thead>
      <tbody data-bind="foreach: filteredApps">
      <tr class="tableRow pointer" data-bind="click: function () { $parent.edit($data); }">
        <td data-bind="text: name"></td>
        <!-- ko if: $data.groups -->
        <td data-bind="text: overriddenGroupNames"></td>
        <!-- /ko -->
        <!-- ko ifnot: $data.groups -->
        <td>&nbsp;</td>
        <!-- /ko -->
      </tr>
      </tbody>
      <tfoot class="hide">
      <tr>
        <td colspan="3">
          <div class="alert">
            ${_('There are no configurations matching the search criteria.')}
          </div>
        </td>
      </tr>
      </tfoot>
    </table>
  </div>
</script>

<script id="edit-app" type="text/html">
  <!-- ko with: selectedApp -->
  <div class="card card-small" style="padding-bottom: 68px;">
    <h1 class="card-heading simple"><!-- ko text: name --><!-- /ko --> ${ _('configuration') }</h1>

    <!-- ko foreach: groups -->
    <h4 class="margin-left-20" style="display: inline-block;">${ _('Role') }</h4>
    <div class="config-actions">
      <a class="inactive-action pointer margin-left-10" title="${ _('Remove') }" rel="tooltip" data-bind="click: function() { $parent.groups.remove($data) }"><i class="fa fa-times"></i> ${ _('Remove') }</a>
    </div>
    <div class="form-horizontal margin-top-20">
      <div class="control-group">
        <label class="control-label">${ _('Groups') }</label>
        <div class="controls">
          <!-- ko component: { name: 'multi-group-selector',
            params: {
              width: 500,
              height: 198,
              options: allGroups,
              optionsValue: 'id',
              optionsText: 'name',
              selectedOptions: group_ids,
            }
          } --><!-- /ko -->
        </div>
      </div>
      <div class="control-group">
        <label class="control-label">${ _('Properties') }</label>
        <div class="controls">
          <!-- ko component: { name: 'property-selector', params: { properties: properties } } --><!-- /ko -->
        </div>
      </div>
    </div>
    <!-- /ko -->
    <div class="margin-left-20 margin-top-20">
      <a class="inactive-action pointer" href="javascript:void(0)" data-bind="click: addGroupOverride">
        <i class="fa fa-plus"></i> ${ _('Add role') }
      </a>
    </div>
  </div>
  <!-- /ko -->
  <div class="form-actions">
    <button class="btn btn-primary" data-bind="click: save">${ _('Update configuration') }</button>
    <button class="btn" data-bind="click: function () { selectedApp(null) }">${ _('Cancel') }</button>
  </div>
</script>

<div id="configurationsComponents" class="container-fluid">
  <!-- ko hueSpinner: { spin: loading, center: true, size: 'large' } --><!-- /ko -->
  <h4 style="width: 100%; text-align: center; display: none;" data-bind="visible: !loading() && hasErrors()">${ _('There was an error loading the configurations') }</h4>
  <!-- ko template: { if: !loading() && !hasErrors() && !selectedApp(), name: 'app-list' } --><!-- /ko -->
  <!-- ko template: { if: !loading() && !hasErrors() && selectedApp(), name: 'edit-app' } --><!-- /ko -->
</div>

%if not is_embeddable:
${ configKoComponents.config() }
%endif
<script src="${ static('desktop/js/list_configurations-inline.js') }" type="text/javascript"></script>

${ layout.commons() }

% if not is_embeddable:
  ${ commonfooter(request, messages) | n,unicode }
% endif

// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import * as ko from 'knockout';

import I18n from 'utils/i18n';

const TEMPLATE_NAME = 'context-partition-details';

// prettier-ignore
export const PARTITION_CONTEXT_TEMPLATE = `
<script type="text/html" id="${ TEMPLATE_NAME }">
  <div class="context-popover-flex-fill" style="overflow: auto;">
    <div class="context-popover-inner-content">
      <div style="position: absolute; right: 6px; top: 8px;">
        <a class="pointer inactive-action" data-bind="visible: !$parent.closeDisabled, click: function () { $parent.close() }"><i class="fa fa-fw fa-times"></i></a>
      </div>
      <!-- ko with: data -->
      <div class="context-popover-flex-header blue"><span data-bind="text: originalName"></span></div>
      <div class="context-popover-flex-attributes">
        <div class="context-popover-attribute"><div>${ I18n('Created') }</div><div data-bind="text: created"></div></div>
      </div>
      <!-- ko if: description -->
      <div class="context-popover-doc-description" data-bind="text: description"></div>
      <!-- /ko -->
      <div class="context-popover-flex-fill">
        <table id="partitionsTable" class="table table-condensed table-nowrap">
          <thead>
          <tr>
            <th>${ I18n('Values') }</th>
          </tr>
          </thead>
          <tbody data-bind="foreach: colValues">
            <tr>
              <td data-bind="text: $data"></td>
            </tr>
          </tbody>
        </table>
      </div>
      <!-- /ko -->
    </div>
  </div>
</script>
`;

class PartitionContext {
  constructor(data) {
    const self = this;
    self.disposals = [];

    self.data = data;
    self.loading = ko.observable(false);
    self.hasErrors = ko.observable(false);
    self.errorText = ko.observable();
    self.template = TEMPLATE_NAME;
  }

  dispose() {
    const self = this;
    while (self.disposals.length) {
      self.disposals.pop()();
    }
  }
}

export default PartitionContext;

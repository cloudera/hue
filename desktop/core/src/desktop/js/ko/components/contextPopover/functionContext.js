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
import { SqlFunctions } from 'sql/sqlFunctions';

const TEMPLATE_NAME = 'context-popover-function-details';

// prettier-ignore
export const FUNCTION_CONTEXT_TEMPLATE = `
<script type="text/html" id="context-popover-function-details">
  <!-- ko if: typeof details === 'undefined' -->
  <div class="context-popover-flex-fill">
    <div class="alert">${ I18n('Could not find details for the function') } <span data-bind="text: $parents[2].title"></span>()</div>
  </div>
  <!-- /ko -->
  <!-- ko if: typeof details !== 'undefined' -->
  <div class="context-popover-flex-fill" data-bind="with: details">
    <div style="padding: 8px">
      <p style="margin: 10px 10px 18px 10px;"><span style="white-space: pre;" class="monospace" data-bind="text: signature"></span></p>
      <p><span data-bind="text: description"></span></p>
    </div>
  </div>
  <!-- /ko -->
</script>
`;

class FunctionContextTabs {
  constructor(data, sourceType) {
    const self = this;
    self.func = ko.observable({
      details: SqlFunctions.findFunction(sourceType, data.function),
      loading: ko.observable(false),
      hasErrors: ko.observable(false)
    });

    self.tabs = [
      {
        id: 'details',
        label: I18n('Details'),
        template: TEMPLATE_NAME,
        templateData: self.func
      }
    ];
    self.activeTab = ko.observable('details');
  }
}

export default FunctionContextTabs;

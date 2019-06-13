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

import ko from 'knockout';

import I18n from 'utils/i18n';
import { SqlFunctions } from 'sql/sqlFunctions';

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
        template: 'context-popover-function-details',
        templateData: self.func
      }
    ];
    self.activeTab = ko.observable('details');
  }
}

export default FunctionContextTabs;

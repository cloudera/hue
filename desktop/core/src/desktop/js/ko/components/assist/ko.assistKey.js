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

import componentUtils from 'ko/components/componentUtils';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';
import { ASSIST_DB_HIGHLIGHT_EVENT } from './events';

import 'ko/bindings/ko.tooltip';

export const ASSIST_KEY_COMPONENT = 'hue-assist-key';

const TEMPLATE = `
  <!-- ko if: entry.isForeignKey() -->
    <!-- ko if: entry.definition.foreignKey.to -->
      <a class="assist-field-link" style="padding: 0 2px;" href="javascript: void(0);" data-bind="
          tooltip: {
            title: foreignKeyTooltipHtml,
            html: true,
            placement: 'bottom'
          },
          click: foreignKeyClick,
          clickbubble: false
        "><i class="fa fa-key"></i></a>
    <!-- /ko -->
    <!-- ko ifnot: entry.definition.foreignKey.to -->
      <i class="fa fa-key" style="padding: 0 2px;" data-bind="
          tooltip: {
            title: '${I18n('Foreign Key')}',
            placement: 'bottom'
          }
        "></i>
    <!-- /ko -->
  <!-- /ko -->
  <!-- ko if: entry.isPrimaryKey() || entry.isPartitionKey() -->
    <i class="fa fa-key" style="padding: 0 2px;" data-bind="
        tooltip: {
          title: entry.isPrimaryKey() ? '${I18n('Primary Key')}' : '${I18n('Partition Key')}',
          placement: 'bottom'
        }
      "></i>
  <!-- /ko -->
  <!-- ko ifnot: entry.isForeignKey() || entry.isPrimaryKey() || entry.isPartitionKey() -->
    <i class="fa fa-key"></i>
  <!-- /ko -->
`;

class AssistKey {
  constructor(params) {
    this.entry = ko.unwrap(params.entry);
    this.onForeignKeyClick = params.onForeignKeyClick;

    this.foreignKeyTooltipHtml = ko.pureComputed(
      () => `<i style="margin-right: 4px" class="fa fa-arrow-right"></i>
    ${this.entry.definition.foreignKey && this.entry.definition.foreignKey.to}`
    );
  }

  foreignKeyClick() {
    this.entry.dataCatalog
      .getEntry({
        path: this.entry.definition.foreignKey.to,
        namespace: this.entry.namespace,
        compute: this.entry.compute
      })
      .then(entry => {
        if (this.onForeignKeyClick) {
          // Ensure definition is loaded
          if (!entry.definition) {
            entry
              .getParent()
              .then(parentEntry => {
                parentEntry.getChildren().then(() => {
                  this.onForeignKeyClick(entry);
                });
              })
              .catch(() => {});
          } else {
            this.onForeignKeyClick(entry);
          }
        } else {
          huePubSub.publish(ASSIST_DB_HIGHLIGHT_EVENT, entry);
        }
      });
  }
}

componentUtils.registerComponent(ASSIST_KEY_COMPONENT, AssistKey, TEMPLATE);

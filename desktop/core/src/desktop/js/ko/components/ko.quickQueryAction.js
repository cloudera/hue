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

import $ from 'jquery';

import componentUtils from 'ko/components/componentUtils';
import DisposableComponent from 'ko/components/DisposableComponent';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';

export const NAME = 'quick-query-action';

// prettier-ignore
const TEMPLATE = `
<div style="display: inline-block; margin-left: 20px; margin-top: 5px;">
  <button class="btn btn-mini disable-feedback" data-bind="click: showQuickQuery">
    <i class="fa fa-play fa-fw"></i> ${ I18n('Quick Query') }
  </button>
</div>
`;

class QuickQueryAction extends DisposableComponent {
  showQuickQuery(data, event) {
    const $source = $(event.target);
    const offset = $source.offset();
    huePubSub.publish('context.popover.show', {
      data: {
        type: 'quickQuery'
      },
      orientation: 'bottom',
      pinEnabled: false,
      source: {
        left: offset.left,
        top: offset.top,
        right: offset.left + $source.outerWidth(),
        bottom: offset.top + $source.outerHeight()
      }
    });
  }
}

componentUtils.registerComponent(NAME, QuickQueryAction, TEMPLATE);

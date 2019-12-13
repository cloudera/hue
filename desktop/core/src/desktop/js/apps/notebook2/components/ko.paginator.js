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

import componentUtils from 'ko/components/componentUtils';
import DisposableComponent from 'ko/components/DisposableComponent';
import I18n from 'utils/i18n';

export const NAME = 'paginator';

// prettier-ignore
const TEMPLATE = `
<div class="pagination" data-bind="visible: totalPages() > 1" style="display: none;">
  <ul>
    <li data-bind="css: { 'disabled' : currentPage() === 1 }">
      <a href="javascript: void(0);" data-bind="click: previousPage.bind($data)">${ I18n("Prev") }</a>
    </li>
    <li class="active"><span data-bind="text: currentPage() + '/' + totalPages()"></span></li>
    <li data-bind="css: { 'disabled' : currentPage() === totalPages() }">
      <a href="javascript: void(0);" data-bind="click: nextPage.bind($data)">${ I18n("Next") }</a>
    </li>
  </ul>
</div>
`;

class Paginator extends DisposableComponent {
  constructor(params, element) {
    super();
    this.totalPages = params.totalPages;
    this.currentPage = params.currentPage;
    this.onPageChange = params.onPageChange;

    if (this.onPageChange) {
      this.subscribe(this.currentPage, this.onPageChange);
    }
  }

  nextPage() {
    if (this.currentPage() < this.totalPages()) {
      this.currentPage(this.currentPage() + 1);
    }
  }

  previousPage() {
    if (this.currentPage() !== 1) {
      this.currentPage(this.currentPage() - 1);
    }
  }
}

componentUtils.registerComponent(NAME, Paginator, TEMPLATE);

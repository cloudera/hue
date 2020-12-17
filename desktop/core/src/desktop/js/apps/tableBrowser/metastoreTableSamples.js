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

class MetastoreTableSamples {
  /**
   * @param {Object} options
   * @param {MetastoreTable} options.metastoreTable
   */
  constructor(options) {
    this.rows = ko.observableArray();
    this.headers = ko.observableArray();
    this.metastoreTable = options.metastoreTable;

    this.hasErrors = ko.observable(false);
    this.errorMessage = ko.observable();
    this.loaded = ko.observable(false);
    this.loading = ko.observable(false);

    this.preview = {
      headers: ko.observableArray(),
      rows: ko.observableArray()
    };
  }

  load() {
    if (this.loaded()) {
      return;
    }
    this.hasErrors(false);
    this.loading(true);
    this.metastoreTable.catalogEntry
      .getSample()
      .then(sample => {
        this.rows(sample.data);
        this.headers(sample.meta.map(meta => meta.name));
        this.preview.rows(this.rows().slice(0, 3));
        this.preview.headers(this.headers());
      })
      .catch(message => {
        this.errorMessage(message);
        this.hasErrors(true);
      })
      .finally(() => {
        this.loading(false);
        this.loaded(true);
      });
  }
}

export default MetastoreTableSamples;

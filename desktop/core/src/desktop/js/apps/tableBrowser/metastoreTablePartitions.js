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
import * as ko from 'knockout';
import komapping from 'knockout.mapping';

import huePubSub from 'utils/huePubSub';

class MetastoreTablePartitions {
  /**
   * @param {Object} options
   * @param {MetastoreTable} options.metastoreTable
   */
  constructor(options) {
    this.detailedKeys = ko.observableArray();
    this.keys = ko.observableArray();
    this.values = ko.observableArray();
    this.selectedValues = ko.observableArray();

    this.valuesFlat = ko.pureComputed(() => this.values().map(item => item.partitionSpec));

    this.selectedValuesFlat = ko.pureComputed(() =>
      this.selectedValues().map(item => item.partitionSpec)
    );

    this.metastoreTable = options.metastoreTable;

    this.loaded = ko.observable(false);
    this.loading = ko.observable(false);

    this.sortDesc = ko.observable(true);
    this.filters = ko.observableArray([]);

    this.typeaheadValues = column => {
      const values = [];
      this.values().forEach(row => {
        const cell = row.columns[this.keys().indexOf(column())];
        if (values.indexOf(cell) !== -1) {
          values.push(cell);
        }
      });
      return values;
    };

    this.addFilter = () => {
      this.filters.push(komapping.fromJS({ column: '', value: '' }));
    };

    this.removeFilter = data => {
      this.filters.remove(data);
      if (this.filters().length === 0) {
        this.sortDesc(true);
        this.filter();
      }
    };

    this.filter = () => {
      this.loading(true);
      this.loaded(false);
      const filters = JSON.parse(ko.toJSON(this.filters));
      const postData = {};
      filters.forEach(filter => {
        postData[filter.column] = filter.value;
      });
      postData['sort'] = this.sortDesc() ? 'desc' : 'asc';

      $.ajax({
        type: 'POST',
        url: '/metastore/table/' + this.metastoreTable.catalogEntry.path.join('/') + '/partitions',
        data: postData,
        dataType: 'json'
      }).done(data => {
        this.values(data.partition_values_json);
        this.loading(false);
        this.loaded(true);
      });
    };

    this.preview = {
      keys: ko.observableArray(),
      values: ko.observableArray()
    };
  }

  load() {
    if (this.loaded()) {
      return;
    }

    this.loading(true);

    this.metastoreTable.catalogEntry
      .getPartitions()
      .then(partitions => {
        this.keys(partitions.partition_keys_json);
        this.values(partitions.partition_values_json);
        this.preview.values(this.values().slice(0, 5));
        this.preview.keys(this.keys());
        huePubSub.publish('metastore.loaded.partitions');
      })
      .finally(() => {
        this.loading(false);
        this.loaded(true);
      });
  }
}

export default MetastoreTablePartitions;

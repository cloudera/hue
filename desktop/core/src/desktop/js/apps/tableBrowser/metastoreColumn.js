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

import huePubSub from 'utils/huePubSub';

class MetastoreColumn {
  /**
   * @param {Object} options
   * @param {MetastoreTable} options.table
   * @param {DataCatalogEntry} options.catalogEntry
   * @constructor
   */
  constructor(options) {
    this.table = options.table;
    this.catalogEntry = options.catalogEntry;

    this.favourite = ko.observable(false);
    this.popularity = ko.observable();
    this.comment = ko.observable();

    this.comment.subscribe(newValue => {
      this.catalogEntry.getComment().then(comment => {
        if (comment !== newValue) {
          this.catalogEntry
            .setComment(newValue)
            .then(this.comment)
            .catch(() => {
              this.comment(comment);
            });
        }
      });
    });

    this.table.catalogEntry.loadNavigatorMetaForChildren().finally(() => {
      this.catalogEntry.getComment().then(this.comment);
    });
  }

  showContextPopover(entry, event) {
    const $source = $(event.target);
    const offset = $source.offset();
    huePubSub.publish('context.popover.show', {
      data: {
        type: 'catalogEntry',
        catalogEntry: entry.catalogEntry
      },
      orientation: 'right',
      source: {
        element: event.target,
        left: offset.left,
        top: offset.top - 2,
        right: offset.left + $source.width() + 1,
        bottom: offset.top + $source.height() - 2
      }
    });
  }
}

export default MetastoreColumn;

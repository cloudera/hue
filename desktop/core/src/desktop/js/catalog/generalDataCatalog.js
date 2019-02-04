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

import $ from 'jquery'
import localforage from 'localforage'

import apiHelper from '../api/apiHelper'

const STORAGE_POSTFIX = LOGGED_USERNAME;
const DATA_CATALOG_VERSION = 5;

class GeneralDataCatalog {

  constructor() {
    let self = this;
    self.store = localforage.createInstance({
      name: 'HueDataCatalog_' + STORAGE_POSTFIX
    });

    self.allNavigatorTagsPromise = undefined;
  }

  /**
   * @param {Object} [options]
   * @param {boolean} [options.silenceErrors]
   * @param {boolean} [options.refreshCache]
   *
   * @return {Promise}
   */
  getAllNavigatorTags(options) {
    let self = this;
    if (self.allNavigatorTagsPromise && (!options || !options.refreshCache)) {
      return self.allNavigatorTagsPromise;
    }

    let deferred = $.Deferred();

    if (!window.HAS_NAVIGATOR) {
      return deferred.reject().promise();
    }

    self.allNavigatorTagsPromise = deferred.promise();

    let reloadAllTags = () => {
      apiHelper.fetchAllNavigatorTags({
        silenceErrors: options && options.silenceErrors,
      }).done(deferred.resolve).fail(deferred.reject);

      if (window.CACHEABLE_TTL.default > 0) {
        deferred.done(function (allTags) {
          self.store.setItem('hue.dataCatalog.allNavTags', { allTags: allTags, hueTimestamp: Date.now(), version: DATA_CATALOG_VERSION });
        })
      }
    };

    if (window.CACHEABLE_TTL.default > 0 && (!options || !options.refreshCache)) {
      self.store.getItem('hue.dataCatalog.allNavTags').then(function (storeEntry) {
        if (storeEntry && storeEntry.version === DATA_CATALOG_VERSION && (!storeEntry.hueTimestamp || (Date.now() - storeEntry.hueTimestamp) < CACHEABLE_TTL.default)) {
          deferred.resolve(storeEntry.allTags);
        } else {
          reloadAllTags();
        }
      }).catch(reloadAllTags);
    } else {
      reloadAllTags();
    }

    return self.allNavigatorTagsPromise;
  };

  /**
   * @param {string[]} tagsToAdd
   * @param {string[]} tagsToRemove
   */
  updateAllNavigatorTags(tagsToAdd, tagsToRemove) {
    let self = this;
    if (self.allNavigatorTagsPromise) {
      self.allNavigatorTagsPromise.done(function (allTags) {
        tagsToAdd.forEach(function (newTag) {
          if (!allTags[newTag]) {
            allTags[newTag] = 0;
          }
          allTags[newTag]++;
        });
        tagsToRemove.forEach(function (removedTag) {
          if (!allTags[removedTag]) {
            allTags[removedTag]--;
            if (allTags[removedTag] === 0) {
              delete allTags[removedTag];
            }
          }
        });
        self.store.setItem('hue.dataCatalog.allNavTags', { allTags: allTags, hueTimestamp: Date.now(), version: DATA_CATALOG_VERSION });
      });
    }
  };
}

export default GeneralDataCatalog
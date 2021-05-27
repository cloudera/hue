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

import localforage from 'localforage';

import { hueWindow } from 'types/types';
import { fetchAllNavigatorTags } from './api';
import { DataCatalog } from './dataCatalog';

export interface Tags {
  [tag: string]: number;
}

interface TagsStoreEntry {
  allTags: Tags;
  hueTimestamp: number;
  version: number;
}

const STORAGE_POSTFIX = (<hueWindow>window).LOGGED_USERNAME;
const DATA_CATALOG_VERSION = 5;
const NAV_TAGS_STORE_ID = 'hue.dataCatalog.allNavTags';

export default class GeneralDataCatalog {
  store: LocalForage;
  allNavigatorTagsPromise?: Promise<Tags>;

  constructor() {
    this.store = localforage.createInstance({
      name: 'HueDataCatalog_' + STORAGE_POSTFIX
    });
  }

  async getAllNavigatorTags(options?: {
    silenceErrors?: boolean;
    refreshCache?: boolean;
  }): Promise<Tags> {
    if (
      this.allNavigatorTagsPromise &&
      DataCatalog.cacheEnabled() &&
      (!options || !options.refreshCache)
    ) {
      return this.allNavigatorTagsPromise;
    }

    if (!(<hueWindow>window).HAS_CATALOG) {
      return {};
    }

    const ttl = (<hueWindow>window).CACHEABLE_TTL || {};

    this.allNavigatorTagsPromise = new Promise((resolve, reject) => {
      const reloadAllTags = () => {
        fetchAllNavigatorTags({
          silenceErrors: options && options.silenceErrors
        })
          .then(allTags => {
            resolve(allTags);
            if (ttl.default && ttl.default > 0) {
              this.store.setItem<TagsStoreEntry>(NAV_TAGS_STORE_ID, {
                allTags,
                hueTimestamp: Date.now(),
                version: DATA_CATALOG_VERSION
              });
            }
          })
          .catch(reject);
      };

      if (
        ttl.default &&
        ttl.default > 0 &&
        DataCatalog.cacheEnabled() &&
        (!options || !options.refreshCache)
      ) {
        this.store
          .getItem<TagsStoreEntry>(NAV_TAGS_STORE_ID)
          .then(storeEntry => {
            if (
              storeEntry &&
              storeEntry.version === DATA_CATALOG_VERSION &&
              ttl.default &&
              (!storeEntry.hueTimestamp || Date.now() - storeEntry.hueTimestamp < ttl.default)
            ) {
              resolve(storeEntry.allTags);
            } else {
              reloadAllTags();
            }
          })
          .catch(reloadAllTags);
      } else {
        reloadAllTags();
      }
    });

    return this.allNavigatorTagsPromise;
  }

  async updateAllNavigatorTags(tagsToAdd: string[], tagsToRemove: string[]): Promise<void> {
    if (this.allNavigatorTagsPromise) {
      const allTags = await this.allNavigatorTagsPromise;
      tagsToAdd.forEach(newTag => {
        if (!allTags[newTag]) {
          allTags[newTag] = 0;
        }
        allTags[newTag]++;
      });
      tagsToRemove.forEach(removedTag => {
        if (!allTags[removedTag]) {
          allTags[removedTag]--;
          if (allTags[removedTag] === 0) {
            delete allTags[removedTag];
          }
        }
      });
      await this.store.setItem<TagsStoreEntry>(NAV_TAGS_STORE_ID, {
        allTags: allTags,
        hueTimestamp: Date.now(),
        version: DATA_CATALOG_VERSION
      });
    }
  }
}

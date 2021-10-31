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

import {
  assistErrorCallback,
  cancelActiveRequest,
  simpleGet,
  simplePost,
  successResponseIsError
} from './apiUtils';
import * as URLS from './urls';
import apiQueueManager from 'api/apiQueueManager';
import CancellableJqPromise from 'api/cancellableJqPromise';
import hueDebug from 'utils/hueDebug';
import huePubSub from 'utils/huePubSub';
import { getFromLocalStorage, setInLocalStorage } from 'utils/storageUtils';

export const LINK_SHARING_PERMS = {
  READ: 'read',
  WRITE: 'write',
  OFF: 'off'
};

class ApiHelper {
  constructor() {
    this.queueManager = apiQueueManager;
    this.cancelActiveRequest = cancelActiveRequest; // TODO: Remove when job_browser.mako is in webpack

    huePubSub.subscribe('assist.clear.git.cache', () => {
      setInLocalStorage(this.getAssistCacheIdentifier({ sourceType: 'git' }), {});
    });

    huePubSub.subscribe('assist.clear.collections.cache', () => {
      setInLocalStorage(this.getAssistCacheIdentifier({ sourceType: 'collections' }), {});
    });

    huePubSub.subscribe('assist.clear.hbase.cache', () => {
      setInLocalStorage(this.getAssistCacheIdentifier({ sourceType: 'hbase' }), {});
    });

    huePubSub.subscribe('assist.clear.document.cache', () => {
      setInLocalStorage(this.getAssistCacheIdentifier({ sourceType: 'document' }), {});
    });

    const clearAllCaches = () => {
      this.clearDbCache({
        sourceType: 'hive',
        clearAll: true
      });
      this.clearDbCache({
        sourceType: 'impala',
        clearAll: true
      });
      setInLocalStorage(this.getAssistCacheIdentifier({ sourceType: 'hdfs' }), {});
      setInLocalStorage(this.getAssistCacheIdentifier({ sourceType: 'adls' }), {});
      setInLocalStorage(this.getAssistCacheIdentifier({ sourceType: 'abfs' }), {});
      setInLocalStorage(this.getAssistCacheIdentifier({ sourceType: 'git' }), {});
      setInLocalStorage(this.getAssistCacheIdentifier({ sourceType: 's3' }), {});
      setInLocalStorage(this.getAssistCacheIdentifier({ sourceType: 'collections' }), {});
      setInLocalStorage(this.getAssistCacheIdentifier({ sourceType: 'hbase' }), {});
      setInLocalStorage(this.getAssistCacheIdentifier({ sourceType: 'document' }), {});
    };

    huePubSub.subscribe('assist.clear.all.caches', clearAllCaches);

    if (window.performance && window.performance.navigation) {
      if (window.performance.navigation.type === 1 && location.href.indexOf('/metastore') !== -1) {
        // Browser refresh of the metastore page
        clearAllCaches();
      }
    }
  }

  clearStorageCache(sourceType) {
    setInLocalStorage(this.getAssistCacheIdentifier({ sourceType: sourceType }), {});
  }

  hasExpired(timestamp, cacheType) {
    if (typeof hueDebug !== 'undefined' && typeof hueDebug.cacheTimeout !== 'undefined') {
      return new Date().getTime() - timestamp > hueDebug.cacheTimeout;
    }
    return new Date().getTime() - timestamp > CACHEABLE_TTL[cacheType];
  }

  /**
   *
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {string} options.url
   * @param {boolean} options.refreshCache
   * @param {string} [options.hash] - Optional hash to use as well as the url
   * @param {Function} options.fetchFunction
   * @param {Function} options.successCallback
   * @param {string} [options.cacheType] - Possible values 'default'|'sqlAnalyzer'. Default value 'default'
   * @param {Object} [options.editor] - Ace editor
   * @param {Object} [options.promise] - Optional promise that will be resolved if cached data exists
   */
  fetchCached(options) {
    const cacheIdentifier = this.getAssistCacheIdentifier(options);
    const cachedData = getFromLocalStorage(cacheIdentifier) || {};
    const cachedId = options.hash ? options.url + options.hash : options.url;

    if (
      options.refreshCache ||
      typeof cachedData[cachedId] == 'undefined' ||
      this.hasExpired(cachedData[cachedId].timestamp, options.cacheType || 'default')
    ) {
      if (typeof options.editor !== 'undefined' && options.editor !== null) {
        options.editor.showSpinner();
      }
      return options.fetchFunction(data => {
        cachedData[cachedId] = {
          timestamp: new Date().getTime(),
          data: data
        };
        try {
          setInLocalStorage(cacheIdentifier, cachedData);
        } catch (e) {}
      });
    } else {
      if (options.promise) {
        options.promise.resolve(cachedData[cachedId].data);
      }

      options.successCallback(cachedData[cachedId].data);
    }
  }

  /**
   * @param {object} options
   * @param {string} options.sourceType
   * @param {string} [options.cacheType] - Default value 'default'
   * @returns {string}
   */
  getAssistCacheIdentifier(options) {
    return 'hue.assist.' + (options.cacheType || 'default') + '.' + options.sourceType;
  }

  /**
   * @param {Object} data
   * @param {Object} options
   * @param {function} [options.successCallback]
   */
  saveSnippetToFile(data, options) {
    $.post(
      URLS.SAVE_TO_FILE_API,
      data,
      result => {
        if (typeof options.successCallback !== 'undefined') {
          options.successCallback(result);
        }
      },
      'json'
    ).fail(assistErrorCallback(options));
  }

  fetchUsersAndGroups(options) {
    $.ajax({
      method: 'GET',
      url: '/desktop/api/users/autocomplete',
      data: options.data || {},
      contentType: 'application/json'
    })
      .done(response => {
        options.successCallback(response);
      })
      .fail(response => {
        options.errorCallback(response);
      });
  }

  fetchUsersByIds(options) {
    $.ajax({
      method: 'GET',
      url: '/desktop/api/users',
      data: { userids: options.userids },
      contentType: 'application/json'
    })
      .done(response => {
        options.successCallback(response);
      })
      .fail(response => {
        options.errorCallback(response);
      });
  }

  /**
   *
   * @param {Object} options
   * @param {string} options.location
   * @param {boolean} [options.silenceErrors]
   */
  fetchTopo(options) {
    const url = URLS.TOPO_URL + options.location;
    return simpleGet(url, undefined, options);
  }

  /**
   *
   * @param {Object} options
   * @param {string[]} options.path
   * @param {string} options.type - 's3', 'adls', 'abfs' or 'hdfs'
   * @param {number} [options.offset]
   * @param {number} [options.length]
   * @param {boolean} [options.silenceErrors]
   */
  fetchStoragePreview(options) {
    let url;
    if (options.type === 's3') {
      url = URLS.S3_API_PREFIX;
    } else if (options.type === 'adls') {
      url = URLS.ADLS_API_PREFIX;
    } else if (options.type === 'abfs') {
      url = URLS.ABFS_API_PREFIX;
    } else {
      url = URLS.HDFS_API_PREFIX;
    }

    const clonedPath = options.path.concat();
    if (clonedPath.length && clonedPath[0] === '/') {
      clonedPath.shift();
    }
    url += clonedPath.join('/').replace(/#/g, '%23') + '?compression=none&mode=text';
    url += '&offset=' + (options.offset || 0);
    url += '&length=' + (options.length || 118784);

    const deferred = $.Deferred();
    $.ajax({
      dataType: 'json',
      url: url,
      success: data => {
        if (successResponseIsError(data)) {
          deferred.reject(assistErrorCallback(options)(data));
        } else {
          deferred.resolve(data);
        }
      },
      fail: deferred.reject
    });

    return deferred.promise();
  }

  /**
   * @param {Object} options
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   * @param {Number} [options.timeout]
   * @param {Object} [options.editor] - Ace editor
   *
   * @param {string[]} options.pathParts
   * @param {number} [options.pageSize] - Default 500
   * @param {number} [options.page] - Default 1
   * @param {string} [options.filter]
   */
  fetchHdfsPath(options) {
    if (
      options.pathParts.length > 0 &&
      (options.pathParts[0] === '/' || options.pathParts[0] === '')
    ) {
      options.pathParts.shift();
    }
    let url =
      URLS.HDFS_API_PREFIX +
      encodeURI(options.pathParts.join('/')) +
      '?format=json&sortby=name&descending=false&pagesize=' +
      (options.pageSize || 500) +
      '&pagenum=' +
      (options.page || 1);
    if (options.filter) {
      url += '&filter=' + options.filter;
    }
    const fetchFunction = storeInCache => {
      if (options.timeout === 0) {
        assistErrorCallback(options)({ status: -1 });
        return;
      }
      return $.ajax({
        dataType: 'json',
        url: url,
        timeout: options.timeout,
        success: data => {
          if (
            !data.error &&
            !successResponseIsError(data) &&
            typeof data.files !== 'undefined' &&
            data.files !== null
          ) {
            if (data.files.length > 2 && !options.filter) {
              storeInCache(data);
            }
            options.successCallback(data);
          } else {
            assistErrorCallback(options)(data);
          }
        }
      })
        .fail(assistErrorCallback(options))
        .always(() => {
          if (typeof options.editor !== 'undefined' && options.editor !== null) {
            options.editor.hideSpinner();
          }
        });
    };

    return this.fetchCached(
      $.extend({}, options, {
        sourceType: 'hdfs',
        url: url,
        fetchFunction: fetchFunction
      })
    );
  }

  /**
   * @param {Object} options
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   * @param {Number} [options.timeout]
   * @param {Object} [options.editor] - Ace editor
   *
   * @param {string[]} options.pathParts
   * @param {number} [options.pageSize] - Default 500
   * @param {number} [options.page] - Default 1
   * @param {string} [options.filter]
   */
  fetchAdlsPath(options) {
    options.pathParts.shift();
    let url =
      URLS.ADLS_API_PREFIX +
      encodeURI(options.pathParts.join('/')) +
      '?format=json&sortby=name&descending=false&pagesize=' +
      (options.pageSize || 500) +
      '&pagenum=' +
      (options.page || 1);
    if (options.filter) {
      url += '&filter=' + options.filter;
    }
    const fetchFunction = storeInCache => {
      if (options.timeout === 0) {
        assistErrorCallback(options)({ status: -1 });
        return;
      }
      return $.ajax({
        dataType: 'json',
        url: url,
        timeout: options.timeout,
        success: data => {
          if (
            !data.error &&
            !successResponseIsError(data) &&
            typeof data.files !== 'undefined' &&
            data.files !== null
          ) {
            if (data.files.length > 2 && !options.filter) {
              storeInCache(data);
            }
            options.successCallback(data);
          } else {
            assistErrorCallback(options)(data);
          }
        }
      })
        .fail(assistErrorCallback(options))
        .always(() => {
          if (typeof options.editor !== 'undefined' && options.editor !== null) {
            options.editor.hideSpinner();
          }
        });
    };

    return this.fetchCached(
      $.extend({}, options, {
        sourceType: 'adls',
        url: url,
        fetchFunction: fetchFunction
      })
    );
  }

  /**
   * @param {Object} options
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   * @param {Number} [options.timeout]
   * @param {Object} [options.editor] - Ace editor
   *
   * @param {string[]} options.pathParts
   * @param {number} [options.pageSize] - Default 500
   * @param {number} [options.page] - Default 1
   * @param {string} [options.filter]
   */
  fetchAbfsPath(options) {
    let url =
      URLS.ABFS_API_PREFIX +
      encodeURI(options.pathParts.join('/')) +
      '?format=json&sortby=name&descending=false&pagesize=' +
      (options.pageSize || 500) +
      '&pagenum=' +
      (options.page || 1);
    if (options.filter) {
      url += '&filter=' + options.filter;
    }
    const fetchFunction = storeInCache => {
      if (options.timeout === 0) {
        assistErrorCallback(options)({ status: -1 });
        return;
      }
      return $.ajax({
        dataType: 'json',
        url: url,
        timeout: options.timeout,
        success: data => {
          if (
            !data.error &&
            !successResponseIsError(data) &&
            typeof data.files !== 'undefined' &&
            data.files !== null
          ) {
            if (data.files.length > 2 && !options.filter) {
              storeInCache(data);
            }
            options.successCallback(data);
          } else {
            assistErrorCallback(options)(data);
          }
        }
      })
        .fail(assistErrorCallback(options))
        .always(() => {
          if (typeof options.editor !== 'undefined' && options.editor !== null) {
            options.editor.hideSpinner();
          }
        });
    };

    return this.fetchCached(
      $.extend({}, options, {
        sourceType: 'abfs',
        url: url,
        fetchFunction: fetchFunction
      })
    );
  }

  /**
   * @param {Object} options
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   * @param {Number} [options.timeout]
   *
   * @param {string[]} options.pathParts
   * @param {string} options.fileType
   */
  fetchGitContents(options) {
    const url =
      URLS.GIT_API_PREFIX +
      '?path=' +
      encodeURI(options.pathParts.join('/')) +
      '&fileType=' +
      options.fileType;
    const fetchFunction = storeInCache => {
      if (options.timeout === 0) {
        assistErrorCallback(options)({ status: -1 });
        return;
      }
      $.ajax({
        dataType: 'json',
        url: url,
        timeout: options.timeout,
        success: data => {
          if (!data.error && !successResponseIsError(data)) {
            if (
              data.fileType === 'dir' &&
              typeof data.files !== 'undefined' &&
              data.files !== null
            ) {
              if (data.files.length > 2) {
                storeInCache(data);
              }
              options.successCallback(data);
            } else if (
              data.fileType === 'file' &&
              typeof data.content !== 'undefined' &&
              data.content !== null
            ) {
              options.successCallback(data);
            }
          } else {
            assistErrorCallback(options)(data);
          }
        }
      }).fail(assistErrorCallback(options));
    };

    this.fetchCached(
      $.extend({}, options, {
        sourceType: 'git',
        url: url,
        fetchFunction: fetchFunction
      })
    );
  }

  /**
   * @param {Object} options
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   * @param {Number} [options.timeout]
   * @param {Object} [options.editor] - Ace editor
   *
   * @param {string[]} options.pathParts
   * @param {number} [options.pageSize] - Default 500
   * @param {number} [options.page] - Default 1
   * @param {string} [options.filter]
   */
  fetchS3Path(options) {
    options.pathParts.shift(); // remove the trailing /
    let url =
      URLS.S3_API_PREFIX +
      encodeURI(options.pathParts.join('/')) +
      '?format=json&sortby=name&descending=false&pagesize=' +
      (options.pageSize || 500) +
      '&pagenum=' +
      (options.page || 1);
    if (options.filter) {
      url += '&filter=' + options.filter;
    }
    const fetchFunction = storeInCache => {
      if (options.timeout === 0) {
        assistErrorCallback(options)({ status: -1 });
        return;
      }

      $.ajax({
        dataType: 'json',
        url: url,
        timeout: options.timeout,
        success: data => {
          if (
            !data.error &&
            !successResponseIsError(data) &&
            typeof data.files !== 'undefined' &&
            data.files !== null
          ) {
            if (data.files.length > 2 && !options.filter) {
              storeInCache(data);
            }
            options.successCallback(data);
          } else {
            assistErrorCallback(options)(data);
          }
        }
      })
        .fail(assistErrorCallback(options))
        .always(() => {
          if (typeof options.editor !== 'undefined' && options.editor !== null) {
            options.editor.hideSpinner();
          }
        });
    };

    this.fetchCached(
      $.extend({}, options, {
        sourceType: 's3',
        url: url,
        fetchFunction: fetchFunction
      })
    );
  }

  async fetchFavoriteApp(options) {
    return new Promise((resolve, reject) => {
      simpleGet('/desktop/api2/user_preferences/default_app').done(resolve).fail(reject);
    });
  }

  async setFavoriteAppAsync(options) {
    return new Promise((resolve, reject) => {
      simplePost('/desktop/api2/user_preferences/default_app', options).done(resolve).fail(reject);
    });
  }

  /**
   * @param {Object} options
   * @param {String} options.collectionName
   * @param {String} options.fieldName
   * @param {String} options.prefix
   * @param {String} [options.engine]
   * @param {Function} options.successCallback
   * @param {Function} [options.alwaysCallback]
   * @param {Number} [options.timeout]
   *
   */
  fetchDashboardTerms(options) {
    if (options.timeout === 0) {
      assistErrorCallback(options)({ status: -1 });
      return;
    }
    $.ajax({
      dataType: 'json',
      url: URLS.DASHBOARD_TERMS_API,
      type: 'POST',
      data: {
        collection: ko.mapping.toJSON({
          id: '',
          name: options.collectionName,
          engine: options.engine || 'solr'
        }),
        analysis: ko.mapping.toJSON({
          name: options.fieldName,
          terms: {
            prefix: options.prefix || ''
          }
        })
      },
      timeout: options.timeout,
      success: data => {
        if (!data.error && !successResponseIsError(data) && data.status === 0) {
          options.successCallback(data);
        } else {
          assistErrorCallback(options)(data);
        }
      }
    })
      .fail(assistErrorCallback(options))
      .always(options.alwaysCallback);
  }

  /**
   * @param {Object} options
   * @param {String} options.collectionName
   * @param {String} options.fieldName
   * @param {String} [options.engine]
   * @param {Function} options.successCallback
   * @param {Function} [options.alwaysCallback]
   * @param {Number} [options.timeout]
   *
   */
  fetchDashboardStats(options) {
    if (options.timeout === 0) {
      assistErrorCallback(options)({ status: -1 });
      return;
    }
    $.ajax({
      dataType: 'json',
      url: URLS.DASHBOARD_STATS_API,
      type: 'POST',
      data: {
        collection: ko.mapping.toJSON({
          id: '',
          name: options.collectionName,
          engine: options.engine || 'solr'
        }),
        analysis: ko.mapping.toJSON({
          name: options.fieldName,
          stats: {
            facet: ''
          }
        }),
        query: ko.mapping.toJSON({
          qs: [{ q: '' }],
          fqs: []
        })
      },
      timeout: options.timeout,
      success: data => {
        if (!data.error && !successResponseIsError(data) && data.status === 0) {
          options.successCallback(data);
        } else if (data.status === 1) {
          options.notSupportedCallback(data);
        } else {
          assistErrorCallback(options)(data);
        }
      }
    })
      .fail(assistErrorCallback(options))
      .always(options.alwaysCallback);
  }

  /**
   * @param {Object} options
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   * @param {Number} [options.timeout]
   * @param {Object} [options.editor] - Ace editor
   */
  fetchHBase(options) {
    let suffix = 'getClusters';
    if (options.parent.name !== '') {
      suffix = 'getTableList/' + options.parent.name;
    }
    const url = URLS.HBASE_API_PREFIX + suffix;
    const fetchFunction = storeInCache => {
      if (options.timeout === 0) {
        assistErrorCallback(options)({ status: -1 });
        return;
      }
      $.ajax({
        dataType: 'json',
        url: url,
        timeout: options.timeout,
        success: data => {
          if (!data.error && !successResponseIsError(data)) {
            storeInCache(data);
            options.successCallback(data);
          } else {
            assistErrorCallback(options)(data);
          }
        }
      })
        .fail(assistErrorCallback(options))
        .always(() => {
          if (typeof options.editor !== 'undefined' && options.editor !== null) {
            options.editor.hideSpinner();
          }
        });
    };

    this.fetchCached(
      $.extend({}, options, {
        sourceType: 'hbase',
        url: url,
        fetchFunction: fetchFunction
      })
    );
  }

  /**
   * @param {Object} options
   * @param {Number} options.pastMs
   * @param {Number} options.stepMs
   *
   * @return {Promise}
   */
  fetchResourceStats(options) {
    const queryMetric = metricName => {
      const now = Date.now();
      return simplePost('/metadata/api/prometheus/query', {
        query: ko.mapping.toJSON(metricName),
        start: Math.floor((now - options.pastMs) / 1000),
        end: Math.floor(now / 1000),
        step: options.stepMs / 1000
      });
    };

    const combinedDeferred = $.Deferred();
    $.when(
      queryMetric('round((go_memstats_alloc_bytes / go_memstats_sys_bytes) * 100)'), // CPU percentage
      queryMetric('round((go_memstats_alloc_bytes / go_memstats_sys_bytes) * 100)'), // Memory percentage
      queryMetric('round((go_memstats_alloc_bytes / go_memstats_sys_bytes) * 100)'), // IO percentage
      queryMetric('impala_queries_count{datawarehouse="' + options.clusterName + '"}'), // Sum of all queries in flight (currently total query executed for testing purpose)
      queryMetric('impala_queries{datawarehouse="' + options.clusterName + '"}') // Queued queries
    )
      .done(() => {
        const timestampIndex = {};
        for (let j = 0; j < arguments.length; j++) {
          const response = arguments[j];
          if (response.data.result[0]) {
            const values = response.data.result[0].values;
            for (let i = 0; i < values.length; i++) {
              if (!timestampIndex[values[i][0]]) {
                timestampIndex[values[i][0]] = [values[i][0] * 1000, 0, 0, 0, 0, 0]; // Adjust back to milliseconds
              }
              timestampIndex[values[i][0]][j + 1] = parseFloat(values[i][1]);
            }
          }
        }
        const result = [];
        Object.keys(timestampIndex).forEach(key => {
          result.push(timestampIndex[key]);
        });
        result.sort((a, b) => {
          return a[0] - b[0];
        });
        combinedDeferred.resolve(result);
      })
      .fail(combinedDeferred.reject);

    return combinedDeferred.promise();
  }

  /**
   * @param {Object} options
   * @param {Function} [options.successCallback]
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   */
  fetchConfigurations(options) {
    simpleGet(URLS.CONFIG_APPS_API, {}, options);
  }

  saveGlobalConfiguration(options) {
    simplePost(
      URLS.CONFIG_APPS_API,
      {
        configuration: ko.mapping.toJSON(options.configuration)
      },
      options
    );
  }

  /**
   * @param {Object} options
   * @param {Function} [options.successCallback]
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   *
   * @param {string} options.app
   * @param {Object} options.properties
   * @param {boolean} [options.isDefault]
   * @param {Number} [options.groupId]
   * @param {Number} [options.userId]
   */
  saveConfiguration(options) {
    simplePost(
      URLS.CONFIG_SAVE_API,
      {
        app: options.app,
        properties: ko.mapping.toJSON(options.properties),
        is_default: options.isDefault,
        group_id: options.groupId,
        user_id: options.userId
      },
      options
    );
  }

  /**
   * @param {Object} options
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   *
   * @param {string} [options.uuid]
   */
  fetchDocuments(options) {
    let id = '';
    if (options.uuid) {
      id += options.uuid;
    }
    if (options.type && options.type !== 'all') {
      id += options.type;
    }

    let promise = this.queueManager.getQueued(URLS.DOCUMENTS_API, id);
    const firstInQueue = typeof promise === 'undefined';
    if (firstInQueue) {
      promise = $.Deferred();
      this.queueManager.addToQueue(promise, URLS.DOCUMENTS_API, id);
    }

    promise.done(options.successCallback).fail(assistErrorCallback(options));

    if (!firstInQueue) {
      return;
    }

    const data = {
      uuid: options.uuid
    };

    if (options.type && options.type !== 'all') {
      data.type = ['directory', options.type];
    }

    $.ajax({
      url: URLS.DOCUMENTS_API,
      data: data,
      traditional: true,
      success: data => {
        if (!successResponseIsError(data)) {
          promise.resolve(data);
        } else {
          promise.reject(data);
        }
      }
    }).fail(promise.reject);
  }

  /**
   * @param {Object} options
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   *
   * @param {string} [options.path]
   * @param {string} [options.query]
   * @param {string} [options.type]
   * @param {int} [options.page]
   * @param {int} [options.limit]
   */
  searchDocuments(options) {
    return $.ajax({
      url: URLS.DOCUMENTS_SEARCH_API,
      data: {
        uuid: options.uuid,
        text: options.query,
        type: options.type,
        page: options.page,
        limit: options.limit,
        include_trashed: options.include_trashed
      },
      success: data => {
        if (!successResponseIsError(data)) {
          options.successCallback(data);
        } else {
          assistErrorCallback(options)(data);
        }
      }
    }).fail(assistErrorCallback(options));
  }

  /**
   * @param {Object} options
   * @param {number} options.uuid
   * @param {boolean} [options.dependencies]
   * @param {boolean} [options.silenceErrors]
   * @param {boolean} [options.fetchContents]
   *
   * @return {CancellableJqPromise}
   */
  fetchDocument(options) {
    const deferred = $.Deferred();
    const request = $.ajax({
      url: URLS.DOCUMENTS_API,
      data: {
        uuid: options.uuid,
        data: !!options.fetchContents,
        dependencies: options.dependencies
      },
      success: data => {
        if (!successResponseIsError(data)) {
          deferred.resolve(data);
        } else {
          deferred.reject(
            assistErrorCallback({
              silenceErrors: options.silenceErrors
            })
          );
        }
      }
    }).fail(
      assistErrorCallback({
        silenceErrors: options.silenceErrors,
        errorCallback: deferred.reject
      })
    );
    return new CancellableJqPromise(deferred, request);
  }

  /**
   * @param {Object} options
   * @param {string} options.uuid
   * @param {boolean} [options.silenceErrors]
   * @param {boolean} [options.dependencies]
   * @param {boolean} [options.fetchContents]
   *
   * @param options
   * @return {Promise<unknown>}
   */
  async fetchDocumentAsync(options) {
    return new Promise((resolve, reject) => {
      this.fetchDocument(options).done(resolve).fail(reject);
    });
  }

  /**
   * @param {Object} options
   * @param {string} options.uuid
   * @param {string} options.perm - See LINK_SHARING_PERMS
   * @param {boolean} [options.silenceErrors]
   *
   * @param options
   * @return {Promise<unknown>}
   */
  async setLinkSharingPermsAsync(options) {
    return new Promise((resolve, reject) => {
      simplePost('/desktop/api2/doc/share/link', {
        uuid: JSON.stringify(options.uuid),
        perm: JSON.stringify(options.perm)
      })
        .done(resolve)
        .fail(reject);
    });
  }

  /**
   * @param {Object} options
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   *
   * @param {string} options.parentUuid
   * @param {string} options.name
   */
  createDocumentsFolder(options) {
    simplePost(
      URLS.DOCUMENTS_API + 'mkdir',
      {
        parent_uuid: ko.mapping.toJSON(options.parentUuid),
        name: ko.mapping.toJSON(options.name)
      },
      options
    );
  }

  /**
   * @param {Object} options
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   *
   * @param {string} options.uuid
   * @param {string} options.name
   */
  updateDocument(options) {
    simplePost(
      URLS.DOCUMENTS_API + 'update',
      {
        uuid: ko.mapping.toJSON(options.uuid),
        name: options.name
      },
      options
    );
  }

  /**
   * @param {Object} options
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {Function} [options.progressHandler]
   * @param {boolean} [options.silenceErrors]
   *
   * @param {FormData} options.formData
   */
  uploadDocument(options) {
    $.ajax({
      url: URLS.DOCUMENTS_API + 'import',
      type: 'POST',
      success: data => {
        if (!successResponseIsError(data)) {
          options.successCallback(data);
        } else {
          assistErrorCallback(options)(data);
        }
      },
      xhr: () => {
        const myXhr = $.ajaxSettings.xhr();
        if (myXhr.upload && options.progressHandler) {
          myXhr.upload.addEventListener('progress', options.progressHandler, false);
        }
        return myXhr;
      },
      dataType: 'json',
      data: options.formData,
      cache: false,
      contentType: false,
      processData: false
    }).fail(assistErrorCallback(options));
  }

  /**
   *
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   *
   * @param {number} options.sourceId - The ID of the source document
   * @param {number} options.destinationId - The ID of the target document
   */
  moveDocument(options) {
    simplePost(
      URLS.DOCUMENTS_API + 'move',
      {
        source_doc_uuid: ko.mapping.toJSON(options.sourceId),
        destination_doc_uuid: ko.mapping.toJSON(options.destinationId)
      },
      options
    );
  }

  /**
   * @param {Object} options
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   *
   * @param {string} options.uuid
   * @param {string} [options.skipTrash] - Default false
   */
  deleteDocument(options) {
    simplePost(
      URLS.DOCUMENTS_API + 'delete',
      {
        uuid: ko.mapping.toJSON(options.uuid),
        skip_trash: ko.mapping.toJSON(options.skipTrash || false)
      },
      options
    );
  }

  /**
   * @param {Object} options
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   *
   * @param {string} options.uuid
   */
  copyDocument(options) {
    simplePost(
      URLS.DOCUMENTS_API + 'copy',
      {
        uuid: ko.mapping.toJSON(options.uuid)
      },
      options
    );
  }

  /**
   * @param {Object} options
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   *
   * @param {string} options.uuid
   */
  restoreDocument(options) {
    simplePost(
      URLS.DOCUMENTS_API + 'restore',
      {
        uuids: ko.mapping.toJSON(options.uuids)
      },
      options
    );
  }

  /**
   *
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {string} [options.databaseName]
   * @param {string} [options.tableName]
   * @param {string} [options.cacheType] - Possible values 'default', 'sqlAnalyzer'. Default value 'default'
   * @param {string[]} [options.fields]
   * @param {boolean} [options.clearAll]
   */
  clearDbCache(options) {
    const cacheIdentifier = this.getAssistCacheIdentifier(options);
    if (options.clearAll) {
      setInLocalStorage(cacheIdentifier, {});
    } else {
      let url = URLS.AUTOCOMPLETE_API_PREFIX;
      if (options.databaseName) {
        url += options.databaseName + '/';
      }
      if (options.tableName) {
        url += options.tableName + '/';
      }
      if (options.fields) {
        url += options.fields.length > 0 ? '/' + options.fields.join('/') : '';
      }
      const cachedData = getFromLocalStorage(cacheIdentifier) || {};
      delete cachedData[url];
      getFromLocalStorage(cacheIdentifier, cachedData);
    }
  }

  /**
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {string} options.invalidate - 'invalidate' or 'invalidateAndFlush'
   * @param {string[]} [options.path]
   * @param {ContextCompute} [options.compute]
   * @param {boolean} [options.silenceErrors]
   */
  invalidateSourceMetadata(options) {
    const deferred = $.Deferred();

    if (
      options.sourceType === 'impala' &&
      (options.invalidate === 'invalidate' || options.invalidate === 'invalidateAndFlush')
    ) {
      const data = {
        flush_all: options.invalidate === 'invalidateAndFlush',
        cluster: JSON.stringify(options.compute)
      };

      if (options.path && options.path.length > 0) {
        data.database = options.path[0];
      }
      if (options.path && options.path.length > 1) {
        data.table = options.path[1];
      }

      const request = simplePost(URLS.IMPALA_INVALIDATE_API, data, options)
        .done(deferred.resolve)
        .fail(deferred.reject);

      return new CancellableJqPromise(deferred, request);
    }

    return deferred.resolve().promise();
  }

  /**
   * Fetches the partitions for the given path
   *
   * @param {Object} options
   * @param {boolean} [options.silenceErrors]
   *
   * @param {string[]} options.path
   * @param {ContextCompute} options.compute
   *
   * @return {CancellableJqPromise}
   */
  fetchPartitions(options) {
    const deferred = $.Deferred();

    // TODO: No sourceType needed?
    const request = $.post('/metastore/table/' + options.path.join('/') + '/partitions', {
      format: 'json',
      cluster: JSON.stringify(options.compute)
    })
      .done(response => {
        if (!successResponseIsError(response)) {
          if (!response) {
            response = {};
          }
          response.hueTimestamp = Date.now();
          deferred.resolve(response);
        } else {
          assistErrorCallback({
            silenceErrors: options.silenceErrors,
            errorCallback: deferred.reject
          })(response);
        }
      })
      .fail(response => {
        // Don't report any partitions if it's not partitioned instead of error to prevent unnecessary calls
        if (
          response &&
          response.responseText &&
          response.responseText.indexOf('is not partitioned') !== -1
        ) {
          deferred.resolve({
            hueTimestamp: Date.now(),
            partition_keys_json: [],
            partition_values_json: []
          });
        } else {
          assistErrorCallback({
            silenceErrors: options.silenceErrors,
            errorCallback: deferred.reject
          })(response);
        }
      });

    return new CancellableJqPromise(deferred, request);
  }

  clearNotebookHistory(options) {
    const data = {
      notebook: options.notebookJson,
      doc_type: options.docType,
      is_notification_manager: options.isNotificationManager
    };
    return simplePost('/notebook/api/clear_history', data);
  }

  closeNotebook(options) {
    const data = {
      notebook: options.notebookJson,
      editorMode: options.editorMode
    };
    return simplePost('/notebook/api/notebook/close', data);
  }

  async checkStatus(options) {
    return new Promise((resolve, reject) => {
      const data = {
        notebook: options.notebookJson
      };
      $.post({
        url: '/notebook/api/check_status',
        data: data
      })
        .done(data => {
          // 0, -3 and other negative values have meaning for this endpoint
          if (data && typeof data.status !== 'undefined') {
            resolve(data);
          } else if (successResponseIsError(data)) {
            reject(assistErrorCallback(options)(data));
          } else {
            reject();
          }
        })
        .fail(assistErrorCallback(options));
    });
  }

  getExternalStatement(options) {
    const data = {
      notebook: options.notebookJson,
      snippet: options.snippetJson
    };
    return simplePost('/notebook/api/get_external_statement', data);
  }

  fetchResultSize(options) {
    const data = {
      notebook: options.notebookJson,
      snippet: options.snippetJson
    };
    return simplePost('/notebook/api/fetch_result_size', data);
  }

  getLogs(options) {
    const data = {
      notebook: options.notebookJson,
      snippet: options.snippetJson,
      from: options.from,
      jobs: options.jobsJson,
      full_log: options.fullLog,
      operationId: options.executable.operationId
    };
    return simplePost('/notebook/api/get_logs', data);
  }

  async saveNotebook(options) {
    const data = {
      notebook: options.notebookJson,
      editorMode: options.editorMode
    };
    return new Promise((resolve, reject) => {
      simplePost('/notebook/api/notebook/save', data).then(resolve).catch(reject);
    });
  }

  async getHistory(options) {
    return new Promise((resolve, reject) => {
      $.get('/api/editor/get_history', {
        doc_type: options.type,
        limit: options.limit || 50,
        page: options.page || 1,
        doc_text: options.docFilter,
        is_notification_manager: options.isNotificationManager
      })
        .done(data => {
          if (successResponseIsError(data)) {
            reject(assistErrorCallback(options)(data));
            return;
          }
          resolve(data);
        })
        .fail(reject);
    });
  }

  /**
   *
   * @param {Object} options
   * @param {Snippet} options.snippet
   *
   * @return {CancellableJqPromise<string>}
   */
  async explainAsync(options) {
    const data = {
      notebook: await options.snippet.parentNotebook.toContextJson(),
      snippet: options.snippet.toContextJson()
    };
    return new Promise((resolve, reject) => {
      simplePost('/notebook/api/explain', data, options)
        .done(response => {
          resolve(response.explanation);
        })
        .fail(reject);
    });
  }

  /**
   *
   * @param {Object} options
   * @param {statement} options.statement
   * @param {doc_type} options.doc_type
   * @param {name} options.name
   * @param {description} options.description
   *
   * @return {CancellableJqPromise<string>}
   */
  async createGistAsync(options) {
    const data = {
      statement: options.statement,
      doc_type: options.doc_type,
      name: options.name,
      description: options.description
    };
    return new Promise((resolve, reject) => {
      simplePost(URLS.GIST_API + 'create', data, options)
        .done(response => {
          resolve(response.link);
        })
        .fail(reject);
    });
  }

  /**
   *
   * @param {Object} options
   * @param {channel} options.channel
   * @param {message} options.message
   *
   * @return {Promise<void>}
   */
  async sendSlackMessageAsync(options) {
    const data = {
      channel: options.channel,
      message: options.message
    };
    return new Promise((resolve, reject) => {
      simplePost(URLS.SEND_SLACK_MESSAGE, data, options).done(resolve).fail(reject);
    });
  }

  /**
   *
   * @param {Object} options
   *
   * @return {Promise<Object>}
   */
  async getSlackChannelsAsync(options) {
    return new Promise((resolve, reject) => {
      simpleGet(URLS.GET_SLACK_CHANNELS, {}, options)
        .done(response => {
          resolve(response.channels);
        })
        .fail(reject);
    });
  }

  /**
   * @param {Object} options
   * @param {boolean} [options.silenceErrors]
   * @param {ContextCompute} options.compute
   * @param {string} options.queryId
   * @return {CancellableJqPromise}
   */
  fetchQueryExecutionAnalysis(options) {
    //var url = '/metadata/api/workload_analytics/get_impala_query/';
    const url = '/impala/api/query/alanize';
    const deferred = $.Deferred();

    let tries = 0;

    const cancellablePromises = [];

    const promise = new CancellableJqPromise(deferred, undefined, cancellablePromises);

    const pollForAnalysis = () => {
      if (tries === 10) {
        deferred.reject();
        return;
      }
      tries++;
      cancellablePromises.pop(); // Remove the last one
      cancellablePromises.push(
        deferred,
        simplePost(
          url,
          {
            cluster: JSON.stringify(options.compute),
            query_id: '"' + options.queryId + '"'
          },
          options
        )
          .done(response => {
            if (response && response.data) {
              deferred.resolve(response.data);
            } else {
              const timeout = window.setTimeout(() => {
                pollForAnalysis();
              }, 1000 + tries * 500); // TODO: Adjust once fully implemented;
              promise.onCancel(() => {
                window.clearTimeout(timeout);
              });
            }
          })
          .fail(deferred.reject)
      );
    };

    pollForAnalysis();

    return promise;
  }

  fixQueryExecutionAnalysis(options) {
    const url = '/impala/api/query/alanize/fix';
    const deferred = $.Deferred();

    const request = simplePost(
      url,
      {
        cluster: JSON.stringify(options.compute),
        fix: JSON.stringify(options.fix),
        start_time: options.start_time
      },
      {
        silenceErrors: options.silenceErrors,
        successCallback: response => {
          if (response.status === 0) {
            deferred.resolve(response.details);
          } else {
            deferred.reject();
          }
        },
        errorCallback: deferred.reject
      }
    );

    return new CancellableJqPromise(deferred, request);
  }

  fetchQueryExecutionStatistics(options) {
    const url = '/impala/api/query/alanize/metrics';
    const deferred = $.Deferred();

    const request = simplePost(
      url,
      {
        cluster: JSON.stringify(options.cluster),
        query_id: '"' + options.queryId + '"'
      },
      {
        silenceErrors: options.silenceErrors,
        successCallback: response => {
          if (response.status === 0) {
            deferred.resolve(response.data);
          } else {
            deferred.reject();
          }
        },
        errorCallback: deferred.reject
      }
    );

    return new CancellableJqPromise(deferred, request);
  }

  async fetchHueConfigAsync(options) {
    return new Promise((resolve, reject) => {
      $.get(URLS.GET_HUE_CONFIG_API)
        .done(response => {
          if (!response && response.status === -1) {
            reject(response.message);
          } else {
            resolve(response);
          }
        })
        .fail(reject);
    });
  }

  fetchHueDocsInteractive(query) {
    const deferred = $.Deferred();
    const request = $.post(URLS.INTERACTIVE_SEARCH_API, {
      query_s: ko.mapping.toJSON(query),
      limit: 50,
      sources: '["documents"]'
    })
      .done(data => {
        if (data.status === 0) {
          deferred.resolve(data);
        } else {
          deferred.reject(data);
        }
      })
      .fail(deferred.reject);
    return new CancellableJqPromise(deferred, request);
  }

  fetchNavEntitiesInteractive(options) {
    const deferred = $.Deferred();
    const request = $.post(URLS.INTERACTIVE_SEARCH_API, {
      query_s: ko.mapping.toJSON(options.query),
      field_facets: ko.mapping.toJSON(options.facets || []),
      limit: 50,
      sources: '["sql", "hdfs", "s3"]'
    })
      .done(data => {
        if (data.status === 0) {
          deferred.resolve(data);
        } else {
          deferred.reject(data);
        }
      })
      .fail(deferred.reject);
    return new CancellableJqPromise(deferred, request);
  }

  /**
   *
   * @param {Object} options
   * @param {string} options.statements
   * @param {boolean} [options.silenceErrors]
   */
  formatSql(options) {
    const deferred = $.Deferred();

    const request = simplePost(
      URLS.FORMAT_SQL_API,
      {
        statements: options.statements
      },
      {
        silenceErrors: options.silenceErrors,
        successCallback: deferred.resolve,
        errorCallback: deferred.reject
      }
    );

    return new CancellableJqPromise(deferred, request);
  }

  /**
   *
   * @param {Object} options
   * @param {string} options.statement
   * @param {string} options.doc_type
   * @param {string} options.name
   * @param {string} options.description
   * @param {boolean} [options.silenceErrors]
   */
  createGist(options) {
    const deferred = $.Deferred();

    const request = simplePost(
      URLS.GIST_API + 'create',
      {
        statement: options.statement,
        doc_type: options.doc_type,
        name: options.name,
        description: options.description
      },
      {
        silenceErrors: options.silenceErrors,
        successCallback: deferred.resolve,
        errorCallback: deferred.reject
      }
    );

    return new CancellableJqPromise(deferred, request);
  }
}

const apiHelper = new ApiHelper();

export default apiHelper;

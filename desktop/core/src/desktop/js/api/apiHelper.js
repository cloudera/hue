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
import ko from 'knockout';

import apiQueueManager from 'api/apiQueueManager';
import CancellablePromise from 'api/cancellablePromise';
import hueDebug from 'utils/hueDebug';
import huePubSub from 'utils/huePubSub';
import hueUtils from 'utils/hueUtils';

const AUTOCOMPLETE_API_PREFIX = '/notebook/api/autocomplete/';
const SAMPLE_API_PREFIX = '/notebook/api/sample/';
const EXECUTE_API_PREFIX = '/notebook/api/execute/';
const DOCUMENTS_API = '/desktop/api2/doc/';
const DOCUMENTS_SEARCH_API = '/desktop/api2/docs/';
const FETCH_CONFIG = '/desktop/api2/get_config/';
const HDFS_API_PREFIX = '/filebrowser/view=' + encodeURIComponent('/');
const ADLS_API_PREFIX = '/filebrowser/view=' + encodeURIComponent('adl:/');
const GIT_API_PREFIX = '/desktop/api/vcs/contents/';
const S3_API_PREFIX = '/filebrowser/view=' + encodeURIComponent('S3A://');
const IMPALA_INVALIDATE_API = '/impala/api/invalidate';
const CONFIG_SAVE_API = '/desktop/api/configurations/save/';
const CONFIG_APPS_API = '/desktop/api/configurations';
const SOLR_COLLECTIONS_API = '/indexer/api/indexes/list/';
const SOLR_FIELDS_API = '/indexer/api/index/list/';
const DASHBOARD_TERMS_API = '/dashboard/get_terms';
const DASHBOARD_STATS_API = '/dashboard/get_stats';
const FORMAT_SQL_API = '/notebook/api/format';
const TOPO_URL = '/desktop/topo/';

const SEARCH_API = '/desktop/api/search/entities';
const INTERACTIVE_SEARCH_API = '/desktop/api/search/entities_interactive';

const HBASE_API_PREFIX = '/hbase/api/';
const SAVE_TO_FILE = '/filebrowser/save';

const NAV_URLS = {
  ADD_TAGS: '/metadata/api/catalog/add_tags',
  DELETE_TAGS: '/metadata/api/catalog/delete_tags',
  FIND_ENTITY: '/metadata/api/catalog/find_entity',
  LIST_TAGS: '/metadata/api/catalog/list_tags',
  UPDATE_PROPERTIES: '/metadata/api/catalog/update_properties'
};

const NAV_OPT_URLS = {
  TOP_AGGS: '/metadata/api/optimizer/top_aggs',
  TOP_COLUMNS: '/metadata/api/optimizer/top_columns',
  TOP_FILTERS: '/metadata/api/optimizer/top_filters',
  TOP_JOINS: '/metadata/api/optimizer/top_joins',
  TOP_TABLES: '/metadata/api/optimizer/top_tables',
  TABLE_DETAILS: '/metadata/api/optimizer/table_details'
};

/**
 *
 * @param {Object} options
 * @param {string} options.sourceType
 * @param {string} options.url
 * @param {boolean} options.refreshCache
 * @param {string} [options.hash] - Optional hash to use as well as the url
 * @param {Function} options.fetchFunction
 * @param {Function} options.successCallback
 * @param {string} [options.cacheType] - Possible values 'default'|'optimizer'. Default value 'default'
 * @param {Object} [options.editor] - Ace editor
 * @param {Object} [options.promise] - Optional promise that will be resolved if cached data exists
 */
const fetchCached = function(options) {
  const self = this;
  const cacheIdentifier = self.getAssistCacheIdentifier(options);
  const cachedData = $.totalStorage(cacheIdentifier) || {};
  const cachedId = options.hash ? options.url + options.hash : options.url;

  if (
    options.refreshCache ||
    typeof cachedData[cachedId] == 'undefined' ||
    self.hasExpired(cachedData[cachedId].timestamp, options.cacheType || 'default')
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
        $.totalStorage(cacheIdentifier, cachedData);
      } catch (e) {}
    });
  } else {
    if (options.promise) {
      options.promise.resolve(cachedData[cachedId].data);
    }

    options.successCallback(cachedData[cachedId].data);
  }
};

/**
 * Fetches the popularity for various aspects of the given tables
 *
 * @param {ApiHelper} apiHelper
 * @param {Object} options
 * @param {boolean} [options.silenceErrors]
 * @param {string[][]} options.paths
 * @param {string} url
 * @return {CancellablePromise}
 */
const genericNavOptMultiTableFetch = function(apiHelper, options, url) {
  const deferred = $.Deferred();

  const dbTables = {};
  options.paths.forEach(path => {
    dbTables[path.join('.')] = true;
  });
  const data = {
    dbTables: ko.mapping.toJSON(Object.keys(dbTables))
  };

  const request = apiHelper.simplePost(url, data, {
    silenceErrors: options.silenceErrors,
    successCallback: function(data) {
      data.hueTimestamp = Date.now();
      deferred.resolve(data);
    },
    errorCallback: deferred.reject
  });

  return new CancellablePromise(deferred, request);
};

/**
 * Wrapper around the response from the Query API
 *
 * @param {string} sourceType
 * @param {Object} response
 *
 * @constructor
 */
class QueryResult {
  constructor(sourceType, compute, response) {
    const self = this;
    self.id = hueUtils.UUID();
    self.type = response.result && response.result.type ? response.result.type : sourceType;
    self.compute = compute;
    self.status = response.status || 'running';
    self.result = response.result || {};
    self.result.type = 'table';
  }
}

class ApiHelper {
  constructor() {
    const self = this;
    self.queueManager = apiQueueManager;

    huePubSub.subscribe('assist.clear.hdfs.cache', () => {
      $.totalStorage(self.getAssistCacheIdentifier({ sourceType: 'hdfs' }), {});
    });

    huePubSub.subscribe('assist.clear.adls.cache', () => {
      $.totalStorage(self.getAssistCacheIdentifier({ sourceType: 'adls' }), {});
    });

    huePubSub.subscribe('assist.clear.git.cache', () => {
      $.totalStorage(self.getAssistCacheIdentifier({ sourceType: 'git' }), {});
    });

    huePubSub.subscribe('assist.clear.s3.cache', () => {
      $.totalStorage(self.getAssistCacheIdentifier({ sourceType: 's3' }), {});
    });

    huePubSub.subscribe('assist.clear.collections.cache', () => {
      $.totalStorage(self.getAssistCacheIdentifier({ sourceType: 'collections' }), {});
    });

    huePubSub.subscribe('assist.clear.hbase.cache', () => {
      $.totalStorage(self.getAssistCacheIdentifier({ sourceType: 'hbase' }), {});
    });

    huePubSub.subscribe('assist.clear.document.cache', () => {
      $.totalStorage(self.getAssistCacheIdentifier({ sourceType: 'document' }), {});
    });

    const clearAllCaches = function() {
      self.clearDbCache({
        sourceType: 'hive',
        clearAll: true
      });
      self.clearDbCache({
        sourceType: 'impala',
        clearAll: true
      });
      $.totalStorage(self.getAssistCacheIdentifier({ sourceType: 'hdfs' }), {});
      $.totalStorage(self.getAssistCacheIdentifier({ sourceType: 'adls' }), {});
      $.totalStorage(self.getAssistCacheIdentifier({ sourceType: 'git' }), {});
      $.totalStorage(self.getAssistCacheIdentifier({ sourceType: 's3' }), {});
      $.totalStorage(self.getAssistCacheIdentifier({ sourceType: 'collections' }), {});
      $.totalStorage(self.getAssistCacheIdentifier({ sourceType: 'hbase' }), {});
      $.totalStorage(self.getAssistCacheIdentifier({ sourceType: 'document' }), {});
    };

    huePubSub.subscribe('assist.clear.all.caches', clearAllCaches);

    if (window.performance && window.performance.navigation) {
      if (window.performance.navigation.type === 1 && location.href.indexOf('/metastore') !== -1) {
        // Browser refresh of the metastore page
        clearAllCaches();
      }
    }
  }

  hasExpired(timestamp, cacheType) {
    if (typeof hueDebug !== 'undefined' && typeof hueDebug.cacheTimeout !== 'undefined') {
      return new Date().getTime() - timestamp > hueDebug.cacheTimeout;
    }
    return new Date().getTime() - timestamp > CACHEABLE_TTL[cacheType];
  }

  /**
   * @param {string} sourceType
   * @returns {string}
   */
  getTotalStorageUserPrefix(sourceType) {
    return sourceType + '_' + window.LOGGED_USERNAME + '_' + window.location.hostname;
  }

  /**
   * @param {object} options
   * @param {string} options.sourceType
   * @param {string} [options.cacheType] - Default value 'default'
   * @returns {string}
   */
  getAssistCacheIdentifier(options) {
    const self = this;
    return (
      'hue.assist.' +
      (options.cacheType || 'default') +
      '.' +
      self.getTotalStorageUserPrefix(options.sourceType)
    );
  }

  /**
   *
   * @param {string} owner - 'assist', 'viewModelA' etc.
   * @param {string} id
   * @param {*} [value] - Optional, undefined and null will remove the value
   */
  setInTotalStorage(owner, id, value) {
    const self = this;
    try {
      const cachedData =
        $.totalStorage('hue.user.settings.' + self.getTotalStorageUserPrefix(owner)) || {};
      if (typeof value !== 'undefined' && value !== null) {
        cachedData[id] = value;
        $.totalStorage('hue.user.settings.' + self.getTotalStorageUserPrefix(owner), cachedData, {
          secure: window.location.protocol.indexOf('https') > -1
        });
      } else if (cachedData[id]) {
        delete cachedData[id];
        $.totalStorage('hue.user.settings.' + self.getTotalStorageUserPrefix(owner), cachedData, {
          secure: window.location.protocol.indexOf('https') > -1
        });
      }
    } catch (e) {}
  }

  /**
   *
   * @param {string} owner - 'assist', 'viewModelA' etc.
   * @param {string} id
   * @param {*} [defaultValue]
   * @returns {*}
   */
  getFromTotalStorage(owner, id, defaultValue) {
    const self = this;
    const cachedData =
      $.totalStorage('hue.user.settings.' + self.getTotalStorageUserPrefix(owner)) || {};
    return typeof cachedData[id] !== 'undefined' ? cachedData[id] : defaultValue;
  }

  /**
   * @param {string} owner - 'assist', 'viewModelA' etc.
   * @param {string} id
   * @param {Observable} observable
   * @param {*} [defaultValue] - Optional default value to use if not in total storage initially
   */
  withTotalStorage(owner, id, observable, defaultValue, noInit) {
    const self = this;

    const cachedValue = self.getFromTotalStorage(owner, id, defaultValue);

    if (!noInit && cachedValue !== 'undefined') {
      observable(cachedValue);
    }

    observable.subscribe(newValue => {
      if (owner === 'assist' && id === 'assist_panel_visible') {
        huePubSub.publish('assist.forceRender');
      }
      self.setInTotalStorage(owner, id, newValue);
    });
    return observable;
  }

  /**
   * @param {Object} [response]
   * @param {number} [response.status]
   * @returns {boolean} - True if actually an error
   */
  successResponseIsError(response) {
    return (
      typeof response !== 'undefined' &&
      (typeof response.traceback !== 'undefined' ||
        (typeof response.status !== 'undefined' && response.status !== 0) ||
        response.code === 503 ||
        response.code === 500)
    );
  }

  /**
   * @param {Object} options
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   * @returns {Function}
   */
  assistErrorCallback(options) {
    return function(errorResponse) {
      let errorMessage = 'Unknown error occurred';
      if (typeof errorResponse !== 'undefined' && errorResponse !== null) {
        if (
          typeof errorResponse.statusText !== 'undefined' &&
          errorResponse.statusText === 'abort'
        ) {
          return;
        } else if (typeof errorResponse.responseText !== 'undefined') {
          try {
            const errorJs = JSON.parse(errorResponse.responseText);
            if (typeof errorJs.message !== 'undefined') {
              errorMessage = errorJs.message;
            } else {
              errorMessage = errorResponse.responseText;
            }
          } catch (err) {
            errorMessage = errorResponse.responseText;
          }
        } else if (typeof errorResponse.message !== 'undefined' && errorResponse.message !== null) {
          errorMessage = errorResponse.message;
        } else if (
          typeof errorResponse.statusText !== 'undefined' &&
          errorResponse.statusText !== null
        ) {
          errorMessage = errorResponse.statusText;
        } else if (
          errorResponse.error !== 'undefined' &&
          Object.prototype.toString.call(errorResponse.error) === '[object String]'
        ) {
          errorMessage = errorResponse.error;
        } else if (Object.prototype.toString.call(errorResponse) === '[object String]') {
          errorMessage = errorResponse;
        }
      }

      if (!options || !options.silenceErrors) {
        hueUtils.logError(errorResponse);
        if (errorMessage && errorMessage.indexOf('AuthorizationException') === -1) {
          $(document).trigger('error', errorMessage);
        }
      }

      if (options && options.errorCallback) {
        options.errorCallback(errorMessage);
      }
      return errorMessage;
    };
  }

  cancelActiveRequest(request) {
    if (typeof request !== 'undefined' && request !== null) {
      const readyState = request.getReadyState ? request.getReadyState() : request.readyState;
      if (readyState < 4) {
        request.abort();
      }
    }
  }

  /**
   * @param {string} url
   * @param {Object} data
   * @param {Object} options
   * @param {function} [options.successCallback]
   * @param {function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   * @param {string} [options.dataType] - Default: Intelligent Guess (xml, json, script, text, html)
   *
   * @return {Promise}
   */
  simplePost(url, data, options) {
    const self = this;
    const deferred = $.Deferred();

    const request = $.post({
      url: url,
      data: data,
      dataType: options && options.dataType
    })
      .done(data => {
        if (self.successResponseIsError(data)) {
          deferred.reject(self.assistErrorCallback(options)(data));
          return;
        }
        if (options && options.successCallback) {
          options.successCallback(data);
        }
        deferred.resolve(data);
      })
      .fail(self.assistErrorCallback(options));

    request.fail(data => {
      deferred.reject(self.assistErrorCallback(options)(data));
    });

    const promise = deferred.promise();

    promise.getReadyState = function() {
      return request.readyState;
    };

    promise.abort = function() {
      request.abort();
    };

    return promise;
  }

  /**
   * @param {Object} data
   * @param {Object} options
   * @param {function} [options.successCallback]
   */
  saveSnippetToFile(data, options) {
    const self = this;
    $.post(
      SAVE_TO_FILE,
      data,
      result => {
        if (typeof options.successCallback !== 'undefined') {
          options.successCallback(result);
        }
      },
      'json'
    ).fail(self.assistErrorCallback(options));
  }

  /**
   * @param {string} url
   * @param {Object} data
   * @param {Object} options
   * @param {function} [options.successCallback]
   * @param {function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   */
  simpleGet(url, data, options) {
    const self = this;
    if (!options) {
      options = {};
    }
    return $.get(url, data, data => {
      if (self.successResponseIsError(data)) {
        self.assistErrorCallback(options)(data);
      } else if (typeof options.successCallback !== 'undefined') {
        options.successCallback(data);
      }
    }).fail(self.assistErrorCallback(options));
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
    const url = TOPO_URL + options.location;
    return this.simpleGet(url, undefined, options);
  }

  /**
   *
   * @param {Object} options
   * @param {string[]} options.path
   * @param {string} options.type - 's3', 'adls' or 'hdfs'
   * @param {number} [options.offset]
   * @param {number} [options.length]
   * @param {boolean} [options.silenceErrors]
   */
  fetchStoragePreview(options) {
    const self = this;
    let url;
    if (options.type === 's3') {
      url = S3_API_PREFIX;
    } else if (options.type === 'adls') {
      url = ADLS_API_PREFIX;
    } else {
      url = HDFS_API_PREFIX;
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
      success: function(data) {
        if (self.successResponseIsError(data)) {
          deferred.reject(self.assistErrorCallback(options)(data));
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
    const self = this;
    if (
      options.pathParts.length > 0 &&
      (options.pathParts[0] === '/' || options.pathParts[0] === '')
    ) {
      options.pathParts.shift();
    }
    let url =
      HDFS_API_PREFIX +
      encodeURI(options.pathParts.join('/')) +
      '?format=json&sortby=name&descending=false&pagesize=' +
      (options.pageSize || 500) +
      '&pagenum=' +
      (options.page || 1);
    if (options.filter) {
      url += '&filter=' + options.filter;
    }
    const fetchFunction = function(storeInCache) {
      if (options.timeout === 0) {
        self.assistErrorCallback(options)({ status: -1 });
        return;
      }
      return $.ajax({
        dataType: 'json',
        url: url,
        timeout: options.timeout,
        success: function(data) {
          if (
            !data.error &&
            !self.successResponseIsError(data) &&
            typeof data.files !== 'undefined' &&
            data.files !== null
          ) {
            if (data.files.length > 2 && !options.filter) {
              storeInCache(data);
            }
            options.successCallback(data);
          } else {
            self.assistErrorCallback(options)(data);
          }
        }
      })
        .fail(self.assistErrorCallback(options))
        .always(() => {
          if (typeof options.editor !== 'undefined' && options.editor !== null) {
            options.editor.hideSpinner();
          }
        });
    };

    return fetchCached.bind(self)(
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
    const self = this;
    options.pathParts.shift();
    let url =
      ADLS_API_PREFIX +
      encodeURI(options.pathParts.join('/')) +
      '?format=json&sortby=name&descending=false&pagesize=' +
      (options.pageSize || 500) +
      '&pagenum=' +
      (options.page || 1);
    if (options.filter) {
      url += '&filter=' + options.filter;
    }
    const fetchFunction = function(storeInCache) {
      if (options.timeout === 0) {
        self.assistErrorCallback(options)({ status: -1 });
        return;
      }
      return $.ajax({
        dataType: 'json',
        url: url,
        timeout: options.timeout,
        success: function(data) {
          if (
            !data.error &&
            !self.successResponseIsError(data) &&
            typeof data.files !== 'undefined' &&
            data.files !== null
          ) {
            if (data.files.length > 2 && !options.filter) {
              storeInCache(data);
            }
            options.successCallback(data);
          } else {
            self.assistErrorCallback(options)(data);
          }
        }
      })
        .fail(self.assistErrorCallback(options))
        .always(() => {
          if (typeof options.editor !== 'undefined' && options.editor !== null) {
            options.editor.hideSpinner();
          }
        });
    };

    return fetchCached.bind(self)(
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
   *
   * @param {string[]} options.pathParts
   * @param {string} options.fileType
   */
  fetchGitContents(options) {
    const self = this;
    const url =
      GIT_API_PREFIX +
      '?path=' +
      encodeURI(options.pathParts.join('/')) +
      '&fileType=' +
      options.fileType;
    const fetchFunction = function(storeInCache) {
      if (options.timeout === 0) {
        self.assistErrorCallback(options)({ status: -1 });
        return;
      }
      $.ajax({
        dataType: 'json',
        url: url,
        timeout: options.timeout,
        success: function(data) {
          if (!data.error && !self.successResponseIsError(data)) {
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
            self.assistErrorCallback(options)(data);
          }
        }
      }).fail(self.assistErrorCallback(options));
    };

    fetchCached.bind(self)(
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
    const self = this;
    options.pathParts.shift(); // remove the trailing /
    let url =
      S3_API_PREFIX +
      encodeURI(options.pathParts.join('/')) +
      '?format=json&sortby=name&descending=false&pagesize=' +
      (options.pageSize || 500) +
      '&pagenum=' +
      (options.page || 1);
    if (options.filter) {
      url += '&filter=' + options.filter;
    }
    const fetchFunction = function(storeInCache) {
      if (options.timeout === 0) {
        self.assistErrorCallback(options)({ status: -1 });
        return;
      }

      $.ajax({
        dataType: 'json',
        url: url,
        timeout: options.timeout,
        success: function(data) {
          if (
            !data.error &&
            !self.successResponseIsError(data) &&
            typeof data.files !== 'undefined' &&
            data.files !== null
          ) {
            if (data.files.length > 2 && !options.filter) {
              storeInCache(data);
            }
            options.successCallback(data);
          } else {
            self.assistErrorCallback(options)(data);
          }
        }
      })
        .fail(self.assistErrorCallback(options))
        .always(() => {
          if (typeof options.editor !== 'undefined' && options.editor !== null) {
            options.editor.hideSpinner();
          }
        });
    };

    fetchCached.bind(self)(
      $.extend({}, options, {
        sourceType: 's3',
        url: url,
        fetchFunction: fetchFunction
      })
    );
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
    const self = this;
    if (options.timeout === 0) {
      self.assistErrorCallback(options)({ status: -1 });
      return;
    }
    $.ajax({
      dataType: 'json',
      url: DASHBOARD_TERMS_API,
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
      success: function(data) {
        if (!data.error && !self.successResponseIsError(data) && data.status === 0) {
          options.successCallback(data);
        } else {
          self.assistErrorCallback(options)(data);
        }
      }
    })
      .fail(self.assistErrorCallback(options))
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
    const self = this;
    if (options.timeout === 0) {
      self.assistErrorCallback(options)({ status: -1 });
      return;
    }
    $.ajax({
      dataType: 'json',
      url: DASHBOARD_STATS_API,
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
      success: function(data) {
        if (!data.error && !self.successResponseIsError(data) && data.status === 0) {
          options.successCallback(data);
        } else if (data.status === 1) {
          options.notSupportedCallback(data);
        } else {
          self.assistErrorCallback(options)(data);
        }
      }
    })
      .fail(self.assistErrorCallback(options))
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
    const self = this;
    let suffix = 'getClusters';
    if (options.parent.name !== '') {
      suffix = 'getTableList/' + options.parent.name;
    }
    const url = HBASE_API_PREFIX + suffix;
    const fetchFunction = function(storeInCache) {
      if (options.timeout === 0) {
        self.assistErrorCallback(options)({ status: -1 });
        return;
      }
      $.ajax({
        dataType: 'json',
        url: url,
        timeout: options.timeout,
        success: function(data) {
          if (!data.error && !self.successResponseIsError(data)) {
            storeInCache(data);
            options.successCallback(data);
          } else {
            self.assistErrorCallback(options)(data);
          }
        }
      })
        .fail(self.assistErrorCallback(options))
        .always(() => {
          if (typeof options.editor !== 'undefined' && options.editor !== null) {
            options.editor.hideSpinner();
          }
        });
    };

    fetchCached.bind(self)(
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
    const self = this;

    const queryMetric = function(metricName) {
      const now = Date.now();
      return self.simplePost('/metadata/api/prometheus/query', {
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
      .done(function() {
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
    const self = this;
    self.simpleGet(CONFIG_APPS_API, {}, options);
  }

  saveGlobalConfiguration(options) {
    const self = this;
    self.simplePost(
      CONFIG_APPS_API,
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
    const self = this;
    self.simplePost(
      CONFIG_SAVE_API,
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
    const self = this;

    let id = '';
    if (options.uuid) {
      id += options.uuid;
    }
    if (options.type && options.type !== 'all') {
      id += options.type;
    }

    let promise = self.queueManager.getQueued(DOCUMENTS_API, id);
    const firstInQueue = typeof promise === 'undefined';
    if (firstInQueue) {
      promise = $.Deferred();
      self.queueManager.addToQueue(promise, DOCUMENTS_API, id);
    }

    promise.done(options.successCallback).fail(self.assistErrorCallback(options));

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
      url: DOCUMENTS_API,
      data: data,
      traditional: true,
      success: function(data) {
        if (!self.successResponseIsError(data)) {
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
    const self = this;
    return $.ajax({
      url: DOCUMENTS_SEARCH_API,
      data: {
        uuid: options.uuid,
        text: options.query,
        type: options.type,
        page: options.page,
        limit: options.limit,
        include_trashed: options.include_trashed
      },
      success: function(data) {
        if (!self.successResponseIsError(data)) {
          options.successCallback(data);
        } else {
          self.assistErrorCallback(options)(data);
        }
      }
    }).fail(self.assistErrorCallback(options));
  }

  /**
   * @param {Object} options
   * @param {number} options.uuid
   * @param {boolean} [options.silenceErrors]
   * @param {boolean} [options.fetchContents]
   *
   * @return {CancellablePromise}
   */
  fetchDocument(options) {
    const self = this;
    const deferred = $.Deferred();
    const request = $.ajax({
      url: DOCUMENTS_API,
      data: {
        uuid: options.uuid,
        data: !!options.fetchContents
      },
      success: function(data) {
        if (!self.successResponseIsError(data)) {
          deferred.resolve(data);
        } else {
          deferred.reject(
            self.assistErrorCallback({
              silenceErrors: options.silenceErrors
            })
          );
        }
      }
    }).fail(
      self.assistErrorCallback({
        silenceErrors: options.silenceErrors,
        errorCallback: deferred.reject
      })
    );
    return new CancellablePromise(deferred, request);
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
    const self = this;
    self.simplePost(
      DOCUMENTS_API + 'mkdir',
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
    const self = this;
    self.simplePost(
      DOCUMENTS_API + 'update',
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
    const self = this;
    $.ajax({
      url: DOCUMENTS_API + 'import',
      type: 'POST',
      success: function(data) {
        if (!self.successResponseIsError(data)) {
          options.successCallback(data);
        } else {
          self.assistErrorCallback(options)(data);
        }
      },
      xhr: function() {
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
    }).fail(self.assistErrorCallback(options));
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
    const self = this;
    self.simplePost(
      DOCUMENTS_API + 'move',
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
    const self = this;
    self.simplePost(
      DOCUMENTS_API + 'delete',
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
    const self = this;
    self.simplePost(
      DOCUMENTS_API + 'copy',
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
    const self = this;
    self.simplePost(
      DOCUMENTS_API + 'restore',
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
   * @param {string} [options.cacheType] - Possible values 'default', 'optimizer. Default value 'default'
   * @param {string[]} [options.fields]
   * @param {boolean} [options.clearAll]
   */
  clearDbCache(options) {
    const self = this;
    const cacheIdentifier = self.getAssistCacheIdentifier(options);
    if (options.clearAll) {
      $.totalStorage(cacheIdentifier, {});
    } else {
      let url = AUTOCOMPLETE_API_PREFIX;
      if (options.databaseName) {
        url += options.databaseName;
      }
      if (options.tableName) {
        url += '/' + options.tableName;
      }
      if (options.fields) {
        url += options.fields.length > 0 ? '/' + options.fields.join('/') : '';
      }
      const cachedData = $.totalStorage(cacheIdentifier) || {};
      delete cachedData[url];
      $.totalStorage(cacheIdentifier, cachedData);
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
    const self = this;
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

      const request = self
        .simplePost(IMPALA_INVALIDATE_API, data, options)
        .done(deferred.resolve)
        .fail(deferred.reject);

      return new CancellablePromise(deferred, request);
    }

    return deferred.resolve().promise();
  }

  /**
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {ContextCompute} options.compute
   * @param {boolean} [options.silenceErrors]
   * @param {number} [options.timeout]
   *
   * @param {string[]} [options.path] - The path to fetch
   *
   * @return {CancellablePromise}
   */
  fetchSourceMetadata(options) {
    const self = this;
    const deferred = $.Deferred();

    const isQuery = options.sourceType.indexOf('-query') !== -1;
    const sourceType = isQuery ? options.sourceType.replace('-query', '') : options.sourceType;

    const request = $.ajax({
      type: 'POST',
      url: AUTOCOMPLETE_API_PREFIX + (isQuery ? options.path.slice(1) : options.path).join('/'),
      data: {
        notebook: {},
        snippet: ko.mapping.toJSON({
          type: sourceType,
          source: isQuery ? 'query' : 'data'
        }),
        cluster: ko.mapping.toJSON(options.compute ? options.compute : '""')
      },
      timeout: options.timeout
    })
      .done(data => {
        data.notFound =
          data.status === 0 &&
          data.code === 500 &&
          data.error &&
          (data.error.indexOf('Error 10001') !== -1 ||
            data.error.indexOf('AnalysisException') !== -1);
        data.hueTimestamp = Date.now();

        // TODO: Display warning in autocomplete when an entity can't be found
        // Hive example: data.error: [...] SemanticException [Error 10001]: Table not found default.foo
        // Impala example: data.error: [...] AnalysisException: Could not resolve path: 'default.foo'
        if (!data.notFound && self.successResponseIsError(data)) {
          self.assistErrorCallback({
            silenceErrors: options.silenceErrors,
            errorCallback: deferred.reject
          })(data);
        } else {
          deferred.resolve(data);
        }
      })
      .fail(
        self.assistErrorCallback({
          silenceErrors: options.silenceErrors,
          errorCallback: deferred.reject
        })
      );

    return new CancellablePromise(deferred, request);
  }

  updateSourceMetadata(options) {
    const self = this;
    let url;
    const data = {
      source_type: options.sourceType
    };
    if (options.path.length === 1) {
      url = '/metastore/databases/' + options.path[0] + '/alter';
      data.properties = ko.mapping.toJSON(options.properties);
    } else if (options.path.length === 2) {
      url = '/metastore/table/' + options.path[0] + '/' + options.path[1] + '/alter';
      if (options.properties) {
        if (options.properties.comment) {
          data.comment = options.properties.comment;
        }
        if (options.properties.name) {
          data.new_table_name = options.properties.name;
        }
      }
    } else if (options.path > 2) {
      url = '/metastore/table/' + options.path[0] + '/' + options.path[1] + '/alter_column';
      data.column = options.path.slice(2).join('.');
      if (options.properties) {
        if (options.properties.comment) {
          data.comment = options.properties.comment;
        }
        if (options.properties.name) {
          data.new_column_name = options.properties.name;
        }
        if (options.properties.type) {
          data.new_column_type = options.properties.name;
        }
        if (options.properties.partitions) {
          data.partition_spec = ko.mapping.toJSON(options.properties.partitions);
        }
      }
    }
    return self.simplePost(url, data, options);
  }

  /**
   * Fetches the analysis for the given source and path
   *
   * @param {Object} options
   * @param {boolean} [options.silenceErrors]
   *
   * @param {ContextCompute} options.compute
   * @param {string} options.sourceType
   * @param {string[]} options.path
   *
   * @return {CancellablePromise}
   */
  fetchAnalysis(options) {
    const self = this;
    const deferred = $.Deferred();

    let url = '/notebook/api/describe/' + options.path[0];

    if (options.path.length > 1) {
      url += '/' + options.path[1] + '/';
    }

    if (options.path.length > 2) {
      url += 'stats/' + options.path.slice(2).join('/');
    }

    const data = {
      format: 'json',
      cluster: JSON.stringify(options.compute),
      source_type: options.sourceType
    };

    const request = self['simplePost'](url, data, {
      silenceErrors: options.silenceErrors,
      successCallback: function(response) {
        if (options.path.length === 1) {
          if (response.data) {
            response.data.hueTimestamp = Date.now();
            deferred.resolve(response.data);
          } else {
            deferred.reject();
          }
        } else {
          deferred.resolve(response);
        }
      },
      errorCallback: deferred.reject
    });

    return new CancellablePromise(deferred, request);
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
   * @return {CancellablePromise}
   */
  fetchPartitions(options) {
    const self = this;
    const deferred = $.Deferred();

    // TODO: No sourceType needed?
    const request = $.post('/metastore/table/' + options.path.join('/') + '/partitions', {
      format: 'json',
      cluster: JSON.stringify(options.compute)
    })
      .done(response => {
        if (!self.successResponseIsError(response)) {
          if (!response) {
            response = {};
          }
          response.hueTimestamp = Date.now();
          deferred.resolve(response);
        } else {
          self.assistErrorCallback({
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
          self.assistErrorCallback({
            silenceErrors: options.silenceErrors,
            errorCallback: deferred.reject
          })(response);
        }
      });

    return new CancellablePromise(deferred, request);
  }

  /**
   * Refreshes the analysis for the given source and path
   *
   * @param {Object} options
   * @param {boolean} [options.silenceErrors]
   *
   * @param {string} options.sourceType
   * @param {ContextCompute} options.compute
   * @param {string[]} options.path
   *
   * @return {CancellablePromise}
   */
  refreshAnalysis(options) {
    const self = this;

    if (options.path.length === 1) {
      return self.fetchAnalysis(options);
    }
    const deferred = $.Deferred();

    const promises = [];

    const pollForAnalysis = (url, delay) => {
      window.setTimeout(() => {
        promises.push(
          self.simplePost(url, undefined, {
            silenceErrors: options.silenceErrors,
            successCallback: function(data) {
              promises.pop();
              if (data.isSuccess) {
                promises.push(
                  self
                    .fetchAnalysis(options)
                    .done(deferred.resolve)
                    .fail(deferred.reject)
                );
              } else if (data.isFailure) {
                deferred.reject(data);
              } else {
                pollForAnalysis(url, 1000);
              }
            },
            errorCallback: deferred.reject
          })
        );
      }, delay);
    };

    const url =
      '/' +
      (options.sourceType === 'hive' ? 'beeswax' : options.sourceType) +
      '/api/analyze/' +
      options.path.join('/') +
      '/';

    promises.push(
      self.simplePost(url, undefined, {
        silenceErrors: options.silenceErrors,
        successCallback: function(data) {
          promises.pop();
          if (data.status === 0 && data.watch_url) {
            pollForAnalysis(data.watch_url, 500);
          } else {
            deferred.reject();
          }
        },
        errorCallback: deferred.reject
      })
    );

    return new CancellablePromise(deferred, undefined, promises);
  }

  /**
   * Checks the status for the given snippet ID
   * Note: similar to notebook and search check_status.
   *
   * @param {Object} options
   * @param {Object} options.notebookJson
   * @param {Object} options.snippetJson
   * @param {boolean} [options.silenceErrors]
   *
   * @return {CancellablePromise}
   */
  whenAvailable(options) {
    const self = this;
    const deferred = $.Deferred();
    const cancellablePromises = [];

    let waitTimeout = -1;

    deferred.fail(() => {
      window.clearTimeout(waitTimeout);
    });

    const waitForAvailable = () => {
      const request = self
        .simplePost(
          '/notebook/api/check_status',
          {
            notebook: options.notebookJson,
            snippet: options.snippetJson,
            cluster: ko.mapping.toJSON(options.compute ? options.compute : '""')
          },
          {
            silenceErrors: options.silenceErrors
          }
        )
        .done(response => {
          if (response && response.query_status && response.query_status.status) {
            const status = response.query_status.status;
            if (status === 'available') {
              deferred.resolve();
            } else if (status === 'running' || status === 'starting' || status === 'waiting') {
              waitTimeout = window.setTimeout(() => {
                waitForAvailable();
              }, 500);
            } else {
              deferred.reject();
            }
          }
        })
        .fail(deferred.reject);

      cancellablePromises.push(new CancellablePromise(request, request));
    };

    waitForAvailable();
    return new CancellablePromise(deferred, undefined, cancellablePromises);
  }

  /**
   *
   * @param {ExecutableStatement} executable
   *
   * @return {{snippet: string, notebook: string}}
   */
  static adaptExecutableToNotebook(executable) {
    const statement = executable.getStatement();
    const snippet = {
      type: executable.sourceType,
      result: {
        handle: executable.handle
      },
      status: executable.status,
      id: executable.snippetId || hueUtils.UUID(),
      statement_raw: statement,
      statement: statement,
      variables: [],
      compute: executable.compute,
      database: executable.database,
      properties: { settings: [] }
    };

    const notebook = {
      type: executable.sourceType,
      snippets: [snippet],
      id: executable.notebookId,
      name: '',
      isSaved: false,
      sessions: executable.sessions || []
    };

    return {
      snippet: JSON.stringify(snippet),
      notebook: JSON.stringify(notebook)
    };
  }

  /**
   * @typedef {Object} ExecutionHandle
   * @property {string} guid
   * @property {boolean} has_more_statements
   * @property {boolean} has_result_set
   * @property {Object} log_context
   * @property {number} modified_row_count
   * @property {number} operation_type
   * @property {string} previous_statement_hash
   * @property {string} secret
   * @property {string} session_guid
   * @property {string} statement
   * @property {number} statement_id
   * @property {number} statements_count
   */

  /**
   * API function to execute an ExecutableStatement
   *
   * @param {Object} options
   * @param {boolean} [options.silenceErrors]
   * @param {ExecutableStatement} options.executable
   *
   * @return {Promise<ExecutionHandle>}
   */
  executeStatement(options) {
    const executable = options.executable;
    const url = EXECUTE_API_PREFIX + executable.sourceType;
    const deferred = $.Deferred();

    this.simplePost(url, ApiHelper.adaptExecutableToNotebook(executable), options)
      .done(response => {
        if (response.handle) {
          deferred.resolve(response.handle);
        } else {
          deferred.reject('No handle in execute response');
        }
      })
      .fail(deferred.reject);

    const promise = deferred.promise();

    promise.cancel = () => {
      const cancelDeferred = $.Deferred();
      deferred
        .done(handle => {
          if (options.executable.handle !== handle) {
            options.executable.handle = handle;
          }
          this.cancelStatement(options).always(cancelDeferred.resolve);
        })
        .fail(cancelDeferred.resolve);
      return cancelDeferred;
    };

    return promise;
  }

  /**
   *
   * @param {Object} options
   * @param {boolean} [options.silenceErrors]
   * @param {ExecutableStatement} options.executable
   *
   * @return {CancellablePromise<string>}
   */
  checkExecutionStatus(options) {
    const deferred = $.Deferred();

    const request = this.simplePost(
      '/notebook/api/check_status',
      ApiHelper.adaptExecutableToNotebook(options.executable),
      options
    )
      .done(response => {
        deferred.resolve(response.query_status.status);
      })
      .fail(deferred.reject);

    return new CancellablePromise(deferred, request);
  }

  /**
   *
   * @param {Object} options
   * @param {boolean} [options.silenceErrors]
   * @param {ExecutableStatement} options.executable
   *
   * @return {Promise}
   */
  cancelStatement(options) {
    return this.simplePost(
      '/notebook/api/cancel_statement',
      ApiHelper.adaptExecutableToNotebook(options.executable),
      options
    );
  }

  /**
   * @typedef {Object} ResultResponseMeta
   * @property {string} comment
   * @property {string} name
   * @property {string} type
   */

  /**
   * @typedef {Object} ResultResponse
   * @property {Object[]} data
   * @property {boolean} has_more
   * @property {boolean} isEscaped
   * @property {ResultResponseMeta[]} meta
   * @property {string} type
   */

  /**
   *
   * @param {Object} options
   * @param {boolean} [options.silenceErrors]
   * @param {ExecutableStatement} options.executable
   * @param {number} options.rows
   * @param {boolean} options.startOver
   *
   * @return {Promise<ResultResponse>}
   */
  async fetchResults(options) {
    return new Promise((resolve, reject) => {
      const data = ApiHelper.adaptExecutableToNotebook(options.executable);
      data.rows = options.rows;
      data.startOver = !!options.startOver;

      this.simplePost(
        '/notebook/api/fetch_result_data',
        data,
        {
          silenceErrors: options.silenceErrors,
          dataType: 'text'
        },
        options
      )
        .done(response => {
          const data = JSON.bigdataParse(response);
          resolve(data.result);
        })
        .fail(reject);
    });
  }

  /**
   *
   * @param {Object} options
   * @param {boolean} [options.silenceErrors]
   * @param {ExecutableStatement} options.executable
   *
   * @return {Promise<ResultResponse>}
   */
  async fetchResultSize(options) {
    return new Promise((resolve, reject) => {
      this.simplePost(
        '/notebook/api/fetch_result_size',
        ApiHelper.adaptExecutableToNotebook(options.executable),
        options
      )
        .done(response => {
          resolve(response.result);
        })
        .fail(reject);
    });
  }

  /**
   *
   * @param {Object} options
   * @param {boolean} [options.silenceErrors]
   * @param {ExecutableStatement} options.executable
   *
   * @return {Promise}
   */
  closeStatement(options) {
    const executable = options.executable;

    return this.simplePost(
      '/notebook/api/close_statement',
      ApiHelper.adaptExecutableToNotebook({
        sourceType: executable.sourceType,
        handle: executable.handle
      }),
      options
    );
  }

  /**
   * Fetches samples for the given source and path
   *
   * @param {Object} options
   * @param {boolean} [options.silenceErrors]
   *
   * @param {string} options.sourceType
   * @param {ContextCompute} options.compute
   * @param {number} [options.sampleCount] - Default 100
   * @param {string[]} options.path
   * @param {string} [options.operation] - Default 'default'
   *
   * @return {CancellablePromise}
   */
  fetchSample(options) {
    const self = this;
    const deferred = $.Deferred();

    const cancellablePromises = [];

    let notebookJson = null;
    let snippetJson = null;

    const cancelQuery = function() {
      if (notebookJson) {
        self.simplePost(
          '/notebook/api/cancel_statement',
          {
            notebook: notebookJson,
            snippet: snippetJson,
            cluster: ko.mapping.toJSON(options.compute ? options.compute : '""')
          },
          { silenceErrors: options.silenceErrors }
        );
      }
    };

    self
      .simplePost(
        SAMPLE_API_PREFIX + options.path.join('/'),
        {
          notebook: {},
          snippet: JSON.stringify({
            type: options.sourceType,
            compute: options.compute
          }),
          async: true,
          operation: '"' + (options.operation || 'default') + '"',
          cluster: ko.mapping.toJSON(options.compute ? options.compute : '""')
        },
        {
          silenceErrors: options.silenceErrors
        }
      )
      .done(sampleResponse => {
        const queryResult = new QueryResult(options.sourceType, options.compute, sampleResponse);

        notebookJson = JSON.stringify({ type: options.sourceType });
        snippetJson = JSON.stringify(queryResult);

        if (sampleResponse && sampleResponse.rows) {
          // Sync results
          const data = { data: sampleResponse.rows, meta: sampleResponse.full_headers };
          data.hueTimestamp = Date.now();
          deferred.resolve(data);
        } else {
          cancellablePromises.push(
            self
              .whenAvailable({
                notebookJson: notebookJson,
                snippetJson: snippetJson,
                compute: options.compute,
                silenceErrors: options.silenceErrors
              })
              .done(() => {
                const resultRequest = self
                  .simplePost(
                    '/notebook/api/fetch_result_data',
                    {
                      notebook: notebookJson,
                      snippet: snippetJson,
                      rows: options.sampleCount || 100,
                      startOver: 'false'
                    },
                    {
                      silenceErrors: options.silenceErrors
                    }
                  )
                  .done(sampleResponse => {
                    const data = (sampleResponse && sampleResponse.result) || {
                      data: [],
                      meta: []
                    };
                    data.hueTimestamp = Date.now();
                    deferred.resolve(data);
                  })
                  .fail(deferred.reject);

                cancellablePromises.push(resultRequest, resultRequest);
              })
              .fail(deferred.reject)
          );
        }
      })
      .fail(deferred.reject);

    cancellablePromises.push({
      cancel: cancelQuery
    });

    return new CancellablePromise(deferred, undefined, cancellablePromises);
  }

  /**
   * Fetches a navigator entity for the given source and path
   *
   * @param {Object} options
   * @param {boolean} [options.silenceErrors]
   *
   * @param {boolean} [options.isView] - Default false
   * @param {string[]} options.path
   *
   * @return {CancellablePromise}
   */
  fetchNavigatorMetadata(options) {
    const self = this;
    const deferred = $.Deferred();
    let url = NAV_URLS.FIND_ENTITY;

    if (options.path.length === 1) {
      url += '?type=database&name=' + options.path[0];
    } else if (options.path.length === 2) {
      url +=
        (options.isView ? '?type=view' : '?type=table') +
        '&database=' +
        options.path[0] +
        '&name=' +
        options.path[1];
    } else if (options.path.length === 3) {
      url +=
        '?type=field&database=' +
        options.path[0] +
        '&table=' +
        options.path[1] +
        '&name=' +
        options.path[2];
    } else {
      return new CancellablePromise($.Deferred().reject());
    }

    const request = self.simplePost(
      url,
      {
        notebook: {},
        snippet: ko.mapping.toJSON({
          type: 'nav'
        })
      },
      {
        silenceErrors: options.silenceErrors,
        successCallback: function(data) {
          data = data.entity || data;
          data.hueTimestamp = Date.now();
          deferred.resolve(data);
        },
        errorCallback: deferred.reject
      }
    );

    return new CancellablePromise(deferred, request);
  }

  /**
   * Updates Navigator properties and custom metadata for the given entity
   *
   * @param {Object} options
   * @param {string} options.identity - The identifier for the Navigator entity to update
   * @param {Object} [options.properties]
   * @param {Object} [options.modifiedCustomMetadata]
   * @param {string[]} [options.deletedCustomMetadataKeys]
   * @param {boolean} [options.silenceErrors]
   *
   * @return {Promise}
   */
  updateNavigatorProperties(options) {
    const self = this;
    const data = { id: ko.mapping.toJSON(options.identity) };

    if (options.properties) {
      data.properties = ko.mapping.toJSON(options.properties);
    }
    if (options.modifiedCustomMetadata) {
      data.modifiedCustomMetadata = ko.mapping.toJSON(options.modifiedCustomMetadata);
    }
    if (options.deletedCustomMetadataKeys) {
      data.deletedCustomMetadataKeys = ko.mapping.toJSON(options.deletedCustomMetadataKeys);
    }
    return self.simplePost(NAV_URLS.UPDATE_PROPERTIES, data, options);
  }

  /**
   * Lists all available navigator tags
   *
   * @param {Object} options
   * @param {boolean} [options.silenceErrors]
   *
   * @return {CancellablePromise}
   */
  fetchAllNavigatorTags(options) {
    const self = this;

    const deferred = $.Deferred();

    const request = self.simplePost(NAV_URLS.LIST_TAGS, undefined, {
      silenceErrors: options.silenceErrors,
      successCallback: function(data) {
        if (data && data.tags) {
          deferred.resolve(data.tags);
        } else {
          deferred.resolve({});
        }
      },
      errorCallback: deferred.reject
    });

    return new CancellablePromise(deferred, request);
  }

  addNavTags(entityId, tags) {
    const self = this;
    return self.simplePost(NAV_URLS.ADD_TAGS, {
      id: ko.mapping.toJSON(entityId),
      tags: ko.mapping.toJSON(tags)
    });
  }

  deleteNavTags(entityId, tags) {
    const self = this;
    return self.simplePost(NAV_URLS.DELETE_TAGS, {
      id: ko.mapping.toJSON(entityId),
      tags: ko.mapping.toJSON(tags)
    });
  }

  /**
   * Fetches navOpt popularity for the children of the given path
   *
   * @param {Object} options
   * @param {boolean} [options.silenceErrors]
   * @param {string[][]} options.paths
   * @return {CancellablePromise}
   */
  fetchNavOptPopularity(options) {
    const self = this;
    const deferred = $.Deferred();
    let url, data;

    if (options.paths.length === 1 && options.paths[0].length === 1) {
      url = NAV_OPT_URLS.TOP_TABLES;
      data = {
        database: options.paths[0][0]
      };
    } else {
      url = NAV_OPT_URLS.TOP_COLUMNS;
      const dbTables = [];
      options.paths.forEach(path => {
        dbTables.push(path.join('.'));
      });
      data = {
        dbTables: ko.mapping.toJSON(dbTables)
      };
    }

    const request = self.simplePost(url, data, {
      silenceErrors: options.silenceErrors,
      successCallback: function(data) {
        data.hueTimestamp = Date.now();
        deferred.resolve(data);
      },
      errorCallback: deferred.reject
    });

    return new CancellablePromise(deferred, request);
  }

  /**
   * Fetches the popular aggregate functions for the given tables
   *
   * @param {Object} options
   * @param {boolean} [options.silenceErrors]
   * @param {string[][]} options.paths
   * @return {CancellablePromise}
   */
  fetchNavOptTopAggs(options) {
    return genericNavOptMultiTableFetch(this, options, NAV_OPT_URLS.TOP_AGGS);
  }

  /**
   * Fetches the popular columns for the given tables
   *
   * @param {Object} options
   * @param {boolean} [options.silenceErrors]
   * @param {string[][]} options.paths
   * @return {CancellablePromise}
   */
  fetchNavOptTopColumns(options) {
    return genericNavOptMultiTableFetch(this, options, NAV_OPT_URLS.TOP_COLUMNS);
  }

  /**
   * Fetches the popular filters for the given tables
   *
   * @param {Object} options
   * @param {boolean} [options.silenceErrors]
   * @param {string[][]} options.paths
   * @return {CancellablePromise}
   */
  fetchNavOptTopFilters(options) {
    return genericNavOptMultiTableFetch(this, options, NAV_OPT_URLS.TOP_FILTERS);
  }

  /**
   * Fetches the popular joins for the given tables
   *
   * @param {Object} options
   * @param {boolean} [options.silenceErrors]
   * @param {string[][]} options.paths
   * @return {CancellablePromise}
   */
  fetchNavOptTopJoins(options) {
    return genericNavOptMultiTableFetch(this, options, NAV_OPT_URLS.TOP_JOINS);
  }

  /**
   * Fetches navOpt meta for the given path, only possible for tables atm.
   *
   * @param {Object} options
   * @param {boolean} [options.silenceErrors]
   * @param {string[]} options.path
   *
   * @return {CancellablePromise}
   */
  fetchNavOptMeta(options) {
    const self = this;
    const deferred = $.Deferred();

    const request = self.simplePost(
      NAV_OPT_URLS.TABLE_DETAILS,
      {
        databaseName: options.path[0],
        tableName: options.path[1]
      },
      {
        silenceErrors: options.silenceErrors,
        successCallback: function(response) {
          if (response.status === 0 && response.details) {
            response.details.hueTimestamp = Date.now();
            deferred.resolve(response.details);
          } else {
            deferred.reject();
          }
        },
        errorCallback: deferred.reject
      }
    );

    return new CancellablePromise(deferred, request);
  }

  /**
   * @param {Object} options
   * @param {boolean} [options.silenceErrors]
   * @param {ContextCompute} options.compute
   * @param {string} options.queryId
   * @return {CancellablePromise}
   */
  fetchQueryExecutionAnalysis(options) {
    const self = this;
    //var url = '/metadata/api/workload_analytics/get_impala_query/';
    const url = '/impala/api/query/alanize';
    const deferred = $.Deferred();

    let tries = 0;

    const cancellablePromises = [];

    const promise = new CancellablePromise(deferred, undefined, cancellablePromises);

    const pollForAnalysis = () => {
      if (tries === 10) {
        deferred.reject();
        return;
      }
      tries++;
      cancellablePromises.pop(); // Remove the last one
      cancellablePromises.push(
        deferred,
        self
          .simplePost(
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
    const self = this;
    const url = '/impala/api/query/alanize/fix';
    const deferred = $.Deferred();

    const request = self.simplePost(
      url,
      {
        cluster: JSON.stringify(options.compute),
        fix: JSON.stringify(options.fix),
        start_time: options.start_time
      },
      {
        silenceErrors: options.silenceErrors,
        successCallback: function(response) {
          if (response.status === 0) {
            deferred.resolve(response.details);
          } else {
            deferred.reject();
          }
        },
        errorCallback: deferred.reject
      }
    );

    return new CancellablePromise(deferred, request);
  }

  fetchQueryExecutionStatistics(options) {
    const self = this;
    const url = '/impala/api/query/alanize/metrics';
    const deferred = $.Deferred();

    const request = self.simplePost(
      url,
      {
        cluster: JSON.stringify(options.cluster),
        query_id: '"' + options.queryId + '"'
      },
      {
        silenceErrors: options.silenceErrors,
        successCallback: function(response) {
          if (response.status === 0) {
            deferred.resolve(response.data);
          } else {
            deferred.reject();
          }
        },
        errorCallback: deferred.reject
      }
    );

    return new CancellablePromise(deferred, request);
  }

  /**
   * @param {Object} options
   * @param {boolean} [options.silenceErrors]
   * @param {string} options.sourceType
   * @return {Promise}
   */
  fetchContextNamespaces(options) {
    const self = this;
    const url = '/desktop/api2/context/namespaces/' + options.sourceType;
    return self.simpleGet(url, undefined, options);
  }

  /**
   * @param {Object} options
   * @param {boolean} [options.silenceErrors]
   * @param {string} options.sourceType
   * @return {Promise}
   */
  fetchContextComputes(options) {
    const self = this;
    const url = '/desktop/api2/context/computes/' + options.sourceType;
    return self.simpleGet(url, undefined, options);
  }

  /**
   * @param {Object} options
   * @param {boolean} [options.silenceErrors]
   * @param {string} options.sourceType
   * @return {Promise}
   */
  fetchContextClusters(options) {
    const self = this;
    const url = '/desktop/api2/context/clusters/' + options.sourceType;
    return self.simpleGet(url, undefined, options);
  }

  getClusterConfig(data) {
    return $.post(FETCH_CONFIG, data);
  }

  fetchHueDocsInteractive(query) {
    const deferred = $.Deferred();
    const request = $.post(INTERACTIVE_SEARCH_API, {
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
    return new CancellablePromise(deferred, request);
  }

  fetchNavEntitiesInteractive(options) {
    const deferred = $.Deferred();
    const request = $.post(INTERACTIVE_SEARCH_API, {
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
    return new CancellablePromise(deferred, request);
  }

  searchEntities(options) {
    const self = this;
    const deferred = $.Deferred();

    const request = self.simplePost(
      SEARCH_API,
      {
        query_s: ko.mapping.toJSON(options.query),
        limit: options.limit || 100,
        raw_query: !!options.rawQuery,
        sources: options.sources ? ko.mapping.toJSON(options.sources) : '["sql"]'
      },
      {
        silenceErrors: options.silenceErrors,
        successCallback: deferred.resolve,
        errorCallback: deferred.reject
      }
    );

    return new CancellablePromise(deferred, request);
  }

  /**
   *
   * @param {Object} options
   * @param {string} options.statements
   * @param {boolean} [options.silenceErrors]
   */
  formatSql(options) {
    const self = this;
    const deferred = $.Deferred();

    const request = self.simplePost(
      FORMAT_SQL_API,
      {
        statements: options.statements
      },
      {
        silenceErrors: options.silenceErrors,
        successCallback: deferred.resolve,
        errorCallback: deferred.reject
      }
    );

    return new CancellablePromise(deferred, request);
  }
}

const apiHelper = new ApiHelper();

export default apiHelper;

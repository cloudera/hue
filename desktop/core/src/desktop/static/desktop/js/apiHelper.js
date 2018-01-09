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

var ApiQueueManager = (function () {

  var instance = null;

  function ApiQueueManager() {
    var self = this;
    self.callQueue = {};
  }

  ApiQueueManager.prototype.getQueued = function (url, hash) {
    var self = this;
    return self.callQueue[url + (hash || '')];
  };

  ApiQueueManager.prototype.addToQueue = function (promise, url, hash) {
    var self = this;
    self.callQueue[url + (hash || '')] = promise;
    promise.always(function () {
      delete self.callQueue[url + (hash || '')];
    })
  };

  return {
    /**
     * @returns {ApiQueueManager}
     */
    getInstance: function () {
      if (instance === null) {
        instance = new ApiQueueManager();
      }
      return instance;
    }
  };
})();

var ApiHelper = (function () {

  var AUTOCOMPLETE_API_PREFIX = "/notebook/api/autocomplete/";
  var SAMPLE_API_PREFIX = "/notebook/api/sample/";
  var DOCUMENTS_API = "/desktop/api2/doc/";
  var DOCUMENTS_SEARCH_API = "/desktop/api2/docs/";
  var FETCH_CONFIG = '/desktop/api2/get_config/';
  var HDFS_API_PREFIX = "/filebrowser/view=/";
  var ADLS_API_PREFIX = "/filebrowser/view=adl:/";
  var GIT_API_PREFIX = "/desktop/api/vcs/contents/";
  var S3_API_PREFIX = "/filebrowser/view=S3A://";
  var IMPALA_INVALIDATE_API = '/impala/api/invalidate';
  var CONFIG_SAVE_API = '/desktop/api/configurations/save/';
  var CONFIG_APPS_API = '/desktop/api/configurations';
  var SOLR_COLLECTIONS_API = '/indexer/api/indexes/list/';
  var SOLR_FIELDS_API = '/indexer/api/index/list/';
  var DASHBOARD_TERMS_API = '/dashboard/get_terms';
  var DASHBOARD_STATS_API = '/dashboard/get_stats';

  var SEARCH_API = '/desktop/api/search/entities';
  var INTERACTIVE_SEARCH_API = '/desktop/api/search/entities_interactive';

  var HBASE_API_PREFIX = '/hbase/api/';
  var SAVE_TO_FILE = '/filebrowser/save';

  var NAV_URLS = {
    ADD_TAGS: '/metadata/api/navigator/add_tags',
    DELETE_TAGS: '/metadata/api/navigator/delete_tags',
    FIND_ENTITY: '/metadata/api/navigator/find_entity',
    LIST_TAGS: '/metadata/api/navigator/list_tags',
    UPDATE_PROPERTIES: '/metadata/api/navigator/update_properties',
  };

  var NAV_OPT_URLS = {
    TOP_AGGS: '/metadata/api/optimizer/top_aggs',
    TOP_COLUMNS: '/metadata/api/optimizer/top_columns',
    TOP_FILTERS: '/metadata/api/optimizer/top_filters',
    TOP_JOINS: '/metadata/api/optimizer/top_joins',
    TOP_TABLES: '/metadata/api/optimizer/top_tables'
  };

  var genericCacheCondition = function (data) {
    return typeof data !== 'undefined' && typeof data.status !== 'undefined' && data.status === 0;
  };

  function ApiHelper () {
    var self = this;
    self.lastKnownDatabases = {};
    self.queueManager = ApiQueueManager.getInstance();
    self.invalidateImpala = null;

    huePubSub.subscribe('assist.invalidate.impala', function (details) {
      self.invalidateImpala = details;
    });

    huePubSub.subscribe('assist.clear.db.cache', function (options) {
      self.clearDbCache(options);
    });

    huePubSub.subscribe('assist.clear.hdfs.cache', function () {
      $.totalStorage(self.getAssistCacheIdentifier({ sourceType: 'hdfs' }), {});
    });

    huePubSub.subscribe('assist.clear.adls.cache', function () {
      $.totalStorage(self.getAssistCacheIdentifier({ sourceType: 'adls' }), {});
    });

    huePubSub.subscribe('assist.clear.git.cache', function () {
      $.totalStorage(self.getAssistCacheIdentifier({ sourceType: 'git' }), {});
    });

    huePubSub.subscribe('assist.clear.s3.cache', function () {
      $.totalStorage(self.getAssistCacheIdentifier({ sourceType: 's3' }), {});
    });

    huePubSub.subscribe('assist.clear.collections.cache', function () {
      $.totalStorage(self.getAssistCacheIdentifier({ sourceType: 'collections' }), {});
    });

    huePubSub.subscribe('assist.clear.hbase.cache', function () {
      $.totalStorage(self.getAssistCacheIdentifier({ sourceType: 'hbase' }), {});
    });

    huePubSub.subscribe('assist.clear.document.cache', function () {
      $.totalStorage(self.getAssistCacheIdentifier({ sourceType: 'document' }), {});
    });

    var clearAllCaches = function () {
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

  ApiHelper.prototype.hasExpired = function (timestamp, cacheType) {
    if (typeof hueDebug !== 'undefined' && typeof hueDebug.cacheTimeout !== 'undefined') {
      return (new Date()).getTime() - timestamp > hueDebug.cacheTimeout;
    }
    return (new Date()).getTime() - timestamp > CACHEABLE_TTL[cacheType];
  };

  /**
   * @param {string} sourceType
   * @returns {string}
   */
  ApiHelper.prototype.getTotalStorageUserPrefix = function (sourceType) {
    return sourceType + '_' + LOGGED_USERNAME + '_' + window.location.hostname;
  };

  /**
   * @param {object} options
   * @param {string} options.sourceType
   * @param {string} [options.cacheType] - Default value 'default'
   * @returns {string}
   */
  ApiHelper.prototype.getAssistCacheIdentifier = function (options) {
    var self = this;
    return "hue.assist." + (options.cacheType || 'default') + '.' + self.getTotalStorageUserPrefix(options.sourceType);
  };

  /**
   *
   * @param {string} owner - 'assist', 'viewModelA' etc.
   * @param {string} id
   * @param {*} [value] - Optional, undefined and null will remove the value
   */
  ApiHelper.prototype.setInTotalStorage = function(owner, id, value) {
    var self = this;
    try {
      var cachedData = $.totalStorage("hue.user.settings." + self.getTotalStorageUserPrefix(owner)) || {};
      if (typeof value !== 'undefined' && value !== null) {
        cachedData[id] = value;
        $.totalStorage("hue.user.settings." + self.getTotalStorageUserPrefix(owner), cachedData, { secure: window.location.protocol.indexOf('https') > -1 });
      } else if (cachedData[id]) {
        delete cachedData[id];
        $.totalStorage("hue.user.settings." + self.getTotalStorageUserPrefix(owner), cachedData, { secure: window.location.protocol.indexOf('https') > -1 });
      }
    } catch (e) {}
  };

  /**
   *
   * @param {string} owner - 'assist', 'viewModelA' etc.
   * @param {string} id
   * @param {*} [defaultValue]
   * @returns {*}
   */
  ApiHelper.prototype.getFromTotalStorage = function(owner, id, defaultValue) {
    var self = this;
    var cachedData = $.totalStorage("hue.user.settings." + self.getTotalStorageUserPrefix(owner)) || {};
    return typeof cachedData[id] !== 'undefined' ? cachedData[id] : defaultValue;
  };

  /**
   * @param {string} owner - 'assist', 'viewModelA' etc.
   * @param {string} id
   * @param {Observable} observable
   * @param {*} [defaultValue] - Optional default value to use if not in total storage initially
   */
  ApiHelper.prototype.withTotalStorage = function(owner, id, observable, defaultValue, noInit) {
    var self = this;

    var cachedValue = self.getFromTotalStorage(owner, id, defaultValue);

    if (! noInit && cachedValue !== 'undefined') {
      observable(cachedValue);
    }

    observable.subscribe(function (newValue) {
      if (owner === 'assist' && id === 'assist_panel_visible') {
        huePubSub.publish('assist.forceRender');
      }
      self.setInTotalStorage(owner, id, newValue);
    });
    return observable;
  };

  /**
   * @param {Object} [response]
   * @param {number} [response.status]
   * @returns {boolean} - True if actually an error
   */
  ApiHelper.prototype.successResponseIsError = function (response) {
    return typeof response !== 'undefined' && (
        typeof response.traceback !== 'undefined' ||
        (typeof response.status !== 'undefined' && response.status !== 0) ||
        response.code === 503 ||
        response.code === 500);
  };

  /**
   * @param {Object} options
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   * @returns {Function}
   */
  ApiHelper.prototype.assistErrorCallback = function (options) {
    return function (errorResponse) {
      var errorMessage = 'Unknown error occurred';
      if (typeof errorResponse !== 'undefined' && errorResponse !== null) {
        if (typeof errorResponse.statusText !== 'undefined' && errorResponse.statusText === 'abort') {
          return;
        } else if (typeof errorResponse.responseText !== 'undefined') {
          try {
            var errorJs = JSON.parse(errorResponse.responseText);
            if (typeof errorJs.message !== 'undefined') {
              errorMessage = errorJs.message;
            } else {
              errorMessage = errorResponse.responseText;
            }
          } catch(err) {
            errorMessage = errorResponse.responseText;
          }
        } else if (typeof errorResponse.message !== 'undefined' && errorResponse.message !== null) {
          errorMessage = errorResponse.message;
        } else if (typeof errorResponse.statusText !== 'undefined' && errorResponse.statusText !== null) {
          errorMessage = errorResponse.statusText;
        } else if (errorResponse.error !== 'undefined' && Object.prototype.toString.call(errorResponse.error) === '[object String]' ) {
          errorMessage = errorResponse.error;
        } else if (Object.prototype.toString.call(errorResponse) === '[object String]') {
          errorMessage = errorResponse;
        }
      }

      if (! options.silenceErrors) {
        hueUtils.logError(errorResponse);
        $(document).trigger("error", errorMessage);
      }

      if (options.errorCallback) {
        options.errorCallback(errorMessage);
      }
      return errorMessage;
    };
  };

  ApiHelper.prototype.cancelActiveRequest = function (request) {
    if (typeof request !== 'undefined' && request !== null && request.readyState < 4) {
      request.abort();
    }
  };

  /**
   * @param {string} url
   * @param {Object} data
   * @param {Object} options
   * @param {function} [options.successCallback]
   * @param {function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   */
  ApiHelper.prototype.simplePost = function (url, data, options) {
    var self = this;
    return $.post(url, data, function (data) {
      if (self.successResponseIsError(data)) {
        self.assistErrorCallback(options)(data);
      } else if (typeof options.successCallback !== 'undefined') {
        options.successCallback(data);
      }
    })
    .fail(self.assistErrorCallback(options));
  };

  /**
   * @param {Object} data
   * @param {Object} options
   * @param {function} [options.successCallback]
   */
  ApiHelper.prototype.saveSnippetToFile = function (data, options) {
    var self = this;
    $.post(SAVE_TO_FILE, data, function (result) {
      if (typeof options.successCallback !== 'undefined') {
        options.successCallback(result);
      }
    }, dataType='json').fail(self.assistErrorCallback(options));
  };

  /**
   * @param {string} url
   * @param {Object} data
   * @param {Object} options
   * @param {function} [options.successCallback]
   * @param {function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   */
  ApiHelper.prototype.simpleGet = function (url, data, options) {
    var self = this;
    $.get(url, data, function (data) {
      if (self.successResponseIsError(data)) {
        self.assistErrorCallback(options)(data);
      } else if (typeof options.successCallback !== 'undefined') {
        options.successCallback(data);
      }
    })
    .fail(self.assistErrorCallback(options));
  };

  ApiHelper.prototype.fetchUsersAndGroups = function (options) {
    var self = this;
    $.ajax({
      method: "GET",
      url: "/desktop/api/users/autocomplete",
      data: options.data || {},
      contentType: 'application/json'
    }).done(function(response) {
      options.successCallback(response);
    }).fail(function (response) {
      options.errorCallback(response);
    });
  };

  ApiHelper.prototype.fetchUsersByIds = function (options) {
    var self = this;
    $.ajax({
      method: "GET",
      url: "/desktop/api/users",
      data: { userids: options.userids},
      contentType: 'application/json'
    }).done(function(response) {
      options.successCallback(response);
    }).fail(function (response) {
      options.errorCallback(response);
    });
  };

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
  ApiHelper.prototype.fetchHdfsPath = function (options) {
    var self = this;
    if (options.pathParts.length > 0 && (options.pathParts[0] === '/' || options.pathParts[0] === '')) {
      options.pathParts.shift();
    }
    var url = HDFS_API_PREFIX + options.pathParts.join("/") + '?format=json&sortby=name&descending=false&pagesize=' + (options.pageSize || 500) + '&pagenum=' + (options.page || 1);
    if (options.filter) {
      url += '&filter=' + options.filter;
    }
    var fetchFunction = function (storeInCache) {
      if (options.timeout === 0) {
        self.assistErrorCallback(options)({ status: -1 });
        return;
      }
      return $.ajax({
        dataType: "json",
        url: url,
        timeout: options.timeout,
        success: function (data) {
          if (!data.error && !self.successResponseIsError(data) && typeof data.files !== 'undefined' && data.files !== null) {
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
      .always(function () {
        if (typeof options.editor !== 'undefined' && options.editor !== null) {
          options.editor.hideSpinner();
        }
      });
    };

    return fetchCached.bind(self)($.extend({}, options, {
      sourceType: 'hdfs',
      url: url,
      fetchFunction: fetchFunction
    }));
  };

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
  ApiHelper.prototype.fetchAdlsPath = function (options) {
    var self = this;
    options.pathParts.shift();
    var url = ADLS_API_PREFIX + options.pathParts.join("/") + '?format=json&sortby=name&descending=false&pagesize=' + (options.pageSize || 500) + '&pagenum=' + (options.page || 1);
    if (options.filter) {
      url += '&filter=' + options.filter;
    }
    var fetchFunction = function (storeInCache) {
      if (options.timeout === 0) {
        self.assistErrorCallback(options)({ status: -1 });
        return;
      }
      return $.ajax({
        dataType: "json",
        url: url,
        timeout: options.timeout,
        success: function (data) {
          if (!data.error && !self.successResponseIsError(data) && typeof data.files !== 'undefined' && data.files !== null) {
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
      .always(function () {
        if (typeof options.editor !== 'undefined' && options.editor !== null) {
          options.editor.hideSpinner();
        }
      });
    };

    return fetchCached.bind(self)($.extend({}, options, {
      sourceType: 'adls',
      url: url,
      fetchFunction: fetchFunction
    }));
  };

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
  ApiHelper.prototype.fetchGitContents = function (options) {
    var self = this;
    var url = GIT_API_PREFIX + '?path=' + options.pathParts.join("/") + '&fileType=' + options.fileType;
    var fetchFunction = function (storeInCache) {
      if (options.timeout === 0) {
        self.assistErrorCallback(options)({ status: -1 });
        return;
      }
      $.ajax({
        dataType: "json",
        url: url,
        timeout: options.timeout,
        success: function (data) {
          if (!data.error && !self.successResponseIsError(data)) {
            if (data.fileType === 'dir' && typeof data.files !== 'undefined' && data.files !== null) {
              if (data.files.length > 2) {
                storeInCache(data);
              }
              options.successCallback(data);
            } else if (data.fileType === 'file' && typeof data.content !== 'undefined' && data.content !== null) {
              options.successCallback(data);
            }
          } else {
            self.assistErrorCallback(options)(data);
          }
        }
      })
      .fail(self.assistErrorCallback(options));
    };

    fetchCached.bind(self)($.extend({}, options, {
      sourceType: 'git',
      url: url,
      fetchFunction: fetchFunction
    }));
  };

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
  ApiHelper.prototype.fetchS3Path = function (options) {
    var self = this;
    options.pathParts.shift(); // remove the trailing /
    var url = S3_API_PREFIX + options.pathParts.join("/") + '?format=json&sortby=name&descending=false&pagesize=' + (options.pageSize || 500) + '&pagenum=' + (options.page || 1);
    if (options.filter) {
      url += '&filter=' + options.filter;
    }
    var fetchFunction = function (storeInCache) {
      if (options.timeout === 0) {
        self.assistErrorCallback(options)({ status: -1 });
        return;
      }

      $.ajax({
        dataType: "json",
        url: url,
        timeout: options.timeout,
        success: function (data) {
          if (!data.error && !self.successResponseIsError(data) && typeof data.files !== 'undefined' && data.files !== null) {
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
      .always(function () {
        if (typeof options.editor !== 'undefined' && options.editor !== null) {
          options.editor.hideSpinner();
        }
      });
    };

    fetchCached.bind(self)($.extend({}, options, {
      sourceType: 's3',
      url: url,
      fetchFunction: fetchFunction
    }));
  };

  /**
   * @param {Object} options
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   * @param {Number} [options.timeout]
   * @param {Object} [options.editor] - Ace editor
   *
   */
  ApiHelper.prototype.fetchSolrCollections = function (options) {
    var self = this;
    var url = SOLR_COLLECTIONS_API;
    var fetchFunction = function (storeInCache) {
      if (options.timeout === 0) {
        self.assistErrorCallback(options)({ status: -1 });
        return;
      }
      $.ajax({
        dataType: "json",
        url: url,
        type: 'POST',
        timeout: options.timeout,
        success: function (data) {
          if (!data.error && !self.successResponseIsError(data) && typeof data.collections !== 'undefined' && data.collections !== null) {
            storeInCache(data);
            options.successCallback(data);
          } else {
            self.assistErrorCallback(options)(data);
          }
        }
      })
      .fail(self.assistErrorCallback(options))
      .always(function () {
        if (typeof options.editor !== 'undefined' && options.editor !== null) {
          options.editor.hideSpinner();
        }
      });
    };

    fetchCached.bind(self)($.extend({}, options, {
      sourceType: 'collections',
      url: url,
      fetchFunction: fetchFunction
    }));
  };

  /**
   * @param {Object} options
   * @param {String} options.collectionName
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   * @param {Number} [options.timeout]
   *
   */
  ApiHelper.prototype.fetchSolrCollection = function (options) {
    var self = this;
    var url = SOLR_FIELDS_API  + '?name=' + options.collectionName;
    var fetchFunction = function (storeInCache) {
      if (options.timeout === 0) {
        self.assistErrorCallback(options)({ status: -1 });
        return;
      }
      $.ajax({
        dataType: "json",
        url: url,
        type: 'GET',
        timeout: options.timeout,
        success: function (data) {
          if (!data.error && !self.successResponseIsError(data) && typeof data.schema !== 'undefined' && data.schema !== null) {
            storeInCache(data);
            options.successCallback(data);
          } else {
            self.assistErrorCallback(options)(data);
          }
        }
      })
      .fail(self.assistErrorCallback(options))
      .always(function () {
        if (typeof options.editor !== 'undefined' && options.editor !== null) {
          options.editor.hideSpinner();
        }
      });
    };

    fetchCached.bind(self)($.extend({}, options, {
      sourceType: 'collections',
      url: url,
      fetchFunction: fetchFunction
    }));
  };

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
  ApiHelper.prototype.fetchDashboardTerms = function (options) {
    var self = this;
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
      success: function (data) {
        if (!data.error && !self.successResponseIsError(data) && data.status === 0) {
          options.successCallback(data);
        } else {
          self.assistErrorCallback(options)(data);
        }
      }
    })
    .fail(self.assistErrorCallback(options))
    .always(options.alwaysCallback);
  };

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
  ApiHelper.prototype.fetchDashboardStats = function (options) {
    var self = this;
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
          },
        }),
        query: ko.mapping.toJSON({
          qs: [{q: ''}],
          fqs: []
        })
      },
      timeout: options.timeout,
      success: function (data) {
        if (!data.error && !self.successResponseIsError(data) && data.status === 0) {
          if (data.status === 0){
            options.successCallback(data);
          }
          else if (data.status === 1) {
            options.notSupportedCallback(data);
          }
          else {
            self.assistErrorCallback(options)(data);
          }
        } else {
          self.assistErrorCallback(options)(data);
        }
      }
    })
    .fail(self.assistErrorCallback(options))
    .always(options.alwaysCallback);
  };

  /**
   * @param {Object} options
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   * @param {Number} [options.timeout]
   * @param {Object} [options.editor] - Ace editor
   */
  ApiHelper.prototype.fetchHBase = function (options) {
    var self = this;
    var suffix = 'getClusters';
    if (options.parent.name !== '') {
      suffix = 'getTableList/' + options.parent.name;
    }
    var url = HBASE_API_PREFIX + suffix;
    var fetchFunction = function (storeInCache) {
      if (options.timeout === 0) {
        self.assistErrorCallback(options)({ status: -1 });
        return;
      }
      $.ajax({
        dataType: "json",
        url: url,
        timeout: options.timeout,
        success: function (data) {
          if (!data.error && !self.successResponseIsError(data)) {
            storeInCache(data);
            options.successCallback(data);
          } else {
            self.assistErrorCallback(options)(data);
          }
        }
      })
      .fail(self.assistErrorCallback(options))
      .always(function () {
        if (typeof options.editor !== 'undefined' && options.editor !== null) {
          options.editor.hideSpinner();
        }
      });
    };

    fetchCached.bind(self)($.extend({}, options, {
      sourceType: 'hbase',
      url: url,
      fetchFunction: fetchFunction
    }));
  };

  /**
   * @param {Object} options
   * @param {Function} [options.successCallback]
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   */
  ApiHelper.prototype.fetchConfigurations = function (options) {
    var self = this;
    self.simpleGet(CONFIG_APPS_API, {}, options);
  };

  ApiHelper.prototype.saveGlobalConfiguration = function (options) {
    var self = this;
    self.simplePost(CONFIG_APPS_API, {
      configuration: ko.mapping.toJSON(options.configuration)
    }, options);
  };

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
  ApiHelper.prototype.saveConfiguration = function (options) {
    var self = this;
    self.simplePost(CONFIG_SAVE_API, {
      app: options.app,
      properties: ko.mapping.toJSON(options.properties),
      is_default: options.isDefault,
      group_id: options.groupId,
      user_id: options.userId
    }, options);
  };

  /**
   * @param {Object} options
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   *
   * @param {string} [options.uuid]
   */
  ApiHelper.prototype.fetchDocuments = function (options) {
    var self = this;

    var id = '';
    if (options.uuid) {
      id += options.uuid;
    }
    if (options.type && options.type !== 'all') {
      id += options.type;
    }

    var promise = self.queueManager.getQueued(DOCUMENTS_API, id);
    var firstInQueue = typeof promise === 'undefined';
    if (firstInQueue) {
      promise = $.Deferred();
      self.queueManager.addToQueue(promise, DOCUMENTS_API, id);
    }

    promise.done(options.successCallback).fail(self.assistErrorCallback(options));

    if (!firstInQueue) {
      return;
    }

    var data = {
      uuid: options.uuid
    };

    if (options.type && options.type !== 'all') {
      data.type = ['directory', options.type];
    }

    $.ajax({
      url: DOCUMENTS_API,
      data: data,
      traditional: true,
      success: function (data) {
        if (! self.successResponseIsError(data)) {
          promise.resolve(data);
        } else {
          promise.reject(data);
        }
      }
    }).fail(promise.reject);
  };

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
  ApiHelper.prototype.searchDocuments = function (options) {
    var self = this;
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
      success: function (data) {
        if (! self.successResponseIsError(data)) {
          options.successCallback(data);
        } else {
          self.assistErrorCallback(options)(data);
        }
      }
    })
    .fail(self.assistErrorCallback(options));
  };

  /**
   * @param {Object} options
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   * @param {boolean} [options.fetchContents]
   *
   * @param {number} options.uuid
   */
  ApiHelper.prototype.fetchDocument = function (options) {
    var self = this;
    var promise = $.Deferred();
    $.ajax({
      url: DOCUMENTS_API,
      data: {
        uuid: options.uuid,
        data: !!options.fetchContents
      },
      success: function (data) {
        if (! self.successResponseIsError(data)) {
          promise.resolve(data)
        } else {
          promise.reject(self.assistErrorCallback({
            silenceErrors: options.silenceErrors
          }));
        }
      }
    })
    .fail(function (errorResponse) {
      promise.reject(self.assistErrorHandler(errorResponse))
    });
    return promise;
  };

  /**
   * @param {Object} options
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   *
   * @param {string} options.parentUuid
   * @param {string} options.name
   */
  ApiHelper.prototype.createDocumentsFolder = function (options) {
    var self = this;
    self.simplePost(DOCUMENTS_API + 'mkdir', {
      parent_uuid: ko.mapping.toJSON(options.parentUuid),
      name: ko.mapping.toJSON(options.name)
    }, options);
  };

  /**
   * @param {Object} options
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   *
   * @param {string} options.uuid
   * @param {string} options.name
   */
  ApiHelper.prototype.updateDocument = function (options) {
    var self = this;
    self.simplePost(DOCUMENTS_API + 'update', {
      uuid: ko.mapping.toJSON(options.uuid),
      name: options.name
    }, options);
  };

  /**
   * @param {Object} options
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {Function} [options.progressHandler]
   * @param {boolean} [options.silenceErrors]
   *
   * @param {FormData} options.formData
   */
  ApiHelper.prototype.uploadDocument = function (options) {
    var self = this;
    $.ajax({
      url: DOCUMENTS_API + 'import',
      type: 'POST',
      success: function (data) {
        if (! self.successResponseIsError(data)) {
          options.successCallback(data);
        } else {
          self.assistErrorCallback(options)(data);
        }
      },
      xhr: function() {
        var myXhr = $.ajaxSettings.xhr();
        if(myXhr.upload && options.progressHandler) {
          myXhr.upload.addEventListener('progress', options.progressHandler, false);
        }
        return myXhr;
      },
      dataType: 'json',
      data: options.formData,
      cache: false,
      contentType: false,
      processData: false
    })
    .fail(self.assistErrorCallback(options));
  };

  /**
   *
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   *
   * @param {number} options.sourceId - The ID of the source document
   * @param {number} options.destinationId - The ID of the target document
   */
  ApiHelper.prototype.moveDocument = function (options) {
    var self = this;
    self.simplePost(DOCUMENTS_API + 'move', {
      source_doc_uuid: ko.mapping.toJSON(options.sourceId),
      destination_doc_uuid: ko.mapping.toJSON(options.destinationId)
    }, options);
  };

  /**
   * @param {Object} options
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   *
   * @param {string} options.uuid
   * @param {string} [options.skipTrash] - Default false
   */
  ApiHelper.prototype.deleteDocument = function (options) {
    var self = this;
    self.simplePost(DOCUMENTS_API + 'delete', {
      uuid: ko.mapping.toJSON(options.uuid),
      skip_trash: ko.mapping.toJSON(options.skipTrash || false)
    }, options);
  };

  /**
   * @param {Object} options
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   *
   * @param {string} options.uuid
   */
  ApiHelper.prototype.restoreDocument = function (options) {
    var self = this;
    self.simplePost(DOCUMENTS_API + 'restore', {
      uuids: ko.mapping.toJSON(options.uuids)
    }, options);
  };

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
  ApiHelper.prototype.clearDbCache = function (options) {
    var self = this;
    var cacheIdentifier = self.getAssistCacheIdentifier(options);
    if (options.clearAll) {
      $.totalStorage(cacheIdentifier, {});
    } else {
      var url = AUTOCOMPLETE_API_PREFIX;
      if (options.databaseName) {
        url += options.databaseName;
      }
      if (options.tableName) {
        url += "/" + options.tableName;
      }
      if (options.fields) {
        url += options.fields.length > 0 ? "/" + options.fields.join("/") : "";
      }
      var cachedData = $.totalStorage(cacheIdentifier) || {};
      delete cachedData[url];
      $.totalStorage(cacheIdentifier, cachedData);
    }
  };

  /**
   * @param {Object} options
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   *
   * @param {string} options.sourceType
   * @param {string} [options.database]
   **/
  ApiHelper.prototype.loadDatabases = function (options) {
    var self = this;

    var loadFunction = function () {

      fetchAssistData.bind(self)($.extend({}, options, {
        url: AUTOCOMPLETE_API_PREFIX,
        successCallback: function (data) {
          var databases = data.databases || [];
          var cleanDatabases = [];
          databases.forEach(function (database) {
            // Blacklist of system databases
            if (database !== '_impala_builtins') {
              // Ensure lower case
              cleanDatabases.push(database.toLowerCase());
            }
          });
          self.lastKnownDatabases[options.sourceType] = cleanDatabases;

          options.successCallback(self.lastKnownDatabases[options.sourceType]);
        },
        errorCallback: function (response) {
          if (response.status == 401) {
            $(document).trigger("showAuthModal", {
              'type': options.sourceType, 'callback': function () {
                self.loadDatabases(options);
              }
            });
            return;
          }
          self.lastKnownDatabases[options.sourceType] = [];
          self.assistErrorCallback(options)(response);
        },
        cacheCondition: genericCacheCondition
      }));
    };

    if (options.sourceType === 'impala' && self.invalidateImpala !== null) {
      if (self.invalidateImpala.database) {
        $.post(IMPALA_INVALIDATE_API, { flush_all:  self.invalidateImpala.flush, database: self.invalidateImpala.database }, loadFunction);
      } else {
        $.post(IMPALA_INVALIDATE_API, { flush_all:  self.invalidateImpala.flush }, loadFunction);
      }
      self.invalidateImpala = null;
    } else {
      loadFunction();
    }
  };

  /**
   * @param {Object} options
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   *
   * @param {string} options.databaseName
   * @param {string} options.tableName
   * @param {Object[]} options.identifierChain
   * @param {string} options.defaultDatabase
   */
  ApiHelper.prototype.fetchPartitions = function (options) {
    var self = this;

    var url;
    if (typeof options.identifierChain !== 'undefined' && options.identifierChain.length === 1) {
      url = '/metastore/table/' + options.defaultDatabase + '/' + options.identifierChain[0].name + '/partitions';
    } else if (typeof options.identifierChain !== 'undefined' && options.identifierChain.length === 2) {
      url = '/metastore/table/' + options.identifierChain[0].name + '/' + options.identifierChain[1].name + '/partitions';
    } else {
      url = '/metastore/table/' + options.databaseName + '/' + options.tableName + '/partitions';
    }

    $.ajax({
      url: url,
      data: {
        format: 'json'
      },
      beforeSend: function (xhr) {
        xhr.setRequestHeader('X-Requested-With', 'Hue');
      },
      success: function (response) {
        if (! self.successResponseIsError(response)) {
          options.successCallback(response);
        } else {
          self.assistErrorCallback(options)(response);
        }

      },
      error: self.assistErrorCallback(options)
    });
  };

  /**
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   *
   * @param {string} options.databaseName
   * @param {string} options.tableName
   */
  ApiHelper.prototype.fetchTableDetails = function (options) {
    var self = this;
    $.ajax({
      url: "/" + (options.sourceType == "hive" ? "beeswax" : options.sourceType) + "/api/table/" + options.databaseName + "/" + options.tableName,
      data: {
        "format" : 'json'
      },
      beforeSend: function (xhr) {
        xhr.setRequestHeader("X-Requested-With", "Hue");
      },
      success: function (response) {
        if (! self.successResponseIsError(response)) {
          options.successCallback(response);
        } else {
          self.assistErrorCallback(options)(response);
        }
      },
      error: self.assistErrorCallback(options)
    });
  };


  /**
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   *
   * @param {string} options.databaseName
   * @param {string} options.tableName
   * @param {Number} [options.timeout]
   * @param {string} [options.columnName]
   * @param {Object} [options.editor] - Ace editor
   */
  ApiHelper.prototype.fetchTableSample = function (options) {
    var self = this;
    var url = SAMPLE_API_PREFIX + options.databaseName + '/' + options.tableName + (options.columnName ? '/' + options.columnName : '');

    var fetchFunction = function (storeInCache) {
      if (options.timeout === 0) {
        self.assistErrorCallback(options)({ status: -1 });
        return;
      }
      $.ajax({
        type: 'POST',
        url: url,
        data: {
          notebook: {},
          snippet: ko.mapping.toJSON({
            type: options.sourceType
          })
        },
        timeout: options.timeout
      }).done(function (data) {
        if (! self.successResponseIsError(data)) {
          if ((typeof data.rows !== 'undefined' && data.rows.length > 0) || typeof data.sample !== 'undefined') {
            storeInCache(data);
          }
          options.successCallback(data);
        } else {
          self.assistErrorCallback(options)(data);
        }
      })
      .fail(self.assistErrorCallback(options))
      .always(function () {
        if (typeof options.editor !== 'undefined' && options.editor !== null) {
          options.editor.hideSpinner();
        }
      });
    };

    if (options.columnName) {
      fetchCached.bind(self)($.extend({}, options, {
        url: url,
        fetchFunction: fetchFunction
      }));
    } else {
      fetchFunction($.noop);
    }
  };


  /**
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   *
   * @param {string} options.databaseName
   * @param {string} options.tableName
   * @param {string} options.columnName
   */
  ApiHelper.prototype.refreshTableStats = function (options) {
    var self = this;
    var pollRefresh = function (url) {
      $.post(url, function (data) {
        if (data.isSuccess) {
          options.successCallback(data);
        } else if (data.isFailure) {
          self.assistErrorCallback(options)(data.message);
        } else {
          window.setTimeout(function () {
            pollRefresh(url);
          }, 1000);
        }
      }).fail(self.assistErrorCallback(options));
    };

    $.post("/" + (options.sourceType == "hive" ? "beeswax" : options.sourceType) + "/api/analyze/" + options.databaseName + "/" + options.tableName + "/"  + (options.columnName || ""), function (data) {
      if (data.status == 0 && data.watch_url) {
        pollRefresh(data.watch_url);
      } else {
        self.assistErrorCallback(options)(data);
      }
    }).fail(self.assistErrorCallback(options));
  };

  /**
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   *
   * @param {string} options.databaseName
   * @param {string} options.tableName
   * @param {string} options.columnName
   */
  ApiHelper.prototype.fetchStats = function (options) {
    var self = this;
    $.ajax({
      url: "/" + options.sourceType + "/api/table/" + options.databaseName + "/" + options.tableName + "/stats/" + ( options.columnName || ""),
      data: {},
      beforeSend: function (xhr) {
        xhr.setRequestHeader("X-Requested-With", "Hue");
      },
      dataType: "json",
      success: function (response) {
        if (! self.successResponseIsError(response)) {
          options.successCallback(response)
        } else {
          self.assistErrorCallback(options)(response);
        }
      },
      error: self.assistErrorCallback(options)
    });
  };

  /**
   * Returns a promise that will always be resolved with:
   *
   * 1. Cached databases
   * 2. Fetched databases
   * 3. Empty array
   *
   * @param sourceType
   * @return {Promise}
   */
  ApiHelper.prototype.getDatabases = function (sourceType) {
    var self = this;
    var promise = $.Deferred();
    if (typeof self.lastKnownDatabases[sourceType] !== 'undefined') {
      promise.resolve(self.lastKnownDatabases[sourceType])
    } else {
      self.loadDatabases({
        sourceType: sourceType,
        silenceErrors: true,
        successCallback: function (databases) {
          promise.resolve(databases)
        },
        errorCallback: function () {
          promise.resolve([]);
        }
      });
    }
    return promise;
  };

  /**
   * Tests if a database exists or not for the given sourceType
   * Returns a promise that will always be resolved with either true or false. In case of error it will be false.
   *
   * @param sourceType
   * @param databaseName
   * @return {Promise}
   */
  ApiHelper.prototype.containsDatabase = function (sourceType, databaseName) {
    var self = this;
    var promise = $.Deferred(); // Will always be resolved
    if (databaseName) {
      self.getDatabases(sourceType).done(function (databases) {
        promise.resolve(databases && databases.indexOf(databaseName.toLowerCase()) > -1);
      });
    } else {
      promise.resolve(false);
    }
    return promise;
  };

  ApiHelper.prototype.expandComplexIdentifierChain = function (sourceType, database, identifierChain, successCallback, errorCallback, cachedOnly) {
    var self = this;

    var fetchFieldsInternal =  function (table, database, identifierChain, callback, errorCallback, fetchedFields) {
      if (!identifierChain) {
        identifierChain = [];
      }
      if (identifierChain.length > 0) {
        fetchedFields.push(identifierChain[0].name);
        identifierChain = identifierChain.slice(1);
      }

      // Parser sometimes knows if it's a map or array.
      if (identifierChain.length > 0 && (identifierChain[0].name === 'item' || identifierChain[0].name === 'value')) {
        fetchedFields.push(identifierChain[0].name);
        identifierChain = identifierChain.slice(1);
      }


      self.fetchFields({
        sourceType: sourceType,
        databaseName: database,
        tableName: table,
        fields: fetchedFields,
        timeout: self.timeout,
        cachedOnly: cachedOnly,
        successCallback: function (data) {
          if (sourceType === 'hive'
              && typeof data.extended_columns !== 'undefined'
              && data.extended_columns.length === 1
              && data.extended_columns.length
              && /^map|array|struct/i.test(data.extended_columns[0].type)) {
            identifierChain.unshift({ name: data.extended_columns[0].name })
          }
          if (identifierChain.length > 0) {
            if (typeof identifierChain[0].name !== 'undefined' && /value|item|key/i.test(identifierChain[0].name)) {
              fetchedFields.push(identifierChain[0].name);
              identifierChain.shift();
            } else {
              if (data.type === 'array') {
                fetchedFields.push('item')
              }
              if (data.type === 'map') {
                fetchedFields.push('value')
              }
            }
            fetchFieldsInternal(table, database, identifierChain, callback, errorCallback, fetchedFields)
          } else {
            fetchedFields.unshift(table);
            callback(fetchedFields);
          }
        },
        silenceErrors: true,
        errorCallback: errorCallback
      });
    };

    fetchFieldsInternal(identifierChain.shift().name, database, identifierChain, successCallback, errorCallback, []);
  };

  /**
   *
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {function} options.errorCallback
   * @param {Object[]} options.identifierChain
   * @param {string} options.identifierChain.name
   * @param {string} options.defaultDatabase
   * @param {boolean} [options.cachedOnly] - Default false
   *
   * @returns {Object} promise
   */
  ApiHelper.prototype.identifierChainToPath = function (options) {
    var self = this;
    var promise = $.Deferred();
    if (options.identifierChain.length === 0) {
      promise.resolve([options.defaultDatabase]);
      return promise;
    }

    var identifierChainClone = options.identifierChain.concat();
    var path = [];

    var dbPromise = self.containsDatabase(options.sourceType, identifierChainClone[0].name);

    dbPromise.done(function (firstIsDatabase) {
      if (!firstIsDatabase) {
        path.push(options.defaultDatabase);
      } else {
        path.push(identifierChainClone.shift().name)
      }

      if (identifierChainClone.length > 1) {
        self.expandComplexIdentifierChain(options.sourceType, path[0], identifierChainClone, function (fetchedFields) {
          promise.resolve(path.concat(fetchedFields))
        }, options.errorCallback, options.cachedOnly);
      } else {
        promise.resolve(path.concat($.map(identifierChainClone, function (identifier) { return identifier.name })))
      }
    });
    return promise;
  };


  /**
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {boolean} [options.silenceErrors]
   * @param {boolean} [options.cachedOnly] - Default false
   * @param {boolean} [options.refreshCache] - Default false
   *
   * @param {string[]} [options.path] - The path to fetch
   *
   * @return {Deferred} Promise
   */
  ApiHelper.prototype.fetchSourceMetadata = function (options) {
    var self = this;
    var promise = $.Deferred();

    fetchAssistData.bind(self)({
      url: AUTOCOMPLETE_API_PREFIX + options.path.join('/'),
      sourceType: options.sourceType,
      silenceErrors: options.silenceErrors,
      cachedOnly: options.cachedOnly,
      refreshCache: options.refreshCache,
      successCallback: promise.resolve,
      errorCallback: self.assistErrorCallback({
        errorCallback: promise.reject,
        silenceErrors: options.silenceErrors
      }),
      cacheCondition: genericCacheCondition
    });

    return promise;
  };


  ApiHelper.prototype.updateSourceMetadata = function (options) {
    var self = this;
    var url;
    var data = {
      source_type: options.sourceType
    };
    if (options.path.length === 1) {
      url = '/metastore/databases/' + options.path[1] + '/alter';
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
  };


  /**
   * Fetches a navigator entity for the given source and path
   *
   * @param {Object} options
   * @param {boolean} [options.silenceErrors]
   * @param {boolean} [options.noCache]
   * @param {boolean} [options.refreshCache] - Default false
   *
   * @param {boolean} [options.isView] - Default false
   * @param {string[]} options.path
   */
  ApiHelper.prototype.fetchNavigatorMetadata = function (options) {
    var self = this;
    var promise = $.Deferred();
    var url = NAV_URLS.FIND_ENTITY;

    if (options.path.length === 1) {
      url += '?type=database&name=' + options.path[0];
    } else if (options.path.length === 2) {
      url +=  (options.isView ? '?type=view' : '?type=table') + '&database=' + options.path[0] + '&name=' + options.path[1];
    } else if (options.path.length === 3) {
      url +=  '?type=field&database=' + options.path[0] + '&table=' + options.path[1] + '&name=' + options.path[2];
    }

    fetchAssistData.bind(self)({
      url: url,
      sourceType: 'nav',
      noCache: options.noCache,
      refreshCache: options.refreshCache,
      silenceErrors: options.silenceErrors,
      successCallback: promise.resolve,
      errorCallback: self.assistErrorCallback({
        errorCallback: promise.reject,
        silenceErrors: options.silenceErrors
      }),
      cacheCondition: genericCacheCondition
    });

    return promise;
  };

  ApiHelper.prototype.updateNavigatorMetadata = function (options) {
    var self = this;
    return self.simplePost(NAV_URLS.UPDATE_PROPERTIES, {
      id: ko.mapping.toJSON(options.identity),
      properties: ko.mapping.toJSON(options.properties)
    }, options)
  };


  ApiHelper.prototype.addNavTags = function (entityId, tags) {
    return $.post(NAV_URLS.ADD_TAGS, {
      id: ko.mapping.toJSON(entityId),
      tags: ko.mapping.toJSON(tags)
    });
  };

  ApiHelper.prototype.deleteNavTags = function (entityId, tags) {
    return $.post(NAV_URLS.DELETE_TAGS, {
      id: ko.mapping.toJSON(entityId),
      tags: ko.mapping.toJSON(tags)
    });
  };

  /**
   * Lists all available navigator tags
   *
   * @param {Object} options
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   */
  ApiHelper.prototype.listNavTags = function (options) {
    var self = this;
    fetchAssistData.bind(self)($.extend({ sourceType: 'nav' }, options, {
      url: NAV_URLS.LIST_TAGS,
      errorCallback: self.assistErrorCallback(options),
      noCache: true
    }));
  };


  /**
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   * @param {Number} [options.timeout]
   * @param {Object} [options.editor] - Ace editor
   * @param {boolean} [options.cachedOnly] - Default false
   *
   * @param {Object[]} options.identifierChain
   * @param {string} options.identifierChain.name
   * @param {string} options.defaultDatabase
   */
  // TODO: Drop and use fetchSqlMetadata instead
  ApiHelper.prototype.fetchAutocomplete = function (options) {
    var self = this;
    self.identifierChainToPath(options).done(function (path) {
      fetchAssistData.bind(self)($.extend({}, options, {
        url: AUTOCOMPLETE_API_PREFIX + path.join('/'),
        errorCallback: self.assistErrorCallback(options),
        cacheCondition: genericCacheCondition
      }));
    });
  };

  /**
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   * @param {Number} [options.timeout]
   * @param {Object} [options.editor] - Ace editor
   *
   * @param {string} options.databaseName
   */
  // TODO: Drop and use fetchSqlMetadata instead
  ApiHelper.prototype.fetchTables = function (options) {
    var self = this;
    return fetchAssistData.bind(self)($.extend({}, options, {
      url: AUTOCOMPLETE_API_PREFIX + options.databaseName,
      errorCallback: self.assistErrorCallback(options),
      cacheCondition: genericCacheCondition
    }));
  };

  /**
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   * @param {Number} [options.timeout]
   * @param {boolean} [options.cachedOnly] - Default false
   * @param {Object} [options.editor] - Ace editor
   *
   * @param {string} options.databaseName
   * @param {string} options.tableName
   * @param {string[]} options.fields
   */
  // TODO: Drop and use fetchSqlMetadata instead
  ApiHelper.prototype.fetchFields = function (options) {
    var self = this;
    var fieldPart = options.fields.length > 0 ? "/" + options.fields.join("/") : "";
    return fetchAssistData.bind(self)($.extend({}, options, {
      url: AUTOCOMPLETE_API_PREFIX + options.databaseName + "/" + options.tableName + fieldPart,
      errorCallback: self.assistErrorCallback(options),
      cacheCondition: genericCacheCondition
    }));
  };

  /**
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   * @param {Number} [options.timeout]
   * @param {Object} [options.editor] - Ace editor
   *
   * @param {Object[]} options.identifierChain
   * @param {string} options.identifierChain.name
   * @param {string} options.defaultDatabase
   */
  ApiHelper.prototype.fetchSamples = function (options) {
    var self = this;
    self.identifierChainToPath(options).done(function (path) {
      fetchAssistData.bind(self)($.extend({}, options, {
        url: SAMPLE_API_PREFIX + path.join('/'),
        errorCallback: self.assistErrorCallback(options),
        cacheCondition: genericCacheCondition
      }));
    });
  };


  /**
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   * @param {Number} [options.timeout]
   * @param {Object} [options.editor] - Ace editor
   *
   * @param {Object[]} options.identifierChain
   * @param {string} options.identifierChain.name
   * @param {string} options.defaultDatabase
   */
  ApiHelper.prototype.fetchAnalysis = function (options) {
    var self = this;
    var clonedIdentifierChain = options.identifierChain.concat();

    var hierarchy = '';

    var dbPromise = self.containsDatabase(options.sourceType, clonedIdentifierChain[0].name);

    dbPromise.done(function (firstIsDatabase) {
      // Database
      if (firstIsDatabase) {
        hierarchy = clonedIdentifierChain.shift().name
      } else {
        hierarchy = options.defaultDatabase;
      }

      // Table
      if (clonedIdentifierChain.length > 0) {
        hierarchy += '/' + clonedIdentifierChain.shift().name;
      }

      // Column/Complex
      if (clonedIdentifierChain.length > 0) {
        hierarchy += '/stats/' + $.map(clonedIdentifierChain, function (identifier) { return identifier.name }).join('/')
      }

      var url = "/" + (options.sourceType == "hive" ? "beeswax" : options.sourceType) + "/api/table/" + hierarchy;

      var fetchFunction = function (storeInCache) {
        if (options.timeout === 0) {
          self.assistErrorCallback(options)({ status: -1 });
          return;
        }
        $.ajax({
          url: url,
          data: {
            "format" : 'json'
          },
          beforeSend: function (xhr) {
            xhr.setRequestHeader("X-Requested-With", "Hue");
          },
          timeout: options.timeout
        }).done(function (data) {
          if (! self.successResponseIsError(data)) {
            if ((typeof data.cols !== 'undefined' && data.cols.length > 0) || typeof data.sample !== 'undefined') {
              storeInCache(data);
            }
            options.successCallback(data);
          } else {
            self.assistErrorCallback(options)(data);
          }
        })
          .fail(self.assistErrorCallback(options))
          .always(function () {
            if (typeof options.editor !== 'undefined' && options.editor !== null) {
              options.editor.hideSpinner();
            }
          });
      };

      fetchCached.bind(self)($.extend({}, options, {
        url: url,
        fetchFunction: fetchFunction
      }));
    });
  };

  ApiHelper.prototype.getClusterConfig = function (data) {
    return $.post(FETCH_CONFIG, data);
  };

  ApiHelper.prototype.createNavOptDbTablesJson = function (options) {
    var self = this;
    var tables = [];
    var tableIndex = {};

    var promise = $.Deferred();

    self.getDatabases(options.sourceType).done(function (databases){
      options.tables.forEach(function (table) {
        if (table.subQuery || !table.identifierChain) {
          return;
        }
        var clonedIdentifierChain = table.identifierChain.concat();

        var databasePrefix;
        if (clonedIdentifierChain.length > 1 && clonedIdentifierChain[0].name && databases.indexOf(clonedIdentifierChain[0].name.toLowerCase()) > -1) {
          databasePrefix = clonedIdentifierChain.shift().name + '.';
        } else if (options.defaultDatabase) {
          databasePrefix = options.defaultDatabase + '.';
        } else {
          databasePrefix = '';
        }
        var identifier = databasePrefix  + $.map(clonedIdentifierChain, function (identifier) { return identifier.name }).join('.');
        if (!tableIndex[databasePrefix  + $.map(clonedIdentifierChain, function (identifier) { return identifier.name }).join('.')]) {
          tables.push(identifier);
          tableIndex[identifier] = true;
        }
      });
      promise.resolve(ko.mapping.toJSON(tables))
    });

    return promise;
  };

  /**
   * Fetches the top tables for the given database
   *
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   *
   * @param {Object[]} options.database
   */
  ApiHelper.prototype.fetchNavOptTopTables = function (options) {
    var self = this;
    return self.fetchNavOptCached(NAV_OPT_URLS.TOP_TABLES, options, function (data) {
      return data.status === 0;
    });
  };

  /**
   * Fetches the top columns for the given tables
   *
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   *
   * @param {Object[]} options.tables
   * @param {Object[]} options.tables.identifierChain
   * @param {string} options.tables.identifierChain.name
   * @param {string} [options.defaultDatabase]
   */
  ApiHelper.prototype.fetchNavOptTopColumns = function (options) {
    var self = this;
    return self.fetchNavOptCached(NAV_OPT_URLS.TOP_COLUMNS, options, function (data) {
      return data.status === 0;
    });
  };

  /**
   * Fetches the popular joins for the given tables
   *
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   *
   * @param {Object[]} options.tables
   * @param {Object[]} options.tables.identifierChain
   * @param {string} options.tables.identifierChain.name
   * @param {string} [options.defaultDatabase]
   */
  ApiHelper.prototype.fetchNavOptPopularJoins = function (options) {
    var self = this;
    return self.fetchNavOptCached(NAV_OPT_URLS.TOP_JOINS, options, function (data) {
      return data.status === 0;
    });
  };

  /**
   * Fetches the popular filters for the given tables
   *
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   *
   * @param {Object[]} options.tables
   * @param {Object[]} options.tables.identifierChain
   * @param {string} options.tables.identifierChain.name
   * @param {string} [options.defaultDatabase]
   */
  ApiHelper.prototype.fetchNavOptTopFilters = function (options) {
    var self = this;
    return self.fetchNavOptCached(NAV_OPT_URLS.TOP_FILTERS, options, function (data) {
      return data.status === 0;
    });
  };

  /**
   * Fetches the popular aggregate functions for the given tables
   *
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   *
   * @param {number} options.timeout
   * @param {Object[]} options.tables
   * @param {Object[]} options.tables.identifierChain
   * @param {string} options.tables.identifierChain.name
   * @param {string} [options.defaultDatabase]
   */
  ApiHelper.prototype.fetchNavOptTopAggs = function (options) {
    var self = this;
    return self.fetchNavOptCached(NAV_OPT_URLS.TOP_AGGS, options, function (data) {
      return data.status === 0;
    });
  };

  ApiHelper.prototype.fetchNavOptCached = function (url, options, cacheCondition) {
    var self = this;

    var performFetch = function (data, hash) {
      var promise = self.queueManager.getQueued(url, hash);
      var firstInQueue = typeof promise === 'undefined';
      if (firstInQueue) {
        promise = $.Deferred();
        self.queueManager.addToQueue(promise, url, hash);
      }

      promise.done(options.successCallback).fail(self.assistErrorCallback(options)).always(function () {
        if (typeof options.editor !== 'undefined' && options.editor !== null) {
          options.editor.hideSpinner();
        }
      });

      if (!firstInQueue) {
        return;
      }

      var fetchFunction = function (storeInCache) {
        if (options.timeout === 0) {
          self.assistErrorCallback(options)({ status: -1 });
          return;
        }

        return $.ajax({
          type: 'post',
          url: url,
          data: data,
          timeout: options.timeout
        })
          .done(function (data) {
            if (data.status === 0) {
              if (cacheCondition(data)) {
                storeInCache(data);
              }
              promise.resolve(data);
            } else {
              promise.reject(data);
            }
          })
          .fail(promise.reject);
      };

      return fetchCached.bind(self)($.extend({}, options, {
        url: url,
        hash: hash,
        cacheType: 'optimizer',
        fetchFunction: fetchFunction,
        promise: promise
      }));
    }

    var promise = $.Deferred();
    if (options.tables) {
      self.createNavOptDbTablesJson(options).done(function (json) {
        promise.resolve(performFetch({
          dbTables: json
        }, json.hashCode()))
      });
    } else if (options.database) {
      promise.resolve(performFetch({
        database: options.database
      }, options.database));
    }
    return promise;
  };

  ApiHelper.prototype.fetchHueDocsInteractive = function (query) {
    var promise = $.Deferred();
    $.post(INTERACTIVE_SEARCH_API, {
      query_s: ko.mapping.toJSON(query),
      limit: 5,
      sources: '["documents"]'
    }).done(function (data) {
      if (data.status === 0) {
        promise.resolve(data);
      } else {
        promise.reject(data);
      }
    }).fail(promise.reject);
    return promise;
  };

  ApiHelper.prototype.fetchNavEntitiesInteractive = function (query) {
    var promise = $.Deferred();
    $.post(INTERACTIVE_SEARCH_API, {
      query_s: ko.mapping.toJSON(query),
      limit: 5,
      sources: '["sql", "hdfs", "s3"]'
    }).done(function (data) {
      if (data.status === 0) {
        promise.resolve(data);
      } else {
        promise.reject(data);
      }
    }).fail(promise.reject);
    return promise;
  };

  ApiHelper.prototype.globalSearchAutocomplete = function (options) {
    var self = this;

    $.when.apply($, [
      $.post(INTERACTIVE_SEARCH_API, {
        query_s: ko.mapping.toJSON(options.query),
        limit: 5,
        sources: '["sql", "hdfs", "s3"]'
      }),
      $.post(INTERACTIVE_SEARCH_API, {
          query_s: ko.mapping.toJSON(options.query),
          limit: 5,
          sources: '["documents"]'
        })
      ]
    ).done(function (metadata, documents) {
      if (metadata[0].status === 0 || documents[0].status === 0) {
        if (documents[0].status === 0) {
           metadata[0].resultsHuedocuments = documents[0].results;
        }
        options.successCallback(metadata[0]);
      } else {
        self.assistErrorCallback(options)(metadata);
      }
    }).fail(self.assistErrorCallback(options));
  };

  ApiHelper.prototype.searchEntities = function (options) {
    var self = this;
    var deferred = $.Deferred();

    $.post(SEARCH_API, {
      query_s: ko.mapping.toJSON(options.query),
      limit: options.limit || 100,
      raw_query: !!options.rawQuery,
      sources: options.sources ? ko.mapping.toJSON(options.sources) : '["sql"]'
	  }).done(function (data) {
      if (data.status === 0 && !self.successResponseIsError(data)) {
        deferred.resolve(data);
      } else {
        self.assistErrorCallback({
          silenceErrors: options.silenceErrors,
          errorCallback: deferred.reject
        })(data);
      }
    }).fail(self.assistErrorCallback({
      silenceErrors: options.silenceErrors,
      errorCallback: deferred.reject
    }));
    return deferred.promise();
  };

  ApiHelper.prototype.formatSql = function (statements) {
    return $.post("/notebook/api/format", {
      statements: statements
    });
  };

  /**
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {string} options.url
   * @param {boolean} [options.noCache]
   * @param {boolean} [options.refreshCache] - Default false
   * @param {Function} options.cacheCondition - Determines whether it should be cached or not
   * @param {Function} options.successCallback
   * @param {Function} options.errorCallback
   * @param {string} [options.cacheType] - Possible values 'default', 'optimizer'. Default value 'default'
   * @param {Number} [options.timeout]
   * @param {boolean} [options.cachedOnly] - Default false
   * @param {Object} [options.editor] - Ace editor
   */
  var fetchAssistData = function (options) {
    var self = this;
    if (!options.sourceType) {
      options.errorCallback('No sourceType supplied');
      console.warn('No sourceType supplied to fetchAssistData');
      return
    }

    if (!options.noCache && !options.refreshCache) {
      var cachedData = $.totalStorage(self.getAssistCacheIdentifier(options)) || {};
      if (typeof cachedData[options.url] !== "undefined" && ! self.hasExpired(cachedData[options.url].timestamp, options.cacheType || 'default')) {
        options.successCallback(cachedData[options.url].data);
        return;
      }
    }
    if (options.cachedOnly) {
      if (options.errorCallback) {
        options.errorCallback(false);
      }
      return;
    }
    if (typeof options.editor !== 'undefined' && options.editor !== null) {
      options.editor.showSpinner();
    }

    var promise = self.queueManager.getQueued(options.url, options.sourceType);
    var firstInQueue = typeof promise === 'undefined';
    if (firstInQueue) {
      promise = $.Deferred();
      self.queueManager.addToQueue(promise, options.url, options.sourceType);
    }

    promise
      .done(function (data) {
        options.successCallback(data)
      })
      .fail(self.assistErrorCallback(options))
      .always(function () {
        if (typeof options.editor !== 'undefined' && options.editor !== null) {
          options.editor.hideSpinner();
        }
      });

    if (!firstInQueue) {
      return;
    }

    if (options.timeout === 0) {
      promise.reject({ status: -1 });
      return;
    }

    return $.ajax({
      type: 'POST',
      url: options.url,
      data: {
        notebook: {},
        snippet: ko.mapping.toJSON({
          type: options.sourceType
        })
      },
      timeout: options.timeout
    }).success(function (data) {
      data.notFound = data.status === 0 && data.code === 500 && data.error && (data.error.indexOf('Error 10001') !== -1 || data.error.indexOf('AnalysisException') !== -1);

      // TODO: Display warning in autocomplete when an entity can't be found
      // Hive example: data.error: [...] SemanticException [Error 10001]: Table not found default.foo
      // Impala example: data.error: [...] AnalysisException: Could not resolve path: 'default.foo'
      if (!data.notFound && self.successResponseIsError(data)) {
        // When not found we at least cache the response to prevent a bunch of unnecessary calls
        promise.reject(data);
      } else {
        // Safe to assume all requests in the queue have the same cacheCondition
        if (!options.noCache && data.status === 0 && options.cacheCondition(data)) {
          var cacheIdentifier = self.getAssistCacheIdentifier(options);
          cachedData = $.totalStorage(cacheIdentifier) || {};
          cachedData[options.url] = {
            timestamp: (new Date()).getTime(),
            data: data
          };
          $.totalStorage(cacheIdentifier, cachedData);
        }
        promise.resolve(data);
      }
    }).fail(promise.reject);
  };

  /**
   *
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {string} options.url
   * @param {string} [options.hash] - Optional hash to use as well as the url
   * @param {Function} options.fetchFunction
   * @param {Function} options.successCallback
   * @param {string} [options.cacheType] - Possible values 'default'|'optimizer'. Default value 'default'
   * @param {Object} [options.editor] - Ace editor
   * @param {Object} [options.promise] - Optional promise that will be resolved if cached data exists
   */
  var fetchCached = function (options) {
    var self = this;
    var cacheIdentifier = self.getAssistCacheIdentifier(options);
    var cachedData = $.totalStorage(cacheIdentifier) || {};
    var cachedId = options.hash ? options.url + options.hash : options.url;

    if (typeof cachedData[cachedId] == "undefined" || self.hasExpired(cachedData[cachedId].timestamp, options.cacheType || 'default')) {
      if (typeof options.editor !== 'undefined' && options.editor !== null) {
        options.editor.showSpinner();
      }
      return options.fetchFunction(function (data) {
        cachedData[cachedId] = {
          timestamp: (new Date()).getTime(),
          data: data
        };
        try {
          $.totalStorage(cacheIdentifier, cachedData);
        } catch (e) {}
      });
    } else {
      if (options.promise) {
        options.promise.resolve(cachedData[cachedId].data)
      }

      options.successCallback(cachedData[cachedId].data);
    }
  };

  var instance = null;

  return {

    /**
     * @returns {ApiHelper}
     */
    getInstance: function () {
      if (instance === null) {
        instance = new ApiHelper();
      }
      return instance;
    }
  };
})();

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

var CancellablePromise = (function () {

  function CancellablePromise(deferred, request, otherCancellables) {
    var self = this;
    self.deferred = deferred;
    self.request = request;
    self.otherCancellables = otherCancellables;
    self.cancelled = false;
    self.cancelPrevented = false;
  }

  /**
   * A promise might be shared across multiple components in the UI, in some cases cancel is not an option and calling
   * this will prevent that to happen.
   *
   * One example is autocompletion of databases while the assist is loading the database tree, closing the autocomplete
   * results would make the assist loading fail if cancel hasn't been prevented.
   *
   * @returns {CancellablePromise}
   */
  CancellablePromise.prototype.preventCancel = function () {
    var self = this;
    self.cancelPrevented = true;
    return self;
  };

  CancellablePromise.prototype.cancel = function () {
    var self = this;
    if (self.cancelPrevented) {
      return;
    }
    self.cancelled = true;
    if (self.request) {
      ApiHelper.getInstance().cancelActiveRequest(self.request);
    }

    if (self.state && self.state() === 'pending' && self.deferred.reject) {
      self.deferred.reject();
    }

    if (self.otherCancellables) {
      self.otherCancellables.forEach(function (cancellable) { if (cancellable.cancel) { cancellable.cancel() } });
    }
    return this;
  };

  CancellablePromise.prototype.then = function () {
    var self = this;
    self.deferred.then.apply(self.deferred, arguments);
    return self;
  };

  CancellablePromise.prototype.done = function (callback) {
    var self = this;
    self.deferred.done.apply(self.deferred, arguments);
    return self;
  };

  CancellablePromise.prototype.fail = function (callback) {
    var self = this;
    self.deferred.fail.apply(self.deferred, arguments);
    return self;
  };

  CancellablePromise.prototype.always = function (callback) {
    var self = this;
    self.deferred.always.apply(self.deferred, arguments);
    return self;
  };

  CancellablePromise.prototype.pipe = function (callback) {
    var self = this;
    self.deferred.pipe.apply(self.deferred, arguments);
    return self;
  };

  CancellablePromise.prototype.progress = function (callback) {
    var self = this;
    self.deferred.progress.apply(self.deferred, arguments);
    return self;
  };

  CancellablePromise.prototype.state = function () {
    var self = this;
    return self.deferred.state && self.deferred.state();
  };

  return CancellablePromise;
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
  var FORMAT_SQL_API = '/notebook/api/format';

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
    TOP_TABLES: '/metadata/api/optimizer/top_tables',
    TABLE_DETAILS: '/metadata/api/optimizer/table_details'
  };

  function ApiHelper () {
    var self = this;
    self.queueManager = ApiQueueManager.getInstance();

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

      if (!options || !options.silenceErrors) {
        hueUtils.logError(errorResponse);
        $(document).trigger("error", errorMessage);
      }

      if (options && options.errorCallback) {
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
      } else if (options && options.successCallback) {
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
    return $.get(url, data, function (data) {
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
          options.successCallback(data);
        } else {
          if (data.status === 1) {
            options.notSupportedCallback(data);
          } else {
            self.assistErrorCallback(options)(data);
          }
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
   * @param {number} options.uuid
   *
   * @return {CancellablePromise}
   */
  ApiHelper.prototype.fetchDocument = function (options) {
    var self = this;
    var deferred = $.Deferred();
    var request = $.ajax({
      url: DOCUMENTS_API,
      data: {
        uuid: options.uuid,
        data: !!options.fetchContents
      },
      success: function (data) {
        if (! self.successResponseIsError(data)) {
          deferred.resolve(data)
        } else {
          deferred.reject(self.assistErrorCallback({
            silenceErrors: options.silenceErrors
          }));
        }
      }
    })
    .fail(function (errorResponse) {
      deferred.reject(self.assistErrorHandler(errorResponse))
    });
    return new CancellablePromise(deferred, request);
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
  ApiHelper.prototype.copyDocument = function (options) {
    var self = this;
    self.simplePost(DOCUMENTS_API + 'copy', {
      uuid: ko.mapping.toJSON(options.uuid)
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
   * @param {string} options.sourceType
   * @param {string} options.invalidate - 'invalidate' or 'invalidateAndFlush'
   * @param {string[]} [options.path]
   * @param {boolean} [options.silenceErrors]
   */
  ApiHelper.prototype.invalidateSourceMetadata = function (options) {
    var self = this;
    var deferred = $.Deferred();

    if (options.sourceType === 'impala' && (options.invalidate === 'invalidate' || options.invalidate === 'invalidateAndFlush')) {
      var data = {
        flush_all: options.invalidate === 'invalidateAndFlush'
      };

      if (options.path && options.path.length > 0) {
        data.database = options.path[0];
      }
      if (options.path && options.path.length > 1) {
        data.table = options.path[1];
      }

      var request = self.simplePost(IMPALA_INVALIDATE_API, data, options).done(deferred.resolve).fail(deferred.reject);

      return new CancellablePromise(deferred, request);
    }

    return deferred.resolve().promise();
  };


  /**
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {boolean} [options.silenceErrors]
   *
   * @param {string[]} [options.path] - The path to fetch
   *
   * @return {CancellablePromise}
   */
  ApiHelper.prototype.fetchSourceMetadata = function (options) {
    var self = this;
    var deferred = $.Deferred();

    var isQuery = options.sourceType.indexOf('-query') !== -1;
    var sourceType = isQuery ? options.sourceType.replace('-query', '') : options.sourceType;

    var request = $.ajax({
      type: 'POST',
      url: AUTOCOMPLETE_API_PREFIX + (isQuery ? options.path.slice(1) : options.path).join('/'),
      data: {
        notebook: {},
        snippet: ko.mapping.toJSON({
          type: sourceType,
          source: isQuery ? 'query' : 'data'
        })
      },
      timeout: options.timeout
    }).success(function (data) {
      data.notFound = data.status === 0 && data.code === 500 && data.error && (data.error.indexOf('Error 10001') !== -1 || data.error.indexOf('AnalysisException') !== -1);
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
    }).fail(self.assistErrorCallback({
      silenceErrors: options.silenceErrors,
      errorCallback: deferred.reject
    }));

    return new CancellablePromise(deferred, request);
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
   * Fetches the analysis for the given source and path
   *
   * @param {Object} options
   * @param {boolean} [options.silenceErrors]
   *
   * @param {string[]} options.path
   *
   * @return {CancellablePromise}
   */
  ApiHelper.prototype.fetchAnalysis = function (options) {
    var self = this;
    var deferred = $.Deferred();

    var url;

    if (options.path.length === 1) {
      url = '/metastore/databases/' + options.path[0] + '/metadata';
    } else {
      url = '/' + (options.sourceType === 'hive' ? 'beeswax' : options.sourceType) + '/api/table/' + options.path[0];

      if (options.path.length > 1) {
        url += '/' + options.path[1];
      }

      if (options.path.length > 2) {
        url += '/stats/' + options.path.slice(2).join('/');
      }
    }

    var request = self.simpleGet(url, {
      'format' : 'json'
    }, {
      silenceErrors: options.silenceErrors,
      successCallback: function (response) {
        if (options.path.length === 1) {
          if (response.data) {
            response.data.hueTimestamp = Date.now();
            deferred.resolve(response.data);
          } else {
            deferred.reject();
          }
        } else {
          deferred.resolve(response)
        }
      },
      errorCallback: deferred.reject
    });

    return new CancellablePromise(deferred, request);
  };

  /**
   * Fetches the partitions for the given path
   *
   * @param {Object} options
   * @param {boolean} [options.silenceErrors]
   *
   * @param {string[]} options.path
   *
   * @return {CancellablePromise}
   */
  ApiHelper.prototype.fetchPartitions = function (options) {
    var self = this;
    var deferred = $.Deferred();

    // TODO: No sourceType needed?
    var request = $.ajax({
      url: '/metastore/table/' + options.path.join('/') + '/partitions',
      data: { format: 'json' },
      success: function (response) {
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
      },
      error: function (response) {
        // Don't report any partitions if it's not partitioned instead of error to prevent unnecessary calls
        if (response && response.responseText && response.responseText.indexOf('is not partitioned') !== -1) {
          deferred.resolve({
            hueTimestamp: Date.now(),
            partition_keys_json: [],
            partition_values_json: []
          })
        } else {
          self.assistErrorCallback({
            silenceErrors: options.silenceErrors,
            errorCallback: deferred.reject
          })(response);
        }
      }
    });

    return new CancellablePromise(deferred, request);
  };

  /**
   * Refreshes the analysis for the given source and path
   *
   * @param {Object} options
   * @param {boolean} [options.silenceErrors]
   *
   * @param {string} options.sourceType
   * @param {string[]} options.path
   *
   * @return {CancellablePromise}
   */
  ApiHelper.prototype.refreshAnalysis = function (options) {
    var self = this;

    if (options.path.length === 1) {
      return self.fetchAnalysis(options);
    }
    var deferred = $.Deferred();

    var promises = [];

    var pollForAnalysis = function (url, delay) {
      window.setTimeout(function () {
        promises.push(self.simplePost(url, undefined, {
          silenceErrors: options.silenceErrors,
          successCallback: function (data) {
            promises.pop();
            if (data.isSuccess) {
              promises.push(self.fetchAnalysis(options).done(deferred.resolve).fail(deferred.reject));
            } else if (data.isFailure) {
              deferred.reject(data);
            } else {
              pollForAnalysis(url, 1000);
            }
          },
          errorCallback: deferred.reject
        }));
      }, delay);
    };

    var url = '/' + (options.sourceType === 'hive' ? 'beeswax' : options.sourceType) + '/api/analyze/' + options.path.join('/') + '/';

    promises.push(self.simplePost(url, undefined, {
      silenceErrors: options.silenceErrors,
      successCallback: function (data) {
        promises.pop();
        if (data.status === 0 && data.watch_url) {
          pollForAnalysis(data.watch_url, 500);
        } else {
          deferred.reject();
        }
      },
      errorCallback: deferred.reject
    }));

    return new CancellablePromise(deferred, undefined, promises);
  };

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
  ApiHelper.prototype.whenAvailable = function (options) {
    var self = this;
    var deferred = $.Deferred();
    var cancellablePromises = [];

    var waitTimeout = -1;

    deferred.fail(function () {
      window.clearTimeout(waitTimeout);
    });

    var waitForAvailable = function () {
      var request = self.simplePost('/notebook/api/check_status', {
        notebook: options.notebookJson,
        snippet: options.snippetJson
      }, {
        silenceErrors: options.silenceErrors
      }).done(function (response) {
        if (response && response.query_status && response.query_status.status) {
          var status = response.query_status.status;
          if (status === 'available') {
            deferred.resolve();
          } else if (status === 'running' || status === 'starting' || status === 'waiting') {
            waitTimeout = window.setTimeout(function () {
              waitForAvailable();
            }, 500);
          } else {
            deferred.reject();
          }
        }
      }).fail(deferred.reject);

      cancellablePromises.push(new CancellablePromise(request, request));
    };

    waitForAvailable();
    return new CancellablePromise(deferred, undefined, cancellablePromises);
  };

  // This is the same as https://github.com/cloudera/hue/blob/master/desktop/libs/dashboard/src/dashboard/static/dashboard/js/search.ko.js#L1783
  var QueryResult = function (vm, initial) { // Similar to to Notebook Snippet
    var self = this;

    self.id = ko.observable(UUID());
    self.type = ko.mapping.fromJS(initial.type);
    self.status = ko.observable(initial.status || 'running');
    self.progress = ko.mapping.fromJS(initial.progress || 0);

    self.hasResultset = ko.observable(true);

    // UI
    self.saveResultsModalVisible = ko.observable(false);

    self.result = ko.mapping.fromJS(initial.result);
    self.result.hasSomeResults = ko.computed(function () {
      return self.hasResultset(); // && self.data().length > 0; // status() == 'available'
    });
    self.result.type = ko.observable('table');

    self.getContext = function() {
      return self;
    }

    self.asyncResult = function() {
      return ko.mapping.toJS(self.result.result);
    }
  };

  /**
   * Fetches samples for the given source and path
   *
   * @param {Object} options
   * @param {boolean} [options.silenceErrors]
   *
   * @param {string} options.sourceType
   * @param {number} [options.sampleCount] - Default 100
   * @param {string[]} options.path
   *
   * @return {CancellablePromise}
   */
  ApiHelper.prototype.fetchSample = function (options) {
    var self = this;
    var deferred = $.Deferred();

    var cancellablePromises = [];

    var notebookJson = null;
    var snippetJson = null;
    var cancelled = false;

    var cancelQuery = function () {
      cancelled = true;
      if (notebookJson) {
        self.simplePost('/notebook/api/cancel_statement', {
          notebook: notebookJson,
          snippet: snippetJson
        }, { silenceErrors:  options.silenceErrors });
      }
    };

    self.simplePost(SAMPLE_API_PREFIX + options.path.join('/'), {
      notebook: {},
      snippet: ko.mapping.toJSON({
        type: options.sourceType
      }),
      async: true
    }, {
      silenceErrors: options.silenceErrors
    }).done(function (sampleResponse) {
      if (sampleResponse.status == 0) {
        var queryResult = new QueryResult(self, {
            type: options.sourceType,
            result: sampleResponse.result,
            status: 'running',
            progress: 0,
        });

        notebookJson = ko.mapping.toJSON({type: queryResult.type()});
        snippetJson = ko.mapping.toJSON(queryResult.getContext());

        cancellablePromises.push(
          self.whenAvailable({ notebookJson: notebookJson, snippetJson: snippetJson, silenceErrors: options.silenceErrors }).done(function () {
            var resultRequest = self.simplePost('/notebook/api/fetch_result_data', {
              notebook: notebookJson,
              snippet: snippetJson,
              rows: options.sampleCount || 100,
              startOver: 'false'
            }, {
              silenceErrors:  options.silenceErrors
            }).done(function (sampleResponse) {
              var data = (sampleResponse && sampleResponse.result) || { data: [], meta: [] };
              data.hueTimestamp = Date.now();
              deferred.resolve(data);
            }).fail(deferred.reject);
            cancellablePromises.push(resultRequest, resultRequest);
          }).fail(deferred.reject)
        );
      } else {
        deferred.reject();
      }
    }).fail(deferred.reject);

    cancellablePromises.push({
      cancel: cancelQuery
    });

    return new CancellablePromise(deferred, undefined, cancellablePromises);
  };

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
  ApiHelper.prototype.fetchNavigatorMetadata = function (options) {
    var self = this;
    var deferred = $.Deferred();
    var url = NAV_URLS.FIND_ENTITY;

    if (options.path.length === 1) {
      url += '?type=database&name=' + options.path[0];
    } else if (options.path.length === 2) {
      url +=  (options.isView ? '?type=view' : '?type=table') + '&database=' + options.path[0] + '&name=' + options.path[1];
    } else if (options.path.length === 3) {
      url +=  '?type=field&database=' + options.path[0] + '&table=' + options.path[1] + '&name=' + options.path[2];
    } else {
      return new CancellablePromise($.Deferred().reject());
    }

    var request = self.simplePost(url, {
      notebook: {},
      snippet: ko.mapping.toJSON({
        type: 'nav'
      })
    }, {
      silenceErrors: options.silenceErrors,
      successCallback: function (data) {
        data = data.entity || data;
        data.hueTimestamp = Date.now();
        deferred.resolve(data);
      },
      errorCallback: deferred.reject
    });

    return new CancellablePromise(deferred, request);
  };

  ApiHelper.prototype.updateNavigatorMetadata = function (options) {
    var self = this;
    return self.simplePost(NAV_URLS.UPDATE_PROPERTIES, {
      id: ko.mapping.toJSON(options.identity),
      properties: ko.mapping.toJSON(options.properties)
    }, options)
  };

  /**
   * Lists all available navigator tags
   *
   * @param {Object} options
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   *
   * @return {CancellablePromise}
   */
  ApiHelper.prototype.fetchAllNavigatorTags = function (options) {
    var self = this;

    var deferred = $.Deferred();

    var request = self.simplePost(NAV_URLS.LIST_TAGS, undefined, {
      silenceErrors: options.silenceErrors,
      successCallback: function (data) {
        if (data && data.tags) {
          deferred.resolve(data.tags);
        } else {
          deferred.resolve({});
        }
      },
      errorCallback: deferred.reject
    });

    return new CancellablePromise(deferred, request);
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
   * Fetches navOpt popularity for the children of the given path
   *
   * @param {Object} options
   * @param {boolean} [options.silenceErrors]
   * @param {string[][]} options.paths
   * @return {CancellablePromise}
   */
  ApiHelper.prototype.fetchNavOptPopularity = function (options) {
    var self = this;
    var deferred = $.Deferred();
    var url, data;

    if (options.paths.length === 1 && options.paths[0].length === 1) {
      url = NAV_OPT_URLS.TOP_TABLES;
      data = {
        database: options.paths[0][0]
      };
    } else {
      url = NAV_OPT_URLS.TOP_COLUMNS;
      var dbTables = [];
      options.paths.forEach(function (path) {
        dbTables.push(path.join('.'));
      });
      data = {
        dbTables: ko.mapping.toJSON(dbTables)
      };
    }

    var request = self.simplePost(url, data, {
      silenceErrors: options.silenceErrors,
      successCallback: function (data) {
        data.hueTimestamp = Date.now();
        deferred.resolve(data);
      },
      errorCallback: deferred.reject
    });

    return new CancellablePromise(deferred, request);
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
  var genericNavOptMultiTableFetch = function (apiHelper, options, url) {
    var deferred = $.Deferred();

    var dbTables = {};
    options.paths.forEach(function (path) {
      dbTables[path.join('.')] = true;
    });
    var data = {
      dbTables: ko.mapping.toJSON(Object.keys(dbTables))
    };

    var request = apiHelper.simplePost(url, data, {
      silenceErrors: options.silenceErrors,
      successCallback: function (data) {
        data.hueTimestamp = Date.now();
        deferred.resolve(data);
      },
      errorCallback: deferred.reject
    });

    return new CancellablePromise(deferred, request);
  };

  /**
   * Fetches the popular aggregate functions for the given tables
   *
   * @param {Object} options
   * @param {boolean} [options.silenceErrors]
   * @param {string[][]} options.paths
   * @return {CancellablePromise}
   */
  ApiHelper.prototype.fetchNavOptTopAggs = function (options) {
    return genericNavOptMultiTableFetch(this, options, NAV_OPT_URLS.TOP_AGGS);
  };

  /**
   * Fetches the popular columns for the given tables
   *
   * @param {Object} options
   * @param {boolean} [options.silenceErrors]
   * @param {string[][]} options.paths
   * @return {CancellablePromise}
   */
  ApiHelper.prototype.fetchNavOptTopColumns = function (options) {
    return genericNavOptMultiTableFetch(this, options, NAV_OPT_URLS.TOP_COLUMNS);
  };

  /**
   * Fetches the popular filters for the given tables
   *
   * @param {Object} options
   * @param {boolean} [options.silenceErrors]
   * @param {string[][]} options.paths
   * @return {CancellablePromise}
   */
  ApiHelper.prototype.fetchNavOptTopFilters = function (options) {
    return genericNavOptMultiTableFetch(this, options, NAV_OPT_URLS.TOP_FILTERS);
  };

  /**
   * Fetches the popular joins for the given tables
   *
   * @param {Object} options
   * @param {boolean} [options.silenceErrors]
   * @param {string[][]} options.paths
   * @return {CancellablePromise}
   */
  ApiHelper.prototype.fetchNavOptTopJoins = function (options) {
    return genericNavOptMultiTableFetch(this, options, NAV_OPT_URLS.TOP_JOINS);
  };

  /**
   * Fetches navOpt meta for the given path, only possible for tables atm.
   *
   * @param {Object} options
   * @param {boolean} [options.silenceErrors]
   * @param {string[]} options.path
   *
   * @return {CancellablePromise}
   */
  ApiHelper.prototype.fetchNavOptMeta = function (options) {
    var self = this;
    var deferred = $.Deferred();

    var request = self.simplePost(NAV_OPT_URLS.TABLE_DETAILS, {
      databaseName: options.path[0],
      tableName: options.path[1]
    }, {
      silenceErrors: options.silenceErrors,
      successCallback: function (response) {
        if (response.status === 0 && response.details) {
          response.details.hueTimestamp = Date.now();
          deferred.resolve(response.details);
        } else {
          deferred.reject();
        }
      },
      errorCallback: deferred.reject
    });

    return new CancellablePromise(deferred, request);
  };

  ApiHelper.prototype.getClusterConfig = function (data) {
    return $.post(FETCH_CONFIG, data);
  };

  ApiHelper.prototype.fetchHueDocsInteractive = function (query) {
    var deferred = $.Deferred();
    var request = $.post(INTERACTIVE_SEARCH_API, {
      query_s: ko.mapping.toJSON(query),
      limit: 50,
      sources: '["documents"]'
    }).done(function (data) {
      if (data.status === 0) {
        deferred.resolve(data);
      } else {
        deferred.reject(data);
      }
    }).fail(deferred.reject);
    return new CancellablePromise(deferred, request);
  };

  ApiHelper.prototype.fetchNavEntitiesInteractive = function (query) {
    var deferred = $.Deferred();
    var request = $.post(INTERACTIVE_SEARCH_API, {
      query_s: ko.mapping.toJSON(query),
      limit: 50,
      sources: '["sql", "hdfs", "s3"]'
    }).done(function (data) {
      if (data.status === 0) {
        deferred.resolve(data);
      } else {
        deferred.reject(data);
      }
    }).fail(deferred.reject);
    return new CancellablePromise(deferred, request);
  };

  ApiHelper.prototype.searchEntities = function (options) {
    var self = this;
    var deferred = $.Deferred();

    var request = self.simplePost(SEARCH_API, {
      query_s: ko.mapping.toJSON(options.query),
      limit: options.limit || 100,
      raw_query: !!options.rawQuery,
      sources: options.sources ? ko.mapping.toJSON(options.sources) : '["sql"]'
    }, {
      silenceErrors: options.silenceErrors,
      successCallback: deferred.resolve,
      errorCallback: deferred.reject
    });

    return new CancellablePromise(deferred, request);
  };

  /**
   *
   * @param {Object} options
   * @param {string} options.statements
   * @param {boolean} [options.silenceErrors]
   */
  ApiHelper.prototype.formatSql = function (options) {
    var self = this;
    var deferred = $.Deferred();

    var request = self.simplePost(FORMAT_SQL_API, {
      statements: options.statements
    }, {
      silenceErrors: options.silenceErrors,
      successCallback: deferred.resolve,
      errorCallback: deferred.reject
    });

    return new CancellablePromise(deferred, request);
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
  var fetchCached = function (options) {
    var self = this;
    var cacheIdentifier = self.getAssistCacheIdentifier(options);
    var cachedData = $.totalStorage(cacheIdentifier) || {};
    var cachedId = options.hash ? options.url + options.hash : options.url;

    if (options.refreshCache || typeof cachedData[cachedId] == "undefined" || self.hasExpired(cachedData[cachedId].timestamp, options.cacheType || 'default')) {
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

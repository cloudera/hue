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

(function (root, factory) {
  if(typeof define === "function" && define.amd) {
    define(['knockout'], factory);
  } else {
    root.ApiHelper = factory(ko);
  }
}(this, function (ko) {

  var TIME_TO_LIVE_IN_MILLIS = $.totalStorage('hue.cacheable.ttl.override') || $.totalStorage('hue.cacheable.ttl'); // 1 day by default, configurable with desktop.custom.cacheable_ttl in the .ini or $.totalStorage('hue.cacheable.ttl.override', 1234567890)

  var AUTOCOMPLETE_API_PREFIX = "/notebook/api/autocomplete/";
  var SAMPLE_API_PREFIX = "/notebook/api/sample/";
  var DOCUMENTS_API = "/desktop/api2/doc/";
  var DOCUMENTS_SEARCH_API = "/desktop/api2/docs/";
  var HDFS_API_PREFIX = "/filebrowser/view=";
  var HDFS_PARAMETERS = "?pagesize=100&format=json";
  var IMPALA_INVALIDATE_API = '/impala/api/invalidate';
  var CONFIG_SAVE_API = '/desktop/api/configurations/save/';
  var CONFIG_APPS_API = '/desktop/api/configurations/apps';

  /**
   * @param {Object} i18n
   * @param {string} i18n.errorLoadingDatabases
   * @param {string} i18n.errorLoadingTablePreview
   * @param {string} user
   *
   * @constructor
   */
  function ApiHelper (i18n, user) {
    var self = this;
    self.i18n = i18n;
    self.user = user;
    self.lastKnownDatabases = {};
    self.fetchQueue = {};
    self.invalidateImpala = 'cache';

    huePubSub.subscribe('assist.clear.db.cache', function (options) {
      self.clearDbCache(options);
    });

    huePubSub.subscribe('assist.clear.hdfs.cache', function () {
      $.totalStorage("hue.assist." + self.getTotalStorageUserPrefix('hdfs'), {});
    });
  }

  ApiHelper.prototype.hasExpired = function (timestamp) {
    return (new Date()).getTime() - timestamp > TIME_TO_LIVE_IN_MILLIS;
  };

  /**
   * @param {string} sourceType
   * @returns {string}
   */
  ApiHelper.prototype.getTotalStorageUserPrefix = function (sourceType) {
    var self = this;
    return sourceType + "_" + self.user;
  };

  /**
   *
   * @param {string} owner - 'assist', 'viewModelA' etc.
   * @param {string} id
   * @param {*} [value] - Optional, undefined and null will remove the value
   */
  ApiHelper.prototype.setInTotalStorage = function(owner, id, value) {
    var self = this;
    var cachedData = $.totalStorage("hue.user.settings." + self.getTotalStorageUserPrefix(owner)) || {};
    if (typeof value !== 'undefined' && value !== null) {
      cachedData[id] = value;
      $.totalStorage("hue.user.settings." + self.getTotalStorageUserPrefix(owner), cachedData);
    } else if (cachedData[id]) {
      delete cachedData[id];
      $.totalStorage("hue.user.settings." + self.getTotalStorageUserPrefix(owner), cachedData);
    }
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
  };

  /**
   * @param {Object} [response]
   * @param {number} [response.status]
   * @returns {boolean} - True if actually an error
   */
  ApiHelper.prototype.successResponseIsError = function (response) {
    return typeof response !== 'undefined' && (response.status === -1 || response.status === 500 || response.code === 503 || response.code === 500);
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
      if (errorResponse !== 'undefined') {
        if (typeof errorResponse.responseText !== 'undefined') {
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
        } else if (typeof errorResponse.message !== 'undefined') {
          errorMessage = errorResponse.message;
        } else if (typeof errorResponse.statusText !== 'undefined') {
          errorMessage = errorResponse.statusText;
        } else if (errorResponse.error !== 'undefined' && toString.call(errorResponse.error) === '[object String]' ) {
          errorMessage = errorResponse.error;
        } else if (toString.call(errorResponse) === '[object String]') {
          errorMessage = errorResponse;
        }
      }

      if (! options.silenceErrors) {
        if (typeof window.console !== 'undefined') {
          console.error(errorResponse);
          console.error(new Error().stack);
        }
        $(document).trigger("error", errorMessage);
      }

      if (options.errorCallback) {
        options.errorCallback(errorMessage);
      }
    };
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
    $.post(url, data, function (data) {
      if (self.successResponseIsError(data)) {
        self.assistErrorCallback(options)(data);
      } else if (typeof options.successCallback !== 'undefined') {
        options.successCallback(data);
      }
    })
    .fail(self.assistErrorCallback(options));
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
    self.simpleGet('/desktop/api/users/autocomplete', {}, options);
  };

  /**
   * @param {Object} options
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   * @param {Object} [options.editor] - Ace editor
   *
   * @param {string[]} options.pathParts
   */
  ApiHelper.prototype.fetchHdfsPath = function (options) {
    var self = this;
    var url = HDFS_API_PREFIX + "/" + options.pathParts.join("/") + HDFS_PARAMETERS;

    var fetchFunction = function (storeInCache) {
      $.ajax({
        dataType: "json",
        url: url,
        success: function (data) {
          if (!data.error && !self.successResponseIsError(data) && typeof data.files !== 'undefined' && data.files !== null) {
            if (data.files.length > 2) {
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
      sourceType: 'hdfs',
      url: url,
      fetchFunction: fetchFunction
    }));
  };

  ApiHelper.prototype.getFetchQueue = function (fetchFunction, identifier) {
    var self = this;
    if (! self.fetchQueue[fetchFunction]) {
      self.fetchQueue[fetchFunction] = {};
    }
    var queueForFunction = self.fetchQueue[fetchFunction];

    var id = typeof identifier === 'undefined' || identifier === null ? 'DEFAULT_QUEUE' : identifier;

    if (! queueForFunction[id]) {
      queueForFunction[id] = [];
    }
    return queueForFunction[id];
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

    var queue = self.getFetchQueue('fetchDocuments', options.uuid);
    queue.push(options);
    if (queue.length > 1) {
      return;
    }

    $.ajax({
      url: DOCUMENTS_API,
      data: {
        uuid: options.uuid
      },
      success: function (data) {
        while (queue.length > 0) {
          var next = queue.shift();
          if (! self.successResponseIsError(data)) {
            next.successCallback(data);
          } else {
            self.assistErrorCallback(next)(data);
          }
        }
      }
    })
    .fail(function (response) {
      while (queue.length > 0) {
        var next = queue.shift();
        self.assistErrorCallback(next)(response);
      }
    });
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
    $.ajax({
      url: DOCUMENTS_SEARCH_API,
      data: {
        uuid: options.uuid,
        text: options.query,
        type: options.type,
        page: options.page,
        limit: options.limit
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
   *
   * @param {number} options.uuid
   */
  ApiHelper.prototype.fetchDocument = function (options) {
    var self = this;
    $.ajax({
      url: DOCUMENTS_API,
      data: {
        uuid: options.uuid
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
   *
   * @param {string} options.parentUuid
   * @param {string} options.name
   */
  ApiHelper.prototype.createDocumentsFolder = function (options) {
    var self = this;
    self.simplePost("/desktop/api2/doc/mkdir", {
      parent_uuid: ko.mapping.toJSON(options.parentUuid),
      name: ko.mapping.toJSON(options.name)
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
      url: '/desktop/api2/doc/import',
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
    self.simplePost("/desktop/api2/doc/move", {
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
    self.simplePost("/desktop/api2/doc/delete", {
      uuid: ko.mapping.toJSON(options.uuid),
      skip_trash: ko.mapping.toJSON(options.skipTrash || false)
    }, options);
  };

  /**
   *
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {string} [options.databaseName]
   * @param {boolean} [options.invalidateImpala]
   * @param {string} [options.tableName]
   * @param {string[]} [options.fields]
   * @param {boolean} [options.clearAll]
   */
  ApiHelper.prototype.clearDbCache = function (options) {
    var self = this;
    self.invalidateImpala = options.invalidateImpala || 'cache';
    if (options.clearAll) {
      $.totalStorage("hue.assist." + self.getTotalStorageUserPrefix(options.sourceType), {});
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
      var cachedData = $.totalStorage("hue.assist." + self.getTotalStorageUserPrefix(options.sourceType)) || {};
      delete cachedData[url];
      $.totalStorage("hue.assist." + self.getTotalStorageUserPrefix(options.sourceType), cachedData);
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
      self.invalidateImpala = 'cache';
      fetchAssistData.bind(self)($.extend({}, options, {
        url: AUTOCOMPLETE_API_PREFIX,
        successCallback: function (data) {
          var databases = data.databases || [];
          // Blacklist of system databases
          self.lastKnownDatabases[options.sourceType] = $.grep(databases, function (database) {
            return database !== "_impala_builtins";
          });
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
        cacheCondition: function (data) {
          return typeof data !== 'undefined' && data !== null && typeof data.databases !== 'undefined' && data.databases !== null && data.databases.length > 0;
        }
      }));
    };

    if (options.sourceType === 'impala' && self.invalidateImpala == 'invalidateAndFlush') {
      $.post(IMPALA_INVALIDATE_API, { flush_all: true, database: options.database }, loadFunction);
    } else if (options.sourceType === 'impala' && self.invalidateImpala == 'invalidate') {
      $.post(IMPALA_INVALIDATE_API, { flush_all: false, database: options.database }, loadFunction);
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
   */
  ApiHelper.prototype.fetchPartitions = function (options) {
    var self = this;
    $.ajax({
      url: "/metastore/table/" + options.databaseName + "/" + options.tableName + "/partitions",
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
   * @param {string} [options.columnName]
   * @param {Object} [options.editor] - Ace editor
   */
  ApiHelper.prototype.fetchTableSample = function (options) {
    var self = this;
    var url = SAMPLE_API_PREFIX + options.databaseName + '/' + options.tableName + (options.columnName ? '/' + options.columnName : '');

    var fetchFunction = function (storeInCache) {
      $.post(url, {
        notebook: {},
        snippet: ko.mapping.toJSON({
          type: options.sourceType
        })
      })
      .done(function (data) {
        if (! self.successResponseIsError(data)) {
          if (data.rows.length > 0) {
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
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   *
   * @param {Object} [options.prefixFilter]
   * @param {string} options.databaseName
   * @param {string} options.tableName
   * @param {string} options.columnName
   */
  ApiHelper.prototype.fetchTerms = function (options) {
    var self = this;
    $.ajax({
      url: "/" + options.sourceType + "/api/table/" + options.databaseName + "/" + options.tableName + "/terms/" + options.columnName + "/" + (options.prefixFilter || ""),
      data: {},
      beforeSend: function (xhr) {
        xhr.setRequestHeader("X-Requested-With", "Hue");
      },
      dataType: "json",
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
   * @param {Object} [options.editor] - Ace editor
   *
   * @param {string} options.databaseName
   */
  ApiHelper.prototype.fetchTables = function (options) {
    var self = this;
    fetchAssistData.bind(self)($.extend({}, options, {
      url: AUTOCOMPLETE_API_PREFIX + options.databaseName,
      errorCallback: self.assistErrorCallback(options),
      cacheCondition: function (data) {
        return typeof data !== 'undefined' && data !== null && typeof data.tables_meta !== 'undefined' && data.tables_meta !== null && data.tables_meta.length > 0;
      }
    }));
  };

  var fieldCacheCondition = function (data) {
    if (typeof data !== 'undefined' && data !== null) {
      return (typeof data.item !== 'undefined' && data.item !== null) ||
          (typeof data.key !== 'undefined' && data.key !== null) ||
          (typeof data.tables_meta !== 'undefined' && data.tables_meta !== null && data.tables_meta.length > 0) ||
          (typeof data.extended_columns !== 'undefined' && data.extended_columns !== null && data.extended_columns.length > 0) ||
          (typeof data.columns !== 'undefined' && data.columns !== null && data.columns.length > 0) ||
          (typeof data.fields !== 'undefined' && data.fields !== null && data.fields.length > 0)
    }
    return false;
  };

  /**
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   * @param {Object} [options.editor] - Ace editor
   *
   * @param {string} options.databaseName
   * @param {string} options.tableName
   * @param {string[]} options.fields
   */
  ApiHelper.prototype.fetchFields = function (options) {
    var self = this;
    var fieldPart = options.fields.length > 0 ? "/" + options.fields.join("/") : "";
    fetchAssistData.bind(self)($.extend({}, options, {
      url: AUTOCOMPLETE_API_PREFIX + options.databaseName + "/" + options.tableName + fieldPart,
      errorCallback: self.assistErrorCallback(options),
      cacheCondition: fieldCacheCondition
    }));
  };

  /**
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   *
   * @param {string[]} options.hierarchy
   */
  ApiHelper.prototype.fetchPanelData = function (options) {
    var self = this;
    fetchAssistData.bind(self)($.extend({}, options, {
      url: AUTOCOMPLETE_API_PREFIX + options.hierarchy.join("/"),
      errorCallback: self.assistErrorCallback(options),
      cacheCondition: fieldCacheCondition
    }));
  };

  /**
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {string} options.url
   * @param {Function} options.cacheCondition - Determines whether it should be cached or not
   * @param {Function} options.successCallback
   * @param {Function} options.errorCallback
   * @param {Object} [options.editor] - Ace editor
   */
  var fetchAssistData = function (options) {
    var self = this;
    if (!options.sourceType) {
      return
    }

    var cachedData = $.totalStorage("hue.assist." + self.getTotalStorageUserPrefix(options.sourceType)) || {};
    if (typeof cachedData[options.url] !== "undefined" && ! self.hasExpired(cachedData[options.url].timestamp)) {
      options.successCallback(cachedData[options.url].data);
      return;
    }
    if (typeof options.editor !== 'undefined' && options.editor !== null) {
      options.editor.showSpinner();
    }

    var queue = self.getFetchQueue('fetchAssistData', options.sourceType + '_' + options.url);
    queue.push(options);
    if (queue.length > 1) {
      return;
    }

    $.post(options.url, {
      notebook: {},
      snippet: ko.mapping.toJSON({
        type: options.sourceType
      })
    }, function (data) {
      // Safe to assume all requests in the queue have the same cacheCondition
      if (data.status === 0 && !self.successResponseIsError(data) && options.cacheCondition(data)) {
        cachedData[options.url] = {
          timestamp: (new Date()).getTime(),
          data: data
        };
        $.totalStorage("hue.assist." + self.getTotalStorageUserPrefix(options.sourceType), cachedData);
      }
      while (queue.length > 0) {
        var next = queue.shift();
        if (data.status === 0 && !self.successResponseIsError(data)) {
          next.successCallback(data);
        } else {
          next.errorCallback(data);
        }
        if (typeof next.editor !== 'undefined' && next.editor !== null) {
          next.editor.hideSpinner();
        }
      }
    }).fail(function (data) {
      while (queue.length > 0) {
        var next = queue.shift();
        next.errorCallback(data);
        if (typeof next.editor !== 'undefined' && next.editor !== null) {
          next.editor.hideSpinner();
        }
      }
    });
  };

  /**
   *
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {string} options.url
   * @param {Function} options.fetchFunction
   * @param {Function} options.successCallback
   * @param {Object} [options.editor] - Ace editor
   */
  var fetchCached = function (options) {
    var self = this;
    var cachedData = $.totalStorage("hue.assist." + self.getTotalStorageUserPrefix(options.sourceType)) || {};

    if (typeof cachedData[options.url] == "undefined" || self.hasExpired(cachedData[options.url].timestamp)) {
      if (typeof options.editor !== 'undefined' && options.editor !== null) {
        options.editor.showSpinner();
      }
      options.fetchFunction(function (data) {
        cachedData[options.url] = {
          timestamp: (new Date()).getTime(),
          data: data
        };
        $.totalStorage("hue.assist." + self.getTotalStorageUserPrefix(options.sourceType), cachedData);
      });
    } else {
      options.successCallback(cachedData[options.url].data);
    }
  };

  var instance = null;

  return {

    /**
     * @param {Object} options
     * @param {Object} options.i18n
     * @param {string} options.i18n.errorLoadingDatabases
     * @param {string} options.i18n.errorLoadingTablePreview
     * @param {string} options.user
     *
     * @returns {ApiHelper}
     */
    getInstance: function (options) {
      if (instance === null) {
        instance = new ApiHelper(options.i18n, options.user);
      }
      return instance;
    }
  };
}));

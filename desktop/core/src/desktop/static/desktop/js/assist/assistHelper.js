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
    root.AssistHelper = factory(ko);
  }
}(this, function (ko) {

  var TIME_TO_LIVE_IN_MILLIS = 86400000; // 1 day
  var AUTOCOMPLETE_API_PREFIX = "/notebook/api/autocomplete/";
  var HDFS_API_PREFIX = "/filebrowser/view=";
  var HDFS_PARAMETERS = "?pagesize=100&format=json";
  var DOCUMENTS_API = "/desktop/api2/docs/";
  var DOCUMENT_API = "/desktop/api2/doc/get";


  /**
   * @param {Object} i18n
   * @param {string} i18n.errorLoadingDatabases
   * @param {string} i18n.errorLoadingTablePreview
   * @param {string} user
   *
   * @constructor
   */
  function AssistHelper (i18n, user) {
    var self = this;
    self.i18n = i18n;
    self.user = user;
    self.lastKnownDatabases = {};
  }

  AssistHelper.prototype.hasExpired = function (timestamp) {
    return (new Date()).getTime() - timestamp > TIME_TO_LIVE_IN_MILLIS;
  };

  /**
   * @param {string} sourceType
   * @returns {string}
   */
  AssistHelper.prototype.getTotalStorageUserPrefix = function (sourceType) {
    var self = this;
    return sourceType + "_" + self.user;
  };

  /**
   *
   * @param {string} owner - 'assist', 'viewModelA' etc.
   * @param {string} id
   * @param {*} [value] - Optional, undefined and null will remove the value
   */
  AssistHelper.prototype.setInTotalStorage = function(owner, id, value) {
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
  AssistHelper.prototype.getFromTotalStorage = function(owner, id, defaultValue) {
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
  AssistHelper.prototype.withTotalStorage = function(owner, id, observable, defaultValue, noInit) {
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
  AssistHelper.prototype.successResponseIsError = function (response) {
    return typeof response !== 'undefined' && (response.status === -1 || response.status === 500);
  };

  /**
   * @param {Object} options
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   * @returns {Function}
   */
  AssistHelper.prototype.assistErrorCallback = function (options) {
    return function (errorResponse) {
      var errorMessage = 'Unknown error occurred';
      if (errorResponse !== 'undefined') {
        if (typeof errorResponse.message !== 'undefined') {
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
   * @param {Object} options
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   * @param {Object} [options.editor] - Ace editor
   *
   * @param {string[]} options.pathParts
   */
  AssistHelper.prototype.fetchHdfsPath = function (options) {
    var self = this;
    var url = HDFS_API_PREFIX + "/" + options.pathParts.join("/") + HDFS_PARAMETERS;

    var fetchFunction = function (successCallback) {
      $.ajax({
        dataType: "json",
        url: url,
        success: function (data) {
          if (!data.error && !self.successResponseIsError(data)) {
            successCallback(data);
          } else {
            self.assistErrorCallback(options)(data);
          }
        }
      })
        .fail(self.assistErrorCallback(options))
        .always(function () {
          if (options.editor) {
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

  /**
   * @param {Object} options
   * @param {Function} options.successCallback
   * @param {Function} [options.errorCallback]
   * @param {boolean} [options.silenceErrors]
   *
   * @param {string} [options.path]
   */
  AssistHelper.prototype.fetchDocuments = function (options) {
    var self = this;
    $.ajax({
      url: DOCUMENTS_API,
      data: {
        path: options.path
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
   * @param {string} [options.path]
   * @param {string} options.query
   */
  AssistHelper.prototype.searchDocuments = function (options) {
    var self = this;
    $.ajax({
          url: DOCUMENTS_API,
          data: {
            path: options.path,
            text: options.query
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
   * @param {number} options.docId
   */
  AssistHelper.prototype.fetchDocument = function (options) {
    var self = this;
    $.ajax({
      url: DOCUMENT_API,
      data: {
        id: options.docId
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
   * @param {string} options.path
   * @param {string} options.name
   */
  AssistHelper.prototype.createDocumentsFolder = function (options) {
    var self = this;
    $.post("/desktop/api2/doc/mkdir", {
      parent_path: ko.mapping.toJSON(options.path),
      name: ko.mapping.toJSON(options.name)
    }, function (data) {
      if (! self.successResponseIsError(data)) {
        options.successCallback(data);
      } else {
        self.assistErrorCallback(options)(data);
      }
    })
      .fail(self.assistErrorCallback(options));
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
  AssistHelper.prototype.uploadDocument = function (options) {
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
  AssistHelper.prototype.moveDocument = function (options) {
    var self = this;
    $.post("/desktop/api2/doc/move", {
      source_doc_id: ko.mapping.toJSON(options.sourceId),
      destination_doc_id: ko.mapping.toJSON(options.destinationId)
    }, function (data) {
      if (! self.successResponseIsError(data)) {
        options.successCallback(data);
      } else {
        self.assistErrorCallback(options)(data);
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
   * @param {string} options.id
   * @param {string} [options.skipTrash] - Default false
   */
  AssistHelper.prototype.deleteDocument = function (options) {
    var self = this;
    $.post("/desktop/api2/doc/delete", {
      doc_id: ko.mapping.toJSON(options.id),
      skip_trash: ko.mapping.toJSON(options.skipTrash || false)
    }, function (data) {
      if (! self.successResponseIsError(data)) {
        options.successCallback(data);
      } else {
        self.assistErrorCallback(options)(data);
      }
    })
      .fail(self.assistErrorCallback(options));
  };

  /**
   *
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {string} [options.databaseName]
   * @param {string} [options.tableName]
   * @param {string[]} [options.fields]
   * @param {boolean} [options.clearAll]
   */
  AssistHelper.prototype.clearCache = function (options) {
    var self = this;
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
   **/
  AssistHelper.prototype.loadDatabases = function (options) {
    var self = this;

    fetchAssistData.bind(self)($.extend({}, options, {
      url: AUTOCOMPLETE_API_PREFIX,
      successCallback: function (data) {
        var databases = data.databases || [];
        // Blacklist of system databases
        self.lastKnownDatabases[options.sourceType] = $.grep(databases, function(database) {
          return database !== "_impala_builtins";
        });
        options.successCallback(self.lastKnownDatabases[options.sourceType]);
      },
      errorCallback: function (response) {
        if (response.status == 401) {
          $(document).trigger("showAuthModal", {'type': options.sourceType, 'callback': function() {
            self.loadDatabases(options);
          }});
          return;
        }
        self.lastKnownDatabases[options.sourceType] = [];
        self.assistErrorCallback(options)(response);
      }
    }));
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
  AssistHelper.prototype.fetchPartitions = function (options) {
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
  AssistHelper.prototype.fetchTableDetails = function (options) {
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
   * @param {string} options.dataType - html or json
   */
  AssistHelper.prototype.fetchTableSample = function (options) {
    var self = this;
    $.ajax({
      url: "/" + (options.sourceType == "hive" ? "beeswax" : options.sourceType) + "/api/table/" + options.databaseName + "/" + options.tableName + "/sample",
      data: {},
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
   * @param {string} options.columnName
   */
  AssistHelper.prototype.refreshTableStats = function (options) {
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
      })
        .fail(self.assistErrorCallback(options));
    };

    $.post("/" + (options.sourceType == "hive" ? "beeswax" : options.sourceType) + "/api/analyze/" + options.databaseName + "/" + options.tableName + "/"  + (options.columnName || ""), function (data) {
      if (data.status == 0 && data.watch_url) {
        pollRefresh(data.watch_url);
      } else {
        self.assistErrorCallback(options)(data);
      }
    })
      .fail(self.assistErrorCallback(options));
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
  AssistHelper.prototype.fetchStats = function (options) {
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
  AssistHelper.prototype.fetchTerms = function (options) {
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
  AssistHelper.prototype.fetchTables = function (options) {
    var self = this;
    fetchAssistData.bind(self)($.extend({}, options, {
      url: AUTOCOMPLETE_API_PREFIX + options.databaseName,
      errorCallback: self.assistErrorCallback(options)
    }));
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
  AssistHelper.prototype.fetchFields = function (options) {
    var self = this;
    var fieldPart = options.fields.length > 0 ? "/" + options.fields.join("/") : "";
    fetchAssistData.bind(self)($.extend({}, options, {
      url: AUTOCOMPLETE_API_PREFIX + options.databaseName + "/" + options.tableName + fieldPart,
      errorCallback: self.assistErrorCallback(options)
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
  AssistHelper.prototype.fetchPanelData = function (options) {
    var self = this;
    fetchAssistData.bind(self)($.extend({}, options, {
      url: AUTOCOMPLETE_API_PREFIX + options.hierarchy.join("/"),
      errorCallback: self.assistErrorCallback(options)
    }));
  };

  /**
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {string} options.url
   * @param {Function} options.successCallback
   * @param {Function} options.errorCallback
   * @param {Object} [options.editor] - Ace editor
   */
  var fetchAssistData = function (options) {
    var self = this;
    if (!options.sourceType) {
      return
    }

    fetchCached.bind(self)($.extend(options, {
      fetchFunction: function (successCallback) {
        $.post(options.url, {
          notebook: {},
          snippet: ko.mapping.toJSON({
            type: options.sourceType
          })
        }, function (data) {
          if (data.status === 0) {
            successCallback(data);
          } else {
            options.errorCallback(data);
          }
        }).fail(options.errorCallback).always(function () {
          if (options.editor) {
            options.editor.hideSpinner();
          }
        });
      }
    }));
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
      if (options.editor) {
        options.editor.showSpinner();
      }
      options.fetchFunction(function (data) {
        cachedData[options.url] = {
          timestamp: (new Date()).getTime(),
          data: data
        };
        $.totalStorage("hue.assist." + self.getTotalStorageUserPrefix(options.sourceType), cachedData);
        options.successCallback(data);
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
     * @returns {AssistHelper}
     */
    getInstance: function (options) {
      if (instance === null) {
        instance = new AssistHelper(options.i18n, options.user);
      }
      return instance;
    }
  };
}));

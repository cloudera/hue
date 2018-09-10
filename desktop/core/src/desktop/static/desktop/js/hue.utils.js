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

/*
 * Array polyfills
*/
if (!('clean' in Array.prototype)) {
  Array.prototype.clean = function (deleteValue) {
    for (var i = 0; i < this.length; i++) {
      if (this[i] == deleteValue) {
        this.splice(i, 1);
        i--;
      }
    }
    return this;
  };
}

if (!('move' in Array.prototype)) {
  Array.prototype.move = function (old_index, new_index) {
    if (new_index >= this.length) {
      var k = new_index - this.length;
      while ((k--) + 1) {
        this.push(undefined);
      }
    }
    this.splice(new_index, 0, this.splice(old_index, 1)[0]);
    return this;
  };
}

if (!('indexOf' in Array.prototype)) {
  Array.prototype.indexOf = function (needle) {
    for (var i = 0; i < this.length; i++) {
      if (this[i] === needle) {
        return i;
      }
    }
    return -1;
  };
}

if (!('filter' in Array.prototype)) {
  Array.prototype.filter = function (filter, that /*opt*/) {
    var other = [], v;
    for (var i = 0, n = this.length; i < n; i++) {
      if (i in this && filter.call(that, v = this[i], i, this)) {
        other.push(v);
      }
    }
    return other;
  };
}

Array.prototype.diff = function (a) {
  return this.filter(function (i) {
    return a.indexOf(i) < 0;
  });
};

/*
 * String polyfills
*/
if (!String.prototype.startsWith) {
  String.prototype.startsWith = function (searchString, position) {
    position = position || 0;
    return this.substr(position, searchString.length) === searchString;
  };
}

if (!String.prototype.endsWith) {
  String.prototype.endsWith = function (searchString, position) {
    var subjectString = this.toString();
    if (typeof position !== 'number' || !isFinite(position) || Math.floor(position) !== position || position > subjectString.length) {
      position = subjectString.length;
    }
    position -= searchString.length;
    var lastIndex = subjectString.lastIndexOf(searchString, position);
    return lastIndex !== -1 && lastIndex === position;
  };
}

if (!String.prototype.includes) {
  String.prototype.includes = function (search, start) {
    'use strict';
    if (typeof start !== 'number') {
      start = 0;
    }

    if (start + search.length > this.length) {
      return false;
    } else {
      return this.indexOf(search, start) !== -1;
    }
  };
}

if (!('addRule' in CSSStyleSheet.prototype)) {
  CSSStyleSheet.prototype.addRule = function (selector, rule, idx) {
    return this.insertRule(selector + "{" + rule + "}", idx || 0);
  }
}


/*
 * Add utility methods to the HUE object
*/

window.hueUtils = window.hueUtils || (function () {
  'use strict';

  var hueUtils = {};

  hueUtils.bootstrapRatios = {
    span3: function () {
      var windowWidth = $(window).width();
      if (windowWidth >= 1200) {
        return 23.07692308;
      } else if (windowWidth >= 768 && windowWidth <= 979) {
        return 22.9281768;
      } else {
        return 23.17073171;
      }
    },
    span9: function () {
      var windowWidth = $(window).width();
      if (windowWidth >= 1200) {
        return 74.35897436;
      } else if (windowWidth >= 768 && windowWidth <= 979) {
        return 74.30939227;
      } else {
        return 74.3902439;
      }
    },
    margin: function () {
      return 2.56410256;
    }
  };

  /*
   * Convert text to URLs
   * Selector arg can be jQuery or document.querySelectorAll()
  */
  hueUtils.text2Url = function (selectors) {
    var i = 0,
      len = selectors.length;

    for (i; i < len; i++) {
      var arr = [],
        selector = selectors[i],
        val = selector.innerHTML.replace(/&nbsp;/g, ' ').split(' ');

      val.forEach(function(word) {
        var matched = null,
          re = /(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?/gi;

        if (re.test(word)) {
          matched = word.match(re);
          word = word.replace(matched, '<a href="' + matched + '">' + matched + '</a>')
          arr.push(word);
        } else {
          arr.push(word);
        }
      });

      selector.innerHTML = arr.join(' ');
    }
    return this;
  };

  /*
   * Create a in-memory div, set it's inner text(which jQuery automatically encodes)
   * then grab the encoded contents back out.
  */

  hueUtils.htmlEncode = function (value){
    return $('<div/>').text(value).html();
  };

  hueUtils.html2text = function (value){
    return $('<div/>').html(value).text().replace(/\u00A0/g, ' ');
  };

  hueUtils.goFullScreen = function () {
    if (!document.fullscreenElement && !document.mozFullScreenElement && !document.webkitFullscreenElement && !document.msFullscreenElement) {
      if (document.documentElement.requestFullscreen) {
        document.documentElement.requestFullscreen();
      } else if (document.documentElement.msRequestFullscreen) {
        document.documentElement.msRequestFullscreen();
      } else if (document.documentElement.mozRequestFullScreen) {
        document.documentElement.mozRequestFullScreen();
      } else if (document.documentElement.webkitRequestFullscreen) {
        document.documentElement.webkitRequestFullscreen(Element.ALLOW_KEYBOARD_INPUT);
      }
    }
  };

  hueUtils.exitFullScreen = function () {
    if (document.fullscreenElement ||
        document.mozFullScreenElement || document.webkitFullscreenElement || document.msFullscreenElement) {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      } else if (document.msExitFullscreen) {
        document.msExitFullscreen();
      } else if (document.mozCancelFullScreen) {
        document.mozCancelFullScreen();
      } else if (document.webkitExitFullscreen) {
        document.webkitExitFullscreen();
      }
    }
  };

  hueUtils.changeURL = function (newURL, params) {
    var extraSearch = '';
    if (params) {
      var newSearchKeys = Object.keys(params);
      if (newSearchKeys.length) {
        while (newSearchKeys.length) {
          var newKey = newSearchKeys.pop();
          extraSearch += newKey + '=' + params[newKey];
          if (newSearchKeys.length) {
            extraSearch += '&';
          }
        }
      }
    }

    if (typeof IS_EMBEDDED !== 'undefined' && IS_EMBEDDED) {
      var search = window.location.search;
      if (extraSearch) {
        search += (search ? '&' : '?') + extraSearch
      }
      newURL = window.location.pathname + search + '#!' + newURL.replace('/hue', '');
      window.history.pushState(null, null, newURL);
      return;
    }

    var hashSplit = newURL.split('#');
    var url = hashSplit[0];
    if (extraSearch) {
      url += (url.indexOf('?') === -1 ? '?' : '&') + extraSearch;
    }
    if (hashSplit.length > 1) {
      url += '#' + hashSplit[1];
    } else if (window.location.hash) {
      url += window.location.hash;
    }
    window.history.pushState(null, null, url);
  };

  hueUtils.replaceURL = function (newURL) {
    window.history.replaceState(null, null, newURL);
  };

  hueUtils.changeURLParameter = function (param, value) {
    if (typeof IS_EMBEDDED !== 'undefined' && IS_EMBEDDED) {
      var currentUrl = window.location.hash.replace('#!', '');
      var parts = currentUrl.split('?');
      var path = parts[0];
      var search = parts.length > 1 ? parts[1] : '';
      if (~search.indexOf(param + '=' + value)) {
        return;
      }
      if (~search.indexOf(param + '=')) {
        if (!value) {
          search = search.replace(new RegExp(param + '=[^&]*&?'), '');
        } else {
          search = search.replace(new RegExp(param + '=[^&]*'), param + '=' + value);
        }
      } else if (value) {
        if (search) {
          search += '&';
        }
        search += param + '=' + value;
      } else {
        return;
      }

      hueUtils.changeURL(search ? path + '?' + search : path);
    } else {
      var newSearch = '';
      if (window.location.getParameter(param, true) !== null) {
        newSearch += '?';
        window.location.search.replace(/\?/gi, '').split('&').forEach(function (p) {
          if (p.split('=')[0] !== param) {
            newSearch += p;
          }
        });
        if (value){
          newSearch += (newSearch !== '?' ? '&' : '') + param + '=' + value;
        }
      } else {
        newSearch = window.location.search + (value ? (window.location.search.indexOf('?') > -1 ? '&' : '?') + param + '=' + value : '' );
      }

      if (newSearch === '?') {
        newSearch = '';
      }

      hueUtils.changeURL(window.location.pathname + newSearch);
    }
  };

  hueUtils.removeURLParameter = function (param) {
    hueUtils.changeURLParameter(param, null);
  };

  /**
   * @param {string} pseudoJson
   * @constructor
   */
  hueUtils.parseHivePseudoJson = function (pseudoJson) {
    // Hive returns a pseudo-json with parameters, like
    // "{Lead Developer=John Foo, Lead Developer Email=jfoo@somewhere.com, date=2013-07-11 }"
    var parsedParams = {};
    if (pseudoJson && pseudoJson.length > 2){
      var splits = pseudoJson.substring(1, pseudoJson.length-1).split(', ');
      splits.forEach(function(part){
        if (part.indexOf('=') > -1){
          parsedParams[part.split('=')[0]] = part.split('=')[1];
        }
      });
    }
    return parsedParams;
  };

  hueUtils.isOverflowing = function (element) {
    if (element instanceof jQuery) {
      element = element[0];
    }
    return element.scrollHeight > element.clientHeight || element.scrollWidth > element.clientWidth;
  };

  /**
   * @param {string} selector
   * @param {Function} condition
   * @param {Function} callback
   * @param {number} [timeout]
   * @constructor
   */
  hueUtils.waitForRendered = function (selector, condition, callback, timeout) {
    var $el = selector instanceof jQuery ? selector: $(selector);
    if (condition($el)) {
      callback($el);
    } else {
      window.clearTimeout($el.data('waitForRenderTimeout'));
      var waitForRenderTimeout = window.setTimeout(function () {
        hueUtils.waitForRendered(selector, condition, callback);
      }, timeout || 100);
      $el.data('waitForRenderTimeout', waitForRenderTimeout);
    }
  };

  /**
   * @param {Function} observable
   * @param {Function} callback
   * @param {number} [timeout]
   * @constructor
   */
  hueUtils.waitForObservable = function (observable, callback, timeout) {
    if (observable()) {
      callback(observable);
    }
    else {
      var subscription = observable.subscribe(function(newValue) {
        if (newValue) {
          subscription.dispose();
          callback(observable);
        }
      });
    }
  };

  /**
   * @param {Function} variable
   * @param {Function} callback
   * @param {number} [timeout]
   * @constructor
   */
  hueUtils.waitForVariable = function (variable, callback, timeout) {
    if (variable) {
      callback(variable);
    }
    else {
      window.setTimeout(function () {
        hueUtils.waitForVariable(variable, callback);
      }, timeout || 100)
    }
  };

  hueUtils.scrollbarWidth = function () {
    var $parent, $children, width;
    $parent = $('<div style="width:50px;height:50px;overflow:auto"><div/></div>').appendTo(HUE_CONTAINER);
    $children = $parent.children();
    width = $children.innerWidth() - $children.height(99).innerWidth();
    $parent.remove();
    return width;
  };

  hueUtils.getSearchParameter = function (search, name, returnNull) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(search);
    if (returnNull && results === null){
      return null;
    }
    return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
  };

  hueUtils.logError = function (error) {
    if (typeof window.console !== 'undefined' && typeof window.console.error !== 'undefined') {
      if (typeof error !== 'undefined') {
        console.error(error);
      }
      console.error(new Error().stack);
    }
  };

  hueUtils.equalIgnoreCase = function (a, b) {
    return a && b && a.toLowerCase() === b.toLowerCase();
  };

  hueUtils.deXSS = function (str) {
    if (typeof str !== 'undefined' && str !== null && typeof str === 'string') {
      return str.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
    }
    return str;
  }

  hueUtils.getStyleFromCSSClass = function (cssClass) {
    for (var i = 0; i < document.styleSheets.length; i++) {
      var cssClasses = document.styleSheets[i].rules || document.styleSheets[i].cssRules;
      for (var x = 0; x < cssClasses.length; x++) {
        if (cssClasses[x].selectorText == cssClass) {
          return (cssClasses[x].style) ? cssClasses[x].style : cssClasses[x];
        }
      }
    }
  };

  hueUtils.highlight = function (text, searchTerm) {
    if (searchTerm === '' || text === '') {
      return text;
    }

    var remText = text;
    var highLightedText = '';
    searchTerm = searchTerm.toLowerCase();

    do {
      var remLowerText = remText.toLowerCase();
      var startIndex = remLowerText.indexOf(searchTerm);
      if(startIndex >= 0) {
        highLightedText += remText.substring(0, startIndex) + '<strong>' + remText.substring(startIndex, startIndex + searchTerm.length) + '</strong>';
        remText = remText.substring(startIndex + searchTerm.length);
      } else {
         highLightedText += remText;
      }
    } while (startIndex >= 0);

    return highLightedText;
  };

  hueUtils.dfs = function(node, callback) {
    if (!node || typeof(node) !== 'object') {
      return;
    }
    Object.keys(node).forEach(function(key) {
      callback(node, key);
      hueUtils.dfs(node[key], callback);
    });
  };

  hueUtils.deleteAllEmptyStringKey = function(node) {
    var fDeleteEmptyStringKey = function (node, key) {
      if (node[key] || typeof(node[key]) !== 'string') {
        return;
      }
      delete node[key];
    };
    hueUtils.dfs(node, fDeleteEmptyStringKey);
  };

  return hueUtils;

})();

if (!Object.keys) {

  Object.keys = (function () {
    'use strict';
    var hasOwnProperty = Object.prototype.hasOwnProperty,
        hasDontEnumBug = !({toString: null}).propertyIsEnumerable('toString'),
        dontEnums = [
          'toString',
          'toLocaleString',
          'valueOf',
          'hasOwnProperty',
          'isPrototypeOf',
          'propertyIsEnumerable',
          'constructor'
        ],
        dontEnumsLength = dontEnums.length;

    return function (obj) {
      if (typeof obj !== 'object' && (typeof obj !== 'function' || obj === null)) {
        throw new TypeError('Object.keys called on non-object');
      }

      var result = [], prop, i;

      for (prop in obj) {
        if (hasOwnProperty.call(obj, prop)) {
          result.push(prop);
        }
      }

      if (hasDontEnumBug) {
        for (i = 0; i < dontEnumsLength; i++) {
          if (hasOwnProperty.call(obj, dontEnums[i])) {
            result.push(dontEnums[i]);
          }
        }
      }
      return result;
    };
  }());
}


function s4() {
  return Math.floor((1 + Math.random()) * 0x10000)
      .toString(16)
      .substring(1);
}

function UUID() {
  return s4() + s4() + '-' + s4() + '-' + s4() + '-' + s4() + '-' + s4() + s4() + s4();
}

// Based on original pub/sub implementation from http://davidwalsh.name/pubsub-javascript
var huePubSub = (function () {
  var topics = {};
  var hOP = topics.hasOwnProperty;

  return {
    subscribe: function (topic, listener, app) {
      if (!hOP.call(topics, topic)) {
        topics[topic] = [];
      }

      var index = topics[topic].push({
        listener: listener,
        app: app,
        status: 'running'
      }) - 1;

      return {
        remove: function () {
          delete topics[topic][index];
        }
      };
    },
    removeAll: function (topic) {
      topics[topic] = [];
    },
    subscribeOnce: function (topic, listener, app) {
      var ephemeral = this.subscribe(topic, function () {
        listener.apply(listener, arguments);
        ephemeral.remove();
      }, app);

    },
    publish: function (topic, info) {
      if (!hOP.call(topics, topic)) {
        return;
      }

      topics[topic].forEach(function (item) {
        if (item.status === 'running') {
          item.listener(info);
        }
      });
    },
    getTopics: function () {
      return topics;
    },
    pauseAppSubscribers: function (app) {
      if (app) {
        Object.keys(topics).forEach(function (topicName) {
          topics[topicName].forEach(function (topic) {
            if (typeof topic.app !== 'undefined' && topic.app !== null && (topic.app === app || topic.app.split('-')[0] === app)) {
              topic.status = 'paused';
            }
          });
        });
      }
    },
    resumeAppSubscribers: function (app) {
      if (app) {
        Object.keys(topics).forEach(function (topicName) {
          topics[topicName].forEach(function (topic) {
            if (typeof topic.app !== 'undefined' && topic.app !== null && (topic.app === app || topic.app.split('-')[0] === app)) {
              topic.status = 'running';
            }
          });
        });
      }
    },
    clearAppSubscribers: function (app) {
      if (app) {
        Object.keys(topics).forEach(function (topicName) {
          topics[topicName] = topics[topicName].filter(function(obj){ return obj.app !== app });
        });
      }
    }
  };
})();

var hueDrop = (function () {
  var draggableMeta = {};
  huePubSub.subscribe('draggable.text.meta', function (meta) {
    draggableMeta = meta;
  });

  return {
    fromAssist: function (element, callback) {
      if (typeof element === 'function' && !(element instanceof jQuery)) {
        callback = element;
      }
      if (typeof element === 'string') {
        element = $(element);
      }
      if (element.length > 0) {
        element.droppable({
          accept: '.draggableText',
          drop: function (e, ui) {
            var droppedText = ui.helper.text();
            if (callback) {
              callback({
                text: ui.helper.text(),
                meta: draggableMeta
              });
            }
          }
        });
      }
      else {
        console.warn('hueDrop.fromAssist could not be attached to the element');
      }
    },
    fromDesktop: function (element, callback, method) {
      if (window.FileReader) {
        if (typeof element === 'function' && !(element instanceof jQuery)) {
          callback = element;
        }
        if (typeof element === 'string') {
          element = $(element);
        }

        function handleFileSelect(e) {
          e.stopPropagation();
          e.preventDefault();
          var dt = e.dataTransfer;
          var files = dt.files;
          for (var i = 0, f; f = files[i]; i++) {
            var reader = new FileReader();
            reader.onload = (function (file) {
              return function (e) {
                callback(e.target.result);
              };
            })(f);
            switch (method) {
              case 'arrayBuffer':
                reader.readAsArrayBuffer(f);
                break;
              case 'binaryString':
                reader.readAsBinaryString(f);
                break;
              case 'dataURL':
                reader.readAsDataURL(f);
                break;
              default:
                reader.readAsText(f);
            }
          }
        }

        function handleDragOver(e) {
          e.stopPropagation();
          e.preventDefault();
          e.dataTransfer.dropEffect = 'copy';
        }

        if (element.length > 0) {
          element[0].addEventListener('dragover', handleDragOver, false);
          element[0].addEventListener('drop', handleFileSelect, false);
        }
        else {
          console.warn('hueDrop.fromDesktop could not be attached to the element');
        }

      }
      else {
        console.warn('FileReader is not supported by your browser. Please consider upgrading to fully experience Hue!')
      }
    }
  };
})();

if (!window.hueDebug) {
  window.hueDebug = {};
}

window.hueDebug.clearCaches = function () {
  var promises = [];
  var clearInstance = function(prefix) {
    promises.push(localforage.createInstance({ name: prefix + LOGGED_USERNAME }).clear());
  };
  clearInstance('HueContextCatalog_');
  clearInstance('HueDataCatalog_');
  clearInstance('HueDataCatalog_hive_');
  clearInstance('HueDataCatalog_hive_multiTable_');
  clearInstance('HueDataCatalog_impala_');
  clearInstance('HueDataCatalog_impala_multiTable_');
  Promise.all(promises).then(function () {
    console.log('Done! Refresh the browser.');
  })
};

var hueDebugTimer = (function () {
  var initialTime = null;
  var times = [];
  var withConsole = false;
  return {
    start: function (enableConsole) {
      times = [];
      initialTime = (new Date()).getTime();
      times.push(initialTime);
      if (enableConsole){
        withConsole = true;
        console.log('Start', initialTime);
      }
    },
    mark: function (label) {
      var mark = (new Date()).getTime();
      times.push(mark);
      if (withConsole){
        console.log(label ? label : times.length, mark - times[times.length - 2], mark - initialTime);
      }
      return mark - times[times.length - 2];
    },
    total: function () {
      return times[times.length - 1] - times[0];
    },
    timeline: function () {
      return times;
    }
  };
})();

var hueAnalytics = (function () {
  return {
    log: function (app, page) {
      if (typeof trackOnGA == 'function') {
        trackOnGA(app + '/' + page);
      }
    },
    convert: function (app, page) {
      $.post("/desktop/log_analytics", {
        page: app + '/' + page,
      });
    }
  };
})();

Number.prototype.toHHMMSS = function (skipZeroSeconds) {
  var n = this;
  var millis = n % 1000;
  n = (n - millis) / 1000;
  millis = +(millis/10).toFixed();
  var seconds = n % 60;
  n = (n - seconds) / 60;
  var minutes = n % 60;
  n = (n - minutes) / 60;
  var hours = n % 24;
  var days = (n - hours) / 24;
  var val = $.trim((days > 0 ? days + "d, " : "") + (hours > 0 ? hours + "h, " : "") + (minutes > 0 ? minutes + "m, " : "") + ((skipZeroSeconds && seconds === 0) ? '' : (seconds + (millis > 0 && minutes == 0 && hours == 0 && days == 0 ? "." + millis : "") + "s")));
  if (val[val.length - 1] === ',') {
    val = val.substr(0, val.length - 1);
  }
  return val;
};

String.prototype.hashCode = function() {
  var hash = 0, i, chr, len;
  if (this.length === 0) return hash;
  for (i = 0, len = this.length; i < len; i++) {
    chr   = this.charCodeAt(i);
    hash  = ((hash << 5) - hash) + chr;
    hash |= 0; // Convert to 32bit integer
  }
  return hash;
};

String.prototype.regexLastIndexOf = function (regex, startpos) {
  regex = (regex.global) ? regex : new RegExp(regex.source, "g" + (regex.ignoreCase ? "i" : "") + (regex.multiLine ? "m" : ""));
  if (typeof (startpos) == "undefined") {
    startpos = this.length;
  } else if (startpos < 0) {
    startpos = 0;
  }
  var stringToWorkWith = this.substring(0, startpos + 1);
  var lastIndexOf = -1;
  var nextStop = 0;
  while ((result = regex.exec(stringToWorkWith)) != null) {
    lastIndexOf = result.index;
    regex.lastIndex = ++nextStop;
  }
  return lastIndexOf;
};

if (!('getParameter' in window.location)) {
  window.location.getParameter = function (name, returnNull) {
    return hueUtils.getSearchParameter(window.location.search, name, returnNull);
  };
}

var escapeOutput = function (str) {
  return $('<span>').text(str).html().trim();
};

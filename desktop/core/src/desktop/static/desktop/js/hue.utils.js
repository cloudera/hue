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

// Array polyfills for older browsers
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
// adding missing .filter for IE8

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
 * Add utility methods to the HUE object
*/

(function (hueUtils) {
  'use strict';

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
    return $('<div/>').html(value).text();
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
  }

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
  }

  hueUtils.changeURL = function (newURL) {
    window.history.pushState(null, null, newURL);
  }

  hueUtils.replaceURL = function (newURL) {
    window.history.replaceState(null, null, newURL);
  }

  /**
   * @param {string} pseudoJson
   * @constructor
   */
  hueUtils.parseHivePseudoJson = function (pseudoJson) {
    // Hive returns a pseudo-json with parameters, like
    // "{Lead Developer=John Foo, Lead Developer Email=jfoo@somewhere.com, date=2013-07-11 }"
    var parsedParams = {};
    if (pseudoJson && pseudoJson.length > 2){
      var splits = pseudoJson.substring(1, pseudoJson.length-2).split(', ');
      splits.forEach(function(part){
        if (part.indexOf('=') > -1){
          parsedParams[part.split('=')[0]] = part.split('=')[1];
        }
      });
    }
    return parsedParams;
  }

  hueUtils.isOverflowing = function (element) {
    if (element instanceof jQuery) {
      element = element[0];
    }
    return element.scrollHeight > element.clientHeight || element.scrollWidth > element.clientWidth;
  }

  /**
   * @param {string} selector
   * @param {Function} condition
   * @param {Function} callback
   * @param {number} [timeout]
   * @constructor
   */
  hueUtils.waitForRendered = function (selector, condition, callback, timeout) {
    var $el = $(selector);
    if (condition($el)) {
      callback($el);
    }
    else {
      window.setTimeout(function () {
        hueUtils.waitForRendered(selector, condition, callback);
      }, timeout || 100)
    }
  }

  /**
   * @constructor
   */
  hueUtils.scrollbarWidth = function () {
    var $parent, $children, width;
    $parent = $('<div style="width:50px;height:50px;overflow:auto"><div/></div>').appendTo('body');
    $children = $parent.children();
    width = $children.innerWidth() - $children.height(99).innerWidth();
    $parent.remove();
    return width;
  }


}(hueUtils = window.hueUtils || {}));

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
    subscribe: function (topic, listener) {
      if (!hOP.call(topics, topic)) {
        topics[topic] = [];
      }

      var index = topics[topic].push(listener) - 1;

      return {
        remove: function () {
          delete topics[topic][index];
        }
      };
    },
    subscribeOnce: function (topic, listener) {
      var ephemeral = this.subscribe(topic, function () {
        listener.apply(arguments);
        ephemeral.remove();
      });

    },
    publish: function (topic, info) {
      if (!hOP.call(topics, topic)) {
        return;
      }

      topics[topic].forEach(function (item) {
        item(info);
      });
    },
    getTopics: function () {
      return topics;
    }
  };
})();


Number.prototype.toHHMMSS = function () {
  var _s = this;
  var _ms = _s % 1000;
  _s = (_s - _ms) / 1000;
  var _secs = _s % 60;
  _s = (_s - _secs) / 60;
  var _mins = _s % 60;
  var _hrs = (_s - _mins) / 60;
  return (_hrs > 0 ? _hrs + "h, " : "") + (_mins > 0 ? _mins + "m, " : "") + _secs + "." + _ms + "s";

}

if (!('getParameter' in window.location)) {
  window.location.getParameter = function (name) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(window.location.search);
    return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
  };
}

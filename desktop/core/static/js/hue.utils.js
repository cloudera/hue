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
    for (var i = 0, n = this.length; i < n; i++)
      if (i in this && filter.call(that, v = this[i], i, this))
        other.push(v);
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
(function (hue) {
  'use strict';

  /*
   * Convert text to URLs
   * Selector arg can be jQuery or document.querySelectorAll()
  */
  hue.text2Url = function (selectors) {
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
}(hue = window.hue || {}));


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

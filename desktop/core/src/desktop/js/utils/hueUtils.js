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

const bootstrapRatios = {
  span3() {
    const windowWidth = $(window).width();
    if (windowWidth >= 1200) {
      return 23.07692308;
    } else if (windowWidth >= 768 && windowWidth <= 979) {
      return 22.9281768;
    } else {
      return 23.17073171;
    }
  },
  span9() {
    const windowWidth = $(window).width();
    if (windowWidth >= 1200) {
      return 74.35897436;
    } else if (windowWidth >= 768 && windowWidth <= 979) {
      return 74.30939227;
    } else {
      return 74.3902439;
    }
  },
  margin() {
    return 2.56410256;
  }
};

/**
 * Convert text to URLs
 * Selector arg can be jQuery or document.querySelectorAll()
 *
 * @param selectors
 * @return {default}
 */
const text2Url = selectors => {
  let i = 0;
  const len = selectors.length;

  for (i; i < len; i++) {
    const arr = [],
      selector = selectors[i],
      val = selector.innerHTML.replace(/&nbsp;/g, ' ').split(' ');

    val.forEach(word => {
      let matched = null;
      const re = /(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?/gi;

      if (re.test(word)) {
        matched = word.match(re);
        word = word.replace(matched, '<a href="' + matched + '">' + matched + '</a>');
        arr.push(word);
      } else {
        arr.push(word);
      }
    });

    selector.innerHTML = arr.join(' ');
  }
  return this;
};

/**
 * Create a in-memory div, set it's inner text(which jQuery automatically encodes)
 * then grab the encoded contents back out.
 *
 * @param value
 * @return {*|jQuery}
 */
const htmlEncode = value => {
  return $('<div/>')
    .text(value)
    .html();
};

const html2text = value => {
  return $('<div/>')
    .html(value)
    .text()
    .replace(/\u00A0/g, ' ');
};

const goFullScreen = () => {
  if (
    !document.fullscreenElement &&
    !document.mozFullScreenElement &&
    !document.webkitFullscreenElement &&
    !document.msFullscreenElement
  ) {
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

const exitFullScreen = () => {
  if (
    document.fullscreenElement ||
    document.mozFullScreenElement ||
    document.webkitFullscreenElement ||
    document.msFullscreenElement
  ) {
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

const changeURL = (newURL, params) => {
  let extraSearch = '';
  if (params) {
    const newSearchKeys = Object.keys(params);
    if (newSearchKeys.length) {
      while (newSearchKeys.length) {
        const newKey = newSearchKeys.pop();
        extraSearch += newKey + '=' + params[newKey];
        if (newSearchKeys.length) {
          extraSearch += '&';
        }
      }
    }
  }

  if (typeof IS_EMBEDDED !== 'undefined' && IS_EMBEDDED) {
    let search = window.location.search;
    if (extraSearch) {
      search += (search ? '&' : '?') + extraSearch;
    }
    newURL = window.location.pathname + search + '#!' + newURL.replace('/hue', '');
    window.history.pushState(null, null, newURL);
    return;
  }

  const hashSplit = newURL.split('#');
  let url = hashSplit[0];
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

const replaceURL = newURL => {
  window.history.replaceState(null, null, newURL);
};

const changeURLParameter = (param, value) => {
  if (typeof IS_EMBEDDED !== 'undefined' && IS_EMBEDDED) {
    const currentUrl = window.location.hash.replace('#!', '');
    const parts = currentUrl.split('?');
    const path = parts[0];
    let search = parts.length > 1 ? parts[1] : '';
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

    changeURL(search ? path + '?' + search : path);
  } else {
    let newSearch = '';
    if (window.location.getParameter(param, true) !== null) {
      newSearch += '?';
      window.location.search
        .replace(/\?/gi, '')
        .split('&')
        .forEach(p => {
          if (p.split('=')[0] !== param) {
            newSearch += p;
          }
        });
      if (value) {
        newSearch += (newSearch !== '?' ? '&' : '') + param + '=' + value;
      }
    } else {
      newSearch =
        window.location.search +
        (value ? (window.location.search.indexOf('?') > -1 ? '&' : '?') + param + '=' + value : '');
    }

    if (newSearch === '?') {
      newSearch = '';
    }

    changeURL(window.location.pathname + newSearch);
  }
};

const removeURLParameter = param => {
  changeURLParameter(param, null);
};

const parseHivePseudoJson = pseudoJson => {
  // Hive returns a pseudo-json with parameters, like
  // "{Lead Developer=John Foo, Lead Developer Email=jfoo@somewhere.com, date=2013-07-11 }"
  const parsedParams = {};
  if (pseudoJson && pseudoJson.length > 2) {
    const splits = pseudoJson.substring(1, pseudoJson.length - 1).split(', ');
    splits.forEach(part => {
      if (part.indexOf('=') > -1) {
        parsedParams[part.split('=')[0]] = part.split('=')[1];
      }
    });
  }
  return parsedParams;
};

const isOverflowing = element => {
  if (element instanceof jQuery) {
    element = element[0];
  }
  return element.scrollHeight > element.clientHeight || element.scrollWidth > element.clientWidth;
};

const waitForRendered = (selector, condition, callback, timeout) => {
  const $el = selector instanceof jQuery ? selector : $(selector);
  if (condition($el)) {
    callback($el);
  } else {
    window.clearTimeout($el.data('waitForRenderTimeout'));
    const waitForRenderTimeout = window.setTimeout(() => {
      waitForRendered(selector, condition, callback);
    }, timeout || 100);
    $el.data('waitForRenderTimeout', waitForRenderTimeout);
  }
};

const waitForObservable = (observable, callback) => {
  if (observable()) {
    callback(observable);
  } else {
    const subscription = observable.subscribe(newValue => {
      if (newValue) {
        subscription.dispose();
        callback(observable);
      }
    });
  }
};

const waitForVariable = (variable, callback, timeout) => {
  if (variable) {
    callback(variable);
  } else {
    window.setTimeout(() => {
      waitForVariable(variable, callback);
    }, timeout || 100);
  }
};

const scrollbarWidth = () => {
  const $parent = $('<div style="width:50px;height:50px;overflow:auto"><div/></div>').appendTo(
    HUE_CONTAINER
  );
  const $children = $parent.children();
  const width = $children.innerWidth() - $children.height(99).innerWidth();
  $parent.remove();
  return width;
};

const getSearchParameter = (search, name, returnNull) => {
  name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
  const regex = new RegExp('[\\?&]' + name + '=([^&#]*)'),
    results = regex.exec(search);
  if (returnNull && results === null) {
    return null;
  }
  return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
};

const logError = error => {
  if (typeof window.console !== 'undefined' && typeof window.console.error !== 'undefined') {
    if (typeof error !== 'undefined') {
      console.error(error);
    }
    console.error(new Error().stack);
  }
};

const equalIgnoreCase = (a, b) => a && b && a.toLowerCase() === b.toLowerCase();

const deXSS = str => {
  if (typeof str !== 'undefined' && str !== null && typeof str === 'string') {
    return str.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
  }
  return str;
};

const getStyleFromCSSClass = cssClass => {
  for (let i = 0; i < document.styleSheets.length; i++) {
    const cssClasses = document.styleSheets[i].rules || document.styleSheets[i].cssRules;
    for (let x = 0; x < cssClasses.length; x++) {
      if (cssClasses[x].selectorText == cssClass) {
        return cssClasses[x].style ? cssClasses[x].style : cssClasses[x];
      }
    }
  }
};

const highlight = (text, searchTerm) => {
  if (searchTerm === '' || text === '') {
    return text;
  }

  let remText = text;
  let highLightedText = '';
  searchTerm = searchTerm.toLowerCase();

  let startIndex;
  do {
    const remLowerText = remText.toLowerCase();
    startIndex = remLowerText.indexOf(searchTerm);
    if (startIndex >= 0) {
      highLightedText +=
        remText.substring(0, startIndex) +
        '<strong>' +
        remText.substring(startIndex, startIndex + searchTerm.length) +
        '</strong>';
      remText = remText.substring(startIndex + searchTerm.length);
    } else {
      highLightedText += remText;
    }
  } while (startIndex >= 0);

  return highLightedText;
};

const dfs = (node, callback) => {
  if (!node || typeof node !== 'object') {
    return;
  }
  Object.keys(node).forEach(key => {
    callback(node, key);
    dfs(node[key], callback);
  });
};

const deleteAllEmptyStringKey = node => {
  const fDeleteEmptyStringKey = function(node, key) {
    if (node[key] || typeof node[key] !== 'string') {
      return;
    }
    delete node[key];
  };
  dfs(node, fDeleteEmptyStringKey);
};

const s4 = () =>
  Math.floor((1 + Math.random()) * 0x10000)
    .toString(16)
    .substring(1);

const UUID = () => s4() + s4() + '-' + s4() + '-' + s4() + '-' + s4() + '-' + s4() + s4() + s4();

const escapeOutput = str =>
  $('<span>')
    .text(str)
    .html()
    .trim();

export default {
  bootstrapRatios: bootstrapRatios,
  text2Url: text2Url,
  htmlEncode: htmlEncode,
  html2text: html2text,
  goFullScreen: goFullScreen,
  exitFullScreen: exitFullScreen,
  changeURL: changeURL,
  replaceURL: replaceURL,
  changeURLParameter: changeURLParameter,
  removeURLParameter: removeURLParameter,
  parseHivePseudoJson: parseHivePseudoJson,
  isOverflowing: isOverflowing,
  waitForRendered: waitForRendered,
  waitForObservable: waitForObservable,
  waitForVariable: waitForVariable,
  scrollbarWidth: scrollbarWidth,
  getSearchParameter: getSearchParameter,
  logError: logError,
  equalIgnoreCase: equalIgnoreCase,
  deXSS: deXSS,
  getStyleFromCSSClass: getStyleFromCSSClass,
  highlight: highlight,
  dfs: dfs,
  deleteAllEmptyStringKey: deleteAllEmptyStringKey,
  UUID: UUID,
  escapeOutput: escapeOutput
};

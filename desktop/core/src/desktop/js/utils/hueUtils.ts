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
import sanitizeHtml from 'sanitize-html';
import { hueWindow } from 'types/types';
import huePubSub from 'utils/huePubSub';
import { hueLocalStorage, withLocalStorage } from './storageUtils';

export const bootstrapRatios = {
  span3(): number {
    if (window.innerWidth >= 1200) {
      return 23.07692308;
    } else if (window.innerWidth >= 768 && window.innerWidth <= 979) {
      return 22.9281768;
    } else {
      return 23.17073171;
    }
  },
  span9(): number {
    if (window.innerWidth >= 1200) {
      return 74.35897436;
    } else if (window.innerWidth >= 768 && window.innerWidth <= 979) {
      return 74.30939227;
    } else {
      return 74.3902439;
    }
  },
  margin(): number {
    return 2.56410256;
  }
};

/**
 * Create a in-memory div, set it's inner text(which jQuery automatically encodes)
 * then grab the encoded contents back out.
 */
export const htmlEncode = (value: string): string => {
  const element = document.createElement('div');
  element.innerText = value;
  return element.innerHTML;
};

export const html2text = (value: string): string => {
  const element = document.createElement('div');
  element.innerHTML = value;
  return element.innerText.replace(/\u00A0/g, ' ');
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type PlainObject = { [name: string]: any };

export const isFullScreen = (): boolean => {
  return (
    document.fullscreenElement ||
    (<PlainObject>document).mozFullScreenElement ||
    (<PlainObject>document).webkitFullscreenElement ||
    (<PlainObject>document).msFullscreenElement
  );
};

export const goFullScreen = async (element: Element): Promise<void> => {
  if (isFullScreen()) {
    return;
  }
  if (!element) {
    element = document.documentElement;
  }

  if (element.requestFullscreen) {
    return element.requestFullscreen();
  }
  const mixedBrowserElement = element as PlainObject;
  if (mixedBrowserElement.msRequestFullscreen) {
    return mixedBrowserElement.msRequestFullscreen();
  }
  if (mixedBrowserElement.mozRequestFullScreen) {
    return mixedBrowserElement.mozRequestFullScreen();
  }
  if (mixedBrowserElement.webkitRequestFullscreen) {
    return mixedBrowserElement.webkitRequestFullscreen(mixedBrowserElement.ALLOW_KEYBOARD_INPUT);
  }
};

export const exitFullScreen = async (): Promise<void> => {
  if (!isFullScreen()) {
    return;
  }
  if (document.exitFullscreen) {
    return document.exitFullscreen();
  }
  const mixedBrowserElement = document as PlainObject;
  if (mixedBrowserElement.msExitFullscreen) {
    return mixedBrowserElement.msExitFullscreen();
  }
  if (mixedBrowserElement.mozCancelFullScreen) {
    return mixedBrowserElement.mozCancelFullScreen();
  }
  if (mixedBrowserElement.webkitExitFullscreen) {
    return mixedBrowserElement.webkitExitFullscreen();
  }
};

export const toggleFullScreen = async (element: Element): Promise<void> => {
  if (isFullScreen()) {
    return exitFullScreen();
  }
  return goFullScreen(element);
};

export const changeURL = (newURL: string, params?: PlainObject): void => {
  let extraSearch = '';
  if (params) {
    const newSearchKeys = Object.keys(params);
    if (newSearchKeys.length) {
      while (newSearchKeys.length) {
        const newKey = newSearchKeys.pop() || '';
        extraSearch += newKey + '=' + params[newKey];
        if (newSearchKeys.length) {
          extraSearch += '&';
        }
      }
    }
  }

  const hashSplit = newURL.split('#');
  const hueBaseUrl = (<hueWindow>window).HUE_BASE_URL;
  const base =
    hueBaseUrl && hashSplit[0].length && hashSplit[0].indexOf(hueBaseUrl) !== 0 ? hueBaseUrl : '';
  let url = base + hashSplit[0];
  if (extraSearch) {
    url += (url.indexOf('?') === -1 ? '?' : '&') + extraSearch;
  }
  if (hashSplit.length > 1) {
    //the foldername may contain # , so create substring ignoring first #
    url += '#' + newURL.substring(newURL.indexOf('#') + 1);
  } else if (window.location.hash) {
    url += window.location.hash;
  }
  window.history.pushState(null, '', url);
};

export const replaceURL = (newURL: string): void => {
  window.history.replaceState(null, '', newURL);
};

export const changeURLParameter = (param: string, value: string | null): void => {
  let newSearch = '';
  if (getParameter(param, true) !== null) {
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
};

export const removeURLParameter = (param: string): void => {
  changeURLParameter(param, null);
};

export const parseHivePseudoJson = (pseudoJson: string): { [key: string]: string } => {
  // Hive returns a pseudo-json with parameters, like
  // "{Lead Developer=John Foo, Lead Developer Email=jfoo@somewhere.com, date=2013-07-11 }"
  const parsedParams: { [key: string]: string } = {};
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

export const isOverflowing = (element: HTMLElement | JQuery): boolean => {
  const htmlElement = (<JQuery>element).jquery ? (<JQuery>element).get(0) : <HTMLElement>element;
  return (
    htmlElement.scrollHeight > htmlElement.clientHeight ||
    htmlElement.scrollWidth > htmlElement.clientWidth
  );
};

export const waitForRendered = (
  selector: string | JQuery,
  condition: (element: JQuery) => boolean,
  callback: (element: JQuery) => void,
  timeout?: number
): void => {
  const $el = (<JQuery>selector).jquery ? <JQuery>selector : $(<string>selector);
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

export const waitForObservable = (
  observable: KnockoutObservable<unknown>,
  callback: (observable: KnockoutObservable<unknown>) => void
): void => {
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

export const waitForVariable = (
  variable: unknown,
  callback: (variable: unknown) => void,
  timeout?: number
): void => {
  if (variable) {
    callback(variable);
  } else {
    window.setTimeout(() => {
      waitForVariable(variable, callback);
    }, timeout || 100);
  }
};

export const scrollbarWidth = (): number => {
  const parent = document.createElement('div');
  parent.style.width = '50px';
  parent.style.height = '50px';
  parent.style.overflow = 'auto';
  const child = document.createElement('div');
  child.style.height = '100px';
  parent.append(child);
  document.body.append(child);
  const width = child.offsetWidth - child.clientWidth;
  parent.remove();
  return width;
};

export const getParameter = (name: string, nullAllowed?: boolean): string | null => {
  return getSearchParameter(window.location.search, name, nullAllowed);
};

export const getSearchParameter = (
  search: string,
  name: string,
  nullAllowed?: boolean
): string | null => {
  name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
  const regex = new RegExp('[\\?&]' + name + '=([^&#]*)'),
    results = regex.exec(search);
  if (nullAllowed && results === null) {
    return null;
  }
  return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
};

export const logError = (error: unknown): void => {
  if (typeof window.console !== 'undefined' && typeof window.console.error !== 'undefined') {
    if (typeof error !== 'undefined') {
      console.error(error);
    }
    console.error(new Error().stack);
  }
};

export const equalIgnoreCase = (a?: string, b?: string): boolean =>
  !!a && !!b && a.toLowerCase() === b.toLowerCase();

export const deXSS = (str?: string | number | null): string =>
  (typeof str !== 'undefined' && sanitizeHtml(str as string)) || '';

export const getStyleFromCSSClass = (
  cssClass: string
): CSSStyleDeclaration | CSSRule | undefined => {
  for (let i = 0; i < document.styleSheets.length; i++) {
    const cssClasses = document.styleSheets[i].rules || document.styleSheets[i].cssRules;
    for (let x = 0; x < cssClasses.length; x++) {
      if ((<CSSStyleRule>cssClasses[x]).selectorText === cssClass) {
        return (<CSSStyleRule>cssClasses[x]).style
          ? (<CSSStyleRule>cssClasses[x]).style
          : <CSSStyleRule>cssClasses[x];
      }
    }
  }
};

export const highlight = (text: string, searchTerm: string): string => {
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
      highLightedText += `${remText.substring(0, startIndex)}<strong>${remText.substring(
        startIndex,
        startIndex + searchTerm.length
      )}</strong>`;
      remText = remText.substring(startIndex + searchTerm.length);
    } else {
      highLightedText += remText;
    }
  } while (startIndex >= 0);

  return highLightedText;
};

type Node = { [key: string]: Node };

export const dfs = (node: Node, callback: (node: Node, key: string) => void): void => {
  if (!node || typeof node !== 'object') {
    return;
  }
  Object.keys(node).forEach(key => {
    callback(node, key);
    dfs(node[key], callback);
  });
};

export const deleteAllEmptyStringKeys = (node: Node): void => {
  dfs(node, (node: Node, key: string) => {
    if (node[key] || typeof node[key] !== 'string') {
      return;
    }
    delete node[key];
  });
};

const s4 = (): string =>
  Math.floor((1 + Math.random()) * 0x10000)
    .toString(16)
    .substring(1);

export const UUID = (): string =>
  s4() + s4() + '-' + s4() + '-' + s4() + '-' + s4() + '-' + s4() + s4() + s4();

export const escapeOutput = (str: string): string => htmlEncode(str).trim();

type ComplexValueAccessor = () => {
  value?: KnockoutObservable<string>;
  displayJustLastBit?: boolean;
};

export const getFileBrowseButton = (
  inputElement: JQuery<HTMLInputElement>,
  selectFolder: string,
  valueAccessor: KnockoutObservable<string> | ComplexValueAccessor,
  stripHdfsPrefix: boolean,
  allBindingsAccessor: KnockoutAllBindingsAccessor,
  isAddon: boolean,
  isNestedModal: boolean,
  linkMarkup: boolean
): JQuery => {
  let button: JQuery;
  if (isAddon) {
    button = $('<span>').addClass('add-on muted pointer filechooser-clickable').text('..');
  } else if (linkMarkup) {
    button = $('<a>').addClass('btn').addClass('fileChooserBtn filechooser-clickable').text('..');
  } else {
    button = $('<button>')
      .addClass('btn')
      .addClass('fileChooserBtn filechooser-clickable')
      .text('..');
  }
  button.on('click', e => {
    e.preventDefault();
    if (!isNestedModal) {
      $('body').addClass('modal-open');
    }

    function callFileChooser() {
      let initialPath: string =
        (<string>inputElement.val()).trim() !== '' ? <string>inputElement.val() || '' : '/';
      if (
        (allBindingsAccessor &&
          allBindingsAccessor().filechooserOptions &&
          allBindingsAccessor().filechooserOptions.skipInitialPathIfEmpty &&
          inputElement.val() === '') ||
        (allBindingsAccessor && allBindingsAccessor().filechooserPrefixSeparator)
      ) {
        initialPath = '';
      }
      if (inputElement.data('fullPath')) {
        initialPath = inputElement.data('fullPath');
      }
      if (initialPath.indexOf('hdfs://') > -1) {
        initialPath = initialPath.substring(7);
      }

      let supportSelectFolder = !!selectFolder;
      if (
        allBindingsAccessor &&
        typeof allBindingsAccessor().filechooserOptions !== 'undefined' &&
        typeof allBindingsAccessor().filechooserOptions.selectFolder !== 'undefined'
      ) {
        supportSelectFolder = allBindingsAccessor().filechooserOptions.selectFolder;
      }

      $('#filechooser').jHueFileChooser({
        suppressErrors: true,
        selectFolder: supportSelectFolder,
        onFolderChoose: filePath => {
          handleChoice(filePath, stripHdfsPrefix);
          if (selectFolder) {
            $('#chooseFile').modal('hide');
            if (!isNestedModal) {
              $('.modal-backdrop').remove();
            }
          }
        },
        onFileChoose: filePath => {
          handleChoice(filePath, stripHdfsPrefix);
          $('#chooseFile').modal('hide');
          if (!isNestedModal) {
            $('.modal-backdrop').remove();
          }
        },
        createFolder:
          allBindingsAccessor &&
          allBindingsAccessor().filechooserOptions &&
          allBindingsAccessor().filechooserOptions.createFolder,
        uploadFile:
          allBindingsAccessor &&
          allBindingsAccessor().filechooserOptions &&
          allBindingsAccessor().filechooserOptions.uploadFile,
        initialPath: initialPath,
        errorRedirectPath: '',
        forceRefresh: true,
        showExtraHome:
          allBindingsAccessor &&
          allBindingsAccessor().filechooserOptions &&
          allBindingsAccessor().filechooserOptions.showExtraHome,
        extraHomeProperties:
          allBindingsAccessor &&
          allBindingsAccessor().filechooserOptions &&
          allBindingsAccessor().filechooserOptions.extraHomeProperties
            ? allBindingsAccessor().filechooserOptions.extraHomeProperties
            : {},
        filterExtensions:
          allBindingsAccessor && allBindingsAccessor().filechooserFilter
            ? allBindingsAccessor().filechooserFilter
            : '',
        displayOnlyFolders:
          allBindingsAccessor &&
          allBindingsAccessor().filechooserOptions &&
          allBindingsAccessor().filechooserOptions.displayOnlyFolders
      });
      $('#chooseFile').modal('show');
      if (!isNestedModal) {
        $('#chooseFile').on('hidden', () => {
          $('body').removeClass('modal-open');
          $('.modal-backdrop').remove();
        });
      }
    }

    // check if it's a relative path
    callFileChooser();

    const handleChoice = (filePath: string, stripHdfsPrefix: boolean) => {
      if (allBindingsAccessor && allBindingsAccessor().filechooserPrefixSeparator) {
        filePath =
          (<string>inputElement.val()).split(allBindingsAccessor().filechooserPrefixSeparator)[0] +
          '=' +
          filePath;
      }
      if (
        allBindingsAccessor &&
        allBindingsAccessor().filechooserOptions &&
        allBindingsAccessor().filechooserOptions.deploymentDir
      ) {
        inputElement.data('fullPath', filePath);
        inputElement.attr('data-original-title', filePath);
        if (filePath.indexOf(allBindingsAccessor().filechooserOptions.deploymentDir) === 0) {
          filePath = filePath.substr(
            allBindingsAccessor().filechooserOptions.deploymentDir.length + 1
          );
        }
      }
      if (stripHdfsPrefix) {
        inputElement.val(filePath);
      } else {
        inputElement.val('hdfs://' + filePath);
      }
      inputElement.trigger('change');
      if (valueAccessor) {
        if (
          typeof valueAccessor() === 'function' ||
          typeof (<ComplexValueAccessor>valueAccessor)().value === 'function'
        ) {
          const complex = (<ComplexValueAccessor>valueAccessor)();
          if (complex.value) {
            complex.value(<string>inputElement.val());
            if (complex.displayJustLastBit) {
              inputElement.data('fullPath', <string>inputElement.val());
              inputElement.attr('data-original-title', <string>inputElement.val());
              const value = <string>inputElement.val();
              inputElement.val(value.split('/')[value.split('/').length - 1]);
            }
            return;
          }
        }
        (<KnockoutObservable<string>>valueAccessor())(<string>inputElement.val());
      }
    };
  });
  if (allBindingsAccessor && allBindingsAccessor().filechooserDisabled) {
    button.addClass('disabled').attr('disabled', 'disabled');
  }
  return button;
};

const stripHtml = (html: string): string => {
  const tmp = document.createElement('DIV');
  tmp.innerHTML = html;
  return tmp.textContent || tmp.innerText;
};

export const stripHtmlFromFunctions = (template: string): string => {
  // strips HTML from inside the functions
  let stripped = template;
  const mustacheFunctions = stripped.match(/{{#(.[\s\S]*?){{\//g);
  if (mustacheFunctions) {
    mustacheFunctions.forEach(fn => {
      stripped = stripped.replace(
        fn,
        fn.substr(0, fn.indexOf('}}') + 2) +
          stripHtml(fn.substr(fn.indexOf('}}') + 2).slice(0, -3)).trim() +
          '{{/'
      );
    });
  }
  return stripped;
};

export const onHueLinkClick = (event: Event, url: string, target?: string): void => {
  if (url.indexOf('http') === 0) {
    window.open(url, target);
  } else {
    const prefix = (<hueWindow>window).HUE_BASE_URL + '/hue' + (url.indexOf('/') === 0 ? '' : '/');
    if (target) {
      window.open(prefix + url, target);
    } else if (
      (<KeyboardEvent>event).ctrlKey ||
      (<KeyboardEvent>event).metaKey ||
      (<KeyboardEvent>event).which === 2
    ) {
      window.open(prefix + url, '_blank');
    } else {
      huePubSub.publish('open.link', url);
    }
  }
};

export const sleep = async (timeout: number): Promise<void> =>
  new Promise(resolve => setTimeout(resolve, timeout));

export const defer = (callback: () => void): void => {
  sleep(0).finally(callback);
};

export const noop = (): void => {
  // noop
};

export default {
  bootstrapRatios,
  changeURL,
  changeURLParameter,
  deleteAllEmptyStringKeys,
  deXSS,
  dfs,
  equalIgnoreCase,
  escapeOutput,
  exitFullScreen,
  getFileBrowseButton,
  getParameter,
  getSearchParameter,
  getStyleFromCSSClass,
  goFullScreen,
  highlight,
  /**
   * Exposed here for legacy code using global window.hueUtils, use utils/storageUtils instead.
   * @deprecated
   */
  hueLocalStorage,
  html2text,
  htmlEncode,
  isFullScreen,
  isOverflowing,
  logError,
  parseHivePseudoJson,
  removeURLParameter,
  replaceURL,
  scrollbarWidth,
  stripHtmlFromFunctions,
  toggleFullScreen,
  UUID,
  waitForObservable,
  waitForRendered,
  waitForVariable,
  /**
   * Exposed here for legacy code using global window.hueUtils, use utils/storageUtils instead.
   * @deprecated
   */
  withLocalStorage
};

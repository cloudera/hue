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
 * Repo for missing jQuery 2 functions, this ease the transition without updating every other plugin in Hue
 *
 */

jQuery.uaMatch = function (ua) {
  ua = ua.toLowerCase();

  var match = /(chrome)[ \/]([\w.]+)/.exec(ua) ||
    /(webkit)[ \/]([\w.]+)/.exec(ua) ||
    /(opera)(?:.*version|)[ \/]([\w.]+)/.exec(ua) ||
    /(msie) ([\w.]+)/.exec(ua) ||
    ua.indexOf("compatible") < 0 && /(mozilla)(?:.*? rv:([\w.]+)|)/.exec(ua) ||
    [];

  return {
    browser: match[ 1 ] || "",
    version: match[ 2 ] || "0"
  };
};

// Don't clobber any existing jQuery.browser in case it's different
if (!jQuery.browser) {
  matched = jQuery.uaMatch(navigator.userAgent);
  browser = {};

  if (matched.browser) {
    browser[ matched.browser ] = true;
    browser.version = matched.version;
  }

  // Chrome is Webkit, but Webkit is also Safari.
  if (browser.chrome) {
    browser.webkit = true;
  } else if (browser.webkit) {
    browser.safari = true;
  }

  jQuery.browser = browser;
}

// Since jQuery.clean is used internally on older versions, we only shim if it's missing
if (!jQuery.clean) {
  jQuery.clean = function (elems, context, fragment, scripts) {
    // Set context per 1.8 logic
    context = context || document;
    context = !context.nodeType && context[0] || context;
    context = context.ownerDocument || context;

    var i, elem, handleScript, jsTags,
      ret = [];

    jQuery.merge(ret, jQuery.buildFragment(elems, context).childNodes);

    // Complex logic lifted directly from jQuery 1.8
    if (fragment) {
      // Special handling of each script element
      handleScript = function (elem) {
        // Check if we consider it executable
        if (!elem.type || rscriptType.test(elem.type)) {
          // Detach the script and store it in the scripts array (if provided) or the fragment
          // Return truthy to indicate that it has been handled
          return scripts ?
            scripts.push(elem.parentNode ? elem.parentNode.removeChild(elem) : elem) :
            fragment.appendChild(elem);
        }
      };

      for (i = 0; (elem = ret[i]) != null; i++) {
        // Check if we're done after handling an executable script
        if (!( jQuery.nodeName(elem, "script") && handleScript(elem) )) {
          // Append to fragment and handle embedded scripts
          fragment.appendChild(elem);
          if (typeof elem.getElementsByTagName !== "undefined") {
            // handleScript alters the DOM, so use jQuery.merge to ensure snapshot iteration
            jsTags = jQuery.grep(jQuery.merge([], elem.getElementsByTagName("script")), handleScript);

            // Splice the scripts into ret after their former ancestor and advance our index beyond them
            ret.splice.apply(ret, [i + 1, 0].concat(jsTags));
            i += jsTags.length;
          }
        }
      }
    }

    return ret;
  };
}

var rscriptType = /\/(java|ecma)script/i,
  oldSelf = jQuery.fn.andSelf || jQuery.fn.addBack;

jQuery.fn.andSelf = function () {
  return oldSelf.apply(this, arguments);
};


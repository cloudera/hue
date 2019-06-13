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

function addTemplateFunctions(item) {
  if (Mustache == "undefined") {
    return;
  }

  function genericDate(val, item) {
    var d = moment(Mustache.render(val, item));
    if (d.isValid()) {
      return d;
    }
    else {
      var number = parseInt(Mustache.render(val, item)) || '';
      if (number) {
        var d = moment(number * 1000); // timestamp * 1000
        if (d.isValid()) {
          return d;
        }
      }
    }
  }

  function genericFormatDate(val, item, format) {
    var d = genericDate(val, item);
    if (d) {
      return d.format(format);
    }
    else {
      return Mustache.render(val, item);
    }
  }

  // Functions

  item.hue_fn_preview = function () {
    return function (val) {
      return '<a href="/filebrowser/view=/' + $.trim(Mustache.render(val, item)) + '">' + $.trim(Mustache.render(val, item)) + '</a>';
    }
  };
  item.hue_fn_embeddeddownload = function () {
    return function (val) {
      return '<a href="/filebrowser/download=/' + $.trim(Mustache.render(val, item)) + '?disposition=inline">' + $.trim(Mustache.render(val, item)) + '</a>';
    }
  };
  item.hue_fn_download = function () {
    return function (val) {
      return '<a href="/filebrowser/download=/' + $.trim(Mustache.render(val, item)) + '">' + $.trim(Mustache.render(val, item)) + '</a>';
    }
  };
  item.hue_fn_date = function () {
    return function (val) {
      return genericFormatDate(val, item, "DD-MM-YYYY");
    }
  };
  item.hue_fn_time = function () {
    return function (val) {
      return genericFormatDate(val, item, "HH:mm:ss");
    }
  };
  item.hue_fn_datetime = function () {
    return function (val) {
      return genericFormatDate(val, item, "DD-MM-YYYY HH:mm:ss");
    }
  };
  item.hue_fn_fulldate = function () {
    return function (val) {
      return genericFormatDate(val, item, null);
    }
  };
  item.hue_fn_timestamp = function () {
    return function (val) {
      var d = moment(Mustache.render(val, item));
      if (d.isValid()) {
        return d.valueOf();
      }
      else {
        return Mustache.render(val, item);
      }
    }
  };
  item.hue_fn_fromnow = function () {
    return function (val) {
      var d = genericDate(val, item);
      if (d && d.isValid()) {
        return d.fromNow();
      }
      else {
        return Mustache.render(val, item);
      }
    }
  };
  item.hue_fn_truncate50 = function () {
    return _truncate(50);
  };
  item.hue_fn_truncate100 = function () {
    return _truncate(100);
  };
  item.hue_fn_truncate200 = function () {
    return _truncate(200);
  };
  item.hue_fn_truncate250 = function () {
    return _truncate(250);
  };
  item.hue_fn_truncate500 = function () {
    return _truncate(500);
  };
  item.hue_fn_truncate1000 = function () {
    return _truncate(1000);
  };

  function _truncate(length) {
    return function (val) {
      var _val = $.trim(Mustache.render(val, item));
      if (_val.length > length) {
        return _val.substr(0, length) + "&hellip;";
      }
      return _val;
    }
  }

  // fix the fields that contain dots in the name
  for (var prop in item) {
    if (item.hasOwnProperty(prop) && prop.indexOf(".") > -1) {
      item[prop.replace(/\./gi, "_")] = item[prop];
    }
  }
}

function fixTemplateDotsAndFunctionNames(template) {
  var _mustacheTmpl = hueUtils.stripHtmlFromFunctions(template);
  var _mustacheTags = _mustacheTmpl.match(/{{(.*?)}}/g);
  if (_mustacheTags){
    $.each(_mustacheTags, function (cnt, tag) {
      if (tag.indexOf("{#") > -1) {
        _mustacheTmpl = _mustacheTmpl.replace(tag, tag.replace(/\#/gi, "#hue_fn_"))
      }
      if (tag.indexOf("{/") > -1) {
        _mustacheTmpl = _mustacheTmpl.replace(tag, tag.replace(/\//gi, "/hue_fn_"))
      }
      if (tag.indexOf(".") > -1) {
        _mustacheTmpl = _mustacheTmpl.replace(tag, tag.replace(/\./gi, "_"))
      }
    });
    _mustacheTmpl = _mustacheTmpl.replace(/\{\{(.+?)\}\}/g, "{{{$1}}}");
    _mustacheTmpl = _mustacheTmpl.replace(/\{\{\{\#hue_fn(.+?)\}\}\}/g, "{{#hue_fn$1}}")
    _mustacheTmpl = _mustacheTmpl.replace(/\{\{\{\/hue_fn(.+?)\}\}\}/g, "{{/hue_fn$1}}")
  }
  return _mustacheTmpl;
}
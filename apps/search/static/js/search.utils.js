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
  function genericFormatDate(val, item, format) {
    var d = moment(Mustache.render(val, item));
    if (d.isValid()) {
      return d.format(format);
    }
    else {
      return Mustache.render(val, item);
    }
  }

  item.preview = function () {
    return function (val) {
      return '<a href="/filebrowser/view/' + $.trim(Mustache.render(val, item)) + '">' + $.trim(Mustache.render(val, item)) + '</a>';
    }
  };
  item.embeddeddownload = function () {
    return function (val) {
      return '<a href="/filebrowser/download/' + $.trim(Mustache.render(val, item)) + '?disposition=inline">' + $.trim(Mustache.render(val, item)) + '</a>';
    }
  };
  item.download = function () {
    return function (val) {
      return '<a href="/filebrowser/download/' + $.trim(Mustache.render(val, item)) + '>' + $.trim(Mustache.render(val, item)) + '</a>';
    }
  };
  item.date = function () {
    return function (val) {
      return genericFormatDate(val, item, "DD-MM-YYYY");
    }
  };
  item.time = function () {
    return function (val) {
      return genericFormatDate(val, item, "HH:mm:ss");
    }
  };
  item.datetime = function () {
    return function (val) {
      return genericFormatDate(val, item, "DD-MM-YYYY HH:mm:ss");
    }
  };
  item.fulldate = function () {
    return function (val) {
      return genericFormatDate(val, item, null);
    }
  };
  item.timestamp = function () {
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
  item.fromnow = function () {
    return function (val) {
      var d = moment(Mustache.render(val, item));
      if (d.isValid()) {
        return d.fromNow();
      }
      else {
        return Mustache.render(val, item);
      }
    }
  };
  item.truncate50 = function () {
    return _truncate(50);
  };
  item.truncate100 = function () {
    return _truncate(100);
  };
  item.truncate200 = function () {
    return _truncate(200);
  };
  item.truncate250 = function () {
    return _truncate(250);
  };
  item.truncate500 = function () {
    return _truncate(500);
  };
  item.truncate1000 = function () {
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

function fixTemplateDots(template) {
  var _mustacheTmpl = template;
  var _mustacheTags = _mustacheTmpl.match(/{{(.*?)}}/g);
  $.each(_mustacheTags, function (cnt, tag) {
    if (tag.indexOf(".") > -1) {
      _mustacheTmpl = _mustacheTmpl.replace(tag, tag.replace(/\./gi, "_"))
    }
  });
  return _mustacheTmpl;
}
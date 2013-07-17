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


//// Get collections utils
function fetcher_success(name, Node, options) {
  return function(data) {
    switch(data.status) {
      case -1:
      $(document).trigger('connection_error.' + name, [options, data])
      break;
      case 0:
        var nodes = [];
        $.each(data[name], function(index, model_dict) {
          var node = new Node({modelDict: model_dict});
          nodes.push(node);
        });
        $(document).trigger('loaded.' + name, [nodes, options]);
      break;
      default:
      case 1:
        $(document).trigger('load_error.' + name, [options, data]);
      break;
    }
  };
}

//// KO utils
ko.bindingHandlers.routie = {
  init: function(element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
    $(element).click(function() {
      var url = ko.utils.unwrapObservable(valueAccessor());
      routie(url);
      return false;
    });
  }
};

ko.bindingHandlers.editableText = {
  init: function(element, valueAccessor) {
    $(element).on('blur', function() {
      var observable = valueAccessor();
      observable( $(this).text() );
    });
  },
  update: function(element, valueAccessor) {
    var value = ko.utils.unwrapObservable(valueAccessor());
    $(element).text(value);
  }
};

//// JQuery Utils
if (jQuery) {
  jQuery.extend({
    setdefault: function(obj, accessor, default_value) {
      if (!(accessor in obj)) {
        obj[accessor] = default_value;
      }
      return obj[accessor];
    }
  });
}

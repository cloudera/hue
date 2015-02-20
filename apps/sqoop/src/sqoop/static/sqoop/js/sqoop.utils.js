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

function fetcher_error(name, Node, options) {
  return function(data) {
    $(document).trigger('connection_error.' + name, [options, data])
  };
}


//// KO utils
ko.bindingHandlers.routie = {
  init: function(element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
    $(element).click(function() {
      var obj = ko.utils.unwrapObservable(valueAccessor());
      var url = null;
      var bubble = false;
      if ($.isPlainObject(obj)) {
        url = obj.url;
        bubble = !!obj.bubble;
      } else {
        url = obj;
      }
      routie(url);
      return bubble;
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

ko.bindingHandlers.clickValue = {
  init: function(element, valueAccessor) {
    var value = ko.utils.unwrapObservable(valueAccessor());
    if ($(element).val() == value) {
      $(element).click();
    }

    $(element).on('click', function() {
      var observable = valueAccessor();
      observable( $(this).val() );
    });
  },
  update: function(element, valueAccessor) {
    var value = ko.utils.unwrapObservable(valueAccessor());
    if ($(element).val() == value) {
      $(element).click();
    }
  }
};

ko.sqoop = {
  'fixModel' : function(root) {
    function parsePropertyName(propertyName) {
      var properties = [];
      if (propertyName) {
        // get object keys in form of array
        var propertyNames = propertyName.split('.');
        // add indexes to array
        $.each(propertyNames, function(index, property) {
          if (property.indexOf(']') !== -1) {
            var left = property.indexOf('[');
            var right = property.indexOf(']');
            var index = parseInt(property.substring(left+1, right));

            properties.push(property.substring(0, left), index);
          } else {
            properties.push(property);
          }
        });
      }

      return properties;
    }

    function getPropertyByName(root, propertyName) {
      var parts = parsePropertyName(propertyName);
      var obj = root;
      $.each(parts, function(index, property) {
        if (ko.isObservable(obj)) {
          obj = obj()[property];
        } else {
          obj = obj[property];
        }
      });
      return obj;
    }

    function setPropertyByName(root, propertyName, propertyValue) {
      var parts = parsePropertyName(propertyName);
      var obj = root;
      var parent = null;
      var propertyName = null;
      if (parts.length != 0) {
        $.each(parts, function(index, property) {
          propertyName = property;
          parent = obj;
          if (ko.isObservable(obj)) {
            obj = obj()[property];
          } else {
            obj = obj[property];
          }
        });

        if (ko.isObservable(parent)) {
          parent()[propertyName] = propertyValue;
        } else {
          parent[propertyName] = propertyValue;
        }
      }
    }

    var models = [];

    // Map to original model
    var root_model = ko.mapping.toJS(root);

    // ko.mapping.visitModel performs a breadth first search.
    ko.mapping.visitModel(root, function(value, parent_name) {
      if (value['fixModel']) {
        models.push(parent_name);
      }
    });
    // Need a depth first search result
    models = models.reverse();

    // Call fixModel on every node that has that method.
    $.each(models, function(index, parent_name) {
      var old_model = getPropertyByName(root_model, parent_name);
      var new_model = getPropertyByName(root, parent_name).fixModel(old_model);
      setPropertyByName(root_model, parent_name, new_model);
    });

    return root_model;
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

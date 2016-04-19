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


function transform_keys(model, keys_dict) {
  $.each(keys_dict, function(key, new_key) {
    if (key in model) {
      model[new_key] = model[key];
      delete model[key];
    }
  });
  return model;
}

function transform_values(model, func_dict) {
  $.each(func_dict, function(key, f) {
    if (key in model) {
      model[key] = f(key, model[key]);
    }
  });
  return model;
}

function to_config(value) {
  return new configs.ConfigModel(value);
}

function to_configs(key, value) {
  $.each(value, function(index, form_dict) {
    value[index] = to_config(form_dict);
  });
  return value;
}

function to_input(value) {
  if (value.type.toLowerCase() == 'map') {
    return new configs.MapInputModel(value);
  } else {
    return new configs.InputModel(value);
  }
}

function to_inputs(key, value) {
  $.each(value, function(index, input_dict) {
    value[index] = to_input(input_dict);
  });
  return value;
}


var configs = (function($) {
  var map_config_properties = {
    'create': function(options) {
      return new SqoopConfig({modelDict: options.data});
    },
    'update': function(options) {
      options.target.initialize({modelDict: options.data})
      return options.target;
    }
  };
  var map_input_properties = {
    'create': function(options) {
      switch(options.data.type.toLowerCase()) {
        case 'map':
        return new SqoopMapInput({modelDict: options.data});

        default:
        return new SqoopInput({modelDict: options.data});
      }
    },
    'update': function(options) {
      options.target.initialize({modelDict: options.data})
      return options.target;
    }
  };
  var map_properties = {
    'link-config': map_config_properties,
    'from-job-config': map_config_properties,
    'to-job-config': map_config_properties,
    'driver-config': map_config_properties,
    'inputs': map_input_properties
  };

  var ConfigModel = koify.Model.extend({
    'id': -1,
    'inputs': [],
    'name': null,
    'type': null,
    'initialize': function(attrs) {
      var self = this;
      attrs = transform_values(attrs, {
        'inputs': to_inputs
      });
      return attrs;
    }
  });

  var InputModel = koify.Model.extend({
    'id': -1,
    'name': null,
    'type': null,
    'size': -1,
    'sensitive': false,
    'values': null,
    'value': "",
    'initialize': function(attrs) {
      var self = this;
      var attrs = $.extend(true, {}, attrs);
      if ('values' in attrs && attrs['values']) {
        attrs['values'] = ($.isArray(attrs['values'])) ? attrs['values'] : attrs['values'].split(',');
      }
      if ('value' in attrs) {
        try {
          attrs.value = decodeURIComponent(attrs.value);
        }
        catch (e) {
        }
      }
      return attrs;
    }
  });

  var MapInputModel = InputModel.extend({
    'value': {},
    'initialize': function(attrs) {
      var self = this;

      if ('value' in attrs && attrs.value) {
        if (!$.isArray(attrs.value)) {
          var map = attrs['value'];
          attrs.value = [];
          $.each(map, function(key, value) {
            attrs.value.push({
              'key': key,
              'value': value
            });
          });
        }
      } else {
        attrs.value = [];
      }
      return attrs;
    }
  });

  var SqoopConfig = koify.MinimalNode.extend({
    'model_class': ConfigModel,
    'map': function() {
      var self = this;
      var mapping_options = $.extend(true, {
        'ignore': ['parent', 'initialize']
      }, map_properties);
      if ('__ko_mapping__' in self) {
        ko.mapping.fromJS(self.model, mapping_options, self);
      } else {
        var mapped = ko.mapping.fromJS(self.model, mapping_options);
        $.extend(self, mapped);
      }
    }
  });

  var SqoopInput = koify.MinimalNode.extend({
    'model_class': InputModel,
    'map': function() {
      var self = this;
      var mapping_options = {
        'ignore': ['parent', 'initialize']
      };
      if ('__ko_mapping__' in self) {
        ko.mapping.fromJS(self.model, mapping_options, self);
      } else {
        var mapped = ko.mapping.fromJS(self.model, mapping_options);
        $.extend(self, mapped);
      }
    }
  });

  var SqoopMapInput = SqoopInput.extend({
    'model_class': MapInputModel,
    'initialize': function() {
      var self = this;
      self.parent.initialize.apply(self, arguments);

      self.addToMap = function() {
        var value = {
          'key': ko.observable(""),
          'value': ko.observable("")
        };
        value.key.subscribe(function() {
          self.value.valueHasMutated();
        });
        value.value.subscribe(function() {
          self.value.valueHasMutated();
        });
        self.value().push(value);
        self.value.valueHasMutated();
      };

      self.removeFromMap = function(index) {
        self.value().splice(index, 1);
        self.value.valueHasMutated();
      };
    },
    fixModel: function(model) {
      var map = {};
      $.each(model.value, function(index, obj) {
        if (obj.key) {
          map[obj.key] = obj.value;
        }
      });
      model.value = map;
      return model;
    }
  });

  return {
    'ConfigModel': ConfigModel,
    'InputModel': InputModel,
    'MapInputModel': MapInputModel,
    'Config': SqoopConfig,
    'Input': SqoopInput,
    'MapInput': SqoopMapInput,
    'MapProperties': map_properties
  };
})(jQuery);

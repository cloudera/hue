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

function to_form(value) {
  return new FormModel(value);
}

function to_forms(key, value) {
  $.each(value, function(index, form_dict) {
    value[index] = to_form(form_dict);
  });
  return value;
}

function to_input(value) {
  return new InputModel(value);
}

function to_inputs(key, value) {
  $.each(value, function(index, input_dict) {
    value[index] = to_input(input_dict);
  });
  return value;
}

var FormModel = koify.Model.extend({
  'id': -1,
  'inputs': [],
  'name': null,
  'type': null,
  'initialize': function(attrs) {
    var self = this;
    var attrs = $.extend(true, attrs, {});
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
  'value': null,
  'initialize': function(attrs) {
    var self = this;
    var attrs = $.extend(true, attrs, {});
    if ('values' in attrs) {
      attrs['values'] = attrs['values'].split(',');
    }
    if ('value' in attrs) {
      attrs.value = decodeURIComponent(attrs.value);
    }
    return attrs;
  }
});

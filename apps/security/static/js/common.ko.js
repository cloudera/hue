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

ko.bindingHandlers.select2 = {
  init: function (element, valueAccessor, allBindingsAccessor, vm) {
    var options = ko.toJS(valueAccessor()) || {};

    if (typeof valueAccessor().update != "undefined") {
      if (options.type == "user" && viewModel.selectableHadoopUsers().indexOf(options.update) == -1) {
        viewModel.availableHadoopUsers.push({
          username: options.update
        });
      }
      if (options.type == "group" && viewModel.selectableHadoopGroups().indexOf(options.update) == -1) {
        viewModel.availableHadoopGroups.push({
          name: options.update
        });
      }
      if (options.type == "action" && viewModel.availableActions().indexOf(options.update) == -1) {
        viewModel.availableActions.push(options.update);
      }
    }
    $(element)
        .select2(options)
        .on("change", function (e) {
          if (typeof e.val != "undefined" && typeof valueAccessor().update != "undefined") {
            valueAccessor().update(e.val);
          }
        })
        .on("select2-open", function () {
          $(".select2-input").off("keyup").data("type", options.type).on("keyup", function (e) {
            if (e.keyCode === 13) {
              var _newVal = $(this).val();
              var _type = $(this).data("type");
              if (_type == "user") {
                viewModel.availableHadoopUsers.push({
                  username: _newVal
                });
              }
              if (_type == "group") {
                viewModel.availableHadoopGroups.push({
                  name: _newVal
                });
              }
              if (_type == "action") {
                viewModel.availableActions.push(_newVal);
              }
              $(element).select2("val", _newVal, true);
              $(element).select2("close");
            }
          });
        })
  },
  update: function (element, valueAccessor, allBindingsAccessor, vm) {
    if (typeof valueAccessor().update != "undefined") {
      $(element).select2("val", valueAccessor().update());
    }
  }
};
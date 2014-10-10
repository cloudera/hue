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
      if (options.type == "group") {
        if (options.update instanceof Array) {
          options.update.forEach(function(opt){
            if (viewModel.selectableHadoopGroups().indexOf(opt) == -1){
              viewModel.availableHadoopGroups.push({
                name: opt
              });
            }
          });
        }
        else if (viewModel.selectableHadoopGroups().indexOf(options.update) == -1){
          viewModel.availableHadoopGroups.push({
            name: options.update
          });
        }
      }
      if (options.type == "action" && viewModel.availableActions().indexOf(options.update) == -1) {
        viewModel.availableActions.push(options.update);
      }
      if (options.type == "scope" && viewModel.availablePrivileges().indexOf(options.update) == -1) {
        viewModel.availablePrivileges.push(options.update);
      }
    }
    $(element)
        .select2(options)
        .on("change", function (e) {
          if (typeof e.val != "undefined" && typeof valueAccessor().update != "undefined") {
            valueAccessor().update(e.val);
          }
        })
        .on("select2-focus", function(e) {
          if (typeof options.onFocus != "undefined"){
            options.onFocus();
          }
        })
        .on("select2-blur", function(e) {
          if (typeof options.onBlur != "undefined"){
            options.onBlur();
          }
        })
        .on("select2-open", function () {
          $(".select2-input").off("keyup").data("type", options.type).on("keyup", function (e) {
            if (e.keyCode === 13) {
              var _isArray = options.update instanceof Array;
              var _newVal = $(this).val();
              var _type = $(this).data("type");
              if ($.trim(_newVal) != "") {
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
                if (_type == "scope") {
                  viewModel.availablePrivileges.push(_newVal);
                }
                if (_type == "role") {
                  var _r = new Role(viewModel, { name: _newVal });
                  viewModel.tempRoles.push(_r);
                  viewModel.roles.push(_r);
                }
                if (_isArray){
                  var _vals = $(element).select2("val");
                  _vals.push(_newVal);
                  $(element).select2("val", _vals, true);
                }
                else {
                  $(element).select2("val", _newVal, true);
                }
                $(element).select2("close");
              }
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

ko.bindingHandlers.hivechooser = {
  init: function(element, valueAccessor, allBindingsAccessor, vm) {
    var self = $(element);
    self.val(valueAccessor()());

    function setPathFromAutocomplete(path){
      self.val(path);
      valueAccessor()(path);
      self.blur();
    }

    self.on("blur", function () {
      valueAccessor()(self.val());
    });

    self.jHueHiveAutocomplete({
      skipColumns: true,
      showOnFocus: true,
      home: "/",
      onPathChange: function (path) {
        setPathFromAutocomplete(path);
      },
      onEnter: function (el) {
        setPathFromAutocomplete(el.val());
      },
      onBlur: function () {
        if (self.val().lastIndexOf(".") == self.val().length - 1){
          self.val(self.val().substr(0, self.val().length - 1));
        }
        valueAccessor()(self.val());
      }
    });
  }
}

ko.bindingHandlers.filechooser = {
  init: function(element, valueAccessor, allBindingsAccessor, vm) {
    var self = $(element);
    self.val(valueAccessor()());

    self.on("blur", function () {
      valueAccessor()(self.val());
    });

    self.after(getFileBrowseButton(self, true, valueAccessor));
  }
};

function getFileBrowseButton(inputElement, selectFolder, valueAccessor) {
  return $("<button>").addClass("btn").addClass("fileChooserBtn").text("..").click(function (e) {
    e.preventDefault();
    // check if it's a relative path
    callFileChooser();

    function callFileChooser() {
      var _initialPath = $.trim(inputElement.val()) != "" ? inputElement.val() : "/";
      if (_initialPath.indexOf("hdfs://") > -1){
        _initialPath = _initialPath.substring(7);
      }
      $("#filechooser").jHueFileChooser({
        suppressErrors: true,
        selectFolder: (selectFolder) ? true : false,
        onFolderChoose: function (filePath) {
          handleChoice(filePath);
          if (selectFolder) {
            $("#chooseFile").modal("hide");
          }
        },
        onFileChoose: function (filePath) {
          handleChoice(filePath);
          $("#chooseFile").modal("hide");
        },
        createFolder: false,
        uploadFile: false,
        initialPath: _initialPath,
        errorRedirectPath: "",
        forceRefresh: true
      });
      $("#chooseFile").modal("show");
    }

    function handleChoice(filePath) {
      inputElement.val("hdfs://" + filePath);
      inputElement.change();
      valueAccessor()(inputElement.val());
    }
  });
}

ko.bindingHandlers.tooltip = {
  update: function (element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
    var options = ko.utils.unwrapObservable(valueAccessor());
    var self = $(element);
    self.tooltip(options);
  }
};
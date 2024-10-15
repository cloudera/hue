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

import * as ko from 'knockout';
import ksb from 'knockout-secure-binding';

var options = {
  attribute: "data-bind",        // default is "data-sbind", using "data-bind" to match regular Knockout bindings
  globals: window,               // makes global window object available to bindings
  bindings: ko.bindingHandlers,  // the Knockout binding handlers to use
  noVirtualElements: false       // allows the use of Knockout virtual elements
};

var is_ksb_enabled = false
console.log("is_ksb_enabled     :"+is_ksb_enabled )
if(is_ksb_enabled) {
  ko.bindingProvider.instance = new ksb(options); // Use the imported 'ksb' as the constructor
}


// Define a custom binding for jQuery UI's autocomplete
ko.bindingHandlers.customAutocomplete = {
init: function (element, valueAccessor, allBindingsAccessor) {
      var options = ko.unwrap(valueAccessor());

      // Check if the appendTo option is provided as an element ID
      var appendToElement;
      if (options.appendTo) {
          appendToElement = document.getElementById(options.appendTo);
      }

      // Initialize the jQuery UI autocomplete widget
      $(element).autocomplete({
          source: options.source,
          select: options.select,
          change: options.change,
          appendTo: appendToElement || undefined,
          // Other options as needed
      });

      // Handle cleanup
      ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
          $(element).autocomplete("destroy");
      });

      // Handle updating the observable with the selected value
      var valueObservable = allBindingsAccessor().textInput;
      if (ko.isObservable(valueObservable)) {
          $(element).on("autocompleteselect", function (event, ui) {
              valueObservable(ui.item.value);
          });
      }
  },
  update: function (element, valueAccessor) {
      var options = ko.unwrap(valueAccessor());

      // Update the jQuery UI autocomplete source if it's an observable
      if (ko.isObservable(options.source)) {
          $(element).autocomplete("option", "source", options.source());
      }
  }
};

ko.bindingHandlers.clickWithArgs = {
  init: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
    var options = valueAccessor();
    var handler = options.handler; // The handler now stores a function reference or a string to look up on the ViewModel
    var params = options.params;
    debugger;
    var newHandler = function() {
      
      // If the handler is a string, check if it's a function on the ViewModel
      if (typeof handler === 'string' && typeof viewModel[handler] === 'function') {
        viewModel[handler].apply(viewModel, params);
      }
      // If the handler is already a function (which we expect for global functions), just call it
      else if (typeof handler === 'function') {
        handler.apply(viewModel, params);
      }
      else {
        throw new Error("clickWithArgs: Handler is not a function.");
      }
    };

    ko.utils.registerEventHandler(element, "click", newHandler);
  }
};



// Custom binding handler for 'dropzone'
ko.bindingHandlers.dropzone = {
  init: function(element, valueAccessor) {
      var options = valueAccessor();
      
      // Initialize Dropzone options object
      var dropzoneOptions = {
          url: options.url,
          clickable: options.clickable,
          paramName: options.paramName,
          // Additional Dropzone options...

          // The `init` option allows binding custom event handlers on Dropzone initialization
          init: function() {
              this.on('complete', function(file) {
                  // Call `huePubSub.publish` with the path
                  huePubSub.publish('assist.dropzone.complete', file.fullPath || file.name);
              });
          }
      };
      
      // Apply the disabled state if needed
      if (options.disabled) {
          dropzoneOptions.maxFiles = 0;
      }

      // Ensure proper cleanup if element is removed (Dropzone's destroy method does this automatically)
      
      // Create an instance of Dropzone on the element with the given options
      var myDropzone = new Dropzone(element, dropzoneOptions);

      // Store the Dropzone instance for later access (e.g., for updates or disposal)
      ko.utils.domNodeDisposal.addDisposeCallback(element, function() {
          myDropzone.destroy();
      });
  },
  update: function(element, valueAccessor) {
      // Update logic, if necessary (e.g., if options are observables and you need to react to changes)
      var options = valueAccessor();
      var myDropzone = Dropzone.forElement(element);

      // Dynamically update the disabled state based on a condition or observable
      if (options.disabled) {
          myDropzone.disable();
      } else {
          myDropzone.enable();
      }
  }
};

function applyConditional(element, data, applyCallback) {
  Object.keys(data).forEach(function (key) {
    var conditionInfo = data[key];
    var condition = ko.unwrap(conditionInfo[0]);
    var trueValue = ko.unwrap(conditionInfo[1]);
    var falseValue = ko.unwrap(conditionInfo[2]);
    
    var valueToApply = condition ? trueValue : falseValue;
    applyCallback(element, key, valueToApply);
  });
}

ko.bindingHandlers.conditionalAttr = {
  update: function(element, valueAccessor) {
    var conditionalAttributes = valueAccessor();
    applyConditional(element, conditionalAttributes, function(elem, attrName, value) {
      elem.setAttribute(attrName, value);
    });
  }
};

ko.bindingHandlers.conditionalStyle = {
  update: function (element, valueAccessor) {
    var styleConditions = valueAccessor();
    applyConditional(element, styleConditions, function(elem, styleName, value) {
      elem.style[styleName] = value;
    });
  }
};



const proxiedKoRegister = ko.components.register;
const registeredComponents = [];

ko.components.register = function () {
  // This guarantees a ko component is only registered once
  // Some currently get registered twice when switching between notebook and editor
  if (registeredComponents.indexOf(arguments[0]) === -1) {
    registeredComponents.push(arguments[0]);
    return proxiedKoRegister.apply(this, arguments);
  }
};

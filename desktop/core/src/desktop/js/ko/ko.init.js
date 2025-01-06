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
import huePubSub from 'utils/huePubSub';
import ksb from 'ko/ksb';
var options = {
  attribute: "data-bind",        // default is "data-sbind", using "data-bind" to match regular Knockout bindings
  globals: window,
  bindings: ko.bindingHandlers,  // the Knockout binding handlers to use
  noVirtualElements: true       // allows the use of Knockout virtual elements
};

var is_ksb_enabled = true
console.log("is_ksb_enabled     :"+is_ksb_enabled )
if(is_ksb_enabled) {
  ko.bindingProvider.instance = new ksb(options); // Use the imported 'ksb' as the constructor
}

const proxiedKoRegister = ko.components.register;
const registeredComponents = [];

ko.bindingHandlers.customdropzone = {
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
    var styles = ko.unwrap(valueAccessor());

    Object.keys(styles).forEach(function (styleProperty) {
      var styleConditions = styles[styleProperty];
      var condition = styleConditions[0];
      var trueStyle = styleConditions[1];
      var falseStyle = styleConditions[2];
      
      var isConditionMet = false;

      // Check if condition is an object, indicating an expression
      if (typeof condition === 'object' && condition.hasOwnProperty('lhs') && condition.hasOwnProperty('op') && condition.hasOwnProperty('rhs')) {
        // Use the provided `evaluateExpression` to determine the result
        isConditionMet = evaluateExpression(condition);
      } else {
        // If it's not an object, it should be a direct boolean value or observable
        isConditionMet = ko.unwrap(condition);
      }

      // Apply the correct style based on the condition's result
      element.style[styleProperty] = isConditionMet ? trueStyle : falseStyle;
    });
  }
};

// Verify 'evaluateExpression' is accessible in the scope where your binding handler is defined

ko.bindingHandlers.templateIf = {
  init: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
      // Using ko.utils.domData.set to store the original element content
      ko.utils.domData.set(element, 'originalContent', element.innerHTML);
      return { 'controlsDescendantBindings': true };
  },
  update: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
      var value = valueAccessor();
      var condition = evaluateExpression(value.condition);
      
      // Clear the element first
      ko.virtualElements.emptyNode(element);
      
      if (condition) {
          // If the condition is true, render the template.
          var templateName = ko.unwrap(value.name);
          // The following line handles the template rendering
          ko.renderTemplate(templateName, bindingContext, {}, element);
      } else {
          // If the condition is false, restore the original content
          element.innerHTML = ko.utils.domData.get(element, 'originalContent');
      }
  }
};

ko.virtualElements.allowedBindings.templateIf = true;  // Allow binding on virtual elements

function evaluateExpression(expr) {
  var result;
  var lhs = ko.unwrap(expr.lhs);
  var rhs = ko.unwrap(expr.rhs);

  switch (expr.op) {
      case '==':
          result = lhs == rhs;
          break;
      case '===':
          result = lhs === rhs;
          break;
      case '<':
          result = lhs < rhs;
          break;
      case '<=':
          result = lhs <= rhs;
          break;
      case '>':
          result = lhs > rhs;
          break;
      case '>=':
          result = lhs >= rhs;
          break;
      // Add more operators as needed
      default:
          throw new Error('Unsupported operator in expression: ' + expr.op);
  }
  
  return result;
}

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

  ko.bindingHandlers.eventWithArgs = {
    init: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
        
        const options = valueAccessor();
        const eventType = options.event || 'click'; // Default to 'click' if no event is specified

        const handlerPath = options.handler; // Path to the handler function, e.g., '$root.someFunction'
        const params = options.params || []; // Parameters to pass to the function

        // Registration function for the event handler
        const registerEventHandler = function(eventType, handler) {
            ko.utils.registerEventHandler(element, eventType, function(event) {
                debugger;
                const handlerFunction = resolveHandler(bindingContext, handlerPath);
                const resolvedParams = params.map(param => resolveParameter(bindingContext, param));
                if (typeof handlerFunction === 'function') {
                    // Ensure that `this` is the current binding context's `$data`
                    handlerFunction.apply(bindingContext.$data, [event].concat(resolvedParams));
                } else {
                    throw new Error("eventWithArgs: Handler is not a function.");
                }
            });
        };

        registerEventHandler(eventType); // Register using the specified event type
    }
};

function resolveHandler(bindingContext, path) {
  const pathParts = path.split('.');
  if (pathParts[0] === 'huePubSub' && (pathParts[1] === 'publish' || pathParts[1] === 'subscribe')) {
    return function() {
      const args = Array.prototype.slice.call(arguments);
      huePubSub[pathParts[1]].apply(huePubSub, args.slice(1));
    };
  }
  let currentContext = bindingContext;

  for (let i = 0; i < pathParts.length; i++) {
    const part = pathParts[i];
    const isLastPart = i === pathParts.length - 1;
    
    switch (part) {
      case '$root':
        currentContext = currentContext.$root;
        break;
      case '$parent':
        currentContext = currentContext.$parent;
        break;
      case '$parents': // In case of $parents[index]
        if (pathParts.length > i + 1) {
          var index = parseInt(pathParts[++i].replace(/^\[|\]$/g, ''), 10);
          currentContext = currentContext.$parents[index];
        } else {
          throw new Error("Handler path must include index for $parents, e.g., $parents[0].someFunction");
        }
        break;
      case '$data': // $data is more often implicit and may not need to be used
        currentContext = currentContext.$data;
        break;
      default: // Regular property access
        if (isLastPart) {
          if (typeof currentContext[part] === 'function') {
            // Return the method/function directly without invoking it
            return currentContext[part];
          } else {
            throw new Error(`Expected function at path '${path}' but got ${typeof currentContext[part]}.`);
          }
        } else {
          if (currentContext[part] === undefined) {
            throw new Error(`Property '${part}' not found on context.`);
          }
          // Update the current context but don't invoke methods if it's an intermediate part of the path
          currentContext = ko.unwrap(currentContext[part]);
        }
        break;
    }
  }

  throw new Error(`Handler function not found at path '${path}'.`);
}

// Enhanced helper function to resolve parameters dynamically
function resolveParameter(bindingContext, param) {
  if (typeof param === 'string' && param.startsWith('$')) {
    // Handle array index notation, e.g., $parents[1]
    const arrayIndexMatch = param.match(/(.+)\[(\d+)\]$/);
    if (arrayIndexMatch) {
      const basePath = arrayIndexMatch[1];
      const index = parseInt(arrayIndexMatch[2], 10);
      const baseContext = resolveHandler(bindingContext, basePath);
      return Array.isArray(baseContext) ? baseContext[index] : undefined;
    }
    return resolveHandler(bindingContext, param);
  }
  return param; // Return the parameter as is if it's not a context reference
}

// Usage in the HTML binding with 'click' event
/*
data-bind="eventWithArgs: {
    event: 'click', 
    handler: 'yourClickHandlerFunction', 
    params: ['param1', 'param2']
}"
*/

// Usage in the HTML binding with 'dblclick' event
/*
data-bind="eventWithArgs: {
    event: 'dblclick', 
    handler: 'yourDblClickHandlerFunction', 
    params: ['param1', 'param2']
}"
*/

ko.components.register = function () {
  // This guarantees a ko component is only registered once
  // Some currently get registered twice when switching between notebook and editor
  if (registeredComponents.indexOf(arguments[0]) === -1) {
    registeredComponents.push(arguments[0]);
    return proxiedKoRegister.apply(this, arguments);
  }
};

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

  
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
import huePubSub from 'utils/huePubSub';

var options = {
  attribute: "data-bind",        // default is "data-sbind", using "data-bind" to match regular Knockout bindings
  globals: window,
  bindings: ko.bindingHandlers,  // the Knockout binding handlers to use
  noVirtualElements: false       // allows the use of Knockout virtual elements
};

var is_ksb_enabled = true
console.log("is_ksb_enabled     :"+is_ksb_enabled )
if(is_ksb_enabled) {
  ko.bindingProvider.instance = new ksb(options); // Use the imported 'ksb' as the constructor
}

ko.bindingHandlers.logRoot = {
  init: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
    console.log('Root context:', bindingContext.$root);

    // Log all the bound values
    const bindings = allBindings();
    console.log('All bindings for element:', element);
    for (const binding in bindings) {
      if (bindings.hasOwnProperty(binding)) {
        console.log(`${binding}:`, ko.unwrap(bindings[binding]));
      }
    }
  }
};

ko.bindingHandlers.aceEditorInit = {
  init: function (element, valueAccessor) {
    // Initialize the Ace editor
    const editor = ace.edit(element);
    // Get the observable to store the editor instance
    const options = valueAccessor();
    if (ko.isObservable(options)) {
      options(editor);
    }

    // Clean up the editor instance when the element is removed
    ko.utils.domNodeDisposal.addDisposeCallback(element, function() {
      editor.destroy();
    });
  }
};

ko.bindingHandlers.aceBinding = {
  init: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
    // Prepare the configuration for aceEditor
    const config = {
      snippet: bindingContext.$data,
      contextTooltip: I18n('Right-click for details'),
      expandStar: I18n('Right-click to expand with columns'),
      highlightedRange: bindingContext.$data.result.statement_range,
      readOnly: bindingContext.$root.isPresentationMode(),
      aceOptions: bindingContext.$root.getAceOptions()
    };

    // Call the aceEditor binding's init function with the prepared config
    ko.bindingHandlers.aceEditor.init(element, () => config, allBindings, viewModel, bindingContext);
  },
  update: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
    // Prepare the configuration for aceEditor
    const config = {
      snippet: bindingContext.$data,
      contextTooltip: I18n('Right-click for details'),
      expandStar: I18n('Right-click to expand with columns'),
      highlightedRange: bindingContext.$data.result.statement_range,
      readOnly: bindingContext.$root.isPresentationMode(),
      aceOptions: bindingContext.$root.getAceOptions()
    };

    // Call the aceEditor binding's update function with the prepared config
    ko.bindingHandlers.aceEditor.update(element, () => config, allBindings, viewModel, bindingContext);
  }
};

// ko.init.js
// ko.init.js
ko.bindingHandlers.aceEditorConfig = {
  init: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
    const data = bindingContext.$data; // Access the current data context
    const config = valueAccessor(); // Get the value passed to the binding

    // Define the aceOptions based on your requirements
    const aceOptions = {
      showLineNumbers: true, // Example option
      showGutter: true,      // Example option
      maxLines: 25,          // Example option
      minLines: 3            // Example option
    };
    let configs = {
      aceEditor: {
        snippet: data,
        aceOptions: aceOptions,

        contextTooltip: I18n('Right-click for details'),
        expandStar: I18n('Right-click to expand with columns'),
        highlightedRange: data.result.statement_range,
        readOnly: bindingContext.$parent.isPresentationMode()
      },
    };
    // Return the configuration object including aceEditor with snippet and aceOptions
    return configs;
  }
};
// const sortableFunctionRegistry = {
//   stopHandler: function(event, ui) {
//     const $element = $(event.target);
//     $element.find('.snippet-body').slideDown('fast', function () {
//       $(MAIN_SCROLLABLE).scrollTop(lastWindowScrollPosition);
//     });
//   },
//   helperHandler: function(event) {
//     lastWindowScrollPosition = $(MAIN_SCROLLABLE).scrollTop();
//     const $element = $(event.target);
//     $element.find('.snippet-body').slideUp('fast', function () {
//       $('.sortable-snippets').sortable('refreshPositions');
//     });
//     const _par = $('<div>')
//       .css('overflow', 'hidden')
//       .addClass('card-widget snippet-move-helper')
//       .width($element.parents('.snippet').width());
//     $('<h2>')
//       .addClass('card-heading')
//       .html($element.parents('h2').html())
//       .appendTo(_par)
//       .find('.hover-actions, .snippet-actions')
//       .removeClass('hover-actions')
//       .removeClass('snippet-actions');
//     $('<pre>')
//       .addClass('dragging-pre muted')
//       .html(ko.dataFor($element.parents('.card-widget')[0]).statement())
//       .appendTo(_par);
//     _par.css('height', '100px');
//     return _par;
//   }
// };

// // Custom binding handler for sortable
// ko.bindingHandlers.sortableConfig = {
//   init: function(element, valueAccessor) {
//     debugger;
//     const options = ko.unwrap(valueAccessor());
//     $(element).sortable({
//       handle: options.handle,
//       axis: options.axis,
//       opacity: options.opacity,
//       placeholder: options.placeholder,
//       greedy: options.greedy,
//       stop: sortableFunctionRegistry[options.stop],
//       helper: sortableFunctionRegistry[options.helper]
//     });
//   }
// };

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

ko.bindingHandlers.componentWithParams = {
  init: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
    const options = valueAccessor();
    const componentName = options.name; // Name of the component
    const params = options.params || {}; // Parameters to pass to the component

    // Resolve parameters from the binding context
    const resolvedParams = {};
    for (const key in params) {
      resolvedParams[key] = resolveParameter(bindingContext, params[key]);
    }

    // Use afterRender to ensure the DOM is ready
    ko.utils.domNodeDisposal.addDisposeCallback(element, function() {
      // Clean up if needed
    });

    // Apply the component binding
    ko.applyBindingsToNode(element, {
      component: {
        name: componentName,
        params: resolvedParams
      }
    }, bindingContext);

    // Delay the initialization of the Ace editor
    setTimeout(() => {
      if (!resolvedParams.editor) {
        const editorElement = $('.ace-editor');
        if (editorElement) {
          const editor = ace.edit(editorElement);
          resolvedParams.editor = editor;
        }
      }
    }, 100); // Delay for 100ms or adjust as needed

    return { controlsDescendantBindings: true };
  }
};


ko.bindingHandlers.clickWithArgs = {
  init: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
    const options = valueAccessor();
    const handlerPath = options.handler; // Path to the handler function, e.g., '$root.someFunction'
    const params = options.params || []; // Parameters to pass to the function

    const newHandler = function() {
      // Resolve the handler function from the path
      const handler = resolveHandler(bindingContext, handlerPath);
      const resolvedParams = params.map(param => resolveParameter(bindingContext, param));

      if (typeof handler === 'function') {
        handler.apply(bindingContext.$data, resolvedParams);
      } else {
        throw new Error("advancedClick: Handler is not a function.");
      }
    };

    ko.utils.registerEventHandler(element, "click", newHandler);
  }
};

ko.bindingHandlers.cssWithFunction = {
  update: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
    const options = valueAccessor();
    const functionPath = options.functionPath;
    const params = options.params || [];

    // Resolve the function from the path
    const cssFunction = resolveHandler(bindingContext, functionPath);
    const resolvedParams = params.map(param => resolveParameter(bindingContext, param));

    // Evaluate the function to get the CSS classes
    const cssClasses = ko.unwrap(cssFunction.apply(bindingContext.$data, resolvedParams));

    ko.bindingHandlers.css.update(element, () => cssClasses, allBindings, viewModel, bindingContext);
  }
};

ko.bindingHandlers.styleWithFunction = {
  update: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
    const options = valueAccessor();
    const functionPath = options.functionPath;
    const params = options.params || [];

    // Resolve the function from the path
    const styleFunction = resolveHandler(bindingContext, functionPath);
    const resolvedParams = params.map(param => resolveParameter(bindingContext, param));

    // Evaluate the function to get the style attributes
    const styles = ko.unwrap(styleFunction.apply(bindingContext.$data, resolvedParams));

    ko.bindingHandlers.style.update(element, () => styles, allBindings, viewModel, bindingContext);
  }
};

ko.bindingHandlers.visibleWithFunction = {
  update: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
    const options = valueAccessor();
    const functionPath = options.functionPath;
    const params = options.params || [];

    // Resolve the function from the path
    const visibleFunction = resolveHandler(bindingContext, functionPath);
    const resolvedParams = params.map(param => resolveParameter(bindingContext, param));

    // Evaluate the function to determine visibility
    const isVisible = ko.unwrap(visibleFunction.apply(bindingContext.$data, resolvedParams));

    ko.bindingHandlers.visible.update(element, () => isVisible, allBindings, viewModel, bindingContext);
  }
};

function resolveHandler(bindingContext, path) {
  const pathParts = path.split('.');
  let context = bindingContext;

  pathParts.forEach(part => {
    const arrayIndexMatch = part.match(/(.+)\[(\d+)\]$/);
    if (arrayIndexMatch) {
      // Handle array-like access
      const basePart = arrayIndexMatch[1];
      const index = parseInt(arrayIndexMatch[2], 10);

      if (basePart === '$parents') {
        context = context.$parents[index];
      } else if (basePart === '$components') {
        context = context.$components[index];
      } else if (basePart === '$data') {
        context = context.$data[index];
      } else {
        context = ko.unwrap(context[basePart])[index];
      }
    } else {
      // Handle regular parts
      if (part === '$root') {
        context = context.$root;
      } else if (part === '$parent') {
        context = context.$parent;
      } else if (part === '$parents') {
        context = context.$parents;
      } else if (part === '$data') {
        context = context.$data;
      } else {
        context = ko.unwrap(context[part]);
      }
    }
  });

  return context;
}

ko.bindingHandlers.conditionalTemplates = {
  init: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
    const options = valueAccessor();
    const type = ko.unwrap(bindingContext.$data.type);
    const suffix = ko.unwrap(bindingContext.$data.suffix);

    const templates = options.templates;
    let selectedTemplate = null;

    // Evaluate each condition and select the appropriate template
    for (const template of templates) {
      if (template.condition(type)) {
        selectedTemplate = template.name + suffix;
        break;
      }
    }

    if (selectedTemplate) {
      ko.applyBindingsToNode(element, {
        template: {
          name: selectedTemplate,
          data: bindingContext.$data
        }
      }, bindingContext);
    }

    return { controlsDescendantBindings: true };
  }
};

ko.bindingHandlers.textWithArgs = {
  update: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
    const options = valueAccessor();
    const handlerPath = options.handler; // Path to the handler function, e.g., '$root.someFunction'
    const params = options.params || []; // Parameters to pass to the function

    // Resolve the handler function from the path
    const handler = resolveHandler(bindingContext, handlerPath);
    const resolvedParams = params.map(param => resolveParameter(bindingContext, param));

    if (typeof handler === 'function') {
      const result = handler.apply(bindingContext.$data, resolvedParams);
      ko.utils.setTextContent(element, result);
    } else {
      throw new Error("textWithArgs: Handler is not a function.");
    }
  }
};



ko.bindingHandlers.dblclickWithArgs = {
  init: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
    const options = valueAccessor();
    const handlerPath = options.handlerPath; // Path to the handler function, e.g., '$root.someFunction'
    const params = options.params || []; // Parameters to pass to the function

    const newHandler = function() {
      // Resolve the handler function from the path
      const handler = resolveHandler(bindingContext, handlerPath);

      // Resolve each parameter dynamically
      const resolvedParams = params.map(param => resolveParameter(bindingContext, param));

      if (typeof handler === 'function') {
        handler.apply(bindingContext.$data, resolvedParams);
      } else {
        throw new Error("dblclickWithArgs: Handler is not a function.");
      }
    };

    ko.utils.registerEventHandler(element, "dblclick", newHandler);
  }
};


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

ko.bindingHandlers.clickFunctionWithNested = {
  init: function(element, valueAccessor, allBindings, viewModel) {
    var path = valueAccessor().split('.');
    var handler = viewModel;
    
    // Traverse the path to get to the function
    for (var i = 0; i < path.length; i++) {
      if (handler[path[i]] !== undefined) {
        handler = handler[path[i]];
      } else {
        throw new Error("clickFunctionWithNested: Unable to resolve path: " + path.join('.'));
      }
    }

    if (typeof handler !== 'function') {
      throw new Error("clickFunctionWithNested: Handler at path is not a function.");
    }
    
    ko.utils.registerEventHandler(element, "click", function() {
      handler.call(viewModel);
    });
  }
};

ko.bindingHandlers.clickFunctionWithPath = {
  init: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
    var path = valueAccessor().split('.');
    var context = bindingContext.$root; // Start at the $root

    // Traverse the path to get to the target observable or function
    while (path.length > 1) {
      context = ko.unwrap(context[path.shift()]);
    }

    var methodName = path.shift();

    ko.utils.registerEventHandler(element, "click", function() {
      var targetFunction = context[methodName];
      if (typeof targetFunction === 'function') {
        targetFunction.apply(context);
      } else {
        throw new Error("clickFunctionWithPath: Method not found at path.");
      }
    });
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

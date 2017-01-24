// (c) Copyright 2016 Cloudera, Inc. All rights reserved.
/**
 * @module ko/components/componentUtils
 * @description Common component code.
 */
var $ = require('jquery');
var ko = require('knockout');
var _ = require('_');

/**
 * Create a context that is outside of the current component context.
 * Make sure to attach the current component to the context in case you want to use it.
 * @param {object} bindingContext The current bindingHandler context.
 * @return {object}
 */
function createEscapedContext(bindingContext) {
  var outsideContext = bindingContext;
  var $component = bindingContext.$component;

  // find the component context
  while (outsideContext && outsideContext.$data !== $component) {
    outsideContext = outsideContext.$parentContext;
  }

  // context outside component
  outsideContext = outsideContext.$parentContext;

  var innerContext = outsideContext.extend({
    $component: $component
  });

  return innerContext;
}

// binding to escape the context inside a component. This allows us to embed content and
// have it work with the context of the page where the content is, and not have it
// broken by the component context. The component context is still available through
// the $component property.
ko.bindingHandlers.componentContextEscaper = {
  init: function(element, valueAccessor, allBindings, viewModel, bindingContext) {

    // binding context is component, but we want to escape that, since the injected
    // html should work outside and inside a component with no issues

    // we can be multiple levels down in the binding context inside an component
    // so we need to figure out how far to traverse upwards to esacpe.
    //
    // note that this might not work properly if there is a component embedded
    // in the component template (since we might need to escape two components then).
    // it will work with a nested template, if the template is passed in through
    // the content tags.

    var escapedContext = createEscapedContext(bindingContext);

    ko.applyBindingsToDescendants(escapedContext, element);

    return { controlsDescendantBindings: true };

  }
};
ko.virtualElements.allowedBindings.componentContextEscaper = true;

/**
 * A child template is defined as:
 *  any block level element that is captured using componentUtils.captureChildTemplate
 * So if you have component <foo>
 * and it contains a custom tag: <bar> (note: bar is not a component)
 * And in Foo constructor, you call:
 *   componentUtils.captureChildTemplate(this, componentInfo.templateNodes, 'bar');
 *
 * Then this component usage is valid:
 * <foo>
 *   Custom foo content
 *   <bar>
 *     <div>Bar child nodes</div>
 *   </bar>
 * </foo>
 *
 * If you have <bar>, then you can inject that node anywhere in <foo>'s template definition
 *  with *this* bindingHandler:
 *
 * foo's template definition:
 * <div>
 *  My foo stuff
 * </div>
 * <div data-bind="injectChildTemplate: 'foo'></div>
 * <div>
 *  Other foo stuff
 * </div>
 *
 * If you have more than one foo element, we inject one at a time.  So multiple injectChildTemplates must be called.
 */
ko.bindingHandlers.injectChildTemplate = {
  init: function(element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
    var $component = bindingContext.$component;
    var childTemplateName = valueAccessor();

    var childTemplates = $component.childNodeTemplates[childTemplateName];
    var nodes = childTemplates.pop(0) || [];

    // apply the template binding handler with any found child nodes
    ko.bindingHandlers.template.init(element, function() { return { nodes: nodes }; });
    return { controlsDescendantBindings: true };
  },
  update: function(element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
    // do the same thing as componentContextEscaper, grab the outer component context
    var escapedContext = createEscapedContext(bindingContext);

    // apply the template binding update handler in order to bind the correct context.
    ko.bindingHandlers.template.update(element, function() { return {}; }, allBindingsAccessor, viewModel, escapedContext);
  }

};
ko.virtualElements.allowedBindings.injectChildTemplate = true;

module.exports = {
  /**
   * Provides a common way to add a component under cloudera-ui.
   * Certain hooks are installed for tests to capture the component view model.
   * We also prevent you from double registerring a component.
   * @param {function} ViewModel A component constructor that takes 2 arguments params and componentInfo.
   * @param {string} name The html tag name of the component.
   * @param {string} template The html string to inject.
   */
  addComponent: function(ViewModel, name, template) {
    if (_.isFunction(ViewModel.prototype.decorateTemplate)) {
      // wrap the child class with the parent component's template
      template = ViewModel.prototype.decorateTemplate(template);
    }

    ViewModel.COMPONENT_NAME = name;
    ViewModel.config = {
      /**
       * Save the componentConstructor so we can access it from the knockout config.
       */
      componentConstructor: ViewModel,

      viewModel: {
        /**
         * Invoke a constructor.
         * @param {object} params Component parameters defined on the component element.
         * @param {function} [params.registerForTest] A callback that invokes during applyBindings in a test.
         * @param {object} componentInfo The component node before the component template is injected.
         */
        createViewModel: function(params, componentInfo) {
          params = params || {};

          var viewModel = new ViewModel(params, componentInfo);

          /**
           * You can specify a param when in test that captures the viewmodel.
           */
          if (params.registerForTest) {
            params.registerForTest(viewModel);
          }

          return viewModel;
        }
      },

      // we allow you to specify a requirejs-text path or the actual template
      template: template.indexOf('text!') === -1 ? template : { require: template },

      // Since the template is distributed with the component, we allow the loading to be synchronous.
      // This flag also makes testing more predictable.
      synchronous: true
    };

    // don't double register a component
    if (!ko.components.isRegistered(name)) {
      ko.components.register(name, ViewModel.config);
    }
  },

  /**
   * Returns the component viewmodel if any.
   * @param {Node} node The component parent node to lookup the component definition.
   * @return {*}
   */
  componentFor: function(componentElement) {
    if (componentElement === undefined) {
      return undefined;
    }

    var $context;

    // find the first child with a $component in it's context.
    var firstChild = _.find(componentElement.childNodes, function(componentElement) {
      $context = ko.contextFor(componentElement);
      return $context !== undefined && $context.$component;
    });
    if (_.isNull(firstChild)) {
      return undefined;
    }

    return $context ? $context.$component : undefined;
  },

  /**
   * Removes all child nodes from componentTemplateNodes that has the same nodeName as templateNodeName.
   * These nodes can be accessed with injectChildTemplate.
   * @param {object} component The component viewModel instance.
   * @param {Node[]} componentTemplateNodes Nodes passed into the component constructor: componentInfo.templateNodes
   * @param {string} templateNodeName The nodes you want to remove from componentTemplateNodes.
   */
  captureChildTemplate: function(component, componentTemplateNodes, templateNodeName) {
    var nodes = _.remove(componentTemplateNodes, function(node) {
      return node.nodeName.toLowerCase() === templateNodeName;
    });

    if (!component.childNodeTemplates) {
      component.childNodeTemplates = {};
    }

    component.childNodeTemplates[templateNodeName] = [];

    _.each(nodes, function(node) {
      component.childNodeTemplates[templateNodeName].push(node.childNodes);
    });
  }
};

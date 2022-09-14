import * as ko from 'knockout';
import { createElement } from 'react';
import { createRoot } from 'react-dom/client';

import { loadComponent } from '../../reactComponents/imports';

/**
 * REACT KNOCKOUT INTEGRATION
 * This is a oneway binding from knockout to react.js. Use the data-binding called reactWrapper
 * followed by the component name. Props are passed in as js object literal coded as a string using
 * the props param. Any new components used must also be added to the import file
 * desktop/core/src/desktop/js/reactComponents/imports.js.
 *
 * Example usage:
 *
 * <MyComponent data-bind="reactWrapper: 'MyComponent',
 *    props: { title: 'Result title', activeExecutable: activeExecutable }">
 * </MyComponent>
 *
 *
 * The name of the component element tag (eg <MyComponent>) can be anything, but for consistency
 * and to stay close to how normal react components look we use the actual component name.
 */

const getProps = allBindings => {
  const props = allBindings.get('props');

  // Functions are not valid as a React child
  return { ...props, children: ko.toJS(props.children) };
};

ko.bindingHandlers.reactWrapper = (() => {
  return {
    init: function (el, valueAccessor, allBindings, viewModel, bindingContext) {
      const componentName = ko.unwrap(valueAccessor());
      const props = getProps(allBindings);

      // The component's react root should only be created once per DOM
      // load so we pass it along via the bindingContext to be reused in the KO update call.
      const reactRoot = createRoot(el);
      el.__KO_React_root = reactRoot;
      loadComponent(componentName).then(Component => {
        reactRoot.render(createElement(Component, props));
      });

      // Since the react component is a root component we need to handle the
      // unmounting explicitly if the dom node is disposed by Knockout, e.g. via "ko if:"
      ko.utils.domNodeDisposal.addDisposeCallback(el, () => reactRoot.unmount());

      // Tell Knockout that it does not need to update the children
      // of this component, since that is now handled by React
      return { controlsDescendantBindings: true };
    },

    update: function (el, valueAccessor, allBindings, viewModel, bindingContext) {
      const componentName = ko.unwrap(valueAccessor());
      const props = getProps(allBindings);

      loadComponent(componentName).then(Component => {
        el.__KO_React_root.render(createElement(Component, props));
      });

      // Handle KO observables
      Object.entries(props).forEach(([propName, propValue]) => {
        if (ko.isObservable(propValue)) {
          const koSubscription = propValue.subscribe(() => {
            loadComponent(componentName).then(Component => {
              el.__KO_React_root.render(
                createElement(Component, { ...props, [propName]: propValue() })
              );
            });
          });
          koSubscription.disposeWhenNodeIsRemoved(el);
        }
      });
    }
  };
})();

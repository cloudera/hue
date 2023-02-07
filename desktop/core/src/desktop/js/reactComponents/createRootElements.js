import { createElement } from 'react';
import { createRoot } from 'react-dom/client';

import { loadComponent } from './imports';

/**
 * REACT INTEGRATION
 * This react integration script can be used for components that are placed directly in an
 * HTML page on load and do not need to have data passed from Knockout.js. The script is called
 * using a globally defined function called createReactComponents. The component element
 * tag must be present in the part of the DOM specified by the selector when this script runs.
 * The component must also be imported and added to the file js/reactComponents/imports.js
 * Exmple when used in the editor .mako file:
 *
 * <script type="text/javascript">
 *   (function () {
 *     window.createReactComponents('#embeddable_editor');
 *   })();
 * </script>
 *
 * <MyComponent
 *    data-reactcomponent='MyComponent'
 *    data-props='{"myObj": 2, "children": "mako template only", "version" : "${sys.version_info[0]}"}'>
 * </MyComponent>
 *
 */

async function render(name, props, root) {
  const Component = await loadComponent(name);
  root.render(createElement(Component, props));
}

export async function createReactComponents(selector) {
  // Find all DOM containers
  document.querySelectorAll(`${selector} [data-reactcomponent]`).forEach(domContainer => {
    const componentName = domContainer.dataset['reactcomponent'];
    const rawPropDataset = domContainer.dataset.props ? JSON.parse(domContainer.dataset.props) : {};
    const root = createRoot(domContainer);
    render(componentName, rawPropDataset, root);
  });
}

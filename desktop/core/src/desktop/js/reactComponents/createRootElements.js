import { createElement } from 'react';
import { createRoot } from 'react-dom/client';
import PropTypes from 'prop-types';

import { loadComponent } from './imports';

/**
 * REACT INTEGRATION
 * This react integration script can be used for components that are placed directly in an
 * HTML page on load and do not need to have data passed from Knockout.js. The script is called
 * using a globally defined function called createReactComponents. The component element
 * tag must be present in the part of the DOM specified by the selector when this script runs.
 * The component must also be imported and added to the file xxxx.... 
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
 *    data-props='{"children": "mako template only", "version" : "${sys.version_info[0]}"}'>
 * </MyComponent>
 * 
 */


// Very basic prop parser, needs to be extended if used.
const parseDatasetPropValue = ({ propName, propValue, proptypesDefinition, componentName }) => {
  const type = proptypesDefinition[propName];
  let parsedValue = propValue;
  switch (type) {
    case PropTypes.string:
      break;
    case PropTypes.number:
      parsedValue = parseInt(propValue, 10);
      break;
    case PropTypes.bool:
      parsedValue = propValue.toLowerCase() === 'true';
      break;
    case PropTypes.any:
      break;      
    case undefined:
      console.warn(`PropType definiton is missing for prop "${propName}" in ${componentName}`);
      break;
    default:
      console.warn(
        `PropType for "${propName}" in ${componentName} not implemented in react prop bridge`
      );
      break;
  }

  return parsedValue;
};

const parseProps = (name, rawPropDataset, myPropTypes) => {
  const props = {};
  for (let propName in rawPropDataset) {
    const propValue = rawPropDataset[propName];
    const parsedPropValue = parseDatasetPropValue({
      propName,
      propValue,
      proptypesDefinition: myPropTypes,
      componentName: name
    });
    props[propName] = parsedPropValue;
  }
  return props;
};

async function render(name, rawPropDataset, root) {
  const Component = await loadComponent(name);
  const props = parseProps(name, rawPropDataset, Component.propTypes);
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

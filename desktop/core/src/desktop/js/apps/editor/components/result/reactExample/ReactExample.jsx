import PropTypes from 'prop-types';
import * as React from 'react';

import ReactExampleGlobal from '../../../../../reactComponents/ReactExampleGlobal/ReactExampleGlobal';
import { useHuePubSub } from '../../../../../reactComponents/useHuePubSub';

import './ReactExample.scss';

('use strict');

const propTypes = {
  // This example component recieves the "activeExecutable" used in the result page but
  // the props in general can of course be of any type
  activeExecutable: PropTypes.oneOfType([PropTypes.func, PropTypes.shape({ id: PropTypes.string })])
};
const defaultProps = { title: 'Default result title' };

const ReactExample = ({ title, activeExecutable }) => {
  // Example of having the react component rerender based on changes from useHuePubSub.
  // Use with caution and preferrably only at the top level component in your component tree.
  const editorCursor = useHuePubSub({ topic: 'editor.cursor.position.changed' });

  const id = activeExecutable?.id;
  const position = editorCursor?.position !== undefined ? JSON.stringify(editorCursor.position) : 'not available';

  return (
    <div className="react-example">
      <h1 className="react-example__title">{title}</h1>
      <p className="react-example__description">
        I'm an Editor specific react component containing subcomponents. The dynamic id that I'm
        getting from a Knockout observable is {id}.
      </p>
      <p className="react-example__description">
        {`I'm also geting a cursor position from hue huePubSub using the hook useHuePubSub which is
        updated on each 'editor.cursor.position.changed'. Cursor position is
        ${position}`}
      </p>
      <ReactExampleGlobal className="react-example__react-example-global-component">
        I'm a button from the application global component set
      </ReactExampleGlobal>
    </div>
  );
};

ReactExample.propTypes = propTypes;
ReactExample.defaultProps = defaultProps;

export default ReactExample;

'use strict';

import React, { FunctionComponent, useState } from 'react';
import { Button, Modal } from 'antd';

// tsx-files don't have the same baseUrl as other js files so
// we are using a relative path when importing
import { Ace } from '../../../../../ext/ace';

import { CURSOR_POSITION_CHANGED_EVENT } from '../../aceEditor/AceLocationHandler';
import ReactExampleGlobal from '../../../../../reactComponents/ReactExampleGlobal/ReactExampleGlobal';
import { useHuePubSub } from '../../../../../reactComponents/useHuePubSub';
import SqlExecutable from '../../../execution/sqlExecutable';

import './ReactExample.scss';

export interface ReactExampleProps {
  title: string;
  // This example component recieves the "activeExecutable" used in the result page but
  // the props in general can of course be of any type
  activeExecutable?: SqlExecutable;
}

// When we have type definitions and Ace imported using webackpack we should
// use those types instead of creating our own, e.g. Ace.Position
interface EditorCursor {
  position: Ace.Position;
}

const defaultProps = { title: 'Default result title' };

// Using the FunctionComponent generic is optional. Alternatively you can explicitly
// define the children prop like in the ReactExampleGlobal component.
const ReactExample: FunctionComponent<ReactExampleProps> = ({ title, activeExecutable }) => {
  // Example of having the react component rerender based on changes from useHuePubSub.
  // Use with caution and preferrably only at the top level component in your component tree.
  const editorCursor = useHuePubSub<EditorCursor>({ topic: CURSOR_POSITION_CHANGED_EVENT });

  const id = activeExecutable?.id;
  const position =
    editorCursor?.position !== undefined ? JSON.stringify(editorCursor.position) : 'not available';

  const [isModalOpen, setIsModalOpen] = useState(false);

  const showModal = () => {
    setIsModalOpen(true);
  };

  const handleOk = () => {
    setIsModalOpen(false);
  };

  const handleCancel = () => {
    setIsModalOpen(false);
  };

  return (
    // The 'antd' class is added to the root element since we want it to apply the correct
    // "global" styling to its antd sub components, e.g. the antd Button.
    // Also make sure that the component specific Antd style is imported in the file
    // 'root-wrapped-antd.less'.
    <div className="react-example antd">
      <h1 className="react-example__title">{title}</h1>
      <Button type="primary" onClick={showModal}>
        Open Modal
      </Button>

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
      <Button type="primary" onClick={() => console.info('clicked')}>
        I'm an Antd button
      </Button>
      <Modal title="Basic Modal" open={isModalOpen} onOk={handleOk} onCancel={handleCancel}>
        <p>Some contents...</p>
        <p>Some contents...</p>
        <p>Some contents...</p>
      </Modal>
    </div>
  );
};

ReactExample.defaultProps = defaultProps;

export default ReactExample;

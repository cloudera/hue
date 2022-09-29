import React, { useState } from 'react';
import './FileChooserComponentButton.scss';
import FileChooserModal from '../FileChooserModal/FileChooserModal';
import { Button } from 'antd';

const FileChooserComponentButton = (): JSX.Element => {
  const [show, setShow] = useState(false);

  return (
    <div>
      <Button type="primary" onClick={() => setShow(true)}>
        File chooser component
      </Button>
      <FileChooserModal onClose={() => setShow(false)} show={show} />
    </div>
  );
};

export default FileChooserComponentButton;

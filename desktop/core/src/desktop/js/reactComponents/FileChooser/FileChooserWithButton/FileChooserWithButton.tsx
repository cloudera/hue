import React, { useState } from 'react';
import { Button } from 'antd';

import './FileChooserWithButton.scss';
import FileChooserModal from '../FileChooserModal/FileChooserModal';

interface FileChooserWithButtonProps {
  title: string;
}

const defaultProps = { title: 'File chooser component' };

const FileChooserWithButton: React.FC<FileChooserWithButtonProps> = ({ title }): JSX.Element => {
  const [show, setShow] = useState(false);

  return (
    <>
      <Button className="file-chooser__button" type="primary" onClick={() => setShow(true)}>
        {title}
      </Button>

      <FileChooserModal
        onCancel={() => setShow(false)}
        show={show}
        title="Choose a file"
        okText="Select"
      />
    </>
  );
};

FileChooserWithButton.defaultProps = defaultProps;

export default FileChooserWithButton;

import React from 'react';
import Modal from 'antd/lib/modal/Modal';

interface FileProps {
  show: boolean;
  onCancel: () => void;
  title: string;
  okText: string;
}

const defaultProps = { title: 'Choose a file', okText: 'Select' };

const FileChooserModal: React.FC<FileProps> = ({ show, onCancel, title, okText }) => {
  const handleOk = () => {
    //temporary until the file is selected through the file chooser compoent
    onCancel();
  };

  const handleCancel = () => {
    onCancel();
  };

  return (
    <Modal
      title={title}
      open={show}
      onOk={handleOk}
      onCancel={handleCancel}
      okText={okText}
    ></Modal>
  );
};

FileChooserModal.defaultProps = defaultProps;

export default FileChooserModal;

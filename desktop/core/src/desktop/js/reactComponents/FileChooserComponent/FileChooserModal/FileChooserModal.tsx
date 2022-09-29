import React from 'react';
import './FileChooserModal.scss';
import Modal from 'antd/lib/modal/Modal';

interface FileProps {
  show: boolean;
  onClose: () => void;
}

const FileChooserModal: React.FC<FileProps> = ({ show, onClose }) => {
  const handleOk = () => {
    onClose();
  };
  const handleCancel = () => {
    onClose();
  };
  return (
    <Modal
      title="Choose a file"
      open={show}
      onOk={handleOk}
      onCancel={handleCancel}
      okText="Select"
    ></Modal>
  );
};

export default FileChooserModal;

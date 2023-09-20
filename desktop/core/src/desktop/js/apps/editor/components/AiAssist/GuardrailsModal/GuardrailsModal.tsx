import React from 'react';
import Alert from 'cuix/dist/components/Alert/Alert';
import Modal from 'cuix/dist/components/Modal';
import { GuardrailAlert } from '../guardRails';

import './GuardrailsModal.scss';

interface GuardrailsModalProps {
  open: boolean;
  onClose: () => void;
  alert: GuardrailAlert;  
}

const GuardrailsModal = ({
  open,
  alert,
  onClose
}: GuardrailsModalProps) => {
  return (
    <Modal
      wrapClassName="cuix hue-ai-guardrails-modal"
      open={open}
      title={alert?.title}
      onCancel={onClose}
      onOk={onClose}
      cancellable={false} 
      okText="Ok"      
    >    
    <Alert description={alert?.nql} type="warning" />      
    <p>{alert?.msg}</p>
    </Modal>
  );
};

export default GuardrailsModal;

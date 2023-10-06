/*
  Licensed to Cloudera, Inc. under one
  or more contributor license agreements.  See the NOTICE file
  distributed with this work for additional information
  regarding copyright ownership.  Cloudera, Inc. licenses this file
  to you under the Apache License, Version 2.0 (the
  "License"); you may not use this file except in compliance
  with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
*/

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

const GuardrailsModal = ({ open, alert, onClose }: GuardrailsModalProps) => {
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
      {alert?.nql && <Alert description={alert?.nql} type="warning" />}
      <p>{alert?.msg}</p>

      <div className="hue-ai-guardrails-modal__ai-response-container">
        <h4 className="hue-ai-guardrails-modal__ai-title">AI response</h4>
        <p className="hue-ai-guardrails-modal__ai-text-container">{alert?.aiMsg}</p>
      </div>
    </Modal>
  );
};

export default GuardrailsModal;

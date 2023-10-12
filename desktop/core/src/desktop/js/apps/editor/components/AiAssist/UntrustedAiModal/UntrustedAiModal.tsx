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

import React, { useState, useEffect } from 'react';
import Modal from 'cuix/dist/components/Modal';

const UNTRUSTED_SERVICE_APPROVED_KEY = 'hue.aiAssistBar.untrustedServiceApproved';

import { getFromLocalStorage, setInLocalStorage } from 'utils/storageUtils';
import { getLastKnownConfig } from '../../../../../config/hueConfig';

export interface UntrustedAiModalProps {
  onCloseBar: () => void;
  aiAssistBarExpanded: boolean;
}

const UntrustedAiModal = ({onCloseBar, aiAssistBarExpanded}) => {
  const storedUntrustedServiceApproval = getFromLocalStorage(
    'hue.aiAssistBar.untrustedServiceApproved',
    false
  );
  const isTrustedService = getLastKnownConfig()?.hue_config?.is_ai_trusted_service;

  const [showUntrustedServiceModal, setShowUntrustedServiceModal] = useState(false);
  const [untrustedServiceApproved, setUntrustedServiceApproved] = useState(
    storedUntrustedServiceApproval
  );

  useEffect(() => {
    if (aiAssistBarExpanded && !isTrustedService && !untrustedServiceApproved) {
      setShowUntrustedServiceModal(true);
    }    
  }, [aiAssistBarExpanded]);

  const handleUntrustedServiceModalAccept = () => {
    setInLocalStorage(UNTRUSTED_SERVICE_APPROVED_KEY, true);
    setShowUntrustedServiceModal(false);
    setUntrustedServiceApproved(true);
  };

  const handleUntrustedServiceModalCancel = () => {
    setShowUntrustedServiceModal(false);
    setUntrustedServiceApproved(false);
    onCloseBar();
  };

  return showUntrustedServiceModal ? (
    <Modal
      open
      title="Warning about sharing data"
      okText="Approve"
      cancelText="Cancel"
      onCancel={handleUntrustedServiceModalCancel}
      onOk={handleUntrustedServiceModalAccept}
    >
      <p>
        The AI service with the name {getLastKnownConfig()?.hue_config.ai_service_name} is not
        configured as trusted. All input, metadata and sample data used by the AI assistant will be
        shared with the provider of this service. Do you approve?
      </p>
    </Modal>
  ) : null;
};

export default UntrustedAiModal;

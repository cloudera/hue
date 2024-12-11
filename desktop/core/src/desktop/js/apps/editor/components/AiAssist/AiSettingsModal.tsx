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

import React, { useMemo, useState } from 'react';
import { Button, Select } from 'antd';
import DefaultButton from 'cuix/dist/components/Button/Button';
import Modal from 'cuix/dist/components/Modal';
import AiAssistantIcon from '../../../../components/icons/AiAssistantIcon';
import I18n from 'utils/i18n';

import Title from 'antd/lib/typography/Title';
import { DefaultOptionType } from 'antd/lib/select';

import './AiSettingsModal.scss';

interface Props {
  open: boolean;
  onClose: () => void;
  allDbNames: string[];
  additionalDbNames: string[];
  setAdditionalDbNames: (value: string[]) => void;
}
const AiSettingsModal = ({
  open,
  onClose,
  allDbNames,
  additionalDbNames,
  setAdditionalDbNames
}: Props): JSX.Element => {
  const [selectedDBNames, setSelectedDBNames] = useState(additionalDbNames);

  const okHandler = () => {
    setAdditionalDbNames(selectedDBNames);
    onClose();
  };

  const cancelHandler = () => {
    setSelectedDBNames(additionalDbNames);
    onClose();
  };

  const dbSelectOptions = useMemo<DefaultOptionType[] | undefined>(
    () => allDbNames && allDbNames.map(option => ({ label: option, value: option })),
    [allDbNames]
  );

  return (
    <Modal
      wrapClassName="cuix hue-ai-preview-modal"
      open={open}
      title={
        <>
          <AiAssistantIcon className="hue-settings-modal__icon" />
          {I18n('AI Assistant Settings')}
        </>
      }
      onCancel={cancelHandler}
      width={'100ch'}
      footer={
        <div className="hue-settings-modal-footer">
          <Button key="submit" type="primary" onClick={okHandler}>
            {I18n('OK')}
          </Button>
          <div className="hue-settings-modal-footer__spacer"></div>
          <DefaultButton data-event="" onClick={cancelHandler}>
            {I18n('Cancel')}
          </DefaultButton>
        </div>
      }
    >
      <Title level={4}>{I18n('Select Additional Databases')}</Title>
      <Select
        mode="multiple"
        className="hue-settings-modal-db_selector"
        allowClear={true}
        getPopupContainer={triggerNode => triggerNode.parentElement}
        placeholder={I18n('Select one or more databases')}
        value={selectedDBNames}
        onChange={setSelectedDBNames}
        options={dbSelectOptions}
      />
    </Modal>
  );
};

export default AiSettingsModal;

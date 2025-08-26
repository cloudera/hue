// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// 'License'); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an 'AS IS' BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

'use strict';

import React, { useState } from 'react';
import { Modal, Skeleton } from 'antd';
import PrimaryButton from 'cuix/dist/components/Button/PrimaryButton';
import Button from 'cuix/dist/components/Button/Button';
import PlusCircleIcon from '@cloudera/cuix-core/icons/react/PlusCircleIcon';

import { Ace } from '../../../../../ext/ace';
import { i18nReact } from '../../../../../utils/i18nReact';
import { useHuePubSub } from '../../../../../utils/hooks/useHuePubSub/useHuePubSub';
import useLoadData from '../../../../../utils/hooks/useLoadData/useLoadData';
import ReactExampleGlobal from '../../../../../reactComponents/ReactExampleGlobal/ReactExampleGlobal';
import LoadingErrorWrapper from '../../../../../reactComponents/LoadingErrorWrapper/LoadingErrorWrapper';
import huePubSub from '../../../../../utils/huePubSub';
import { GLOBAL_INFO_TOPIC } from '../../../../../reactComponents/GlobalAlert/events';
import { HueAlert } from '../../../../../reactComponents/GlobalAlert/types';

import { CURSOR_POSITION_CHANGED_EVENT } from '../../aceEditor/AceLocationHandler';
import SqlExecutable from '../../../execution/sqlExecutable';

import './ReactExample.scss';

export interface ReactExampleProps {
  title?: string;
  activeExecutable?: SqlExecutable;
}

interface EditorHistoryEntry {
  id: string;
  statement: string;
  status: string;
  created: string;
}

interface EditorHistoryResponse {
  history: EditorHistoryEntry[];
  total: number;
}

/**
 * @remarks
 * This code is not intended for production. It only serves as an example
 * for new developers and AI assistants.
 * @example
 * Usage in mako template:
 * ```tsx
 * <ReactExample data-bind="reactWrapper: 'ReactExample', props: { activeExecutable: activeExecutable }"></ReactExample>
 * ```
 */
const ReactExample = ({ title, activeExecutable }: ReactExampleProps): JSX.Element => {
  const { t, ready: i18nReady } = i18nReact.useTranslation(undefined, { useSuspense: false });

  const displayTitle = title || t('Schedule');

  // Example: Reactive data with useHuePubSub
  const editorCursor = useHuePubSub<{ position: Ace.Position }>({
    topic: CURSOR_POSITION_CHANGED_EVENT
  });

  // Example: API data loading with useLoadData + LoadingErrorWrapper
  const {
    data: historyData,
    loading: loadingHistory,
    error: historyError,
    reloadData: reloadHistory
  } = useLoadData<EditorHistoryResponse>('/api/v1/editor/get_history', {
    params: { limit: 5 },
    onSuccess: data => {
      huePubSub.publish<HueAlert>(GLOBAL_INFO_TOPIC, {
        message: t('Editor history loaded successfully with {{total}} items', { total: data.total })
      });
    },
    onError: () => {} // Errors handled by LoadingErrorWrapper
  });

  // Example: getting the id of the active executable via Knockout binding
  const id = activeExecutable?.id;

  // Example: getting the cursor position of the editor via useHuePubSub
  const position = editorCursor?.position
    ? JSON.stringify(editorCursor.position)
    : t('Not available');

  const [isModalOpen, setIsModalOpen] = useState(false);

  const showModal = (): void => setIsModalOpen(true);
  const handleOk = (): void => setIsModalOpen(false);
  const handleCancel = (): void => setIsModalOpen(false);

  // Example: LoadingErrorWrapper error configuration
  const errorConfig = [
    {
      enabled: !!historyError,
      message: t('Failed to load editor history'),
      description: historyError,
      actionText: t('Retry'),
      onClick: reloadHistory
    }
  ];

  // Example: The i18n is not ready yet, so we return a skeleton
  if (!i18nReady) {
    return (
      <div className="antd">
        <Skeleton />
      </div>
    );
  }

  return (
    // The 'antd' class is added to the root element since we want it to apply the correct
    // "global" styling to its antd sub components, e.g. the antd Button.
    // Only add the antd and cuix if this is a true react root component, i.e. has no parent react component.
    <div className="react-example cuix antd">
      <h1 className="react-example__title hue-h1">{displayTitle}</h1>
      <p className="react-example__description">
        {t(
          "I'm an Editor specific react component containing subcomponents. The dynamic id that I'm getting from a Knockout observable is {{id}}.",
          { id }
        )}
      </p>
      <p className="react-example__description">
        {t(
          "I'm also getting a cursor position from hue huePubSub using the hook useHuePubSub which is updated on each 'editor.cursor.position.changed'. Cursor position is {{position}}",
          { position }
        )}
      </p>
      <ReactExampleGlobal>
        {t("I'm a button from the application global component set")}
      </ReactExampleGlobal>

      {/* We always use aria-label for icon only buttons */}
      <PrimaryButton icon={<PlusCircleIcon />} onClick={showModal} aria-label={t('Open Modal')} />

      {/* Example of displaying data loaded with useLoadData using LoadingErrorWrapper */}
      <div className="react-example__history-section">
        <h3 className="react-example__history-section-title">
          {t('Editor History (useLoadData + LoadingErrorWrapper example)')}
        </h3>
        <LoadingErrorWrapper loading={loadingHistory} errors={errorConfig}>
          {historyData && (
            <div>
              <p>{t('Total history items: {{total}}', { total: historyData.total })}</p>
              <Button onClick={reloadHistory}>{t('Reload History')}</Button>
              {historyData.history?.slice(0, 3).map(item => (
                <div key={item.id} className="react-example__history-item">
                  <span className="react-example__history-item-status">{item.status}</span> -{' '}
                  {item.statement.substring(0, 50)}...
                </div>
              ))}
            </div>
          )}
        </LoadingErrorWrapper>
      </div>

      {/* The title and content of the Modal is internationalized using the t-function */}
      <Modal title={t('Modify')} open={isModalOpen} onOk={handleOk} onCancel={handleCancel}>
        <p>{t('Settings')}</p>
      </Modal>
    </div>
  );
};

export default ReactExample;

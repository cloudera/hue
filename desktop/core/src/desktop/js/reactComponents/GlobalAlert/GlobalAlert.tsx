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

import React, { useState } from 'react';
import { AlertProps } from 'antd/lib/alert';
import Alert from 'cuix/dist/components/Alert/Alert';

import './GlobalAlert.scss';
import {
  GLOBAL_ERROR_TOPIC,
  GLOBAL_INFO_TOPIC,
  GLOBAL_WARNING_TOPIC,
  HIDE_GLOBAL_ALERTS_TOPIC
} from './events';
import { HueAlert } from './types';
import { useHuePubSub } from '../../utils/hooks/useHuePubSub';
import { i18nReact } from 'utils/i18nReact';

type alertType = AlertProps['type'];

interface VisibleAlert {
  alert: HueAlert;
  type: alertType;
  timeoutHandle?: number;
}

const clearCloseTimeout = (alert: VisibleAlert) => {
  if (alert.timeoutHandle) {
    clearTimeout(alert.timeoutHandle);
  }
};

const GlobalAlert: React.FC = () => {
  const [alerts, setAlerts] = useState<VisibleAlert[]>([]);
  const updateAlerts = (alert: HueAlert, type: alertType) => {
    if (!alert.message) {
      return;
    }
    setAlerts(activeAlerts => {
      // Prevent showing the same message multiple times.
      // TODO: Consider showing a count in the error notification when the same message is reported multiple times.
      if (activeAlerts.some(activeAlerts => activeAlerts.alert.message === alert.message)) {
        return activeAlerts;
      }

      const newAlert: VisibleAlert = { alert, type };

      if (type === 'info' || alert.noStick) {
        newAlert.timeoutHandle = setTimeout(() => {
          handleClose(newAlert);
        }, 3000);
      }

      return [...activeAlerts, newAlert];
    });
  };

  useHuePubSub<HueAlert>({
    topic: GLOBAL_ERROR_TOPIC,
    callback: newAlert => updateAlerts(newAlert, 'error')
  });

  useHuePubSub<HueAlert>({
    topic: GLOBAL_INFO_TOPIC,
    callback: newAlert => updateAlerts(newAlert, 'info')
  });

  useHuePubSub<HueAlert>({
    topic: GLOBAL_WARNING_TOPIC,
    callback: newAlert => updateAlerts(newAlert, 'warning')
  });

  useHuePubSub<void>({
    topic: HIDE_GLOBAL_ALERTS_TOPIC,
    callback: () => {
      alerts.forEach(visibleAlert => clearCloseTimeout(visibleAlert));
      setAlerts([]);
    }
  });

  const handleClose = (alertToClose: VisibleAlert) => {
    const filteredAlerts = alerts.filter(alert => alert !== alertToClose);
    clearCloseTimeout(alertToClose);
    setAlerts(filteredAlerts);
  };

  const { t } = i18nReact.useTranslation();

  const getHeader = (alert: VisibleAlert) => {
    if (alert.type === 'error') {
      return t('Error');
    } else if (alert.type === 'info') {
      return t('Info');
    } else if (alert.type === 'warning') {
      return t('Warning');
    }
  };

  return (
    <div className="hue-alert flash-messages cuix antd">
      {alerts.map(visibleAlert => (
        <Alert
          key={visibleAlert.alert.message}
          type={visibleAlert.type}
          message={getHeader(visibleAlert)}
          description={visibleAlert.alert.message}
          showIcon={true}
          closable={true}
          onClose={() => handleClose(visibleAlert)}
        />
      ))}
    </div>
  );
};

export default GlobalAlert;

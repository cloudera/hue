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

import './AlertComponent.scss';
import { i18nReact } from '../../utils/i18nReact';
import { useHuePubSub } from '../useHuePubSub';

interface HueAlert {
  message: string;
  noStick: boolean;
}

type alertType = AlertProps['type'];

interface VisibleAlert {
  alert: HueAlert;
  type: alertType;
}
const AlertComponent: React.FC = () => {
  const [alert, setAlerts] = useState<VisibleAlert[]>([]);
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
        setTimeout(() => {
          handleClose(newAlert);
        }, 3000);
      }

      return [...activeAlerts, newAlert];
    });
  };

  useHuePubSub<HueAlert>({
    topic: 'hue.global.error',
    callback: newAlert => {
      updateAlerts(newAlert, 'error');
    }
  });

  useHuePubSub<HueAlert>({
    topic: 'hue.global.info',
    callback: newAlert => {
      updateAlerts(newAlert, 'info');
    }
  });

  useHuePubSub<HueAlert>({
    topic: 'hue.global.warning',
    callback: newAlert => {
      updateAlerts(newAlert, 'warning');
    }
  });

  const handleClose = (alertObjToClose: VisibleAlert) => {
    const filteredAlerts = alert.filter(alertObj => alertObj !== alertObjToClose);
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
      {alert.map(alertObj => (
        <Alert
          key={alertObj.alert.message}
          type={alertObj.type}
          message={getHeader(alertObj)}
          description={alertObj.alert.message}
          showIcon={true}
          closable={true}
          onClose={() => handleClose(alertObj)}
        />
      ))}
    </div>
  );
};

export default AlertComponent;

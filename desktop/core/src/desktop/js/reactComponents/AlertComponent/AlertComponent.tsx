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

import React, { useEffect, useState } from 'react';
import Alert from 'cuix/dist/components/Alert/Alert';

import huePubSub from 'utils/huePubSub';
import './AlertComponent.scss';
import { i18nReact } from '../../utils/i18nReact';

interface HueAlert {
  message: string;
}

interface VisibleAlert {
  alert: HueAlert;
  type: 'error' | 'info' | 'warning';
}

const AlertComponent: React.FC = () => {
  const [alert, setAlerts] = useState<VisibleAlert[]>([]);

  const updateAlerts = (alert, type) => {
    if (!alert.message) {
      return;
    }
    setAlerts(activeAlerts => {
      // Prevent showing the same message multiple times.
      // TODO: Consider showing a count in the error notification when the same message is reported multiple times.
      if (activeAlerts.some(activeAlerts => activeAlerts.alert.message === alert.message)) {
        return activeAlerts;
      }
      return [...activeAlerts, { alert, type }];
    });
  };

  useEffect(() => {
    const hueSub = huePubSub.subscribe('hue.global.error', (newAlert: HueAlert) => {
      updateAlerts(newAlert, 'error');
    });
    return () => {
      hueSub.remove();
    };
  }, []);

  useEffect(() => {
    const hueSub = huePubSub.subscribe('hue.global.info', (newAlert: HueAlert) => {
      updateAlerts(newAlert, 'info');
    });
    return () => {
      hueSub.remove();
    };
  }, []);

  useEffect(() => {
    const hueSub = huePubSub.subscribe('hue.global.warning', (newAlert: HueAlert) => {
      updateAlerts(newAlert, 'warning');
    });
    return () => {
      hueSub.remove();
    };
  }, []);

  const handleClose = (alertObjToClose: HueAlert) => {
    const filteredAlerts = alert.filter(alertObj => alertObj.alert !== alertObjToClose);
    setAlerts(filteredAlerts);
  };

  const { t } = i18nReact.useTranslation();

  const getHeader = (alert) => {
    if (alert.type === 'error') {
      return t('Error');
    } 
    else if (alert.type === 'info') {
      return t('Info');
    } 
    else if (alert.type === 'warning') {
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
          onClose={() => handleClose(alertObj.alert)}
        />
      ))}
    </div>
  );
};

export default AlertComponent;

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

interface ErrorAlert {
  message: string;
}

const AlertComponent: React.FC = () => {
  const [errors, setErrors] = useState<ErrorAlert[]>([]);

  useEffect(() => {
    const hueSub = huePubSub.subscribe('hue.global.error', (errorObj: ErrorAlert) => {
      setErrors(prevData => [...prevData, errorObj]);
    });
    return () => {
      hueSub.remove();
    };
  }, []);

  const handleClose = (errorObjToClose: ErrorAlert) => {
    const filteredErrors = errors.filter(errorObj => errorObj !== errorObjToClose);
    setErrors(filteredErrors);
  };

  //TODO: add support for warnings and success messages
  return (
    <div className="hue-alert flash-messages cuix antd">
      {errors.map((errorObj, index) => (
        <Alert
          key={index}
          type="error"
          message={errorObj.message}
          closable={true}
          onClose={() => handleClose(errorObj)}
        />
      ))}
    </div>
  );
};

export default AlertComponent;

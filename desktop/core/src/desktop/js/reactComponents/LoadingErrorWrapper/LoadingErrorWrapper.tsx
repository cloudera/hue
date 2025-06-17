// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import React from 'react';
import { Alert, AlertProps, Spin } from 'antd';
import { BorderlessButton } from 'cuix/dist/components/Button';
import SpinnerIcon from 'cuix/dist/components/SpinnerIcon';

import './LoadingErrorWrapper.scss';

interface WrapperError {
  enabled: boolean;
  message: AlertProps['message'];
  description?: AlertProps['description'];
  actionText?: string;
  onClick?: AlertProps['onClick'];
  closable?: AlertProps['closable'];
}

interface LoadingErrorWrapperProps {
  loading?: boolean;
  errors?: WrapperError[];
  children: React.ReactNode;
  hideOnLoading?: boolean;
  hideOnError?: boolean;
}

const LoadingErrorWrapper = ({
  loading = false,
  errors = [],
  children,
  hideOnLoading = false,
  hideOnError = false
}: LoadingErrorWrapperProps): JSX.Element => {
  if (loading) {
    return (
      <div className="loading-error-wrapper__spinner">
        <Spin
          spinning={loading}
          indicator={<SpinnerIcon size="default" />}
          data-testid="loading-error-wrapper__spinner"
        >
          {hideOnLoading === false && children}
        </Spin>
      </div>
    );
  }

  const enabledErrors = errors.filter(error => error.enabled);
  if (enabledErrors.length > 0) {
    return (
      <>
        <div className="loading-error-wrapper__errors" data-testid="loading-error-wrapper__errors">
          {enabledErrors.map(error => (
            <Alert
              showIcon
              key={error.message?.toString()}
              type="error"
              message={error.message}
              description={error.description}
              closable={error.closable}
              action={
                <BorderlessButton onClick={error.onClick}>{error.actionText}</BorderlessButton>
              }
            />
          ))}
        </div>
        {hideOnError === false && children}
      </>
    );
  }

  return <>{children}</>;
};

export default LoadingErrorWrapper;

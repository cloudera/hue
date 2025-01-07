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

import { Spin } from 'antd';
import { PrimaryButton } from 'cuix/dist/components/Button';
import React from 'react';
import './LoadingErrorWrapper.scss';

interface WrapperError {
  enabled: boolean;
  message: string;
  action?: string;
  onClick?: () => void;
}

interface LoadingErrorWrapperProps {
  loading: boolean;
  errors: WrapperError[];
  children: React.ReactNode;
}

const LoadingErrorWrapper = ({
  loading,
  errors,
  children
}: LoadingErrorWrapperProps): JSX.Element => {
  if (loading) {
    // TODO: discuss in UI meeting, if we need to render children while loading
    // Initial thoughts:
    // -- On first render -> hide children
    // -- On re-render -> render children
    return (
      <Spin spinning={loading} data-testid="loading-error-wrapper__sppiner">
        {children}
      </Spin>
    );
  }

  const enabledErrors = errors.filter(error => error.enabled);
  if (enabledErrors.length > 0) {
    return (
      <>
        {enabledErrors
          .filter(error => error.enabled)
          .map(error => (
            <div className="loading-error-wrapper__error" key={error.message}>
              <div>{error.message}</div>
              {error.onClick && (
                <PrimaryButton onClick={error.onClick} data-event="">
                  {error.action}
                </PrimaryButton>
              )}
            </div>
          ))}
      </>
    );
  }

  return <>{children}</>;
};

export default LoadingErrorWrapper;

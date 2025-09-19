// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// See the NOTICE file distributed with this work for additional information
// regarding copyright ownership. Cloudera, Inc. licenses this file to you under
// the Apache License, Version 2.0 (the "License"); you may not use this file
// except in compliance with the License. You may obtain a copy of the License at
// http://www.apache.org/licenses/LICENSE-2.0
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
// WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
// License for the specific language governing permissions and limitations under
// the License.

import React, { ReactNode } from 'react';
import { Result } from 'antd';
import Button from 'cuix/dist/components/Button/Button';
import { ErrorBoundary } from 'react-error-boundary';
import { i18nReact } from '../../../utils/i18nReact';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onRetry?: () => void;
}

// Functional fallback content with i18n
const DefaultFallback = ({ onRetry }: { onRetry?: () => void }): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  return (
    <Result
      status="error"
      title={t('Something went wrong')}
      subTitle={t(
        'An error occurred while loading the table browser. Please try refreshing the page.'
      )}
      extra={[
        <Button key="retry" onClick={onRetry}>
          {t('Try Again')}
        </Button>,
        <Button key="refresh" onClick={() => window.location.reload()}>
          {t('Refresh Page')}
        </Button>
      ]}
    />
  );
};

const TableBrowserErrorBoundary = ({ children, fallback, onRetry }: Props): JSX.Element => {
  return (
    <ErrorBoundary
      fallbackRender={({ resetErrorBoundary }) =>
        fallback ?? <DefaultFallback onRetry={() => resetErrorBoundary()} />
      }
      onError={(error, info) => {
        // eslint-disable-next-line no-console
        console.error('TableBrowser Error Boundary caught an error:', error, info);
      }}
      onReset={() => {
        onRetry?.();
      }}
    >
      {children}
    </ErrorBoundary>
  );
};

export default TableBrowserErrorBoundary;

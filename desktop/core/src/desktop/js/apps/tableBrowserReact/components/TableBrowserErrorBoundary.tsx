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

import React, { Component, ReactNode } from 'react';
import { Result } from 'antd';
import Button from 'cuix/dist/components/Button/Button';
import { i18nReact } from '../../../utils/i18nReact';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onRetry?: () => void;
}

interface State {
  hasError: boolean;
  error?: Error;
}

class TableBrowserErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('TableBrowser Error Boundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      const { t } = i18nReact.useTranslation();
      
      return (
        <Result
          status="error"
          title={t('Something went wrong')}
          subTitle={t('An error occurred while loading the table browser. Please try refreshing the page.')}
          extra={[
            <Button
              key="retry"
              onClick={() => {
                this.setState({ hasError: false, error: undefined });
                this.props.onRetry?.();
              }}
            >
              {t('Try Again')}
            </Button>,
            <Button
              key="refresh"
              onClick={() => window.location.reload()}
            >
              {t('Refresh Page')}
            </Button>
          ]}
        />
      );
    }

    return this.props.children;
  }
}

export default TableBrowserErrorBoundary;

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

import React from 'react';
import BorderlessButton from 'cuix/dist/components/Button/BorderlessButton';
import RefreshIcon from '@cloudera/cuix-core/icons/react/RefreshIcon';
import { i18nReact } from '../../../utils/i18nReact';
import Breadcrumbs from './Breadcrumbs';

export interface PageHeaderProps {
  title?: string;
  icon?: React.ReactElement;
  onRefresh?: () => void;
  loading?: boolean;
  isRefreshing?: boolean;
  // Breadcrumbs props
  sourceType?: string;
  database?: string;
  table?: string;
  column?: string;
  fields?: string[];
  sourceOptions?: string[];
  onSelectSource?: (sourceType: string) => void;
  onClickDataSources?: () => void;
  onClickDatabases?: () => void;
  onClickDatabase?: (database: string) => void;
  onClickTable?: (table: string) => void;
  onClickColumn?: () => void;
  onClickField?: (path: string[]) => void;
}

const PageHeader = ({
  title,
  icon,
  onRefresh,
  loading,
  isRefreshing,
  sourceType,
  database,
  table,
  column,
  fields,
  sourceOptions,
  onSelectSource,
  onClickDataSources,
  onClickDatabases,
  onClickDatabase,
  onClickTable,
  onClickColumn,
  onClickField
}: PageHeaderProps): JSX.Element | null => {
  const { t } = i18nReact.useTranslation();

  // Don't render if no title is provided and no breadcrumbs data
  if (!title && !sourceType && !database && !table && !column) {
    return null;
  }

  return (
    <div className="hue-table-browser__page-header">
      {/* Top row: Title and Refresh Button */}
      <div className="hue-table-browser__page-header__top-row">
        {icon && React.cloneElement(icon, { className: 'hue-table-browser__page-header__icon' })}
        {title && <h3 className="hue-h3 hue-table-browser__page-header__text">{title}</h3>}
        {onRefresh && (
          <BorderlessButton
            onClick={onRefresh}
            title={t('Refresh')}
            icon={<RefreshIcon />}
            disabled={!!loading || !!isRefreshing}
            {...(isRefreshing && { loading: true })}
          >
            {t('Refresh')}
          </BorderlessButton>
        )}
      </div>

      {/* Second row: Breadcrumbs */}
      {(sourceType || database || table || column) && (
        <div className="hue-table-browser__page-header__breadcrumbs-row">
          <Breadcrumbs
            sourceType={sourceType}
            database={database}
            table={table}
            column={column}
            fields={fields}
            sourceOptions={sourceOptions}
            onSelectSource={onSelectSource}
            onClickDataSources={onClickDataSources}
            onClickDatabases={onClickDatabases}
            onClickDatabase={onClickDatabase}
            onClickTable={onClickTable}
            onClickColumn={onClickColumn}
            onClickField={onClickField}
          />
        </div>
      )}
    </div>
  );
};

export default PageHeader;

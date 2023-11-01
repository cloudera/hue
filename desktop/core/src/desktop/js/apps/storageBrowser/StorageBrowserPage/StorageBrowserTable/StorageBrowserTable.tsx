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
import { i18nReact } from '../../../../utils/i18nReact';
import Table from 'cuix/dist/components/Table';
import { ColumnProps } from 'antd/lib/table';

import { StorageBrowserTableData } from '../../../../reactComponents/FileChooser/types';
import './StorageBrowserTable.scss';
import Tooltip from 'antd/es/tooltip';

interface StorageBrowserTableProps {
  className?: string;
  dataSource: StorageBrowserTableData[];
  rowClassName?: string;
  testId?: string;
}

const defaultProps = {
  className: 'hue-storage-browser__table',
  rowClassName: 'hue-storage-browser__table-row',
  testId: 'hue-storage-browser__table'
};

const StorageBrowserTable: React.FC<StorageBrowserTableProps> = ({
  className,
  dataSource,
  rowClassName,
  testId,
  ...restProps
}): JSX.Element => {
  const { t } = i18nReact.useTranslation();

  const getColumns = files => {
    // eslint-disable-next-line prefer-const
    let columns: ColumnProps<unknown>[] = [];
    for (const [key] of Object.entries(files[0])) {
      const temp: ColumnProps<unknown> = {
        dataIndex: `${key}`,
        title: t(`${key}`),
        key: `${key}`,
        width: '20em',
        ellipsis: true,
        //TODO: Apply tooltip only for truncated values
        render: key => <Tooltip title={key}>{key}</Tooltip>
      };
      columns.push(temp);
    }
    return columns;
  };

  if (dataSource) {
    return (
      <>
        <Table
          className={className}
          columns={getColumns(dataSource)}
          dataSource={dataSource}
          rowClassName={rowClassName}
          data-testid={`${testId}`}
          {...restProps}
        ></Table>
      </>
    );
  }
};

StorageBrowserTable.defaultProps = defaultProps;
export default StorageBrowserTable;

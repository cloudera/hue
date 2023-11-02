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

import React, { useEffect, useState } from 'react';
import { i18nReact } from '../../../../utils/i18nReact';
import Table from 'cuix/dist/components/Table';
import { ColumnProps } from 'antd/lib/table';
import FolderIcon from '@cloudera/cuix-core/icons/react/ProjectIcon';
//Todo: Use cuix icon (Currently fileIcon does not exist in cuix)
import { FileOutlined } from '@ant-design/icons';

import { StorageBrowserTableData } from '../../../../reactComponents/FileChooser/types';
import './StorageBrowserTable.scss';
import Tooltip from 'antd/es/tooltip';

interface StorageBrowserTableProps {
  className?: string;
  dataSource: StorageBrowserTableData[];
  onFilepathChange: (path: string) => void;
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
  onFilepathChange,
  rowClassName,
  testId,
  ...restProps
}): JSX.Element => {
  const [tableHeight, setTableHeight] = useState<number>();

  const { t } = i18nReact.useTranslation();

  const getColumns = file => {
    // eslint-disable-next-line prefer-const
    let columns: ColumnProps<unknown>[] = [];
    for (const [key] of Object.entries(file)) {
      const temp: ColumnProps<unknown> = {
        dataIndex: `${key}`,
        title: t(`${key}`),
        key: `${key}`,
        width: '20em'
      };
      if (key === 'name') {
        temp.ellipsis = true;
        //TODO: Apply tooltip only for truncated values
        temp.render = (_, record: any) => (
          <Tooltip title={record.name}>
            {record.type === 'dir' ? <FolderIcon /> : <FileOutlined />}
            <span className="hue-storage-browser__table-name-cell">{record.name}</span>
          </Tooltip>
        );
      }
      columns.push(temp);
    }
    return columns.filter(col => col.dataIndex !== 'type' && col.dataIndex !== 'path');
  };

  const onRowClicked = record => {
    return {
      onClick: e => {
        if (record.type === 'dir') {
          onFilepathChange(record.path);
        }
        //TODO: handle onclick file
      }
    };
  };

  useEffect(() => {
    const calculateTableHeight = () => {
      const windowHeight = window.innerHeight;
      // Todo: move 400 to dynamic based on  table header height, tab nav and some header.
      const tableHeightFix = windowHeight - 400;
      return tableHeightFix;
    };

    const handleWindowResize = () => {
      const tableHeight = calculateTableHeight();
      setTableHeight(tableHeight);
    };

    handleWindowResize(); // Calculate initial scroll height

    window.addEventListener('resize', handleWindowResize);

    return () => {
      window.removeEventListener('resize', handleWindowResize);
    };
  }, []);

  if (dataSource) {
    return (
      <>
        <Table
          className={className}
          columns={getColumns(dataSource[0])}
          dataSource={dataSource}
          onRow={onRowClicked}
          rowClassName={rowClassName}
          rowKey={(record, index) => record.path + '' + index}
          scroll={{ y: tableHeight }}
          data-testid={`${testId}`}
          {...restProps}
        ></Table>
      </>
    );
  }
};

StorageBrowserTable.defaultProps = defaultProps;
export default StorageBrowserTable;

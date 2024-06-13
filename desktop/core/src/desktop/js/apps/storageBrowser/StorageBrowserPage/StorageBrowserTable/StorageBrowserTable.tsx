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
import { ColumnProps } from 'antd/lib/table';
import { Dropdown, Input } from 'antd';
import { MenuItemGroupType } from 'antd/lib/menu/hooks/useItems';
import Tooltip from 'antd/es/tooltip';

import FolderIcon from '@cloudera/cuix-core/icons/react/ProjectIcon';
import SortAscending from '@cloudera/cuix-core/icons/react/SortAscendingIcon';
import SortDescending from '@cloudera/cuix-core/icons/react/SortDescendingIcon';
import DropDownIcon from '@cloudera/cuix-core/icons/react/DropdownIcon';
import ImportIcon from '@cloudera/cuix-core/icons/react/ImportIcon';
//TODO: Use cuix icon (Currently fileIcon does not exist in cuix)
import { FileOutlined } from '@ant-design/icons';

import { PrimaryButton } from 'cuix/dist/components/Button';
import Table from 'cuix/dist/components/Table';

import { i18nReact } from '../../../../utils/i18nReact';
import { mkdir, touch } from '../../../../reactComponents/FileChooser/api';
import {
  PageStats,
  StorageBrowserTableData,
  SortOrder
} from '../../../../reactComponents/FileChooser/types';
import Pagination from '../../../../reactComponents/Pagination/Pagination';
import StorageBrowserActions from '../StorageBrowserActions/StorageBrowserActions';
import InputModal from '../../InputModal/InputModal';

import './StorageBrowserTable.scss';
interface StorageBrowserTableProps {
  className?: string;
  dataSource?: StorageBrowserTableData[];
  filePath: string;
  onFilepathChange: (path: string) => void;
  onPageNumberChange: (pageNumber: number) => void;
  onPageSizeChange: (pageSize: number) => void;
  onSortByColumnChange: (sortByColumn: string) => void;
  onSortOrderChange: (sortOrder: SortOrder) => void;
  pageSize: number;
  pageStats?: PageStats;
  sortByColumn: string;
  sortOrder: SortOrder;
  rowClassName?: string;
  setRefreshKey: (value: number) => void;
  setLoadingFiles: (value: boolean) => void;
  testId?: string;
}

const defaultProps = {
  className: 'hue-storage-browser__table',
  rowClassName: 'hue-storage-browser__table-row',
  testId: 'hue-storage-browser__table'
};

const StorageBrowserTable = ({
  className,
  dataSource,
  filePath,
  onFilepathChange,
  onPageNumberChange,
  onPageSizeChange,
  onSortByColumnChange,
  onSortOrderChange,
  sortByColumn,
  sortOrder,
  pageSize,
  pageStats,
  rowClassName,
  setRefreshKey,
  setLoadingFiles,
  testId,
  ...restProps
}: StorageBrowserTableProps): JSX.Element => {
  const [tableHeight, setTableHeight] = useState<number>();
  const [selectedFiles, setSelectedFiles] = useState<StorageBrowserTableData[]>([]);
  const [showNewFolderModal, setShowNewFolderModal] = useState<boolean>(false);
  const [showNewFileModal, setShowNewFileModal] = useState<boolean>(false);

  const { t } = i18nReact.useTranslation();

  const newActionsMenuItems: MenuItemGroupType[] = [
    {
      key: 'create',
      type: 'group',
      label: t('CREATE'),
      children: [
        {
          icon: <FileOutlined />,
          key: 'new_file',
          label: t('New File'),
          onClick: () => {
            setShowNewFileModal(true);
          }
        },
        {
          icon: <FolderIcon />,
          key: 'new_folder',
          label: t('New Folder'),
          onClick: () => {
            setShowNewFolderModal(true);
          }
        }
      ]
    },
    {
      key: 'upload',
      type: 'group',
      label: t('UPLOAD'),
      children: [
        {
          icon: <ImportIcon />,
          key: 'upload',
          label: t('New Upload')
        }
      ]
    }
  ];

  const onColumnTitleClicked = (columnClicked: string) => {
    if (columnClicked === sortByColumn) {
      if (sortOrder === SortOrder.NONE) {
        onSortOrderChange(SortOrder.ASC);
      } else if (sortOrder === SortOrder.ASC) {
        onSortOrderChange(SortOrder.DSC);
      } else {
        onSortOrderChange(SortOrder.NONE);
      }
    } else {
      onSortByColumnChange(columnClicked);
      onSortOrderChange(SortOrder.ASC);
    }
  };

  const getColumns = (file: StorageBrowserTableData) => {
    const columns: ColumnProps<StorageBrowserTableData>[] = [];
    for (const [key] of Object.entries(file)) {
      const column: ColumnProps<StorageBrowserTableData> = {
        dataIndex: key,
        title: (
          <div
            className="hue-storage-browser__table-column-header"
            onClick={() => onColumnTitleClicked(key)}
          >
            <div className="hue-storage-browser__table-column-title">
              {key === 'mtime' ? t('Last Updated') : t(key)}
            </div>
            {key === sortByColumn ? (
              sortOrder === SortOrder.DSC ? (
                <SortDescending />
              ) : sortOrder === SortOrder.ASC ? (
                <SortAscending />
              ) : null
            ) : null}
          </div>
        ),
        key: `${key}`
      };
      if (key === 'name') {
        column.width = '45%';
        //TODO: Apply tooltip only for truncated values
        column.render = (_, record: StorageBrowserTableData) => (
          <Tooltip title={record.name}>
            <span className="hue-storage-browser__table-cell-icon">
              {record.type === 'dir' ? <FolderIcon /> : <FileOutlined />}
            </span>
            <span className="hue-storage-browser__table-cell-name">{record.name}</span>
          </Tooltip>
        );
      } else if (key === 'mtime') {
        column.width = '15%';
      }
      columns.push(column);
    }
    return columns.filter(col => col.dataIndex !== 'type' && col.dataIndex !== 'path');
  };

  const onRowClicked = (record: StorageBrowserTableData) => {
    return {
      onClick: () => {
        if (record.type === 'dir') {
          onFilepathChange(record.path);
          onPageNumberChange(1);
        }
        //TODO: handle onclick file
      }
    };
  };

  const rowSelection = {
    onChange: (selectedRowKeys: React.Key[], selectedRows: StorageBrowserTableData[]) => {
      setSelectedFiles(selectedRows);
    }
  };

  //pagination related functions handled by parent
  const onPreviousPageButtonClicked = (previousPageNumber: number) => {
    //If previous page does not exists api returns 0
    onPageNumberChange(previousPageNumber === 0 ? 1 : previousPageNumber);
  };

  const onNextPageButtonClicked = (nextPageNumber: number, numPages: number) => {
    //If next page does not exists api returns 0
    onPageNumberChange(nextPageNumber === 0 ? numPages : nextPageNumber);
  };

  const handleCreateNewFolder = (folderName: string) => {
    setLoadingFiles(true);
    mkdir(folderName, filePath)
      .then(() => {
        setRefreshKey(oldKey => oldKey + 1);
      })
      .catch(error => {
        // eslint-disable-next-line no-restricted-syntax
        console.log(error);
      })
      .finally(() => {
        setLoadingFiles(false);
      });
  };

  const handleCreateNewFile = (fileName: string) => {
    setLoadingFiles(true);
    touch(fileName, filePath)
      .then(() => {
        setRefreshKey(oldKey => oldKey + 1);
      })
      .catch(error => {
        // eslint-disable-next-line no-restricted-syntax
        console.log(error);
      })
      .finally(() => {
        setLoadingFiles(false);
      });
  };

  useEffect(() => {
    //TODO: handle table resize
    const calculateTableHeight = () => {
      const windowHeight = window.innerHeight;
      // TODO: move 450 to dynamic based on  table header height, tab nav and some header.
      const tableHeightFix = windowHeight - 450;
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

  //function removes ..(previous folder) and .(current folder) from table data
  const removeDots = (dataSource: StorageBrowserTableData[]) => {
    return dataSource.length > 2 ? dataSource.slice(2) : [];
  };

  const locale = {
    emptyText: t('Folder is empty')
  };

  if (dataSource && pageStats) {
    return (
      <>
        <div className="hue-storage-browser__actions-bar">
          <Input className="hue-storage-browser__search" placeholder={t('Search')} />
          <div className="hue-storage-browser__actions-bar-right">
            <StorageBrowserActions selectedFiles={selectedFiles} />
            <Dropdown
              overlayClassName="hue-storage-browser__actions-dropdown"
              menu={{
                items: newActionsMenuItems,
                className: 'hue-storage-browser__action-menu'
              }}
              trigger={['hover', 'click']}
            >
              <PrimaryButton data-event={''}>
                {t('New')}
                <DropDownIcon />
              </PrimaryButton>
            </Dropdown>
          </div>
        </div>

        <Table
          className={className}
          columns={getColumns(dataSource[0])}
          dataSource={removeDots(dataSource)}
          onRow={onRowClicked}
          pagination={false}
          rowClassName={rowClassName}
          rowKey={(record, index) => record.path + '' + index}
          rowSelection={{
            type: 'checkbox',
            ...rowSelection
          }}
          scroll={{ y: tableHeight }}
          data-testid={`${testId}`}
          locale={locale}
          {...restProps}
        />

        <Pagination
          onNextPageButtonClicked={onNextPageButtonClicked}
          onPageNumberChange={onPageNumberChange}
          onPageSizeChange={onPageSizeChange}
          onPreviousPageButtonClicked={onPreviousPageButtonClicked}
          pageSize={pageSize}
          pageStats={pageStats}
        />

        <InputModal
          title={t('Create New Folder')}
          inputLabel={t('Enter Folder name here')}
          submitText={t('Create')}
          showModal={showNewFolderModal}
          onSubmit={handleCreateNewFolder}
          onClose={() => setShowNewFolderModal(false)}
        />
        <InputModal
          title={t('Create New File')}
          inputLabel={t('Enter File name here')}
          submitText={t('Create')}
          showModal={showNewFileModal}
          onSubmit={handleCreateNewFile}
          onClose={() => setShowNewFileModal(false)}
        />
      </>
    );
  } else {
    return <div />;
  }
};

StorageBrowserTable.defaultProps = defaultProps;
export default StorageBrowserTable;

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
import React, { useCallback, useMemo, useState } from 'react';
import Modal from 'cuix/dist/components/Modal';

import { i18nReact } from '../../../utils/i18nReact';

import './CopyMoveModal.scss';
import useLoadData from '../../../utils/hooks/useLoadData';
import { PathAndFileData } from '../../../reactComponents/FileChooser/types';
import { VIEWFILES_API_URl } from '../../../reactComponents/FileChooser/api';
import PathBrowser from '../../../reactComponents/FileChooser/PathBrowser/PathBrowser';
import Table, { ColumnProps } from 'cuix/dist/components/Table';
import { Input, Spin, Tooltip } from 'antd';
import FolderIcon from '@cloudera/cuix-core/icons/react/ProjectIcon';
import { FileOutlined } from '@ant-design/icons';
import useDebounce from '../../../utils/useDebounce';

interface CopyMoveModalProps {
  // cancelText?: string;
  // inputLabel: string;
  // submitText?: string;
  onClose: () => void;
  onSubmit: (destination_path: string) => void;
  showModal: boolean;
  title: string;
  sourcePath: string;
}

interface TableData {
  name: string;
  path: string;
  type: string;
}

const CopyMoveModal = ({
  showModal,
  onClose,
  onSubmit,
  title,
  sourcePath
}: CopyMoveModalProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const [destPath, setDestPath] = useState<string>(sourcePath);
  const [searchTerm, setSearchTerm] = useState<string>('');

  const {
    data: filesData,
    loading
    // reloadData
  } = useLoadData<PathAndFileData>(destPath, {
    urlPrefix: VIEWFILES_API_URl,
    params: {
      pagesize: '1000',
      filter: searchTerm
    },
    skip: destPath === '' || destPath === undefined
  });

  const tableData: TableData[] = useMemo(() => {
    if (!filesData?.files) {
      return [];
    }

    return filesData?.files?.map(file => ({
      name: file.name,
      path: file.path,
      type: file.type
    }));
  }, [filesData]);

  const handleSearch = useCallback(
    useDebounce(searchTerm => {
      setSearchTerm(encodeURIComponent(searchTerm));
    }),
    [setSearchTerm]
  );

  const getColumns = (file: TableData) => {
    const columns: ColumnProps<TableData>[] = [];
    for (const key of Object.keys(file)) {
      const column: ColumnProps<TableData> = {
        dataIndex: key,
        key: `${key}`
      };
      if (key === 'name') {
        column.render = (_, record: TableData) => (
          <Tooltip title={record.name} mouseEnterDelay={1.5}>
            <span className="hue-copy__table-cell-icon">
              {record.type === 'dir' ? <FolderIcon /> : <FileOutlined />}
            </span>
            <span className="hue-copy__table-cell-name">{record.name}</span>
          </Tooltip>
        );
      }
      columns.push(column);
    }
    return columns.filter(col => col.dataIndex !== 'type' && col.dataIndex !== 'path');
  };

  const onRowClicked = (record: TableData) => {
    return {
      onClick: () => {
        if (record.type === 'dir') {
          setDestPath(record.path);
        }
      }
    };
  };

  return (
    <Modal
      cancelText={t('Cancel')}
      className="hue-copymove-modal cuix antd"
      okText={t('Submit')}
      title={title}
      open={showModal}
      onCancel={() => {
        onClose();
      }}
      onOk={() => {
        onSubmit(destPath);
        onClose();
      }}
    >
      <div className="hue-copy-modal__body">
        <div className="hue-copy__path-browser-panel">
          <span className="hue-copy__destPath">{t('Destination Path:')}</span>
          <PathBrowser
            breadcrumbs={filesData?.breadcrumbs}
            onFilepathChange={setDestPath}
            seperator={'/'}
            showIcon={false}
          />
        </div>
        <Input
          className="hue-storage-browser__search"
          placeholder={t('Search')}
          allowClear={true}
          onChange={event => {
            handleSearch(event.target.value);
          }}
        />
        <Spin spinning={loading}>
          <Table
            className="copyModaltable"
            dataSource={tableData?.slice(2)}
            pagination={false}
            columns={getColumns(tableData[0] ?? {})}
            rowKey={(record, index) => record.path + '' + index}
            scroll={{ y: '250px' }}
            rowClassName="hue-copy__table-row"
            onRow={onRowClicked}
          />
        </Spin>
      </div>
    </Modal>
  );
};

export default CopyMoveModal;

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

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import Modal from 'cuix/dist/components/Modal';
import { Input, Tooltip } from 'antd';
import Table, { ColumnProps } from 'cuix/dist/components/Table';
import classNames from 'classnames';

import FolderIcon from '@cloudera/cuix-core/icons/react/ProjectIcon';
import FileIcon from '@cloudera/cuix-core/icons/react/DocumentationIcon';

import { i18nReact } from '../../../utils/i18nReact';
import useDebounce from '../../../utils/useDebounce';
import useLoadData from '../../../utils/hooks/useLoadData/useLoadData';

import { BrowserViewType, ListDirectory } from '../types';
import { LIST_DIRECTORY_API_URL } from '../api';
import PathBrowser from '../../../reactComponents/PathBrowser/PathBrowser';
import LoadingErrorWrapper from '../../../reactComponents/LoadingErrorWrapper/LoadingErrorWrapper';

import './FileChooserModal.scss';

interface FileChooserModalProps {
  onClose: () => void;
  onSubmit: (destination_path: string) => Promise<void>;
  showModal: boolean;
  title: string;
  sourcePath: string;
  submitText?: string;
  cancelText?: string;
}

interface FileChooserTableData {
  name: string;
  path: string;
  type: string;
}

const FileChooserModal = ({
  showModal,
  onClose,
  onSubmit,
  title,
  sourcePath,
  ...i18n
}: FileChooserModalProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const { cancelText = t('Cancel'), submitText = t('Submit') } = i18n;
  const [destPath, setDestPath] = useState<string>(sourcePath);
  const [submitLoading, setSubmitLoading] = useState<boolean>(false);
  const [searchTerm, setSearchTerm] = useState<string>('');

  useEffect(() => {
    setDestPath(sourcePath);
  }, [sourcePath]);

  const { data: filesData, loading } = useLoadData<ListDirectory>(LIST_DIRECTORY_API_URL, {
    params: {
      path: destPath,
      pagesize: '1000',
      filter: searchTerm
    },
    skip: destPath === '' || destPath === undefined || !showModal
  });

  const tableData: FileChooserTableData[] = useMemo(() => {
    if (!filesData?.files) {
      return [];
    }

    return filesData?.files?.map(file => ({
      name: file.path.split('/').pop() ?? '',
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

  const getColumns = (file: FileChooserTableData) => {
    const columns: ColumnProps<FileChooserTableData>[] = [];
    for (const key of Object.keys(file)) {
      const column: ColumnProps<FileChooserTableData> = {
        dataIndex: key,
        key: `${key}`
      };
      if (key === 'name') {
        column.render = (_, record: FileChooserTableData) => (
          <Tooltip title={record.name} mouseEnterDelay={1.5}>
            <span className="hue-filechooser-modal__table-cell-icon">
              {record.type === BrowserViewType.dir ? <FolderIcon /> : <FileIcon />}
            </span>
            <span className="hue-filechooser-modal__table-cell-name">{record.name}</span>
          </Tooltip>
        );
      }
      columns.push(column);
    }
    return columns.filter(col => col.dataIndex !== 'type' && col.dataIndex !== 'path');
  };

  const onRowClicked = (record: FileChooserTableData) => {
    return {
      onClick: () => {
        if (record.type === BrowserViewType.dir) {
          setDestPath(record.path);
        }
      }
    };
  };

  const locale = {
    emptyText: t('Folder is empty')
  };

  const handleOk = async () => {
    setSubmitLoading(true);
    await onSubmit(destPath);
    setSubmitLoading(false);
    onClose();
  };

  return (
    <Modal
      open={showModal}
      title={title}
      className="hue-filechooser-modal cuix antd"
      okText={submitText}
      onOk={handleOk}
      okButtonProps={{ disabled: sourcePath === destPath, loading: submitLoading }}
      cancelText={cancelText}
      onCancel={onClose}
    >
      <div className="hue-filechooser-modal__body">
        <div className="hue-filechooser-modal__path-browser-panel">
          <PathBrowser filePath={destPath} onFilepathChange={setDestPath} showIcon={false} />
        </div>
        <Input
          className="hue-filechooser-modal__search"
          placeholder={t('Search')}
          allowClear={true}
          onChange={event => {
            handleSearch(event.target.value);
          }}
        />
        <LoadingErrorWrapper loading={loading}>
          <Table
            className="hue-filechooser-modal__table"
            data-testid="hue-filechooser-modal__table"
            dataSource={tableData}
            pagination={false}
            columns={getColumns(tableData[0] ?? {})}
            rowKey={r => `${r.path}__${r.type}__${r.name}`}
            scroll={{ y: '250px' }}
            rowClassName={record =>
              record.type === BrowserViewType.file
                ? classNames('hue-filechooser-modal__table-row', 'disabled-row')
                : 'hue-filechooser-modal__table-row'
            }
            onRow={onRowClicked}
            locale={locale}
            showHeader={false}
          />
        </LoadingErrorWrapper>
      </div>
    </Modal>
  );
};

export default FileChooserModal;

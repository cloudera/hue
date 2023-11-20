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
import { Button, Dropdown } from 'antd';
import type { MenuProps } from 'antd';
import { i18nReact } from '../../../../../utils/i18nReact';

import PageFirstIcon from '@cloudera/cuix-core/icons/react/PageFirstIcon';
import PagePreviousIcon from '@cloudera/cuix-core/icons/react/PagePreviousIcon';
import PageNextIcon from '@cloudera/cuix-core/icons/react/PageNextIcon';
import PageLastIcon from '@cloudera/cuix-core/icons/react/PageLastIcon';
import DropdownIcon from '@cloudera/cuix-core/icons/react/DropdownIcon';

import { PageStats } from '../../../../../reactComponents/FileChooser/types';
import './StorageBrowserPagination.scss';

interface StorageBrowserPaginationProps {
  onPageNumberChange: (pageNumber: number) => void;
  onPageSizeChange: (pageSize: number) => void;
  pageSize: number;
  pageSizeOptions?: number[];
  pageStats: PageStats;
}

const defaultProps = {
  currentPage: 1,
  pageSizeOptions: [15, 30, 45, 60, 100, 200, 1000]
};

const StorageBrowserPagination: React.FC<StorageBrowserPaginationProps> = ({
  onPageNumberChange,
  onPageSizeChange,
  pageSize,
  pageSizeOptions,
  pageStats
}): JSX.Element => {
  const { t } = i18nReact.useTranslation();

  const currentPageSize = pageSize;

  const pageSizeOptionsMenu: MenuProps['items'] = pageSizeOptions.map(option => {
    return {
      key: option,
      label: (
        <Button
          onClick={() => {
            onPageSizeChange(option);
            onPageNumberChange(1);
          }}
          className="hue-pagination__page-size-menu-item-btn"
        >
          {option}
        </Button>
      )
    };
  });

  return (
    <div className="hue-storage-browser__pagination">
      <div className="hue-pagination__page-size-control">
        {t('Rows per page: ')}
        <Dropdown menu={{ items: pageSizeOptionsMenu }}>
          <Button className="hue-pagination__page-size-menu-btn">
            <div>
              <span>{currentPageSize}</span>
              <DropdownIcon />
            </div>
          </Button>
        </Dropdown>
      </div>
      <div className="hue-pagination__rows-stats-display">
        {pageStats.start_index} - {pageStats.end_index} of {pageStats.total_count}
      </div>
      <div className="hue-pagination__control-buttons-panel">
        <Button onClick={() => onPageNumberChange(1)} className="hue-pagination__control-button">
          <PageFirstIcon />
        </Button>
        <Button
          onClick={() =>
            onPageNumberChange(
              //If previous page does not exists api returns 0
              pageStats.previous_page_number === 0 ? 1 : pageStats.previous_page_number
            )
          }
          className="hue-pagination__control-button"
        >
          <PagePreviousIcon />
        </Button>
        <Button
          onClick={() =>
            onPageNumberChange(
              //If next page does not exists api returns 0
              pageStats.next_page_number === 0 ? pageStats.num_pages : pageStats.next_page_number
            )
          }
          className="hue-pagination__control-button"
        >
          <PageNextIcon />
        </Button>
        <Button
          onClick={() => onPageNumberChange(pageStats.num_pages)}
          className="hue-pagination__control-button"
        >
          <PageLastIcon />
        </Button>
      </div>
    </div>
  );
};

StorageBrowserPagination.defaultProps = defaultProps;
export default StorageBrowserPagination;

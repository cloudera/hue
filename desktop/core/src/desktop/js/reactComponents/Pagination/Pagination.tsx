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
import { Dropdown } from 'antd';
import type { MenuProps } from 'antd';
import { i18nReact } from '../../utils/i18nReact';
import { BorderlessButton } from 'cuix/dist/components/Button';
import PageFirstIcon from '@cloudera/cuix-core/icons/react/PageFirstIcon';
import PagePreviousIcon from '@cloudera/cuix-core/icons/react/PagePreviousIcon';
import PageNextIcon from '@cloudera/cuix-core/icons/react/PageNextIcon';
import PageLastIcon from '@cloudera/cuix-core/icons/react/PageLastIcon';
import DropdownIcon from '@cloudera/cuix-core/icons/react/DropdownIcon';

import './Pagination.scss';

export interface PageStats {
  pageNumber: number;
  totalPages: number;
  pageSize: number;
  totalSize: number;
}

export interface PaginationProps {
  setPageNumber: (pageNumber: number) => void;
  setPageSize?: (pageSize: number) => void;
  pageSize?: number;
  pageSizeOptions?: number[];
  pageStats: PageStats;
  showIndexes?: boolean;
}

const Pagination = ({
  setPageNumber,
  setPageSize,
  pageSizeOptions = [10, 50, 500, 1000],
  pageStats,
  showIndexes = false
}: PaginationProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();

  const startIndex = pageStats.pageSize * (pageStats.pageNumber - 1) + 1;
  const endIndex = Math.min(pageStats.pageSize * pageStats.pageNumber, pageStats.totalSize);

  const pageSizeOptionsMenu: MenuProps['items'] = pageSizeOptions.map(option => {
    return {
      key: option,
      label: (
        <BorderlessButton
          onClick={() => {
            setPageSize?.(option);
            setPageNumber(1);
          }}
          className="hue-pagination__page-size-menu-item-btn"
        >
          {option}
        </BorderlessButton>
      )
    };
  });

  return (
    <div className="hue-pagination">
      {pageStats.pageSize > 0 && (
        <div className="hue-pagination__page-size-control">
          {t('Rows per page: ')}
          <Dropdown menu={{ items: pageSizeOptionsMenu }}>
            <BorderlessButton
              className="hue-pagination__page-size-menu-btn"
              icon={<DropdownIcon />}
              iconPosition="right"
            >
              {pageStats.pageSize}
            </BorderlessButton>
          </Dropdown>
        </div>
      )}
      <div className="hue-pagination__rows-stats-display">
        {showIndexes
          ? `${startIndex} - ${endIndex} of ${pageStats.totalSize}`
          : `${pageStats.pageNumber} of ${pageStats.totalPages}`}
      </div>
      <div className="hue-pagination__control-buttons-panel">
        <BorderlessButton
          onClick={() => setPageNumber(1)}
          className="hue-pagination__control-button"
          disabled={pageStats.pageNumber === 1}
          title={t('First Page')}
          icon={<PageFirstIcon />}
        />
        <BorderlessButton
          onClick={() => setPageNumber(pageStats.pageNumber - 1)}
          className="hue-pagination__control-button"
          disabled={pageStats.pageNumber === 1}
          title={t('First Page')}
          icon={<PagePreviousIcon />}
        />
        <BorderlessButton
          onClick={() => setPageNumber(pageStats.pageNumber + 1)}
          className="hue-pagination__control-button"
          disabled={pageStats.pageNumber === pageStats.totalPages}
          title={t('Next Page')}
          icon={<PageNextIcon />}
        />
        <BorderlessButton
          onClick={() => setPageNumber(pageStats.totalPages)}
          className="hue-pagination__control-button"
          disabled={pageStats.pageNumber === pageStats.totalPages}
          title={t('Last Page')}
          icon={<PageLastIcon />}
        />
      </div>
    </div>
  );
};

export default Pagination;

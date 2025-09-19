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

import { useState, useMemo } from 'react';
import type { SortOrder } from 'antd/lib/table/interface';
import type { Connector } from '../../../config/types';

export interface SourcesListState {
  // Loading state
  isInitializing: boolean;

  sourceFilter: string;
  setSourceFilter: (value: string) => void;
  sourcePageSize: number;
  setSourcePageSize: (size: number) => void;
  sourcePageNumber: number;
  setSourcePageNumber: (page: number) => void;

  sortByColumn: string | undefined;
  setSortByColumn: (col?: string) => void;
  sortOrder: SortOrder;
  setSortOrder: (order: SortOrder) => void;
}

export function useSourcesListState(options: { connectors?: Connector[] }): SourcesListState {
  const { connectors } = options;

  const [sourceFilter, setSourceFilter] = useState('');
  const [sourcePageSize, setSourcePageSize] = useState(50);
  const [sourcePageNumber, setSourcePageNumber] = useState(1);

  const [sortByColumn, setSortByColumn] = useState<string | undefined>(undefined);
  const [sortOrder, setSortOrder] = useState<SortOrder>(null);

  // Determine if we're still initializing based on connectors availability
  const isInitializing = useMemo(() => {
    // If connectors is undefined or empty, we're still loading
    return !connectors || connectors.length === 0;
  }, [connectors]);

  return {
    isInitializing,
    sourceFilter,
    setSourceFilter,
    sourcePageSize,
    setSourcePageSize,
    sourcePageNumber,
    setSourcePageNumber,
    sortByColumn,
    setSortByColumn,
    sortOrder,
    setSortOrder
  };
}

export default useSourcesListState;

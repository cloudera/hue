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
import { useDescriptionManager } from '../hooks/useDescriptionManager';
import type { Connector, Namespace, Compute } from '../../../config/types';

export interface ListCellEditState {
  values: Record<string, string>;
  editingId: string | null;
  editingValue: string;
  setEditingId: (id: string | null) => void;
  setEditingValue: (v: string) => void;
  save: (id: string, value: string) => void;
}

export interface TablesListState {
  // Loading state
  isInitializing: boolean;

  // Page-level (filter/pagination)
  tableFilter: string;
  setTableFilter: (value: string) => void;
  tablePageSize: number;
  setTablePageSize: (size: number) => void;
  tablePageNumber: number;
  setTablePageNumber: (page: number) => void;

  // List UI state
  selected: string[];
  setSelected: (names: string[]) => void;
  confirmOpen: boolean;
  setConfirmOpen: (open: boolean) => void;
  skipTrash: boolean;
  setSkipTrash: (skip: boolean) => void;
  sortByColumn: string | undefined;
  setSortByColumn: (col?: string) => void;
  sortOrder: SortOrder;
  setSortOrder: (order: SortOrder) => void;
  selectedTypes: string[];
  setSelectedTypes: (types: string[]) => void;

  // Description editing
  editState: ListCellEditState;
}

export function useTablesListState(options: {
  connector?: Connector;
  namespace?: Namespace;
  compute?: Compute;
  database?: string;
  tables?: string[];
  /** When true, bypass cache and force fresh API calls for descriptions */
  refreshCache?: boolean;
}): TablesListState {
  const { connector, namespace, compute, database, tables, refreshCache = false } = options;

  // Page-level (filter/pagination)
  const [tableFilter, setTableFilter] = useState('');
  const [tablePageSize, setTablePageSize] = useState(50);
  const [tablePageNumber, setTablePageNumber] = useState(1);

  const [selected, setSelected] = useState<string[]>([]);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [skipTrash, setSkipTrash] = useState(false);
  const [sortByColumn, setSortByColumn] = useState<string | undefined>(undefined);
  const [sortOrder, setSortOrder] = useState<SortOrder>(null);
  const [selectedTypes, setSelectedTypes] = useState<string[]>([]);

  // Description editing using the shared hook
  const {
    descriptions,
    editingItem,
    editingValue,
    setEditingItem,
    setEditingValue,
    saveDescription
  } = useDescriptionManager({
    connector,
    namespace,
    compute,
    items: tables || [],
    path: database ? [database] : [],
    currentItem: undefined, // Tables don't have a single "current" item
    refreshCache
  });

  const editState: ListCellEditState = {
    values: descriptions,
    editingId: editingItem,
    editingValue,
    setEditingId: setEditingItem,
    setEditingValue,
    save: saveDescription
  };

  // Determine if we're still initializing based on dependencies
  const isInitializing = useMemo(() => {
    // If we don't have connector/namespace/compute/database yet, we're initializing
    if (!connector || !namespace || !compute || !database) {
      return true;
    }
    // If tables is undefined (not loaded yet), we're still loading
    // Note: Empty array (tables.length === 0) is a valid state for empty databases
    if (tables === undefined) {
      return true;
    }
    return false;
  }, [connector, namespace, compute, database, tables]);

  return {
    isInitializing,
    tableFilter,
    setTableFilter,
    tablePageSize,
    setTablePageSize,
    tablePageNumber,
    setTablePageNumber,
    selected,
    setSelected,
    confirmOpen,
    setConfirmOpen,
    skipTrash,
    setSkipTrash,
    sortByColumn,
    setSortByColumn,
    sortOrder,
    setSortOrder,
    selectedTypes,
    setSelectedTypes,
    editState
  };
}

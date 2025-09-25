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

import { useState, useMemo, useEffect, useRef } from 'react';
import type { SortOrder } from 'antd/lib/table/interface';
import { useDescriptionManager } from '../hooks/useDescriptionManager';
import type { Connector, Namespace, Compute } from '../../../config/types';

export interface CreateDatabaseFormState {
  name: string;
  comment: string;
  location: string;
  useDefaultLocation: boolean;
}

export interface ListCellEditState {
  values: Record<string, string>;
  editingId: string | null;
  editingValue: string;
  setEditingId: (id: string | null) => void;
  setEditingValue: (v: string) => void;
  save: (id: string, value: string) => void;
}

export interface DatabasesListState {
  // Loading state
  isInitializing: boolean;

  // Page-level (filter/pagination)
  dbFilter: string;
  setDbFilter: (value: string) => void;
  dbPageSize: number;
  setDbPageSize: (size: number) => void;
  dbPageNumber: number;
  setDbPageNumber: (page: number) => void;

  // List UI-level
  selected: string[];
  setSelected: (names: string[]) => void;
  confirmOpen: boolean;
  setConfirmOpen: (open: boolean) => void;
  createModalOpen: boolean;
  setCreateModalOpen: (open: boolean) => void;
  sortByColumn: string | undefined;
  setSortByColumn: (col?: string) => void;
  sortOrder: SortOrder;
  setSortOrder: (order: SortOrder) => void;
  createForm: CreateDatabaseFormState;
  setCreateForm: (form: CreateDatabaseFormState) => void;

  // Description editing
  editState: ListCellEditState;
}

export function useDatabasesListState(options: {
  connector?: Connector;
  namespace?: Namespace;
  compute?: Compute;
  databases?: string[];
  currentDatabase?: string;
  /** When true, bypass cache and force fresh API calls for descriptions */
  refreshCache?: boolean;
}): DatabasesListState {
  const {
    connector,
    namespace,
    compute,
    databases,
    currentDatabase,
    refreshCache = false
  } = options;

  // Page-level
  const [dbFilter, setDbFilter] = useState('');
  const [dbPageSize, setDbPageSize] = useState(10);
  const [dbPageNumber, setDbPageNumber] = useState(1);

  const [selected, setSelected] = useState<string[]>([]);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [sortByColumn, setSortByColumn] = useState<string | undefined>(undefined);
  const [sortOrder, setSortOrder] = useState<SortOrder>(null);
  const [createForm, setCreateForm] = useState<CreateDatabaseFormState>({
    name: '',
    comment: '',
    location: '',
    useDefaultLocation: true
  });

  // Description editing using the shared hook
  // Prevent stale data: track connector changes and clear databases immediately when connector changes
  const connectorKey = useMemo(() => {
    return connector?.id || connector?.type || 'no-connector';
  }, [connector?.id, connector?.type]);

  const lastConnectorKeyRef = useRef(connectorKey);
  const safeDatabases = useMemo(() => {
    // If connector has changed, immediately return empty array to prevent stale data
    if (connectorKey !== lastConnectorKeyRef.current) {
      lastConnectorKeyRef.current = connectorKey;
      return [];
    }

    if (!connector || !namespace || !compute) {
      return [];
    }
    return databases || [];
  }, [connector, namespace, compute, databases, connectorKey]);

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
    items: safeDatabases,
    path: [],
    currentItem: currentDatabase,
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
    // If we don't have connector/namespace/compute yet, we're initializing
    if (!connector || !namespace || !compute) {
      return true;
    }
    // If databases is undefined or empty (and we expect databases), we're still loading
    if (!databases || databases.length === 0) {
      return true;
    }
    return false;
  }, [connector, namespace, compute, databases]);

  // Clear all state when connector changes to prevent stale data when switching sources
  useEffect(() => {
    // Reset pagination
    setDbPageNumber(1);
    setDbPageSize(10);

    // Reset filters and selections
    setDbFilter('');
    setSelected([]);

    // Reset sort
    setSortByColumn('');
    setSortOrder(null);

    // Reset modals and forms
    setConfirmOpen(false);
    setCreateModalOpen(false);
    setCreateForm({
      name: '',
      comment: '',
      location: '',
      useDefaultLocation: true
    });
  }, [connector?.id]);

  return {
    isInitializing,
    dbFilter,
    setDbFilter,
    dbPageSize,
    setDbPageSize,
    dbPageNumber,
    setDbPageNumber,
    selected,
    setSelected,
    confirmOpen,
    setConfirmOpen,
    createModalOpen,
    setCreateModalOpen,
    sortByColumn,
    setSortByColumn,
    sortOrder,
    setSortOrder,
    createForm,
    setCreateForm,
    editState
  };
}

export default useDatabasesListState;

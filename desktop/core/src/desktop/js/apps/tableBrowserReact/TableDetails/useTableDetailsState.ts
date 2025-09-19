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

import { useState } from 'react';

import type { Connector, Namespace, Compute } from '../../../config/types';
import { useTableDetails } from '../hooks/useTableDetails';
import type { TableDetailsState as TableDetailsData } from '../hooks/useTableDetails';
import type { TabKey } from '../sharedComponents/Tabs';

export interface UseTableDetailsStateArgs {
  database: string;
  table: string;
  connector: Connector | null;
  namespace: Namespace | null;
  compute: Compute | null;
  activeTab: TabKey;
  onTabChange: (tab: TabKey) => void;
}

export interface TableDetailsState {
  // Tab state
  activeTab: TabKey;
  setActiveTab: (tab: TabKey) => void;

  // Table data
  tableDetails: TableDetailsData;

  // UI state
  isDropping: boolean;
  setIsDropping: (value: boolean) => void;
  confirmOpen: boolean;
  setConfirmOpen: (open: boolean) => void;
  skipTrash: boolean;
  setSkipTrash: (value: boolean) => void;
  importModalOpen: boolean;
  setImportModalOpen: (open: boolean) => void;
}

export function useTableDetailsState(args: UseTableDetailsStateArgs): TableDetailsState {
  const { database, table, connector, namespace, compute, activeTab, onTabChange } = args;

  const [isDropping, setIsDropping] = useState<boolean>(false);
  const [confirmOpen, setConfirmOpen] = useState<boolean>(false);
  const [skipTrash, setSkipTrash] = useState<boolean>(false);
  const [importModalOpen, setImportModalOpen] = useState<boolean>(false);

  // Table details data fetching
  const tableDetails = useTableDetails({
    connector,
    namespace,
    compute,
    database,
    table
  });

  return {
    activeTab,
    setActiveTab: onTabChange,
    tableDetails,
    isDropping,
    setIsDropping,
    confirmOpen,
    setConfirmOpen,
    skipTrash,
    setSkipTrash,
    importModalOpen,
    setImportModalOpen
  };
}

export default useTableDetailsState;

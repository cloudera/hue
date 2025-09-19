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

export interface UseTablesPageState {
  tableFilter: string;
  setTableFilter: (value: string) => void;
  tablePageSize: number;
  setTablePageSize: (size: number) => void;
  tablePageNumber: number;
  setTablePageNumber: (page: number) => void;
}

export function useTablesPageState(): UseTablesPageState {
  const [tableFilter, setTableFilter] = useState('');
  const [tablePageSize, setTablePageSize] = useState(50);
  const [tablePageNumber, setTablePageNumber] = useState(1);

  return {
    tableFilter,
    setTableFilter,
    tablePageSize,
    setTablePageSize,
    tablePageNumber,
    setTablePageNumber
  };
}

export default useTablesPageState;



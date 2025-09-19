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

import { useCallback, useEffect, useMemo, useState } from 'react';

export type PartitionColumn = { name: string; value: string };

export interface UseImportDataFormArgs {
  open: boolean;
  partitionColumns: PartitionColumn[];
}

export interface UseImportDataForm {
  filePath: string;
  setFilePath: (path: string) => void;
  overwrite: boolean;
  setOverwrite: (next: boolean) => void;
  partitionValues: Record<string, string>;
  setPartitionValue: (name: string, value: string) => void;
  initialPartitionValues: Record<string, string>;
  resetForm: () => void;
}

export function useImportDataForm({ open, partitionColumns }: UseImportDataFormArgs): UseImportDataForm {
  const initialPartitionValues = useMemo(() => {
    const init: Record<string, string> = {};
    (partitionColumns || []).forEach(col => {
      init[col.name] = col.value || '';
    });
    return init;
  }, [partitionColumns]);

  const [filePath, setFilePath] = useState<string>('');
  const [overwrite, setOverwrite] = useState<boolean>(false);
  const [partitionValues, setPartitionValues] = useState<Record<string, string>>(initialPartitionValues);

  // Initialize/refresh partition values when dialog opens or when columns change while open
  useEffect(() => {
    if (open) {
      setPartitionValues(initialPartitionValues);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, initialPartitionValues]);

  // Reset form on close
  useEffect(() => {
    if (!open) {
      setFilePath('');
      setOverwrite(false);
      setPartitionValues({});
    }
  }, [open]);

  const setPartitionValue = useCallback((name: string, value: string) => {
    setPartitionValues(prev => ({ ...prev, [name]: value }));
  }, []);

  const resetForm = useCallback(() => {
    setFilePath('');
    setOverwrite(false);
    setPartitionValues(initialPartitionValues);
  }, [initialPartitionValues]);

  return {
    filePath,
    setFilePath,
    overwrite,
    setOverwrite,
    partitionValues,
    setPartitionValue,
    initialPartitionValues,
    resetForm
  };
}



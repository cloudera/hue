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

import { useCallback, useEffect, useState, useRef, useMemo } from 'react';
import { i18nReact } from '../../../utils/i18nReact';
import dataCatalog from '../../../catalog/dataCatalog';
import { notifyError, notifyInfo } from '../utils/notifier';
import type { Connector, Namespace, Compute } from '../../../config/types';

export interface UseDescriptionManagerArgs {
  connector?: Connector | null;
  namespace?: Namespace | null;
  compute?: Compute | null;
  items?: string[];
  path?: string[];
  currentItem?: string;
}

export interface DescriptionManagerState {
  descriptions: Record<string, string>;
  editingItem: string | null;
  editingValue: string;
  setEditingItem: (name: string | null) => void;
  setEditingValue: (value: string) => void;
  saveDescription: (name: string, value: string) => Promise<void>;
}

export function useDescriptionManager({
  connector,
  namespace,
  compute,
  items,
  path = [],
  currentItem
}: UseDescriptionManagerArgs): DescriptionManagerState {
  const { t } = i18nReact.useTranslation();
  const [descriptions, setDescriptions] = useState<Record<string, string>>({});
  const [editingItem, setEditingItem] = useState<string | null>(null);
  const [editingValue, setEditingValue] = useState('');
  const fetchedItemsRef = useRef<Set<string>>(new Set());

  // Stabilize path and items arrays to prevent unnecessary re-renders
  const stablePath = useMemo(() => path, [JSON.stringify(path)]);
  const stableItems = useMemo(() => items, [JSON.stringify(items)]);
  const pathKey = useMemo(() => stablePath.join('/'), [stablePath]);

  // Reset fetched items when path changes (different context)
  useEffect(() => {
    fetchedItemsRef.current.clear();
  }, [pathKey]);

  // Prefetch descriptions (Navigator or source metadata) when listing items
  useEffect(() => {
    const loadDescriptions = async () => {
      if (!connector || !namespace || !compute || !stableItems || currentItem) {
        return;
      }
      try {
        const sourceEntry = await dataCatalog.getEntry({
          connector,
          namespace,
          compute,
          path: stablePath
        });
        await sourceEntry.getChildren({ silenceErrors: true });
        const children = await sourceEntry.loadNavigatorMetaForChildren({ silenceErrors: true });
        const map: Record<string, string> = {};
        children.forEach(child => {
          const childPath = (child as unknown as { path: string[] }).path;
          if (childPath?.length === stablePath.length + 1) {
            map[child.name] = child.getResolvedComment();
          }
        });
        setDescriptions(map);
      } catch {
        // Silently fail for description loading
      }
    };
    loadDescriptions();
  }, [connector, namespace, compute, stableItems, currentItem, stablePath]);

  // Fallback: ensure comments via describe for visible page items
  useEffect(() => {
    if (!stableItems || currentItem || !connector || !namespace || !compute) {
      return;
    }

    const fetchDescriptionsForItems = async () => {
      // Use functional update to get current descriptions without adding to deps
      setDescriptions(currentDescriptions => {
        const itemsToFetch = stableItems.filter(name => {
          const itemKey = `${pathKey}/${name}`;
          return (
            !fetchedItemsRef.current.has(itemKey) &&
            typeof currentDescriptions[name] === 'undefined'
          );
        });

        if (itemsToFetch.length === 0) {
          return currentDescriptions; // No changes needed
        }

        // Mark items as being fetched to prevent duplicate requests
        itemsToFetch.forEach(name => {
          const itemKey = `${pathKey}/${name}`;
          fetchedItemsRef.current.add(itemKey);
        });

        // Fetch descriptions for all items that need them (async operation outside setState)
        (async () => {
          const fetchPromises = itemsToFetch.map(async name => {
            try {
              const entry = await dataCatalog.getEntry({
                connector,
                namespace,
                compute,
                path: [...stablePath, name]
              });
              const describe: unknown = await entry.getAnalysis({ silenceErrors: true });
              const comment = (describe as unknown as { comment?: string }).comment || '';
              return { name, comment };
            } catch {
              return { name, comment: '' };
            }
          });

          const results = await Promise.all(fetchPromises);

          // Batch update all descriptions at once
          const newDescriptions: Record<string, string> = {};
          results.forEach(({ name, comment }) => {
            if (typeof comment !== 'undefined') {
              newDescriptions[name] = comment;
            }
          });

          if (Object.keys(newDescriptions).length > 0) {
            setDescriptions(prev => ({ ...prev, ...newDescriptions }));
          }
        })();

        return currentDescriptions; // Return current state unchanged
      });
    };

    fetchDescriptionsForItems();
  }, [stableItems, connector, namespace, compute, currentItem, pathKey, stablePath]);

  const saveDescription = useCallback(
    async (name: string, value: string) => {
      setEditingItem(null);
      // Optimistic update
      setDescriptions(prev => ({ ...prev, [name]: value }));
      try {
        const entry = await dataCatalog.getEntry({
          connector,
          namespace,
          compute,
          path: [...stablePath, name]
        });
        await entry.setComment(value, { silenceErrors: true });
        notifyInfo(t('Description saved'));
      } catch {
        // Revert on error
        setDescriptions(prev => ({ ...prev, [name]: prev[name] }));
        notifyError(t('Failed to save description'));
      }
    },
    [connector, namespace, compute, stablePath, t]
  );

  return {
    descriptions,
    editingItem,
    editingValue,
    setEditingItem,
    setEditingValue,
    saveDescription
  };
}

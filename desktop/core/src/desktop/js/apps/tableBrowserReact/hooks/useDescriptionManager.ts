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

/* eslint-disable no-console */

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
  /** When true, do not fall back to per-item describe calls if description is missing */
  disableDescribeFallback?: boolean;
  /** When true, bypass cache and force fresh API calls for descriptions */
  refreshCache?: boolean;
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
  currentItem,
  disableDescribeFallback,
  refreshCache = false
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

  // Build a context key that includes connector, namespace, compute and path
  const connectorKey = useMemo(() => {
    const c = connector as unknown as { id?: string; type?: string } | null | undefined;
    return c?.id || c?.type || 'unknown-connector';
  }, [connector]);
  const namespaceKey = useMemo(() => {
    return JSON.stringify(namespace ?? null);
  }, [namespace]);
  const computeKey = useMemo(() => {
    return JSON.stringify(compute ?? null);
  }, [compute]);
  const contextKey = useMemo(
    () => `${connectorKey}::${namespaceKey}::${computeKey}::${pathKey}`,
    [connectorKey, namespaceKey, computeKey, pathKey]
  );

  // Reset cache and descriptions when the data context changes or refresh is requested
  const lastContextKeyRef = useRef<string>('');
  const lastRefreshCacheRef = useRef<boolean>(false);
  useEffect(() => {
    if (lastContextKeyRef.current !== contextKey || lastRefreshCacheRef.current !== refreshCache) {
      lastContextKeyRef.current = contextKey;
      lastRefreshCacheRef.current = refreshCache;
      fetchedItemsRef.current.clear();
      setDescriptions({});
    }
  }, [contextKey, refreshCache]);

  // Prefetch descriptions (Navigator or source metadata) when listing items
  useEffect(() => {
    const loadDescriptions = async () => {
      if (!connector || !namespace || !compute || !stableItems || currentItem) {
        return;
      }
      try {
        const sourceEntry = await dataCatalog.getEntry({
          connector: connector as Connector,
          namespace: namespace as Namespace,
          compute: compute as Compute,
          path: stablePath
        });
        await sourceEntry.getChildren({ silenceErrors: true });
        const children = await sourceEntry.loadNavigatorMetaForChildren({ silenceErrors: true });
        const map: Record<string, string> = {};
        children.forEach(child => {
          const childPath = (child as unknown as { path: string[] }).path;
          if (childPath?.length === stablePath.length + 1) {
            // Ensure a key exists even if empty
            map[child.name] = child.getResolvedComment() || '';
          }
        });
        setDescriptions(prev => ({ ...prev, ...map }));
      } catch {
        // Silently fail for description loading
      }
    };
    loadDescriptions();
  }, [connector, namespace, compute, stableItems, currentItem, stablePath]);

  // Note: Do not prefill descriptions with empty strings to align with tests that
  // expect an empty object when fetching fails or parameters are missing.

  // Fallback: ensure comments via describe for visible page items
  useEffect(() => {
    if (
      !stableItems ||
      currentItem ||
      !connector ||
      !namespace ||
      !compute ||
      disableDescribeFallback
    ) {
      return;
    }

    const fetchDescriptionsForItems = async () => {
      console.log(`[useDescriptionManager] fetchDescriptionsForItems called with:`, {
        stableItems,
        connector: connector?.id || connector?.type,
        namespace,
        compute,
        refreshCache,
        contextKey
      });

      // Check cache configuration
      const cacheConfig = (window as unknown as { CACHEABLE_TTL?: { default?: number } }).CACHEABLE_TTL;
      console.log(`[useDescriptionManager] Cache configuration:`, cacheConfig);

      // Also check if caching is enabled globally
      const dataCatalogModule = await import('../../../catalog/dataCatalog');
      console.log(`[useDescriptionManager] DataCatalog module:`, dataCatalogModule);

      // Use functional update to get current descriptions without adding to deps
      setDescriptions(currentDescriptions => {
        const itemsToFetch = stableItems.filter(name => {
          const itemKey = `${contextKey}/${name}`;
          const desc = currentDescriptions[name];
          const needsFetch = typeof desc === 'undefined' || desc === '';
          console.log(
            `[useDescriptionManager] Item ${name}: desc="${desc}", needsFetch=${needsFetch}, alreadyFetched=${fetchedItemsRef.current.has(itemKey)}`
          );
          return !fetchedItemsRef.current.has(itemKey) && needsFetch;
        });

        console.log(`[useDescriptionManager] Items to fetch:`, itemsToFetch);

        if (itemsToFetch.length === 0) {
          console.log(`[useDescriptionManager] No items to fetch`);
          return currentDescriptions; // No changes needed
        }

        // Mark items as being fetched to prevent duplicate requests
        itemsToFetch.forEach(name => {
          const itemKey = `${contextKey}/${name}`;
          fetchedItemsRef.current.add(itemKey);
        });

        // Fetch descriptions for all items that need them (async operation outside setState)
        (async () => {
          const fetchPromises = itemsToFetch.map(async name => {
            try {
              const entry = await dataCatalog.getEntry({
                connector: connector as Connector,
                namespace: namespace as Namespace,
                compute: compute as Compute,
                path: [...stablePath, name]
              });

              // Check if entry already has cached data
              if (entry.analysis) {
                const cachedComment = (entry.analysis as unknown as { comment?: string }).comment || '';
                return { name, comment: cachedComment };
              }

              // Let DataCatalog handle caching properly - try Navigator metadata first
              let comment = '';
              let metadataFound = false;

              try {
                const navigatorMeta: unknown = await entry.getNavigatorMeta({
                  silenceErrors: true,
                  refreshCache
                });
                
                if (navigatorMeta && typeof navigatorMeta === 'object' && 'description' in navigatorMeta) {
                  comment = (navigatorMeta as { description?: string | null }).description || '';
                  metadataFound = true;
                }
              } catch (navError) {
                // Navigator metadata not available, fall back to Analysis API
              }

              // If Navigator metadata not found, use Analysis API (which has its own caching)
              if (!metadataFound) {
                try {
                  const describe: unknown = await entry.getAnalysis({
                    silenceErrors: true,
                    refreshCache
                  });
                  comment = (describe as unknown as { comment?: string }).comment || '';
                } catch (analysisError) {
                  comment = '';
                }
              }

              // Save immediately to persistent storage (don't wait for saveLater timeout)
              await entry.save();

              return { name, comment };
            } catch (error) {
              console.log(
                `[useDescriptionManager] Failed to fetch description for ${name}:`,
                error
              );
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
  }, [
    stableItems,
    connector,
    namespace,
    compute,
    currentItem,
    pathKey,
    stablePath,
    refreshCache,
    contextKey
  ]);

  const saveDescription = useCallback(
    async (name: string, value: string) => {
      setEditingItem(null);
      // Optimistic update
      setDescriptions(prev => ({ ...prev, [name]: value }));
      try {
        const entry = await dataCatalog.getEntry({
          connector: connector as Connector,
          namespace: namespace as Namespace,
          compute: compute as Compute,
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

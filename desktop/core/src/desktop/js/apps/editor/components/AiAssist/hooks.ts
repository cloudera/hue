import { useMemo, useState, useEffect, useRef } from 'react';
import { throttle } from 'lodash';
import huePubSub from 'utils/huePubSub';

import { getFromLocalStorage, setInLocalStorage } from 'utils/storageUtils';

// Determines the most common case (upper/lower) of the keywords in the
// statement currently selected by the editor
export const useKeywordCase = (parser: any, selectedStatement: string) => {
  const [autoFormatCount, setAutoFormatCount] = useState(0);
  useEffect(() => {
    // Subscribe to autoformatting events from the editor itself
    // to trigger a recalculation of the keyword case
    const subscription = huePubSub.subscribe('editor.autoformat.applied', () => {
      setAutoFormatCount(prevCount => prevCount + 1);
    });
    return () => {
      subscription.remove();
    };
  }, []);

  const sqlKeywords = useMemo(() => {
    const terminals: { [key: number]: string } = parser?.terminals_ || {};
    const onlyLettersRegex = /^[A-Za-z]+$/;
    const upperCase = Object.values(terminals).filter(str => onlyLettersRegex.test(str));
    const lowerCase = upperCase.map(keyword => keyword.toLowerCase());
    return { upperCase, lowerCase };
  }, [parser]);

  const keywordCase = useMemo(() => {
    const hasKey = (statement: string, keyword: string) => {
      const regex = new RegExp('\\b' + keyword + '\\b', 'g');
      return statement.match(regex);
    };
    const { upperCase, lowerCase } = sqlKeywords;
    const upperCaseCount = upperCase.filter(keyword => hasKey(selectedStatement, keyword)).length;
    const lowerCaseCount = lowerCase.filter(keyword => hasKey(selectedStatement, keyword)).length;

    return lowerCaseCount > upperCaseCount ? 'lower' : 'upper';
  }, [selectedStatement, sqlKeywords, autoFormatCount]);

  return keywordCase;
};

interface UseResizeAwareElementSize {
  height: number;
  width: number;
}

export const useResizeAwareElementSize = (
  refElement: React.RefObject<HTMLElement>
): UseResizeAwareElementSize | undefined => {
  const [size, setSize] = useState<UseResizeAwareElementSize>();
  const observerRef = useRef<ResizeObserver | null>(null);

  // Throttle to avoid too many rerenders during animations
  // use useRef to avoid creating a new function on every render
  const throttledSetSize = useRef(
    throttle(() => {
      setSize(
        refElement.current
          ? {
              height: refElement.current?.clientHeight,
              width: refElement.current?.clientWidth
            }
          : undefined
      );
    }, 100)
  ).current;

  useEffect(() => {
    // We need a state change to trigger the rerender
    const handleResize = (): void => {
      throttledSetSize();
    };

    if (refElement.current) {
      observerRef.current = new ResizeObserver(handleResize);
      observerRef.current.observe(refElement.current);
    }

    return (): void => {
      observerRef.current?.disconnect();
      observerRef.current = null;
    };
  }, [refElement]);

  return size;
};

export const useKeyboardShortcuts = (shortcuts: Record<string, () => void>) => {
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      const { key, ctrlKey, metaKey } = event;

      if (ctrlKey && metaKey && key in shortcuts) {
        event.preventDefault();
        shortcuts[key]?.();
      }
    };

    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, []);
};

export interface HistoryItem {
  date: number;
  value: string;
}

export const useLocalStorageHistory = (
  key: string,
  maxHistoryLength = 10
): [HistoryItem[], (newItem: HistoryItem) => void] => {
  const [history, setHistory] = useState<HistoryItem[]>(() => {
    const savedHistory = getFromLocalStorage(key) as HistoryItem[];
    return savedHistory?.length > 0 ? savedHistory : [];
  });

  useEffect(() => {
    setInLocalStorage(key, history);
  }, [history, key]);

  const addNewItem = (newItem: HistoryItem) => {
    setHistory(prevHistory => {
      const oldItemIndex = prevHistory.findIndex(
        existingItem => existingItem.value === newItem.value
      );
      if (oldItemIndex !== -1) {
        prevHistory.splice(oldItemIndex, 1);
      }
      const newHistory = [newItem, ...prevHistory];
      if (newHistory.length > maxHistoryLength) {
        newHistory.pop();
      }
      return newHistory;
    });
  };

  return [history, addNewItem];
};

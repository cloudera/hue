import { useMemo, useState, useEffect, useRef } from 'react';
import { throttle } from 'lodash';

export const useKeywordCase = (parser: any, selectedStatement: string) => {
  const sqlKeywords = useMemo(() => {
    const terminals: { [key: number]: string } = parser?.terminals_ || {};
    const onlyLettersRegex = /^[A-Za-z]+$/;
    const upperCase = Object.values(terminals).filter(str => onlyLettersRegex.test(str));
    const lowerCase = upperCase.map(keyword => keyword.toLowerCase());

    return { upperCase, lowerCase };
  }, [parser]);

  const keywordCase = useMemo(() => {
    const { upperCase, lowerCase } = sqlKeywords;
    const upperCaseCount = upperCase.filter(keyword => selectedStatement.includes(keyword)).length;
    const lowerCaseCount = lowerCase.filter(keyword => selectedStatement.includes(keyword)).length;
    return lowerCaseCount > upperCaseCount ? 'lower' : 'upper';
  }, [selectedStatement, sqlKeywords]);

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

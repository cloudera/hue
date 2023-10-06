/*
  Licensed to Cloudera, Inc. under one
  or more contributor license agreements.  See the NOTICE file
  distributed with this work for additional information
  regarding copyright ownership.  Cloudera, Inc. licenses this file
  to you under the Apache License, Version 2.0 (the
  "License"); you may not use this file except in compliance
  with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
*/

import React, { useMemo, useState, useEffect, forwardRef } from 'react';

import ReactDOM from 'react-dom';
import classNames from 'classnames';
import HideIcon from '@cloudera/cuix-core/icons/react/HideIcon';
import ViewIcon from '@cloudera/cuix-core/icons/react/ViewIcon';
import IconButton from 'cuix/dist/components/Button/IconButton';
import HistoryIcon from '@cloudera/cuix-core/icons/react/HistoryIcon';

import './AiAssistToolbarHistory.scss';
import TimeAgo from '../../../../../reactComponents/TimeAgo/TimeAgo';

export interface HistoryItem {
  date: number;
  value: string;
}

type HighlightableTextItem = { val: string; highlight?: boolean; key: string };

interface HistoryItemRenderable {
  date: number;
  highligtableValue: Array<HighlightableTextItem>;
  value: string;
  length: number;
  active: boolean;
}

interface AiAssistToolbarHistoryProps {
  autoShow: boolean;
  position: { top: number; left: number } | undefined;
  searchValue: string;
  items: Array<HistoryItem>;
  onHide: () => void;
  onSelect: (HistoryItem) => void;
  onToggleAutoShow: (autoShow: boolean) => void;
  show: boolean;
  ref;
  width: number | undefined;
}

const ENTER_KEY = 'Enter';
const ESCAPE_KEY = 'Escape';
const DOWN_KEY = 'ArrowDown';
const UP_KEY = 'ArrowUp';

const insertBetween = highlighted => {
  return (result: HighlightableTextItem[], value: HighlightableTextItem, index, array) => {
    if (index < array.length - 1) {
      return result.concat([value, { ...highlighted, key: `${highlighted.key}${index}` }]);
    } else {
      return result.concat(value);
    }
  };
};

const AiAssistToolbarHistory = forwardRef(
  (
    {
      position,
      searchValue = '',
      items,
      onToggleAutoShow,
      onHide,
      onSelect,
      show,
      autoShow,
      width
    }: AiAssistToolbarHistoryProps,
    ref
  ) => {
    const [activeItemIndex, setActiveItemIndex] = useState(-1);

    useEffect(() => {
      function handleClickOutside(event: MouseEvent) {
        const refElement: HTMLElement = (ref as any)?.current;
        if (show && refElement && !refElement.contains(event.target as Node)) {
          onHide();
        }
      }
      document.addEventListener('mousedown', handleClickOutside);
      return () => {
        document.removeEventListener('mousedown', handleClickOutside);
      };
    }, [ref, onHide]);

    const lowerCaseSearchValue = searchValue.toLowerCase();
    const lowerCaseItems = useMemo(
      () =>
        items.map(item => ({
          ...item,
          value: item.value.toLowerCase(),
          length: item.value.length
        })),
      [items]
    );

    const filteredItems: Array<HistoryItem> = lowerCaseItems.filter(item => {
      return !lowerCaseSearchValue || item.value.includes(lowerCaseSearchValue);
    });

    const itemRefs = useMemo(
      () =>
        Array(filteredItems.length)
          .fill(0)
          .map(i => React.createRef<HTMLElement>()),
      [filteredItems]
    );

    const renderableItems: Array<HistoryItemRenderable> = filteredItems.map((item, index) => {
      let highlightableText = [{ val: item.value, key: item.value }];
      const shouldHighlightText = lowerCaseSearchValue !== '';
      if (shouldHighlightText) {
        const highlighted: HighlightableTextItem = {
          val: lowerCaseSearchValue,
          highlight: true,
          key: lowerCaseSearchValue
        };

        highlightableText = item.value
          .split(lowerCaseSearchValue)
          .map((val, index) => ({ val, key: `${val}${index}` } as HighlightableTextItem))
          .reduce(insertBetween(highlighted), [] as HighlightableTextItem[]);
      }
      return {
        ...item,
        length: item.value.length,
        highligtableValue: highlightableText,
        active: index === activeItemIndex
      };
    });

    const handleFocus = () => {
      setActiveItemIndex(0);
    };

    const scrollIntoView = (index: number) => {
      itemRefs[index]?.current?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
      e.preventDefault();
      if (e.key === DOWN_KEY) {
        const isLastItem = activeItemIndex === renderableItems.length - 1;
        const newIndex = isLastItem ? activeItemIndex : activeItemIndex + 1;
        setActiveItemIndex(newIndex);
        scrollIntoView(newIndex);
      } else if (e.key === UP_KEY) {
        if (activeItemIndex === 0) {
          setActiveItemIndex(-1);
          onHide();
        } else {
          setActiveItemIndex(activeItemIndex - 1);
          scrollIntoView(activeItemIndex - 1);
        }
      } else if (e.key === ENTER_KEY && activeItemIndex >= 0) {
        const selectedItem = filteredItems[activeItemIndex];
        setActiveItemIndex(-1);
        onSelect(selectedItem);
      } else if (e.key === ESCAPE_KEY && activeItemIndex >= 0) {
        setActiveItemIndex(-1);
        onHide();
      }
    };

    const toggleTitle = autoShow
      ? `Click to not show history automatically`
      : `Click to automatically show history`;

    return !filteredItems.length || !show || !position
      ? null
      : ReactDOM.createPortal(
          <div
            ref={ref as React.RefObject<HTMLDivElement>}
            onFocus={handleFocus}
            onKeyDown={handleKeyDown}
            role="menu"
            aria-label="Prompt history"
            tabIndex={0}
            style={{ top: `${position.top}px`, left: `${position.left}px`, width: `${width}px` }}
            className="hue-ai-assist-toolbar-history"
          >
            <div className="hue-ai-assist-toolbar-history__top">
              <IconButton
                className="hue-ai-assist-toolbar-history__toggle-auto-show"
                onClick={() => onToggleAutoShow(!autoShow)}
                aria-label={toggleTitle}
                title={toggleTitle}
                data-event=""
                icon={
                  autoShow ? (
                    <div style={{ width: '24px', height: '24px' }}>
                      <ViewIcon />
                    </div>
                  ) : (
                    <div style={{ width: '24px', height: '24px' }}>
                      <HideIcon />
                    </div>
                  )
                }
                onFocusCapture={e => e.stopPropagation()}
              />
            </div>
            <ul className="hue-ai-assist-toolbar-history__menu-container">
              {renderableItems.map((item, index) => {
                return (
                  <li
                    role="menuitem"
                    tabIndex={-1}
                    key={item.date}
                    className={classNames('hue-ai-assist-toolbar-history__item', {
                      'hue-ai-assist-toolbar-history__item--active': item.active
                    })}
                    title={item.value}
                    aria-label={item.value}
                    onClick={() => onSelect({ value: item.value, date: item.date })}
                    ref={itemRefs[index]}
                  >
                    <HistoryIcon className="hue-ai-assist-toolbar-history__item-icon" />
                    <div className="hue-ai-assist-toolbar-history__item-value">
                      {item.highligtableValue.map(valueContainer =>
                        valueContainer.highlight ? (
                          <span
                            key={valueContainer.key}
                            className="hue-ai-assist-toolbar-history__item-highlight"
                          >
                            {valueContainer.val}
                          </span>
                        ) : (
                          <span key={valueContainer.key}>{valueContainer.val}</span>
                        )
                      )}
                    </div>
                    <div
                      title={new Date(item.date).toLocaleString()}
                      className="hue-ai-assist-toolbar-history__item-time"
                    >
                      <TimeAgo value={item.date} />
                    </div>
                  </li>
                );
              })}
            </ul>
          </div>,
          document.body
        );
  }
);

export default AiAssistToolbarHistory;

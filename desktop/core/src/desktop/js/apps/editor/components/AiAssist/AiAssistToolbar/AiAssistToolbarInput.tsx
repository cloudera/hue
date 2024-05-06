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

import React, { useState, useEffect, useRef } from 'react';
import classNames from 'classnames';
import { EnterOutlined } from '@ant-design/icons';
import { Button } from 'antd';

import { getFromLocalStorage, setInLocalStorage } from 'utils/storageUtils';
import huePubSub from 'utils/huePubSub';

import AiAssistToolbarHistory, { HistoryItem } from './AiAssistToolbarHistory';
import { useResizeAwareElementSize, useLocalStorageHistory } from '../hooks';
import { GLOBAL_INFO_TOPIC } from '../../../../../reactComponents/AlertComponent/events';

import './AiAssistToolbarInput.scss';

const ENTER_KEY = 'Enter';
const ESCAPE_KEY = 'Escape';
const DOWN_KEY = 'ArrowDown';
const TAB_KEY = 'Tab';
const MAX_INPUT_WIDTH = 700;
const MAX_INPUT_LINES = 10;
const AUTO_SHOW_STORAGE_KEY = 'hue.aiAssistBar.history.autoShow';
const HISTORY_STORAGE_KEY = 'hue.aiAssistBar.history.items';

const getSingleLineHeight = (singleLineSpanRef: React.RefObject<HTMLSpanElement>): number => {
  return singleLineSpanRef?.current?.clientHeight || 0;
};

const isMultiLineSpan = (
  spanRefToMeasure: React.RefObject<HTMLSpanElement>,
  singleLineSpanRefToCompareWith: React.RefObject<HTMLSpanElement>,
  text: string
): boolean => {
  const isEmpty = text === '';
  const trailingNewLine = text.endsWith('\n');
  const singleLineHeight = getSingleLineHeight(singleLineSpanRefToCompareWith);
  const spanToMeasureHeight = spanRefToMeasure?.current?.clientHeight || 0;
  return isEmpty ? false : trailingNewLine || spanToMeasureHeight > singleLineHeight;
};

const calculateAvailableWidth = (toolbarButtonWrapperRef: React.RefObject<HTMLSpanElement>) => {
  const containerWidth = toolbarButtonWrapperRef.current?.clientWidth;
  const buttonElement = toolbarButtonWrapperRef.current?.querySelector(
    '.hue-toolbar-button'
  ) as HTMLElement;
  const additionalPadding = 18;
  const newLineButtonWidth = buttonElement ? buttonElement.offsetWidth + additionalPadding : 0;
  return containerWidth ? containerWidth - newLineButtonWidth : undefined;
};

const updateTextareaDimensions = ({
  sizeMeasureSpan,
  textarea,
  userText,
  maxWidth,
  maxHeight,
  singleLineHeight,
  availableWidth
}: {
  sizeMeasureSpan: HTMLElement | null;
  textarea: HTMLTextAreaElement;
  userText: string;
  maxWidth: number;
  maxHeight: number;
  singleLineHeight: number;
  availableWidth: number;
}) => {
  if (sizeMeasureSpan) {
    sizeMeasureSpan.style.maxWidth = `${maxWidth}px`;

    const calculatedWidth = sizeMeasureSpan.offsetWidth;
    const modifiedWidth = userText ? `${calculatedWidth}px` : `${availableWidth}px`;
    textarea.style.width = modifiedWidth;
    const newLineWithoutContent = userText.endsWith('\n') ? singleLineHeight : 0;
    const modifiedHeight = userText
      ? `${sizeMeasureSpan.offsetHeight + newLineWithoutContent}px`
      : `${singleLineHeight}px`;
    textarea.style.height = modifiedHeight;
    textarea.style.maxHeight = `${maxHeight}px`;
  }
};

const isPrefillMultiLine = (sizeMeasureSpan: HTMLElement | null, singleLineHeight: number) => {
  return !!sizeMeasureSpan && sizeMeasureSpan.offsetHeight > singleLineHeight;
};

const truncatePlaceholderText = (placeholder: string, spanSingleLineRef, spanSizeRef) => {
  const placeHolderTextFullLength = placeholder;
  const singleLineHeight = getSingleLineHeight(spanSingleLineRef);
  const needsEllipsis = isPrefillMultiLine(spanSizeRef.current, singleLineHeight);
  const placeHolderText = needsEllipsis
    ? `${placeHolderTextFullLength.slice(0, 50)}...`
    : placeHolderTextFullLength;
  return placeHolderText;
};

const calculateDropdownPosition = (
  textareaElement: HTMLTextAreaElement,
  textAreaIsMultiLine: boolean
) => {
  const textareaTop = textareaElement.getBoundingClientRect().top;
  const textareaLeft = textareaElement.getBoundingClientRect().left;
  const DEFAULT_VERTICAL_SPACING = 4;
  const extraSpacingTop = textAreaIsMultiLine ? 0 : DEFAULT_VERTICAL_SPACING;
  const dropdownTop = textareaTop + extraSpacingTop + textareaElement.clientHeight;

  return {
    top: dropdownTop,
    left: textareaLeft
  };
};

const hasReasonableInputLength = (value: string) => {
  const trimmed = value?.trim();
  const atLeast4NonDigits = /(?:\D.*?){4}/u;
  return atLeast4NonDigits.test(trimmed);
};

function AiAssistToolbarInput({
  isAnimating,
  placeholder,
  onSubmit,
  onCancel,
  onAnimationEnded,
  onInputChanged,
  isLoading,
  isExpanded,
  prefill = '',
  value
}: {
  isAnimating: boolean;
  isExpanded: boolean;
  isLoading: boolean;
  placeholder: string;
  prefill?: string;
  onSubmit: (value: string) => void;
  onCancel: () => void;
  onInputChanged: (value: string) => void;
  onAnimationEnded: () => void;
  value: string;
}): JSX.Element {
  const autoShow = getFromLocalStorage(AUTO_SHOW_STORAGE_KEY, true);
  const [dirty, setDirty] = useState<boolean>(false);
  const [touched, setTouched] = useState<boolean>(false);
  const [historyDropdownPostion, setHistoryDropdownPostion] =
    useState<{ top: number; left: number }>();
  const [historyDropdownWidth, setHistoryDropdownWidth] = useState<number>();
  const [showHistoryDropdown, setShowHistoryDropdown] = useState<boolean>(autoShow);
  const [singleLinePlaceholderText, setSingleLinePlaceholderText] = useState<string>();
  const [userChoiceAutoShowHistory, setUserChoiceAutoShowHistory] = useState<boolean>(autoShow);
  const [historyItems, addHistoryItem] = useLocalStorageHistory(HISTORY_STORAGE_KEY, 50);

  const toolbarButtonWrapperRef = useRef<HTMLDivElement>(null);
  const spanSizeRef = useRef<HTMLSpanElement>(null);
  const spanSingleLineRef = useRef<HTMLSpanElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const historyDropdownRef = useRef<HTMLElement>(null);

  const resizeAwareMaxWidth = useResizeAwareElementSize(toolbarButtonWrapperRef)?.width;
  const placeholderText = prefill || placeholder;
  const isMultiLine = isMultiLineSpan(spanSizeRef, spanSingleLineRef, value);

  useEffect(() => {
    const availableWidth = calculateAvailableWidth(toolbarButtonWrapperRef) || 0;
    const maxWidth = availableWidth ? Math.min(availableWidth, MAX_INPUT_WIDTH) : MAX_INPUT_WIDTH;
    const singleLineHeight = getSingleLineHeight(spanSingleLineRef);
    const maxHeight = getSingleLineHeight(spanSingleLineRef) * MAX_INPUT_LINES;

    if (textareaRef.current) {
      updateTextareaDimensions({
        sizeMeasureSpan: spanSizeRef.current,
        textarea: textareaRef.current,
        userText: value,
        maxWidth,
        maxHeight,
        singleLineHeight,
        availableWidth
      });

      setSingleLinePlaceholderText(
        truncatePlaceholderText(placeholderText, spanSingleLineRef, spanSizeRef)
      );

      setHistoryDropdownPostion(calculateDropdownPosition(textareaRef.current, isMultiLine));
      setHistoryDropdownWidth(textareaRef.current.parentElement?.clientWidth);
    }
  }, [inputPromptValue, prefill, resizeAwareMaxWidth, placeholderText]);

  useEffect(() => {
    if (!isAnimating && isExpanded) {
      if (userChoiceAutoShowHistory && !showHistoryDropdown) {
        setShowHistoryDropdown(true);
      }
      focusInput();
    }
  }, [isAnimating, isExpanded]);

  const handleSubmit = () => {
    addHistoryItem({ value: value, date: new Date().getTime() });
    onSubmit(value);
    setDirty(false);
    setTouched(false);
  };

  const handleCancel = () => {
    onCancel();
    setDirty(false);
    setTouched(false);
    onInputChanged('');
  };

  const handleOnChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value;
    onInputChanged(newValue);
    setDirty(newValue ? true : false);
    setTouched(true);
  };

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === ENTER_KEY && !event.shiftKey) {
      event.preventDefault();
      if (hasReasonableInputLength(value)) {
        handleSubmit();
      } else {
        huePubSub.publish(GLOBAL_INFO_TOPIC, {
          message: 'Please use at least 4 letters in your prompt'
        });
      }
    } else if (event.key === ESCAPE_KEY) {
      handleCancel();
    } else if (event.key === TAB_KEY && !dirty && prefill) {
      onInputChanged(prefill);
      event.preventDefault();
    } else if (event.key === DOWN_KEY) {
      setShowHistoryDropdown(true);
      historyDropdownRef.current?.focus();
    }
  };

  const focusInput = () => {
    textareaRef.current?.focus();
  };

  const handleHistorySelect = (item: HistoryItem) => {
    onInputChanged(item.value);
    setShowHistoryDropdown(false);
    focusInput();
  };

  const executeLabel = 'Press enter or click here to execute';

  return (
    <li
      onAnimationEnd={() => {
        onAnimationEnded();
      }}
      ref={toolbarButtonWrapperRef}
      className={classNames('hue-toolbar-button__wrapper', 'hue-ai-assist-toolbar-input__wrapper', {
        'hue-ai-assist-toolbar-input__wrapper--expanded': isExpanded
      })}
    >
      {isExpanded && (
        <>
          <textarea
            title={
              !dirty && !touched && prefill
                ? `Press Tab to insert prompt:\n${placeholderText}`
                : 'Press down arrow to select from history'
            }
            disabled={isLoading}
            ref={textareaRef}
            value={value}
            onChange={handleOnChange}
            placeholder={singleLinePlaceholderText}
            spellCheck="false"
            className={classNames('hue-ai-assist-toolbar-input__text-input', {
              ['hue-ai-assist-toolbar-input__text-input--empty']: !value,
              ['hue-ai-assist-toolbar-input__text-input--animating']: isAnimating,
              ['hue-ai-assist-toolbar-input__text-input--multi-line']: isMultiLine,
              ['hue-ai-assist-toolbar-input__text-input--is-prefill']: !value && prefill
            })}
            onKeyDown={handleKeyDown}
          />

          <span className="hue-ai-assist-toolbar-input__size-reference-element" ref={spanSizeRef}>
            {value || placeholderText}
          </span>
          <span
            className="hue-ai-assist-toolbar-input__single-line-reference-element"
            ref={spanSingleLineRef}
          >
            ""
          </span>
          <AiAssistToolbarHistory
            ref={historyDropdownRef}
            position={historyDropdownPostion}
            width={historyDropdownWidth}
            show={!isAnimating && !isLoading && showHistoryDropdown}
            autoShow={userChoiceAutoShowHistory}
            onToggleAutoShow={newAutoShow => {
              setInLocalStorage(AUTO_SHOW_STORAGE_KEY, newAutoShow);
              setUserChoiceAutoShowHistory(newAutoShow);
            }}
            onHide={() => {
              focusInput();
              setShowHistoryDropdown(false);
            }}
            onSelect={handleHistorySelect}
            searchValue={value}
            items={historyItems}
          />
          {hasReasonableInputLength(value) && (
            <Button
              disabled={isLoading}
              className={'hue-toolbar-button'}
              onClick={handleSubmit}
              type="link"
              title={executeLabel}
              aria-label={executeLabel}
            >
              <EnterOutlined className="hue-ai-assist-toolbar-input__enter-icon" />
            </Button>
          )}
        </>
      )}
    </li>
  );
}

export default AiAssistToolbarInput;

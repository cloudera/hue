import React, { useState, useEffect, useRef } from 'react';
import classNames from 'classnames';
import { EnterOutlined } from '@ant-design/icons';
import { Button } from 'antd';

import { useResizeAwareElementSize } from '../hooks';

import './AiAssistToolbarInput.scss';

const ENTER_KEY = 'Enter';
const ESCAPE_KEY = 'Escape';
const MAX_INPUT_WIDTH = 700;
const MAX_INPUT_LINES = 10;

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
  const newLineButtonWidth = 64;
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
}) => {
  if (sizeMeasureSpan && textarea) {
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

function AiAssistToolbarInput({
  placeholder,
  onSubmit,
  onCancel,
  isLoading,
  isExpanded
}: {
  isExpanded: boolean;
  isLoading: boolean;
  placeholder: string;
  onSubmit: (value: string) => void;
  onCancel: () => void;
}) {
  const [value, setValue] = useState<string>('');
  const toolbarButtonWrapperRef = useRef<HTMLDivElement>(null);
  const spanSizeRef = useRef<HTMLSpanElement | null>(null);
  const spanSingleLineRef = useRef<HTMLSpanElement | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  const availableWidth = useResizeAwareElementSize(toolbarButtonWrapperRef)?.width;

  useEffect(() => {
    console.info(JSON.stringify(value));
    const availableWidth = calculateAvailableWidth(toolbarButtonWrapperRef);
    const maxWidth = availableWidth ? Math.min(availableWidth, MAX_INPUT_WIDTH) : MAX_INPUT_WIDTH;
    const singleLineHeight = getSingleLineHeight(spanSingleLineRef);
    const maxHeight = `${getSingleLineHeight(spanSingleLineRef) * MAX_INPUT_LINES}`;

    updateTextareaDimensions({
      sizeMeasureSpan: spanSizeRef.current,
      textarea: textareaRef.current,
      userText: value,
      maxWidth,
      maxHeight,
      singleLineHeight,
      availableWidth
    });
  }, [value, availableWidth]);

  const isMultiLine = isMultiLineSpan(spanSizeRef, spanSingleLineRef, value);

  return (
    <li
      ref={toolbarButtonWrapperRef}
      className={classNames('hue-toolbar-button__wrapper', 'hue-ai-assist-toolbar-input__wrapper', {
        'hue-ai-assist-toolbar-input__wrapper--expanded': isExpanded
      })}
    >
      {isExpanded && (
        <>
          <textarea
            disabled={isLoading}
            ref={textareaRef}
            value={value}
            onChange={e => setValue(e.target.value)}
            placeholder={placeholder}
            autoFocus
            spellCheck="false"
            className={classNames('hue-ai-assist-toolbar-input__text-input', {
              ['hue-ai-assist-toolbar-input__text-input--empty']: !value,
              ['hue-ai-assist-toolbar-input__text-input--multi-line']: isMultiLine
            })}
            onKeyDown={event => {
              if (event.key === ENTER_KEY && !event.shiftKey && value) {
                onSubmit(value);
              } else if (event.key === ESCAPE_KEY) {
                onCancel();
              }
            }}
          />
          <span className="hue-ai-assist-toolbar-input__size-reference-element" ref={spanSizeRef}>
            {value}
          </span>
          <span
            className="hue-ai-assist-toolbar-input__single-line-reference-element"
            ref={spanSingleLineRef}
          >
            ""
          </span>
          {value && (
            <Button
              disabled={isLoading}
              className={'hue-toolbar-button'}
              onClick={() => onSubmit(value)}
              type="link"
              title="Hit enter or click here to execute"
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

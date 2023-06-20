import React, { useState, useEffect, useRef } from 'react';
import classNames from 'classnames';
import { EnterOutlined } from '@ant-design/icons';
import { Button } from 'antd';

import { useResizeAwareElementSize } from '../hooks';

import './AiAssistToolbarInput.scss';

const ENTER_KEY = 'Enter';
const ESCAPE_KEY = 'Escape';
const TAB_KEY = 'Tab';
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
  isExpanded,
  prefill = ''
}: {
  isExpanded: boolean;
  isLoading: boolean;
  placeholder: string;
  prefill?: string;
  onSubmit: (value: string) => void;
  onCancel: () => void;
}) {
  const [value, setValue] = useState<string>('');
  const [dirty, setDirty] = useState<boolean>(false);
  const [touched, setTouched] = useState<boolean>(false);
  const toolbarButtonWrapperRef = useRef<HTMLDivElement>(null);
  const spanSizeRef = useRef<HTMLSpanElement | null>(null);
  const spanSingleLineRef = useRef<HTMLSpanElement | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  const availableWidth = useResizeAwareElementSize(toolbarButtonWrapperRef)?.width;
  const placeHolderText = prefill ? prefill : placeholder;

  useEffect(() => {
    const availableWidth = calculateAvailableWidth(toolbarButtonWrapperRef);
    const maxWidth = availableWidth ? Math.min(availableWidth, MAX_INPUT_WIDTH) : MAX_INPUT_WIDTH;
    const singleLineHeight = getSingleLineHeight(spanSingleLineRef);
    const maxHeight = `${getSingleLineHeight(spanSingleLineRef) * MAX_INPUT_LINES}`;

    updateTextareaDimensions({
      sizeMeasureSpan: spanSizeRef.current,
      textarea: textareaRef.current,
      userText: value || prefill,
      maxWidth,
      maxHeight,
      singleLineHeight,
      availableWidth
    });
  }, [value, prefill, availableWidth]);

  const isMultiLine = isMultiLineSpan(spanSizeRef, spanSingleLineRef, value);

  const handleSubmit = () => {
    onSubmit(value);
    setValue('');
    setDirty(false);
    setTouched(false);
  };

  const handleCancel = () => {
    onCancel();
    setValue('');
    setDirty(false);
    setTouched(false);
  };

  const handleOnChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value;
    setValue(newValue);
    setDirty(newValue ? true : false);
    setTouched(true);
  };

  return (
    <li
      onAnimationEnd={() => {
        console.info('onAnimationEnd');
      }}
      ref={toolbarButtonWrapperRef}
      className={classNames('hue-toolbar-button__wrapper', 'hue-ai-assist-toolbar-input__wrapper', {
        'hue-ai-assist-toolbar-input__wrapper--expanded': isExpanded
      })}
    >
      {isExpanded && (
        <>
          <textarea
            title={!dirty && !touched && prefill? 'Press Tab to insert NQL from comment' : ''}
            disabled={isLoading}
            ref={textareaRef}
            value={value}
            onChange={handleOnChange}
            placeholder={placeHolderText}
            autoFocus
            spellCheck="false"
            className={classNames('hue-ai-assist-toolbar-input__text-input', {
              ['hue-ai-assist-toolbar-input__text-input--empty']: !value,
              ['hue-ai-assist-toolbar-input__text-input--multi-line']: isMultiLine,
              ['hue-ai-assist-toolbar-input__text-input--is-prefill']: !value && prefill
            })}
            onKeyDown={event => {
              if (event.key === ENTER_KEY && !event.shiftKey && value) {
                handleSubmit();
              } else if (event.key === ESCAPE_KEY) {
                handleCancel();
              } else if (event.key === TAB_KEY && !dirty && prefill) {
                setValue(prefill);
                event.preventDefault();
              }
            }}
          />
          <span className="hue-ai-assist-toolbar-input__size-reference-element" ref={spanSizeRef}>
            {value || placeHolderText}
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
              onClick={handleSubmit}
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

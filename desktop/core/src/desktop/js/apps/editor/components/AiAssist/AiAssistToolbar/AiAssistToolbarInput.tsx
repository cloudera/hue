import React, { useState, useEffect, useRef } from 'react';
import classNames from 'classnames';
import { EnterOutlined } from '@ant-design/icons';
import { Button } from 'antd';

const ENTER_KEY = 'Enter';
const ESCAPE_KEY = 'Escape';

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
  const spanRef = useRef<HTMLSpanElement | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    if (spanRef.current && inputRef.current) {
      const modifiedWidth = value ? `${spanRef.current.offsetWidth}px` : '100%';
      inputRef.current.style.width = modifiedWidth;
    }
  }, [value]);

  return (
    <li
      className={classNames('hue-toolbar-button__wrapper', 'hue-ai-assist-toolbar-input__wrapper', {
        'hue-ai-assist-toolbar-input__wrapper--expanded': isExpanded
      })}
    >
      {isExpanded && (
        <>
          <input
            disabled={isLoading}
            ref={inputRef}
            value={value}
            onChange={e => setValue(e.target.value)}
            placeholder={placeholder}
            type="text"
            autoFocus
            spellCheck="false"
            className={classNames('hue-ai-assist-toolbar-input__text-input', {
              ['hue-ai-assist-toolbar-input__text-input--empty']: !value
            })}
            onKeyDown={event => {
              if (event.key === ENTER_KEY && value) {
                onSubmit(value);
              } else if (event.key === ESCAPE_KEY) {
                onCancel();
              }
            }}
          />
          <span className="hue-ai-assist-toolbar-input__width-reference-element" ref={spanRef}>
            {value}
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

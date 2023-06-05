import React from 'react';
import classNames from 'classnames';

function AiAssistToolbarInput ({ expanded, placeholder, onSubmit }) {
  return (
    <li
      className={classNames(
        'hue-toolbar-button__wrapper',
        'hue-ai-assist-toolbar-input__wrapper',
        {
          'hue-ai-assist-toolbar-input__wrapper--expanded': expanded
        }
      )}
    >
      {expanded && (
        <input
          placeholder={placeholder}
          type="text"
          autoFocus
          spellCheck="false"
          className="hue-ai-assist-toolbar-input__text-input"
          onKeyDown={(event)=>{
            if (event.key === 'Enter') {
              const userInput = (event.target as HTMLInputElement).value;
              onSubmit(userInput);
            }

          }}
        />
      )}
    </li>
  );
};

export default AiAssistToolbarInput;
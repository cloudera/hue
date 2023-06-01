import React from 'react';
import classNames from 'classnames';

function ToolbarInput ({ expanded, placeholder, onSubmit }) {
  return (
    <li
      className={classNames(
        'hue-toolbar-button__wrapper',
        'hue-ai-assist-bar__toolbar__input-wrapper',
        {
          'hue-ai-assist-bar__toolbar__input-wrapper--expanded': expanded
        }
      )}
    >
      {expanded && (
        <input
          placeholder={placeholder}
          type="text"
          autoFocus
          spellCheck="false"
          className="hue-ai-assist-bar__generate-text-input"
          // onChange={evt => console.info(evt.target.value, evt)}
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

export default ToolbarInput;
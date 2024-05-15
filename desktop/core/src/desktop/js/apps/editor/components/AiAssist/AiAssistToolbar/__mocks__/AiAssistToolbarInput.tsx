import React from 'react';

const AiAssistToolbarInputMock = jest.fn(({ placeholder }) => (
  <div data-testid="mock-ai-assist-toolbar-input">{placeholder}</div>
));

export default AiAssistToolbarInputMock;

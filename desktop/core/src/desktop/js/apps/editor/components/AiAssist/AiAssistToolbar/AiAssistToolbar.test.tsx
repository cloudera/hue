jest.mock('./AiAssistToolbarInput');

import React from 'react';
import { render,act } from '@testing-library/react';
import '@testing-library/jest-dom';
import userEvent from '@testing-library/user-event';
import AssistToolbar from './AiAssistToolbar';
import { AiActionModes } from '../sharedTypes';
  
jest.mock( 'api/apiAIHelper', () => ({
  getHistoryItems: jest.fn().mockResolvedValue([{
    id: 1,
    prompt: 'Existing Prompt in history',
    updatedAt: 12351,
    db: 'default',
    dialect: 'hive'
  }]),
  createHistoryItem: jest.fn().mockResolvedValue({ prompt: 'created', id: 1 }),
  updateHistoryItem: jest.fn().mockResolvedValue({ prompt: 'created', id: 1 })
}));
describe('AssistToolbar', () => {
  const mockSetActionMode = jest.fn();
  const mockSetErrorStatusText = jest.fn();
  const mockLoadExplanation = jest.fn();
  const mockLoadOptimization = jest.fn();
  const mockLoadFixSuggestion = jest.fn();
  const mockLoadComments = jest.fn();
  const mockOnInputSubmit = jest.fn();
  const mockOnInputChanged = jest.fn();
  const defaultProps = {
    showActions: [
      AiActionModes.GENERATE,
      AiActionModes.EDIT,
      AiActionModes.EXPLAIN,
      AiActionModes.OPTIMIZE,
      AiActionModes.FIX,
      AiActionModes.COMMENT
    ],
    actionMode: undefined,
    setActionMode: mockSetActionMode,
    isLoading: false,
    setErrorStatusText: mockSetErrorStatusText,
    inputExpanded: false,
    inputValue: '',
    inputPrefill: '',
    loadExplanation: mockLoadExplanation,
    loadComments: mockLoadComments,
    parsedStatement: { statement: 'SELECT * FROM table' },
    loadOptimization: mockLoadOptimization,
    loadFixSuggestion: mockLoadFixSuggestion,
    isSqlError: false,
    onInputSubmit: mockOnInputSubmit,
    onInputChanged: mockOnInputChanged,
    databaseName: '',
    dialect: ''
  };


  it('renders AiAssistToolbarInput mock correctly', async () => {
    let getAllByTestId;
    await act(async () => {
      const renderResult = render(
        <AssistToolbar {...defaultProps} actionMode={AiActionModes.GENERATE} />
      );
      getAllByTestId = renderResult.getAllByTestId;

    });
    const aiAssistToolbarInputs = getAllByTestId('mock-ai-assist-toolbar-input');
    expect(aiAssistToolbarInputs).toHaveLength(2);
  });

  it('should disable edit, explain, optimize and fix buttons on empty statement', async () => {
    let getByTitle;
    await act(async () => {
      const renderResult = render(<AssistToolbar {...defaultProps} parsedStatement={{ statement: '' }} />);
      getByTitle = renderResult.getByTitle;
    });

    const editButton = getByTitle('Edit selected SQL statement using natural language');
    expect(editButton).toBeDisabled();

    const explainButton = getByTitle('Explain the selected SQL statement');
    expect(explainButton).toBeDisabled();

    const optimizeButton = getByTitle('Optimize the selected SQL statement');
    expect(optimizeButton).toBeDisabled();

    const fixButton = getByTitle('Fix the selected SQL statement');
    expect(fixButton).toBeDisabled();
  });

  it('should not disable generate button when there is a statement present', async () => {
    let getByTitle;
    await act(async () => {
      const renderResult = render(<AssistToolbar {...defaultProps} />);
      getByTitle = renderResult.getByTitle;
    });
    const generateButton = getByTitle('Generate SQL using natural language');
    expect(generateButton).not.toBeDisabled();
  });

  it('should enable generate button if the statement only has nql comment', async () => {
    let getByTitle;
    await act(async () => {
       const renderResult = render(<AssistToolbar {...defaultProps} parsedStatement={{ statement: '/* NQL: do stuff */' }} />)
       getByTitle = renderResult.getByTitle
    });
    const generateButton = getByTitle('Generate SQL using natural language');
    expect(generateButton).toBeEnabled();
  });

  it('should disable all buttons on loading', async () => {
    let getByTitle, renderResult;
    await act(async () => {
      renderResult = render(<AssistToolbar {...defaultProps} isLoading />);
      getByTitle = renderResult.getByTitle;
    });


    const editButton = getByTitle('Edit selected SQL statement using natural language');
    expect(editButton).toBeDisabled();

    const explainButton = getByTitle('Explain the selected SQL statement');
    expect(explainButton).toBeDisabled();

    const optimizeButton = getByTitle('Optimize the selected SQL statement');
    expect(optimizeButton).toBeDisabled();

    const fixButton = getByTitle('Fix the selected SQL statement');
    expect(fixButton).toBeDisabled();

    renderResult.rerender(<AssistToolbar {...defaultProps} parsedStatement={{ statement: '' }} isLoading />);
    const generateButton = getByTitle('Generate SQL using natural language');
    expect(generateButton).toBeDisabled();
  });

  it('should toggle action generate action mode correctly', async () => {
    const user = userEvent.setup();
    const { getByTitle } = render(
      <AssistToolbar {...defaultProps} parsedStatement={{ statement: '' }} />
    );
    const generateButton = getByTitle('Generate SQL using natural language');
    await user.click(generateButton);
    
    expect(mockSetActionMode).toHaveBeenCalledWith(AiActionModes.GENERATE);
  });

  it('should toggle action edit action mode correctly', async () => {
    const user = userEvent.setup();
    const { getByTitle } = render(<AssistToolbar {...defaultProps} />);
    const editButton = getByTitle('Edit selected SQL statement using natural language');
    await user.click(editButton);
    expect(mockSetActionMode).toHaveBeenCalledWith(AiActionModes.EDIT);
  });


  it('should disable buttons when isLoading is true', async () => {
    const props = { ...defaultProps, isLoading: true };
    let getByTitle;
    await act(async () => {
      const renderResult = render(<AssistToolbar {...props} />);
      getByTitle = renderResult.getByTitle;
    });
  
    const generateButton = getByTitle('Generate SQL using natural language');
    expect(generateButton).toBeDisabled();
  });

  it('should call loadExplanation on explain button click', async () => {
    const user = userEvent.setup();
    const { getByTitle } = render(<AssistToolbar {...defaultProps} />);
    const explainButton = getByTitle('Explain the selected SQL statement');
    await user.click(explainButton);
    expect(mockLoadExplanation).toHaveBeenCalledWith('SELECT * FROM table');
  });

  it('should call loadOptimization on optimize button click', async () => {
    const user = userEvent.setup();
    const { getByTitle } = render(<AssistToolbar {...defaultProps} />);
    const optimizeButton = getByTitle('Optimize the selected SQL statement');
    await user.click(optimizeButton);
    expect(mockLoadOptimization).toHaveBeenCalledWith('SELECT * FROM table');
  });

  it('should call loadFixSuggestion on fix button click when isSqlError is true', async () => {
    const user = userEvent.setup();
    const props = { ...defaultProps, isSqlError: true };
    const { getByTitle } = render(<AssistToolbar {...props} />);
    const fixButton = getByTitle('Fix the selected SQL statement');
    await user.click(fixButton);
    expect(mockLoadFixSuggestion).toHaveBeenCalledWith('SELECT * FROM table');
  });


  it('should call loadComments on comment button click', async () => {
    const user = userEvent.setup();
    const props = { ...defaultProps };
    const { getByTitle } = render(<AssistToolbar {...props} />);
    const commentButton = getByTitle('Comment SQL');
    await user.click(commentButton);
    expect(mockLoadComments).toHaveBeenCalledWith('SELECT * FROM table');
  });

  it('hides the action buttons if the action is missing in the showActions prop', async () => {
    const props = { ...defaultProps, isSqlError: true, showActions: [] };
    await act(async () => {
      const {queryByTitle} = render(<AssistToolbar {...props} />);
      expect(queryByTitle('Fix the selected SQL statement')).toBeNull();
      expect(queryByTitle('Comment SQL')).toBeNull();
      expect(queryByTitle('Optimize the selected SQL statement')).toBeNull();
      expect(queryByTitle('Explain the selected SQL statement')).toBeNull();
      expect(queryByTitle('Edit selected SQL statement using natural language')).toBeNull();
    });
  });
});

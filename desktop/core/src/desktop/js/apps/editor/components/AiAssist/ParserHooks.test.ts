// Mocks for external dependencies
jest.mock('utils/huePubSub');
jest.mock('parse/sql/sqlParserRepository');

import { renderHook, waitFor, act } from '@testing-library/react';

import huePubSub from 'utils/huePubSub';
import Executor from 'apps/editor/execution/executor';
import SqlExecutable from '../../execution/sqlExecutable';
import sqlParserRepository from 'parse/sql/sqlParserRepository';

import { useParser } from './ParserHook';

const VALID_SQL = 'SELECT * FROM customers';

describe('useParser hook', () => {
  const mockExecutor = (mock: unknown): Executor => mock as Executor;
  let sqlExecutableMock;
  let removeSubscriptionMock;
  let parseSyntaxMock;
  let parseSqlMock;

  beforeEach(() => {
    sqlExecutableMock = new SqlExecutable({
      database: 'default',
      parsedStatement: { statement: VALID_SQL },
      executor: mockExecutor({
        connector: () => ({ id: 'test', dialect: 'hive' }),
        compute: () => ({ id: 'test' }),
        namespace: () => ({ id: 'test' }),
        defaultLimit: () => 100,
        toJs: () => ({})
      })
    });
    removeSubscriptionMock = jest.fn();
    huePubSub.subscribe.mockImplementation(() => {
      return { remove: removeSubscriptionMock };
    });
    parseSyntaxMock = jest.fn();
    sqlParserRepository.getSyntaxParser.mockImplementation(() =>
      Promise.resolve({ parseSyntax: parseSyntaxMock })
    );

    parseSqlMock = jest.fn();
    sqlParserRepository.getAutocompleteParser.mockImplementation(() =>
      Promise.resolve({ parseSql: parseSqlMock })
    );

    // Reset mocks before each test
    huePubSub.subscribe.mockClear();
    sqlParserRepository.getSyntaxParser.mockClear();
    parseSyntaxMock.mockClear();
  });

  it('subscribes to "sql.error.missing.name" and updates the hasIncorrectSql accordingly', async () => {
    huePubSub.subscribe.mockImplementation((eventName, callback) => {
      // Mock that there is a publish event
      act(() => {
        callback(true);
      });

      return { remove: removeSubscriptionMock };
    });

    const { result } = renderHook(() => useParser(sqlExecutableMock));
    await waitFor(() => {
      expect(result.current.hasIncorrectSql).toBeTruthy();
    });

    expect(huePubSub.subscribe).toHaveBeenCalledWith(
      'sql.error.missing.name',
      expect.any(Function)
    );
  });

  it('subscribes to "sql.error.missing.name" on mount', async () => {
    const { result } = renderHook(() => useParser(sqlExecutableMock));

    expect(huePubSub.subscribe).toHaveBeenCalledWith(
      'sql.error.missing.name',
      expect.any(Function)
    );

    expect(result.current.sqlDialect).not.toBe('');
  });

  it('removes subscription to "sql.error.missing.name" on unmount', async () => {
    const { unmount } = renderHook(() => useParser(sqlExecutableMock));
    expect(removeSubscriptionMock).not.toHaveBeenCalled();
    unmount();
    expect(removeSubscriptionMock).toHaveBeenCalled();
  });

  it('should return the sqlDialect directly on first render', async () => {
    const { result } = renderHook(() => useParser(sqlExecutableMock));
    expect(result.current.sqlDialect).toBe('hive');
  });

  it('should load and return the syntaxParser based on dialect', async () => {
    const { result, rerender } = renderHook(() => useParser(sqlExecutableMock));

    // First render asynchronously loads parser
    await waitFor(() => {
      expect(result.current.syntaxParser).toBeUndefined();
    });

    rerender();
    expect(result.current.sqlDialect).toBe('hive');
    expect(result.current.syntaxParser.parseSyntax).toBe(parseSyntaxMock);
    expect(sqlParserRepository.getSyntaxParser).toHaveBeenCalledWith('hive');
  });

  it('should load and return the autocompleteParser based on dialect', async () => {
    const { result, rerender } = renderHook(() => useParser(sqlExecutableMock));

    // First render asynchronously loads parser
    await waitFor(() => {
      expect(result.current.autocompleteParser).toBeUndefined();
    });

    rerender();
    expect(result.current.sqlDialect).toBe('hive');
    expect(result.current.autocompleteParser.parseSql).toBe(parseSqlMock);
    expect(sqlParserRepository.getAutocompleteParser).toHaveBeenCalledWith('hive');
  });

  it('should return hasIncorrectSql based on syntax parser and SQL statement', async () => {
    parseSyntaxMock.mockImplementation(() => ({ error: 'error' }));
    sqlParserRepository.getSyntaxParser.mockImplementation(() =>
      Promise.resolve({
        parseSyntax: parseSyntaxMock
      })
    );
    const { result, rerender } = renderHook(() => useParser(sqlExecutableMock));

    // First render asynchronously loads parser, but it then sets the error
    // which causes a state update so we can just wait for the result
    await waitFor(() => {
      expect(result.current.hasIncorrectSql).toBeTruthy();
      expect(parseSyntaxMock).toHaveBeenCalledWith('', VALID_SQL);
    });

    // Simulate that the dialect inside the SqlExecutable have changed
    sqlExecutableMock.executor.connector = () => ({ id: 'test', dialect: 'new-dialect' });

    // Simulate a new parser (retrieved from the repository) that does not return an error
    // in the parseSyntax function for the SQL statement SELECT * FROM customers'
    const modifiedParseSyntaxMock = jest
      .fn()
      .mockImplementation((...args) => (args[1] === VALID_SQL ? undefined : { error: 'error' }));

    sqlParserRepository.getSyntaxParser.mockImplementation(() =>
      Promise.resolve({ parseSyntax: modifiedParseSyntaxMock })
    );

    rerender();

    await waitFor(() => {
      expect(sqlParserRepository.getSyntaxParser).toBeCalledWith('new-dialect');
      expect(result.current.hasIncorrectSql).toBeFalsy();
      expect(parseSyntaxMock).toHaveBeenCalledWith('', VALID_SQL);
    });

    // Simulate that the SQL statement inside the SqlExecutable have changed
    // into something that will return an error in the parseSyntax function
    sqlExecutableMock.parsedStatement = { statement: 'SELECT *' };

    rerender();

    await waitFor(() => {
      expect(result.current.hasIncorrectSql).toBeTruthy();
      expect(modifiedParseSyntaxMock).toHaveBeenCalledWith('', 'SELECT *');
    });
  });
});

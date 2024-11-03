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

import Executor from '../apps/editor/execution/executor';
import { generativeFunctionFactory } from './apiAIHelper';
import * as utils from '../api/utils';

jest.mock('../api/utils', () => ({
  post: jest.fn()
}));

jest.mock('../apps/editor/execution/executor');

// Mock to get all the tables
const dbName = 'mockDB';
const ALL_TABLES = ['mockTable1', 'mockTable2', 'mockTable3'];
jest.mock('../catalog/dataCatalog', () => ({
  getEntry: jest.fn().mockReturnValue({
    getChildren: jest.fn().mockReturnValue(ALL_TABLES.map(name => ({ name })))
  })
}));

jest.mock('../config/hueConfig', () => ({
  getLastKnownConfig: jest.fn()
}));

jest.mock('./HueError');

jest.mock('../api/utils', () => ({
  post: jest.fn()
}));

const checkThatTablesAreFiltered = ({
  postMock,
  expectedFilterInput,
  onStatusChange
}: {
  postMock: jest.Mock;
  expectedFilterInput: string;
  onStatusChange: jest.Mock;
}) => {
  const firstApiCall = postMock.mock.calls[0];
  const firstApiCallUrl = firstApiCall[0];
  const apiCallData = firstApiCall[1];
  if (expectedFilterInput) {
    expect(apiCallData.input.trim()).toEqual(expectedFilterInput.trim());
  }

  expect(firstApiCallUrl).toContain('ai/dbs');
  const tableNames = apiCallData.dbs[0].tables;
  expect(tableNames).toEqual(ALL_TABLES);
  expect(tableNames.length).toEqual(3);

  const secondApiCall = postMock.mock.calls[1];
  const secondApiCallUrl = secondApiCall[0];
  const tablesPassedToLLM = secondApiCall[1].metadata.tables;
  expect(secondApiCallUrl).toContain('ai/sql');
  expect(tablesPassedToLLM.length).toBe(2);

  expect(onStatusChange).toHaveBeenCalledWith('Retrieving all table names');
  expect(onStatusChange).toHaveBeenCalledWith('Filtering relevant tables');
  expect(onStatusChange).toHaveBeenCalledWith('Retrieving table metadata');
};

describe('GenerativeFunctionFactory', () => {
  const postMock = utils.post as jest.Mock;
  const createMockExecutor = (mock: unknown): Executor => mock as Executor;
  const mockExecutor = createMockExecutor({
    connector: () => ({ id: 'test', dialect: 'hive' }),
    compute: () => ({ id: 'test' }),
    namespace: () => ({ id: 'test' }),
    defaultLimit: () => 1000,
    toJs: () => ({})
  });

  const onStatusChange = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();

    postMock.mockImplementation((url: string) => {
      if (url.includes('ai/dbs')) {
        return Promise.resolve({
          dbs: [
            {
              name: dbName,
              tables: ALL_TABLES.slice(0, 2)
            }
          ]
        });
      } else if (url.includes('ai/sql')) {
        return Promise.resolve({
          sql: 'mocked SQL query',
          explanation: 'mocked explanation'
        });
      }
    });
  });

  describe('generateOptimizedSql', () => {
    it('should retrive and filter out relevant tables based on existing SQL before LLM call', async () => {
      const { generateOptimizedSql } = generativeFunctionFactory();
      await generateOptimizedSql({
        statement: 'SELECT * FROM table',
        databaseName: 'db',
        executor: mockExecutor,
        dialect: 'hive',
        onStatusChange
      });

      checkThatTablesAreFiltered({
        postMock,
        expectedFilterInput: 'SELECT * FROM table',
        onStatusChange
      });
    });

    it('should call the API with the correct task and dialect', async () => {
      const { generateOptimizedSql } = generativeFunctionFactory();
      await generateOptimizedSql({
        statement: 'SELECT * FROM table',
        databaseName: 'db',
        executor: mockExecutor,
        dialect: 'hive',
        onStatusChange
      });

      const llmApiCall = postMock.mock.calls[1];
      const llmApiCallUrl = llmApiCall[0];
      const llmApiCallData = llmApiCall[1];
      expect(llmApiCallUrl).toContain('ai/sql');
      expect(llmApiCallData.dialect).toEqual('hive');
      expect(llmApiCallData.task).toEqual('optimize');
    });

    it('should return the new sql and the explanation', async () => {
      const { generateOptimizedSql } = generativeFunctionFactory();
      const result = await generateOptimizedSql({
        statement: 'SELECT * FROM table',
        databaseName: 'db',
        executor: mockExecutor,
        dialect: 'hive',
        onStatusChange
      });

      expect(result).toEqual({ explanation: 'mocked explanation', sql: 'mocked SQL query' });
    });

    it('should update status', async () => {
      const { generateOptimizedSql } = generativeFunctionFactory();
      await generateOptimizedSql({
        statement: 'SELECT * FROM table',
        databaseName: 'db',
        executor: mockExecutor,
        dialect: 'hive',
        onStatusChange
      });
      expect(onStatusChange).toHaveBeenCalledWith('Optimizing SQL query');
    });

    it('should throw proper error msg', async () => {
      const originalConsoleError = console.error;
      console.error = jest.fn();

      postMock.mockImplementation((url: string) => {
        if (url.includes('ai/dbs')) {
          return Promise.resolve({
            dbs: [
              {
                name: dbName,
                tables: ALL_TABLES.slice(0, 2)
              }
            ]
          });
        } else if (url.includes('ai/sql')) {
          throw Error('error');
        }
      });
      const { generateOptimizedSql } = generativeFunctionFactory();

      try {
        await generateOptimizedSql({
          statement: 'SELECT * FROM table',
          databaseName: 'db',
          executor: mockExecutor,
          dialect: 'hive',
          onStatusChange
        });
        expect(true).toBe(false); // force fail
      } catch (error) {
        expect(error.message).toBe('Call to AI to optimize SQL query failed');
      } finally {
        console.error = originalConsoleError;
      }
    });
  });

  describe('generateSQLfromNQL', () => {
    it('should retrive and filter out relevant tables based on user prompt before LLM call', async () => {
      const { generateSQLfromNQL } = generativeFunctionFactory();
      await generateSQLfromNQL({
        nql: 'nl prompt mock',
        databaseName: 'db',
        executor: mockExecutor,
        dialect: 'hive',
        onStatusChange
      });

      checkThatTablesAreFiltered({
        postMock,
        expectedFilterInput: 'nl prompt mock',
        onStatusChange
      });
    });

    it('should call the API with the correct task and dialect', async () => {
      const { generateSQLfromNQL } = generativeFunctionFactory();
      await generateSQLfromNQL({
        nql: 'nl mock prompt',
        databaseName: 'db',
        executor: mockExecutor,
        dialect: 'hive',
        onStatusChange
      });

      const llmApiCall = postMock.mock.calls[1];
      const llmApiCallUrl = llmApiCall[0];
      const llmApiCallData = llmApiCall[1];
      expect(llmApiCallUrl).toContain('ai/sql');
      expect(llmApiCallData.dialect).toEqual('hive');
      expect(llmApiCallData.task).toEqual('generate');
    });

    it('should return the new sql, explanation and tableColumnsMetadata', async () => {
      const { generateSQLfromNQL } = generativeFunctionFactory();
      const result = await generateSQLfromNQL({
        nql: 'nl mock prompt',
        databaseName: 'db',
        executor: mockExecutor,
        dialect: 'hive',
        onStatusChange
      });

      expect(result).toEqual({
        explanation: 'mocked explanation',
        sql: 'mocked SQL query',
        tableColumnsMetadata: expect.any(Array)
      });
      expect(result.tableColumnsMetadata?.length).toBe(2);
      const exampleTableObj = result.tableColumnsMetadata && result.tableColumnsMetadata[0];
      expect(exampleTableObj).toEqual(
        expect.objectContaining({
          columns: expect.any(Array),
          dbName: 'db',
          name: 'mockTable1',
          partitions: undefined
        })
      );
    });

    it('should update status', async () => {
      const { generateSQLfromNQL } = generativeFunctionFactory();
      await generateSQLfromNQL({
        nql: 'nl mock prompt',
        databaseName: 'db',
        executor: mockExecutor,
        dialect: 'hive',
        onStatusChange
      });
      expect(onStatusChange).toHaveBeenCalledWith('Generating SQL query');
    });

    it('should throw proper error msg', async () => {
      const originalConsoleError = console.error;
      console.error = jest.fn();

      postMock.mockImplementation((url: string) => {
        if (url.includes('ai/dbs')) {
          return Promise.resolve({
            dbs: [
              {
                name: dbName,
                tables: ALL_TABLES.slice(0, 2)
              }
            ]
          });
        } else if (url.includes('ai/sql')) {
          throw Error('error');
        }
      });
      const { generateSQLfromNQL } = generativeFunctionFactory();

      try {
        await generateSQLfromNQL({
          nql: 'nl mock prompt',
          databaseName: 'db',
          executor: mockExecutor,
          dialect: 'hive',
          onStatusChange
        });
        expect(true).toBe(false); // force fail
      } catch (error) {
        expect(error.message.trim()).toBe('Call to AI to generate SQL query failed');
      } finally {
        console.error = originalConsoleError;
      }
    });
  });

  describe('generateEditedSQLfromNQL', () => {
    it('should retrive and filter out relevant tables based on user prompt before LLM call', async () => {
      const { generateEditedSQLfromNQL } = generativeFunctionFactory();
      await generateEditedSQLfromNQL({
        nql: 'nl prompt mock',
        sql: 'SELECT * FROM table',
        databaseName: 'db',
        executor: mockExecutor,
        dialect: 'hive',
        onStatusChange
      });

      checkThatTablesAreFiltered({
        postMock,
        expectedFilterInput: 'nl prompt mock',
        onStatusChange
      });
    });

    it('should call the API with the correct task and dialect', async () => {
      const { generateEditedSQLfromNQL } = generativeFunctionFactory();
      await generateEditedSQLfromNQL({
        nql: 'nl prompt mock',
        sql: 'SELECT * FROM table',
        databaseName: 'db',
        executor: mockExecutor,
        dialect: 'hive',
        onStatusChange
      });

      const llmApiCall = postMock.mock.calls[1];
      const llmApiCallUrl = llmApiCall[0];
      const llmApiCallData = llmApiCall[1];
      expect(llmApiCallUrl).toContain('ai/sql');
      expect(llmApiCallData.dialect).toEqual('hive');
      expect(llmApiCallData.task).toEqual('edit');
    });

    it('should return the new sql, explanation and tableColumnsMetadata', async () => {
      const { generateEditedSQLfromNQL } = generativeFunctionFactory();
      const result = await generateEditedSQLfromNQL({
        nql: 'nl prompt mock',
        sql: 'SELECT * FROM table',
        databaseName: 'db',
        executor: mockExecutor,
        dialect: 'hive',
        onStatusChange
      });

      expect(result).toEqual({
        explanation: 'mocked explanation',
        sql: 'mocked SQL query',
        tableColumnsMetadata: expect.any(Array)
      });
      expect(result.tableColumnsMetadata?.length).toBe(2);
      const exampleTableObj = result.tableColumnsMetadata && result.tableColumnsMetadata[0];
      expect(exampleTableObj).toEqual(
        expect.objectContaining({
          columns: expect.any(Array),
          dbName: 'db',
          name: 'mockTable1',
          partitions: undefined
        })
      );
    });

    it('should update status', async () => {
      const { generateEditedSQLfromNQL } = generativeFunctionFactory();
      await generateEditedSQLfromNQL({
        nql: 'nl prompt mock',
        sql: 'SELECT * FROM table',
        databaseName: 'db',
        executor: mockExecutor,
        dialect: 'hive',
        onStatusChange
      });
      expect(onStatusChange).toHaveBeenCalledWith('Generating SQL query');
    });

    it('should throw proper error msg', async () => {
      const originalConsoleError = console.error;
      console.error = jest.fn();

      postMock.mockImplementation((url: string) => {
        if (url.includes('ai/dbs')) {
          return Promise.resolve({
            dbs: [
              {
                name: dbName,
                tables: ALL_TABLES.slice(0, 2)
              }
            ]
          });
        } else if (url.includes('ai/sql')) {
          throw Error('error');
        }
      });
      const { generateEditedSQLfromNQL } = generativeFunctionFactory();

      try {
        await generateEditedSQLfromNQL({
          nql: 'nl prompt mock',
          sql: 'SELECT * FROM table',
          databaseName: 'db',
          executor: mockExecutor,
          dialect: 'hive',
          onStatusChange
        });
        expect(true).toBe(false); // force fail
      } catch (error) {
        expect(error.message.trim()).toBe('Call to AI to edit SQL query failed');
      } finally {
        console.error = originalConsoleError;
      }
    });
  });

  describe('generateCorrectedSql', () => {
    it('should retrive and filter out relevant tables based on existing SQL before LLM call', async () => {
      const { generateCorrectedSql } = generativeFunctionFactory();
      await generateCorrectedSql({
        statement: 'SELECT * FROM table',
        databaseName: 'db',
        executor: mockExecutor,
        dialect: 'hive',
        onStatusChange
      });

      checkThatTablesAreFiltered({
        postMock,
        expectedFilterInput: 'SELECT * FROM table',
        onStatusChange
      });
    });

    it('should call the API with the correct task and dialect', async () => {
      const { generateCorrectedSql } = generativeFunctionFactory();
      await generateCorrectedSql({
        statement: 'SELECT * FROM table',
        databaseName: 'db',
        executor: mockExecutor,
        dialect: 'hive',
        onStatusChange
      });

      const llmApiCall = postMock.mock.calls[1];
      const llmApiCallUrl = llmApiCall[0];
      const llmApiCallData = llmApiCall[1];
      expect(llmApiCallUrl).toContain('ai/sql');
      expect(llmApiCallData.dialect).toEqual('hive');
      expect(llmApiCallData.task).toEqual('fix');
    });

    it('should return the new sql and the explanation', async () => {
      const { generateCorrectedSql } = generativeFunctionFactory();
      const result = await generateCorrectedSql({
        statement: 'SELECT * FROM table',
        databaseName: 'db',
        executor: mockExecutor,
        dialect: 'hive',
        onStatusChange
      });

      expect(result).toEqual({ explanation: 'mocked explanation', sql: 'mocked SQL query' });
    });

    it('should update status', async () => {
      const { generateCorrectedSql } = generativeFunctionFactory();
      await generateCorrectedSql({
        statement: 'SELECT * FROM table',
        databaseName: 'db',
        executor: mockExecutor,
        dialect: 'hive',
        onStatusChange
      });
      expect(onStatusChange).toHaveBeenCalledWith('Generating corrected SQL query');
    });

    it('should throw proper error msg', async () => {
      const originalConsoleError = console.error;
      console.error = jest.fn();

      postMock.mockImplementation((url: string) => {
        if (url.includes('ai/dbs')) {
          return Promise.resolve({
            dbs: [
              {
                name: dbName,
                tables: ALL_TABLES.slice(0, 2)
              }
            ]
          });
        } else if (url.includes('ai/sql')) {
          throw Error('error');
        }
      });
      const { generateCorrectedSql } = generativeFunctionFactory();

      try {
        await generateCorrectedSql({
          statement: 'SELECT * FROM table',
          databaseName: 'db',
          executor: mockExecutor,
          dialect: 'hive',
          onStatusChange
        });
        expect(true).toBe(false); // force fail
      } catch (error) {
        expect(error.message).toBe('Call to AI to fix SQL query failed');
      } finally {
        console.error = originalConsoleError;
      }
    });
  });

  describe('generateExplanation', () => {
    it('should retrive and filter out relevant tables based on existing SQL before LLM call', async () => {
      const { generateExplanation } = generativeFunctionFactory();
      await generateExplanation({
        statement: 'SELECT * FROM table',
        databaseName: 'db',
        executor: mockExecutor,
        dialect: 'hive',
        onStatusChange
      });

      checkThatTablesAreFiltered({
        postMock,
        expectedFilterInput: 'SELECT * FROM table',
        onStatusChange
      });
    });

    it('should call the API with the correct task and dialect', async () => {
      const { generateExplanation } = generativeFunctionFactory();
      await generateExplanation({
        statement: 'SELECT * FROM table',
        databaseName: 'db',
        executor: mockExecutor,
        dialect: 'hive',
        onStatusChange
      });

      const llmApiCall = postMock.mock.calls[1];
      const llmApiCallUrl = llmApiCall[0];
      const llmApiCallData = llmApiCall[1];
      expect(llmApiCallUrl).toContain('ai/sql');
      expect(llmApiCallData.dialect).toEqual('hive');
      expect(llmApiCallData.task).toEqual('summarize');
    });

    it('should return the new sql and the explanation', async () => {
      const { generateExplanation } = generativeFunctionFactory();
      const result = await generateExplanation({
        statement: 'SELECT * FROM table',
        databaseName: 'db',
        executor: mockExecutor,
        dialect: 'hive',
        onStatusChange
      });

      expect(result).toEqual({ explanation: 'mocked explanation', sql: 'mocked SQL query' });
    });

    it('should update status', async () => {
      const { generateExplanation } = generativeFunctionFactory();
      await generateExplanation({
        statement: 'SELECT * FROM table',
        databaseName: 'db',
        executor: mockExecutor,
        dialect: 'hive',
        onStatusChange
      });
      expect(onStatusChange).toHaveBeenCalledWith('Generating explanation');
    });

    it('should throw proper error msg', async () => {
      const originalConsoleError = console.error;
      console.error = jest.fn();

      postMock.mockImplementation((url: string) => {
        if (url.includes('ai/dbs')) {
          return Promise.resolve({
            dbs: [
              {
                name: dbName,
                tables: ALL_TABLES.slice(0, 2)
              }
            ]
          });
        } else if (url.includes('ai/sql')) {
          throw Error('error');
        }
      });
      const { generateExplanation } = generativeFunctionFactory();

      try {
        await generateExplanation({
          statement: 'SELECT * FROM table',
          databaseName: 'db',
          executor: mockExecutor,
          dialect: 'hive',
          onStatusChange
        });
        expect(true).toBe(false); // force fail
      } catch (error) {
        expect(error.message).toBe('Call to AI to explain SQL query failed');
      } finally {
        console.error = originalConsoleError;
      }
    });
  });

  describe('generateCommentedSql', () => {
    it('should call the API with the correct task and dialect', async () => {
      const { generateCommentedSql } = generativeFunctionFactory();
      await generateCommentedSql({
        statement: 'SELECT * FROM table',
        dialect: 'hive',
        onStatusChange
      });

      const llmApiCall = postMock.mock.calls[0];
      const llmApiCallUrl = llmApiCall[0];
      const llmApiCallData = llmApiCall[1];
      expect(llmApiCallUrl).toContain('ai/sql');
      expect(llmApiCallData.dialect).toEqual('hive');
      expect(llmApiCallData.task).toEqual('comment');
    });

    it('should return the new sql', async () => {
      const { generateCommentedSql } = generativeFunctionFactory();
      const result = await generateCommentedSql({
        statement: 'SELECT * FROM table',
        dialect: 'hive',
        onStatusChange
      });

      expect(result.sql).toEqual('mocked SQL query');
    });

    it('should update status', async () => {
      const { generateCommentedSql } = generativeFunctionFactory();
      await generateCommentedSql({
        statement: 'SELECT * FROM table',
        dialect: 'hive',
        onStatusChange
      });
      expect(onStatusChange).toHaveBeenCalledWith('Generating comments for SQL query');
    });

    it('should throw proper error msg', async () => {
      const originalConsoleError = console.error;
      console.error = jest.fn();

      postMock.mockImplementation((url: string) => {
        if (url.includes('ai/dbs')) {
          return Promise.resolve({
            dbs: [
              {
                name: dbName,
                tables: ALL_TABLES.slice(0, 2)
              }
            ]
          });
        } else if (url.includes('ai/sql')) {
          throw Error('error');
        }
      });
      const { generateCommentedSql } = generativeFunctionFactory();

      try {
        await generateCommentedSql({
          statement: 'SELECT * FROM table',
          dialect: 'hive',
          onStatusChange
        });
        expect(true).toBe(false); // force fail
      } catch (error) {
        expect(error.message).toBe('Call to AI to comment SQL query failed');
      } finally {
        console.error = originalConsoleError;
      }
    });
  });
});

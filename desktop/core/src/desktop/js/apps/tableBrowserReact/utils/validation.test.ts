// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// See the NOTICE file distributed with this work for additional information
// regarding copyright ownership. Cloudera, Inc. licenses this file to you under
// the Apache License, Version 2.0 (the "License"); you may not use this file
// except in compliance with the License. You may obtain a copy of the License at
// http://www.apache.org/licenses/LICENSE-2.0
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
// WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
// License for the specific language governing permissions and limitations under
// the License.

import {
  validateDatabaseName,
  validateTableName,
  validateColumnName,
  isValidDatabaseName,
  isValidTableName,
  isValidColumnName
} from './validation';

describe('validateDatabaseName', () => {
  describe('valid database names', () => {
    const validNames = [
      'test',
      'test_db',
      'test123',
      'db1',
      'my_database',
      'MyDatabase',
      'TESTDB',
      'a',
      '1',
      '123abc',
      'abc123def',
      'test_123_abc'
    ];

    test.each(validNames)('should accept valid name: %s', name => {
      const result = validateDatabaseName(name);
      expect(result.isValid).toBe(true);
      expect(result.error).toBeUndefined();
    });
  });

  describe('invalid database names', () => {
    const invalidCases = [
      { name: '', expectedError: 'Database name is required' },
      { name: '   ', expectedError: 'Database name cannot have leading or trailing spaces' },
      { name: ' test', expectedError: 'Database name cannot have leading or trailing spaces' },
      { name: 'test ', expectedError: 'Database name cannot have leading or trailing spaces' },
      {
        name: '_test',
        expectedError:
          'Database name must start with a letter or number and contain only letters, numbers, and underscores'
      },
      {
        name: 'test-db',
        expectedError:
          'Database name must start with a letter or number and contain only letters, numbers, and underscores'
      },
      {
        name: 'test.db',
        expectedError:
          'Database name must start with a letter or number and contain only letters, numbers, and underscores'
      },
      {
        name: 'test db',
        expectedError:
          'Database name must start with a letter or number and contain only letters, numbers, and underscores'
      },
      {
        name: 'test@db',
        expectedError:
          'Database name must start with a letter or number and contain only letters, numbers, and underscores'
      },
      {
        name: 'test#db',
        expectedError:
          'Database name must start with a letter or number and contain only letters, numbers, and underscores'
      },
      {
        name: 'test$db',
        expectedError:
          'Database name must start with a letter or number and contain only letters, numbers, and underscores'
      },
      {
        name: 'test%db',
        expectedError:
          'Database name must start with a letter or number and contain only letters, numbers, and underscores'
      }
    ];

    test.each(invalidCases)('should reject invalid name: $name', ({ name, expectedError }) => {
      const result = validateDatabaseName(name);
      expect(result.isValid).toBe(false);
      expect(result.error).toBe(expectedError);
    });
  });

  describe('reserved keywords', () => {
    const reservedWords = ['SELECT', 'FROM', 'WHERE', 'DATABASE', 'TABLE', 'CREATE', 'DROP'];

    test.each(reservedWords)('should reject reserved keyword: %s', keyword => {
      const result = validateDatabaseName(keyword);
      expect(result.isValid).toBe(false);
      expect(result.error).toBe('Database name cannot be a reserved SQL keyword');
    });

    test.each(reservedWords)('should reject reserved keyword (lowercase): %s', keyword => {
      const result = validateDatabaseName(keyword.toLowerCase());
      expect(result.isValid).toBe(false);
      expect(result.error).toBe('Database name cannot be a reserved SQL keyword');
    });
  });

  describe('length validation', () => {
    test('should accept names up to 128 characters', () => {
      const longName = 'a'.repeat(128);
      const result = validateDatabaseName(longName);
      expect(result.isValid).toBe(true);
    });

    test('should reject names longer than 128 characters', () => {
      const tooLongName = 'a'.repeat(129);
      const result = validateDatabaseName(tooLongName);
      expect(result.isValid).toBe(false);
      expect(result.error).toBe('Database name must be 128 characters or fewer');
    });
  });

  describe('dialect-specific validation', () => {
    test('should use hive reserved words when dialect is specified', () => {
      const result = validateDatabaseName('AUTHORIZATION', 'hive');
      expect(result.isValid).toBe(false);
      expect(result.error).toBe('Database name cannot be a reserved SQL keyword');
    });

    test('should use impala reserved words when dialect is specified', () => {
      const result = validateDatabaseName('ANALYTIC', 'impala');
      expect(result.isValid).toBe(false);
      expect(result.error).toBe('Database name cannot be a reserved SQL keyword');
    });
  });
});

describe('validateTableName', () => {
  describe('valid table names', () => {
    const validNames = [
      'test',
      'test_table',
      'test123',
      'table1',
      'my_table',
      'MyTable',
      'TESTTBL',
      'a',
      '1',
      'db.tbl',
      'my_db.my_table',
      'test123.table456',
      'database_name.table_name'
    ];

    test.each(validNames)('should accept valid name: %s', name => {
      const result = validateTableName(name);
      expect(result.isValid).toBe(true);
      expect(result.error).toBeUndefined();
    });
  });

  describe('invalid table names', () => {
    const invalidCases = [
      { name: '', expectedError: 'Table name is required' },
      { name: '   ', expectedError: 'Table name cannot have leading or trailing spaces' },
      { name: ' test', expectedError: 'Table name cannot have leading or trailing spaces' },
      { name: 'test ', expectedError: 'Table name cannot have leading or trailing spaces' },
      {
        name: '_test',
        expectedError:
          'Table name must start with a letter or number and contain only letters, numbers, and underscores. Database prefix format: database.table'
      },
      {
        name: 'test-table',
        expectedError:
          'Table name must start with a letter or number and contain only letters, numbers, and underscores. Database prefix format: database.table'
      },
      {
        name: 'test table',
        expectedError:
          'Table name must start with a letter or number and contain only letters, numbers, and underscores. Database prefix format: database.table'
      },
      {
        name: 'db._table',
        expectedError:
          'Table name must start with a letter or number and contain only letters, numbers, and underscores. Database prefix format: database.table'
      },
      {
        name: '_db.table',
        expectedError:
          'Table name must start with a letter or number and contain only letters, numbers, and underscores. Database prefix format: database.table'
      }
    ];

    test.each(invalidCases)('should reject invalid name: $name', ({ name, expectedError }) => {
      const result = validateTableName(name);
      expect(result.isValid).toBe(false);
      expect(result.error).toBe(expectedError);
    });
  });

  describe('reserved keywords in table names', () => {
    test('should reject reserved keyword as table name', () => {
      const result = validateTableName('SELECT');
      expect(result.isValid).toBe(false);
      expect(result.error).toBe(
        '"SELECT" is a reserved SQL keyword and cannot be used in table names'
      );
    });

    test('should reject reserved keyword in database.table format', () => {
      const result = validateTableName('SELECT.table');
      expect(result.isValid).toBe(false);
      expect(result.error).toBe(
        '"SELECT" is a reserved SQL keyword and cannot be used in table names'
      );
    });

    test('should reject reserved keyword in table part of database.table format', () => {
      const result = validateTableName('mydb.SELECT');
      expect(result.isValid).toBe(false);
      expect(result.error).toBe(
        '"SELECT" is a reserved SQL keyword and cannot be used in table names'
      );
    });
  });
});

describe('validateColumnName', () => {
  describe('valid column names', () => {
    const validNames = [
      'test',
      'test_column',
      'test123',
      'col1',
      'my_column',
      'Column',
      'TEST',
      'a',
      '1',
      '123abc',
      'abc123def',
      'test_123_abc'
    ];

    test.each(validNames)('should accept valid name: %s', name => {
      const result = validateColumnName(name);
      expect(result.isValid).toBe(true);
      expect(result.error).toBeUndefined();
    });
  });

  describe('invalid column names', () => {
    const invalidCases = [
      { name: '', expectedError: 'Column name is required' },
      { name: '   ', expectedError: 'Column name cannot have leading or trailing spaces' },
      { name: ' test', expectedError: 'Column name cannot have leading or trailing spaces' },
      { name: 'test ', expectedError: 'Column name cannot have leading or trailing spaces' },
      {
        name: '_test',
        expectedError:
          'Column name must start with a letter or number and contain only letters, numbers, and underscores'
      },
      {
        name: 'test-col',
        expectedError:
          'Column name must start with a letter or number and contain only letters, numbers, and underscores'
      },
      {
        name: 'test.col',
        expectedError:
          'Column name must start with a letter or number and contain only letters, numbers, and underscores'
      },
      {
        name: 'test col',
        expectedError:
          'Column name must start with a letter or number and contain only letters, numbers, and underscores'
      }
    ];

    test.each(invalidCases)('should reject invalid name: $name', ({ name, expectedError }) => {
      const result = validateColumnName(name);
      expect(result.isValid).toBe(false);
      expect(result.error).toBe(expectedError);
    });
  });
});

describe('convenience functions', () => {
  describe('isValidDatabaseName', () => {
    test('should return true for valid names', () => {
      expect(isValidDatabaseName('test_db')).toBe(true);
    });

    test('should return false for invalid names', () => {
      expect(isValidDatabaseName('_invalid')).toBe(false);
      expect(isValidDatabaseName('SELECT')).toBe(false);
    });
  });

  describe('isValidTableName', () => {
    test('should return true for valid names', () => {
      expect(isValidTableName('test_table')).toBe(true);
      expect(isValidTableName('db.tbl')).toBe(true);
    });

    test('should return false for invalid names', () => {
      expect(isValidTableName('_invalid')).toBe(false);
      expect(isValidTableName('SELECT')).toBe(false);
    });
  });

  describe('isValidColumnName', () => {
    test('should return true for valid names', () => {
      expect(isValidColumnName('test_column')).toBe(true);
    });

    test('should return false for invalid names', () => {
      expect(isValidColumnName('_invalid')).toBe(false);
      expect(isValidColumnName('SELECT')).toBe(false);
    });
  });
});

describe('edge cases', () => {
  test('should handle null and undefined inputs', () => {
    expect(validateDatabaseName(null as any).isValid).toBe(false);
    expect(validateDatabaseName(undefined as any).isValid).toBe(false);
    expect(validateTableName(null as any).isValid).toBe(false);
    expect(validateColumnName(null as any).isValid).toBe(false);
  });

  test('should handle non-string inputs', () => {
    expect(validateDatabaseName(123 as any).isValid).toBe(false);
    expect(validateTableName({} as any).isValid).toBe(false);
    expect(validateColumnName([] as any).isValid).toBe(false);
  });
});

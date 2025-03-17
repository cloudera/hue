// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import { convertKeysToCamelCase, toCamelCase, words } from './changeCasing';

describe('words', () => {
  it('should match words in snake_case string', () => {
    const input = 'snake_case_example';
    const result = words(input);
    expect(result).toEqual(['snake', 'case', 'example']);
  });

  it('should match words in camelCase string', () => {
    const input = 'camelCaseExample';
    const result = words(input);
    expect(result).toEqual(['camel', 'Case', 'Example']);
  });

  it('should match words in PascalCase string', () => {
    const input = 'PascalCaseString';
    const result = words(input);
    expect(result).toEqual(['Pascal', 'Case', 'String']);
  });

  it('should match a string with numbers and words', () => {
    const input = 'someText123with456numbers';
    const result = words(input);
    expect(result).toEqual(['some', 'Text', '123', 'with', '456', 'numbers']);
  });

  it('should return an empty array for an empty string', () => {
    const input = '';
    const result = words(input);
    expect(result).toEqual([]);
  });

  it('should match numbers', () => {
    const input = '1234test567';
    const result = words(input);
    expect(result).toEqual(['1234', 'test', '567']);
  });

  it('should match words in a string with multiple underscores', () => {
    const input = 'multiple__underscores_test';
    const result = words(input);
    expect(result).toEqual(['multiple', 'underscores', 'test']);
  });

  it('should match a string with numbers, underscores, and mixed case', () => {
    const input = 'test_123Number_caseTest';
    const result = words(input);
    expect(result).toEqual(['test', '123', 'Number', 'case', 'Test']);
  });

  it('should handle a string with only numbers', () => {
    const input = '12345';
    const result = words(input);
    expect(result).toEqual(['12345']);
  });

  it('should handle a string with special characters', () => {
    const input = 'word@123#test!';
    const result = words(input);
    expect(result).toEqual(['word', '123', 'test']);
  });
});

describe('toCamelCase', () => {
  it('should convert snake_case to camelCase for simple strings', () => {
    expect(toCamelCase('snake_case_key')).toBe('snakeCaseKey');
  });

  it('should handle strings with multiple underscores', () => {
    expect(toCamelCase('this_is_a_test')).toBe('thisIsATest');
  });

  it('should handle strings with leading underscores', () => {
    expect(toCamelCase('_leading_underscore')).toBe('leadingUnderscore');
  });

  it('should handle strings with trailing underscores', () => {
    expect(toCamelCase('trailing_underscore_')).toBe('trailingUnderscore');
  });

  it('should handle strings with multiple leading and trailing underscores', () => {
    expect(toCamelCase('__trailing__underscore__')).toBe('trailingUnderscore');
  });

  it('should return the same string if there are no underscores', () => {
    expect(toCamelCase('alreadyCamelCase')).toBe('alreadyCamelCase');
  });

  it('should handle empty strings correctly', () => {
    expect(toCamelCase('')).toBe('');
  });

  it('should not modify uppercase letters after the first one', () => {
    expect(toCamelCase('test_STRING_VALUE')).toBe('testStringValue');
  });

  it('should convert multiple underscores correctly', () => {
    expect(toCamelCase('multiple__underscores')).toBe('multipleUnderscores');
  });

  it('should handle numbers in the string', () => {
    expect(toCamelCase('snake_case_123_test')).toBe('snakeCase123Test');
  });

  it('should handle mixed-case strings', () => {
    expect(toCamelCase('MIXED_CASE_example')).toBe('mixedCaseExample');
  });
});

describe('convertKeysToCamelCase', () => {
  it('should convert a single object from snake_case to camelCase', () => {
    const input = { snake_case_key: 'value', another_snake_case: 'anotherValue' };
    const result = convertKeysToCamelCase(input);
    expect(result).toEqual({
      snakeCaseKey: 'value',
      anotherSnakeCase: 'anotherValue'
    });
  });

  it('should convert nested objects from snake_case to camelCase', () => {
    const input = {
      snake_case_key: 'value',
      nested_object: { inner_snake_case_key: 'innerValue' }
    };
    const result = convertKeysToCamelCase(input);
    expect(result).toEqual({
      snakeCaseKey: 'value',
      nestedObject: { innerSnakeCaseKey: 'innerValue' }
    });
  });

  it('should convert arrays of objects from snake_case to camelCase', () => {
    const input = [
      { snake_case_key: 'value1', another_snake_case: 'value2' },
      { third_snake_case: 'value3' }
    ];
    const result = convertKeysToCamelCase(input);
    expect(result).toEqual([
      { snakeCaseKey: 'value1', anotherSnakeCase: 'value2' },
      { thirdSnakeCase: 'value3' }
    ]);
  });

  it('should handle arrays of primitives correctly without changing them', () => {
    const input = [1, 2, 3];
    const result = convertKeysToCamelCase(input);
    expect(result).toEqual([1, 2, 3]);
  });

  it('should handle primitive values without modifying them', () => {
    const input = 'string';
    const result = convertKeysToCamelCase(input);
    expect(result).toBe('string');
  });

  it('should return null for null input', () => {
    const input = null;
    const result = convertKeysToCamelCase(input);
    expect(result).toBeNull();
  });

  it('should return an empty object if the input is an empty object', () => {
    const input = {};
    const result = convertKeysToCamelCase(input);
    expect(result).toEqual({});
  });

  it('should return an empty array if the input is an empty array', () => {
    const input = [];
    const result = convertKeysToCamelCase(input);
    expect(result).toEqual([]);
  });

  it('should convert deeply nested objects from snake_case to camelCase', () => {
    const input = {
      snake_case_key: {
        another_snake_case: {
          deeply_nested_snake_case: 'value'
        }
      }
    };
    const result = convertKeysToCamelCase(input);
    expect(result).toEqual({
      snakeCaseKey: {
        anotherSnakeCase: {
          deeplyNestedSnakeCase: 'value'
        }
      }
    });
  });
});

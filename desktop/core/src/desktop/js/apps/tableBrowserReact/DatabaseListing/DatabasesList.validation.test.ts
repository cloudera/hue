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

/**
 * Unit tests for validation logic integration in DatabasesList component
 * These tests focus on the validation logic without rendering the full component
 */

import { validateDatabaseName } from '../utils/validation';

describe('DatabasesList validation integration', () => {
  describe('validateDatabaseName with different dialects', () => {
    it('should validate with hive dialect', () => {
      const result = validateDatabaseName('test_db', 'hive');
      expect(result.isValid).toBe(true);
      expect(result.error).toBeUndefined();
    });

    it('should validate with impala dialect', () => {
      const result = validateDatabaseName('test_db', 'impala');
      expect(result.isValid).toBe(true);
      expect(result.error).toBeUndefined();
    });

    it('should default to hive when no dialect provided', () => {
      const result = validateDatabaseName('test_db');
      expect(result.isValid).toBe(true);
      expect(result.error).toBeUndefined();
    });

    it('should reject invalid names regardless of dialect', () => {
      const invalidResult = validateDatabaseName('_invalid', 'hive');
      expect(invalidResult.isValid).toBe(false);
      expect(invalidResult.error).toBe(
        'Database name must start with a letter or number and contain only letters, numbers, and underscores'
      );
    });

    it('should reject reserved keywords based on dialect', () => {
      // Test with a common reserved keyword
      const result = validateDatabaseName('SELECT', 'hive');
      expect(result.isValid).toBe(false);
      expect(result.error).toBe('Database name cannot be a reserved SQL keyword');
    });
  });

  describe('form validation scenarios', () => {
    it('should handle empty string validation', () => {
      const result = validateDatabaseName('');
      expect(result.isValid).toBe(false);
      expect(result.error).toBe('Database name is required');
    });

    it('should handle whitespace-only validation', () => {
      const result = validateDatabaseName('   ');
      expect(result.isValid).toBe(false);
      expect(result.error).toBe('Database name cannot have leading or trailing spaces');
    });

    it('should handle leading/trailing spaces', () => {
      const result = validateDatabaseName(' test_db ');
      expect(result.isValid).toBe(false);
      expect(result.error).toBe('Database name cannot have leading or trailing spaces');
    });

    it('should handle maximum length validation', () => {
      const longName = 'a'.repeat(129);
      const result = validateDatabaseName(longName);
      expect(result.isValid).toBe(false);
      expect(result.error).toBe('Database name must be 128 characters or fewer');
    });

    it('should accept names at maximum length', () => {
      const maxLengthName = 'a'.repeat(128);
      const result = validateDatabaseName(maxLengthName);
      expect(result.isValid).toBe(true);
      expect(result.error).toBeUndefined();
    });
  });

  describe('real-world database name examples', () => {
    const validExamples = [
      'production_db',
      'test_environment',
      'analytics_2024',
      'user_data',
      'reporting_v2',
      'staging',
      'dev_db',
      'warehouse',
      'logs_archive',
      'temp_storage'
    ];

    const invalidExamples = [
      '_private_db', // starts with underscore
      'test-db', // contains hyphen
      'test db', // contains space
      'test.db', // contains dot (not allowed in simple database names)
      'SELECT', // reserved keyword
      'DATABASE', // reserved keyword
      'CREATE', // reserved keyword
      'test@db', // contains special character
      'test#db', // contains special character
      'test$db' // contains special character
    ];

    test.each(validExamples)('should accept valid database name: %s', name => {
      const result = validateDatabaseName(name, 'hive');
      expect(result.isValid).toBe(true);
      expect(result.error).toBeUndefined();
    });

    test.each(invalidExamples)('should reject invalid database name: %s', name => {
      const result = validateDatabaseName(name, 'hive');
      expect(result.isValid).toBe(false);
      expect(result.error).toBeDefined();
    });
  });

  describe('form state simulation', () => {
    interface CreateForm {
      name: string;
      comment: string;
      useDefaultLocation: boolean;
      location: string;
    }

    const validateForm = (form: CreateForm, sourceType = 'hive') => {
      const nameValidation = form.name
        ? validateDatabaseName(form.name, sourceType)
        : { isValid: true };
      const isFormValid = form.name.length > 0 && nameValidation.isValid;

      return {
        nameValidation,
        isFormValid
      };
    };

    it('should validate form with empty name', () => {
      const form: CreateForm = {
        name: '',
        comment: '',
        useDefaultLocation: true,
        location: ''
      };

      const { nameValidation, isFormValid } = validateForm(form);
      expect(nameValidation.isValid).toBe(true); // Don't show error for empty initially
      expect(isFormValid).toBe(false); // But form is not valid
    });

    it('should validate form with valid name', () => {
      const form: CreateForm = {
        name: 'test_database',
        comment: 'Test database',
        useDefaultLocation: true,
        location: ''
      };

      const { nameValidation, isFormValid } = validateForm(form);
      expect(nameValidation.isValid).toBe(true);
      expect(isFormValid).toBe(true);
    });

    it('should validate form with invalid name', () => {
      const form: CreateForm = {
        name: '_invalid_db',
        comment: 'Invalid database',
        useDefaultLocation: true,
        location: ''
      };

      const { nameValidation, isFormValid } = validateForm(form);
      expect(nameValidation.isValid).toBe(false);
      expect(isFormValid).toBe(false);
    });

    it('should use correct dialect from sourceType', () => {
      const form: CreateForm = {
        name: 'test_db',
        comment: '',
        useDefaultLocation: true,
        location: ''
      };

      // Test with different source types
      const hiveResult = validateForm(form, 'hive');
      const impalaResult = validateForm(form, 'impala');
      const defaultResult = validateForm(form); // should default to hive

      expect(hiveResult.isFormValid).toBe(true);
      expect(impalaResult.isFormValid).toBe(true);
      expect(defaultResult.isFormValid).toBe(true);
    });
  });
});

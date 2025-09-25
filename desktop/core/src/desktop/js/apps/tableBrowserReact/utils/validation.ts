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

import { RESERVED_WORDS as HIVE_RESERVED_WORDS } from '../../../sql/reference/hive/reservedKeywords';
import { RESERVED_WORDS as IMPALA_RESERVED_WORDS } from '../../../sql/reference/impala/reservedKeywords';
import { RESERVED_WORDS as GENERIC_RESERVED_WORDS } from '../../../sql/reference/generic/reservedKeywords';
import { get } from '../../../api/utils';

/**
 * Backend Hive identifier regex pattern from apps/beeswax/src/beeswax/common.py
 * HIVE_IDENTIFER_REGEX = re.compile(r"(^[a-zA-Z0-9]\w*\.)?[a-zA-Z0-9]\w*$")
 *
 * This pattern allows:
 * - Optional database prefix: [a-zA-Z0-9]\w*\.
 * - Main identifier: [a-zA-Z0-9]\w*
 * - Where \w includes letters, digits, and underscores
 */
const HIVE_IDENTIFIER_PATTERN = /^([a-zA-Z0-9]\w*\.)?[a-zA-Z0-9]\w*$/;

/**
 * Database name pattern (without the optional database prefix)
 * Must start with alphanumeric, then alphanumeric + underscores
 */
const DATABASE_NAME_PATTERN = /^[a-zA-Z0-9][a-zA-Z0-9_]*$/;

/**
 * Standard SQL identifier maximum length
 */
const MAX_IDENTIFIER_LENGTH = 128;

/**
 * Validation result interface
 */
export interface ValidationResult {
  isValid: boolean;
  error?: string;
}

/**
 * Get reserved keywords set based on SQL dialect
 */
function getReservedKeywords(dialect?: string): Set<string> {
  switch (dialect?.toLowerCase()) {
    case 'hive':
      return HIVE_RESERVED_WORDS;
    case 'impala':
      return IMPALA_RESERVED_WORDS;
    default:
      return GENERIC_RESERVED_WORDS;
  }
}

/**
 * Validates a database name according to Hive identifier rules
 *
 * Rules based on backend HIVE_IDENTIFER_REGEX:
 * - Must not be empty or only whitespace
 * - Must not exceed maximum length (128 characters)
 * - Must start with alphanumeric character (a-z, A-Z, 0-9)
 * - Subsequent characters can be alphanumeric or underscore
 * - Cannot be a reserved SQL keyword
 * - Cannot contain spaces or special characters
 *
 * @param name - The database name to validate
 * @param dialect - Optional SQL dialect for reserved keyword checking ('hive', 'impala', or 'generic')
 * @returns ValidationResult with isValid boolean and optional error message
 */
export function validateDatabaseName(name: string, dialect?: string): ValidationResult {
  // Check for empty or whitespace-only names
  if (!name || typeof name !== 'string') {
    return {
      isValid: false,
      error: 'Database name is required'
    };
  }

  // Check for leading/trailing whitespace
  if (name !== name.trim()) {
    return {
      isValid: false,
      error: 'Database name cannot have leading or trailing spaces'
    };
  }

  // Check length
  if (name.length > MAX_IDENTIFIER_LENGTH) {
    return {
      isValid: false,
      error: `Database name must be ${MAX_IDENTIFIER_LENGTH} characters or fewer`
    };
  }

  // Check pattern - must match Hive identifier rules
  if (!DATABASE_NAME_PATTERN.test(name)) {
    return {
      isValid: false,
      error:
        'Database name must start with a letter or number and contain only letters, numbers, and underscores'
    };
  }

  // Check for reserved keywords
  const reservedKeywords = getReservedKeywords(dialect);
  if (reservedKeywords.has(name.toUpperCase())) {
    return {
      isValid: false,
      error: 'Database name cannot be a reserved SQL keyword'
    };
  }

  return {
    isValid: true
  };
}

/**
 * Validates a table name according to Hive identifier rules
 * Supports both simple table names and database.table format
 *
 * @param name - The table name to validate (can include database prefix)
 * @param dialect - Optional SQL dialect for reserved keyword checking
 * @returns ValidationResult with isValid boolean and optional error message
 */
export function validateTableName(name: string, dialect?: string): ValidationResult {
  // Check for empty or whitespace-only names
  if (!name || typeof name !== 'string') {
    return {
      isValid: false,
      error: 'Table name is required'
    };
  }

  // Check for leading/trailing whitespace
  if (name !== name.trim()) {
    return {
      isValid: false,
      error: 'Table name cannot have leading or trailing spaces'
    };
  }

  // Check length
  if (name.length > MAX_IDENTIFIER_LENGTH) {
    return {
      isValid: false,
      error: `Table name must be ${MAX_IDENTIFIER_LENGTH} characters or fewer`
    };
  }

  // Check pattern - uses full Hive identifier pattern (supports database.table)
  if (!HIVE_IDENTIFIER_PATTERN.test(name)) {
    return {
      isValid: false,
      error:
        'Table name must start with a letter or number and contain only letters, numbers, and underscores. Database prefix format: database.table'
    };
  }

  // Check for reserved keywords in each part
  const reservedKeywords = getReservedKeywords(dialect);
  const parts = name.split('.');

  for (const part of parts) {
    if (reservedKeywords.has(part.toUpperCase())) {
      return {
        isValid: false,
        error: `"${part}" is a reserved SQL keyword and cannot be used in table names`
      };
    }
  }

  return {
    isValid: true
  };
}

/**
 * Validates a column name according to Hive identifier rules
 *
 * @param name - The column name to validate
 * @param dialect - Optional SQL dialect for reserved keyword checking
 * @returns ValidationResult with isValid boolean and optional error message
 */
export function validateColumnName(name: string, dialect?: string): ValidationResult {
  // Check for empty or whitespace-only names
  if (!name || typeof name !== 'string') {
    return {
      isValid: false,
      error: 'Column name is required'
    };
  }

  // Check for leading/trailing whitespace
  if (name !== name.trim()) {
    return {
      isValid: false,
      error: 'Column name cannot have leading or trailing spaces'
    };
  }

  // Check length
  if (name.length > MAX_IDENTIFIER_LENGTH) {
    return {
      isValid: false,
      error: `Column name must be ${MAX_IDENTIFIER_LENGTH} characters or fewer`
    };
  }

  // Column names use the same pattern as database names (no dot separator)
  if (!DATABASE_NAME_PATTERN.test(name)) {
    return {
      isValid: false,
      error:
        'Column name must start with a letter or number and contain only letters, numbers, and underscores'
    };
  }

  // Check for reserved keywords
  const reservedKeywords = getReservedKeywords(dialect);
  if (reservedKeywords.has(name.toUpperCase())) {
    return {
      isValid: false,
      error: 'Column name cannot be a reserved SQL keyword'
    };
  }

  return {
    isValid: true
  };
}

/**
 * Convenience function to check if a database name is valid
 *
 * @param name - The database name to validate
 * @param dialect - Optional SQL dialect
 * @returns boolean indicating if the name is valid
 */
export function isValidDatabaseName(name: string, dialect?: string): boolean {
  return validateDatabaseName(name, dialect).isValid;
}

/**
 * Convenience function to check if a table name is valid
 *
 * @param name - The table name to validate
 * @param dialect - Optional SQL dialect
 * @returns boolean indicating if the name is valid
 */
export function isValidTableName(name: string, dialect?: string): boolean {
  return validateTableName(name, dialect).isValid;
}

/**
 * Convenience function to check if a column name is valid
 *
 * @param name - The column name to validate
 * @param dialect - Optional SQL dialect
 * @returns boolean indicating if the name is valid
 */
export function isValidColumnName(name: string, dialect?: string): boolean {
  return validateColumnName(name, dialect).isValid;
}

/**
 * Checks if a database name already exists by querying the backend
 *
 * @param name - The database name to check
 * @returns Promise<boolean> indicating if the database already exists
 */
export async function checkDatabaseExists(name: string): Promise<boolean> {
  try {
    const response = await get<{ databases?: string[] }>('/beeswax/api/autocomplete/', {
      silenceErrors: true
    });

    if (response?.databases) {
      return response.databases.includes(name);
    }

    return false;
  } catch (error) {
    // If we can't check, assume it doesn't exist to avoid blocking the user
    console.warn('Failed to check database existence:', error);
    return false;
  }
}

/**
 * Validates database name including uniqueness check
 * Combines format validation with backend uniqueness check
 *
 * @param name - The database name to validate
 * @param dialect - Optional SQL dialect for reserved keyword checking
 * @returns Promise<ValidationResult> with isValid boolean and optional error message
 */
export async function validateDatabaseNameWithUniqueness(
  name: string,
  dialect?: string
): Promise<ValidationResult> {
  // First check format/syntax validation
  const formatValidation = validateDatabaseName(name, dialect);
  if (!formatValidation.isValid) {
    return formatValidation;
  }

  // Then check uniqueness
  const exists = await checkDatabaseExists(name);
  if (exists) {
    return {
      isValid: false,
      error: `Database "${name}" already exists`
    };
  }

  return { isValid: true };
}

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

import { useState, useEffect, useCallback } from 'react';
import { validateDatabaseNameWithUniqueness, ValidationResult } from '../utils/validation';

interface UseDebouncedDatabaseValidationArgs {
  name: string;
  dialect?: string;
  debounceMs?: number;
}

interface UseDebouncedDatabaseValidationResult {
  validation: ValidationResult;
  isValidating: boolean;
  hasValidated: boolean; // Whether we've completed validation for the current name
}

/**
 * Custom hook for debounced database name validation including uniqueness check
 *
 * @param name - The database name to validate
 * @param dialect - Optional SQL dialect for reserved keyword checking
 * @param debounceMs - Debounce delay in milliseconds (default: 500)
 * @returns Validation result and loading state
 */
export function useDebouncedDatabaseValidation({
  name,
  dialect,
  debounceMs = 500
}: UseDebouncedDatabaseValidationArgs): UseDebouncedDatabaseValidationResult {
  const [validation, setValidation] = useState<ValidationResult>({ isValid: true });
  const [isValidating, setIsValidating] = useState(false);
  const [hasValidated, setHasValidated] = useState(false);
  const [lastValidatedName, setLastValidatedName] = useState('');

  const validateName = useCallback(
    async (nameToValidate: string) => {
      if (!nameToValidate || nameToValidate.trim() === '') {
        setValidation({ isValid: true }); // Don't show error for empty field initially
        setIsValidating(false);
        setHasValidated(false); // No validation needed for empty field
        setLastValidatedName('');
        return;
      }

      setIsValidating(true);
      setHasValidated(false); // Mark as not validated while in progress

      try {
        const result = await validateDatabaseNameWithUniqueness(nameToValidate, dialect);
        setValidation(result);
        setLastValidatedName(nameToValidate);
        setHasValidated(true); // Mark as validated after completion
      } catch (error) {
        console.error('Database validation error:', error);
        setValidation({
          isValid: false,
          error: 'Failed to validate database name'
        });
        setLastValidatedName(nameToValidate);
        setHasValidated(true); // Still mark as validated even if failed
      } finally {
        setIsValidating(false);
      }
    },
    [dialect]
  );

  useEffect(() => {
    // Reset validation state when name changes
    if (name !== lastValidatedName) {
      setHasValidated(false);
    }

    const timeoutId = setTimeout(() => {
      validateName(name);
    }, debounceMs);

    return () => clearTimeout(timeoutId);
  }, [name, validateName, debounceMs, lastValidatedName]);

  // Only consider validated if we've completed validation for the current name
  const isCurrentNameValidated = hasValidated && name === lastValidatedName;

  return {
    validation,
    isValidating,
    hasValidated: isCurrentNameValidated
  };
}

export default useDebouncedDatabaseValidation;

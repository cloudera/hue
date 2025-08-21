import * as ko from 'knockout';
import { applySelect2SecurityFix } from './ko.select2';

describe('ko.select2.js - XSS Security Fix', () => {

  it('should apply security fix that sanitizes HTML in formatResult function', () => {
    // Test the exported security fix function directly
    const options = { placeholder: 'Test' };
    
    // Apply the security fix
    applySelect2SecurityFix(options);
    
    // Verify that formatResult function was created
    expect(options).toHaveProperty('formatResult');
    expect(typeof options.formatResult).toBe('function');

    // Test the formatResult function
    const formatResult = options.formatResult;
    
    // Test with malicious script - should be sanitized by deXSS
    const maliciousData = { text: '<script>alert("xss")</script>' };
    const result = formatResult(maliciousData);
    expect(result).toBe(''); // deXSS removes script tags completely
    
    // Test with safe HTML - should be preserved
    const safeData = { text: '<b>Bold text</b>' };
    const safeResult = formatResult(safeData);
    expect(safeResult).toBe('<b>Bold text</b>'); // Safe HTML is preserved
    
    // Test with mixed content - script removed, safe text preserved
    const mixedData = { text: '<script>alert("xss")</script>Safe text' };
    const mixedResult = formatResult(mixedData);
    expect(mixedResult).toBe('Safe text'); // Script removed, safe text preserved

    // Test with null/undefined data - should handle gracefully
    expect(formatResult(null)).toBeUndefined();
    expect(formatResult({ id: '1' })).toBeUndefined(); // No text property
  });

  it('should preserve original formatResult behavior when provided', () => {
    // Test that if there's an original formatResult function, it's called properly
    const originalFormatResult = jest.fn((data) => `Original: ${data.text}`);
    const options = { 
      placeholder: 'Test',
      formatResult: originalFormatResult
    };
    
    // Apply the security fix
    applySelect2SecurityFix(options);
    
    const formatResult = options.formatResult;
    
    // Test with safe data - should call original function with sanitized data
    const safeData = { text: '<b>Bold text</b>' };
    const result = formatResult(safeData);
    
    // Should call original function and get its result
    expect(originalFormatResult).toHaveBeenCalledWith(safeData);
    expect(result).toBe('Original: <b>Bold text</b>');
    
    // Test with malicious data - should sanitize before calling original
    const maliciousData = { text: '<script>alert("xss")</script>Malicious' };
    originalFormatResult.mockClear();
    formatResult(maliciousData);
    
    // Original function should be called with sanitized data
    expect(originalFormatResult).toHaveBeenCalledWith({ text: 'Malicious' });
  });

  it('should verify the binding exists and contains the security fix', () => {
    // Verify that the binding exists and has the security fix
    expect(ko.bindingHandlers.select2).toBeDefined();
    expect(typeof ko.bindingHandlers.select2.init).toBe('function');
    
    // Check that the security fix is present in the source code.
    // Not the ideal way to test this but mocking all required jquery and select2 
    // would have been very complex for this test.
    const initFunctionString = ko.bindingHandlers.select2.init.toString();
    expect(initFunctionString).toContain('applySelect2SecurityFix');
  });

});
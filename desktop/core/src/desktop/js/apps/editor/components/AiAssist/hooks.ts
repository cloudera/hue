import { useMemo } from 'react';

export const useKeywordCase = (parser: any, selectedStatement: string) => {
  const sqlKeywords = useMemo(() => {
    const terminals: { [key: number]: string } = parser?.terminals_ || {};
    const onlyLettersRegex = /^[A-Za-z]+$/;
    const upperCase = Object.values(terminals).filter(str => onlyLettersRegex.test(str));
    const lowerCase = upperCase.map(keyword => keyword.toLowerCase());

    return { upperCase, lowerCase };
  }, [parser]);

  const keywordCase = useMemo(() => {
    const { upperCase, lowerCase } = sqlKeywords;
    const upperCaseCount = upperCase.filter(keyword => selectedStatement.includes(keyword)).length;
    const lowerCaseCount = lowerCase.filter(keyword => selectedStatement.includes(keyword)).length;
    return lowerCaseCount > upperCaseCount ? 'lower' : 'upper';
  }, [selectedStatement, sqlKeywords]);

  return keywordCase;
};

import React from 'react';
import { render, screen } from '@testing-library/react';
import SyntaxHighlighterDiff, { DIFF_INLINE_STYLE } from './SyntaxHighlighterDiff';
import '@testing-library/jest-dom';

function hexToRgbStyle(hex) {
  hex = hex.replace(/^#/, '');
  const r = parseInt(hex.substring(0, 2), 16);
  const g = parseInt(hex.substring(2, 4), 16);
  const b = parseInt(hex.substring(4, 6), 16);
  return `rgb(${r}, ${g}, ${b})`;
}

describe('SyntaxHighlighterDiff Component', () => {
  it('renders and displays old and new code', () => {
    render(
      <SyntaxHighlighterDiff
        oldCode="SELECT col1 \n FROM table2"
        newCode="SELECT col1 \n FROM table1;"
      />
    );

    const parentSpanNew = screen.getByTestId('syntax-highlighter-new');
    expect(parentSpanNew.textContent).toMatch(/SELECT col1 \\n FROM table1;/);

    const parentSpanOld = screen.getByTestId('syntax-highlighter-old');
    expect(parentSpanOld.textContent).toMatch(/SELECT col1 \\n FROM table2/);
  });

  describe('Left side (old code)', () => {
    it('renders inline color styles depending on diff type', () => {
      render(
        <SyntaxHighlighterDiff
          oldCode="SELECT colA FROM tableA;"
          newCode="SELECT colA FROM tableB;"
        />
      );

      const codeColumn = screen.getByTestId('syntax-highlighter-old').querySelector('code');
      const codeColumnFirstLine = codeColumn?.children[0];
      expect(codeColumnFirstLine?.getAttribute('style')).toContain(
        `background-color: ${hexToRgbStyle(DIFF_INLINE_STYLE.rowDeleted.backgroundColor)}`
      );
      const codeColumnSecondLine = codeColumn?.children[1];
      expect(codeColumnSecondLine?.getAttribute('style')).toContain(
        `background-color: ${hexToRgbStyle(DIFF_INLINE_STYLE.rowEmpty.backgroundColor)}`
      );

      const lineNrColumn = screen.getByTestId('syntax-highlighter-row-nr-col-old');
      const lineNrColumnFirstLine = lineNrColumn?.children[0];
      expect(lineNrColumnFirstLine?.getAttribute('style')).toContain(
        `background-color: ${hexToRgbStyle(DIFF_INLINE_STYLE.rowDeleted.backgroundColor)}`
      );
      const lineNrColumnSecondLine = lineNrColumn?.children[1];
      expect(lineNrColumnSecondLine?.getAttribute('style')).toContain(
        `background-color: ${hexToRgbStyle(DIFF_INLINE_STYLE.rowEmpty.backgroundColor)}`
      );
    });

    it('renders line numbers and minus sign', () => {
      render(
        // NOTE, linebreaks matters here, as the line numbers are
        // calculated based on the number of lines
        <SyntaxHighlighterDiff
          oldCode={`SELECT colA 
          FROM tableA;`}
          newCode={`SELECT colA 
          FROM tableB;`}
        />
      );
      const lineNrColumn = screen.getByTestId('syntax-highlighter-row-nr-col-old');
      const firstLine = lineNrColumn?.children[0];
      expect(firstLine?.textContent?.trim()).toEqual('1');
      const secondLine = lineNrColumn?.children[1];
      expect(secondLine?.textContent?.trim()).toEqual('2 -');
      const thirdLine = lineNrColumn?.children[2];
      expect(thirdLine?.textContent?.trim()).toEqual('');
    });
  });

  describe('Right side (new code)', () => {
    it('renders inline color styles depending on diff type', () => {
      render(
        <SyntaxHighlighterDiff
          oldCode="SELECT colA FROM tableA;"
          newCode="SELECT colA FROM tableB;"
        />
      );
      const codeColumn = screen.getByTestId('syntax-highlighter-new').querySelector('code');

      const codeColumnFirstLine = codeColumn?.children[0];
      expect(codeColumnFirstLine?.getAttribute('style')).toContain(
        `background-color: ${hexToRgbStyle(DIFF_INLINE_STYLE.rowEmpty.backgroundColor)}`
      );
      const codeColumnSecondLine = codeColumn?.children[1];
      expect(codeColumnSecondLine?.getAttribute('style')).toContain(
        `background-color: ${hexToRgbStyle(DIFF_INLINE_STYLE.rowAdded.backgroundColor)}`
      );

      const lineNrColumn = screen.getByTestId('syntax-highlighter-row-nr-col-new');
      const lineNrColumnFirstLine = lineNrColumn?.children[0];
      expect(lineNrColumnFirstLine?.getAttribute('style')).toContain(
        `background-color: ${hexToRgbStyle(DIFF_INLINE_STYLE.rowEmpty.backgroundColor)}`
      );
      const lineNrColumnSecondLine = lineNrColumn?.children[1];
      expect(lineNrColumnSecondLine?.getAttribute('style')).toContain(
        `background-color: ${hexToRgbStyle(DIFF_INLINE_STYLE.rowAdded.backgroundColor)}`
      );
    });

    it('renders line numbers and plus signs', () => {
      render(
        // NOTE, linebreaks matters here, as the line numbers are
        // calculated based on the number of lines
        <SyntaxHighlighterDiff
          oldCode={`SELECT colA 
          FROM tableA;`}
          newCode={`SELECT colA 
          FROM tableB;`}
        />
      );
      const lineNrColumn = screen.getByTestId('syntax-highlighter-row-nr-col-new');

      const line1 = lineNrColumn?.children[0];
      expect(line1?.textContent?.trim()).toEqual('1');

      const line2 = lineNrColumn?.children[1];
      expect(line2?.textContent?.trim()).toEqual('');

      const line3 = lineNrColumn?.children[2];
      expect(line3?.textContent?.trim()).toEqual('2 +');
    });
  });
});

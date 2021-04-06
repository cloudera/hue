import React, { FC, useEffect, useRef } from 'react';

import hiveSyntaxParser from 'gethue/lib/parsers/hiveSyntaxParser';
import hiveAutocompleteParser from 'gethue/lib/parsers/hiveAutocompleteParser';
import Executor from 'gethue/lib/execution/executor';
import SqlExecutable from 'gethue/apps/editor/execution/sqlExecutable';
import { SetOptions, SqlReferenceProvider, UdfCategory } from 'gethue/sql/reference/types'
import { ActiveStatementChangedEvent } from 'gethue/apps/editor/components/aceEditor/types';
import { setWebCompProp } from './utils';

const sqlReferenceProvider: SqlReferenceProvider = {
  async getReservedKeywords(dialect: string): Promise<Set<string>> {
    return new Set<string>();
  },
  async getSetOptions(dialect: string): Promise<SetOptions> {
    return {};
  },
  async getUdfCategories(dialect: string): Promise<UdfCategory[]> {
    return [];
  },
  hasUdfCategories(dialect: string): boolean {
    return false;
  }
}

const sqlAutocompleteProvider: any = {
  getAutocompleteParser(dialect: string): Promise<any> {
    return Promise.resolve(hiveAutocompleteParser);
  },
  getSyntaxParser(dialect: string): Promise<any> {
    return Promise.resolve(hiveSyntaxParser);
  }
}

interface QueryEditorElement extends HTMLElement {
  executor: Executor;
  'sql-parser-provider': any;
  'sql-reference-provider': SqlReferenceProvider;
}

interface QueryEditorProps {
  executor: Executor;
  id?: string; // Set a unique ID to allow multiple query editors on one page
  setActiveExecutable(executable: SqlExecutable): void;
}

export const QueryEditor: FC<QueryEditorProps> = ({ setActiveExecutable, executor, id }) => {
  const containerElement = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (containerElement.current) {
      const queryEditorElement = document.createElement('query-editor');
      setWebCompProp<QueryEditorElement>(queryEditorElement, 'executor', executor);
      setWebCompProp<QueryEditorElement>(queryEditorElement, 'id', id || 'some-id');
      setWebCompProp<QueryEditorElement>(queryEditorElement, 'sql-parser-provider', sqlAutocompleteProvider);
      setWebCompProp<QueryEditorElement>(queryEditorElement, 'sql-reference-provider', sqlReferenceProvider);
      containerElement.current.innerHTML = '';
      containerElement.current?.appendChild(queryEditorElement);
    }
  }, [containerElement, executor, id]);

  useEffect(() => {
    if (containerElement.current?.firstChild) {
      containerElement.current.firstChild.addEventListener('active-statement-changed', event => {
        const activeStatementChangedEvent = event as ActiveStatementChangedEvent;
        executor.update(activeStatementChangedEvent.detail, false);
        setActiveExecutable(executor.activeExecutable);
      })
    }
  }, [setActiveExecutable, containerElement, executor])

  return <div ref={ containerElement }/>
};

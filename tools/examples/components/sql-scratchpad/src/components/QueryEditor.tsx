import React, { FC } from 'react';

import hiveSyntaxParser from 'gethue/lib/parsers/hiveSyntaxParser';
import hiveAutocompleteParser from 'gethue/lib/parsers/hiveAutocompleteParser';
import Executor from 'gethue/lib/execution/executor';
import SqlExecutable from 'gethue/apps/editor/execution/sqlExecutable';
import { SetOptions, SqlReferenceProvider, UdfCategory } from 'gethue/sql/reference/types'
import { ActiveStatementChangedEvent } from 'gethue/apps/editor/components/aceEditor/types';

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

export const QueryEditor: FC<QueryEditorProps> = React.memo(({ executor, id, setActiveExecutable }) => {
  const nodeElement = document.createElement('query-editor') as QueryEditorElement;
  nodeElement.setAttribute('hue-base-url', 'http://localhost:8888');
  nodeElement.setAttribute('executor', '');
  nodeElement.setAttribute('sql-parser-provider', '');
  nodeElement.setAttribute('sql-reference-provider', '');

  nodeElement.setAttribute('id', id || 'some-id');
  nodeElement.executor = executor;
  nodeElement['sql-parser-provider'] = sqlAutocompleteProvider;
  nodeElement['sql-reference-provider'] = sqlReferenceProvider;

  nodeElement.addEventListener('active-statement-changed', event => {
    const activeStatementChangedEvent = event as ActiveStatementChangedEvent;
    executor.update(activeStatementChangedEvent.detail, false);
    setActiveExecutable(executor.activeExecutable);
  })

  //nodeElement.addEventListener('value-changed', event => {
  //  // event.detail contains the value
  //})

  // nodeElement.addEventListener('create-new-doc', () => {
  //   // Triggered when the user presses ctrl+n
  // })

  // nodeElement.addEventListener('save-doc', () => {
  //   // Triggered when the user presses ctrl+s
  // })

  // nodeElement.addEventListener('ace-created', event => {
  //   // event.detail contains the Ace editor instance
  // })

  // nodeElement.addEventListener('cursor-changed', event => {
  //   // event.detail contains the cursor position
  // })

  return <div className={ 'query-editor-wrapper' }
    ref={
      element => {
        if (element) {
          element.innerHTML = '';
          element.append(nodeElement);
        }
      }
    }
  />;
});

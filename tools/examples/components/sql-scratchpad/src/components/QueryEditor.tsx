import React, { FC } from 'react';

import 'gethue/lib/components/query-editor-components';

import hiveSyntaxParser from 'gethue/lib/parsers/hiveSyntaxParser';
import hiveAutocompleteParser from 'gethue/lib/parsers/hiveAutocompleteParser';
import Executor from 'gethue/lib/execution/executor';
import { SetOptions, SqlReferenceProvider, UdfCategory } from 'gethue/src/sql/reference/types'

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
}

export const QueryEditor: FC<QueryEditorProps> = ({ executor }) => {
  const nodeElement = document.createElement('query-editor') as QueryEditorElement;
  nodeElement.setAttribute('hue-base-url', 'http://localhost:8888');
  nodeElement.setAttribute('executor', '');
  nodeElement.setAttribute('sql-parser-provider', '');
  nodeElement.setAttribute('sql-reference-provider', '');
  nodeElement.executor = executor;
  nodeElement['sql-parser-provider'] = sqlAutocompleteProvider;
  nodeElement['sql-reference-provider'] = sqlReferenceProvider;

  return <div className={ 'query-editor-wrapper' }
    ref={
      element => {
        element?.append(nodeElement);
      }
    }
  />;
}
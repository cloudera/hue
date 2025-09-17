// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// Apache License 2.0 applies.

import React, { useMemo } from 'react';
import EmptyState from 'cuix/dist/components/EmptyState';
import Button, { PrimaryButton } from 'cuix/dist/components/Button';
import CopyClipboardIcon from '@cloudera/cuix-core/icons/react/CopyClipboardIcon';
import { i18nReact } from '../../../../utils/i18nReact';
import huePubSub from '../../../../utils/huePubSub';
import type { Analysis } from '../../../../catalog/DataCatalogEntry';

import './ViewSql.scss';

export interface ViewSqlProps {
  rawAnalysis?: Analysis;
  sourceType?: string;
}

const ViewSql = ({ rawAnalysis, sourceType }: ViewSqlProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();

  // Extract SQL from analysis.properties (same logic as legacy implementation)
  const sql = useMemo(() => {
    if (!rawAnalysis?.properties) {
      return '';
    }

    // Look for view SQL in properties array - matches legacy implementation
    const viewSqlPropertyNames = new Set(['view original text:', 'original query:']);
    const foundIndex = rawAnalysis.properties.findIndex(property =>
      viewSqlPropertyNames.has(property.col_name.toLowerCase())
    );

    if (foundIndex === -1) {
      return '';
    }

    // Collect SQL from the found property and subsequent properties
    let sql = rawAnalysis.properties[foundIndex]?.data_type || '';

    // Check subsequent properties for continuation (empty col_name with data_type or comment)
    for (let i = foundIndex + 1; i < rawAnalysis.properties.length; i++) {
      const prop = rawAnalysis.properties[i];
      if (!prop.col_name || prop.col_name.trim() === '') {
        if (prop.data_type && prop.data_type.trim() !== '') {
          sql += '\n' + prop.data_type;
        }
        if (prop.comment && prop.comment.trim() !== '') {
          sql += '\n' + prop.comment;
        }
      } else {
        // Stop when we hit a new section (non-empty col_name)
        break;
      }
    }

    return sql.trim();
  }, [rawAnalysis]);

  // Simple SQL formatting and syntax highlighting
  const formattedSql = useMemo(() => {
    if (!sql) {
      return '';
    }

    // Basic SQL formatting - add line breaks after common clauses
    return sql
      .replace(
        /\s+(SELECT|FROM|WHERE|GROUP BY|ORDER BY|HAVING|JOIN|LEFT JOIN|RIGHT JOIN|INNER JOIN|OUTER JOIN|UNION|WITH)\s+/gi,
        '\n$1 '
      )
      .replace(/\s+(AND|OR)\s+/gi, '\n  $1 ')
      .trim();
  }, [sql]);

  const handleCopyToClipboard = async (): Promise<void> => {
    if (sql) {
      try {
        await navigator.clipboard.writeText(sql);
      } catch (error) {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = sql;
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
      }
    }
  };

  const handleOpenInEditor = (): void => {
    if (!sql) {
      return;
    }
    const type = sourceType || 'hive';
    huePubSub.publish('open.editor.new.prefilled.query', {
      type,
      query: sql
    });
  };

  if (!sql) {
    return (
      <EmptyState
        title={t('No view SQL available')}
        subtitle={t('This view does not have a SQL definition.')}
      />
    );
  }

  return (
    <div className="view-sql">
      <div className="view-sql__title-bar">
        {t('View SQL')}
        <div className="view-sql__action-group">
          <PrimaryButton onClick={handleOpenInEditor} title={t('Open in Editor')}>
            {t('Query')}
          </PrimaryButton>
          <Button onClick={handleCopyToClipboard} title={t('Copy SQL to clipboard')}>
            <CopyClipboardIcon /> {t('Copy')}
          </Button>
        </div>
      </div>
      <div className="view-sql__content" role="region" aria-label={t('View SQL')}>
        <textarea className="view-sql__textarea" value={formattedSql} readOnly />
      </div>
    </div>
  );
};

export default ViewSql;

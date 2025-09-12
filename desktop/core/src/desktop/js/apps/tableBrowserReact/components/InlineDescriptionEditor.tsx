// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// Apache License 2.0 applies.

import React from 'react';
import { Skeleton } from 'antd';
import Input from 'cuix/dist/components/Input';
import BorderlessButton from 'cuix/dist/components/Button/BorderlessButton';
import Button from 'cuix/dist/components/Button/Button';
import PrimaryButton from 'cuix/dist/components/Button/PrimaryButton';
import { i18nReact } from '../../../utils/i18nReact';

interface InlineDescriptionEditorProps {
  /** The unique identifier for this item */
  itemId: string;
  /** Current description value from the descriptions state */
  currentDescription?: string;
  /** Original/fallback description value */
  originalDescription?: string;
  /** Whether this item is currently being edited */
  isEditing: boolean;
  /** Current editing value */
  editingValue: string;
  /** Whether description data has been loaded */
  hasLoadedDescription: boolean;
  /** Callback when edit mode is started */
  onStartEdit: (itemId: string, initialValue: string) => void;
  /** Callback when edit is cancelled */
  onCancelEdit: () => void;
  /** Callback when description is saved */
  onSave: (itemId: string, value: string) => void;
  /** Callback when editing value changes */
  onEditingValueChange: (value: string) => void;
  /** Placeholder text for the input */
  placeholder?: string;
}

const InlineDescriptionEditor = ({
  itemId,
  currentDescription,
  originalDescription,
  isEditing,
  editingValue,
  hasLoadedDescription,
  onStartEdit,
  onCancelEdit,
  onSave,
  onEditingValueChange,
  placeholder
}: InlineDescriptionEditorProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();

  const displayValue = currentDescription || originalDescription || '';
  const defaultPlaceholder = placeholder || t('Add a description...');

  // Show skeleton while loading
  if (!hasLoadedDescription && !originalDescription) {
    return <Skeleton.Input active size="small" style={{ width: '60%' }} />;
  }

  // Edit mode
  if (isEditing) {
    return (
      <div>
        <Input
          value={editingValue}
          onChange={e => onEditingValueChange(e.target.value)}
          onPressEnter={e => {
            e.preventDefault();
            onSave(itemId, editingValue);
          }}
          placeholder={defaultPlaceholder}
          size="small"
        />
        <div style={{ marginTop: 2 }}>
          <PrimaryButton size="small" onClick={() => onSave(itemId, editingValue)}>
            {t('Save')}
          </PrimaryButton>
          <Button size="small" onClick={onCancelEdit} style={{ marginLeft: 4 }}>
            {t('Cancel')}
          </Button>
        </div>
      </div>
    );
  }

  // Display mode
  return (
    <span>
      {displayValue && <span style={{ marginRight: 8 }}>{displayValue}</span>}
      <BorderlessButton
        size="small"
        style={{ opacity: 0.7, fontSize: '12px', padding: 0, height: 'auto', lineHeight: 1 }}
        onClick={() => onStartEdit(itemId, displayValue)}
      >
        {displayValue ? t('Edit') : t('Add')}
      </BorderlessButton>
    </span>
  );
};

export default InlineDescriptionEditor;

// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// Apache License 2.0 applies.

import React from 'react';
import { Skeleton, Input as AntdInput } from 'antd';
import BorderlessButton from 'cuix/dist/components/Button/BorderlessButton';
import Button from 'cuix/dist/components/Button/Button';
import PrimaryButton from 'cuix/dist/components/Button/PrimaryButton';
import { i18nReact } from '../../../utils/i18nReact';
import classNames from 'classnames';
import './InlineDescriptionEditor.scss';

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
    return <Skeleton.Input active size="small" className="inline-desc-editor__skeleton" />;
  }

  // Edit mode
  if (isEditing) {
    return (
      <div className="inline-desc-editor">
        <AntdInput.TextArea
          className="inline-desc-editor__input"
          value={editingValue}
          onChange={e => onEditingValueChange(e.target.value)}
          onPressEnter={e => {
            e.preventDefault();
            onSave(itemId, editingValue);
          }}
          placeholder={defaultPlaceholder}
          size="middle"
          autoSize={{ minRows: 1, maxRows: 4 }}
        />
        <div className="inline-desc-editor__actions">
          <PrimaryButton size="small" onClick={() => onSave(itemId, editingValue)}>
            {t('Save')}
          </PrimaryButton>
          <Button size="small" onClick={onCancelEdit} className="inline-desc-editor__cancel">
            {t('Cancel')}
          </Button>
        </div>
      </div>
    );
  }

  // Display mode
  return (
    <span className="inline-desc-editor inline-desc-editor--display">
      {displayValue && <span className="inline-desc-editor__text">{displayValue}</span>}
      <BorderlessButton
        size="small"
        className={classNames({ 'inline-desc-editor__button--is-editing': displayValue })}
        onClick={() => onStartEdit(itemId, displayValue)}
      >
        {displayValue ? t('Edit') : t('Add')}
      </BorderlessButton>
    </span>
  );
};

export default InlineDescriptionEditor;

// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// Apache License 2.0 applies.

import React, { useState, useRef, useEffect } from 'react';
import { Skeleton, Input as AntdInput } from 'antd';
import BorderlessButton from 'cuix/dist/components/Button/BorderlessButton';
import Button from 'cuix/dist/components/Button/Button';
import PrimaryButton from 'cuix/dist/components/Button/PrimaryButton';
import CaratDownIcon from '@cloudera/cuix-core/icons/react/CaratDownIcon';
import CaratRightIcon from '@cloudera/cuix-core/icons/react/CaratRightIcon';
import EditIcon from '@cloudera/cuix-core/icons/react/EditIcon';
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
  const [isExpanded, setIsExpanded] = useState(false);
  const [needsTruncation, setNeedsTruncation] = useState(false);
  const textRef = useRef<HTMLSpanElement>(null);

  const displayValue = currentDescription || originalDescription || '';
  const defaultPlaceholder = placeholder || t('Add a description...');

  // Generate unique IDs for accessibility
  const inputId = `inline-desc-input-${itemId}`;
  const actionsId = `inline-desc-actions-${itemId}`;
  const textId = `inline-desc-text-${itemId}`;
  const expandButtonId = `inline-desc-expand-${itemId}`;

  // Check if text needs truncation by measuring if it would overflow on one line
  useEffect(() => {
    if (displayValue && textRef.current) {
      const element = textRef.current;
      // Create a temporary element to measure the full text width
      const tempElement = document.createElement('span');
      tempElement.style.visibility = 'hidden';
      tempElement.style.position = 'absolute';
      tempElement.style.whiteSpace = 'nowrap';
      tempElement.style.font = window.getComputedStyle(element).font;
      tempElement.textContent = displayValue;

      document.body.appendChild(tempElement);
      const fullTextWidth = tempElement.offsetWidth;
      document.body.removeChild(tempElement);

      // Compare with available width (accounting for buttons)
      const containerWidth = element.parentElement?.offsetWidth || 0;
      const buttonSpace = 100; // Approximate space for edit/expand buttons

      setNeedsTruncation(fullTextWidth > containerWidth - buttonSpace);
    }
  }, [displayValue]);

  // Show skeleton while loading
  if (!hasLoadedDescription && !originalDescription) {
    return <Skeleton.Input active size="small" className="inline-desc-editor__skeleton" />;
  }

  // Edit mode
  if (isEditing) {
    return (
      <div className="inline-desc-editor" role="group" aria-labelledby={inputId}>
        <AntdInput.TextArea
          id={inputId}
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
          maxLength={1024}
          aria-label={t('Edit description text')}
          aria-describedby={actionsId}
        />
        <div
          id={actionsId}
          className="inline-desc-editor__actions"
          role="group"
          aria-label={t('Edit actions')}
        >
          <PrimaryButton
            size="small"
            onClick={() => onSave(itemId, editingValue)}
            aria-label={t('Save description changes')}
          >
            {t('Save')}
          </PrimaryButton>
          <Button
            size="small"
            onClick={onCancelEdit}
            className="inline-desc-editor__cancel"
            aria-label={t('Cancel editing and discard changes')}
          >
            {t('Cancel')}
          </Button>
        </div>
      </div>
    );
  }

  const handleToggleExpand = () => {
    setIsExpanded(!isExpanded);
  };

  // Display mode
  return (
    <span className="inline-desc-editor inline-desc-editor--display">
      {displayValue && (
        <span
          ref={textRef}
          id={textId}
          className={classNames('inline-desc-editor__text', {
            'inline-desc-editor__text--truncated': needsTruncation && !isExpanded,
            'inline-desc-editor__text--expanded': needsTruncation && isExpanded,
            'inline-desc-editor__text--clickable': needsTruncation && !isExpanded
          })}
          onClick={needsTruncation && !isExpanded ? handleToggleExpand : undefined}
          role={needsTruncation && !isExpanded ? 'button' : undefined}
          tabIndex={needsTruncation && !isExpanded ? 0 : undefined}
          aria-expanded={needsTruncation ? isExpanded : undefined}
          aria-describedby={needsTruncation ? expandButtonId : undefined}
          aria-label={
            needsTruncation && !isExpanded
              ? t('Description text (truncated). Click to expand.')
              : undefined
          }
          onKeyDown={
            needsTruncation && !isExpanded
              ? e => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    handleToggleExpand();
                  }
                }
              : undefined
          }
        >
          {displayValue}
        </span>
      )}
      <div
        className="inline-desc-editor__buttons"
        role="group"
        aria-label={t('Description actions')}
      >
        {needsTruncation && displayValue && (
          <button
            type="button"
            id={expandButtonId}
            className="inline-desc-editor__expand-button"
            onClick={handleToggleExpand}
            aria-label={isExpanded ? t('Collapse description text') : t('Expand description text')}
            aria-expanded={isExpanded}
            aria-controls={textId}
            title={isExpanded ? t('Show less text') : t('Show more text')}
          >
            {isExpanded ? <CaratDownIcon /> : <CaratRightIcon />}
          </button>
        )}
        <BorderlessButton
          size="small"
          className="inline-desc-editor__edit-button"
          onClick={() => onStartEdit(itemId, displayValue)}
          aria-label={displayValue ? t('Edit description') : t('Add description')}
          title={displayValue ? t('Edit description') : t('Add description')}
        >
          <EditIcon />
        </BorderlessButton>
      </div>
    </span>
  );
};

export default InlineDescriptionEditor;

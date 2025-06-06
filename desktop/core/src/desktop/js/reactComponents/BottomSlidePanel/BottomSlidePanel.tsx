// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import { BorderlessButton, PrimaryButton } from 'cuix/dist/components/Button';
import React, { useEffect, useState } from 'react';
import './BottomSlidePanel.scss';

interface BottomSlidePanelProps {
  isOpen: boolean;
  onClose: () => void;
  onPrimaryClick?: (unknown) => void;
  primaryText?: string;
  cancelText?: string;
  title?: string;
  children: React.ReactNode;
  className?: string;
  showMask?: boolean;
  maskClosable?: boolean;
}

const BottomSlidePanel: React.FC<BottomSlidePanelProps> = ({
  isOpen,
  onClose,
  onPrimaryClick,
  primaryText,
  cancelText,
  title,
  children,
  className = '',
  showMask = true,
  maskClosable = true
}) => {
  const [shouldRender, setShouldRender] = useState<boolean>(isOpen);

  useEffect(() => {
    if (isOpen) {
      setShouldRender(true);
    } else {
      const timeout = setTimeout(() => setShouldRender(false), 300); // match CSS duration
      return () => clearTimeout(timeout);
    }
  }, [isOpen]);

  if (!shouldRender) {
    return null;
  }

  return (
    <>
      {showMask && (
        <div
          className={`hue-bottom-slide-mask ${isOpen ? 'fade-in' : 'fade-out'}`}
          role="button"
          tabIndex={0}
          onClick={maskClosable ? onClose : undefined}
          onKeyDown={e => {
            if (maskClosable && (e.key === 'Enter' || e.key === ' ')) {
              e.preventDefault();
              onClose();
            }
          }}
          data-testid="mask"
        />
      )}
      <div
        className={`hue-bottom-slide-panel ${isOpen ? 'hue-bottom-slide-in' : 'hue-bottom-slide-out'} ${className}`}
      >
        {title && <div className="hue-bottom-slide-panel__title">{title}</div>}

        <div className="hue-bottom-slide-panel__content">{children}</div>

        {(primaryText || cancelText) && (
          <div className="hue-bottom-slide-panel__footer">
            {primaryText && <PrimaryButton onClick={onPrimaryClick}>{primaryText}</PrimaryButton>}
            {cancelText && <BorderlessButton onClick={onClose}>{cancelText}</BorderlessButton>}
          </div>
        )}
      </div>
    </>
  );
};

export default BottomSlidePanel;

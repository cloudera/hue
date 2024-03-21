/*
  Licensed to Cloudera, Inc. under one
  or more contributor license agreements.  See the NOTICE file
  distributed with this work for additional information
  regarding copyright ownership.  Cloudera, Inc. licenses this file
  to you under the Apache License, Version 2.0 (the
  "License"); you may not use this file except in compliance
  with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
*/

import React, { useRef } from 'react';
import classNames from 'classnames';
import LinkButton from 'cuix/dist/components/Button/LinkButton';

import AiAssistantIcon from '../../../../../components/icons/AiAssistantIcon';
import AnimatedCloseButton from '../AnimatedCloseButton/AnimatedCloseButton';
import CirclesLoader from '../CirclesLoader/CirclesLoader';

import './AnimatedLauncher.scss';

interface AnimatedLauncherProps {
  isAnimating: string;
  isExpanded: boolean;
  isLoading: boolean;
  loadingStatusText?: string;
  errorStatusText?: string;
  warningStatusText?: string;
  onExpandClick: () => void;
  onCloseErrorClick: () => void;
  onCloseWarningClick: () => void;
  onMoreWarningInfoClick: () => void;
  onAnimationEnd: (event: React.AnimationEvent<HTMLDivElement>) => void;
}

function AnimatedLauncher({
  isAnimating,
  isExpanded,
  isLoading,
  loadingStatusText,
  errorStatusText,
  warningStatusText,
  onExpandClick,
  onCloseErrorClick,
  onCloseWarningClick,
  onMoreWarningInfoClick,
  onAnimationEnd
}: AnimatedLauncherProps): JSX.Element {
  const showErrorMessage = !!errorStatusText;
  const showWarningMessage = !!warningStatusText;

  const handleClickOnCircleOrInfobar = () => {
    const loaderIsShowingMessage =
      isExpanded && (loadingStatusText || showErrorMessage || showWarningMessage);
    if (!loaderIsShowingMessage) {
      onExpandClick();
    }
  };

  const barIsActive = isExpanded || isAnimating !== 'no';

  // We only want the twinkle animation to run one time and
  // only if the bar is not expanded when first rendered.
  // We use useRef to make sure HTML class 'ai-assist-icon--twinkle-once'
  // is only added once and never removed.
  const twinkleOnce = useRef(!isExpanded);

  return (
    <>
      <div className="hue-ai-assist-bar__animated-launcher-btn-container">
        <LinkButton
          aria-label={'Assistant'}
          title={barIsActive ? '' : 'Open the SQL AI Assistant'}
          className={classNames('hue-ai-assist-bar__animated-launcher-btn', {
            'hue-ai-assist-bar__animated-launcher-btn--active': barIsActive
          })}
          icon={
            <AiAssistantIcon
              className={twinkleOnce.current ? 'ai-assist-icon--twinkle-once' : ''}
            />
          }
          disabled={barIsActive}
          onClick={() => onExpandClick()}
        >
          Assistant
        </LinkButton>
      </div>
      <button
        onAnimationEnd={onAnimationEnd}
        className={classNames('hue-ai-assist-bar__animated-launcher', {
          'hue-ai-assist-bar__animated-launcher--expanding': isAnimating === 'expand',
          'hue-ai-assist-bar__animated-launcher--contracting': isAnimating === 'contract',
          'hue-ai-assist-bar__animated-launcher--expanded': isExpanded,
          'hue-ai-assist-bar__animated-launcher--loading': isExpanded && isLoading,
          'hue-ai-assist-bar__animated-launcher--loading-with-status':
            isExpanded && isLoading && loadingStatusText,
          'hue-ai-assist-bar__animated-launcher--error': showErrorMessage,
          'hue-ai-assist-bar__animated-launcher--warning': showWarningMessage
        })}
        onClick={handleClickOnCircleOrInfobar}
      >
        {isExpanded && isLoading && (
          <>
            <CirclesLoader />
            <div className="hue-ai-assist-bar__animated-launcher-loading-status">
              {loadingStatusText}
            </div>
          </>
        )}
        {isExpanded && showErrorMessage && (
          <>
            <AnimatedCloseButton
              title="Close Error Message"
              className="hue-ai-assist-bar__animated-launcher-error-close-btn"
              size="small"
              onClick={onCloseErrorClick}
            />
            <div className="hue-ai-assist-bar__animated-launcher-error-text">{errorStatusText}</div>
          </>
        )}
        {isExpanded && showWarningMessage && (
          <>
            <AnimatedCloseButton
              title="Close Warning Message"
              className="hue-ai-assist-bar__animated-launcher-warning-close-btn"
              size="small"
              onClick={onCloseWarningClick}
            />
            <div className="hue-ai-assist-bar__animated-launcher-warning-text">
              {warningStatusText}
              <LinkButton
                onClick={onMoreWarningInfoClick}
                data-event=""
                className="hue-ai-assist-bar__animated-launcher-warning-link"
              >
                More info...
              </LinkButton>
            </div>
          </>
        )}
      </button>
    </>
  );
}

export default AnimatedLauncher;

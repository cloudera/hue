import React from 'react';
import classNames from 'classnames';
import LinkButton from 'cuix/dist/components/Button/LinkButton';

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
}: AnimatedLauncherProps) {
  const showErrorMessage = !!errorStatusText;
  const showWarningMessage = !!warningStatusText;

  const handleClickOnCircleOrInfobar = () => {
    const loaderIsShowingMessage =
      isExpanded && (loadingStatusText || showErrorMessage || showWarningMessage);
    if (!loaderIsShowingMessage) onExpandClick();
  };

  return (
    <div
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
    </div>
  );
}

export default AnimatedLauncher;

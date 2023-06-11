import React from 'react';
import classNames from 'classnames';


import AnimatedCloseButton from '../AnimatedCloseButton/AnimatedCloseButton';

import CirclesLoader from '../CirclesLoader/CirclesLoader';

import './AnimatedLauncher.scss';

interface AnimatedLauncherProps {
  isAnimating: string;
  isExpanded: boolean;
  isLoading: boolean;
  loadingStatusText: string;
  errorStatusText: string;
  setErrorStatusText: React.Dispatch<React.SetStateAction<string>>;
  onExpandClick: () => void;
  onCloseErrorClick: () => void;
  onAnimationEnd: (event: React.AnimationEvent<HTMLDivElement>) => void;
}

function AnimatedLauncher({
  isAnimating,
  isExpanded,
  isLoading,
  loadingStatusText,
  errorStatusText,
  onExpandClick,
  onCloseErrorClick,
  onAnimationEnd
}: AnimatedLauncherProps) {
  const showErrorMessage = !!errorStatusText;
  console.info('isAnimating:', isAnimating)
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
        'hue-ai-assist-bar__animated-launcher--error': showErrorMessage
      })}
      onClick={onExpandClick}
    >
      {isExpanded && isLoading && (
        <>
          <CirclesLoader />
          <div className="hue-ai-assist-bar__animated-launcher-loading-status">
            {loadingStatusText}
          </div>
        </>
      )}
      {isExpanded && errorStatusText && (
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
    </div>
  );
}

export default AnimatedLauncher;

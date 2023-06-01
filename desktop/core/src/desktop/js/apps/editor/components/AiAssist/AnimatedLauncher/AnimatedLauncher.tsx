import React from 'react';
import classNames from 'classnames';

import AnimatedCloseButton from '../AnimatedCloseButton/AnimatedCloseButton';

import CirclesLoader from '../CirclesLoader/CirclesLoader';

import './AnimatedLauncher.scss';

interface AnimatedLauncerProps {
  isAnimating: string;
  isExpanded: boolean;
  isLoading: boolean;
  loadingStatusText: string;
  errorStatusText: string;
  setIsExpanded: React.Dispatch<React.SetStateAction<boolean>>;
  setIsAnimating: React.Dispatch<React.SetStateAction<'no' | 'expand' | 'contract'>>;
  setErrorStatusText: React.Dispatch<React.SetStateAction<string>>;
}

function AnimatedLauncer({
  isAnimating,
  isExpanded,
  isLoading,
  loadingStatusText,
  errorStatusText,
  setIsExpanded,
  setIsAnimating,
  setErrorStatusText
}: AnimatedLauncerProps) {

  return (
    <div
      onAnimationEnd={event => {
        // event.stopPropagation();
        // if (event.target === event.currentTarget) {
        // setIsLoading(false);
      }}
      className={classNames('hue-ai-assist-bar__icon', {
        'hue-ai-assist-bar__icon--expanding': isAnimating === 'expand',
        'hue-ai-assist-bar__icon--expanded': isExpanded,
        'hue-ai-assist-bar__icon--loading': isExpanded && isLoading,
        'hue-ai-assist-bar__icon--loading-with-status':
          isExpanded && isLoading && loadingStatusText,
        'hue-ai-assist-bar__icon--error': !!errorStatusText
      })}
      onClick={() => {
        setIsExpanded(true);
        setIsAnimating(prev => (prev === 'no' ? (isExpanded ? 'contract' : 'expand') : prev));
      }}
    >
      {isExpanded && isLoading && <CirclesLoader />}
      {isExpanded && isLoading && (
        <div className="hue-ai-assist-bar__icon-loading-status">{loadingStatusText}</div>
      )}
      {isExpanded && errorStatusText && (
        <>
          <AnimatedCloseButton
            title="Close Error Message"
            className="hue-ai-assist-bar__icon-error-close-btn"
            size="small"
            onClick={() => {
              setErrorStatusText('');
            }}
          />
          <div className="hue-ai-assist-bar__icon-error-text">{errorStatusText}</div>
        </>
      )}
    </div>
  );
}

export default AnimatedLauncer;

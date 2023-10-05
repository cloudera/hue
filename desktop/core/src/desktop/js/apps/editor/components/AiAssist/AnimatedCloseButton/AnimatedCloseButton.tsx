import React from 'react';
import classNames from 'classnames';

import './AnimatedCloseButton.scss';

type Size = 'small' | 'large';
type Direction = 'left' | 'right';

type Props = {
  title: string;
  className?: string;
  onClick: () => void;
  size?: Size;
  direction?: Direction;
};

function AnimatedCloseButton({
  title,
  className,
  onClick,
  size = 'large',
  direction = 'left'
}: Props) {
  return (
    <div
      title={title}
      className={classNames(
        'hue-animated-close-button',
        className,
        `hue-animated-close-button--${size}`,
        `hue-animated-close-button--${direction}`
      )}
      onClick={onClick}
    >
      <span></span>
      <span></span>
      <span></span>
    </div>
  );
}

export default AnimatedCloseButton;

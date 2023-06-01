import React from 'react';

import './CirclesLoader.scss';

function CirclesLoader({
  repeatCount = 'indefinite',
  duration = '1.5s'
}: {
  repeatCount?: number | string;
  duration?: string;
}) {
  const cy = '12';
  const renderAnimation = begin => (
    <animate
      attributeName="r"
      begin={begin}
      calcMode="spline"
      dur={duration}
      keySplines="0.2 0.2 0.4 0.8;0.2 0.2 0.4 0.8;0.2 0.2 0.4 0.8"
      repeatCount={repeatCount}
      values="0;2;0;0"
    />
  );

  return (
    <svg
      className="hue-ai-assist-bar__circles-loader"
      xmlns="http://www.w3.org/2000/svg"
      width="14"
      height="14"
      viewBox="0 0 24 24"
    >
      <circle className="hue-ai-assist-bar__circles-loader-circle" cx="18" cy={cy} r="0">
        {renderAnimation('.67')}
      </circle>
      <circle className="hue-ai-assist-bar__circles-loader-circle" cx="12" cy={cy} r="0">
        {renderAnimation('.33')}
      </circle>
      <circle className="hue-ai-assist-bar__circles-loader-circle" cx="6" cy={cy} r="0">
        {renderAnimation('0')}
      </circle>
    </svg>
  );
}

export default CirclesLoader;

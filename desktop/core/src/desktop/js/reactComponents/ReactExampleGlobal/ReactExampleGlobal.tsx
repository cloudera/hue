'use strict';

import React, { useState } from 'react';

import './ReactExampleGlobal.scss';

export interface ReactExampleGlobalProps {
  onClick?(e: React.MouseEvent): void;
  version?: string;
  myObj?: { id: string };
  className?: string;
  children?: React.ReactNode | React.ReactNode[];
}

const defaultProps = {
  // eslint-disable-next-line @typescript-eslint/no-empty-function
  onClick: () => {},
  version: 'xxx'
};

const ReactExampleGlobal = ({
  onClick,
  children,
  version,
  myObj
}: ReactExampleGlobalProps): JSX.Element => {
  const [isClicked, setIsClicked] = useState(false);

  return (
    <button
      className="react-example-global"
      disabled={isClicked}
      onClick={e => {
        onClick && onClick(e);
        setIsClicked(true);
        console.info(`ReactExampleGlobal clicked  ${version} ${myObj?.id}`);
      }}
    >
      ReactExampleGlobal - {children ?? 'Like me'}
    </button>
  );
};

ReactExampleGlobal.defaultProps = defaultProps;

export default ReactExampleGlobal;

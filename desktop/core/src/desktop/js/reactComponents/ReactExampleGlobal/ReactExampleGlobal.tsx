'use strict';

import React, { useState } from 'react';

import './ReactExampleGlobal.scss';

export interface ReactExampleGlobalProps {
  onClick(e: React.MouseEvent): any;
  version: string;
  myObj?: any;
  className?: string;
  children?: React.ReactNode | React.ReactNode[];
}

const defaultProps = {
  onClick: () => {},
  version: 'xxx'
};

const ReactExampleGlobal = ({ onClick, children, version, myObj }: ReactExampleGlobalProps) => {
  const [isClicked, setIsClicked] = useState(false);

  return (
    <button
      className="react-example-global"
      disabled={isClicked}
      onClick={e => {
        onClick(e);
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

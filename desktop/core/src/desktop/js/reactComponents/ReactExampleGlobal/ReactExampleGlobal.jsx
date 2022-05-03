import React, { useState } from 'react';
import PropTypes from 'prop-types';

import './ReactExampleGlobal.scss';

('use strict');

const propTypes = {
  onClick: PropTypes.func,
  version: PropTypes.string,
  myObj: PropTypes.any,
  children: PropTypes.any,
};


const defaultProps = {
  onClick: ()=>{},
  version: 'xxx',
};

const ReactExampleGlobal = ({ children, onClick, version, myObj }) => {
  const [isClicked, setIsClicked] = useState(false);

  return (
    <button
      className='react-example-global'
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

ReactExampleGlobal.propTypes = propTypes;
ReactExampleGlobal.defaultProps = defaultProps;

export default ReactExampleGlobal;

'use strict';

import * as React from 'react';


// This component is rendered if the react loadComponent can't find
// which react component to use 
const FallbackComponent = () => {
  return (
    <div>Placeholder component
    </div>
  );
};

export default FallbackComponent;

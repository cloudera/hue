'use strict';

import React, { useState } from 'react';

import { i18nReact } from '../../utils/i18nReact';
import hueAnalytics from '../../utils/hueAnalytics';

import './ReactExampleGlobal.scss';

export interface ReactExampleGlobalProps {
  onClick?(e: React.MouseEvent): void;
  version?: string;
  myObj?: { id: string };
  className?: string;
  children?: React.ReactNode | React.ReactNode[];
}

const ReactExampleGlobal = ({
  onClick,
  children,
  version = '1',
  myObj
}: ReactExampleGlobalProps): JSX.Element => {
  const [isClicked, setIsClicked] = useState(false);

  // We use the translation hook with the built in suspence,
  // meaning that this component won't render until the language file
  // have been loaded.
  const { t } = i18nReact.useTranslation();

  return (
    <button
      className="react-example-global"
      disabled={isClicked}
      onClick={e => {
        onClick && onClick(e);
        setIsClicked(true);
        console.info(`ReactExampleGlobal clicked  ${version} ${myObj?.id}`);
        hueAnalytics.log('test-area', 'button click', true);
      }}
    >
      ReactExampleGlobal - {children ?? t('Yes')}
    </button>
  );
};

export default ReactExampleGlobal;

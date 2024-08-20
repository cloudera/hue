// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import React, { ReactNode, useState } from 'react';
import Joyride from 'react-joyride';

import { hueWindow } from 'types/types';
import I18n from 'utils/i18n';
import { useHuePubSub } from '../../utils/hooks/useHuePubSub';

import './WelcomeTour.scss';
import scssVariables from './WelcomeTour.module.scss';

const {
  backButtonBorder,
  borderRadius,
  buttonFontSize,
  buttonLineHeight,
  buttonPadding,
  overlayColor,
  primaryColor,
  tourZIndex
} = scssVariables;

const getStepContent = (title?: ReactNode, text?: ReactNode) => (
  <>
    {title && <h3>{title}</h3>}
    {text && <p>{text}</p>}
  </>
);

const steps: Joyride.Step[] = [
  {
    content: getStepContent(
      I18n('Welcome to Hue 4!'),
      I18n('We want to introduce you to the new interface. It takes less than a minute. Ready?')
    ),
    target: 'body',
    disableBeacon: true,
    placement: 'center'
  },
  {
    content: getStepContent(
      I18n('A new top bar!'),
      I18n('Do global search and view status of jobs and notifications on the right.')
    ),
    target: '.navbar-default',
    disableBeacon: true,
    placement: 'bottom'
  },
  {
    content: getStepContent(
      I18n('Sidebar for navigation'),
      I18n('Open apps and browsers, get help and manage your user profile.')
    ),
    target: '.sidebar',
    disableBeacon: true,
    placement: 'right'
  },
  {
    content: getStepContent(
      I18n('Left Assist Panel'),
      I18n(
        'Discover data sources with the improved data assist panel. Remember to right-click items for more!'
      )
    ),
    target: '.left-panel',
    disableBeacon: true,
    placement: 'right'
  },
  {
    content: getStepContent(
      undefined,
      `${I18n('This is the main attraction, where your selected app runs.')}\n${I18n(
        'Hover on the app name to star it as your favorite application.'
      )}`
    ),
    target: '.page-content',
    disableBeacon: true,
    placement: 'bottom',
    styles: {
      tooltip: {
        marginTop: '100px'
      }
    }
  },
  {
    content: getStepContent(
      I18n('Right Assist Panel'),
      I18n(
        'Some apps have a right panel with additional information to assist you in your data discovery.'
      )
    ),
    target: '.right-panel',
    disableBeacon: true,
    placement: 'left'
  },
  {
    content: (
      <>
        <p>
          {I18n(
            'This ends the tour. To see it again, click Welcome Tour from the help section in the sidebar.'
          )}
        </p>
        <p>
          {I18n('And now go ')}
          <b>{I18n('Query, Explore, Repeat')}</b>!
        </p>
      </>
    ),
    target: 'body',
    disableBeacon: true,
    placement: 'center'
  }
];

if ((window as hueWindow).USER_IS_ADMIN) {
  steps.splice(3, 0, {
    content: getStepContent(
      I18n('Administration'),
      I18n(
        'As a superuser, you can check system configuration from the user menu and install sample data and jobs for your users.'
      )
    ),
    target: '.server-position-pointer-welcome-tour',
    disableBeacon: true,
    placement: 'right-end'
  });
}

const styles: Partial<Joyride.Styles> = {
  options: {
    overlayColor,
    primaryColor,
    zIndex: parseInt(tourZIndex) || 1 // the fallback to 1 is for testing where it doesn't pick up the scss vars properly
  },
  buttonBack: {
    border: backButtonBorder,
    borderRadius,
    fontSize: buttonFontSize,
    lineHeight: buttonLineHeight,
    padding: buttonPadding
  },
  buttonNext: {
    borderRadius,
    fontSize: buttonFontSize,
    lineHeight: buttonLineHeight,
    padding: buttonPadding
  },
  tooltip: {
    borderRadius
  },
  spotlight: {
    borderRadius: 0
  }
};

export const WelcomeTour = (): JSX.Element => {
  const [run, setRun] = useState(false);
  const [joyrideHelpers, setJoyrideHelpers] = useState<Joyride.StoreHelpers>();

  useHuePubSub({
    topic: 'show.welcome.tour',
    callback: () => {
      setRun(true);
    }
  });

  const onStateChange: Joyride.Callback = ({ action }) => {
    if (action === 'close' || action === 'reset') {
      setRun(false);
      if (joyrideHelpers) {
        joyrideHelpers.reset(false);
      }

      // While migrating the old welcome tour I noticed that we no longer start the welcome tour
      // automatically for new users, this was done intentionally in commit:
      // https://github.com/cloudera/hue/commit/f54d0e23fa1105b1bbf8c2cd8f830c2835572be1
      // The user preference is in place in the backend so if we ever want to revert that change
      // we should uncomment the below code and set the initial "run" state based on the value
      // of the preference.

      // post('/desktop/api2/user_preferences/is_welcome_tour_seen', {
      //   set: 'seen'
      // });
    }
  };

  return (
    <Joyride
      steps={steps}
      run={run}
      disableScrolling={true}
      continuous={true}
      spotlightPadding={0}
      callback={onStateChange}
      getHelpers={setJoyrideHelpers}
      locale={{
        back: I18n('Back'),
        close: I18n('Close'),
        last: I18n('Close'),
        next: I18n('Next')
      }}
      styles={styles}
    />
  );
};

export default WelcomeTour;

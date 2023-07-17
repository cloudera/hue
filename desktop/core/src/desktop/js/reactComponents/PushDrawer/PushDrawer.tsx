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

import React, { FunctionComponent } from 'react';
import classNames from 'classnames';

import Drawer from './Drawer/Drawer';
import DrawerHeaderExport from './DrawerHeader/DrawerHeader';

import './PushDrawer.scss';

/**
 * PushDrawer - stateless drawer that pushes main content to the side when open.
 * Uses render props for drawer header, drawer content and main content.
 * Supports smoth animations for drawers on the left and right side that can
 * be used simultaneously.
 *
 * Example usage:
 *
 * import PushDrawer, { DrawerHeader} from './PushDrawer/PushDrawer';
 * const [isOpen, setIsOpen] = useState(true);
 *
 * <PushDrawer
 *  leftDrawer={
 *    {
 *      content: () => <div> I'm the left drawer content </div>
 *      header: () => <DrawerHeader onClose={() => setIsOpen(false)} title={'My drawer'} />,
 *      isOpen,
 *      width: '100px',
 *    }
 *  }
 *  mainContent={() => <div>I'm the main content</div>}
 * />
 */
export const DrawerHeader = DrawerHeaderExport;
export interface DrawerConfig {
  isOpen: boolean;
  width: string;
  header?: () => JSX.Element | null;
  content: () => JSX.Element;
}

export interface PushDrawerProps {
  mainContent: () => JSX.Element;
  testId?: string;
  leftDrawer?: DrawerConfig;
  rightDrawer?: DrawerConfig;
}

const defaultProps = {
  testId: 'hue-push-drawer'
};

const PushDrawer: FunctionComponent<PushDrawerProps> = ({
  mainContent,
  testId,
  leftDrawer,
  rightDrawer
}) => {
  const spaceUsedByLeftDrawer = leftDrawer?.isOpen ? parseInt(leftDrawer.width) : 0;
  const spaceUsedByRightDrawer = rightDrawer?.isOpen ? parseInt(rightDrawer.width) : 0;
  const totalSpaceUsedByDrawers = spaceUsedByLeftDrawer + spaceUsedByRightDrawer;

  const mainContentWidth = `calc(100% - ${totalSpaceUsedByDrawers}px)`;
  const mainContentLeftPosition = leftDrawer?.isOpen ? leftDrawer.width : 0;

  return (
    <React.StrictMode>
      <div className="hue-push-drawer" data-testid={testId}>
        {leftDrawer && (
          <Drawer
            isOpen={leftDrawer.isOpen}
            width={leftDrawer.width}
            header={leftDrawer.header}
            content={leftDrawer.content}
            direction="left"
            testId={`${testId}-left-drawer`}
          />
        )}
        <div
          data-testid={`${testId}-content`}
          style={{ width: mainContentWidth, left: mainContentLeftPosition }}
          className={classNames('hue-push-drawer__content')}
        >
          {mainContent()}
        </div>

        {rightDrawer && (
          <Drawer
            isOpen={rightDrawer.isOpen}
            width={rightDrawer.width}
            header={rightDrawer.header}
            content={rightDrawer.content}
            direction="right"
            testId={`${testId}-right-drawer`}
          />
        )}
      </div>
    </React.StrictMode>
  );
};

PushDrawer.defaultProps = defaultProps;
export default PushDrawer;

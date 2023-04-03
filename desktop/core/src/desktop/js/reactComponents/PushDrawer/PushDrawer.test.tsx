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

import React from 'react';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

import PushDrawer, { DrawerHeader } from './PushDrawer';

const drawerTestTitle = 'test drawer title';
const drawerContentCheckboxLabel = 'test content checkbox';

const getTestDrawerConfig = () => ({
  width: '100px',
  header: () => <DrawerHeader onClose={jest.fn()} title={drawerTestTitle} />,
  content: () => (
    <div>
      <input type="checkbox" id="chk1-label" />
      <label htmlFor="chk1-label">{drawerContentCheckboxLabel}</label>
    </div>
  )
});

describe('PushDrawer', () => {
  describe('with left drawer open', () => {
    test('renders drawer on the left side in parent container', () => {
      const myTestConfig = { ...getTestDrawerConfig(), isOpen: true };
      render(<PushDrawer leftDrawer={myTestConfig} mainContent={() => <div></div>} />);

      const drawerContainer = screen.getByTestId('hue-push-drawer-left-drawer');
      expect(getComputedStyle(drawerContainer).width).toEqual('100px');
      expect(getComputedStyle(drawerContainer).left).toEqual('0px');
    });

    test('sets the correct width on content container', () => {
      const myTestConfig = { ...getTestDrawerConfig(), isOpen: true };
      render(<PushDrawer leftDrawer={myTestConfig} mainContent={() => <div></div>} />);

      const contentContainer = screen.getByTestId('hue-push-drawer-content');
      expect(getComputedStyle(contentContainer).width).toEqual('calc(100% - 100px)');
    });

    test('renders DrawerHeader as visible', () => {
      const myTestConfig = { ...getTestDrawerConfig(), isOpen: true };
      render(<PushDrawer leftDrawer={myTestConfig} mainContent={() => <div></div>} />);

      const drawerContainer = screen.getByTestId('hue-push-drawer-left-drawer');
      expect(within(drawerContainer).getByRole('heading', { level: 3 })).toBeVisible();
      expect(within(drawerContainer).getByRole('button', { name: 'Close' })).toBeVisible();
    });

    test('renders drawer with custom title in DrawerHeader', async () => {
      const myTestConfig = { ...getTestDrawerConfig(), isOpen: true };
      render(<PushDrawer leftDrawer={myTestConfig} mainContent={() => <div></div>} />);

      const drawerContainer = screen.getByTestId('hue-push-drawer-left-drawer');
      expect(within(drawerContainer).getByText(drawerTestTitle)).toBeVisible();
    });

    test('renders custom JSX header', () => {
      const myTestConfig = {
        ...getTestDrawerConfig(),
        isOpen: true,
        header: () => <h1>custom-header</h1>
      };
      render(<PushDrawer leftDrawer={myTestConfig} mainContent={() => <div></div>} />);

      const drawerContainer = screen.getByTestId('hue-push-drawer-left-drawer');
      expect(within(drawerContainer).getByText('custom-header')).toBeVisible();
    });

    test('renders drawer content as visible', () => {
      const myTestConfig = { ...getTestDrawerConfig(), isOpen: true };
      render(<PushDrawer leftDrawer={myTestConfig} mainContent={() => <div></div>} />);

      const drawerContainer = screen.getByTestId('hue-push-drawer-left-drawer');
      const checkbox = within(drawerContainer).getByRole('checkbox', {
        name: drawerContentCheckboxLabel
      });
      expect(checkbox).toBeVisible();
    });

    test('accepts tab focus on input elements placed in the drawer', async () => {
      const user = userEvent.setup();
      const myTestConfig = { ...getTestDrawerConfig(), isOpen: true };
      render(<PushDrawer leftDrawer={myTestConfig} mainContent={() => <div></div>} />);

      expect(document.body).toHaveFocus();

      const drawerContainer = screen.getByTestId('hue-push-drawer-left-drawer');
      const closeButton = within(drawerContainer).getByRole('button', { name: 'Close' });
      const contentCheckbox = within(drawerContainer).getByRole('checkbox', {
        name: drawerContentCheckboxLabel
      });

      await user.tab();
      expect(closeButton).toHaveFocus();
      await user.tab();
      expect(contentCheckbox).toHaveFocus();
    });

    test('has visible main content', async () => {
      const myTestConfig = { ...getTestDrawerConfig(), isOpen: true };
      render(
        <PushDrawer
          leftDrawer={myTestConfig}
          mainContent={() => (
            <div>
              <button>main content button</button>
            </div>
          )}
        />
      );
      const mainContent = screen.getByTestId('hue-push-drawer-content');
      expect(
        within(mainContent).getByRole('button', { name: 'main content button' })
      ).toBeVisible();
    });

    test('has focusable main content', async () => {
      const user = userEvent.setup();
      const myTestConfig = { ...getTestDrawerConfig(), isOpen: true };
      const configWithEmptyDrawer = {
        ...myTestConfig,
        header: () => <></>,
        content: () => <></>
      };
      render(
        <PushDrawer
          leftDrawer={configWithEmptyDrawer}
          mainContent={() => (
            <div>
              <button>test me</button>
            </div>
          )}
        />
      );
      const mainContent = screen.getByTestId('hue-push-drawer-content');

      await user.tab();
      expect(within(mainContent).getByRole('button', { name: 'test me' })).toHaveFocus();
    });

    test('calls onClose when close button is clicked', async () => {
      const onCloseMock = jest.fn();
      const user = userEvent.setup();
      const myTestConfig = {
        ...getTestDrawerConfig(),
        isOpen: true,
        header: () => <DrawerHeader onClose={onCloseMock} />
      };

      render(<PushDrawer leftDrawer={myTestConfig} mainContent={() => <div></div>} />);
      const drawerContainer = screen.getByTestId('hue-push-drawer-left-drawer');
      const closeButton = within(drawerContainer).getByRole('button', { name: 'Close' });

      expect(onCloseMock).not.toHaveBeenCalled();
      await user.click(closeButton);
      expect(onCloseMock).toHaveBeenCalled();
    });
  });

  describe('with left drawer closed', () => {
    test('renders drawer outside parent container', () => {
      const myTestConfig = { ...getTestDrawerConfig(), isOpen: false };
      render(<PushDrawer leftDrawer={myTestConfig} mainContent={() => <div></div>} />);

      const drawerContainer = screen.getByTestId('hue-push-drawer-left-drawer');
      const drawerLeftPosition = getComputedStyle(drawerContainer).left;

      expect(getComputedStyle(drawerContainer).width).toEqual('100px');
      expect(drawerLeftPosition).toEqual('-100px');
      expect(
        within(drawerContainer).getByRole('heading', { level: 3, hidden: true })
      ).not.toBeVisible();
      expect(
        within(drawerContainer).getByRole('button', { name: 'Close', hidden: true })
      ).not.toBeVisible();
    });

    test('sets the correct width on main content container', () => {
      const myTestConfig = { ...getTestDrawerConfig(), isOpen: true };
      render(<PushDrawer leftDrawer={myTestConfig} mainContent={() => <div></div>} />);

      const contentContainer = screen.getByTestId('hue-push-drawer-content');
      expect(getComputedStyle(contentContainer).width).toEqual('calc(100% - 100px)');
    });

    test('renders DrawerHeader as not visible', () => {
      const myTestConfig = { ...getTestDrawerConfig(), isOpen: false };
      render(<PushDrawer leftDrawer={myTestConfig} mainContent={() => <div></div>} />);

      const drawerContainer = screen.getByTestId('hue-push-drawer-left-drawer');
      expect(
        within(drawerContainer).getByRole('heading', { level: 3, hidden: true })
      ).not.toBeVisible();
      expect(
        within(drawerContainer).getByRole('button', { name: 'Close', hidden: true })
      ).not.toBeVisible();
    });

    test('does not accept tab focus on input elements placed in the drawer', async () => {
      const user = userEvent.setup();
      const myTestConfig = { ...getTestDrawerConfig(), isOpen: false };
      render(<PushDrawer leftDrawer={myTestConfig} mainContent={() => <div></div>} />);

      const drawerContainer = screen.getByTestId('hue-push-drawer-left-drawer');
      const closeButton = within(drawerContainer).getByRole('button', {
        name: 'Close',
        hidden: true
      });
      const contentCheckbox = within(drawerContainer).getByRole('checkbox', {
        name: drawerContentCheckboxLabel,
        hidden: true
      });

      expect(document.body).toHaveFocus();
      await user.tab();
      expect(closeButton).not.toHaveFocus();
      expect(contentCheckbox).not.toHaveFocus();
      await user.tab();
      expect(closeButton).not.toHaveFocus();
      expect(contentCheckbox).not.toHaveFocus();
    });

    test('has visible main content', async () => {
      const myTestConfig = { ...getTestDrawerConfig(), isOpen: false };
      render(
        <PushDrawer
          leftDrawer={myTestConfig}
          mainContent={() => (
            <div>
              <button>main content button</button>
            </div>
          )}
        />
      );
      const mainContent = screen.getByTestId('hue-push-drawer-content');
      expect(
        within(mainContent).getByRole('button', { name: 'main content button' })
      ).toBeVisible();
    });

    test('has focusable main content', async () => {
      const user = userEvent.setup();
      const myTestConfig = { ...getTestDrawerConfig(), isOpen: false };
      const configWithEmptyDrawer = {
        ...myTestConfig,
        header: () => <></>,
        content: () => <></>
      };
      render(
        <PushDrawer
          leftDrawer={configWithEmptyDrawer}
          mainContent={() => (
            <div>
              <button>test me</button>
            </div>
          )}
        />
      );
      const mainContent = screen.getByTestId('hue-push-drawer-content');
      await user.tab();
      expect(within(mainContent).getByRole('button', { name: 'test me' })).toHaveFocus();
    });
  });

  describe('with right drawer open', () => {
    test('renders drawer on the left side in parent container', () => {
      const myTestConfig = { ...getTestDrawerConfig(), isOpen: true };
      render(<PushDrawer rightDrawer={myTestConfig} mainContent={() => <div></div>} />);

      const drawerContainer = screen.getByTestId('hue-push-drawer-right-drawer');
      expect(getComputedStyle(drawerContainer).width).toEqual('100px');
      expect(getComputedStyle(drawerContainer).left).toEqual('calc(100% - 100px)');
    });

    test('sets the correct width on main content container', () => {
      const myTestConfig = { ...getTestDrawerConfig(), isOpen: true };
      render(<PushDrawer rightDrawer={myTestConfig} mainContent={() => <div></div>} />);

      const contentContainer = screen.getByTestId('hue-push-drawer-content');
      expect(getComputedStyle(contentContainer).width).toEqual('calc(100% - 100px)');
    });

    test('renders DrawerHeader as visible', () => {
      const myTestConfig = { ...getTestDrawerConfig(), isOpen: true };
      render(<PushDrawer rightDrawer={myTestConfig} mainContent={() => <div></div>} />);

      const drawerContainer = screen.getByTestId('hue-push-drawer-right-drawer');
      expect(within(drawerContainer).getByRole('heading', { level: 3 })).toBeVisible();
      expect(within(drawerContainer).getByRole('button', { name: 'Close' })).toBeVisible();
    });

    test('renders drawer with custom title in DrawerHeader', async () => {
      const myTestConfig = { ...getTestDrawerConfig(), isOpen: true };
      render(<PushDrawer rightDrawer={myTestConfig} mainContent={() => <div></div>} />);

      const drawerContainer = screen.getByTestId('hue-push-drawer-right-drawer');
      expect(within(drawerContainer).getByText(drawerTestTitle)).toBeVisible();
    });

    test('renders custom JSX header', () => {
      const myTestConfig = {
        ...getTestDrawerConfig(),
        isOpen: true,
        header: () => <h1>custom-header</h1>
      };
      render(<PushDrawer rightDrawer={myTestConfig} mainContent={() => <div></div>} />);

      const drawerContainer = screen.getByTestId('hue-push-drawer-right-drawer');
      expect(within(drawerContainer).getByText('custom-header')).toBeVisible();
    });

    test('renders drawer content as visible', () => {
      const myTestConfig = { ...getTestDrawerConfig(), isOpen: true };
      render(<PushDrawer rightDrawer={myTestConfig} mainContent={() => <div></div>} />);

      const drawerContainer = screen.getByTestId('hue-push-drawer-right-drawer');
      const checkbox = within(drawerContainer).getByRole('checkbox', {
        name: drawerContentCheckboxLabel
      });
      expect(checkbox).toBeVisible();
    });

    test('accepts tab focus on input elements placed in the drawer', async () => {
      const user = userEvent.setup();
      const myTestConfig = { ...getTestDrawerConfig(), isOpen: true };
      render(<PushDrawer rightDrawer={myTestConfig} mainContent={() => <div></div>} />);

      expect(document.body).toHaveFocus();

      const drawerContainer = screen.getByTestId('hue-push-drawer-right-drawer');
      const closeButton = within(drawerContainer).getByRole('button', { name: 'Close' });
      const contentCheckbox = within(drawerContainer).getByRole('checkbox', {
        name: drawerContentCheckboxLabel
      });

      await user.tab();
      expect(closeButton).toHaveFocus();
      await user.tab();
      expect(contentCheckbox).toHaveFocus();
    });

    test('has visible main content', async () => {
      const myTestConfig = { ...getTestDrawerConfig(), isOpen: true };
      render(
        <PushDrawer
          rightDrawer={myTestConfig}
          mainContent={() => (
            <div>
              <button>main content button</button>
            </div>
          )}
        />
      );
      const mainContent = screen.getByTestId('hue-push-drawer-content');
      expect(
        within(mainContent).getByRole('button', { name: 'main content button' })
      ).toBeVisible();
    });

    test('has focusable main content', async () => {
      const user = userEvent.setup();
      const myTestConfig = { ...getTestDrawerConfig(), isOpen: true };
      const configWithEmptyDrawer = {
        ...myTestConfig,
        header: () => <></>,
        content: () => <></>
      };
      render(
        <PushDrawer
          rightDrawer={configWithEmptyDrawer}
          mainContent={() => (
            <div>
              <button>test me</button>
            </div>
          )}
        />
      );
      const mainContent = screen.getByTestId('hue-push-drawer-content');

      await user.tab();
      expect(within(mainContent).getByRole('button', { name: 'test me' })).toHaveFocus();
    });

    test('calls onClose when close button is clicked', async () => {
      const onCloseMock = jest.fn();
      const user = userEvent.setup();
      const myTestConfig = {
        ...getTestDrawerConfig(),
        isOpen: true,
        header: () => <DrawerHeader onClose={onCloseMock} />
      };

      render(<PushDrawer rightDrawer={myTestConfig} mainContent={() => <div></div>} />);
      const drawerContainer = screen.getByTestId('hue-push-drawer-right-drawer');
      const closeButton = within(drawerContainer).getByRole('button', { name: 'Close' });

      expect(onCloseMock).not.toHaveBeenCalled();
      await user.click(closeButton);
      expect(onCloseMock).toHaveBeenCalled();
    });
  });

  describe('with right drawer closed', () => {
    test('renders drawer outside parent container', () => {
      const myTestConfig = { ...getTestDrawerConfig(), isOpen: false };
      render(<PushDrawer rightDrawer={myTestConfig} mainContent={() => <div></div>} />);

      const drawerContainer = screen.getByTestId('hue-push-drawer-right-drawer');
      expect(getComputedStyle(drawerContainer).width).toEqual('100px');
      expect(getComputedStyle(drawerContainer).left).toEqual('calc(100% - 0px)');
    });

    test('sets the correct width on main content container', () => {
      const myTestConfig = { ...getTestDrawerConfig(), isOpen: true };
      render(<PushDrawer rightDrawer={myTestConfig} mainContent={() => <div></div>} />);

      const contentContainer = screen.getByTestId('hue-push-drawer-content');
      expect(getComputedStyle(contentContainer).width).toEqual('calc(100% - 100px)');
    });

    test('renders DrawerHeader as not visible', () => {
      const myTestConfig = { ...getTestDrawerConfig(), isOpen: false };
      render(<PushDrawer rightDrawer={myTestConfig} mainContent={() => <div></div>} />);

      const drawerContainer = screen.getByTestId('hue-push-drawer-right-drawer');
      expect(
        within(drawerContainer).getByRole('heading', { level: 3, hidden: true })
      ).not.toBeVisible();
      expect(
        within(drawerContainer).getByRole('button', { name: 'Close', hidden: true })
      ).not.toBeVisible();
    });

    test('does not accept tab focus on input elements placed in the drawer', async () => {
      const user = userEvent.setup();
      const myTestConfig = { ...getTestDrawerConfig(), isOpen: false };
      render(<PushDrawer rightDrawer={myTestConfig} mainContent={() => <div></div>} />);

      const drawerContainer = screen.getByTestId('hue-push-drawer-right-drawer');
      const closeButton = within(drawerContainer).getByRole('button', {
        name: 'Close',
        hidden: true
      });
      const contentCheckbox = within(drawerContainer).getByRole('checkbox', {
        name: drawerContentCheckboxLabel,
        hidden: true
      });

      expect(document.body).toHaveFocus();
      await user.tab();
      expect(closeButton).not.toHaveFocus();
      expect(contentCheckbox).not.toHaveFocus();
      await user.tab();
      expect(closeButton).not.toHaveFocus();
      expect(contentCheckbox).not.toHaveFocus();
    });

    test('has visible main content', async () => {
      const myTestConfig = { ...getTestDrawerConfig(), isOpen: false };
      render(
        <PushDrawer
          rightDrawer={myTestConfig}
          mainContent={() => (
            <div>
              <button>main content button</button>
            </div>
          )}
        />
      );
      const mainContent = screen.getByTestId('hue-push-drawer-content');
      expect(
        within(mainContent).getByRole('button', { name: 'main content button' })
      ).toBeVisible();
    });

    test('has focusable main content', async () => {
      const user = userEvent.setup();
      const myTestConfig = { ...getTestDrawerConfig(), isOpen: false };
      const configWithEmptyDrawer = {
        ...myTestConfig,
        header: () => <></>,
        content: () => <></>
      };
      render(
        <PushDrawer
          rightDrawer={configWithEmptyDrawer}
          mainContent={() => (
            <div>
              <button>test me</button>
            </div>
          )}
        />
      );
      const mainContent = screen.getByTestId('hue-push-drawer-content');
      await user.tab();
      expect(within(mainContent).getByRole('button', { name: 'test me' })).toHaveFocus();
    });
  });

  describe('with left AND right drawer open', () => {
    test('renders drawers on the left and right side in parent container', () => {
      const myTestConfig = { ...getTestDrawerConfig(), isOpen: true };
      render(
        <PushDrawer
          leftDrawer={myTestConfig}
          rightDrawer={myTestConfig}
          mainContent={() => <div></div>}
        />
      );

      const leftDrawerContainer = screen.getByTestId('hue-push-drawer-left-drawer');
      expect(getComputedStyle(leftDrawerContainer).width).toEqual('100px');
      expect(getComputedStyle(leftDrawerContainer).left).toEqual('0px');

      const rightDrawerContainer = screen.getByTestId('hue-push-drawer-right-drawer');
      expect(getComputedStyle(rightDrawerContainer).width).toEqual('100px');
      expect(getComputedStyle(rightDrawerContainer).left).toEqual('calc(100% - 100px)');
    });

    test('sets the correct width on content container', () => {
      const myTestConfig = { ...getTestDrawerConfig(), isOpen: true };
      render(
        <PushDrawer
          leftDrawer={myTestConfig}
          rightDrawer={myTestConfig}
          mainContent={() => <div></div>}
        />
      );

      const contentContainer = screen.getByTestId('hue-push-drawer-content');
      expect(getComputedStyle(contentContainer).width).toEqual('calc(100% - 200px)');
    });

    test('renders DrawerHeaders as visible', () => {
      const myTestConfig = { ...getTestDrawerConfig(), isOpen: true };
      render(
        <PushDrawer
          leftDrawer={myTestConfig}
          rightDrawer={myTestConfig}
          mainContent={() => <div></div>}
        />
      );

      const leftDrawerContainer = screen.getByTestId('hue-push-drawer-left-drawer');
      expect(within(leftDrawerContainer).getByRole('heading', { level: 3 })).toBeVisible();
      expect(within(leftDrawerContainer).getByRole('button', { name: 'Close' })).toBeVisible();

      const rightDrawerContainer = screen.getByTestId('hue-push-drawer-right-drawer');
      expect(within(rightDrawerContainer).getByRole('heading', { level: 3 })).toBeVisible();
      expect(within(rightDrawerContainer).getByRole('button', { name: 'Close' })).toBeVisible();
    });

    test('renders all drawer content as visible', () => {
      const myLeftTestConfig = {
        ...getTestDrawerConfig(),
        isOpen: true,
        content: () => (
          <div>
            <input type="checkbox" id="chk1-label" />
            <label htmlFor="chk1-label">{drawerContentCheckboxLabel}</label>
          </div>
        )
      };
      const myRightTestConfig = {
        ...getTestDrawerConfig(),
        isOpen: true,
        content: () => (
          <div>
            <input type="checkbox" id="chk2-label" />
            <label htmlFor="chk2-label">{drawerContentCheckboxLabel}</label>
          </div>
        )
      };

      render(
        <PushDrawer
          leftDrawer={myLeftTestConfig}
          rightDrawer={myRightTestConfig}
          mainContent={() => <div></div>}
        />
      );

      const leftDrawerContainer = screen.getByTestId('hue-push-drawer-left-drawer');
      const leftDrawerCheckbox = within(leftDrawerContainer).getByRole('checkbox', {
        name: drawerContentCheckboxLabel
      });
      expect(leftDrawerCheckbox).toBeVisible();

      const rightDrawerContainer = screen.getByTestId('hue-push-drawer-right-drawer');
      const rightDrawerCheckbox = within(rightDrawerContainer).getByRole('checkbox', {
        name: drawerContentCheckboxLabel
      });
      expect(rightDrawerCheckbox).toBeVisible();
    });

    test('accepts tab focus on input elements placed in both the drawers', async () => {
      const user = userEvent.setup();
      const myTestConfig = { ...getTestDrawerConfig(), isOpen: true, content: () => <div></div> };
      render(
        <PushDrawer
          leftDrawer={myTestConfig}
          rightDrawer={myTestConfig}
          mainContent={() => <div></div>}
        />
      );

      expect(document.body).toHaveFocus();

      const leftDrawerContainer = screen.getByTestId('hue-push-drawer-left-drawer');
      const leftCloseButton = within(leftDrawerContainer).getByRole('button', { name: 'Close' });
      const rightDrawerContainer = screen.getByTestId('hue-push-drawer-right-drawer');
      const rightCloseButton = within(rightDrawerContainer).getByRole('button', { name: 'Close' });

      await user.tab();
      expect(leftCloseButton).toHaveFocus();
      await user.tab();
      expect(rightCloseButton).toHaveFocus();
    });

    test('has visible main content', async () => {
      const myTestConfig = { ...getTestDrawerConfig(), isOpen: true };
      render(
        <PushDrawer
          leftDrawer={myTestConfig}
          rightDrawer={myTestConfig}
          mainContent={() => (
            <div>
              <button>main content button</button>
            </div>
          )}
        />
      );
      const mainContent = screen.getByTestId('hue-push-drawer-content');
      expect(
        within(mainContent).getByRole('button', { name: 'main content button' })
      ).toBeVisible();
    });

    test('has focusable main content', async () => {
      const user = userEvent.setup();
      const myTestConfig = { ...getTestDrawerConfig(), isOpen: true };
      const configWithEmptyDrawer = {
        ...myTestConfig,
        header: () => <></>,
        content: () => <></>
      };
      render(
        <PushDrawer
          leftDrawer={configWithEmptyDrawer}
          rightDrawer={configWithEmptyDrawer}
          mainContent={() => (
            <div>
              <button>test me</button>
            </div>
          )}
        />
      );
      const mainContent = screen.getByTestId('hue-push-drawer-content');

      await user.tab();
      expect(within(mainContent).getByRole('button', { name: 'test me' })).toHaveFocus();
    });

    test('calls correct onClose when close buttons are clicked', async () => {
      const onLeftCloseMock = jest.fn();
      const onRightCloseMock = jest.fn();
      const user = userEvent.setup();
      const leftTestConfig = {
        ...getTestDrawerConfig(),
        isOpen: true,
        header: () => <DrawerHeader onClose={onLeftCloseMock} />
      };
      const rightTestConfig = {
        ...getTestDrawerConfig(),
        isOpen: true,
        header: () => <DrawerHeader onClose={onRightCloseMock} />
      };

      render(
        <PushDrawer
          leftDrawer={leftTestConfig}
          rightDrawer={rightTestConfig}
          mainContent={() => <div></div>}
        />
      );

      const leftDrawerContainer = screen.getByTestId('hue-push-drawer-left-drawer');
      const leftCloseButton = within(leftDrawerContainer).getByRole('button', { name: 'Close' });

      expect(onLeftCloseMock).not.toHaveBeenCalled();
      await user.click(leftCloseButton);
      expect(onLeftCloseMock).toHaveBeenCalled();

      const rightDrawerContainer = screen.getByTestId('hue-push-drawer-right-drawer');
      const rightCloseButton = within(rightDrawerContainer).getByRole('button', { name: 'Close' });

      expect(onRightCloseMock).not.toHaveBeenCalled();
      await user.click(rightCloseButton);
      expect(onRightCloseMock).toHaveBeenCalled();
    });
  });
});

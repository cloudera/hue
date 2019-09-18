import huePubSub from 'utils/huePubSub';
import sessionManager from 'apps/notebook2/execution/sessionManager';
import { koSetup } from 'spec/jasmineSetup';
import { NAME, SESSION_PANEL_SHOW_EVENT } from '../ko.sessionPanel';

describe('ko.sessionPanel.js', () => {
  const setup = koSetup();

  it('should render component', async () => {
    const element = await setup.renderComponent(NAME, {});

    expect(element.querySelector('[data-test="' + NAME + '"]')).toBeTruthy();
  });

  it('should be visible on publish event', async () => {
    const wrapper = await setup.renderComponent(NAME, {});
    const sessionPanelElement = wrapper.querySelector('[data-test="' + NAME + '"]');
    spyOn(sessionManager, 'getAllSessions').and.returnValue(Promise.resolve([]));

    // Initially hidden
    expect(sessionPanelElement.style['display']).toEqual('none');

    huePubSub.publish(SESSION_PANEL_SHOW_EVENT, 'impala');
    await setup.waitForKoUpdate();

    // Visible after pubsub
    expect(sessionPanelElement.style['display']).toBeFalsy();
  });
});

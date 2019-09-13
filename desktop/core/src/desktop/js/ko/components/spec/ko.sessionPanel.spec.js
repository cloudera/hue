import huePubSub from 'utils/huePubSub';
import sessionManager from 'apps/notebook2/execution/sessionManager';
import { koSetup } from 'spec/jasmineSetup';
import { NAME, SHOW_EVENT_NAME } from '../ko.sessionPanel';

describe('ko.sessionPanel.js', () => {
  const setup = koSetup();

  it('should render component', async () => {
    const element = await setup.renderComponent(NAME, {});

    expect(element.querySelector('.session-panel')).toBeTruthy();
  });

  it('should be visible on publish event', async () => {
    const wrapper = await setup.renderComponent(NAME, {});
    const sessionPanelElement = wrapper.querySelector('.session-panel');
    spyOn(sessionManager, 'getAllSessions').and.returnValue(Promise.resolve([]));

    // Initially hidden
    expect(sessionPanelElement.style['display']).toEqual('none');

    huePubSub.publish(SHOW_EVENT_NAME, 'impala');
    await setup.waitForKoUpdate();

    // Visible after pubsub
    expect(sessionPanelElement.style['display']).toBeFalsy();
  });
});
